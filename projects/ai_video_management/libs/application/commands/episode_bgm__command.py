"""Episode-BGM-aggregate commands: assign / unassign a library track to a cue
slot, and burn the assigned cues onto the subtitled episode master."""
from __future__ import annotations

from libs.application.dtos.episode_bgm__dto import (
    BurnEpisodeBgmResultCdto,
    EpisodeBgmReadQdto,
)
from libs.application.mappers.episode_bgm__mapper import EpisodeBgmMapper
from libs.domain.repositories.episode_bgm__repository import EpisodeBgmRepository


class EpisodeBgmCommand:
    def __init__(self, manager: EpisodeBgmRepository) -> None:
        self._manager = manager

    def assign(
        self, rel: str, start: float, end: float, bgm_id: str
    ) -> EpisodeBgmReadQdto:
        return EpisodeBgmMapper.read_to_qdto(
            self._manager.assign(rel, start, end, bgm_id)  # type: ignore[arg-type]
        )

    def unassign(self, rel: str, start: float, end: float) -> EpisodeBgmReadQdto:
        return EpisodeBgmMapper.read_to_qdto(
            self._manager.unassign(rel, start, end)  # type: ignore[arg-type]
        )

    def burn(self, rel: str) -> BurnEpisodeBgmResultCdto:
        return EpisodeBgmMapper.burn_to_cdto(self._manager.burn(rel))  # type: ignore[arg-type]
