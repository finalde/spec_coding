"""Seam-repair concat for Seedance first/last-frame chained clips.

Seedance first/last-frame generation eases each clip's motion to a near-stop on
its END frame and eases the next clip back UP from that same START frame — and
because the next clip is generated FROM the previous clip's last frame, A's last
frame ≈ B's first frame. A plain `concat` therefore shows, at every seam:

    decelerate → the SAME frame held twice (a 2-frame freeze) → accelerate

which reads as "明显的镜头切换感". It is a VELOCITY break plus a duplicate frame,
NOT a pixel jump — so a cross-dissolve can't hide it (verified: it reads worse).

What this tool does RELIABLY (方案1 — highest value, ffmpeg-only):

    trims the ease-out tail off each clip and the ease-in head off the next, which
    ALSO drops the duplicated shared frame, then concats. The freeze is gone and
    the residual is a small motion step instead of a dead hold.

For genuinely continuous seams the post-trim step is tiny (the seam frames were
near-identical to begin with) and usually reads clean on its own.

True MOTION RECONSTRUCTION across the seam (方案3) needs a real frame interpolator
— RIFE / FlowFrames. ffmpeg's `minterpolate` was tested and does NOT work between
two arbitrary stills (it produces a few garbled frames), so it is deliberately
NOT used here. Pass `--rife <exe>` to bridge each seam with an external RIFE
interpolator (e.g. rife-ncnn-vulkan); without it the tool stays trim-only rather
than fake a bridge.

This whole tool only makes sense for CONTINUOUS seams (same scene / framing /
camera). For a hard cut between different shots, just hard-cut — a clean cut reads
fine and trimming/bridging a cut only damages it.

Usage:
  python tools/seam_concat.py --out ep.mp4 A.mp4 B.mp4 [C.mp4 ...] \
      [--trim 0.10] [--rife /path/to/rife-ncnn-vulkan] [--fps 0]

  --trim   seconds cut from EACH side of every seam (the dead ease motion +
           duplicate frame). 0.10 ≈ 3 frames @30fps. Raise if a freeze remains.
  --rife   optional RIFE executable; when given, each seam is motion-bridged.
  --fps    output framerate; 0 = follow the first clip.

ffmpeg is located via the bundled imageio_ffmpeg when present, else `ffmpeg` on
PATH.
"""
from __future__ import annotations

import argparse
import math
import re
import subprocess
import sys
import tempfile
from pathlib import Path

_TIME_RE = re.compile(r"time=\s*(\d+):(\d+):(\d+(?:\.\d+)?)")
_FPS_RE = re.compile(r"(\d+(?:\.\d+)?)\s*fps")
_SIZE_RE = re.compile(r",\s*(\d+)x(\d+)[,\s]")


def _ffmpeg_exe() -> str:
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"


def _run(cmd: list[str]) -> subprocess.CompletedProcess[bytes]:
    try:
        return subprocess.run(cmd, capture_output=True, check=False)
    except (FileNotFoundError, OSError) as exc:
        return subprocess.CompletedProcess(cmd, 1, b"", str(exc).encode())


def _probe(ffmpeg: str, src: Path) -> tuple[float, float, int, int]:
    """Return (video-stream duration, fps, width, height) for `src`."""
    info = _run([ffmpeg, "-i", str(src)]).stderr.decode("utf-8", "replace")
    dur_probe = _run(
        [ffmpeg, "-i", str(src), "-map", "0:v:0", "-c", "copy", "-f", "null", "-"]
    ).stderr.decode("utf-8", "replace")
    times = _TIME_RE.findall(dur_probe)
    dur = (
        int(times[-1][0]) * 3600 + int(times[-1][1]) * 60 + float(times[-1][2])
        if times
        else 5.0
    )
    fps_m = _FPS_RE.search(info)
    fps = float(fps_m.group(1)) if fps_m else 30.0
    size_m = _SIZE_RE.search(info)
    w, h = (int(size_m.group(1)), int(size_m.group(2))) if size_m else (0, 0)
    return max(0.1, dur), fps, w, h


def _norm(w: int, h: int, fps: int) -> str:
    """The shared normalisation tail so every segment has identical params (a
    must for concat without re-scaling surprises)."""
    return (
        f"scale={w}:{h}:force_original_aspect_ratio=decrease,"
        f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:black,setsar=1,fps={fps}"
    )


