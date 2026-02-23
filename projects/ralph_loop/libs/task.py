from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .criterion import Criterion


@dataclass(frozen=True)
class Task:
    id: str
    title: str
    description: str
    instructions: list[str]
    acceptance_criteria: list[Criterion]

    @classmethod
    def _from_dict(cls, data: dict[str, Any]) -> Task:
        task_id: str = (data.get("id") or "").strip()
        if not task_id:
            raise ValueError("Each task must have a non-empty 'id'")
        criteria_raw: list[dict[str, Any]] = data.get("acceptance_criteria") or []
        if not criteria_raw:
            raise ValueError(
                f"Task '{task_id}' has no acceptance_criteria — "
                "every task must have at least one verifiable criterion"
            )
        return cls(
            id=task_id,
            title=(data.get("title") or "").strip(),
            description=(data.get("description") or "").strip(),
            instructions=data.get("instructions") or [],
            acceptance_criteria=[Criterion._from_dict(c) for c in criteria_raw],
        )
