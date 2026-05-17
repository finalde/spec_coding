"""Media-aggregate queries: serve a media file by sandbox-relative path."""
from __future__ import annotations

from pathlib import Path

from libs.application.dtos.media__dto import MediaFileQdto
from libs.common.exposed_tree import MEDIA_EXTENSIONS, ExposedTree
from libs.common.safe_resolve import SafeResolver
from libs.domain.errors.file__error import (
    FileNotInSandboxError,
    UnsupportedFileExtensionError,
)

_MEDIA_MIME_MAP: dict[str, str] = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".gif": "image/gif",
    ".bmp": "image/bmp",
    ".mp4": "video/mp4",
    ".mov": "video/quicktime",
    ".webm": "video/webm",
    ".mkv": "video/x-matroska",
    ".avi": "video/x-msvideo",
    ".m4v": "video/mp4",
}


class MediaQuery:
    def __init__(self, exposed: ExposedTree, resolver: SafeResolver) -> None:
        self._exposed = exposed
        self._resolver = resolver

    def serve(self, rel_path: str) -> MediaFileQdto:
        ext = Path(rel_path).suffix.lower() if isinstance(rel_path, str) else ""
        if ext not in MEDIA_EXTENSIONS:
            raise UnsupportedFileExtensionError(ext)
        if not self._exposed.is_inside(rel_path):
            raise FileNotInSandboxError(rel_path)
        resolved = self._resolver.resolve(rel_path)
        if resolved is None or not resolved.is_file():
            raise FileNotInSandboxError(rel_path)
        return MediaFileQdto(
            resolved_path=resolved,
            media_type=_MEDIA_MIME_MAP.get(ext, "application/octet-stream"),
            filename=resolved.name,
        )
