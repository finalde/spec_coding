"""Subtitle-cue domain knowledge: parse the per-shot `subtitles.md`
dialogue-timeline into bilingual cues, and render those cues as an ASS
subtitle script for ffmpeg burn-in, in one of three language modes.

The per-shot file format (one cue per line; `#` / blank / fence lines are
ignored) is lenient on purpose — authors hand-edit it. Each cue carries a
Chinese line and (optionally) an English line, separated by `||`:

    0-3      老天爷，竟真让我重活一回。 || Heavens — I really have lived again.
    3-5.5    （内心）这一世我绝不再忍。 || This life, I will never yield again.
    5.5-8    你们，都等着。              || Just you all wait.

A line with no `||` is Chinese-only (English empty) — backward compatible
with the original zh-only format.

内心独白 (OS) carries no special styling — it is a normal bottom-centered
hard subtitle, only its time window differs (per feature decision).

Burn modes (`lang`):
  - "zh"   : Chinese line only.
  - "en"   : English line only.
  - "both" : Chinese stacked above English (smaller).
"""
from __future__ import annotations

import re
from dataclasses import dataclass

# start[-~至]end  optional colon separator  text (text may carry a `||` zh/en
# split — so `|` is NOT a time-text separator here, it is the bilingual delim).
_CUE_RE = re.compile(
    r"^\s*(\d+(?:\.\d+)?)\s*[-–~至]\s*(\d+(?:\.\d+)?)\s*[:：]?\s*(\S.*?)\s*$"
)
_BILINGUAL_SEP = "||"

VALID_LANGS: tuple[str, ...] = ("zh", "en", "both")

# ASS style assumes the project-default 9:16 1080x1920 canvas. libass scales
# the rendered script to the actual video size, so off-default takes still
# render proportionally (divergence note per the spec).
_PLAY_RES_X: int = 1080
_PLAY_RES_Y: int = 1920
_FONT_ZH: str = "微软雅黑"
_FONT_EN: str = "Arial"
_FONT_SIZE_ZH: int = 64
_FONT_SIZE_EN: int = 46
# left/right safe margin (px) on the 1080-wide canvas — keeps text off the edges.
# Usable text width = 1080 - 2*120 = 840px.
_MARGIN_LR: int = 120
# bottom margin (px from frame bottom). Raised off the very bottom so subtitles
# don't kiss the frame edge. "both" renders zh+en as one bottom-anchored block.
_MARGIN_V_SOLO: int = 170
# Max characters per line before wrapping to the next line. A line that doesn't
# fit the 840px safe width is split into balanced lines (mobile 9:16: long 台词
# must wrap to 2+ lines, never overflow). zh full-width ≈ font px; latin ≈ half.
_MAX_CHARS_ZH: int = 13   # 13*64 ≈ 832 < 840
_MAX_CHARS_EN: int = 32


@dataclass(frozen=True)
class SubtitleCue:
    start: float
    end: float
    zh: str
    en: str

    def text_for(self, lang: str) -> str:
        if lang == "zh":
            return self.zh
        if lang == "en":
            return self.en
        return self.zh or self.en  # "both": present if either side has text


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
        raw = m.group(3).strip()
        if _BILINGUAL_SEP in raw:
            zh_part, en_part = raw.split(_BILINGUAL_SEP, 1)
            zh, en = zh_part.strip(), en_part.strip()
        else:
            zh, en = raw, ""
        if end <= start or not (zh or en):
            continue
        cues.append(SubtitleCue(start=start, end=end, zh=zh, en=en))
    return tuple(cues)


def has_text_for(cues: tuple[SubtitleCue, ...], lang: str) -> bool:
    return any(c.text_for(lang) for c in cues)


