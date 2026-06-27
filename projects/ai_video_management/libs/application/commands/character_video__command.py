"""Character-video aggregate commands: truncate per-character mp4, concat
per-shot character reel, extract character views + audio."""
from __future__ import annotations

from libs.application.dtos.character_video__dto import (
    ConcatShotCharactersResultCdto,
    ExtractAllCharacterViewsResultCdto,
    ExtractCharacterViewsResultCdto,
    TruncateCharacterVideoResultCdto,
)
from libs.application.mappers.character_video__mapper import CharacterVideoMapper
from libs.infrastructure.writers.character_video__writer import (
    CharacterVideoTruncator,
    CharacterViewExtractor,
    ShotConcatBuilder,
)


class CharacterVideoCommand:
    def __init__(
        self,
        truncator: CharacterVideoTruncator,
        builder: ShotConcatBuilder,
        extractor: CharacterViewExtractor,
    ) -> None:
        self._truncator = truncator
        self._builder = builder
        self._extractor = extractor

    def truncate(self, rel_path: str) -> TruncateCharacterVideoResultCdto:
        return CharacterVideoMapper.truncate_to_cdto(self._truncator.truncate(rel_path))

    def concat_shot(self, rel_path: str) -> ConcatShotCharactersResultCdto:
        return CharacterVideoMapper.concat_to_cdto(self._builder.build(rel_path))

    def extract_views(self, rel_path: str) -> ExtractCharacterViewsResultCdto:
        return CharacterVideoMapper.views_to_cdto(self._extractor.extract(rel_path))

    def extract_all_views(self, rel_path: str) -> ExtractAllCharacterViewsResultCdto:
        return CharacterVideoMapper.extract_all_to_cdto(self._extractor.extract_all(rel_path))
