"""Casting-aggregate queries: read a drama's casting.md."""
from __future__ import annotations

from libs.application.dtos.casting__dto import CastingQdto
from libs.application.mappers.casting__mapper import CastingMapper
from libs.domain.errors.casting__error import DramaNotFoundError, InvalidDramaPathError
from libs.domain.repositories.casting__repository import CastingRepository
from libs.domain.value_objects.drama__valueobject import DramaPath
from libs.infrastructure.writers.media__writer import DramaNotFound, InvalidDramaPath


class CastingQuery:
    def __init__(self, casting: CastingRepository) -> None:
        self._casting = casting

    def read(self, rel_drama_path: str) -> CastingQdto:
        DramaPath(rel=rel_drama_path)
        try:
            result = self._casting.read(rel_drama_path)
        except InvalidDramaPath as exc:
            raise InvalidDramaPathError(str(exc)) from exc
        except DramaNotFound as exc:
            raise DramaNotFoundError(str(exc)) from exc
        return CastingMapper.to_qdto(result)
