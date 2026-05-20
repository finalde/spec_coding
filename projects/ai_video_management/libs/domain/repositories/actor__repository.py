"""Repository Protocol for the Actor aggregate. Concrete implementation
lives in libs/infrastructure/ — the domain only sees this interface (the
dependency-inversion seam per development.md §2).
"""
from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable

from libs.domain.entities.actor__entity import ActorEntity
from libs.domain.value_objects.actor__valueobject import ActorAttrs


@runtime_checkable
class ActorRepository(Protocol):
    """Read-and-write surface for AI-generated actor faces. Implemented by
    libs.infrastructure.actor_pool__writer.ActorPool."""

    def actor_exists(self, actor_id: str) -> bool: ...

    def list_actors(self) -> list[ActorEntity]: ...

    def actor_face_filename(self, actor_id: str) -> str | None: ...

    def actors_dir(self) -> Path: ...

    def delete_actor(self, actor_id: str) -> dict[str, str]: ...

    def generate_batch(
        self,
        attrs: ActorAttrs,
        count: int,
        resolution: str,
        seeds: list[int] | None,
        archetype: str | None = None,
        batch_seed: int | None = None,
        batch_size: int | None = None,
        slot_index: int | None = None,
    ) -> object: ...

    def preview_prompts(
        self,
        attrs: ActorAttrs,
        count: int,
        resolution: str,
        seeds: list[int] | None = None,
        archetype: str | None = None,
        batch_seed: int | None = None,
        batch_size: int | None = None,
        slot_index: int | None = None,
    ) -> dict[str, object]: ...

    def preview_diverse_prompts(
        self,
        gender: str,
        ethnicity: str,
        count: int,
        resolution: str,
    ) -> dict[str, object]: ...

    def generate_diverse_batch(
        self,
        gender: str,
        ethnicity: str,
        count: int,
        resolution: str,
    ) -> object: ...

    def actor_body_filename(self, actor_id: str) -> str | None: ...
