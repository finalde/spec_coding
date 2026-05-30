"""Casting-aggregate commands: assign + unassign actor on a drama's casting.md."""
from __future__ import annotations

from libs.application.dtos.casting__dto import (
    AssignActorInputCdto,
    CastingQdto,
    UnassignActorInputCdto,
)
from libs.application.mappers.casting__mapper import CastingMapper
from libs.domain.entities.casting__entity import validate_role
from libs.domain.repositories.casting__repository import CastingRepository
from libs.domain.value_objects.drama__valueobject import DramaPath


class CastingCommand:
    def __init__(self, casting: CastingRepository) -> None:
        self._casting = casting

    def assign(self, input_cdto: AssignActorInputCdto) -> CastingQdto:
        DramaPath(rel=input_cdto.rel_drama_path)
        validate_role(input_cdto.role)
        result = self._casting.assign(
            input_cdto.rel_drama_path,
            input_cdto.role,
            input_cdto.actor_id,
            input_cdto.notes,
        )
        return CastingMapper.to_qdto(result)

    def unassign(self, input_cdto: UnassignActorInputCdto) -> CastingQdto:
        DramaPath(rel=input_cdto.rel_drama_path)
        validate_role(input_cdto.role)
        result = self._casting.unassign(input_cdto.rel_drama_path, input_cdto.role)
        return CastingMapper.to_qdto(result)

    # Voice surface (follow-up 115). The signatures stay route-friendly:
    # plain positional + optional notes rather than wrapping in a dedicated
    # Cdto, because the voice flows are pure pass-through to the repository
    # (validation happens in the domain).
    def assign_voice(
        self, rel_drama_path: str, role: str, voice_id: str, notes: str | None = None
    ) -> CastingQdto:
        DramaPath(rel=rel_drama_path)
        validate_role(role)
        result = self._casting.assign_voice(rel_drama_path, role, voice_id, notes)
        return CastingMapper.to_qdto(result)

    def unassign_voice(self, rel_drama_path: str, role: str) -> CastingQdto:
        DramaPath(rel=rel_drama_path)
        validate_role(role)
        result = self._casting.unassign_voice(rel_drama_path, role)
        return CastingMapper.to_qdto(result)
