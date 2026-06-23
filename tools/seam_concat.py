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


def _has_audio(ffmpeg: str, src: Path) -> bool:
    """True iff `src` carries at least one Audio stream (parsed from `ffmpeg -i`
    stderr — imageio_ffmpeg ships no ffprobe)."""
    info = _run([ffmpeg, "-i", str(src), "-hide_banner"]).stderr.decode("utf-8", "replace")
    return "Audio:" in info


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


# RIFE only reconstructs motion cleanly in a middle band: the two seam frames
# must differ ENOUGH that there is real motion to interpolate, but not SO much
# that the figure scales/jumps (RIFE then morphs → 乱码). The gate is the mean
# absolute luma difference between the two frames (0–255, via ffmpeg
# blend=difference→signalstats YAVG). Calibrated on EP1's two承接 seams, both of
# which are OUTSIDE the band: shot10→11 ≈ 11 (near-duplicate handoff frame → a
# frozen bridge reads as a 停顿) and shot11→12 ≈ 73 (a scale/framing jump → morph).
# Out-of-band seams fall back to the clean trim+butt-join (no pause, no melt).
_BRIDGE_MIN_DIFF: float = 20.0   # below → too similar (near-still); butt-join
_BRIDGE_MAX_DIFF: float = 55.0   # above → scale/scene jump; butt-join
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
    # morphs (乱码). Either way fall back to the clean trim+butt-join.
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
    # at 4 (15 frames). Single-pair `-0/-1/-o` only (dir-mode `-n` varies by build).
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
    if pads:
        joined = "".join(pads)
        fc.append(f"{joined}concat=n={len(pads)}:v=0:a=1,"
                  f"apad,atrim=0:{bridge_dur:.3f},asetpts=N/SR/TB[a]")
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
) -> int:
    """Stitch `inputs` into `out_path`, repairing 承接 seams. Returns the number
    of RIFE bridges actually inserted (0 when rife is None or all seams 硬切)."""
    ffmpeg = _ffmpeg_exe()
    probes = [_probe(ffmpeg, p) for p in inputs]
    fps = fps_override or max(1, round(probes[0][1]))
    w = max((pr[2] for pr in probes), default=0) or 720
    h = max((pr[3] for pr in probes), default=0) or 1280
    n = len(inputs)

    # seams[i] == True ⟺ seam between clip i and i+1 is a 承接 (continuous) chain
    # that gets trim + RIFE bridge. A 硬切 (intended cut) is pure butt-join: no
    # trim, no bridge. Default (no spec) = every seam is a bridge (legacy behavior).
    if seams is None:
        bridge_seam = [True] * (n - 1)
    else:
        if len(seams) != n - 1:
            raise RuntimeError(f"--seams needs {n - 1} entries, got {len(seams)}")
        bridge_seam = list(seams)

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        bodies: list[Path] = []
        for i, src in enumerate(inputs):
            # trim a side only when the seam touching it is a 承接 bridge.
            head = trim if i > 0 and bridge_seam[i - 1] else 0.0
            tail = trim if i < n - 1 and bridge_seam[i] else 0.0
            body = tmp / f"body_{i:03d}.mp4"
            _render_body(ffmpeg, src, head, tail, probes[i][0], fps, w, h, body)
            bodies.append(body)

        segments: list[Path] = []
        bridged = 0
        for i in range(n):
            segments.append(bodies[i])
            if rife and i < n - 1 and bridge_seam[i]:
                br = tmp / f"bridge_{i:03d}.mp4"
                if _rife_bridge(ffmpeg, rife, bodies[i], bodies[i + 1],
                                inputs[i], inputs[i + 1], probes[i][0],
                                trim, fps, w, h, tmp, i, br):
                    segments.append(br)
                    bridged += 1
                else:
                    # gated out of band (reason already printed) or RIFE failed —
                    # either way the seam is a clean trim+butt-join.
                    print(f"  seam {i}->{i+1}: no bridge, butt-joining",
                          file=sys.stderr)

        # Concat via the filter (one re-encode) — reliable for short/heterogeneous
        # segments where the stream-copy muxer silently drops frames.
        cmd: list[str] = [ffmpeg, "-y"]
        for s in segments:
            cmd.extend(["-i", str(s)])
        labels = "".join(f"[{k}:v][{k}:a]" for k in range(len(segments)))
        cmd.extend([
            "-filter_complex",
            f"{labels}concat=n={len(segments)}:v=1:a=1[v][a]",
            "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-ar", str(_AR), "-ac", "2",
            "-movflags", "+faststart", "-loglevel", "error", str(out_path),
        ])
        if _run(cmd).returncode != 0 or not out_path.is_file():
            raise RuntimeError("final concat failed")

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
