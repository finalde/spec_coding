"""One-time sweep: prepend a compact import tag as the first line of every
render-prompt fenced block in the performance library, so a downloaded
Kling/Seedance/Seedream file (named from the prompt's first ~9 chars) carries a
token the downloads importer can route to the right `perf_NNNN/` folder.

Tag scheme (per `_performances/_testrig.md`): `演{NNNN}{克|即|始}`
  演 = 演技库 marker (distinguishes from drama shot tags)
  NNNN = the entry's 4-digit perf number
  克 = Kling 可灵 video / 即 = 即梦 Seedance video / 始 = 起始帧 Seedream still

Section → marker:
  `### Kling 版 …`   → 克
  `### Seedance 版 …` → 即
  `## 起始帧表情`     → 始

Idempotent: a block whose first content line already starts with `演` is skipped.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

PERF_ROOT = Path(__file__).resolve().parent.parent / "ai_videos" / "_performances"
_PERF_NUM = re.compile(r"perf_(\d{4})")


def _marker_for(header: str) -> str | None:
    if header.startswith("### Kling"):
        return "克"
    if header.startswith("### Seedance"):
        return "即"
    if header.startswith("## 起始帧表情"):
        return "始"
    return None


def tag_file(path: Path) -> int:
    m = _PERF_NUM.search(path.stem)
    if not m:
        return 0
    num = m.group(1)
    lines = path.read_text(encoding="utf-8").splitlines()
    out: list[str] = []
    pending: str | None = None  # marker awaiting the next opening fence
    in_block = False
    inserted = 0
    for line in lines:
        stripped = line.strip()
        marker = _marker_for(stripped)
        if marker is not None:
            pending = marker
            out.append(line)
            continue
        if stripped == "```":
            if pending is not None and not in_block:
                # opening fence of a pending render block
                out.append(line)
                in_block = True
                continue
            if in_block:
                in_block = False
            out.append(line)
            continue
        if in_block and pending is not None:
            # first content line of the pending block
            if stripped.startswith("演"):
                pending = None  # already tagged; leave as-is
                out.append(line)
                continue
            out.append(f"演{num}{pending}")
            out.append(line)
            inserted += 1
            pending = None
            continue
        out.append(line)
    if inserted:
        path.write_text("\n".join(out) + "\n", encoding="utf-8")
    return inserted


def main() -> None:
    total_files = 0
    total_tags = 0
    for f in sorted(PERF_ROOT.glob("*/perf_*/perf_*.md")):
        n = tag_file(f)
        if n:
            total_files += 1
            total_tags += n
    sys.stdout.write(f"tagged {total_tags} render blocks across {total_files} files\n")


if __name__ == "__main__":
    main()
