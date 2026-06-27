"""EpisodeTakes-aggregate command: lock each shot's selected take (copy newest
renders/ mp4 → shot{NN}.mp4). Thin application seam over EpisodeTakesSelector."""
from __future__ import annotations

from libs.application.dtos.episode_takes__dto import SelectTakesResultCdto
from libs.application.mappers.episode_takes__mapper import EpisodeTakesMapper
from libs.infrastructure.writers.episode_takes__writer import EpisodeTakesSelector


class EpisodeTakesCommand:
    def __init__(self, selector: EpisodeTakesSelector) -> None:
        self._selector = selector

    def select(self, rel_path: str) -> SelectTakesResultCdto:
        return EpisodeTakesMapper.to_cdto(self._selector.select(rel_path))
