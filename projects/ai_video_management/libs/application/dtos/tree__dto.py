"""Tree-aggregate DTOs: GetTreeQuery's Qdto.
Renamed from the former `tree__qdto.py`."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class TreeQdto:
    root: dict[str, Any]

    def to_payload(self) -> dict[str, Any]:
        return self.root
