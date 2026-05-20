"""Repository Protocol for the Casting aggregate."""
from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class CastingRepository(Protocol):
    """Read-and-write surface for per-drama casting tables. Implemented by
    libs.infrastructure.casting__writer.Casting."""

    def read(self, rel_drama_path: str) -> object: ...

    def assign(self, rel_drama_path: str, role: str, actor_id: str, notes: str = "") -> object: ...

    def unassign(self, rel_drama_path: str, role: str) -> object: ...

    def find_assignments_for_actor(self, actor_id: str) -> list[dict[str, object]]: ...

    def unassign_actor_everywhere(self, actor_id: str) -> list[dict[str, str]]: ...

    def assigned_actor_ids(self) -> set[str]:
        """Per follow-up 086: single-pass scan of every drama's casting.md
        returning the set of actor_ids appearing in any row. Used by
        `ActorQuery.list()` to tag each actor's `is_assigned` flag in the
        grid listing without N × `find_assignments_for_actor` round-trips."""
        ...
