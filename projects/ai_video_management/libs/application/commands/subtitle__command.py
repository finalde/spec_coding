"""Subtitle-aggregate commands: burn dialogue into a shot mp4, scaffold
the per-shot `subtitles.md` dialogue-timeline file.

Cue parsing + ASS rendering is domain knowledge
(libs.domain.value_objects.subtitle__valueobject). The ffmpeg subprocess
and file I/O live in infrastructure (SubtitleBurner).
"""
from __future__ import annotations

from libs.application.dtos.subtitle__dto import (
    BurnSubtitlesResultCdto,
    ScaffoldSubtitlesResultCdto,
)
from libs.application.mappers.subtitle__mapper import SubtitleMapper
from libs.infrastructure.writers.subtitle__writer import SubtitleBurner


class SubtitleCommand:
    def __init__(self, burner: SubtitleBurner) -> None:
        self._burner = burner

    def burn(self, rel_path: str) -> BurnSubtitlesResultCdto:
        return SubtitleMapper.to_burn_cdto(self._burner.burn(rel_path))

    def scaffold(self, rel_path: str) -> ScaffoldSubtitlesResultCdto:
        return SubtitleMapper.to_scaffold_cdto(self._burner.scaffold(rel_path))
