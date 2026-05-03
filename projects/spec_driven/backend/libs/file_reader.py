"""
file_reader — backing module for GET /api/file (FR-3, FR-5, AC-2, AC-7, AC-8).

- Allowed extensions: .md, .json, .yaml, .yml, .jsonl, .txt, .png, .jpg
- Files >1 MB return 413 (size check via os.stat BEFORE any read).
- Anything outside the EXPOSED_TREE returns 404 (single status — no enumeration
  side-channel between "missing inside tree" and "outside tree").
"""

from __future__ import annotations

import base64
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .safe_resolve import OutsideTreeError, SafeResolver

ALLOWED_TEXT_EXT = frozenset({".md", ".json", ".yaml", ".yml", ".jsonl", ".txt"})
ALLOWED_IMAGE_EXT = frozenset({".png", ".jpg"})
ALLOWED_EXT = ALLOWED_TEXT_EXT | ALLOWED_IMAGE_EXT
MAX_BYTES = 1 * 1024 * 1024


class NotFoundError(Exception):
    """Maps to HTTP 404. Used for both 'missing inside tree' and 'outside tree'."""


class TooLargeError(Exception):
    pass


class UnsupportedExtensionError(Exception):
    pass


@dataclass(frozen=True)
class ReadResult:
    path: str
    content: str
    mtime: str
    bytes: int
    is_image: bool

    def to_dict(self) -> dict:
        d = {"path": self.path, "content": self.content, "mtime": self.mtime, "bytes": self.bytes}
        if self.is_image:
            d["data_encoding"] = "base64"
        return d


@dataclass(frozen=True)
class FileReader:
    resolver: SafeResolver

    def read(self, rel: str) -> ReadResult:
        try:
            absolute = self.resolver.resolve(rel)
        except OutsideTreeError as e:
            raise NotFoundError("not found") from e

        ext = absolute.suffix.lower()
        if ext not in ALLOWED_EXT:
            raise UnsupportedExtensionError("unsupported_extension")

        if not absolute.is_file():
            raise NotFoundError("not found")

        st = absolute.stat()
        if st.st_size > MAX_BYTES:
            raise TooLargeError("too_large")

        is_image = ext in ALLOWED_IMAGE_EXT
        if is_image:
            content = base64.b64encode(absolute.read_bytes()).decode("ascii")
        else:
            content = absolute.read_bytes().decode("utf-8", errors="replace")

        rel_normalized = rel.replace("\\", "/").lstrip("./")
        try:
            rel_normalized = absolute.resolve().relative_to(self.resolver.root).as_posix()
        except ValueError:
            pass

        mtime = datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).isoformat()
        return ReadResult(
            path=rel_normalized,
            content=content,
            mtime=mtime,
            bytes=st.st_size,
            is_image=is_image,
        )
