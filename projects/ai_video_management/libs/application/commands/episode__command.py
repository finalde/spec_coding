"""Episode-aggregate commands: concat each shot's newest render into one
`ep{NN}.mp4`.

The choice of which mp4 represents a shot (newest under `renders/`) and the
ffmpeg concat that materialises the episode reel both live in infrastructure;
this command is the thin application-layer seam the route depends on.
"""
from __future__ import annotations

from libs.application.dtos.episode__dto import ConcatEpisodeResultCdto
from libs.application.mappers.episode__mapper import EpisodeMapper
from libs.infrastructure.writers.episode__writer import EpisodeConcatBuilder


class EpisodeCommand:
    def __init__(self, builder: EpisodeConcatBuilder) -> None:
        self._builder = builder

    def concat(
        self, rel_path: str, lang: str = "original", rife: bool = False,
        plan: list[dict] | None = None,
    ) -> ConcatEpisodeResultCdto:
        return EpisodeMapper.concat_to_cdto(
            self._builder.build(rel_path, lang, rife, plan)
        )
