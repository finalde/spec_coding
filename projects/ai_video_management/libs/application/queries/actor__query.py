"""Actor-aggregate queries: list / preview / preview-diverse / assignments."""
from __future__ import annotations

from libs.application.dtos.actor__dto import (
    ActorAssignmentsQdto,
    ActorListQdto,
    GenerateActorsInputCdto,
    GenerateDiverseActorsInputCdto,
    PreviewPromptsQdto,
)
from libs.application.mappers.actor__mapper import ActorMapper
from libs.domain.repositories.actor__repository import ActorRepository
from libs.domain.repositories.casting__repository import CastingRepository
from libs.domain.value_objects.actor__valueobject import ActorAttrs, validate_actor_id


class ActorQuery:
    def __init__(self, pool: ActorRepository, casting: CastingRepository) -> None:
        self._pool = pool
        self._casting = casting

    def list(self, include_pending: bool = False) -> ActorListQdto:
        """Tags each actor with `is_assigned` via one bulk
        `CastingRepository.assigned_actor_ids()` scan (follow-up 086).
        `include_pending=True` also returns prompt-only actors (no jpg yet),
        flagged `pending_import`, so the grid can filter + bulk-delete them."""
        assigned_ids = self._casting.assigned_actor_ids()
        return ActorMapper.list_to_qdto(
            self._pool.list_actors(include_pending=include_pending),
            assigned_ids=assigned_ids,
        )

    def preview_prompts(self, input_cdto: GenerateActorsInputCdto) -> PreviewPromptsQdto:
        """Dry-run prompt preview (follow-up 032). Same {seed, prompt} pairs
        `ActorCommand.generate` would send, without writing anything."""
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
        raw = self._pool.preview_prompts(
            attrs,
            input_cdto.count,
            input_cdto.resolution,
            seeds=input_cdto.seeds,
            batch_seed=input_cdto.batch_seed,
            batch_size=input_cdto.batch_size,
            slot_index=input_cdto.slot_index,
        )
        return ActorMapper.preview_to_qdto(raw)

    def preview_diverse_prompts(
        self, input_cdto: GenerateDiverseActorsInputCdto
    ) -> PreviewPromptsQdto:
        """Dry-run preview for diverse mode (follow-up 059)."""
        raw = self._pool.preview_diverse_prompts(
            input_cdto.gender,
            input_cdto.ethnicity,
            input_cdto.count,
            input_cdto.resolution,
        )
        return ActorMapper.preview_to_qdto(raw)

    def get_assignments(self, actor_id: str) -> ActorAssignmentsQdto:
        """List every drama/role that references this actor."""
        validate_actor_id(actor_id)
        assignments = self._casting.find_assignments_for_actor(actor_id)
        return ActorAssignmentsQdto(actor_id=actor_id, assignments=assignments)
