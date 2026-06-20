"""Performance-library-aggregate DTOs (Q-side).

Backs `POST /api/performance-candidates`: top-N ranked candidates from the
performance library (`ai_videos/_performances/{emotion}/perf_NNNN/`) matched
against a shot's emotion / intensity / duration.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PerformanceCandidateQdto:
    perf_id: str
    emotion: str
    intensity: int | None
    style: str
    carrier: str
    duration_s: float | None
    title: str
    preview: str
    mp4_rel_path: str | None
    score: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "perf_id": self.perf_id,
            "emotion": self.emotion,
            "intensity": self.intensity,
            "style": self.style,
            "carrier": self.carrier,
            "duration_s": self.duration_s,
            "title": self.title,
            "preview": self.preview,
            "mp4_rel_path": self.mp4_rel_path,
            "score": self.score,
        }


@dataclass(frozen=True)
class PerformanceCandidatesQdto:
    candidates: tuple[PerformanceCandidateQdto, ...]
    shot_emotion_guess: str | None

    def to_payload(self) -> dict[str, Any]:
        return {
            "candidates": [c.to_dict() for c in self.candidates],
            "shot_emotion_guess": self.shot_emotion_guess,
        }
