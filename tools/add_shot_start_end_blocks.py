"""Insert `起始帧` + `结束帧` code blocks above the existing video block in each shot.md.

Per follow-up 2026-05-27: every shotNN.md must carry THREE prompt code
blocks instead of one:

  1. **起始帧** — text describing the shot's t=0 still-frame state (角色姿态 /
     位置/构图 / 表情 / 道具). Drives image-to-video models' first-frame
     latching and helps any model attend to the opening visual anchor.
  2. **结束帧** — text describing the shot's t=duration still-frame state.
     Same field schema as start. Helps the model land on the intended last
     frame so subsequent shots stitch cleanly.
  3. **视频 prompt** — the existing video shot prompt (镜头 / 动作 / 台词
     / etc.). Unchanged.

Auto-population: when the existing video block has timed-beat lines in its
`动作:` section (e.g. `- 0-2s ...`), the migrator extracts the first beat
for the start block and the last beat for the end block. Otherwise inserts
field-labeled placeholders.

Idempotent: if 起始帧 or 结束帧 blocks already exist (by `## 起始帧` /
`## 结束帧` heading), skips.

Usage:
    python tools/add_shot_start_end_blocks.py --all
    python tools/add_shot_start_end_blocks.py <drama_slug>
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
AI_VIDEOS = REPO_ROOT / "ai_videos"

# Locate the `## 视频 prompt — 复制下方代码块` heading and the immediately
# following code block. We insert ABOVE this heading.
_VIDEO_HEADING_RE = re.compile(
    r"^##\s+视频\s*prompt[^\n]*$",
    re.MULTILINE,
)
_EXISTING_START_HEADING_RE = re.compile(r"^##\s+起始帧\b", re.MULTILINE)
_EXISTING_END_HEADING_RE = re.compile(r"^##\s+结束帧\b", re.MULTILINE)

# Inside the FIRST `text` code block, find timed-beat lines under 动作:.
_TEXT_BLOCK_RE = re.compile(r"```text\n([\s\S]*?)```")
_DONGZUO_RE = re.compile(r"^动作\s*[:：]\s*$", re.MULTILINE)
_TIMED_BEAT_RE = re.compile(
    r"^[-•·\s]*(\d+(?:\.\d+)?)[\s\-–~]+(\d+(?:\.\d+)?)\s*s\s*[:：]?\s*(.+)$",
    re.MULTILINE,
)
_DURATION_RE = re.compile(r"^时长\s*[:：]\s*(\d+(?:\.\d+)?)\s*s", re.MULTILINE)

_PLACEHOLDER_START = (
    "角色姿态: (待填写 — shot 起始 0s 时角色的身体姿势 / 手势 / 朝向)\n"
    "位置/构图: (待填写 — 角色在画面中的位置 / 焦距 / frame 占比)\n"
    "表情: (待填写 — 眉/眼/唇/下颌的情绪锚点)\n"
    "道具: (待填写 — 角色手持 / 身上 / 场景中的关键 prop)"
)
_PLACEHOLDER_END = (
    "角色姿态: (待填写 — shot 结束时角色的身体姿势 / 手势 / 朝向)\n"
    "位置/构图: (待填写 — 与起始帧的变化点 / 镜头收尾点)\n"
    "表情: (待填写 — 情绪落点)\n"
    "道具: (待填写 — 与起始帧道具状态的变化)"
)


def _extract_beats(video_body: str) -> tuple[str | None, str | None, str | None]:
    """Return (first_beat_text, last_beat_text, duration_str) from the
    existing video code block body, or all None if no beats present."""
    dongzuo = _DONGZUO_RE.search(video_body)
    duration_match = _DURATION_RE.search(video_body)
    duration_str = duration_match.group(1) + "s" if duration_match else None

    if dongzuo is None:
        # Some shots interleave beats directly without a 动作: header.
        beats = list(_TIMED_BEAT_RE.finditer(video_body))
    else:
        # Scan beats only from the 动作: section onward, stop at next blank
        # block (a blank line followed by a field-label line).
        sub = video_body[dongzuo.end():]
        # Cap at the next field-label section to avoid pulling beats from
        # 镜头 / 台词 etc.
        next_field = re.search(r"^\n(?:[一-鿿A-Za-z_/ ]{1,20}\s*[:：])", sub, re.MULTILINE)
        if next_field:
            sub = sub[: next_field.start()]
        beats = list(_TIMED_BEAT_RE.finditer(sub))

    if not beats:
        return None, None, duration_str

    first = beats[0].group(3).strip()
    last = beats[-1].group(3).strip()
    # Trim each to a reasonable length for the start/end block.
    def _trim(s: str, cap: int = 220) -> str:
        s = s.replace("\n", " ").strip()
        return s if len(s) <= cap else s[: cap - 1].rstrip() + "…"
    return _trim(first), _trim(last), duration_str


def _build_start_block(first_beat: str | None) -> str:
    if first_beat:
        return (
            "角色姿态: " + first_beat + "\n"
            "位置/构图: (待填写 — 焦距 / frame 占比, 与 video 镜头一致)\n"
            "表情: (待填写 — 起始情绪锚点)\n"
            "道具: (待填写)"
        )
    return _PLACEHOLDER_START


def _build_end_block(last_beat: str | None) -> str:
    if last_beat:
        return (
            "角色姿态: " + last_beat + "\n"
            "位置/构图: (待填写 — 镜头收尾位置, 与 video 末段一致)\n"
            "表情: (待填写 — 情绪落点)\n"
            "道具: (待填写 — 与起始帧的变化)"
        )
    return _PLACEHOLDER_END


def transform_shot_file(path: Path) -> tuple[bool, str]:
    text = path.read_text(encoding="utf-8")

    # Idempotency: skip if both headings already exist.
    if _EXISTING_START_HEADING_RE.search(text) and _EXISTING_END_HEADING_RE.search(text):
        return False, "already has 起始帧 + 结束帧 blocks"

    video_heading = _VIDEO_HEADING_RE.search(text)
    if video_heading is None:
        return False, "no `## 视频 prompt` heading found"

    code_block = _TEXT_BLOCK_RE.search(text)
    if code_block is None:
        return False, "no ```text code block found"
    first_beat, last_beat, duration_str = _extract_beats(code_block.group(1))

    duration_label = duration_str or "duration"
    start_block = (
        "## 起始帧 (shot 起始 0s 时画面状态 — 描述 t=0 静帧, 不含运动)\n\n"
        "```text\n"
        f"{_build_start_block(first_beat)}\n"
        "```\n\n"
    )
    end_block = (
        f"## 结束帧 (shot 结束 {duration_label} 时画面状态 — 描述末帧静态落点)\n\n"
        "```text\n"
        f"{_build_end_block(last_beat)}\n"
        "```\n\n"
    )

    insertion = start_block + end_block
    new_text = text[: video_heading.start()] + insertion + text[video_heading.start():]

    path.write_text(new_text, encoding="utf-8", newline="\n")
    populated = bool(first_beat and last_beat)
    return True, f"inserted start + end blocks ({'auto-extracted from 动作 beats' if populated else 'placeholders'})"


def run_drama(drama_dir: Path) -> tuple[int, int]:
    files = sorted(drama_dir.glob("episodes/*/shots/*/*.md"))
    if not files:
        return 0, 0
    print(f"\n=== {drama_dir.name} ({len(files)} shot files) ===")
    changed = 0
    for f in files:
        rel = f.relative_to(drama_dir).as_posix()
        try:
            did, msg = transform_shot_file(f)
        except Exception as exc:
            print(f"  ! {rel}  ERROR: {exc}")
            continue
        marker = "*" if did else " "
        print(f"  {marker} {rel}  — {msg}")
        if did:
            changed += 1
    return len(files), changed


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__, file=sys.stderr)
        return 2
    if argv[0] == "--all":
        targets = [
            p for p in sorted(AI_VIDEOS.iterdir())
            if p.is_dir() and not p.name.startswith("_")
        ]
    else:
        d = AI_VIDEOS / argv[0]
        if not d.is_dir():
            print(f"ERROR: drama folder not found: {d}", file=sys.stderr)
            return 1
        targets = [d]
    total = changed = 0
    for d in targets:
        n, c = run_drama(d)
        total += n
        changed += c
    print(f"\nTotal: {changed} files changed / {total} files scanned")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
