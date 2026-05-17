"""CastingEntity — per-drama aggregate root. Holds the list of role→actor
mappings and enforces invariants (role uniqueness, role shape) on assign /
unassign. The on-disk casting.md and the _cast.md sibling are written by
the infrastructure CastingWriter; this entity is the canonical in-memory
form.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from libs.domain.value_objects.casting__valueobject import CastEntry
from libs.domain.errors.casting__error import InvalidRoleError, RoleNotFoundError

_ROLE_INVALID_RE = re.compile(r"[\x00-\x1f|]")
_ROLE_MAX_LEN: int = 200


def validate_role(role: str) -> None:
    if not isinstance(role, str) or not role.strip():
        raise InvalidRoleError("role must be a non-empty string")
    if len(role) > _ROLE_MAX_LEN:
        raise InvalidRoleError(f"role must be ≤ {_ROLE_MAX_LEN} characters")
    if _ROLE_INVALID_RE.search(role):
        raise InvalidRoleError("role contains control characters or markdown table separator")


@dataclass
class CastingEntity:
    drama_name: str
    entries: list[CastEntry] = field(default_factory=list)

    def assign(self, role: str, actor_id: str, notes: str = "") -> None:
        """Add or replace the row for this role. role-uniqueness invariant:
        a role can appear at most once. Replacing is upsert semantics."""
        validate_role(role)
        self.entries = [e for e in self.entries if e.role != role]
        self.entries.append(CastEntry(role=role, actor_id=actor_id, notes=notes))

    def unassign(self, role: str) -> None:
        """Drop the row for this role. Raises RoleNotFoundError if absent."""
        validate_role(role)
        before = len(self.entries)
        self.entries = [e for e in self.entries if e.role != role]
        if len(self.entries) == before:
            raise RoleNotFoundError(f"role={role!r} not in casting")

    def to_dicts(self) -> list[dict[str, str]]:
        return [e.to_dict() for e in self.entries]
