"""Episode-BGM-aggregate queries: read a drama episode's BGM cue timeline."""
from __future__ import annotations

from libs.application.dtos.episode_bgm__dto import EpisodeBgmReadQdto
from libs.application.mappers.episode_bgm__mapper import EpisodeBgmMapper
from libs.domain.repositories.episode_bgm__repository import EpisodeBgmRepository


class EpisodeBgmQuery:
    def __init__(self, manager: EpisodeBgmRepository) -> None:
        self._manager = manager

    def read(self, rel: str) -> EpisodeBgmReadQdto:
        return EpisodeBgmMapper.read_to_qdto(self._manager.read(rel))  # type: ignore[arg-type]
