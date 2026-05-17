"""Actor-aggregate commands: one class, one method per operation.

Per follow-up 060: the previous layout was three separate command classes
in one file (`GenerateActorsCommand`, `GenerateDiverseActorsCommand`,
`DeleteActorCommand`). The new convention rolls them into a single
`ActorCommand` class with three methods (`generate`, `generate_diverse`,
`delete`). The operation name lives on the method, not the class.
"""
from __future__ import annotations

from libs.application.dtos.actor__dto import (
    DeleteActorResultCdto,
    GenerateActorsInputCdto,
    GenerateActorsResultCdto,
    GenerateDiverseActorsInputCdto,
)
from libs.application.mappers.actor__mapper import ActorMapper
from libs.domain.entities.actor__entity import validate_actor_id
from libs.domain.errors.actor__error import (
    ActorAlreadyAssignedError,
    ActorNotFoundError,
    InvalidActorAttributeError,
    InvalidActorIdError,
)
from libs.domain.repositories.actor__repository import ActorRepository
from libs.domain.repositories.casting__repository import CastingRepository
from libs.domain.value_objects.actor__valueobject import (
    ActorAttrs,
    validate_batch_count,
    validate_resolution,
    validate_seeds,
)
from libs.infrastructure.writers.actor__writer import (
    ActorDeleteFailed,
    ActorDeleteTargetExists,
    ActorNotFound,
    GenerationDirMissing,
    InvalidAttribute,
)
from libs.infrastructure.writers.casting__writer import InvalidActorId


class ActorCommand:
    def __init__(self, pool: ActorRepository, casting: CastingRepository) -> None:
        self._pool = pool
        self._casting = casting

    def generate(self, input_cdto: GenerateActorsInputCdto) -> GenerateActorsResultCdto:
        attrs = ActorAttrs(
            ethnicity=input_cdto.ethnicity,
            gender=input_cdto.gender,
            age_range=input_cdto.age_range,
            look=input_cdto.look,
            style=input_cdto.style,
            notes=input_cdto.notes,
        )
        attrs.validate()
        validate_batch_count(input_cdto.count)
        validate_resolution(input_cdto.resolution)
        validate_seeds(input_cdto.seeds, input_cdto.count)
        try:
            result = self._pool.generate_batch(
                attrs,
                input_cdto.count,
                input_cdto.resolution,
                input_cdto.seeds,
                archetype=input_cdto.archetype,
            )
        except InvalidAttribute as exc:
            raise InvalidActorAttributeError(str(exc)) from exc
        except GenerationDirMissing:
            raise
        return ActorMapper.generate_to_cdto(result)

    def generate_diverse(self, input_cdto: GenerateDiverseActorsInputCdto) -> GenerateActorsResultCdto:
        """Per follow-up 053: diverse mode rolls per-slot attrs from a
        10-archetype even-distribution plan."""
        validate_batch_count(input_cdto.count)
        validate_resolution(input_cdto.resolution)
        try:
            result = self._pool.generate_diverse_batch(
                input_cdto.gender,
                input_cdto.ethnicity,
                input_cdto.count,
                input_cdto.resolution,
            )
        except InvalidAttribute as exc:
            raise InvalidActorAttributeError(str(exc)) from exc
        except GenerationDirMissing:
            raise
        return ActorMapper.generate_to_cdto(result)

    def delete(self, actor_id: str) -> DeleteActorResultCdto:
        """Soft-delete an actor folder; refuses when any drama's casting.md
        still references this actor (follow-up 043)."""
        validate_actor_id(actor_id)
        try:
            assignments = self._casting.find_assignments_for_actor(actor_id)
        except InvalidActorId as exc:
            raise InvalidActorIdError(str(exc)) from exc
        if assignments:
            raise ActorAlreadyAssignedError(actor_id=actor_id, assignments=assignments)
        try:
            move = self._pool.delete_actor(actor_id)
        except InvalidAttribute as exc:
            raise InvalidActorIdError(str(exc)) from exc
        except ActorNotFound as exc:
            raise ActorNotFoundError(str(exc)) from exc
        except (ActorDeleteTargetExists, ActorDeleteFailed):
            raise
        return DeleteActorResultCdto(
            src_rel=str(move["from"]),
            dst_rel=str(move["to"]),
            unassigned=[],
        )