def _ass_time(seconds: float) -> str:
    centis = int(round(seconds * 100))
    cs = centis % 100
    total_s = centis // 100
    s = total_s % 60
    m = (total_s // 60) % 60
    h = total_s // 3600
    return f"{h:d}:{m:02d}:{s:02d}.{cs:02d}"


def _wrap(text: str, max_chars: int) -> str:
    """Break a single subtitle line into balanced lines of <= max_chars so it
    always fits the safe width (mobile 9:16). Inserts real newlines, which
    `_ass_text` converts to ASS `\\N`. Balanced split: e.g. 20 chars / max 13
    → two ~10-char lines rather than 13+7. Whitespace-delimited where possible
    (latin); otherwise hard char split (CJK has no spaces)."""
    text = text.strip()
    if len(text) <= max_chars:
        return text
    n_lines = -(-len(text) // max_chars)  # ceil
    per = -(-len(text) // n_lines)        # balanced chars per line
    # Prefer breaking at a space near each boundary (latin); fall back to a hard
    # cut at `per` (CJK).
    lines: list[str] = []
    rest = text
    while len(rest) > per:
        window = rest[:per]
        cut = window.rfind(" ")
        if cut < per // 2:  # no good space → hard cut (CJK / long token)
            cut = per
        lines.append(rest[:cut].strip())
        rest = rest[cut:].strip()
    if rest:
        lines.append(rest)
    return "\n".join(lines)


def _ass_text(text: str) -> str:
    # `{`/`}` start ASS override blocks; neutralise so dialogue renders literally.
    return text.replace("{", "(").replace("}", ")").replace("\n", r"\N")


def _style_row(name: str, font: str, size: int) -> str:
    return (
        f"Style: {name},{font},{size},&H00FFFFFF,&H000000FF,"
        f"&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,3,0,2,"
        f"{_MARGIN_LR},{_MARGIN_LR},{_MARGIN_V_SOLO},1"
    )


def _dialogue(
    start: float, end: float, style: str, margin_v: int, text: str
) -> str:
    """`text` is already wrapped (may contain real newlines)."""
    return (
        f"Dialogue: 0,{_ass_time(start)},{_ass_time(end)},{style},,0,0,"
        f"{margin_v},,{_ass_text(text)}"
    )


def cues_to_ass(cues: tuple[SubtitleCue, ...], lang: str = "zh") -> str:
    if lang not in VALID_LANGS:
        raise ValueError(f"unknown subtitle lang: {lang!r}")
    header = (
        "[Script Info]\n"
        "ScriptType: v4.00+\n"
        f"PlayResX: {_PLAY_RES_X}\n"
        f"PlayResY: {_PLAY_RES_Y}\n"
        "WrapStyle: 0\n"  # smart auto-wrap (we also pre-wrap long lines manually)
        "ScaledBorderAndShadow: yes\n"
        "\n"
        "[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
        "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, "
        "ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
        "Alignment, MarginL, MarginR, MarginV, Encoding\n"
        f"{_style_row('ZH', _FONT_ZH, _FONT_SIZE_ZH)}\n"
        f"{_style_row('EN', _FONT_EN, _FONT_SIZE_EN)}\n"
        "\n"
        "[Events]\n"
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, "
        "Effect, Text\n"
    )
    lines: list[str] = []
    for c in cues:
        if lang == "zh":
            if c.zh:
                lines.append(
                    _dialogue(c.start, c.end, "ZH", _MARGIN_V_SOLO,
                              _wrap(c.zh, _MAX_CHARS_ZH))
                )
        elif lang == "en":
            if c.en:
                lines.append(
                    _dialogue(c.start, c.end, "EN", _MARGIN_V_SOLO,
                              _wrap(c.en, _MAX_CHARS_EN))
                )
        else:  # both — one bottom-anchored block, zh line(s) above en line(s),
               # so multi-line wraps never overlap. Single ZH style.
            parts = []
            if c.zh:
                parts.append(_wrap(c.zh, _MAX_CHARS_ZH))
            if c.en:
                parts.append(_wrap(c.en, _MAX_CHARS_EN))
            if parts:
                lines.append(
                    _dialogue(c.start, c.end, "ZH", _MARGIN_V_SOLO, "\n".join(parts))
                )
    return header + "\n".join(lines) + "\n"
