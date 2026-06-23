"""Episode-aggregate DTOs: ConcatEpisode result + per-shot used/skipped rows.
No Qdtos for this aggregate (single write-side concat operation)."""
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
class ConcatEpisodeResultCdto:
    episode_rel: str
    out_rel: str | None
    used: tuple[EpisodeShotUsedCdto, ...]
    skipped: tuple[EpisodeShotSkippedCdto, ...]
    lang: str
    rife_used: bool = False
    rife_bridges: int = 0

    def to_payload(self) -> dict[str, Any]:
        return {
            "episode": self.episode_rel,
            "out": self.out_rel,
            "used": [u.to_payload() for u in self.used],
            "skipped": [s.to_payload() for s in self.skipped],
            "lang": self.lang,
            "rife_used": self.rife_used,
            "rife_bridges": self.rife_bridges,
        }
