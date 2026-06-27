"""EpisodeSubtitleMapper — whole-episode burn writer-result → Cdto."""
from __future__ import annotations

from libs.application.dtos.subtitle__dto import EpisodeWholeBurnResultCdto
from libs.infrastructure.writers.episode_subtitle__writer import EpisodeWholeBurnResult


class EpisodeSubtitleMapper:
    @staticmethod
    def to_cdto(r: EpisodeWholeBurnResult) -> EpisodeWholeBurnResultCdto:
        return EpisodeWholeBurnResultCdto(
            episode_rel=r.episode_rel,
            out_rel=r.out_rel,
            lang=r.lang,
            cue_count=r.cue_count,
            shot_count=r.shot_count,
        )
