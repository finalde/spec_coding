"""Actor-aggregate DTOs: queries' Qdtos + commands' Cdtos.

Per follow-up 114: input Cdtos validate themselves in __post_init__ so
neither the Command nor the Query has to re-run the same `validate_*`
calls. Constructing a `GenerateActorsInputCdto(**body.model_dump())`
either yields a valid value or raises a domain error — there is no
"valid shape but unchecked" state.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from libs.domain.value_objects.actor__valueobject import (
    ActorAttrs,
    validate_batch_count,
    validate_resolution,
    validate_seeds,
)


# --- Query DTOs -------------------------------------------------------------


@dataclass(frozen=True)
class ActorListRowQdto:
    actor_id: str
    image_path: str
    mtime: float
    ethnicity: str
    gender: str
    age_range: str
    look: str
    notes: str
    is_assigned: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.actor_id,
            "image_path": self.image_path,
            "mtime": self.mtime,
            "ethnicity": self.ethnicity,
            "gender": self.gender,
            "age_range": self.age_range,
            "look": self.look,
            "notes": self.notes,
            "is_assigned": self.is_assigned,
        }


@dataclass(frozen=True)
class ActorListQdto:
    actors: tuple[ActorListRowQdto, ...]

    def to_payload(self) -> dict[str, Any]:
        return {"actors": [a.to_dict() for a in self.actors]}


@dataclass(frozen=True)
class PreviewPromptQdto:
    seed: int
    prompt: str
    body_prompt: str | None = None
    archetype: str | None = None
    archetype_label: str | None = None
    attrs: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {"seed": self.seed, "prompt": self.prompt}
        if self.body_prompt is not None:
            out["body_prompt"] = self.body_prompt
        if self.archetype is not None:
            out["archetype"] = self.archetype
        if self.archetype_label is not None:
            out["archetype_label"] = self.archetype_label
        if self.attrs is not None:
            out["attrs"] = self.attrs
        return out


@dataclass(frozen=True)
class PreviewPromptsQdto:
    prompts: tuple[PreviewPromptQdto, ...]
    resolution: str

    def to_payload(self) -> dict[str, Any]:
        return {"prompts": [p.to_dict() for p in self.prompts], "resolution": self.resolution}


@dataclass(frozen=True)
class ActorAssignmentsQdto:
    actor_id: str
    assignments: list[dict[str, Any]]

    def to_payload(self) -> dict[str, Any]:
        return {"actor_id": self.actor_id, "assignments": self.assignments}


# --- Command DTOs -----------------------------------------------------------


@dataclass(frozen=True)
class GenerateActorsInputCdto:
    count: int
    ethnicity: str
    gender: str
    age_range: str
    look: str
    notes: str
    resolution: str
    seeds: list[int] | None
    archetype: str | None = None
    batch_seed: int | None = None
    batch_size: int | None = None
    slot_index: int | None = None
    eyes: str = ""
    nose: str = ""
    lips: str = ""
    face: str = ""
    skin: str = ""
    body: str = ""
    qi_zhi: str = ""

    def __post_init__(self) -> None:
        # Constructing ActorAttrs runs its own __post_init__ validation.
        ActorAttrs(
            ethnicity=self.ethnicity,
            gender=self.gender,
            age_range=self.age_range,
            look=self.look,
            notes=self.notes,
            eyes=self.eyes,
            nose=self.nose,
            lips=self.lips,
            face=self.face,
            skin=self.skin,
            body=self.body,
            qi_zhi=self.qi_zhi,
        )
        validate_batch_count(self.count)
        validate_resolution(self.resolution)
        validate_seeds(self.seeds, self.count)


@dataclass(frozen=True)
class GenerateDiverseActorsInputCdto:
    """Diverse mode input — user picks only gender + ethnicity + count +
    resolution. Backend rolls age_range / look / style / archetype per slot
    using `_distribute_archetypes` even-distribution (follow-up 053)."""

    count: int
    gender: str
    ethnicity: str
    resolution: str

    def __post_init__(self) -> None:
        validate_batch_count(self.count)
        validate_resolution(self.resolution)


@dataclass(frozen=True)
class GenerateActorsResultCdto:
    generated: list[dict[str, Any]]
    errors: list[dict[str, str]]

    def to_payload(self) -> dict[str, Any]:
        return {"generated": list(self.generated), "errors": list(self.errors)}


@dataclass(frozen=True)
class DeleteActorResultCdto:
    src_rel: str
    dst_rel: str
    unassigned: list[dict[str, str]]

    def to_payload(self) -> dict[str, Any]:
        return {"from": self.src_rel, "to": self.dst_rel, "unassigned": list(self.unassigned)}
