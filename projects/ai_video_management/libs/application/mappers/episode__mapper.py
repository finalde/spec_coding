"""EpisodeMapper — writer-result ↔ Cdto translation for episode concat."""
from __future__ import annotations

from libs.application.dtos.episode__dto import (
    ConcatEpisodeResultCdto,
    EpisodeShotSkippedCdto,
    EpisodeShotUsedCdto,
    SeamAnalysisQdto,
    SeamInfoQdto,
)
from libs.infrastructure.writers.episode__writer import (
    EpisodeConcatResult,
    SeamAnalysis,
)


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
            segments_rel=r.segments_rel,
        )

    @staticmethod
    def analysis_to_qdto(a: SeamAnalysis) -> SeamAnalysisQdto:
        seams = tuple(
            SeamInfoQdto(
                index=s.index, from_shot=s.from_shot, to_shot=s.to_shot,
                link=s.link, diff=s.diff, suggest=s.suggest, method=s.method,
                trim=s.trim, depth=s.depth, thumb_a=s.thumb_a, thumb_b=s.thumb_b,
            )
            for s in a.seams
        )
        return SeamAnalysisQdto(
            episode_rel=a.episode_rel, lang=a.lang, seams=seams,
            has_saved_plan=a.has_saved_plan,
        )
