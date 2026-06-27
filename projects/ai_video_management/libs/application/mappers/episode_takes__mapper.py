"""EpisodeTakesMapper — writer-result → Cdto translation for take selection."""
from __future__ import annotations

from libs.application.dtos.episode_takes__dto import (
    SelectTakesResultCdto,
    TakeSelectionCdto,
    TakeSkipCdto,
)
from libs.infrastructure.writers.episode_takes__writer import SelectTakesResult


class EpisodeTakesMapper:
    @staticmethod
    def to_cdto(r: SelectTakesResult) -> SelectTakesResultCdto:
        return SelectTakesResultCdto(
            episode_rel=r.episode_rel,
            selected=tuple(
                TakeSelectionCdto(s.shot, s.src_rel, s.out_rel) for s in r.selected
            ),
            skipped=tuple(TakeSkipCdto(s.shot, s.reason) for s in r.skipped),
        )