_AR: int = 44100   # uniform audio rate/layout across every segment (concat needs identical)
# Click-free joins. A short equal-power fade at each segment's audio boundaries
# (NO overlap → duration preserved → no A/V drift, unlike a true crossfade which
# would shrink the audio and desync it from the hard-cut video over many joins)
# removes the pop from splicing two waveforms at a non-zero-crossing. Inside a
# bridge the two reused halves ARE crossfaded (self-contained, re-padded to the
# fixed bridge length, so no global drift).
_SEAM_FADE_S: float = 0.010   # ~10ms boundary micro-fade (inaudible, kills clicks)
_BRIDGE_XFADE_S: float = 0.05  # crossfade between the bridge's prev-tail & next-head halves


def _has_audio(ffmpeg: str, src: Path) -> bool:
    """True iff `src` carries at least one Audio stream (parsed from `ffmpeg -i`
    stderr — imageio_ffmpeg ships no ffprobe)."""
    info = _run([ffmpeg, "-i", str(src), "-hide_banner"]).stderr.decode("utf-8", "replace")
    return "Audio:" in info


def _segment_ok(ffmpeg: str, src: Path) -> bool:
    """True iff a freshly-built segment is usable in the final concat — i.e. it
    exists and carries a decodable Video stream. A degenerate RIFE bridge (e.g. one
    forced over a big scale/scene jump) can encode to a file with no usable video
    stream; concatenating it makes the whole filtergraph fail ('matches no streams')
    and breaks the episode. Reject such a bridge so the seam falls back to a clean
    butt-join instead."""
    if not src.is_file():
        return False
    info = _run([ffmpeg, "-i", str(src), "-hide_banner"]).stderr.decode("utf-8", "replace")
    return "Video:" in info


def _render_body(
    ffmpeg: str, src: Path, head: float, tail: float, dur: float,
    fps: int, w: int, h: int, out: Path,
) -> None:
    """Re-encode `src` minus its ease head/tail (the head trim also drops the
    duplicated shared seam frame) to a uniform segment, carrying the matching
    slice of audio (or silence when the source is mute) so the final concat keeps
    sound and every segment has an identical a/v layout."""
    end = max(head + 0.05, dur - tail)
    vf = f"trim=start={head:.3f}:end={end:.3f},setpts=PTS-STARTPTS,{_norm(w, h, fps)}"
    if _has_audio(ffmpeg, src):
        af = (
            f"atrim=start={head:.3f}:end={end:.3f},asetpts=PTS-STARTPTS,"
            f"aresample={_AR}"
        )
        cmd = [
            ffmpeg, "-y", "-i", str(src), "-vf", vf, "-af", af,
            "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-ar", str(_AR), "-ac", "2",
            "-loglevel", "error", str(out),
        ]
    else:
        cmd = [
            ffmpeg, "-y", "-i", str(src),
            "-f", "lavfi", "-i", f"anullsrc=r={_AR}:cl=stereo",
            "-vf", vf, "-map", "0:v:0", "-map", "1:a:0", "-shortest",
            "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-ar", str(_AR), "-ac", "2",
            "-loglevel", "error", str(out),
        ]
    if _run(cmd).returncode != 0 or not out.is_file():
        raise RuntimeError(f"body render failed: {src.name}")


