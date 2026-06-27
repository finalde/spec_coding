"""DramaTakesMapper — writer-result → Cdto translation for drama-wide 定版."""
from __future__ import annotations

from libs.application.dtos.drama_takes__dto import (
    DramaTakesResultCdto,
    EpisodeTakesOutcomeCdto,
)
from libs.infrastructure.writers.drama_takes__writer import DramaTakesResult


class DramaTakesMapper:
    @staticmethod
    def to_cdto(r: DramaTakesResult) -> DramaTakesResultCdto:
        return DramaTakesResultCdto(
            drama_rel=r.drama_rel,
            outcomes=tuple(
                EpisodeTakesOutcomeCdto(
                    o.episode, o.episode_rel, o.ok, o.selected, o.skipped, o.reason
                )
                for o in r.outcomes
            ),
        )
