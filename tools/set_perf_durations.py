"""Allocate each perf entry's 时长 by need (follow-up 005), not a fixed 5s:

- explicit multi-beat entries (锁定块 carries `[a–b s]` timed windows): duration
  = clamp(round(2.5 * beats), 8, 15); the windows AND the `总和 N 秒` text are
  rescaled proportionally so beats fill the new length (no model filler).
- everything else: an intensity ladder — 强度1=4s, 2=5s, 3=5s, 4=7s, 5=9s
  (higher intensity recruits more body / a longer arc; micro beats stay short).

Idempotent: duration is recomputed from (intensity, beats) and the scale factor
is D / current_total, so a second run is a no-op.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

PERF_ROOT = Path(__file__).resolve().parent.parent / "ai_videos" / "_performances"
_BEAT = re.compile(r"\[\s*([0-9.]+)\s*[–\-]\s*([0-9.]+)\s*s\s*\]")
_INTENSITY = re.compile(r"^intensity:\s*([1-5])", re.M)
_LADDER = {1: 4, 2: 5, 3: 5, 4: 7, 5: 9}


def _fmt(x: float) -> str:
    return str(int(round(x))) if abs(x - round(x)) < 0.05 else f"{x:.1f}"


def target_duration(intensity: int, beats: list[tuple[float, float]]) -> int:
    if beats:
        n = len({(a, b) for a, b in beats})
        return max(8, min(15, round(2.5 * n)))
    return _LADDER[intensity]


def process(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    im = _INTENSITY.search(text)
    if not im:
        return False
    intensity = int(im.group(1))
    beats = [(float(a), float(b)) for a, b in _BEAT.findall(text)]
    D = target_duration(intensity, beats)

    new = text
    if beats:
        cur_total = max(b for _, b in beats)
        if cur_total > 0:
            f = D / cur_total
            new = _BEAT.sub(lambda m: f"[{_fmt(float(m.group(1)) * f)}–{_fmt(float(m.group(2)) * f)}s]", new)
        new = re.sub(r"总和\s*[0-9.]+\s*秒", f"总和 {D} 秒", new)
        new = re.sub(r"总和[0-9.]+秒", f"总和{D}秒", new)
    new = re.sub(r"时长\s*[0-9.]+\s*秒", f"时长 {D} 秒", new)

    if new != text:
        path.write_text(new, encoding="utf-8")
        return True
    return False


def main() -> None:
    changed = 0
    rows: list[str] = []
    for f in sorted(PERF_ROOT.glob("*/perf_*/perf_*.md")):
        text = f.read_text(encoding="utf-8")
        im = _INTENSITY.search(text)
        beats = [(float(a), float(b)) for a, b in _BEAT.findall(text)]
        D = target_duration(int(im.group(1)) if im else 3, beats)
        if process(f):
            changed += 1
        rows.append(f"  {f.stem}: int={im.group(1) if im else '?'} beats={len({(a,b) for a,b in beats})} -> {D}s")
    sys.stdout.write("\n".join(rows) + f"\nupdated {changed} entries\n")


if __name__ == "__main__":
    main()
