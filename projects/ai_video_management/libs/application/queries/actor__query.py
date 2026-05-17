"""Actor-aggregate queries: one class, one method per operation.

Per follow-up 060: collapses `ListActorsQuery`, `PreviewActorPromptsQuery`,
`GetActorAssignmentsQuery` into a single `ActorQuery` class with three
methods.
"""
from __future__ import annotations

from libs.application.dtos.actor__dto import (
    ActorAssignmentsQdto,
    ActorListQdto,
    GenerateActorsInputCdto,
    GenerateDiverseActorsInputCdto,
    PreviewPromptsQdto,
)
from libs.application.mappers.actor__mapper import ActorMapper
from libs.domain.entities.actor__entity import validate_actor_id
from libs.domain.errors.actor__error import (
    InvalidActorAttributeError,
    InvalidActorIdError,
)
from libs.domain.repositories.actor__repository import ActorRepository
from libs.domain.repositories.casting__repository import CastingRepository
from libs.domain.value_objects.actor__valueobject import (
    ActorAttrs,
    validate_batch_count,
    validate_resolution,
)
from libs.infrastructure.writers.actor__writer import InvalidAttribute
from libs.infrastructure.writers.casting__writer import InvalidActorId


class ActorQuery:
    def __init__(self, pool: ActorRepository, casting: CastingRepository) -> None:
        self._pool = pool
        self._casting = casting

    def list(self) -> ActorListQdto:
        return ActorMapper.list_to_qdto(self._pool.list_actors())

    def preview_prompts(self, input_cdto: GenerateActorsInputCdto) -> PreviewPromptsQdto:
        """Dry-run prompt preview (follow-up 032). Computes the same
        {seed, prompt} pairs ActorCommand.generate would send to Kling,
        without allocating actor folders / calling Kling / writing files."""
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
        try:
            raw = self._pool.preview_prompts(
                attrs,
                input_cdto.count,
                input_cdto.resolution,
                seeds=input_cdto.seeds,
            )
        except InvalidAttribute as exc:
            raise InvalidActorAttributeError(str(exc)) from exc
        return ActorMapper.preview_to_qdto(raw)

    def preview_diverse_prompts(
        self, input_cdto: GenerateDiverseActorsInputCdto
    ) -> PreviewPromptsQdto:
        """Per follow-up 059: dry-run preview for diverse mode. Returns one
        entry per slot with `{seed, archetype, archetype_label, attrs,
        prompt, body_prompt}`. Confirm step iterates the returned slots and
        fires per-slot `generate_batch(count=1, …slot.attrs, seeds=[seed],
        archetype=slot.archetype)` via the worker pool — gives the user
        progressive UI feedback instead of one long blocking HTTP call."""
        validate_batch_count(input_cdto.count)
        validate_resolution(input_cdto.resolution)
        try:
            raw = self._pool.preview_diverse_prompts(
                input_cdto.gender,
                input_cdto.ethnicity,
                input_cdto.count,
                input_cdto.resolution,
            )
        except InvalidAttribute as exc:
            raise InvalidActorAttributeError(str(exc)) from exc
        return ActorMapper.preview_to_qdto(raw)

    def get_assignments(self, actor_id: str) -> ActorAssignmentsQdto:
        """List every drama/role that references this actor."""
        validate_actor_id(actor_id)
        try:
            assignments = self._casting.find_assignments_for_actor(actor_id)
        except InvalidActorId as exc:
            raise InvalidActorIdError(str(exc)) from exc
        return ActorAssignmentsQdto(actor_id=actor_id, assignments=assignments)
