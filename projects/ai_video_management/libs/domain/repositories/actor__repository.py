"""Repository Protocol for the Actor aggregate. Concrete implementation
lives in libs/infrastructure/ — the domain only sees this interface (the
dependency-inversion seam per development.md §2).

Per follow-up 114: the previous return type `list[ActorEntity]` was a lie
— the concrete `ActorPool.list_actors()` returns `list[ActorInfo]` (an
infrastructure dataclass). The Protocol now reflects reality. Phase 2 will
move `ActorInfo` into the domain as a proper dataclass and re-tighten this
seam; in the meantime, the Protocol's honesty matters more than the
direction of the import.
"""
from __future__ import annotations

from pathlib import Path
from typing import Protocol, TYPE_CHECKING

from libs.domain.value_objects.actor__valueobject import ActorAttrs

if TYPE_CHECKING:
    from libs.infrastructure.writers.actor__writer import ActorInfo


class ActorRepository(Protocol):
    """Read-and-write surface for AI-generated actor faces. Implemented by
    `libs.infrastructure.writers.actor__writer.ActorPool`."""

    def actor_exists(self, actor_id: str) -> bool: ...

    def list_actors(self, include_pending: bool = False) -> "list[ActorInfo]": ...

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

    def create_prompts_batch(
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
