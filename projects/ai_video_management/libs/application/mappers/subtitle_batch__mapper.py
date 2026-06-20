"""SubtitleBatchMapper — batch writer-result↔Cdto translation."""
from __future__ import annotations

from libs.application.dtos.subtitle__dto import (
    BatchShotOutcomeCdto,
    BurnDramaSubtitlesResultCdto,
    ScaffoldEpisodeSubtitlesResultCdto,
)
from libs.infrastructure.writers.subtitle_batch__writer import (
    BatchShotOutcome,
    DramaBurnResult,
    EpisodeScaffoldResult,
)


class SubtitleBatchMapper:
    @staticmethod
    def to_scaffold_episode_cdto(
        r: EpisodeScaffoldResult,
    ) -> ScaffoldEpisodeSubtitlesResultCdto:
        return ScaffoldEpisodeSubtitlesResultCdto(
            episode_rel=r.episode_rel,
            outcomes=tuple(SubtitleBatchMapper._outcome(o) for o in r.outcomes),
        )

    @staticmethod
    def to_burn_drama_cdto(r: DramaBurnResult) -> BurnDramaSubtitlesResultCdto:
        return BurnDramaSubtitlesResultCdto(
            drama_rel=r.drama_rel,
            lang=r.lang,
            outcomes=tuple(SubtitleBatchMapper._outcome(o) for o in r.outcomes),
        )

    @staticmethod
    def _outcome(o: BatchShotOutcome) -> BatchShotOutcomeCdto:
        return BatchShotOutcomeCdto(
            episode=o.episode,
            shot=o.shot,
            ok=o.ok,
            out_rel=o.out_rel,
            cue_count=o.cue_count,
            reason=o.reason,
        )
