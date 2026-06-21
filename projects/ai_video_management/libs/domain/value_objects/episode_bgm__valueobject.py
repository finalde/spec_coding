"""BgmCue value object + cue-line grammar for the episode BGM timeline.

The episode BGM arrangement lives at `episodes/ep{NN}/bgm/bgm.md` as a SPARSE,
line-oriented timeline: only the dramatic beats that actually want music get a
line; everything else plays with no BGM. One cue per line:

    {start}-{end}  {slot} | cat={category} | vol={v} | duck={on|off} | fade={spec}  # 注释

* `start` / `end` — seconds on the episode timeline (floats ok).
* `slot` — the assigned library track `bgm_NNNN`, or `-` when still a
  placeholder waiting for assignment.
* `cat=` — the DESIRED emotion category (one of the BGM library enum). Kept
  even after assignment so the UI can filter the picker and an unassign can
  restore the `-` placeholder without losing intent.
* `vol=` — 0-1 linear gain (matches the library's cue `vol=` unit).
* `duck=on` — duck this BGM under the episode's own dialogue audio
  (sidechain); `off` lays it flat.
* `fade=` — `in/out` | `in` | `out` | `none`.
* `# …` — free-text author note (the plot beat), ignored by the muxer.

Pure domain: parsing + serialisation + validation, no I/O.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from libs.domain.errors.episode_bgm__error import InvalidBgmCueError
from libs.domain.value_objects.bgm__valueobject import CATEGORY_OPTIONS

_WINDOW_RE = re.compile(r"^(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s+(\S+)$")
_BGM_ID_RE = re.compile(r"^bgm_\d{4,}$")
PLACEHOLDER_SLOT: str = "-"
DEFAULT_VOL: float = 0.6


@dataclass(frozen=True)
class BgmCue:
    start: float
    end: float
    category: str
    bgm_id: str | None = None
    vol: float = DEFAULT_VOL
    duck: bool = True
    fade_in: bool = False
    fade_out: bool = False
    comment: str = ""

    @property
    def window(self) -> float:
        return max(self.end - self.start, 0.0)

    @property
    def assigned(self) -> bool:
        return self.bgm_id is not None

    def to_payload(self) -> dict[str, object]:
        return {
            "start": self.start,
            "end": self.end,
            "category": self.category,
            "bgm_id": self.bgm_id,
            "assigned": self.assigned,
            "vol": self.vol,
            "duck": self.duck,
            "fade_in": self.fade_in,
            "fade_out": self.fade_out,
            "comment": self.comment,
        }


def _fmt_num(value: float) -> str:
    return str(int(value)) if float(value).is_integer() else f"{value:g}"


def _fade_spec(cue: BgmCue) -> str:
    if cue.fade_in and cue.fade_out:
        return "in/out"
    if cue.fade_in:
        return "in"
    if cue.fade_out:
        return "out"
    return "none"


def serialize_cue(cue: BgmCue) -> str:
    slot = cue.bgm_id if cue.bgm_id else PLACEHOLDER_SLOT
    line = (
        f"{_fmt_num(cue.start)}-{_fmt_num(cue.end)}  {slot} "
        f"| cat={cue.category} | vol={_fmt_num(cue.vol)} "
        f"| duck={'on' if cue.duck else 'off'} | fade={_fade_spec(cue)}"
    )
    if cue.comment:
        line += f"  # {cue.comment}"
    return line


def parse_cue_line(line: str) -> BgmCue | None:
    """Parse one cue line, or None if the line is not a cue (header / fence /
    blank / help text). Raises InvalidBgmCueError on a line that LOOKS like a
    cue (valid window prefix) but carries a bad value."""
    stripped = line.strip()
    if not stripped or stripped[0] in "#>`":
        return None
    body = stripped
    comment = ""
    if "#" in body:
        body, comment = body.split("#", 1)
        comment = comment.strip()
        body = body.strip()
    segs = [s.strip() for s in body.split("|")]
    m = _WINDOW_RE.match(segs[0])
    if not m:
        return None
    start = float(m.group(1))
    end = float(m.group(2))
    slot = m.group(3)
    if end < start:
        raise InvalidBgmCueError(f"cue end {end} < start {start}")
    params: dict[str, str] = {}
    for seg in segs[1:]:
        if "=" in seg:
            k, v = seg.split("=", 1)
            params[k.strip().lower()] = v.strip()
    bgm_id = slot if _BGM_ID_RE.match(slot) else None
    category = params.get("cat", "").strip().lower()
    if category and category not in CATEGORY_OPTIONS:
        raise InvalidBgmCueError(f"cat={category!r} not a known BGM category")
    vol = _parse_vol(params.get("vol"))
    duck = params.get("duck", "on").strip().lower() != "off"
    fade = params.get("fade", "none").strip().lower()
    return BgmCue(
        start=start,
        end=end,
        category=category,
        bgm_id=bgm_id,
        vol=vol,
        duck=duck,
        fade_in="in" in fade,
        fade_out="out" in fade,
        comment=comment,
    )


def parse_bgm_cues(text: str) -> list[BgmCue]:
    cues: list[BgmCue] = []
    for raw in text.splitlines():
        cue = parse_cue_line(raw)
        if cue is not None:
            cues.append(cue)
    return cues


def _parse_vol(raw: str | None) -> float:
    if raw is None or raw == "":
        return DEFAULT_VOL
    try:
        v = float(raw)
    except ValueError as exc:
        raise InvalidBgmCueError(f"vol={raw!r} is not a number") from exc
    if not 0.0 <= v <= 1.0:
        raise InvalidBgmCueError(f"vol={v} out of 0-1 range")
    return v
