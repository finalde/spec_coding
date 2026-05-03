from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import format_datetime, parsedate_to_datetime
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


class InvalidBodyEncoding(Exception):
    pass


class OutsideSandbox(Exception):
    pass


class StaleWrite(Exception):
    def __init__(self, current_mtime: float) -> None:
        super().__init__(f"stale_write: current_mtime={current_mtime}")
        self.current_mtime: float = current_mtime


@dataclass(frozen=True)
class WriteResult:
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


class FileWriter:
    def __init__(self, exposed: ExposedTree, resolver: SafeResolver) -> None:
        self._exposed = exposed
        self._resolver = resolver

    def write(
        self,
        rel: str,
        content: str,
        if_unmodified_since: str | None = None,
    ) -> WriteResult:
        resolved = self._resolver.resolve(rel)
        if resolved is None:
            raise OutsideSandbox()
        ext = Path(rel).suffix.lower() if isinstance(rel, str) else ""
        if ext not in ALLOWED_EXTENSIONS:
            raise UnsupportedExtension(ext)
        if ext in _IMAGE_EXTENSIONS:
            raise UnsupportedExtension(ext)
        if ext not in _TEXT_EXTENSIONS:
            raise UnsupportedExtension(ext)

        body = content.encode("utf-8")
        if len(body) > MAX_FILE_BYTES:
            raise FileTooLarge(len(body))

        prefix = body[:16]
        if b"\x00" in prefix:
            raise InvalidBodyEncoding("nul_in_prefix")
        try:
            prefix.decode("utf-8")
        except UnicodeDecodeError as e:
            try:
                body[: min(64, len(body))].decode("utf-8")
            except UnicodeDecodeError:
                raise InvalidBodyEncoding("invalid_utf8_prefix") from e

        parent = resolved.parent
        if not parent.is_dir():
            raise OutsideSandbox()

        if if_unmodified_since is not None and resolved.exists():
            current_mtime = resolved.stat().st_mtime
            requested = self._parse_http_date(if_unmodified_since)
            if requested is not None:
                if current_mtime > requested + 1.0:
                    raise StaleWrite(current_mtime=current_mtime)

        fd, tmp_path = tempfile.mkstemp(prefix=".tmp_", dir=str(parent))
        try:
            with os.fdopen(fd, "wb") as f:
                f.write(body)
            os.replace(tmp_path, str(resolved))
        except Exception:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise

        stat = resolved.stat()
        mtime_dt = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
        return WriteResult(
            rel_path=Path(rel).as_posix(),
            size_bytes=stat.st_size,
            mtime_unix=stat.st_mtime,
            mtime_http=format_datetime(mtime_dt, usegmt=True),
        )

    @staticmethod
    def _parse_http_date(value: str) -> float | None:
        try:
            dt = parsedate_to_datetime(value)
        except (TypeError, ValueError):
            return None
        if dt is None:
            return None
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.timestamp()
