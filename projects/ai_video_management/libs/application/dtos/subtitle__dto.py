"""Subtitle-aggregate DTOs: burn / scaffold result Cdtos (no Qdtos)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class BurnSubtitlesResultCdto:
    src_rel: str
    out_rel: str
    cue_count: int
    lang: str

    def to_payload(self) -> dict[str, Any]:
        return {
            "src": self.src_rel,
            "out": self.out_rel,
            "cues": self.cue_count,
            "lang": self.lang,
        }


@dataclass(frozen=True)
class ScaffoldSubtitlesResultCdto:
    md_rel: str
    cue_count: int
    created: bool

    def to_payload(self) -> dict[str, Any]:
        return {
            "path": self.md_rel,
            "cues": self.cue_count,
            "created": self.created,
        }


@dataclass(frozen=True)
class BatchShotOutcomeCdto:
    episode: str
    shot: str
    ok: bool
    out_rel: str | None
    cue_count: int | None
    reason: str | None

    def to_payload(self) -> dict[str, Any]:
        return {
            "episode": self.episode,
            "shot": self.shot,
            "ok": self.ok,
            "out": self.out_rel,
            "cues": self.cue_count,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class ScaffoldEpisodeSubtitlesResultCdto:
    episode_rel: str
    outcomes: tuple[BatchShotOutcomeCdto, ...]

    def to_payload(self) -> dict[str, Any]:
        return {
            "episode": self.episode_rel,
            "outcomes": [o.to_payload() for o in self.outcomes],
        }


@dataclass(frozen=True)
class BurnDramaSubtitlesResultCdto:
    drama_rel: str
    lang: str
    outcomes: tuple[BatchShotOutcomeCdto, ...]

    def to_payload(self) -> dict[str, Any]:
        return {
            "drama": self.drama_rel,
            "lang": self.lang,
            "outcomes": [o.to_payload() for o in self.outcomes],
        }
