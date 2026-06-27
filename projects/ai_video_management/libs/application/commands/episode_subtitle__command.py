"""EpisodeSubtitle-aggregate command: burn ONE subtitle track onto the clean
stitched ep{NN}.mp4 (whole-episode pass, follow-up 147). Thin seam over
EpisodeSubtitleBurner."""
from __future__ import annotations

from libs.application.dtos.subtitle__dto import EpisodeWholeBurnResultCdto
from libs.application.mappers.episode_subtitle__mapper import EpisodeSubtitleMapper
from libs.infrastructure.writers.episode_subtitle__writer import EpisodeSubtitleBurner


class EpisodeSubtitleCommand:
    def __init__(self, burner: EpisodeSubtitleBurner) -> None:
        self._burner = burner

    def burn_whole(self, rel_path: str, lang: str = "zh") -> EpisodeWholeBurnResultCdto:
        return EpisodeSubtitleMapper.to_cdto(self._burner.burn_whole(rel_path, lang))
