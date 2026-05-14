from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AddPromotionCdto:
    project_type: str
    project_name: str
    stage_folder: str
    source_file: str
    item_id: str
    item_text: str


@dataclass(frozen=True)
class RemovePromotionCdto:
    project_type: str
    project_name: str
    stage_folder: str
    item_id: str


@dataclass(frozen=True)
class PromotionResultCdto:
    status: str
    item_id: str

    def to_payload(self) -> dict[str, Any]:
        return {"status": self.status, "item_id": self.item_id}
