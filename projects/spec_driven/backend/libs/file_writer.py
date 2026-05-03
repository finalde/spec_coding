"""
file_writer — backing module for PUT /api/file (FR-6, FR-7, FR-8, NFR-10).

- 1 MB body cap (FR-7); over -> 413 with {detail: {kind: "too_large"}}.
- First 16 bytes must be valid UTF-8 with no NUL byte (FR-8); failure -> 415
  with {detail: {kind: "not_text"}}.
- Image extensions (.png, .jpg) are NOT writable in v1 (FR-8) -> 415.
- SVG is NOT in the allowlist (NFR-9) -> 415.
- Atomic write: temp file in same directory + os.replace (NFR-10).
"""

from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .file_reader import (
    ALLOWED_TEXT_EXT,
    MAX_BYTES,
    NotFoundError,
    TooLargeError,
    UnsupportedExtensionError,
)
from .safe_resolve import OutsideTreeError, SafeResolver


class NotTextError(Exception):
    pass


@dataclass(frozen=True)
class WriteResult:
    path: str
    bytes: int
    mtime: str

    def to_dict(self) -> dict:
        return {"path": self.path, "bytes": self.bytes, "mtime": self.mtime}


@dataclass(frozen=True)
class FileWriter:
    resolver: SafeResolver

    def write(self, rel: str, content: str) -> WriteResult:
        encoded = content.encode("utf-8")
        if len(encoded) > MAX_BYTES:
            raise TooLargeError("too_large")

        try:
            absolute = self.resolver.resolve(rel)
        except OutsideTreeError as e:
            raise NotFoundError("not found") from e

        ext = absolute.suffix.lower()
        if ext not in ALLOWED_TEXT_EXT:
            raise UnsupportedExtensionError("unsupported_extension")

        head = encoded[:16]
        if b"\x00" in head:
            raise NotTextError("not_text")
        try:
            head.decode("utf-8")
        except UnicodeDecodeError:
            try:
                encoded[:32].decode("utf-8")
            except UnicodeDecodeError as e:
                raise NotTextError("not_text") from e

        absolute.parent.mkdir(parents=True, exist_ok=True)

        fd, tmp_path = tempfile.mkstemp(prefix=".tmp-", dir=str(absolute.parent))
        try:
            with os.fdopen(fd, "wb") as f:
                f.write(encoded)
                f.flush()
                try:
                    os.fsync(f.fileno())
                except OSError:
                    pass
            os.replace(tmp_path, absolute)
        except Exception:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise

        st = absolute.stat()
        rel_normalized = absolute.resolve().relative_to(self.resolver.root).as_posix()
        mtime = datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).isoformat()
        return WriteResult(path=rel_normalized, bytes=st.st_size, mtime=mtime)
