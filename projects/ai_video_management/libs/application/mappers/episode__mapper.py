"""EpisodeMapper — writer-result ↔ Cdto translation for episode concat."""
from __future__ import annotations

from libs.application.dtos.episode__dto import (
    ConcatEpisodeResultCdto,
    EpisodeShotSkippedCdto,
    EpisodeShotUsedCdto,
)
from libs.infrastructure.writers.episode__writer import EpisodeConcatResult


class EpisodeMapper:
    @staticmethod
    def concat_to_cdto(r: EpisodeConcatResult) -> ConcatEpisodeResultCdto:
        used = tuple(
            EpisodeShotUsedCdto(shot=c.shot, video_rel=c.video_rel, trimmed_s=c.trimmed_s)
            for c in r.used
        )
        skipped = tuple(
            EpisodeShotSkippedCdto(shot=s.shot, reason=s.reason) for s in r.skipped
        )
        return ConcatEpisodeResultCdto(
            episode_rel=r.episode_rel,
            out_rel=r.out_rel,
            used=used,
            skipped=skipped,
            lang=r.lang,
            rife_used=r.rife_used,
            rife_bridges=r.rife_bridges,
        )
