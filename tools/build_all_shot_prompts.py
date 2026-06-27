#!/usr/bin/env python3
"""Rebuild an episode's `all_shot_prompts.md` from its `shotNN.md` sources.

`all_shot_prompts.md` is a READ-ONLY derived snapshot — `shots/shotNN/shotNN.md`
is the single source of truth. Edit the shots, then run this to recompile the
snapshot; never hand-edit the snapshot (hand edits drift from the sources).

It aggregates, per shot in numeric order:
  - the H1 title (`# ep{NN} / shotNN · ...`) -> `## shotNN · ...` section head,
  - the `## 视频 prompt` ```text block,
  - the `## 台词配音 prompt` ```text block, if the shot is a speaking shot.

The human-curated header (everything above the first `## shot` line) is
preserved verbatim from the existing snapshot; only the per-shot body is rebuilt.
If no snapshot exists yet, a minimal default header is written.

Usage:
    python tools/build_all_shot_prompts.py <episode_dir> [<episode_dir> ...]
    python tools/build_all_shot_prompts.py --all <episodes_dir>

Examples:
    python tools/build_all_shot_prompts.py \
        ai_videos/wushen_juexing/5_6_分镜与prompt/episodes/ep04
    python tools/build_all_shot_prompts.py --all \
        ai_videos/wushen_juexing/5_6_分镜与prompt/episodes
"""
from __future__ import annotations

import glob
import os
import re
import sys

VIDEO_HEADING = "视频 prompt"
TTS_HEADING = "台词配音 prompt"


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _text_block(source: str, heading: str) -> str | None:
    pattern = r"##\s*" + re.escape(heading) + r".*?\n```text\n(.*?)\n```"
    match = re.search(pattern, source, re.S)
    return match.group(1) if match else None


def _section_title(source: str) -> str | None:
    match = re.search(r"^#\s*ep\d+\s*/\s*(.+?)\s*$", source, re.M)
    return match.group(1) if match else None


def _duration_seconds(source: str) -> int:
    match = re.search(r"^时长:\s*`?\s*(\d+)", source, re.M)
    return int(match.group(1)) if match else 0


def _existing_header(snapshot_path: str) -> str | None:
    if not os.path.exists(snapshot_path):
        return None
    head_lines: list[str] = []
    for line in _read(snapshot_path).splitlines():
        if re.match(r"^##\s*shot", line):
            break
        head_lines.append(line)
    return "\n".join(head_lines).rstrip() + "\n"


def _default_header(ep_dir: str) -> str:
    ep = os.path.basename(ep_dir.rstrip("/\\")).upper()
    return (
        f"# {ep} 全镜 prompt 汇编（只读快照）\n\n"
        "> ⚠ 只读快照——改各 `shots/shotNN/shotNN.md` 源后用 "
        "`tools/build_all_shot_prompts.py` 重新汇编，勿手改本文件。\n"
        "> 复制每镜 `视频 prompt` 代码块进 Seedance/Kling 出片；"
        "`台词配音` 块喂 TTS。\n"
    )


def build_episode(ep_dir: str) -> tuple[int, int]:
    shot_files = sorted(
        glob.glob(os.path.join(ep_dir, "shots", "shot*", "shot*.md"))
    )
    if not shot_files:
        raise SystemExit(f"no shot sources under {ep_dir}/shots/")

    snapshot_path = os.path.join(ep_dir, "all_shot_prompts.md")
    parts: list[str] = [_existing_header(snapshot_path) or _default_header(ep_dir)]

    total_seconds = 0
    for shot_file in shot_files:
        source = _read(shot_file)
        name = os.path.basename(os.path.dirname(shot_file))
        title = _section_title(source) or name
        video = _text_block(source, VIDEO_HEADING)
        if video is None:
            raise SystemExit(f"{shot_file}: missing `## {VIDEO_HEADING}` block")
        total_seconds += _duration_seconds(source)

        parts.append(f"\n## {title}\n```text\n{video}\n```\n")
        tts = _text_block(source, TTS_HEADING)
        if tts is not None:
            parts.append(f"\n### 台词配音 prompt\n```text\n{tts}\n```\n")

    with open(snapshot_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("".join(parts))

    return len(shot_files), total_seconds


def main(argv: list[str]) -> None:
    if not argv:
        raise SystemExit(__doc__)

    if argv[0] == "--all":
        if len(argv) != 2:
            raise SystemExit("--all takes exactly one <episodes_dir>")
        ep_dirs = sorted(
            d for d in glob.glob(os.path.join(argv[1], "ep*")) if os.path.isdir(d)
        )
    else:
        ep_dirs = argv

    for ep_dir in ep_dirs:
        shots, seconds = build_episode(ep_dir)
        snapshot = os.path.join(ep_dir, "all_shot_prompts.md")
        print(f"rebuilt {snapshot} — {shots} 镜 / {seconds}s", file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv[1:])
