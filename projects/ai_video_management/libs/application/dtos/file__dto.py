"""File-aggregate DTOs: ReadFileQuery's Qdto + WriteFileCommand's input/result.
Consolidates `file__qdto.py` + `file__cdto.py`."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class FileReadQdto:
    rel_path: str
    content: str
    encoding: str
    size_bytes: int
    mtime_unix: float
    mtime_http: str

    def to_payload(self) -> dict[str, Any]:
        return {
            "path": self.rel_path,
            "content": self.content,
            "encoding": self.encoding,
            "bytes": self.size_bytes,
            "mtime": self.mtime_unix,
            "mtime_http": self.mtime_http,
        }


@dataclass(frozen=True)
class WriteFileInputCdto:
    rel_path: str
    content: str
    if_unmodified_since: str | None


@dataclass(frozen=True)
class FileWriteResultCdto:
    rel_path: str
    size_bytes: int
    mtime_unix: float
    mtime_http: str

    def to_payload(self) -> dict[str, Any]:
        return {
            "path": self.rel_path,
            "bytes": self.size_bytes,
            "mtime": self.mtime_unix,
            "mtime_http": self.mtime_http,
        }
