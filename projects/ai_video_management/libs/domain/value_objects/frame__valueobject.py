"""FrameSpec — the 8-frame schedule for scene-reference video extraction.

Per follow-up 041: 5 canonical dwell anchors + 3 strategic transition
frames; rank field defines upload-priority order so that r1 / r2 / r3 cover
the three most distinct focal scales. This is domain knowledge — the
choice of which 8 frames + the rank order is editorial / aesthetic, not
infrastructure. The ffmpeg subprocess invocation that materialises each
frame lives in infrastructure.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FrameSpec:
    timestamp: float
    role: str
    shot_size: str
    rank: int


CANONICAL_FRAMES: tuple[FrameSpec, ...] = (
    FrameSpec(0.5,  "hero",         "wide",      2),
    FrameSpec(2.5,  "side",         "wide",      6),
    FrameSpec(4.4,  "reverse",      "wide",      4),
    FrameSpec(7.9,  "vert",         "wide",      5),
    FrameSpec(10.0, "threequarter", "oblique",   7),
    FrameSpec(11.4, "mid",          "medium",    1),
    FrameSpec(13.0, "mediumclose",  "medium",    8),
    FrameSpec(14.6, "detail",       "telephoto", 3),
)


def output_filename(prefix: str, spec: FrameSpec) -> str:
    """`{prefix}_r{rank}_{role}_{shot_size}.png` per follow-up 041."""
    return f"{prefix}_r{spec.rank}_{spec.role}_{spec.shot_size}.png"
