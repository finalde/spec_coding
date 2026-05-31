"""Strip the redundant in-body shot-title line from shot prompts.

Per follow-up "在 shot prompt 裏，類似這句話是完全多餘的：
`ep01 / shot06 · 陈凡 内心独白 + reveal motif checkpoint #1 — 6s`，把這類的語句全刪掉".

Inside a shot's `视频 prompt` ```text block some dramas (feng_shou_lu,
nvdi_tuihun_houhuile) carry a free-form title line of the form
`ep{NN} / shot{NN} · {summary} [— {duration}]`. It duplicates the file's
`# ep{NN} / shot{NN} · …` H1 heading AND the in-block `场景:` / `时长:`
fields, so the video model gains nothing from it. The H1 heading
(prefixed with `# `) is the file's navigable title and is left untouched.

Removes each matching line plus one adjacent blank so no double blank is
left behind. Idempotent; safe to re-run. Run from repo root:

    python tools/strip_redundant_shot_title.py            # apply
    python tools/strip_redundant_shot_title.py --dry-run  # preview
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# Column-0 line `ep<NN> / shot<NN> · …`; NOT a markdown heading (no leading `# `).
_TITLE_RE = re.compile(r"^ep\d+\s*/\s*shot\d+\s*·")

AI_VIDEOS = Path("ai_videos")


def strip_file(path: Path) -> int:
    lines = path.read_text(encoding="utf-8").split("\n")
    out: list[str] = []
    removed = 0
    for line in lines:
        if _TITLE_RE.match(line):
            removed += 1
            # Collapse a trailing blank into the preceding blank so the
            # ref-header / 场景 separation stays a single blank line.
            if out and out[-1].strip() == "":
                # drop the matched line; let the next blank be absorbed below
                pass
            continue
        # Absorb a blank that immediately follows a just-removed title line.
        if removed and line.strip() == "" and out and out[-1].strip() == "":
            continue
        out.append(line)
    if removed:
        path.write_text("\n".join(out), encoding="utf-8")
    return removed


def main() -> int:
    dry = "--dry-run" in sys.argv
    if not AI_VIDEOS.is_dir():
        print("run from repo root (ai_videos/ not found)", file=sys.stderr)
        return 2
    total_lines = 0
    total_files = 0
    for path in sorted(AI_VIDEOS.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        hits = [ln for ln in text.split("\n") if _TITLE_RE.match(ln)]
        if not hits:
            continue
        total_files += 1
        total_lines += len(hits)
        rel = path.as_posix()
        for ln in hits:
            print(f"{'[dry] ' if dry else ''}{rel}: - {ln}")
        if not dry:
            strip_file(path)
    print(f"\n{'would remove' if dry else 'removed'} {total_lines} line(s) across {total_files} file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
