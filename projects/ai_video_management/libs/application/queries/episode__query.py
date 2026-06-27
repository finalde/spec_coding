"""Episode-aggregate queries: read-side seam analysis for the seam-planner UI.

`analyze_seams` inspects every shot→shot junction (承接/硬切, boundary-frame
thumbnails, frame-diff suggestion, any saved plan) without mutating anything; the
ffmpeg probing + thumbnailing live in infrastructure (`EpisodeConcatBuilder`).
"""
from __future__ import annotations

from libs.application.dtos.episode__dto import SeamAnalysisQdto
from libs.application.mappers.episode__mapper import EpisodeMapper
from libs.infrastructure.writers.episode__writer import EpisodeConcatBuilder


class EpisodeQuery:
    def __init__(self, builder: EpisodeConcatBuilder) -> None:
        self._builder = builder

    def analyze_seams(
        self, rel_path: str, lang: str = "original"
    ) -> SeamAnalysisQdto:
        return EpisodeMapper.analysis_to_qdto(
            self._builder.analyze_seams(rel_path, lang)
        )

    def score_seams(
        self, rel_path: str, lang: str = "original", compare: bool = True
    ) -> dict:
        """Objective seam-quality scorecard (optical-flow + SSIM) for the dashboard.
        The payload is the seam_metrics tool's structured result — a dynamic nested
        dict (per-seam metric breakdowns + a ranked method panel + metric defs), so
        it passes through verbatim rather than through a fixed DTO."""
        return self._builder.score_seams(rel_path, lang, compare)

    def read_seam_scores(self, rel_path: str) -> dict:
        """The persisted scorecard from the last build (instant, no recompute) — the
        payload the dashboard auto-loads on page open. `{persisted: false}` when the
        episode has not been scored yet."""
        card = self._builder.read_seam_scores(rel_path)
        return card if card is not None else {"persisted": False}
