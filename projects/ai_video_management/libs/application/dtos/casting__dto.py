"""Casting-aggregate DTOs: ReadCastingQuery's Qdto + Assign/Unassign
command inputs. Consolidates `casting__qdto.py` + `casting__cdto.py`."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CastingQdto:
    rel_path: str
    entries: list[dict[str, str]]

    def to_payload(self) -> dict[str, Any]:
        return {"path": self.rel_path, "entries": list(self.entries)}


@dataclass(frozen=True)
class AssignActorInputCdto:
    rel_drama_path: str
    role: str
    actor_id: str
    notes: str = ""


@dataclass(frozen=True)
class UnassignActorInputCdto:
    rel_drama_path: str
    role: str
