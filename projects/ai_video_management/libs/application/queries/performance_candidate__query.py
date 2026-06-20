"""Performance-candidate query: rank performance-library entries against a
shot's emotion / intensity / duration and return the top-N.

Scoring (descending priority): exact emotion-class match → intensity proximity
→ duration proximity → carrier presence. When `emotion` is null the query reads
the shot file and roughly guesses the emotion class from its 情节: / 动作: text;
if it can't guess, it falls back to intensity/duration ranking over the whole
library and surfaces `shot_emotion_guess=null`.
"""
from __future__ import annotations

from dataclasses import dataclass

from libs.application.dtos.performance__dto import (
    PerformanceCandidateQdto,
    PerformanceCandidatesQdto,
)
from libs.common.safe_resolve import SafeResolver
from libs.infrastructure.readers.performance_library__reader import (
    PerformanceEntry,
    PerformanceLibraryReader,
)

# Weights keep the lexicographic priority intact: emotion dominates intensity,
# which dominates duration, which dominates carrier.
_EMOTION_WEIGHT = 1000.0
_INTENSITY_WEIGHT = 50.0
_DURATION_WEIGHT = 5.0
_CARRIER_WEIGHT = 1.0


@dataclass(frozen=True)
class _Scored:
    entry: PerformanceEntry
    score: float


class PerformanceCandidateQuery:
    def __init__(
        self,
        reader: PerformanceLibraryReader,
        resolver: SafeResolver,
    ) -> None:
        self._reader = reader
        self._resolver = resolver

    def recommend(
        self,
        shot_path: str,
        emotion: str | None,
        intensity: int | None,
        duration_s: float | None,
        top_n: int = 8,
    ) -> PerformanceCandidatesQdto:
        entries = self._reader.list_entries()
        guess: str | None = None
        target_emotion = emotion.strip() if isinstance(emotion, str) and emotion.strip() else None
        if target_emotion is None:
            guess = self._guess_emotion(shot_path, entries)
            target_emotion = guess

        scored = [
            _Scored(entry=e, score=self._score(e, target_emotion, intensity, duration_s))
            for e in entries
        ]
        scored.sort(
            key=lambda s: (s.score, -(s.entry.intensity or 0), s.entry.perf_id),
            reverse=True,
        )
        limit = top_n if isinstance(top_n, int) and top_n > 0 else 8
        top = scored[:limit]
        candidates = tuple(
            PerformanceCandidateQdto(
                perf_id=s.entry.perf_id,
                emotion=s.entry.emotion,
                intensity=s.entry.intensity,
                style=s.entry.style,
                carrier=s.entry.carrier,
                duration_s=s.entry.duration_s,
                title=s.entry.title,
                preview=s.entry.preview,
                mp4_rel_path=s.entry.mp4_rel_path,
                score=round(s.score, 3),
            )
            for s in top
        )
        return PerformanceCandidatesQdto(candidates=candidates, shot_emotion_guess=guess)

    @staticmethod
    def _score(
        entry: PerformanceEntry,
        target_emotion: str | None,
        intensity: int | None,
        duration_s: float | None,
    ) -> float:
        score = 0.0
        if target_emotion is not None and entry.emotion == target_emotion:
            score += _EMOTION_WEIGHT
        if intensity is not None and entry.intensity is not None:
            score += _INTENSITY_WEIGHT / (1.0 + abs(entry.intensity - intensity))
        if duration_s is not None and entry.duration_s is not None:
            score += _DURATION_WEIGHT / (1.0 + abs(entry.duration_s - duration_s))
        if entry.carrier:
            score += _CARRIER_WEIGHT
        return score

    def _guess_emotion(self, shot_path: str, entries: list[PerformanceEntry]) -> str | None:
        text = self._read_shot_text(shot_path)
        if not text:
            return None
        scope = self._field_scope(text)
        emotions = {e.emotion for e in entries if e.emotion}
        best: str | None = None
        best_hits = 0
        for emotion in emotions:
            hits = sum(1 for ch in emotion if ch in scope)
            if hits > best_hits and hits >= 2:
                best_hits = hits
                best = emotion
        return best

    def _read_shot_text(self, shot_path: str) -> str:
        resolved = self._resolver.resolve((shot_path or "").replace("\\", "/"))
        if resolved is None or not resolved.is_file():
            return ""
        try:
            return resolved.read_text(encoding="utf-8")
        except OSError:
            return ""

    @staticmethod
    def _field_scope(text: str) -> str:
        parts: list[str] = []
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("情节") or stripped.startswith("动作"):
                parts.append(stripped)
        return "\n".join(parts) if parts else text
