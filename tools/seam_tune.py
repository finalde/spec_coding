"""Auto-tune per-seam RIFE depth + trim for 承接 (first/last-frame) splice points,
then build the episode video with the winning parameters.

Reusable across every episode. Given an episode folder that has `shots/shotNN/`
clips and a `seam_plan.json`, this:

  1. reads the seam plan, finds each 承接 seam (method=="rife") — the first/last-frame
     handoff points where clip B was generated FROM clip A's last frame, so the two
     seam frames nearly match and the join must hide a tiny velocity step;
  2. for every such seam, sweeps a grid of (trim 裁切秒 × depth 补帧密度), stitches the
     ISOLATED 2-clip pair for each combo with `tools/seam_concat.py`, and scores how
     smooth the join reads with an objective motion-continuity metric (below);
  3. picks the lowest-scoring (smoothest) combo per seam, optionally writes it back into
     `seam_plan.json`, and builds the whole-episode video with the tuned plan;
  4. flags any seam that is a PROMPT PROBLEM rather than a tuning problem — when the two
     seam frames are too far apart (out of the RIFE-bridgeable band) NO (trim,depth) can
     hide the cut, because the承接 frames genuinely don't match. That is reported, not
     silently bridged into a morph.

Smoothness metric (lower = smoother):
  The join should keep frame-to-frame motion CONSTANT through the seam — no dead hold
  (a freeze: consecutive diff dips to ~0), no jump/morph (a spike: consecutive diff
  shoots far above the surrounding motion). We extract a short window around the seam in
  the stitched output and read the per-frame luma difference series via one ffmpeg pass
  (`tblend=difference,signalstats,metadata=print`). The reference velocity is the median
  diff in the window's outer thirds (genuine A-tail / B-head motion); the score is the
  MAX absolute deviation of the seam-region diffs from that reference. A spike (morph) or
  a dip (freeze) both raise it; a clean constant-velocity join keeps it low.

Usage:
  # tune ep01's 承接 seams, write winners into seam_plan.json, build the episode:
  python tools/seam_tune.py "ai_videos/.../episodes/ep01" --apply --build

  # dry-run report only (no plan edit, no build):
  python tools/seam_tune.py "<epdir>"

  # choose the clip language variant fed to the stitch (default: auto — prefers the
  # variant whose seam frames are actually continuous):
  python tools/seam_tune.py "<epdir>" --lang original|zh|auto

  # custom grids / output path:
  python tools/seam_tune.py "<epdir>" --trims 0.08,0.10,0.12,0.14,0.16,0.20 \
      --depths 2,3,4 --build --out "<epdir>/ep01_rife.mp4"

ffmpeg is located via the bundled imageio_ffmpeg when present, else `ffmpeg` on PATH.
RIFE is taken from --rife, else $RIFE_NCNN_VULKAN_EXE, else the default install path.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_RIFE_DEFAULT = r"C:\tools\rife\rife-ncnn-vulkan-20221029-windows\rife-ncnn-vulkan.exe"
# Out-of-band gate (mirrors seam_concat's auto gate). Above MAX the seam frames are a
# composition/scale change RIFE morphs → a prompt problem, not a tuning problem. Below
# MIN the frames are a frozen duplicate (nothing to bridge).
_BRIDGEABLE_MIN = 3.0
_BRIDGEABLE_MAX = 40.0


def _ffmpeg() -> str:
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"


def _resolve_rife(explicit: str | None) -> str | None:
    cand = explicit or os.environ.get("RIFE_NCNN_VULKAN_EXE") or _RIFE_DEFAULT
    import shutil

    if shutil.which(cand) or Path(cand).is_file():
        return cand
    return None


def _load_seam_concat():
    spec = importlib.util.spec_from_file_location("seam_concat", _HERE / "seam_concat.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


FF = _ffmpeg()
_YAVG = re.compile(r"signalstats\.YAVG=([0-9.]+)")
_TIME = re.compile(r"time=\s*(\d+):(\d+):(\d+(?:\.\d+)?)")
_FPS = re.compile(r"(\d+(?:\.\d+)?)\s*fps")


def _run(cmd: list[str]) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(cmd, capture_output=True)


def _probe(src: Path) -> tuple[float, float]:
    """(duration_s, fps)."""
    info = _run([FF, "-i", str(src)]).stderr.decode("utf-8", "replace")
    d = _run([FF, "-i", str(src), "-map", "0:v:0", "-c", "copy", "-f", "null", "-"]).stderr.decode("utf-8", "replace")
    t = _TIME.findall(d)
    dur = int(t[-1][0]) * 3600 + int(t[-1][1]) * 60 + float(t[-1][2]) if t else 5.0
    fm = _FPS.search(info)
    return max(0.1, dur), (float(fm.group(1)) if fm else 30.0)


def _last_frame(src: Path, dst: Path) -> bool:
    import glob

    pat = str(dst.with_suffix("")) + "_%03d.png"
    _run([FF, "-y", "-sseof", "-0.3", "-i", str(src), "-vsync", "0", "-q:v", "2", pat])
    fs = sorted(glob.glob(str(dst.with_suffix("")) + "_*.png"))
    if not fs:
        return False
    os.replace(fs[-1], dst)
    for f in fs[:-1]:
        Path(f).unlink(missing_ok=True)
    return dst.is_file()


def _first_frame(src: Path, dst: Path) -> bool:
    _run([FF, "-y", "-i", str(src), "-frames:v", "1", "-q:v", "2", str(dst)])
    return dst.is_file()


def _seam_frame_diff(a: Path, b: Path, tmp: Path) -> float | None:
    """Mean abs luma diff (0-255) between clip a's last frame and clip b's first."""
    la, fb = tmp / "seam_L.png", tmp / "seam_F.png"
    if not (_last_frame(a, la) and _first_frame(b, fb)):
        return None
    out = _run([FF, "-i", str(la), "-i", str(fb), "-lavfi",
                "[0][1]blend=all_mode=difference,signalstats,metadata=print:file=-",
                "-f", "null", "-"]).stdout.decode("utf-8", "replace")
    m = _YAVG.findall(out)
    return float(m[-1]) if m else None


def _diff_series(src: Path, start: float, end: float) -> list[float]:
    """Per-frame consecutive luma-diff series over [start,end] of `src`, one ffmpeg pass."""
    out = _run([FF, "-ss", f"{max(0.0, start):.3f}", "-to", f"{end:.3f}", "-i", str(src),
                "-vf", "tblend=all_mode=difference,signalstats,metadata=print:file=-",
                "-an", "-f", "null", "-"]).stdout.decode("utf-8", "replace")
    # first frame of tblend has no predecessor → its YAVG is the frame vs itself; drop it.
    vals = [float(x) for x in _YAVG.findall(out)]
    return vals[1:] if len(vals) > 1 else vals


def _score_window(series: list[float], seam_idx: float, n_bridge: int) -> tuple[float, dict]:
    """Score smoothness from the diff series. seam_idx = float index (in `series`) where
    the bridge starts; n_bridge bridge frames follow. Reference velocity = median of the
    series' outer thirds (real A-tail / B-head motion); score = max |seam-region - ref|."""
    if len(series) < 6:
        return float("inf"), {"reason": "too-few-frames"}
    n = len(series)
    third = max(1, n // 3)
    ref_vals = series[:third] + series[-third:]
    ref = sorted(ref_vals)[len(ref_vals) // 2]
    lo = max(0, int(seam_idx) - 2)
    hi = min(n, int(seam_idx) + n_bridge + 3)
    region = series[lo:hi]
    if not region:
        return float("inf"), {"reason": "empty-region"}
    dev = max(abs(v - ref) for v in region)
    rmin, rmax = min(region), max(region)
    return dev, {"ref": round(ref, 2), "region_min": round(rmin, 2),
                 "region_max": round(rmax, 2), "dev": round(dev, 2),
                 "freeze": rmin < 0.4 * ref, "spike": rmax > 2.2 * ref + 4}


def score_combo(seam_concat, a: Path, b: Path, trim: float, depth: int,
                rife: str, tmp: Path, tag: str) -> tuple[float, dict]:
    """Stitch the isolated (a,b) pair with (trim,depth) and score the seam smoothness."""
    out = tmp / f"pair_{tag}.mp4"
    plan = [{"bridge": True, "trim": trim, "depth": depth}]
    try:
        bridged = seam_concat.seam_concat([a, b], out, trim, rife, 0, None, plan)
    except Exception as exc:
        return float("inf"), {"reason": f"stitch-failed: {exc}"}
    if not out.is_file():
        return float("inf"), {"reason": "no-output"}
    durA, fps = _probe(a)
    fps = max(1, round(fps))
    n_bridge = (2 ** depth) - 1 if bridged else 0
    seam_t = durA - trim  # A body length in the paired output
    win_lo, win_hi = seam_t - 0.7, seam_t + n_bridge / fps + 0.7
    series = _diff_series(out, win_lo, win_hi)
    seam_idx = 0.7 * fps  # frames from win_lo to the seam
    score, det = _score_window(series, seam_idx, n_bridge)
    det.update({"bridged": bool(bridged), "n_bridge": n_bridge, "frames": len(series)})
    out.unlink(missing_ok=True)
    return score, det


def _butt_score(seam_concat, a: Path, b: Path, trim: float, tmp: Path) -> tuple[float, dict]:
    """Score a trim-only butt-join (no RIFE) as the baseline to beat."""
    out = tmp / "pair_butt.mp4"
    plan = [{"bridge": True, "trim": trim, "depth": None}]
    try:
        seam_concat.seam_concat([a, b], out, trim, None, 0, None, plan)
    except Exception as exc:
        return float("inf"), {"reason": f"butt-failed: {exc}"}
    durA, fps = _probe(a)
    fps = max(1, round(fps))
    series = _diff_series(out, durA - trim - 0.7, durA - trim + 0.7)
    score, det = _score_window(series, 0.7 * fps, 0)
    det.update({"bridged": False, "n_bridge": 0, "frames": len(series)})
    out.unlink(missing_ok=True)
    return score, det


def _clip_path(epdir: Path, shot: str, lang: str) -> Path:
    suffix = "_zh" if lang == "zh" else ""
    return epdir / "shots" / shot / f"{shot}{suffix}.mp4"


def _auto_lang(epdir: Path, seams: list[dict], tmp: Path) -> str:
    """Pick the clip variant whose 承接 seam frames are actually continuous (smaller mean
    seam frame diff). A stale variant (video predating a continuity regen) shows big
    diffs; the continuous variant shows small ones."""
    best, best_diff = "original", float("inf")
    for lang in ("original", "zh"):
        diffs = []
        for s in seams:
            if s.get("method") != "rife":
                continue
            a, b = _clip_path(epdir, s["from"], lang), _clip_path(epdir, s["to"], lang)
            if a.is_file() and b.is_file():
                d = _seam_frame_diff(a, b, tmp)
                if d is not None:
                    diffs.append(d)
        if diffs:
            mean = sum(diffs) / len(diffs)
            if mean < best_diff:
                best, best_diff = lang, mean
    return best


def tune(epdir: Path, lang: str, trims: list[float], depths: list[int],
         rife: str, apply: bool, build: bool, out: Path | None) -> int:
    seam_concat = _load_seam_concat()
    plan_path = epdir / "seam_plan.json"
    if not plan_path.is_file():
        print(f"no seam_plan.json in {epdir}", file=sys.stderr)
        return 2
    plan_doc = json.loads(plan_path.read_text(encoding="utf-8"))
    seams = plan_doc.get("seams", [])
    if not seams:
        print("seam_plan.json has no seams", file=sys.stderr)
        return 2

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        if lang == "auto":
            lang = _auto_lang(epdir, seams, tmp)
            print(f"[lang] auto-selected '{lang}' (most-continuous seam frames)\n")

        # Tune every 首尾帧承接 seam — whether the saved plan currently has it as a RIFE
        # bridge OR a trim-butt join (so re-running on an already-tuned ep re-tunes it,
        # not skips it). 硬切 (butt) seams are never seams to smooth.
        tune_seams = [s for s in seams if s.get("method") in ("rife", "trim")]
        if not tune_seams:
            print("no 承接 (method=rife/trim) seams to tune; nothing to do.")
        prompt_problems: list[str] = []

        for s in tune_seams:
            a = _clip_path(epdir, s["from"], lang)
            b = _clip_path(epdir, s["to"], lang)
            if not (a.is_file() and b.is_file()):
                print(f"!! {s['from']}->{s['to']}: missing clip(s) for lang={lang}; skipping")
                continue
            raw_diff = _seam_frame_diff(a, b, tmp)
            diff_str = f"{raw_diff:.1f}" if raw_diff is not None else "n/a"
            print(f"=== seam {s['from']} -> {s['to']}  (seam-frame diff "
                  f"{diff_str})  lang={lang} ===")
            if raw_diff is not None and raw_diff > _BRIDGEABLE_MAX:
                msg = (f"{s['from']}->{s['to']}: seam-frame diff {raw_diff:.1f} > "
                       f"{_BRIDGEABLE_MAX:.0f} — the two 承接 frames don't match "
                       f"(composition/scale change). NO trim/depth can hide this; it is a "
                       f"PROMPT problem (clip B's first frame was not generated to equal "
                       f"clip A's last frame). Fix the shot prompt / re-lock the handoff "
                       f"frame, don't bridge.")
                print("   !! " + msg + "\n")
                prompt_problems.append(msg)
                continue
            if raw_diff is not None and raw_diff < _BRIDGEABLE_MIN:
                print(f"   (near-identical frames; a short trim-only butt-join is best)\n")

            # baseline trim-butt 承接 join (trim + dedup, NO RIFE) to beat. Swept over
            # the trim grid too — the trim bite that removes the ease/dup-frame cleanly
            # is itself a parameter.
            butt_best = (float("inf"), None, {})
            for bt in trims:
                bs, bd = _butt_score(seam_concat, a, b, bt, tmp)
                print(f"   trim-butt trim={bt:.2f}           score={bs:7.2f}  {bd}")
                if bs < butt_best[0]:
                    butt_best = (bs, bt, bd)
            butt_score, butt_trim, butt_det = butt_best

            best = (float("inf"), None, None, {})
            for depth in depths:
                for trim in trims:
                    sc, det = score_combo(seam_concat, a, b, trim, depth, rife, tmp,
                                          f"{s['from']}_{trim}_{depth}")
                    flag = ""
                    if det.get("freeze"):
                        flag += " FREEZE"
                    if det.get("spike"):
                        flag += " SPIKE"
                    print(f"   rife trim={trim:.2f} depth={depth} (+{(2**depth)-1:>2}f) "
                          f"score={sc:7.2f}  {det}{flag}")
                    if sc < best[0]:
                        best = (sc, trim, depth, det)
            print()
            bscore, btrim, bdepth, bdet = best
            # Adopt RIFE only if it beats the butt baseline by a clear MARGIN. A plain
            # trim+butt-join is the simpler, more robust join (no synthesized frames to
            # morph), so it wins ties — RIFE must EARN its place. The margin scales with
            # the baseline so near-static seams (tiny scores, all essentially flat) don't
            # flip to RIFE on noise. RIFE's real win case is a seam with a genuine
            # freeze/hold the butt-join can't remove, where it beats butt decisively.
            margin = max(0.5, 0.30 * butt_score)
            if btrim is not None and bscore < butt_score - margin:
                s["method"] = "rife"
                s["trim"] = round(btrim, 3)
                s["depth"] = bdepth
                print(f"   >> WINNER rife trim={btrim:.2f} depth={bdepth} "
                      f"score={bscore:.2f} (beats trim-butt {butt_score:.2f})\n")
            else:
                s["method"] = "trim"
                s["trim"] = round(butt_trim, 3)
                s["depth"] = None
                print(f"   >> WINNER trim-butt trim={butt_trim:.2f} score={butt_score:.2f} "
                      f"(RIFE did not clearly improve)\n")

        if prompt_problems:
            print("PROMPT PROBLEMS (not fixable by tuning):")
            for m in prompt_problems:
                print("  - " + m)
            print()

        if apply:
            plan_path.write_text(json.dumps(plan_doc, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"[apply] wrote tuned parameters into {plan_path}\n")

        if build:
            # Default to the CANONICAL reel name (ep{NN}.mp4 / ep{NN}_zh.mp4) — the tuned
            # plan is usually trim-butt, not RIFE, so a "_rife" suffix would mislead; the
            # winning plan is what the episode should ship as. Override with --out.
            out_path = out or (epdir / f"{epdir.name}{'_zh' if lang == 'zh' else ''}.mp4")
            _build_episode(seam_concat, epdir, lang, seams, rife, out_path)
            print(f"[build] wrote {out_path}")

    return 0


def _build_episode(seam_concat, epdir: Path, lang: str, seams: list[dict],
                   rife: str, out_path: Path) -> None:
    """Concat every shot in order with the (tuned) per-seam plan."""
    shots = [seams[0]["from"]] + [s["to"] for s in seams]
    inputs = [_clip_path(epdir, sh, lang) for sh in shots]
    missing = [str(p) for p in inputs if not p.is_file()]
    if missing:
        raise SystemExit(f"missing clips for build: {missing}")
    tool_plan: list[dict] = []
    for s in seams:
        m = s.get("method")
        trim = float(s["trim"]) if s.get("trim") is not None else 0.10
        if m == "rife":   # trim both sides + insert a RIFE motion bridge
            tool_plan.append({"bridge": True, "rife": True, "trim": trim, "depth": s.get("depth")})
        elif m == "trim":  # 承接: trim the ease/dup-frame + butt-join, NO RIFE bridge
            tool_plan.append({"bridge": True, "rife": False, "trim": trim, "depth": None})
        else:              # butt / hardcut: plain hard cut, no trim
            tool_plan.append({"bridge": False, "rife": False, "trim": trim, "depth": None})
    any_rife = any(e.get("rife") and e["bridge"] for e in tool_plan)
    seam_concat.seam_concat(inputs, out_path, 0.10, rife if any_rife else None, 0, None, tool_plan)


def main(argv: list[str] | None = None) -> int:
    for st in (sys.stdout, sys.stderr):
        if hasattr(st, "reconfigure"):
            st.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Auto-tune RIFE/trim per 承接 seam and build the episode.")
    ap.add_argument("epdir", type=Path, help="episode folder (has shots/ and seam_plan.json)")
    ap.add_argument("--lang", choices=["original", "zh", "auto"], default="auto")
    ap.add_argument("--trims", type=str, default="0.08,0.10,0.12,0.14,0.16,0.20")
    ap.add_argument("--depths", type=str, default="2,3,4")
    ap.add_argument("--rife", type=str, default=None)
    ap.add_argument("--apply", action="store_true", help="write winners into seam_plan.json")
    ap.add_argument("--build", action="store_true", help="build the episode video with tuned plan")
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args(argv)

    if not args.epdir.is_dir():
        ap.error(f"not a directory: {args.epdir}")
    rife = _resolve_rife(args.rife)
    if rife is None:
        ap.error("RIFE executable not found — pass --rife or set $RIFE_NCNN_VULKAN_EXE")
    trims = [float(x) for x in args.trims.split(",") if x.strip()]
    depths = [int(x) for x in args.depths.split(",") if x.strip()]
    return tune(args.epdir, args.lang, trims, depths, rife, args.apply, args.build, args.out)


if __name__ == "__main__":
    raise SystemExit(main())
