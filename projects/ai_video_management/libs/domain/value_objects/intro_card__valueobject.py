"""Character intro-card domain knowledge (ai_video.md rule 11d).

The intro card is an **image asset** — a complete per-character nameplate PNG
(frame + 烫金 name + identity, designed by the user in Kling/即梦) with a
transparent background, kept **per drama** under `2_世界观人设/intro_cards/`
(Chinese filenames, matching the character bibles). The burn simply composites
that PNG onto a shot's top corner with a fade in/out; nothing is drawn
programmatically.

Parse a per-episode `intro_cards.md` into intro cards.

`intro_cards.md` line format (one card per line, inside a ```text fence;
`#` / blank / fence lines ignored), pipe-separated:

    角色 | 首登shot | 出现点(秒) | 卡图 | 位置(右上/左上) | 显示时长(秒) | 宽度占比

`卡图` is the RAW reference, resolved by the writer against THIS drama: a bare id
(`裴知秋` → the drama's `intro_cards/裴知秋.png`), a drama-relative path, or a
full sandbox path. `宽度占比` (overlay width as a fraction of the video width) is
optional — defaults to 0.28; a value > 1 is treated as a percentage. `位置` →
top-right unless it says 左/left.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

_FENCE_OR_COMMENT = ("#", "```", ">")
_DEFAULT_WIDTH_FRAC = 0.28
_MIN_WIDTH_FRAC = 0.10
_MAX_WIDTH_FRAC = 0.60


@dataclass(frozen=True)
class IntroCard:
    shot: str          # e.g. "shot01"
    at: float          # appear time in seconds (into the shot)
    duration: float    # on-screen seconds
    image_ref: str     # RAW card reference (writer resolves it per drama)
    corner: str        # "tr" (top-right) | "tl" (top-left)
    width_frac: float  # overlay width as a fraction of the video width
    label: str         # character name (for reporting / docs)


def parse_intro_cards(md_text: str) -> tuple[IntroCard, ...]:
    cards: list[IntroCard] = []
    for line in md_text.splitlines():
        s = line.strip()
        if not s or s.startswith(_FENCE_OR_COMMENT) or "|" not in s:
            continue
        parts = [p.strip() for p in s.split("|")]
        if len(parts) < 6:
            continue
        label = parts[0]
        shot = _norm_shot(parts[1])
        at = _to_float(parts[2])
        image = parts[3].strip().strip("`")
        corner = _norm_corner(parts[4])
        dur = _to_float(parts[5])
        width = _norm_width(parts[6]) if len(parts) >= 7 else _DEFAULT_WIDTH_FRAC
        if not shot or at is None or dur is None or dur <= 0 or not image:
            continue
        cards.append(IntroCard(shot, at, dur, image, corner, width, label))
    return tuple(cards)


def cards_for_shot(cards: tuple[IntroCard, ...], shot: str) -> tuple[IntroCard, ...]:
    target = _norm_shot(shot)
    return tuple(sorted((c for c in cards if c.shot == target), key=lambda c: c.at))


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


def _norm_width(s: str) -> float:
    v = _to_float(s)
    if v is None:
        return _DEFAULT_WIDTH_FRAC
    if v > 1:
        v = v / 100.0
    return max(_MIN_WIDTH_FRAC, min(_MAX_WIDTH_FRAC, v))
