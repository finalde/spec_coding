"""Casting-aggregate queries: read a drama's casting.md."""
from __future__ import annotations

from libs.application.dtos.casting__dto import CastingQdto
from libs.application.mappers.casting__mapper import CastingMapper
from libs.domain.repositories.casting__repository import CastingRepository
from libs.domain.value_objects.drama__valueobject import DramaPath


class CastingQuery:
    def __init__(self, casting: CastingRepository) -> None:
        self._casting = casting

    def read(self, rel_drama_path: str) -> CastingQdto:
        DramaPath(rel=rel_drama_path)
        return CastingMapper.to_qdto(self._casting.read(rel_drama_path))
