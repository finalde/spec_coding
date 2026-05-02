from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from libs.exposed_tree import ALLOWED_EXTENSIONS, ExposedTree
from libs.safe_resolve import OutsideSandbox, SymlinkRefused, safe_resolve


MAX_FILE_BYTES: int = 2 * 1024 * 1024


class FileReadError(Exception):
    def __init__(self, status: int, error: str, kind: str | None = None) -> None:
        super().__init__(error)
        self.status: int = status
        self.error: str = error
        self.kind: str | None = kind

    def to_dict(self) -> dict[str, object]:
        body: dict[str, object] = {"error": self.error}
        if self.kind:
            body["kind"] = self.kind
        return body


@dataclass(frozen=True)
class FileContent:
    path: str
    extension: str
    bytes_size: int
    text: str


def _to_posix(rel: Path) -> str:
    return rel.as_posix()


def read_file(rel: str, repo_root: Path) -> FileContent:
    try:
        relative = safe_resolve(rel, repo_root)
    except (OutsideSandbox, SymlinkRefused):
        raise FileReadError(400, "outside_sandbox", kind="outside_sandbox")

    resolved = (repo_root / relative).resolve(strict=False)

    if not ExposedTree(repo_root).is_inside(resolved):
        raise FileReadError(404, "not_found", kind="outside_exposed_tree")

    ext = resolved.suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise FileReadError(415, "unsupported_extension", kind="unsupported_extension")

    try:
        size = resolved.stat().st_size
    except FileNotFoundError:
        raise FileReadError(404, "not_found", kind="file_removed")
    except PermissionError:
        raise FileReadError(403, "permission_denied", kind="permission_denied")
    except IsADirectoryError:
        raise FileReadError(400, "is_directory", kind="is_directory")

    if resolved.is_dir():
        raise FileReadError(400, "is_directory", kind="is_directory")

    if size > MAX_FILE_BYTES:
        raise FileReadError(413, "too_large", kind="too_large")

    try:
        text = resolved.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        raise FileReadError(404, "not_found", kind="file_removed")
    except PermissionError:
        raise FileReadError(403, "permission_denied", kind="permission_denied")
    except IsADirectoryError:
        raise FileReadError(400, "is_directory", kind="is_directory")

    if "\x00" in text:
        raise FileReadError(415, "binary_content", kind="binary_content")

    return FileContent(
        path=_to_posix(relative),
        extension=ext,
        bytes_size=size,
        text=text,
    )
