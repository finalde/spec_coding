"""SubtitleBatch-aggregate commands: scaffold every shot's `subtitles.md` in an
episode, and burn every shot's subtitle master across a whole drama.

The episode/drama tree-walk + per-shot delegation lives in infrastructure
(SubtitleBatchBurner); this command only maps results to Cdtos.
"""
from __future__ import annotations

from libs.application.dtos.subtitle__dto import (
    BurnDramaSubtitlesResultCdto,
    ScaffoldEpisodeSubtitlesResultCdto,
)
from libs.application.mappers.subtitle_batch__mapper import SubtitleBatchMapper
from libs.infrastructure.writers.subtitle_batch__writer import SubtitleBatchBurner


class SubtitleBatchCommand:
    def __init__(self, batch_burner: SubtitleBatchBurner) -> None:
        self._batch = batch_burner

    def scaffold_episode(self, rel_path: str) -> ScaffoldEpisodeSubtitlesResultCdto:
        return SubtitleBatchMapper.to_scaffold_episode_cdto(
            self._batch.scaffold_episode(rel_path)
        )

    def burn_drama(self, rel_path: str, lang: str = "zh") -> BurnDramaSubtitlesResultCdto:
        return SubtitleBatchMapper.to_burn_drama_cdto(
            self._batch.burn_drama(rel_path, lang)
        )
