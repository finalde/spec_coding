"""Collapse each entry's render prompts to ONE generic, actor-agnostic,
model-agnostic block (follow-up 003).

Per-entry transform (the `## 锁定文本块` / `## 配套镜头` / `## 实测与验证`
sections are left untouched — only the render wrappers change):
- `## 检验视频`: the two near-identical `### Kling 版` + `### Seedance 版` blocks
  collapse into ONE generic block. The hardcoded `actor_0001…纯灰背景…中性白光`
  wrapper is replaced by `[演员: 上传任意 actor 参考照]` + 表演室 + the emotion's
  `灯光氛围`. Import tag `演{NNNN}克/即` → `演{NNNN}`.
- `## 起始帧表情`: the Seedream block becomes actor-agnostic (drop actor_0001,
  swap neutral wall/light for 表演室 + emotion lighting). Tag stays `演{NNNN}始`.

The performance text (`表演（唯一变量）:` → now `表演:`) and the startframe peak
(`表情：…`) are EXTRACTED and preserved byte-for-byte — they are the asset.
Idempotent: a file already on the generic format (no `### Kling 版`) is skipped.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

PERF_ROOT = Path(__file__).resolve().parent.parent / "ai_videos" / "_performances"
_NUM = re.compile(r"perf_(\d{4})")
_LIGHTING = re.compile(r"^灯光氛围（检验视频）:\s*(.+)$")
_PERF_LINE = re.compile(r"^表演(?:（唯一变量）)?:\s*(.+)$")


def _lighting_for(emotion_dir: Path) -> str:
    md = emotion_dir / "_emotion.md"
    if md.is_file():
        for line in md.read_text(encoding="utf-8").splitlines():
            m = _LIGHTING.match(line.strip())
            if m:
                return m.group(1).strip()
    return "按情绪氛围布光"


def _sections(body_lines: list[str]) -> list[tuple[str, list[str]]]:
    """Split body into (heading, lines-including-heading) by `## ` headers.
    Content before the first `## ` is returned under heading ''."""
    out: list[tuple[str, list[str]]] = []
    cur_head = ""
    cur: list[str] = []
    for line in body_lines:
        if line.startswith("## "):
            out.append((cur_head, cur))
            cur_head = line[3:].strip()
            cur = [line]
        else:
            cur.append(line)
    out.append((cur_head, cur))
    return out


def _fenced_body(section: list[str]) -> list[str]:
    body: list[str] = []
    in_fence = False
    for line in section:
        if line.strip() == "```":
            if in_fence:
                break
            in_fence = True
            continue
        if in_fence:
            body.append(line)
    return body


def _extract_perf(sections: list[tuple[str, list[str]]]) -> str | None:
    for head, lines in sections:
        if head == "检验视频":
            for line in _fenced_body(lines):
                m = _PERF_LINE.match(line.strip())
                if m:
                    return m.group(1).strip()
    return None


def _extract_peak(sections: list[tuple[str, list[str]]]) -> str | None:
    for head, lines in sections:
        if head.startswith("起始帧表情"):
            for line in _fenced_body(lines):
                m = re.search(r"表情[^：]*：(.+)", line)  # 表情：/ 表情与姿态：
                if m:
                    return m.group(1).strip()
    return None


def _has_startframe(sections: list[tuple[str, list[str]]]) -> bool:
    return any(h.startswith("起始帧表情") for h, _ in sections)


def _new_checkvideo(num: str, lighting: str, perf: str, startframe: bool) -> list[str]:
    note = (
        "> 通用 prompt（model-agnostic）：上传你的 actor 参考照（image-to-video，任意演员），"
        "场景为表演室、灯光按本情绪氛围。控制变量见 `_performances/_testrig.md`；"
        "同一情绪内比较不同 entry 用同一张参考照，唯一变量 = 表演描述。"
    )
    block = ["## 检验视频", "", note, "", "```", f"演{num}", "[演员: 上传任意 actor 参考照，image-to-video]",
             f"表演室内，近景，正面平视，镜头静止，{lighting}，9:16，时长 5 秒。"]
    if startframe:
        block.append("[起始帧: 本条 ## 起始帧表情 生成的静帧]")
    block.append(f"表演: {perf}")
    block.append("```")
    block.append("")
    return block


def _new_startframe(num: str, lighting: str, peak: str) -> list[str]:
    note = (
        "> 本条默认起始帧模式：用下方 Seedream prompt（基于你上传的 actor 参考照 + 峰值表情）"
        "生成一张峰值静帧，作 image-to-video 起始帧；检验视频只承担从该帧出发的动作插值。"
    )
    return [
        "## 起始帧表情", "", note, "", "```", f"演{num}始",
        f"[演员: 上传任意 actor 参考照]表演室内，近景特写，正面平视，{lighting}，9:16。表情：{peak}",
        "```", "",
    ]


def genericize(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if "### Kling 版" not in text:
        return False  # already generic
    num = _NUM.search(path.stem).group(1)
    emotion_dir = path.parent.parent
    lighting = _lighting_for(emotion_dir)
    lines = text.splitlines()
    # split frontmatter (first --- ... ---) from body
    fm: list[str] = []
    body_start = 0
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                fm = lines[: i + 1]
                body_start = i + 1
                break
    body = lines[body_start:]
    secs = _sections(body)
    perf = _extract_perf(secs)
    if perf is None:
        sys.stderr.write(f"SKIP (no 表演 line): {path}\n")
        return False
    startframe = _has_startframe(secs)
    peak = _extract_peak(secs) if startframe else None

    out: list[str] = list(fm)
    for head, sec_lines in secs:
        if head == "检验视频":
            out += _new_checkvideo(num, lighting, perf, startframe)
        elif head.startswith("起始帧表情"):
            if peak is not None:
                out += _new_startframe(num, lighting, peak)
            else:
                out += sec_lines
        else:
            out += sec_lines
    # normalize: collapse trailing blank lines to one
    while len(out) >= 2 and out[-1] == "" and out[-2] == "":
        out.pop()
    path.write_text("\n".join(out).rstrip("\n") + "\n", encoding="utf-8")
    return True


def main() -> None:
    changed = 0
    for f in sorted(PERF_ROOT.glob("*/perf_*/perf_*.md")):
        if genericize(f):
            changed += 1
    sys.stdout.write(f"genericized {changed} entries\n")


if __name__ == "__main__":
    main()
