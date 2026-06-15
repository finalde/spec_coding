from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CreatePromptLabFileCdto:
    category: str
    filename: str
    content: str


@dataclass(frozen=True)
class DeletePromptLabFileCdto:
    path: str


@dataclass(frozen=True)
class PromptLabFileResultCdto:
    path: str
    bytes: int
    mtime: float
    mtime_http: str

    def to_payload(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "bytes": self.bytes,
            "mtime": self.mtime,
            "mtime_http": self.mtime_http,
        }


@dataclass(frozen=True)
class DeletePromptLabResultCdto:
    path: str

    def to_payload(self) -> dict[str, Any]:
        return {"path": self.path, "deleted": True}
