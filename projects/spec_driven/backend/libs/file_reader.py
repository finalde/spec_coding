from __future__ import annotations

import base64
from dataclasses import dataclass
from email.utils import format_datetime
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from libs.exposed_tree import ALLOWED_EXTENSIONS, MAX_FILE_BYTES, ExposedTree
from libs.safe_resolve import SafeResolver

_TEXT_EXTENSIONS: frozenset[str] = frozenset(
    {".md", ".json", ".yaml", ".yml", ".jsonl", ".txt"}
)
_IMAGE_EXTENSIONS: frozenset[str] = frozenset({".png", ".jpg"})


class UnsupportedExtension(Exception):
    pass


class FileTooLarge(Exception):
    pass


class OutsideSandbox(Exception):
    pass


@dataclass(frozen=True)
class ReadResult:
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


class FileReader:
    def __init__(self, exposed: ExposedTree, resolver: SafeResolver) -> None:
        self._exposed = exposed
        self._resolver = resolver

    def read(self, rel: str) -> ReadResult:
        resolved = self._resolver.resolve(rel)
        if resolved is None:
            raise OutsideSandbox()
        ext = Path(rel).suffix.lower() if isinstance(rel, str) else ""
        if ext not in ALLOWED_EXTENSIONS:
            raise UnsupportedExtension(ext)
        if not resolved.is_file():
            raise OutsideSandbox()
        try:
            stat = resolved.stat()
        except OSError as e:
            raise OutsideSandbox() from e
        if stat.st_size > MAX_FILE_BYTES:
            raise FileTooLarge(stat.st_size)
        raw = resolved.read_bytes()
        if ext in _IMAGE_EXTENSIONS:
            content = base64.b64encode(raw).decode("ascii")
            encoding = "base64"
        else:
            content = raw.decode("utf-8", errors="replace")
            encoding = "utf-8"
        mtime_dt = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
        return ReadResult(
            rel_path=Path(rel).as_posix(),
            content=content,
            encoding=encoding,
            size_bytes=stat.st_size,
            mtime_unix=stat.st_mtime,
            mtime_http=format_datetime(mtime_dt, usegmt=True),
        )

    @staticmethod
    def security_headers(filename: str) -> dict[str, str]:
        safe = "".join(c for c in filename if 32 <= ord(c) < 127 and c not in '"\\')
        if not safe:
            safe = "file"
        return {
            "X-Content-Type-Options": "nosniff",
            "Content-Disposition": f'attachment; filename="{safe}"',
        }
