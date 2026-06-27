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
