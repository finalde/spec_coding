from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class WriteFileCdto:
    path: str
    content: str
    if_unmodified_since: str | None = None


@dataclass(frozen=True)
class WriteFileResultCdto:
    path: str
    size_bytes: int
    mtime_unix: float
    mtime_http: str

    def to_payload(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "bytes": self.size_bytes,
            "mtime": self.mtime_unix,
            "mtime_http": self.mtime_http,
        }
