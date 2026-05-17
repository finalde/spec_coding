"""Casting-aggregate commands: assign + unassign actor on a drama's casting.md."""
from __future__ import annotations

from libs.application.dtos.casting__dto import (
    AssignActorInputCdto,
    CastingQdto,
    UnassignActorInputCdto,
)
from libs.application.mappers.casting__mapper import CastingMapper
from libs.domain.entities.casting__entity import validate_role
from libs.domain.errors.actor__error import InvalidActorIdError
from libs.domain.errors.casting__error import (
    DramaNotFoundError,
    InvalidDramaPathError,
    InvalidRoleError,
)
from libs.domain.repositories.casting__repository import CastingRepository
from libs.domain.value_objects.drama__valueobject import DramaPath
from libs.infrastructure.writers.casting__writer import InvalidActorId, InvalidRole
from libs.infrastructure.writers.media__writer import DramaNotFound, InvalidDramaPath


class CastingCommand:
    def __init__(self, casting: CastingRepository) -> None:
        self._casting = casting

    def assign(self, input_cdto: AssignActorInputCdto) -> CastingQdto:
        DramaPath(rel=input_cdto.rel_drama_path)
        validate_role(input_cdto.role)
        try:
            result = self._casting.assign(
                input_cdto.rel_drama_path,
                input_cdto.role,
                input_cdto.actor_id,
                input_cdto.notes,
            )
        except InvalidDramaPath as exc:
            raise InvalidDramaPathError(str(exc)) from exc
        except InvalidRole as exc:
            raise InvalidRoleError(str(exc)) from exc
        except InvalidActorId as exc:
            raise InvalidActorIdError(str(exc)) from exc
        except DramaNotFound as exc:
            raise DramaNotFoundError(str(exc)) from exc
        return CastingMapper.to_qdto(result)

    def unassign(self, input_cdto: UnassignActorInputCdto) -> CastingQdto:
        DramaPath(rel=input_cdto.rel_drama_path)
        validate_role(input_cdto.role)
        try:
            result = self._casting.unassign(input_cdto.rel_drama_path, input_cdto.role)
        except InvalidDramaPath as exc:
            raise InvalidDramaPathError(str(exc)) from exc
        except InvalidRole as exc:
            raise InvalidRoleError(str(exc)) from exc
        except DramaNotFound as exc:
            raise DramaNotFoundError(str(exc)) from exc
        return CastingMapper.to_qdto(result)
