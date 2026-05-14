from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ReadFileQdto:
    path: str
    content: str
    encoding: str
    size_bytes: int
    mtime_unix: float
    mtime_http: str

    def to_payload(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "content": self.content,
            "encoding": self.encoding,
            "bytes": self.size_bytes,
            "mtime": self.mtime_unix,
            "mtime_http": self.mtime_http,
        }
