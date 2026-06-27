"""CharacterViewSpec — the 3-angle schedule for character turntable extraction.

Per follow-up 093: extract 3 still frames (front / side / back) + the full
audio track from a character turntable mp4 (per
`.claude/agent_refs/project/ai_video.md` rule #12.5). The turntable keeps
3 static landings (front / side / back) joined by 2 short motion bridges so
each pick is taken from a guaranteed-static moment.

Per 2026-06-27 follow-up the turntable is COMPRESSED 7s → 4s (same
front→side→back arc done inside 4s). The 3 timestamps are the algebraic
image of the 4s 5-phase camera path:

  0-1s   static front lock         → front pick at t=0.5s (mid static intro)
  1-1.5s motion 0° → 90°
  1.5-2.5s static side lock        → side  pick at t=2.0s (mid static)
  2.5-3s motion 90° → 180°
  3-4s   static back lock + settle → back  pick at t=3.5s (mid static)

All 3 picks share IDENTICAL medium-full framing because the take forbids any
dolly / zoom — only the angle changes between landings. If rule #12.5's
phase schedule changes again, these constants must change too.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CharacterViewSpec:
    timestamp: float
    role: str


CANONICAL_VIEWS: tuple[CharacterViewSpec, ...] = (
    CharacterViewSpec(0.5, "front"),
    CharacterViewSpec(2.0, "side"),
    CharacterViewSpec(3.5, "back"),
)


def view_output_filename(prefix: str, spec: CharacterViewSpec) -> str:
    """`{prefix}_{role}.png` per follow-up 093."""
    return f"{prefix}_{spec.role}.png"


def audio_output_filename(prefix: str) -> str:
    """`{prefix}_audio.mp3` per follow-up 093."""
    return f"{prefix}_audio.mp3"


TRIM_DURATION_S: float = 2.0


def trim_output_filename(prefix: str) -> str:
    """`{prefix}_trim{N}s.mp4` — the first `TRIM_DURATION_S` seconds of the
    source turntable mp4, emitted alongside the 3 view PNGs + audio so a single
    click yields all 5 files. The `{N}s` in the name is derived from
    `TRIM_DURATION_S`, so changing the constant renames the output in lockstep
    (2s per the 2026-06-27 follow-up — sample window aligned to the 0-2s
    front-lock phase)."""
    return f"{prefix}_trim{int(TRIM_DURATION_S)}s.mp4"