# RIFE reconstructs motion cleanly only up to a point: too much frame-to-frame
# change (a scale/framing jump) makes it morph the figure → 乱码. The gate is the
# mean absolute luma difference between the two seam frames (0–255, via ffmpeg
# blend=difference→signalstats YAVG). The HIGH bound is the load-bearing one
# (EP1 shot11→12 ≈ 73 jump, EP4 several ≈ 56–58 → all morph if bridged). The LOW
# bound only skips a *true freeze* (diff ≈ 0 → RIFE makes identical frames, a
# pointless hold); it is deliberately small because a large STATIC background
# dilutes the global diff of a seam whose SUBJECTS move (e.g. EP4 shot6→7 ≈ 12:
# two figures shift against a fixed temple — RIFE bridges it cleanly, so it must
# NOT be gated). Once the bridge carries real ambient audio (not silence) a small-
# motion bridge no longer reads as a 停顿, so the old high MIN is retired.
_BRIDGE_MIN_DIFF: float = 6.0    # below → essentially a frozen duplicate; butt-join
# Above this the seam is a composition/camera change (not continuous motion) and
# RIFE morphs the frame into a smear (乱码). 40 brackets the observed gap between
# clean bridges (≤~35: EP4 shot6→7≈12, EP1 seam1≈20–30) and morphs (≥~46: EP4
# shot9→10≈46 crowd-wide→man+stele, shot11→12≈74, several jumps 56–58). Note the
# global luma diff is a crude proxy — it can't tell big continuous motion from a
# composition change with similar brightness, so a 承接 seam whose render is really
# a camera change (an over-claimed 衔接 label) is what this catches.
_BRIDGE_MAX_DIFF: float = 40.0   # above → composition/camera change RIFE morphs; butt-join
_YAVG_RE = re.compile(r"lavfi\.signalstats\.YAVG=([0-9.]+)")


def _frame_diff(ffmpeg: str, a: Path, b: Path) -> float | None:
    """Mean absolute luma difference (0–255) between two frames, or None on
    failure. Used to gate RIFE bridging to the bridgeable motion band."""
    out = _run([
        ffmpeg, "-i", str(a), "-i", str(b),
        "-lavfi", "[0][1]blend=all_mode=difference,signalstats,metadata=print:file=-",
        "-f", "null", "-",
    ]).stdout.decode("utf-8", "replace")
    m = _YAVG_RE.findall(out)
    if not m:
        return None
    try:
        return float(m[-1])
    except ValueError:
        return None


def _rife_mid(rife: str, a: Path, b: Path, dst: Path) -> bool:
    """One RIFE midpoint frame between `a` and `b` → `dst`. The `-0/-1/-o file`
    single-pair interface is stable across rife-ncnn-vulkan builds."""
    return _run([rife, "-0", str(a), "-1", str(b), "-o", str(dst)]).returncode == 0 and dst.is_file()


def _rife_chain(rife: str, a: Path, b: Path, depth: int, sd: Path, tag: str) -> list[Path]:
    """Recursively bisect [a, b] `depth` times → up to 2**depth - 1 ORDERED
    in-between frames (a binary subdivision: mid, then mids of each half, ...).
    A failed midpoint collapses that branch — never a silent fake."""
    if depth <= 0:
        return []
    mid = sd / f"m_{tag}.png"
    if not _rife_mid(rife, a, b, mid):
        return []
    left = _rife_chain(rife, a, mid, depth - 1, sd, tag + "0")
    right = _rife_chain(rife, mid, b, depth - 1, sd, tag + "1")
    return left + [mid] + right


