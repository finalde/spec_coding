"""CharacterViewSpec — the 3-angle schedule for character turntable extraction.

Per follow-up 093: extract 3 still frames (front / side / back) + the full
audio track from a character turntable mp4 (per
`.claude/agent_refs/project/ai_video.md` rule #12.5). Per follow-up 098
the rule is bumped v10 → v10.2 (7s locked-framing 5-phase single-take with
3 static landings + 2 short motion bridges) — empirical evidence (user
report after first v10 renders) was that the model under-rotates v10's
single 4s continuous orbit, leaving the side / back picks in motion segments
rather than at the spec angles. v10.2 introduces explicit static holds at
90° and 180° so each pick is taken from a guaranteed-static moment.

The 3 timestamps are the algebraic image of v10.2's 5-phase camera path:

  0-2s static front lock         → front pick at t=1.0s (mid static intro)
  2-3s motion 0° → 90°
  3-4s static side lock          → side  pick at t=3.5s (mid static, was 4.0s in v10)
  4-5s motion 90° → 180°
  5-7s static back lock + settle → back  pick at t=6.0s (mid static, unchanged)

All 3 picks share IDENTICAL medium-full framing because v10.2 forbids any
dolly / zoom within the take — only the angle changes between landings.
If rule #12.5 changes again (v11+), these constants must change too.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CharacterViewSpec:
    timestamp: float
    role: str


CANONICAL_VIEWS: tuple[CharacterViewSpec, ...] = (
    CharacterViewSpec(1.0, "front"),
    CharacterViewSpec(3.5, "side"),
    CharacterViewSpec(6.0, "back"),
)


def view_output_filename(prefix: str, spec: CharacterViewSpec) -> str:
    """`{prefix}_{role}.png` per follow-up 093."""
    return f"{prefix}_{spec.role}.png"


def audio_output_filename(prefix: str) -> str:
    """`{prefix}_audio.mp3` per follow-up 093."""
    return f"{prefix}_audio.mp3"


TRIM_DURATION_S: float = 3.0


def trim_output_filename(prefix: str) -> str:
    """`{prefix}_trim3s.mp4` — the first `TRIM_DURATION_S` seconds of the source
    turntable mp4, emitted alongside the 3 view PNGs + audio so a single click
    yields all 5 files."""
    return f"{prefix}_trim3s.mp4"
