"""Actor-aggregate commands: one class, one method per operation."""
from __future__ import annotations

from libs.application.dtos.actor__dto import (
    DeleteActorResultCdto,
    GenerateActorsInputCdto,
    GenerateActorsResultCdto,
    GenerateDiverseActorsInputCdto,
)
from libs.application.mappers.actor__mapper import ActorMapper
from libs.domain.errors.actor__error import (
    ActorAlreadyAssignedError,
    AssignmentsScanFailedError,
)
from libs.domain.repositories.actor__repository import ActorRepository
from libs.domain.repositories.casting__repository import CastingRepository
from libs.domain.value_objects.actor__valueobject import ActorAttrs, validate_actor_id


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
            notes=input_cdto.notes,
            eyes=input_cdto.eyes,
            nose=input_cdto.nose,
            lips=input_cdto.lips,
            face=input_cdto.face,
            skin=input_cdto.skin,
            body=input_cdto.body,
            qi_zhi=input_cdto.qi_zhi,
        )
        result = self._pool.generate_batch(
            attrs,
            input_cdto.count,
            input_cdto.resolution,
            input_cdto.seeds,
            archetype=input_cdto.archetype,
            batch_seed=input_cdto.batch_seed,
            batch_size=input_cdto.batch_size,
            slot_index=input_cdto.slot_index,
        )
        return ActorMapper.generate_to_cdto(result)

    def generate_diverse(self, input_cdto: GenerateDiverseActorsInputCdto) -> GenerateActorsResultCdto:
        """Diverse mode rolls per-slot attrs from a 10-archetype even-distribution plan."""
        result = self._pool.generate_diverse_batch(
            input_cdto.gender,
            input_cdto.ethnicity,
            input_cdto.count,
            input_cdto.resolution,
        )
        return ActorMapper.generate_to_cdto(result)

    def delete(self, actor_id: str) -> DeleteActorResultCdto:
        """Soft-delete an actor folder; refuses when any drama's casting.md
        still references this actor (follow-up 043)."""
        validate_actor_id(actor_id)
        try:
            assignments = self._casting.find_assignments_for_actor(actor_id)
        except OSError as exc:
            raise AssignmentsScanFailedError(str(exc)) from exc
        if assignments:
            raise ActorAlreadyAssignedError(actor_id=actor_id, assignments=assignments)
        move = self._pool.delete_actor(actor_id)
        return DeleteActorResultCdto(
            src_rel=str(move["from"]),
            dst_rel=str(move["to"]),
            unassigned=[],
        )
