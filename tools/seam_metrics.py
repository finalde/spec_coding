"""Quantitative seam-quality scorecard for 承接 (first/last-frame) splice points.

Where `seam_tune.py` SEARCHES for the best (trim, depth) per seam, this tool MEASURES
how good a given stitch actually is, on an objective, documented rubric — so "是不是最
好的" stops being a judgment call. For every 承接 seam it builds the isolated 2-clip join
(with the method saved in seam_plan.json) and scores four independent metrics computed
from the rendered output, then — by default — re-scores the SAME seam as a plain hard-cut
and as the best RIFE bridge, so the chosen method's win is shown, not asserted.

The four metrics (each 0–100, higher = smoother; the seam score is their weighted mean):

  M1 · 运动速度连贯 (Velocity continuity, weight 40) — the load-bearing one.
     Dense optical flow (Farneback, cv2) between consecutive output frames gives the
     per-frame motion SPEED (px/frame). A smooth join keeps that speed CONSTANT through
     the seam; a cut/morph spikes it, a freeze drops it to ~0. Score = how little the
     seam-region speed deviates from the surrounding real-motion baseline, on a
     perceptual scale (a >~8 px/frame velocity break reads as a clear jolt).

  M2 · 无冻结 (No-freeze, weight 15) — the minimum consecutive motion in the seam region
     vs the baseline. A held/duplicate frame (motion ≈ 0 while the clip is otherwise
     moving) reads as a stutter. Full marks when the seam never stalls below the
     surrounding motion; penalised as the min approaches zero.

  M3 · 无跳变/无拖影 (No jump / no morph, weight 25) — the maximum consecutive motion
     AND luma spike in the seam region vs baseline. A hard pixel jump (cut) or a RIFE
     ghost/smear both show up as a spike far above the natural motion. Full marks when
     the peak stays near the baseline; penalised as it exceeds ~2× baseline.

  M4 · 接缝结构连续 (Junction structural continuity, weight 20) — the WORSE of two cut
     detectors: (a) the lowest adjacent-frame SSIM in the region (a visible "snap":
     1.0 = seamless, <~0.6 = a content jump), and (b) the motion-compensated residual
     ratio — warp the before-frame along its own flow and see what's left unexplained;
     a hard cut's content swap can't be reconstructed by flow so its residual spikes far
     above the natural per-frame residual, catching cuts that SSIM alone misses because
     the two frames are the same scene/framing.

The seam is LOCATED EMPIRICALLY (not trusted from durations, which drift a frame or two
after dedup/trim): we find the transition by its local MC-residual prominence near the
expected spot, so the metrics measure where the cut/bridge ACTUALLY is. Without this a
mislocated hard cut leaks out of the measured region and scores as smooth (the "90+ but
visibly cuts" bug) while RIFE's correctly-measured bridge gets out-competed.

Each metric also reports its RAW measurement (px/frame, ratio, SSIM 0–1) next to its
score, so the number is auditable, not a black box.

Usage:
  # score the saved plan's seams + compare vs hard-cut & RIFE:
  python tools/seam_metrics.py "ai_videos/.../episodes/ep01"

  # score only the chosen method (no comparison), pick clip language:
  python tools/seam_metrics.py "<epdir>" --no-compare --lang original

  # JSON scorecard (for the UI / CI):
  python tools/seam_metrics.py "<epdir>" --json
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import cv2
import numpy as np

_HERE = Path(__file__).resolve().parent
_RIFE_DEFAULT = r"C:\tools\rife\rife-ncnn-vulkan-20221029-windows\rife-ncnn-vulkan.exe"

# Perceptual scales (720x1280 @ ~24fps, measured at a 360px-wide analysis frame).
_VEL_JOLT_PXF = 8.0     # a velocity break ≥ this many px/frame reads as a clear jolt → 0
_SPIKE_OK_RATIO = 2.0   # seam peak motion ≤ this × baseline is unnoticeable → full marks
_SPIKE_BAD_RATIO = 5.0  # ≥ this × baseline is a hard jump/morph → 0
_SSIM_BAD = 0.55        # junction SSIM ≤ this is a clear content snap → 0
_SSIM_GOOD = 0.95       # ≥ this is structurally seamless → full marks
_MCR_OK_RATIO = 2.0     # seam MC-residual ≤ this × baseline = motion explains it → full marks
_MCR_BAD_RATIO = 8.0    # ≥ this × baseline = a content swap flow can't explain (hard cut) → 0
_ANALYSIS_W = 360       # downscale width for flow/ssim (speed; motion ratios scale-free)
# Perceptual ABSOLUTE floors — below these the difference is sub-threshold, so ratio-based
# metrics (which blow up when the baseline is ~0 on a near-static seam) must NOT penalise.
_FREEZE_BASE_FLOOR = 1.0   # baseline motion < this px/frame → shot ~static → no freeze possible
_JUMP_ABS_FLOOR = 3.0      # seam peak motion < this px/frame → no perceptible jump regardless of ratio

_W = {"M1": 40.0, "M2": 15.0, "M3": 25.0, "M4": 20.0}
# Selection rule (2026-06-28): a candidate that gets EVERY metric ≥ this floor is always
# preferred over one that doesn't — only inside each tier does the weighted score rank.
# So "先把所有 metric 做到 80 以上，再按权重评分"; when NO candidate can clear the floor
# (e.g. a seam with an unavoidable structural step), fall back to weighted score.
_METRIC_FLOOR = 80.0
_METRIC_SCORE_KEYS = ("M1_velocity", "M2_no_freeze", "M3_no_jump", "M4_junction_ssim")


def _ffmpeg() -> str:
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"


FF = _ffmpeg()
import re

_TIME = re.compile(r"time=\s*(\d+):(\d+):(\d+(?:\.\d+)?)")
_FPS = re.compile(r"(\d+(?:\.\d+)?)\s*fps")


def _run(cmd: list[str]) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(cmd, capture_output=True)


def _resolve_rife(explicit: str | None) -> str | None:
    cand = explicit or os.environ.get("RIFE_NCNN_VULKAN_EXE") or _RIFE_DEFAULT
    import shutil

    return cand if (shutil.which(cand) or Path(cand).is_file()) else None


def _load_seam_concat():
    spec = importlib.util.spec_from_file_location("seam_concat", _HERE / "seam_concat.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def _probe(src: Path) -> tuple[float, int]:
    info = _run([FF, "-i", str(src)]).stderr.decode("utf-8", "replace")
    d = _run([FF, "-i", str(src), "-map", "0:v:0", "-c", "copy", "-f", "null", "-"]).stderr.decode("utf-8", "replace")
    t = _TIME.findall(d)
    dur = int(t[-1][0]) * 3600 + int(t[-1][1]) * 60 + float(t[-1][2]) if t else 5.0
    fm = _FPS.search(info)
    return max(0.1, dur), max(1, round(float(fm.group(1)) if fm else 24.0))


def _extract_window(src: Path, start: float, end: float, tmp: Path) -> list[np.ndarray]:
    """Decode [start,end] of `src` to grayscale frames downscaled to _ANALYSIS_W wide."""
    pat = str(tmp / "f_%04d.png")
    for f in tmp.glob("f_*.png"):
        f.unlink()
    _run([FF, "-ss", f"{max(0.0, start):.3f}", "-to", f"{end:.3f}", "-i", str(src),
          "-vf", f"scale={_ANALYSIS_W}:-2", "-vsync", "0", pat])
    out = []
    for p in sorted(tmp.glob("f_*.png")):
        img = cv2.imread(str(p), cv2.IMREAD_GRAYSCALE)
        if img is not None:
            out.append(img)
    return out


def _flow_field(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Dense optical-flow vector field (HxWx2, px/frame) from a→b."""
    return cv2.calcOpticalFlowFarneback(a, b, None, 0.5, 3, 15, 3, 5, 1.2, 0)


