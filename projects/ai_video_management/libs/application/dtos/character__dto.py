"""Character read-side DTOs: per-folder newest turntable video listing."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CharacterVideoListingQdto:
    folder: str
    latest_video: str | None

    def to_payload(self) -> dict[str, Any]:
        return {"folder": self.folder, "latest_video": self.latest_video}


@dataclass(frozen=True)
class CharacterVideoListQdto:
    items: tuple[CharacterVideoListingQdto, ...]

    def to_payload(self) -> dict[str, Any]:
        return {"items": [i.to_payload() for i in self.items]}
