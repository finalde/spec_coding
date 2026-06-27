"""DramaEpisodes-aggregate query: list a drama's episodes for the production
console. Thin read-side seam over DramaEpisodesReader."""
from __future__ import annotations

from libs.application.dtos.drama_episodes__dto import DramaEpisodesResultQdto
from libs.application.mappers.drama_episodes__mapper import DramaEpisodesMapper
from libs.infrastructure.readers.drama_episodes__reader import DramaEpisodesReader


class DramaEpisodesQuery:
    def __init__(self, reader: DramaEpisodesReader) -> None:
        self._reader = reader

    def list(self, rel_path: str) -> DramaEpisodesResultQdto:
        return DramaEpisodesMapper.to_qdto(self._reader.list(rel_path))
