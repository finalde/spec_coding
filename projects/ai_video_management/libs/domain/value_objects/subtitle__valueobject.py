"""Subtitle-cue domain knowledge: parse the per-shot `subtitles.md`
dialogue-timeline into cues, and render those cues as an ASS subtitle
script for ffmpeg burn-in.

The per-shot file format (one cue per line; `#` / blank / fence lines are
ignored) is lenient on purpose — authors hand-edit it:

    0-3      老天爷，竟真让我重活一回。
    3-5.5    （内心）这一世，我裴知秋绝不再忍。
    5.5-8    你们，都等着。

内心独白 (OS) carries no special styling — it is a normal bottom-centered
hard subtitle, only its time window differs (per feature decision).
"""
from __future__ import annotations

import re
from dataclasses import dataclass

# start[-~至]end  optional separator  text
_CUE_RE = re.compile(
    r"^\s*(\d+(?:\.\d+)?)\s*[-–~至]\s*(\d+(?:\.\d+)?)\s*[|｜:：]?\s*(\S.*?)\s*$"
)

# ASS style assumes the project-default 9:16 1080x1920 canvas. libass scales
# the rendered script to the actual video size, so off-default takes still
# render proportionally (divergence note per the spec).
_PLAY_RES_X: int = 1080
_PLAY_RES_Y: int = 1920
_FONT_NAME: str = "微软雅黑"
_FONT_SIZE: int = 72


@dataclass(frozen=True)
class SubtitleCue:
    start: float
    end: float
    text: str


def parse_subtitles(md_text: str) -> tuple[SubtitleCue, ...]:
    cues: list[SubtitleCue] = []
    for line in md_text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("```"):
            continue
        m = _CUE_RE.match(line)
        if m is None:
            continue
        start = float(m.group(1))
        end = float(m.group(2))
        text = m.group(3).strip()
        if end <= start or not text:
            continue
        cues.append(SubtitleCue(start=start, end=end, text=text))
    return tuple(cues)


def _ass_time(seconds: float) -> str:
    centis = int(round(seconds * 100))
    cs = centis % 100
    total_s = centis // 100
    s = total_s % 60
    m = (total_s // 60) % 60
    h = total_s // 3600
    return f"{h:d}:{m:02d}:{s:02d}.{cs:02d}"


def _ass_text(text: str) -> str:
    # `{`/`}` start ASS override blocks; neutralise so dialogue renders literally.
    return text.replace("{", "(").replace("}", ")").replace("\n", r"\N")


def cues_to_ass(cues: tuple[SubtitleCue, ...]) -> str:
    header = (
        "[Script Info]\n"
        "ScriptType: v4.00+\n"
        f"PlayResX: {_PLAY_RES_X}\n"
        f"PlayResY: {_PLAY_RES_Y}\n"
        "WrapStyle: 2\n"
        "ScaledBorderAndShadow: yes\n"
        "\n"
        "[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
        "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, "
        "ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
        "Alignment, MarginL, MarginR, MarginV, Encoding\n"
        f"Style: Default,{_FONT_NAME},{_FONT_SIZE},&H00FFFFFF,&H000000FF,"
        "&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,3,0,2,60,60,80,1\n"
        "\n"
        "[Events]\n"
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, "
        "Effect, Text\n"
    )
    lines = [
        f"Dialogue: 0,{_ass_time(c.start)},{_ass_time(c.end)},Default,,0,0,0,,"
        f"{_ass_text(c.text)}"
        for c in cues
    ]
    return header + "\n".join(lines) + "\n"
