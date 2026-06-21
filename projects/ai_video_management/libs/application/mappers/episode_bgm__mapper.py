"""Map episode-BGM infrastructure results into application DTOs."""
from __future__ import annotations

from libs.application.dtos.episode_bgm__dto import (
    BurnEpisodeBgmResultCdto,
    EpisodeBgmReadQdto,
)
from libs.infrastructure.writers.episode_bgm__writer import (
    BurnEpisodeBgmResult,
    EpisodeBgmReadResult,
)


class EpisodeBgmMapper:
    @staticmethod
    def read_to_qdto(result: EpisodeBgmReadResult) -> EpisodeBgmReadQdto:
        return EpisodeBgmReadQdto(payload=result.to_payload())

    @staticmethod
    def burn_to_cdto(result: BurnEpisodeBgmResult) -> BurnEpisodeBgmResultCdto:
        return BurnEpisodeBgmResultCdto(payload=result.to_payload())
