"""Extract still frames from a perf entry's downloaded test video(s) so Claude
can look at them and rate the performance (Claude reads images, not mp4).

Frames land in `{perf}/renders/_frames/{video_stem}_f{i}.png` — evenly spaced
across the clip. The startframe PNG (if present) is already directly readable.

Usage:
  python tools/extract_perf_frames.py <emotion>/<perf_id>     # one entry
  python tools/extract_perf_frames.py --all                   # every entry with renders
  python tools/extract_perf_frames.py <...> --n 6             # frames per video (default 5)

Honest limit: these are stills — Claude rates expression / pose / framing from
them and flags continuous-motion smoothness as inferred, not observed.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cv2  # type: ignore

PERF_ROOT = Path(__file__).resolve().parent.parent / "ai_videos" / "_performances"
_VIDEO_EXT = {".mp4", ".mov", ".webm", ".mkv", ".avi", ".m4v"}


def extract_video(mp4: Path, n: int) -> list[Path]:
    cap = cv2.VideoCapture(str(mp4))
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0
    if total <= 0:
        cap.release()
        return []
    out_dir = mp4.parent / "_frames"
    out_dir.mkdir(parents=True, exist_ok=True)
    # evenly spaced, skipping the very first/last frame
    picks = [int(total * (i + 1) / (n + 1)) for i in range(n)]
    written: list[Path] = []
    for i, fidx in enumerate(picks):
        cap.set(cv2.CAP_PROP_POS_FRAMES, fidx)
        ok, frame = cap.read()
        if not ok:
            continue
        dst = out_dir / f"{mp4.stem}_f{i + 1}.png"
        cv2.imwrite(str(dst), frame)
        written.append(dst)
    cap.release()
    return written


def process_entry(perf_dir: Path, n: int) -> int:
    renders = perf_dir / "renders"
    if not renders.is_dir():
        return 0
    count = 0
    for mp4 in sorted(renders.iterdir()):
        if mp4.is_file() and mp4.suffix.lower() in _VIDEO_EXT:
            frames = extract_video(mp4, n)
            count += len(frames)
            for f in frames:
                sys.stdout.write(f"  frame: {f.relative_to(PERF_ROOT.parent.parent)}\n")
    return count


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("entry", nargs="?", help="<emotion>/<perf_id>, e.g. yayi_yinren/perf_0003")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--n", type=int, default=5)
    args = ap.parse_args()
    total = 0
    if args.all:
        for em in sorted(PERF_ROOT.iterdir()):
            if not em.is_dir() or em.name.startswith("_"):
                continue
            for perf in sorted(em.glob("perf_*")):
                total += process_entry(perf, args.n)
    elif args.entry:
        perf = PERF_ROOT / args.entry
        if not perf.is_dir():
            sys.stderr.write(f"not found: {perf}\n")
            sys.exit(1)
        total += process_entry(perf, args.n)
    else:
        ap.print_help()
        sys.exit(1)
    sys.stdout.write(f"extracted {total} frames\n")


if __name__ == "__main__":
    main()
