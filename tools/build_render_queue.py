"""Generate a copy-paste render queue per emotion: `{emotion}/_render_queue.md`.

Extracts every render-prompt block (起始帧 / Kling / Seedance) from each
`perf_NNNN.md` in entry order and lays them out as a top-to-bottom checklist the
user works through — copy a block, paste into Seedream/Kling/Seedance, download,
then one-click import (the first-line `演{NNNN}{克|即|始}` tag routes the file).

Regenerate after authoring/editing entries. This file is GENERATED — do not edit
by hand; edits belong in the source `perf_NNNN.md`.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

PERF_ROOT = Path(__file__).resolve().parent.parent / "ai_videos" / "_performances"
_PERF_NUM = re.compile(r"perf_(\d{4})")
_BLOCK_HEADERS = ("## 起始帧表情", "## 检验视频")


def _extract_blocks(md: str) -> list[tuple[str, str]]:
    """Return (label, fenced-body) for each render block, in source order."""
    lines = md.splitlines()
    blocks: list[tuple[str, str]] = []
    i = 0
    pending: str | None = None
    while i < len(lines):
        line = lines[i].strip()
        if any(line.startswith(h) for h in _BLOCK_HEADERS):
            pending = line.lstrip("# ").strip()
            i += 1
            continue
        if line == "```" and pending is not None:
            body: list[str] = []
            i += 1
            while i < len(lines) and lines[i].strip() != "```":
                body.append(lines[i])
                i += 1
            blocks.append((pending, "\n".join(body)))
            pending = None
        i += 1
    return blocks


def _title(md: str) -> str:
    for line in md.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def build_emotion(emotion_dir: Path) -> int:
    perf_files = sorted(emotion_dir.glob("perf_*/perf_*.md"))
    if not perf_files:
        return 0
    emotion_title = ""
    em_md = emotion_dir / "_emotion.md"
    if em_md.is_file():
        emotion_title = _title(em_md.read_text(encoding="utf-8"))
    out: list[str] = []
    out.append(f"# 渲染队列 — {emotion_title or emotion_dir.name}")
    out.append("")
    out.append(
        "> **GENERATED — 勿手改**（由 `tools/build_render_queue.py` 生成；源在各 `perf_NNNN.md`）。"
    )
    out.append(
        "> 用法：上传你的 actor 参考照；从上到下，每个代码块整段复制（**含首行 tag**：`演{编号}`=检验视频 / "
        "`演{编号}始`=起始帧静帧）→ 起始帧块粘进 Seedream/即梦生成静帧、检验视频块粘进任意视频模型（Kling/Seedance/…）"
        "image-to-video 生成 → 下载 → 点侧栏「📥 导入检验视频」一键归位 → 在该 entry 的 `## 实测与验证` 回填三轴分数。"
    )
    out.append("")
    total = 0
    for pf in perf_files:
        num = _PERF_NUM.search(pf.stem).group(1)
        md = pf.read_text(encoding="utf-8")
        title = _title(md)
        blocks = _extract_blocks(md)
        if not blocks:
            continue
        out.append(f"## {title}")
        out.append("")
        for label, body in blocks:
            out.append(f"### {title.split('·', 1)[0].strip()} — {label}")
            out.append("")
            out.append("```")
            out.append(body)
            out.append("```")
            out.append("")
            total += 1
    queue_path = emotion_dir / "_render_queue.md"
    queue_path.write_text("\n".join(out) + "\n", encoding="utf-8")
    return total


def main() -> None:
    emotions = 0
    blocks = 0
    for emotion_dir in sorted(PERF_ROOT.iterdir()):
        if not emotion_dir.is_dir() or emotion_dir.name.startswith("_"):
            continue
        n = build_emotion(emotion_dir)
        if n:
            emotions += 1
            blocks += n
    sys.stdout.write(f"built render queues for {emotions} emotions, {blocks} prompt blocks\n")


if __name__ == "__main__":
    main()
