"""DramaEpisodesMapper — reader-result → Qdto translation for the episode list."""
from __future__ import annotations

from libs.application.dtos.drama_episodes__dto import (
    DramaEpisodesResultQdto,
    EpisodeInfoQdto,
)
from libs.infrastructure.readers.drama_episodes__reader import DramaEpisodesResult


class DramaEpisodesMapper:
    @staticmethod
    def to_qdto(r: DramaEpisodesResult) -> DramaEpisodesResultQdto:
        return DramaEpisodesResultQdto(
            drama_rel=r.drama_rel,
            episodes=tuple(
                EpisodeInfoQdto(
                    e.episode, e.episode_rel, e.shots, e.locked, e.has_master
                )
                for e in r.episodes
            ),
        )