def _rife_bridge(
    ffmpeg: str, rife: str, body_prev: Path, body_next: Path,
    src_prev: Path, src_next: Path, dur_prev: float,
    trim: float, fps: int, w: int, h: int, tmp: Path, idx: int, out: Path,
    gate: bool = True, depth_override: int | None = None,
) -> bool:
    """Bridge a seam with an external RIFE interpolator: extract the predecessor's
    last frame + successor's first frame, synthesise motion-compensated in-between
    frames, encode them. The bridge's audio is the genuinely-removed seam content
    (predecessor's trimmed tail + successor's trimmed head, taken from the ORIGINAL
    clips — so it's continuous ambient, not dead silence, and not an echo of the
    body audio). Returns False (caller butt-joins) on any failure — never a silent
    fake."""
    sd = tmp / f"rife_{idx:03d}"
    sd.mkdir(parents=True, exist_ok=True)
    la, fb = sd / "0.png", sd / "1.png"
    if _run([ffmpeg, "-y", "-sseof", "-0.20", "-i", str(body_prev),
             "-update", "1", "-q:v", "2", str(la)]).returncode != 0:
        return False
    if _run([ffmpeg, "-y", "-i", str(body_next), "-frames:v", "1",
             "-q:v", "2", str(fb)]).returncode != 0:
        return False
    if not (la.is_file() and fb.is_file()):
        return False
    # Motion gate: bridge only when the two seam frames sit in the bridgeable band.
    # Too similar → a frozen bridge (停顿); too different → a scale/scene jump RIFE
    # morphs (乱码). Either way fall back to the clean trim+butt-join. Skipped when
    # `gate` is False (the user chose RIFE explicitly via the seam plan).
    if gate:
        diff = _frame_diff(ffmpeg, la, fb)
        if diff is not None and not (_BRIDGE_MIN_DIFF <= diff <= _BRIDGE_MAX_DIFF):
            why = "near-still" if diff < _BRIDGE_MIN_DIFF else "scene/scale jump"
            print(f"  seam {idx}->{idx+1}: frame diff {diff:.0f} out of band "
                  f"[{_BRIDGE_MIN_DIFF:.0f},{_BRIDGE_MAX_DIFF:.0f}] ({why}); butt-joining",
                  file=sys.stderr)
            return False
    # Synthesise ~as many bridge frames as trim removed at this seam (both sides),
    # so the reconstructed motion ≈ the deleted motion and the seam timing stays
    # natural. Binary subdivision → 2**depth-1 frames; depth from the target, capped
    # at 4 (15 frames), or an explicit `depth_override` (补帧密度) from the plan.
    # Single-pair `-0/-1/-o` only (dir-mode `-n` varies by build).
    if depth_override is not None:
        depth = max(1, min(4, int(depth_override)))
    else:
        target = max(1, round(2.0 * trim * fps))
        depth = max(1, min(4, math.ceil(math.log2(target + 1))))
    inner = _rife_chain(rife, la, fb, depth, sd, "r")
    if not inner:
        return False
    seq = sd / "seq"
    seq.mkdir(exist_ok=True)
    for k, f in enumerate(inner):
        (seq / f"{k:03d}.png").write_bytes(f.read_bytes())
    # Audio under the synthesised frames = the genuinely-removed seam content
    # (predecessor tail [dur-trim, dur] + successor head [0, trim] from the ORIGINAL
    # clips), padded/capped to the bridge length. This is continuous ambient (no
    # dead air → no 停顿) and is NOT present in the bodies (no echo). A source with
    # no audio contributes silence for its slice.
    bridge_dur = max(0.04, len(inner) / float(fps))
    cmd: list[str] = [
        ffmpeg, "-y", "-framerate", str(fps), "-i", str(seq / "%03d.png"),
    ]
    fc: list[str] = [f"[0:v]{_norm(w, h, fps)}[v]"]
    pads: list[str] = []
    ai = 1
    fmt = f"aresample={_AR},aformat=sample_fmts=fltp:channel_layouts=stereo"
    if _has_audio(ffmpeg, src_prev):
        cmd += ["-i", str(src_prev)]
        fc.append(f"[{ai}:a]atrim=start={max(0.0, dur_prev - trim):.3f},"
                  f"asetpts=N/SR/TB,{fmt}[ap]")
        pads.append("[ap]"); ai += 1
    if _has_audio(ffmpeg, src_next):
        cmd += ["-i", str(src_next)]
        fc.append(f"[{ai}:a]atrim=start=0:end={trim:.3f},asetpts=N/SR/TB,{fmt}[an]")
        pads.append("[an]"); ai += 1
    if len(pads) == 2:
        # crossfade the two reused halves (no internal hard cut → no click),
        # then re-pad/cap to the fixed bridge length.
        xf = max(0.02, min(_BRIDGE_XFADE_S, trim * 0.5))
        fc.append(f"{pads[0]}{pads[1]}acrossfade=d={xf:.3f}:c1=tri:c2=tri,"
                  f"apad,atrim=0:{bridge_dur:.3f},asetpts=N/SR/TB[a]")
    elif len(pads) == 1:
        fc.append(f"{pads[0]}apad,atrim=0:{bridge_dur:.3f},asetpts=N/SR/TB[a]")
    else:
        cmd += ["-f", "lavfi", "-i", f"anullsrc=r={_AR}:cl=stereo"]
        fc.append(f"[{ai}:a]atrim=0:{bridge_dur:.3f}[a]")
    cmd += [
        "-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]", "-shortest",
        "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-ar", str(_AR), "-ac", "2",
        "-loglevel", "error", str(out),
    ]
    return _run(cmd).returncode == 0 and out.is_file()


