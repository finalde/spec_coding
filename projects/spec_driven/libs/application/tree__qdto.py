from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class TreeQdto:
    tree: dict[str, Any]

    def to_payload(self) -> dict[str, Any]:
        return self.tree
