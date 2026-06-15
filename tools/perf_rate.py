"""Apply Claude's review score to a perf entry — the CLI Claude runs after
extracting + looking at the video frames. Reuses the SAME scoring engine the
webapp uses (`update_scores_text`), so 你-side (webapp) and Claude-side (this)
write the identical table format and the 合议 is computed one way.

Usage:
  python tools/perf_rate.py <emotion>/<perf_id> <da_yi> <qing_xu> <guo_huo> [note]
e.g.
  python tools/perf_rate.py yayi_yinren/perf_0003 4 4 2 "眼神先垮 land，嘴角略被放大"
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PERF_ROOT = REPO / "ai_videos" / "_performances"
# reuse the webapp's pure scoring engine (single source of truth)
sys.path.insert(0, str(REPO / "projects" / "ai_video_management"))
from libs.infrastructure.writers.perf_score__writer import update_scores_text  # noqa: E402


def main() -> None:
    if len(sys.argv) < 5:
        sys.stdout.write(__doc__ or "")
        sys.exit(1)
    entry, da, qing, guo = sys.argv[1:5]
    note = sys.argv[5] if len(sys.argv) > 5 else ""
    md_path = PERF_ROOT / entry / f"{Path(entry).name}.md"
    if not md_path.is_file():
        sys.stderr.write(f"not found: {md_path}\n")
        sys.exit(1)
    md = md_path.read_text(encoding="utf-8")
    new_md, result = update_scores_text(md, "Claude", int(da), int(qing), int(guo), note)
    md_path.write_text(new_md.rstrip("\n") + "\n", encoding="utf-8")
    sys.stdout.write(f"{entry}: decision={result['decision']} status={result['validation_status']}\n合议: {result['verdict']}\n")


if __name__ == "__main__":
    main()
