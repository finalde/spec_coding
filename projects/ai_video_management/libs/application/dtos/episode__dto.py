"""Episode-aggregate DTOs: ConcatEpisode result + per-shot used/skipped rows,
plus the seam-planner analysis (Qdto-shaped read of every shot→shot junction)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class EpisodeShotUsedCdto:
    shot: str
    video_rel: str
    trimmed_s: float = 0.0

    def to_payload(self) -> dict[str, Any]:
        return {"shot": self.shot, "video": self.video_rel, "trimmed_s": self.trimmed_s}


@dataclass(frozen=True)
class EpisodeShotSkippedCdto:
    shot: str
    reason: str

    def to_payload(self) -> dict[str, Any]:
        return {"shot": self.shot, "reason": self.reason}


@dataclass(frozen=True)
class SeamInfoQdto:
    index: int
    from_shot: str
    to_shot: str
    link: str
    diff: float | None
    suggest: str
    method: str
    trim: float
    depth: int | None
    thumb_a: str
    thumb_b: str

    def to_payload(self) -> dict[str, Any]:
        return {
            "index": self.index, "from": self.from_shot, "to": self.to_shot,
            "link": self.link, "diff": self.diff, "suggest": self.suggest,
            "method": self.method, "trim": self.trim, "depth": self.depth,
            "thumb_a": self.thumb_a, "thumb_b": self.thumb_b,
        }


@dataclass(frozen=True)
class SeamAnalysisQdto:
    episode_rel: str
    lang: str
    seams: tuple[SeamInfoQdto, ...]
    has_saved_plan: bool

    def to_payload(self) -> dict[str, Any]:
        return {
            "episode": self.episode_rel, "lang": self.lang,
            "seams": [s.to_payload() for s in self.seams],
            "has_saved_plan": self.has_saved_plan,
        }


@dataclass(frozen=True)
class ConcatEpisodeResultCdto:
    episode_rel: str
    out_rel: str | None
    used: tuple[EpisodeShotUsedCdto, ...]
    skipped: tuple[EpisodeShotSkippedCdto, ...]
    lang: str
    rife_used: bool = False
    rife_bridges: int = 0
    segments_rel: str | None = None

    def to_payload(self) -> dict[str, Any]:
        return {
            "episode": self.episode_rel,
            "out": self.out_rel,
            "used": [u.to_payload() for u in self.used],
            "skipped": [s.to_payload() for s in self.skipped],
            "lang": self.lang,
            "rife_used": self.rife_used,
            "rife_bridges": self.rife_bridges,
            "segments": self.segments_rel,
        }
