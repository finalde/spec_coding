"""ActorMapper — DAO↔Entity↔Qdto/Cdto translation for the actor pool."""
from __future__ import annotations

from libs.application.dtos.actor__dto import GenerateActorsResultCdto
from libs.application.dtos.actor__dto import (
    ActorListQdto,
    ActorListRowQdto,
    PreviewPromptQdto,
    PreviewPromptsQdto,
)
from libs.infrastructure.writers.actor__writer import ActorInfo, GenerateResult


class ActorMapper:
    @staticmethod
    def info_to_qdto(info: ActorInfo, is_assigned: bool = False) -> ActorListRowQdto:
        return ActorListRowQdto(
            actor_id=info.id,
            image_path=info.image_path,
            mtime=info.mtime,
            ethnicity=info.attrs.ethnicity,
            gender=info.attrs.gender,
            age_range=info.attrs.age_range,
            look=info.attrs.look,
            notes=info.attrs.notes,
            is_assigned=is_assigned,
        )

    @staticmethod
    def list_to_qdto(
        infos: list[ActorInfo], assigned_ids: set[str] | None = None,
    ) -> ActorListQdto:
        """Per follow-up 086: optional `assigned_ids` set is the union of
        actor_ids appearing in any drama's casting.md (produced by
        `CastingRepository.assigned_actor_ids()`). When provided, each row's
        `is_assigned` reflects membership; when omitted (legacy callers),
        all rows get `is_assigned=False`."""
        ids = assigned_ids or set()
        return ActorListQdto(
            actors=tuple(ActorMapper.info_to_qdto(i, is_assigned=i.id in ids) for i in infos)
        )

    @staticmethod
    def generate_to_cdto(r: GenerateResult) -> GenerateActorsResultCdto:
        return GenerateActorsResultCdto(generated=list(r.generated), errors=list(r.errors))

    @staticmethod
    def preview_to_qdto(raw: dict[str, object]) -> PreviewPromptsQdto:
        """Per follow-up 052: pass-through body_prompt when present.
        Per follow-up 059: pass-through archetype / archetype_label / attrs
        for diverse-mode preview entries; standard-mode entries omit those
        fields (and they remain None in the Qdto)."""
        prompts_in = raw.get("prompts", [])
        prompts: list[PreviewPromptQdto] = []
        if isinstance(prompts_in, list):
            for entry in prompts_in:
                if not isinstance(entry, dict):
                    continue
                seed = entry.get("seed")
                prompt = entry.get("prompt")
                if not (isinstance(seed, int) and isinstance(prompt, str)):
                    continue
                body_prompt = entry.get("body_prompt")
                archetype = entry.get("archetype")
                archetype_label = entry.get("archetype_label")
                attrs = entry.get("attrs")
                prompts.append(PreviewPromptQdto(
                    seed=seed,
                    prompt=prompt,
                    body_prompt=body_prompt if isinstance(body_prompt, str) else None,
                    archetype=archetype if isinstance(archetype, str) else None,
                    archetype_label=archetype_label if isinstance(archetype_label, str) else None,
                    attrs=attrs if isinstance(attrs, dict) else None,
                ))
        resolution = raw.get("resolution")
        return PreviewPromptsQdto(
            prompts=tuple(prompts),
            resolution=resolution if isinstance(resolution, str) else "normal",
        )