def _flow_mag(a: np.ndarray, b: np.ndarray) -> float:
    """Mean dense optical-flow magnitude (px/frame) from a→b."""
    F = _flow_field(a, b)
    return float(np.mean(np.sqrt(F[..., 0] ** 2 + F[..., 1] ** 2)))


def _mc_residual(a: np.ndarray, b: np.ndarray, F: np.ndarray) -> float:
    """Motion-compensated residual: warp `a` toward `b` along its own flow `F`, then
    measure what's LEFT unexplained (mean abs luma, 0–255). For genuinely continuous
    motion the flow explains the change → low residual; at a HARD CUT the flow is
    matching unrelated content → the warp can't reconstruct `b` → high residual. This is
    the signal that tells a real motion step from a content swap even when the two raw
    frames look similar (same scene/framing) and SSIM/magnitude alone are fooled."""
    h, w = a.shape
    gx, gy = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
    mapx = gx + F[..., 0]
    mapy = gy + F[..., 1]
    warped = cv2.remap(a, mapx, mapy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    return float(np.mean(np.abs(warped.astype(np.int16) - b.astype(np.int16))))


def _ssim(a: np.ndarray, b: np.ndarray) -> float:
    """Global SSIM between two grayscale frames (Wang et al. constants)."""
    a = a.astype(np.float64); b = b.astype(np.float64)
    C1, C2 = (0.01 * 255) ** 2, (0.03 * 255) ** 2
    ka = cv2.getGaussianKernel(11, 1.5)
    win = ka @ ka.T
    mu_a = cv2.filter2D(a, -1, win)[5:-5, 5:-5]
    mu_b = cv2.filter2D(b, -1, win)[5:-5, 5:-5]
    a2 = cv2.filter2D(a * a, -1, win)[5:-5, 5:-5] - mu_a ** 2
    b2 = cv2.filter2D(b * b, -1, win)[5:-5, 5:-5] - mu_b ** 2
    ab = cv2.filter2D(a * b, -1, win)[5:-5, 5:-5] - mu_a * mu_b
    s = ((2 * mu_a * mu_b + C1) * (2 * ab + C2)) / (
        (mu_a ** 2 + mu_b ** 2 + C1) * (a2 + b2 + C2))
    return float(np.clip(s.mean(), -1, 1))


def _luma_diff(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.mean(np.abs(a.astype(np.int16) - b.astype(np.int16))))


def _score_curve(val: float, good: float, bad: float) -> float:
    """100 at `good`, 0 at `bad`, linear between (handles good<bad or good>bad)."""
    if good == bad:
        return 100.0
    t = (val - bad) / (good - bad)
    return float(np.clip(t, 0.0, 1.0) * 100.0)


def measure_seam(frames: list[np.ndarray], seam_idx: int, n_bridge: int) -> dict:
    """Compute the four metrics from the extracted seam-window frames. `seam_idx` =
    the EXPECTED index of the last frame before the join (derived from durations, which
    can be off by a frame or two after dedup/trim); `n_bridge` synth frames follow.

    The seam is LOCATED EMPIRICALLY, not trusted from `seam_idx`: a hard cut concentrates
    its discontinuity in one frame step, and if the duration-math points a couple of frames
    off, that catastrophe leaks OUT of a fixed region and the seam scores as smooth (the bug
    behind "scores 90+ but visibly cuts", and behind RIFE never winning — its spread-out
    bridge stayed in-region and got honestly scored while the trim-cut's spike leaked out).
    So we slide the transition-length window over a search band around the expected spot and
    lock onto the placement with the worst motion-compensated residual — i.e. measure where
    the transition ACTUALLY is."""
    n = len(frames)
    if n < 8:
        return {"error": "too-few-frames", "frames": n}
    fields = [_flow_field(frames[i], frames[i + 1]) for i in range(n - 1)]
    flow = [float(np.mean(np.sqrt(F[..., 0] ** 2 + F[..., 1] ** 2))) for F in fields]
    luma = [_luma_diff(frames[i], frames[i + 1]) for i in range(n - 1)]
    ssim_pair = [_ssim(frames[i], frames[i + 1]) for i in range(n - 1)]
    mcr = [_mc_residual(frames[i], frames[i + 1], fields[i]) for i in range(n - 1)]
    nf = len(flow)
    # Empirically locate the transition ONSET by local prominence — how much a step's MC-
    # residual spikes above its own neighbours — NOT by absolute residual (which is high
    # wherever a clip simply moves fast, so a plain max would drift onto the faster clip's
    # steady motion instead of the seam). A hard cut is a sharp prominence spike; a RIFE
    # bridge's onset is a smaller-but-clear rise off the calmer predecessor. Search only a
    # tight band — the duration math is off by a frame or two (dedup), not ten.
    region_len = min(nf, n_bridge + 2)
    radius = 4
    band_lo = max(0, seam_idx - radius)
    band_hi = min(nf - 1, seam_idx + radius)
    if band_hi < band_lo:
        band_lo = band_hi = max(0, min(seam_idx, nf - 1))

    def _prominence(i: int) -> float:
        k = 2
        neigh = min(mcr[max(0, i - k)], mcr[min(nf - 1, i + k)])
        return mcr[i] / (1.0 + neigh)

    p = max(range(band_lo, band_hi + 1), key=_prominence)
    # Region STARTS at the transition step p (the cut step itself / the bridge onset) and
    # extends forward — so it captures the discontinuity and its trailing shoulder WITHOUT
    # swallowing the predecessor's natural ease-out frame (which would read as a false freeze).
    lo = max(0, min(p, nf - region_len))
    hi = lo + region_len
    far = flow[:max(0, lo - 1)] + flow[hi + 1:]
    base = float(np.median(far)) if far else float(np.median(flow))
    base = max(base, 0.05)
    region_f = flow[lo:hi] or flow
    region_l = luma[lo:hi] or luma
    region_ssim = ssim_pair[lo:hi] or ssim_pair
    region_mcr = mcr[lo:hi] or mcr
    far_mcr = mcr[:max(0, lo - 1)] + mcr[hi + 1:]
    base_mcr = max(float(np.median(far_mcr)) if far_mcr else float(np.median(mcr)), 0.5)
    seam_idx = lo  # report where the transition was actually found
    # M1 velocity continuity: worst absolute deviation of seam-region speed from baseline.
    vel_break = max(abs(v - base) for v in region_f)
    m1 = _score_curve(vel_break, good=0.0, bad=_VEL_JOLT_PXF)
    # M2 no-freeze: min seam-region motion vs baseline. A freeze only counts when the shot
    # is actually MOVING (baseline above the floor); on a near-static seam there is nothing
    # to freeze, so it scores full marks instead of exploding on a ~0 divisor.
    fr_ratio = min(region_f) / base
    m2 = 100.0 if base < _FREEZE_BASE_FLOOR else _score_curve(fr_ratio, good=1.0, bad=0.0)
    # M3 no-jump/morph: the seam's peak motion / luma spike vs baseline — but a jump only
    # counts when the ABSOLUTE peak motion is perceptible (≥ floor); tiny sub-pixel motion
    # on a near-static seam is not a jump no matter the ratio.
    base_l = max(float(np.median([luma[i] for i in range(len(luma)) if not (lo <= i < hi)] or luma)), 0.5)
    peak_abs = max(region_f)
    spike_ratio = max(peak_abs / base, max(region_l) / base_l)
    m3 = 100.0 if peak_abs < _JUMP_ABS_FLOOR and max(region_l) < 12.0 else _score_curve(
        spike_ratio, good=_SPIKE_OK_RATIO, bad=_SPIKE_BAD_RATIO)
    # M4 junction structural continuity: a real "snap" shows up two ways, and M4 is the worse
    # of them so neither can be fooled. (a) WORST adjacent-frame SSIM in the region — the
    # classic "啪一下" structural break. (b) MC-residual ratio — the seam's peak motion-
    # compensated residual vs the baseline: a hard cut's content swap can't be explained by
    # flow so its residual spikes far above the natural per-frame residual, even when the two
    # frames are the same scene and SSIM looks fine. A smooth join / clean RIFE bridge keeps
    # both high; a cut tanks at least one.
    j_ssim = min(region_ssim)
    m4_ssim = _score_curve(j_ssim, good=_SSIM_GOOD, bad=_SSIM_BAD)
    mcr_ratio = max(region_mcr) / base_mcr
    m4_mcr = _score_curve(mcr_ratio, good=_MCR_OK_RATIO, bad=_MCR_BAD_RATIO)
    m4 = min(m4_ssim, m4_mcr)
    total = (m1 * _W["M1"] + m2 * _W["M2"] + m3 * _W["M3"] + m4 * _W["M4"]) / sum(_W.values())
    min_metric = min(m1, m2, m3, m4)
    return {
        "score": round(total, 1),
        "floor_pass": bool(min_metric >= _METRIC_FLOOR),  # every metric ≥ 80
        "min_metric": round(min_metric, 1),
        "seam_at": lo,  # empirically-located transition step within the window
        "M1_velocity": {"score": round(m1, 1), "vel_break_pxf": round(vel_break, 2),
                        "baseline_pxf": round(base, 2)},
        "M2_no_freeze": {"score": round(m2, 1), "min_ratio": round(fr_ratio, 2)},
        "M3_no_jump": {"score": round(m3, 1), "peak_ratio": round(spike_ratio, 2)},
        "M4_junction_ssim": {"score": round(m4, 1), "ssim": round(j_ssim, 3),
                             "mcr_ratio": round(mcr_ratio, 2)},
        "frames": n,
    }


def rank_key(r: dict) -> tuple:
    """Sort key for ranking candidate methods (higher = better). Tiered per the 2026-06-28
    rule: candidates clearing the 80-floor on EVERY metric come first; ONLY within that
    floor-pass tier does the weighted score rank ("全部≥80 之后再按分数排名").

    Below the floor (no candidate yet all-≥80) ranking is LEXIMIN (lexicographic maximin,
    2026-06-28 refinement): compare the candidates' metric vectors sorted ascending, weakest
    board first — bigger weakest wins; when the weakest boards are ~level (within a 3-point
    dead-band) compare the next-weakest, and so on. This keeps the core intent (4×80 beats
    3×100+1×79 — and that case is actually decided one tier up, since 4×80 is floor-pass)
    while fixing the degenerate maximin case where the weakest board is capped low for EVERY
    candidate (e.g. an unfixable freeze): pure maximin would chase a meaningless +0.x on that
    hopeless board and sacrifice the others (picking rife with M4=13.7 over trim with
    M4=100); leximin, after the ~level weakest, prefers the candidate that keeps the other
    boards high. Weighted score is only the final in-band tiebreak; exact ties then prefer the
    simpler join (trim > butt > rife) and the smaller trim. Errored candidates sink."""
    if "error" in r or "score" not in r:
        return (0, (), -1.0, -1, 0.0)
    method_pref = {"trim": 2, "butt": 1, "rife": 0}.get(r.get("method"), 0)
    score = float(r["score"])
    if r.get("floor_pass"):
        primary: tuple = (score,)
    else:
        # quantize to a 3-point dead-band so a 6.9-vs-7.1 weakest counts as level and the
        # decision falls through to the next-weakest board (leximin), not the rounding noise.
        metrics = (r["M1_velocity"]["score"], r["M2_no_freeze"]["score"],
                   r["M3_no_jump"]["score"], r["M4_junction_ssim"]["score"])
        primary = tuple(sorted(round(m / 3.0) for m in metrics))  # ascending: weakest first
    return (1 if r.get("floor_pass") else 0, primary, score,
            method_pref, -float(r.get("trim") or 0.0))


def _build_and_measure(seam_concat, a: Path, b: Path, method: str, trim: float,
                       depth: int | None, rife: str | None, tmp: Path, tag: str) -> dict:
    out = tmp / f"pair_{tag}.mp4"
    if method == "butt":
        plan = [{"bridge": False, "rife": False, "trim": trim, "depth": None}]
        use_rife = None
    elif method == "trim":
        plan = [{"bridge": True, "rife": False, "trim": trim, "depth": None}]
        use_rife = None
    else:  # rife
        plan = [{"bridge": True, "rife": True, "trim": trim, "depth": depth}]
        use_rife = rife
    try:
        bridged = seam_concat.seam_concat([a, b], out, trim, use_rife, 0, None, plan)
    except Exception as exc:
        return {"error": f"build-failed: {exc}"}
    durA, fps = _probe(a)
    n_bridge = (2 ** depth - 1) if (method == "rife" and bridged and depth) else (
        0 if method != "rife" else (2 ** (depth or 1) - 1) if bridged else 0)
    seam_t = durA - (trim if method in ("trim", "rife") else 0.0)
    win_lo = seam_t - 0.5
    win_hi = seam_t + n_bridge / fps + 0.5
    frames = _extract_window(out, win_lo, win_hi, tmp)
    seam_idx = int(round((seam_t - win_lo) * fps))
    seam_idx = max(1, min(len(frames) - 2, seam_idx))
    res = measure_seam(frames, seam_idx, n_bridge)
    res["method"] = method
    res["trim"] = trim
    res["depth"] = depth
    out.unlink(missing_ok=True)
    return res


def _clip(epdir: Path, shot: str, lang: str) -> Path:
    return epdir / "shots" / shot / f"{shot}{'_zh' if lang == 'zh' else ''}.mp4"


# Machine-readable metric definitions — the single source of truth for what each metric
# means, its weight, and its good/bad thresholds. Served to the UI dashboard so the panel
# and its help text never drift from the scorer. Edit a metric here → UI updates for free.
METRIC_DEFS = [
    {"id": "M1", "key": "M1_velocity", "name": "运动速度连贯", "en": "velocity",
     "weight": _W["M1"], "unit": "px/frame",
     "desc": "光流测每帧运动速度，接缝前后应恒定；偏离基线越小越平滑。",
     "good": "Δ→0 px/帧", "bad": f"Δ≥{_VEL_JOLT_PXF} px/帧 (明显顿挫)"},
    {"id": "M2", "key": "M2_no_freeze", "name": "无冻结", "en": "no-freeze",
     "weight": _W["M2"], "unit": "×baseline",
     "desc": "接缝处最小运动相对基线；出现卡住/重复帧=冻结。近静态镜无冻结概念自动满分。",
     "good": "min≈基线", "bad": "min→0 (卡住)"},
    {"id": "M3", "key": "M3_no_jump", "name": "无跳变/无拖影", "en": "no-jump",
     "weight": _W["M3"], "unit": "×baseline",
     "desc": "接缝处运动/亮度峰值相对基线；硬跳或 RIFE 鬼影=尖峰。峰值低于感知地板自动满分。",
     "good": f"峰≤{_SPIKE_OK_RATIO}×", "bad": f"峰≥{_SPIKE_BAD_RATIO}× (硬跳/拖影)"},
    {"id": "M4", "key": "M4_junction_ssim", "name": "接缝结构连续", "en": "junction-ssim",
     "weight": _W["M4"], "unit": "SSIM / MC残差比",
     "desc": "接缝结构突变，取两者更差：相邻帧最低 SSIM(“啪一下”) 与 运动补偿残差比(硬切的内容跳变光流解释不了→残差飙升，即便同场景 SSIM 也骗不过)。",
     "good": f"SSIM≥{_SSIM_GOOD} 且残差≤{_MCR_OK_RATIO}×", "bad": f"SSIM≤{_SSIM_BAD} 或残差≥{_MCR_BAD_RATIO}× (画面突变)"},
]


def _seam_timeline(epdir: Path, lang: str, all_seams: list[dict]) -> dict[str, dict]:
    """Where each seam lands in the FINAL stitched ep timeline. Returns {"from->to":
    {at_s, start_s, end_s}} — at_s = the join instant; [start_s,end_s] = the transition
    window to scrub to (the join ± the trim bite + any RIFE bridge). Effective per-shot
    length = dur − head_trim − tail_trim, trims applied only at 承接 (trim/rife) seams."""
    if not all_seams:
        return {}
    shots = [all_seams[0]["from"]] + [s["to"] for s in all_seams]
    durs, fpss = [], []
    for sh in shots:
        c = _clip(epdir, sh, lang)
        d, f = _probe(c) if c.is_file() else (0.0, 24)
        durs.append(d); fpss.append(f)

    def bite(seam: dict) -> float:
        return float(seam.get("trim") or 0.0) if seam.get("method") in ("trim", "rife") else 0.0

    out: dict[str, dict] = {}
    cursor = 0.0
    for i in range(len(all_seams)):
        s = all_seams[i]
        head = bite(all_seams[i - 1]) if i > 0 else 0.0
        tail = bite(s)
        eff = max(0.1, durs[i] - head - tail)
        cursor += eff  # boundary after shot i = this seam's join instant
        n_bridge = (2 ** int(s["depth"]) - 1) if (s.get("method") == "rife" and s.get("depth")) else 0
        bridge_dur = n_bridge / max(1, fpss[i])
        out[f"{s['from']}->{s['to']}"] = {
            "at_s": round(cursor, 2),
            "start_s": round(max(0.0, cursor - tail - 0.1), 2),
            "end_s": round(cursor + bridge_dur + tail + 0.1, 2),
        }
        cursor += bridge_dur  # bridge frames occupy time before the next shot
    return out


def compute_scorecard(epdir: Path, lang: str, compare: bool,
                      rife: str | None) -> dict:
    """Score every 承接 seam (and, when `compare`, a ranked method panel) and return a
    structured scorecard dict — the shared payload for the CLI, the UI dashboard and CI.
    Only 首尾帧承接 seams (method trim/rife) are scored; 硬切 cuts are not seams to smooth."""
    seam_concat = _load_seam_concat()
    plan_doc = json.loads((epdir / "seam_plan.json").read_text(encoding="utf-8"))
    all_seams = plan_doc.get("seams", [])
    times = _seam_timeline(epdir, lang, all_seams)
    seams = [s for s in all_seams if s.get("method") in ("trim", "rife")]
    report: list[dict] = []
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        for s in seams:
            a, b = _clip(epdir, s["from"], lang), _clip(epdir, s["to"], lang)
            if not (a.is_file() and b.is_file()):
                tk = f"{s['from']}->{s['to']}"
                report.append({"seam": tk, "time": times.get(tk),
                               "chosen": {"error": "missing-clip"}, "panel": []})
                continue
            ctrim = float(s.get("trim") or 0.10)
            chosen = _build_and_measure(seam_concat, a, b, s["method"], ctrim,
                                        s.get("depth"), rife, tmp, "chosen")
            chosen["label"] = f"CHOSEN({s['method']} trim={ctrim} depth={s.get('depth')})"
            tk = f"{s['from']}->{s['to']}"
            entry = {"seam": tk, "time": times.get(tk), "chosen": chosen, "panel": []}
            if compare:
                panel_spec = [
                    ("butt", 0.10, None, "hardcut"),
                    ("trim", 0.10, None, "trim@0.10"),
                    ("trim", 0.14, None, "trim@0.14"),
                ]
                if rife:
                    panel_spec += [
                        ("rife", 0.14, 2, "rife@0.14/d2"),
                        ("rife", 0.14, 3, "rife@0.14/d3"),
                    ]
                for j, (m, t, d, label) in enumerate(panel_spec):
                    r = _build_and_measure(seam_concat, a, b, m, t, d, rife, tmp, f"p{j}")
                    r["label"] = label
                    entry["panel"].append(r)
            report.append(entry)

    chosen_scores = [e["chosen"]["score"] for e in report if "error" not in e["chosen"]]
    chosen_ok = [e["chosen"] for e in report if "error" not in e["chosen"]]
    best_scores = []
    for e in report:
        ok = [x for x in ([e["chosen"]] + e.get("panel", [])) if "error" not in x]
        if ok:
            best_scores.append(max(ok, key=rank_key)["score"])  # best by tiered rule
    overall = round(sum(chosen_scores) / len(chosen_scores), 1) if chosen_scores else None
    ceiling = round(sum(best_scores) / len(best_scores), 1) if best_scores else None
    return {
        "episode": epdir.name, "lang": lang, "weights": _W,
        "metric_floor": _METRIC_FLOOR,
        "metric_defs": METRIC_DEFS, "seams": report,
        "overall": overall, "overall_grade": _letter(overall) if overall is not None else None,
        # all_floor_pass: every chosen seam clears the 80 floor on every metric (the
        # primary goal under the tiered rule); else some metric is the laggard.
        "all_floor_pass": bool(chosen_ok) and all(c.get("floor_pass") for c in chosen_ok),
        "ceiling": ceiling, "ceiling_grade": _letter(ceiling) if ceiling is not None else None,
        "weakest": round(min(chosen_scores), 1) if chosen_scores else None,
        "n_seams": len(chosen_scores),
    }


# Sidecar the episode build persists so the dashboard shows the last generation's
# score instantly (no recompute) the moment the page opens.
SCORECARD_FILENAME = "seam_scores.json"


def scorecard_path(epdir: Path) -> Path:
    return epdir / f"{epdir.name}.{SCORECARD_FILENAME}"


def save_scorecard(epdir: Path, card: dict, generated_at: str | None = None) -> Path:
    """Write the scorecard sidecar next to the episode. `generated_at` is stamped by
    the caller (the workflow runtime forbids wall-clock inside scripts/tools)."""
    if generated_at is not None:
        card = {**card, "generated_at": generated_at}
    p = scorecard_path(epdir)
    p.write_text(json.dumps(card, ensure_ascii=False, indent=2), encoding="utf-8")
    return p


def grade(epdir: Path, lang: str, compare: bool, rife: str | None,
          as_json: bool, save: bool = False) -> int:
    card = compute_scorecard(epdir, lang, compare, rife)
    if not card["seams"]:
        print("no 承接 (trim/rife) seams in seam_plan.json", file=sys.stderr)
        return 2
    if save:
        p = save_scorecard(epdir, card)
        print(f"[save] wrote {p}", file=sys.stderr)
    if as_json:
        print(json.dumps(card, ensure_ascii=False, indent=2))
        return 0
    _print_report(card["episode"], lang, card["seams"], compare)
    return 0


def _fmt(m: dict) -> str:
    if "error" in m:
        return f"ERROR({m['error']})"
    floor = "✓80" if m.get("floor_pass") else f"✗{m.get('min_metric','?')}"
    return (f"{m['score']:5.1f}[{floor}] | M1速度 {m['M1_velocity']['score']:5.1f}"
            f"(Δ{m['M1_velocity']['vel_break_pxf']}/基线{m['M1_velocity']['baseline_pxf']}px)"
            f" · M2无冻结 {m['M2_no_freeze']['score']:5.1f}(min×{m['M2_no_freeze']['min_ratio']})"
            f" · M3无跳变 {m['M3_no_jump']['score']:5.1f}(峰×{m['M3_no_jump']['peak_ratio']})"
            f" · M4结构 {m['M4_junction_ssim']['score']:5.1f}(SSIM {m['M4_junction_ssim']['ssim']})")


def _print_report(name: str, lang: str, report: list[dict], compare: bool) -> None:
    print(f"\n=== Seam quality scorecard — {name} (lang={lang}) ===")
    print("metric weights: M1 velocity 40 · M2 no-freeze 15 · M3 no-jump/morph 25 · M4 junction SSIM 20")
    print(f"排名规则: 先比「四项是否全≥{_METRIC_FLOOR:.0f}」(✓/✗)，达标档按加权分；未达标档用 leximin(最短板优先·≈持平差<3分则比次短板·依次类推)，加权分仅最后 tiebreak。\n")
    chosen_scores = []
    best_scores = []
    for e in report:
        t = e.get("time")
        loc = f"  @{t['at_s']}s (区间 {t['start_s']}–{t['end_s']}s)" if t else ""
        print(f"● {e['seam']}{loc}")
        c = e["chosen"]
        if "error" not in c:
            chosen_scores.append(c["score"])
        # rank chosen + panel together: floor-pass tier first, then weighted score.
        cands = [c] + e.get("panel", [])
        ok = [x for x in cands if "error" not in x]
        ok.sort(key=rank_key, reverse=True)
        if ok:
            best_scores.append(ok[0]["score"])
        for rank, x in enumerate(ok, 1):
            tag = x.get("label", x.get("method", "?"))
            star = " ★BEST" if rank == 1 else ""
            ischosen = "CHOSEN" in str(x.get("label", ""))
            print(f"   {rank}. {tag:28} {_fmt(x)}{star}{'  ←当前plan' if ischosen else ''}")
        print()
    if chosen_scores:
        overall = sum(chosen_scores) / len(chosen_scores)
        g = _letter(overall)
        print(f"=== 当前 seam_plan 成绩: {overall:.1f}/100  →  {g}   (最弱缝 {min(chosen_scores):.1f}; n={len(chosen_scores)}) ===")
    if compare and best_scores:
        best = sum(best_scores) / len(best_scores)
        print(f"=== 各缝取最高分方法的上限: {best:.1f}/100  →  {_letter(best)} ===")


def _letter(v: float) -> str:
    return ("A+ 卓越" if v >= 95 else "A 优秀" if v >= 90 else "B 良好" if v >= 80
            else "C 合格" if v >= 70 else "D 待改进")


def main(argv: list[str] | None = None) -> int:
    for st in (sys.stdout, sys.stderr):
        if hasattr(st, "reconfigure"):
            st.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Quantitative seam-quality scorecard.")
    ap.add_argument("epdir", type=Path)
    ap.add_argument("--lang", choices=["original", "zh"], default="original")
    ap.add_argument("--no-compare", action="store_true",
                    help="score only the chosen method (skip hard-cut/RIFE comparison)")
    ap.add_argument("--rife", type=str, default=None)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--save", action="store_true",
                    help="write the scorecard sidecar (ep{NN}.seam_scores.json) for the dashboard")
    args = ap.parse_args(argv)
    if not args.epdir.is_dir():
        ap.error(f"not a directory: {args.epdir}")
    if not (args.epdir / "seam_plan.json").is_file():
        ap.error("no seam_plan.json in episode dir")
    rife = _resolve_rife(args.rife)
    return grade(args.epdir, args.lang, not args.no_compare, rife, args.json, args.save)


if __name__ == "__main__":
    raise SystemExit(main())
