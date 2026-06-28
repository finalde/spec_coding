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


def _load_seam_metrics():
    """The scorer module — seam_tune SELECTS using the exact same cv2 4-metric +
    tiered rule (floor-pass first, then weighted) that seam_metrics SCORES with, so
    the tool that picks the params and the dashboard that grades them never disagree."""
    spec = importlib.util.spec_from_file_location("seam_metrics", _HERE / "seam_metrics.py")
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


def _is_continuity_seam(epdir: Path, to_shot: str) -> bool:
    """True iff the 'to' shot is a 首尾帧承接 shot — read from its `衔接:` line (the
    authoritative source), NOT from the plan's method. So a 承接 seam still gets re-tuned
    even if a prior run wrote it as butt/trim. 硬切 → False. (Mirrors the webapp's
    _is_continuity_shot: check 硬切 before 承接 since the hard-cut text contains 承接.)"""
    md = epdir / "shots" / to_shot / f"{to_shot}.md"
    try:
        text = md.read_text(encoding="utf-8")
    except OSError:
        return False
    for line in text.splitlines():
        if "衔接" in line:
            if "硬切" in line:
                return False
            if "承接" in line:
                return True
    return False


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
    metrics = _load_seam_metrics()
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

        # Tune every 首尾帧承接 seam — identified by the 'to' shot's `衔接:承接` line (the
        # truth), so a seam still re-tunes even if a prior run wrote it as butt/trim/rife.
        # Fall back to the plan method for any ep whose shot .md lacks a 衔接 line. 硬切
        # seams are never seams to smooth.
        tune_seams = [
            s for s in seams
            if _is_continuity_seam(epdir, s["to"]) or s.get("method") in ("rife", "trim")
        ]
        if not tune_seams:
            print("no 首尾帧承接 seams to tune; nothing to do.")
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

            # Candidate set for a 首尾帧承接 seam: trim-butt over the trim grid + RIFE over
            # trim×depth. A bare hard-cut ("butt") is deliberately NOT selectable here — a
            # 承接 seam should always at least trim the ease/dup-frame (a hardcut would lose
            # that AND drop the seam from future re-tunes); hardcut stays only in the
            # dashboard's comparison panel for reference. Each candidate is built+scored
            # with the SAME cv2 4-metric the dashboard uses, then ranked by the tiered rule
            # (2026-06-28): every metric ≥ 80 first (and only there does weighted score rank);
            # below the floor, LEXIMIN — compare metric vectors weakest-board-first, and when
            # the weakest are ~level (dead-band 3) fall through to the next-weakest (so an
            # unfixable low board isn't chased at the cost of the others); weighted score only
            # the final tiebreak; ties then prefer the smaller trim / simpler join.
            candidates: list[tuple[str, float, int | None]] = [
                ("trim", t, None) for t in trims
            ]
            candidates += [("rife", t, d) for d in depths for t in trims]

            results: list[dict] = []
            for k, (m, t, d) in enumerate(candidates):
                r = metrics._build_and_measure(
                    seam_concat, a, b, m, t, d, rife, tmp, f"{s['from']}_{k}"
                )
                if "error" in r:
                    print(f"   {m:4} trim={t:.2f} depth={d}  ERROR({r['error']})")
                    continue
                results.append(r)
                tag = f"{m} trim={t:.2f}" + (f" d{d}(+{(2**d)-1}f)" if m == "rife" else "")
                floor = "✓全≥80" if r.get("floor_pass") else f"✗最低{r.get('min_metric')}"
                print(f"   {tag:22} 加权{r['score']:5.1f} [{floor}] "
                      f"M1 {r['M1_velocity']['score']:.0f}·M2 {r['M2_no_freeze']['score']:.0f}·"
                      f"M3 {r['M3_no_jump']['score']:.0f}·M4 {r['M4_junction_ssim']['score']:.0f}")
            print()
            if not results:
                print("   !! all candidates errored; leaving seam unchanged\n")
                continue
            win = max(results, key=metrics.rank_key)
            s["method"] = win["method"]
            s["trim"] = round(float(win["trim"]), 3)
            s["depth"] = win["depth"] if win["method"] == "rife" else None
            tier = ("全指标≥80" if win.get("floor_pass")
                    else f"无任何方案达标·leximin 选(最低指标{win.get('min_metric')})")
            dd = f" depth={win['depth']}" if win["method"] == "rife" else ""
            print(f"   >> WINNER {win['method']} trim={s['trim']}{dd} "
                  f"加权 {win['score']:.1f} · {tier}\n")

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
