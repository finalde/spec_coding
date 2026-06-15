from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PromptLabQdto:
    categories: list[dict[str, Any]]

    def to_payload(self) -> dict[str, Any]:
        return {"categories": self.categories}
