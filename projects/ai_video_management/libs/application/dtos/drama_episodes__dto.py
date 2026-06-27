"""DramaEpisodes-aggregate DTO: the per-episode list for the production console.
Qdto only — read-side."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class EpisodeInfoQdto:
    episode: str
    episode_rel: str
    shots: int
    locked: int
    has_master: bool

    def to_payload(self) -> dict[str, Any]:
        return {
            "episode": self.episode,
            "episode_rel": self.episode_rel,
            "shots": self.shots,
            "locked": self.locked,
            "has_master": self.has_master,
        }


@dataclass(frozen=True)
class DramaEpisodesResultQdto:
    drama_rel: str
    episodes: tuple[EpisodeInfoQdto, ...]

    def to_payload(self) -> dict[str, Any]:
        return {
            "drama": self.drama_rel,
            "episodes": [e.to_payload() for e in self.episodes],
        }