def seam_concat(
    inputs: list[Path], out_path: Path, trim: float, rife: str | None,
    fps_override: int, seams: list[bool] | None = None,
    plan: list[dict] | None = None,
) -> int:
    """Stitch `inputs` into `out_path`, repairing 承接 seams. Returns the number
    of RIFE bridges actually inserted (0 when rife is None or all seams 硬切).

    `plan` (length n-1, one entry per seam) is the explicit per-seam decision from
    the UI seam-planner; when given it OVERRIDES both `seams` and the auto motion
    gate (the user has chosen). Each entry: {bridge: bool, trim: float|None,
    depth: int|None}. `seams` (b/c) + the auto gate remain the default when no
    plan is supplied."""
    ffmpeg = _ffmpeg_exe()
    probes = [_probe(ffmpeg, p) for p in inputs]
    fps = fps_override or max(1, round(probes[0][1]))
    w = max((pr[2] for pr in probes), default=0) or 720
    h = max((pr[3] for pr in probes), default=0) or 1280
    n = len(inputs)

    # Per-seam config arrays (length n-1): whether to bridge, the trim bite, an
    # optional depth override, and whether the auto motion gate applies. A `plan`
    # is the explicit user decision (gate off); otherwise fall back to seams+gate.
    bridge_seam = [True] * (n - 1)
    trims = [trim] * (n - 1)
    depths: list[int | None] = [None] * (n - 1)
    gated = [True] * (n - 1)
    if plan is not None:
        if len(plan) != n - 1:
            raise RuntimeError(f"plan needs {n - 1} entries, got {len(plan)}")
        for j, e in enumerate(plan):
            bridge_seam[j] = bool(e.get("bridge", True))
            if e.get("trim") is not None:
                trims[j] = float(e["trim"])
            depths[j] = e.get("depth")
            gated[j] = False  # explicit user choice — no auto gate
    elif seams is not None:
        if len(seams) != n - 1:
            raise RuntimeError(f"--seams needs {n - 1} entries, got {len(seams)}")
        bridge_seam = list(seams)

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        bodies: list[Path] = []
        for i, src in enumerate(inputs):
            # trim a side only when the seam touching it is a 承接 bridge.
            head = trims[i - 1] if i > 0 and bridge_seam[i - 1] else 0.0
            tail = trims[i] if i < n - 1 and bridge_seam[i] else 0.0
            body = tmp / f"body_{i:03d}.mp4"
            _render_body(ffmpeg, src, head, tail, probes[i][0], fps, w, h, body)
            bodies.append(body)

        segments: list[Path] = []
        bridged = 0
        for i in range(n):
            segments.append(bodies[i])
            if rife and i < n - 1 and bridge_seam[i]:
                br = tmp / f"bridge_{i:03d}.mp4"
                ok = _rife_bridge(ffmpeg, rife, bodies[i], bodies[i + 1],
                                  inputs[i], inputs[i + 1], probes[i][0],
                                  trims[i], fps, w, h, tmp, i, br,
                                  gate=gated[i], depth_override=depths[i])
                if ok and _segment_ok(ffmpeg, br):
                    segments.append(br)
                    bridged += 1
                elif ok:
                    # The bridge encoded but is degenerate (no decodable video stream
                    # — e.g. a forced bridge over a big scale/scene jump): adding it
                    # would make the final filtergraph fail ("matches no streams") and
                    # break the WHOLE episode. Drop it → clean butt-join for this seam.
                    print(f"  seam {i}->{i+1}: bridge unusable (no video stream), "
                          f"butt-joining", file=sys.stderr)
                else:
                    # gated out of band (reason already printed) or RIFE failed —
                    # either way the seam is a clean trim+butt-join.
                    print(f"  seam {i}->{i+1}: no bridge, butt-joining",
                          file=sys.stderr)

        # Concat via the filter (one re-encode) — reliable for short/heterogeneous
        # segments where the stream-copy muxer silently drops frames. Write to a
        # `.part` sibling and atomically rename only on success: a build killed
        # mid-encode (e.g. the HTTP client disconnects and Starlette cancels the
        # handler) then never leaves a 0-byte/partial file at the real path — the
        # previous good output survives, and the orphaned `.part` is cleaned up.
        part = out_path.with_name(out_path.name + ".part")
        # Micro-fade each segment's audio in/out (~10ms, NO overlap → exact
        # duration preserved → video stays in sync) so the hard concat has no
        # click/pop where two waveforms meet. Needs each segment's true duration.
        seg_durs = [_probe(ffmpeg, s)[0] for s in segments]
        # A segment can lack an audio stream (e.g. a degenerate 1-frame RIFE bridge,
        # or a body whose mute-source fallback dropped out): `[k:a]` would then match
        # no streams and the whole filtergraph fails ("final concat failed"). So probe
        # each segment and substitute a silent `anullsrc` of its duration for any that
        # are audio-less — mirroring the butt-path `_ffmpeg_concat`, so concat=...:a=1
        # always has an audio input for every segment.
        seg_has_audio = [_has_audio(ffmpeg, s) for s in segments]
        cmd: list[str] = [ffmpeg, "-y"]
        for s in segments:
            cmd.extend(["-i", str(s)])
        af_parts: list[str] = []
        silent_idx = len(segments)   # next free input index for anullsrc fills
        for k, d in enumerate(seg_durs):
            if seg_has_audio[k]:
                fo = max(0.0, d - _SEAM_FADE_S)
                af_parts.append(
                    f"[{k}:a]afade=t=in:st=0:d={_SEAM_FADE_S},"
                    f"afade=t=out:st={fo:.3f}:d={_SEAM_FADE_S}[a{k}]"
                )
            else:
                cmd.extend(["-f", "lavfi", "-i", f"anullsrc=r={_AR}:cl=stereo"])
                af_parts.append(f"[{silent_idx}:a]atrim=0:{d:.3f},asetpts=N/SR/TB[a{k}]")
                silent_idx += 1
        labels = "".join(f"[{k}:v][a{k}]" for k in range(len(segments)))
        filt = ";".join(
            af_parts + [f"{labels}concat=n={len(segments)}:v=1:a=1[v][a]"]
        )
        cmd.extend([
            "-filter_complex", filt,
            "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-ar", str(_AR), "-ac", "2",
            # `-f mp4` is required: the muxer can't be inferred from the `.part`
            # extension (ffmpeg guesses format from the output suffix).
            "-movflags", "+faststart", "-f", "mp4", "-loglevel", "error", str(part),
        ])
        res = _run(cmd)
        if res.returncode != 0 or not part.is_file():
            part.unlink(missing_ok=True)
            err = res.stderr.decode("utf-8", errors="replace").strip()
            raise RuntimeError(f"final concat failed: {err[-700:] or 'no stderr'}")
        part.replace(out_path)

    dur, _, _, _ = _probe(ffmpeg, out_path)
    mode = f"{bridged} RIFE bridges" if rife else "trim + dedup (no bridge)"
    print(f"wrote {out_path}  ({n} clips, {mode}, {dur:.1f}s, {w}x{h}@{fps}fps)")
    return bridged


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Seam-repair concat for chained clips.")
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("clips", nargs="+", type=Path)
    ap.add_argument("--trim", type=float, default=0.10)
    ap.add_argument("--rife", type=str, default=None)
    ap.add_argument("--fps", type=int, default=0)
    ap.add_argument(
        "--seams", type=str, default=None,
        help="per-seam continuity, one char per seam (len = #clips-1): "
             "'b'=承接 bridge (trim+RIFE), 'c'=硬切 cut (butt-join). "
             "Omit = all bridges.",
    )
    args = ap.parse_args(argv)

    if len(args.clips) < 2:
        ap.error("need at least 2 clips to concat")
    for c in args.clips:
        if not c.is_file():
            ap.error(f"not found: {c}")
    if args.rife is not None:
        import shutil

        if shutil.which(args.rife) is None and not Path(args.rife).is_file():
            ap.error(f"--rife executable not found: {args.rife}")

    seams: list[bool] | None = None
    if args.seams is not None:
        spec = args.seams.strip().lower()
        if len(spec) != len(args.clips) - 1 or any(ch not in "bc" for ch in spec):
            ap.error(
                f"--seams must be {len(args.clips) - 1} chars of b/c, got {args.seams!r}")
        seams = [ch == "b" for ch in spec]

    seam_concat(args.clips, args.out, args.trim, args.rife, args.fps, seams)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
