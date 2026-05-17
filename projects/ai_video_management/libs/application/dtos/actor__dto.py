"""Actor-aggregate DTOs: queries' Qdtos + commands' Cdtos.

Consolidates the former `actor__qdto.py` + `actor__cdto.py`. One DTO
file per aggregate per follow-up 059; the Q/C suffix on each class name
already disambiguates intent within the file.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


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
    style: str
    notes: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.actor_id,
            "image_path": self.image_path,
            "mtime": self.mtime,
            "ethnicity": self.ethnicity,
            "gender": self.gender,
            "age_range": self.age_range,
            "look": self.look,
            "style": self.style,
            "notes": self.notes,
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
    # Per follow-up 052: optional body-shot prompt rendered alongside face.
    body_prompt: str | None = None
    # Per follow-up 059 (diverse-mode preview): rolled archetype + attrs the
    # frontend's confirm path forwards to per-slot `generate_batch` calls.
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
    style: str
    notes: str
    resolution: str
    seeds: list[int] | None
    # Per follow-up 059: optional archetype slug that diverse-mode confirm
    # path forwards per slot so each actor's sidecar carries the archetype
    # row from first write. Standard-mode callers pass None (the sidecar
    # gets backfilled by `migrate_archetypes()` at next startup).
    archetype: str | None = None


@dataclass(frozen=True)
class GenerateDiverseActorsInputCdto:
    """Per follow-up 053: diverse mode input — user picks only gender +
    ethnicity + count + resolution. Backend rolls age_range / look / style /
    archetype per slot using `_distribute_archetypes` even-distribution."""

    count: int
    gender: str
    ethnicity: str
    resolution: str


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
