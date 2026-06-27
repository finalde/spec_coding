"""Character-aggregate read query: list each character's newest turntable mp4."""
from __future__ import annotations

from libs.application.dtos.character__dto import CharacterVideoListQdto
from libs.application.mappers.character__mapper import CharacterMapper
from libs.infrastructure.readers.character__reader import CharacterReader


class CharacterQuery:
    def __init__(self, reader: CharacterReader) -> None:
        self._reader = reader

    def list_latest_videos(self, characters_rel: str) -> CharacterVideoListQdto:
        return CharacterMapper.list_to_qdto(
            self._reader.list_latest_videos(characters_rel)
        )
