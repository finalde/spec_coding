"""Downloads-aggregate DTOs: ImportFromDownloadsCommand's result Cdto.
Renamed from the former `downloads__cdto.py`."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ImportFromDownloadsResultCdto:
    moved: list[dict[str, str]]
    unmatched: list[dict[str, str]]
    errors: list[dict[str, str]]
    rename: dict[str, Any]

    def to_payload(self) -> dict[str, Any]:
        return {
            "moved": list(self.moved),
            "unmatched": list(self.unmatched),
            "errors": list(self.errors),
            "rename": self.rename,
        }
