"""Character intro-card domain knowledge (ai_video.md rule 11d).

Parse a per-episode `intro_cards.md` into intro cards, and render the cards as
an ASS subtitle script for a **corner framed nameplate overlay** — the video
keeps playing smoothly (no freeze); each card fades in at its appear-time in a
top corner, mounted in an ornate gold frame, then fades out.

`intro_cards.md` line format (one card per line, inside a ```text fence;
`#` / blank / fence lines ignored), pipe-separated:

    角色 | 首登shot | 出现点(秒) | 主名 | 副身份 | 边框样式 | 位置(右上/左上) | 显示时长(秒)

Load-bearing: `首登shot`, `出现点`, `主名`, `副身份`, `位置`, `显示时长`.
`边框样式` is an author note (the burn uses the locked framed-plate style). A
row missing the shot id or a positive duration is skipped; at least one of
`主名`/`副身份` must be non-empty. `位置` → top-right unless it says 左/left.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

_FENCE_OR_COMMENT = ("#", "```", ">")

# canvas matches the subtitle burn (9:16 1080x1920); libass scales to real size.
_PLAY_RES_X: int = 1080
_PLAY_RES_Y: int = 1920
_FONT_MAIN: str = "楷体"          # 古风书法感; libass substitutes if absent
_FONT_SUB: str = "微软雅黑"
_FS_MAIN: int = 72
_FS_SUB: int = 40
# warm 描金 gold name / cold white sub / gold frame border / dark translucent plate.
_C_MAIN: str = "&H0070C8F0"       # ASS &HAABBGGRR (gold)
_C_SUB: str = "&H00F0F0F0"
_C_FRAME: str = "&H0060B8E8"      # gold box border (OutlineColour)
_C_PLATE: str = "&H78201810"      # box fill (BackColour) — ~47% alpha warm dark
_MARGIN_H: int = 60               # distance from the left/right frame edge
_MARGIN_TOP: int = 80             # distance from the top frame edge
_FADE_MS: int = 350


@dataclass(frozen=True)
class IntroCard:
    shot: str          # e.g. "shot01"
    at: float          # appear time in seconds (into the shot)
    duration: float    # on-screen seconds
    main: str          # 主名 (character name)
    sub: str           # 副身份 (one-line identity)
    corner: str        # "tr" (top-right) | "tl" (top-left)


def parse_intro_cards(md_text: str) -> tuple[IntroCard, ...]:
    cards: list[IntroCard] = []
    for line in md_text.splitlines():
        s = line.strip()
        if not s or s.startswith(_FENCE_OR_COMMENT) or "|" not in s:
            continue
        parts = [p.strip() for p in s.split("|")]
        if len(parts) < 8:
            continue
        shot = _norm_shot(parts[1])
        at = _to_float(parts[2])
        main, sub = parts[3], parts[4]
        corner = _norm_corner(parts[6])
        dur = _to_float(parts[7])
        if not shot or at is None or dur is None or dur <= 0:
            continue
        if not (main or sub):
            continue
        cards.append(IntroCard(shot, at, dur, main, sub, corner))
    return tuple(cards)


def cards_for_shot(cards: tuple[IntroCard, ...], shot: str) -> tuple[IntroCard, ...]:
    target = _norm_shot(shot)
    return tuple(sorted((c for c in cards if c.shot == target), key=lambda c: c.at))


def cards_to_ass(cards: tuple[IntroCard, ...]) -> str:
    """One ASS overlay holding every card as a timed, corner-anchored, framed
    nameplate. The video is NOT frozen — each card simply fades in over the
    moving footage at [at, at+duration]."""
    header = (
        "[Script Info]\n"
        "ScriptType: v4.00+\n"
        f"PlayResX: {_PLAY_RES_X}\n"
        f"PlayResY: {_PLAY_RES_Y}\n"
        "WrapStyle: 2\n"
        "ScaledBorderAndShadow: yes\n\n"
        "[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
        "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, "
        "ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
        "Alignment, MarginL, MarginR, MarginV, Encoding\n"
        # BorderStyle 3 = opaque box (the framed plate): Outline=box border,
        # BackColour=plate fill. Alignment 9 (top-right) is the default; each
        # event overrides with \an for top-left.
        f"Style: CARD,{_FONT_SUB},{_FS_SUB},{_C_SUB},&H000000FF,{_C_FRAME},"
        f"{_C_PLATE},0,0,0,0,100,100,0,0,3,3,2,9,"
        f"{_MARGIN_H},{_MARGIN_H},{_MARGIN_TOP},1\n\n"
        "[Events]\n"
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, "
        "Effect, Text\n"
    )
    events: list[str] = []
    for c in cards:
        an = 7 if c.corner == "tl" else 9
        pieces: list[str] = []
        if c.main:
            pieces.append(
                f"{{\\fn{_FONT_MAIN}\\fs{_FS_MAIN}\\b1\\1c{_C_MAIN}}}"
                f"{_ass_escape(c.main)}"
            )
        if c.sub:
            pieces.append(
                f"{{\\fn{_FONT_SUB}\\fs{_FS_SUB}\\b0\\1c{_C_SUB}}}{_ass_escape(c.sub)}"
            )
        body = r"\N".join(pieces)
        events.append(
            f"Dialogue: 0,{_ass_time(c.at)},{_ass_time(c.at + c.duration)},CARD,,0,0,0,,"
            f"{{\\an{an}\\fad({_FADE_MS},{_FADE_MS})}}{body}"
        )
    return header + "\n".join(events) + "\n"


def _norm_shot(s: str) -> str:
    m = re.search(r"shot\s*0*(\d+)", s, re.IGNORECASE)
    return f"shot{int(m.group(1)):02d}" if m else ""


def _norm_corner(s: str) -> str:
    low = s.lower()
    if "左" in s or "tl" in low or "left" in low:
        return "tl"
    return "tr"


def _to_float(s: str) -> float | None:
    m = re.search(r"(\d+(?:\.\d+)?)", s)
    return float(m.group(1)) if m else None


def _ass_time(seconds: float) -> str:
    centis = int(round(seconds * 100))
    cs = centis % 100
    total_s = centis // 100
    return f"{total_s // 3600:d}:{(total_s // 60) % 60:02d}:{total_s % 60:02d}.{cs:02d}"


def _ass_escape(text: str) -> str:
    return text.replace("{", "(").replace("}", ")").replace("\n", " ")
