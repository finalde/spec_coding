"""SubtitleMapper — writer-result↔Cdto translation for burn / scaffold."""
from __future__ import annotations

from libs.application.dtos.subtitle__dto import (
    BurnSubtitlesResultCdto,
    ScaffoldSubtitlesResultCdto,
)
from libs.infrastructure.writers.subtitle__writer import BurnResult, ScaffoldResult


class SubtitleMapper:
    @staticmethod
    def to_burn_cdto(r: BurnResult) -> BurnSubtitlesResultCdto:
        return BurnSubtitlesResultCdto(
            src_rel=r.src_rel, out_rel=r.out_rel, cue_count=r.cue_count, lang=r.lang
        )

    @staticmethod
    def to_scaffold_cdto(r: ScaffoldResult) -> ScaffoldSubtitlesResultCdto:
        return ScaffoldSubtitlesResultCdto(
            md_rel=r.md_rel, cue_count=r.cue_count, created=r.created
        )
