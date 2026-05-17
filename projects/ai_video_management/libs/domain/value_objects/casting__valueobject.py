"""CastEntry value object — one row in a drama's casting.md table."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CastEntry:
    role: str
    actor_id: str
    notes: str

    def to_dict(self) -> dict[str, str]:
        return {"role": self.role, "actor_id": self.actor_id, "notes": self.notes}
