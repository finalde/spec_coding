from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from libs.exposed_tree import ALLOWED_EXTENSIONS, ExposedTree
from libs.safe_resolve import OutsideSandbox, SymlinkRefused, safe_resolve

MAX_FILE_BYTES: int = 2 * 1024 * 1024


@dataclass(frozen=True)
class FileReadError(Exception):
    status: int
    error: str
    kind: str | None = None

    def __post_init__(self) -> None:
        super().__init__(f"{self.status} {self.error}{f' ({self.kind})' if self.kind else ''}")

    def to_dict(self) -> dict[str, str]:
        out: dict[str, str] = {"error": self.error}
        if self.kind is not None:
            out["kind"] = self.kind
        return out


@dataclass(frozen=True)
class FileContent:
    path: str
    extension: str
    bytes_size: int
    text: str


def _classify_extension(path: Path) -> str:
    return path.suffix.lower()


def read_file(rel: str, repo_root: Path) -> FileContent:
    try:
        resolved = safe_resolve(rel, repo_root)
    except OutsideSandbox as err:
        raise FileReadError(status=400, error="outside_sandbox") from err
    except SymlinkRefused as err:
        raise FileReadError(status=400, error="outside_sandbox") from err

    tree = ExposedTree(repo_root=repo_root)
    if not tree.is_inside(resolved):
        raise FileReadError(status=404, error="not_found", kind="outside_exposed_tree")

    extension = _classify_extension(resolved)
    if extension not in ALLOWED_EXTENSIONS:
        raise FileReadError(status=415, error="unsupported_extension")

    try:
        size = resolved.stat().st_size
    except FileNotFoundError as err:
        raise FileReadError(status=404, error="not_found", kind="file_removed") from err
    except PermissionError as err:
        raise FileReadError(status=403, error="permission_denied") from err
    except IsADirectoryError as err:
        raise FileReadError(status=400, error="is_directory") from err

    if size > MAX_FILE_BYTES:
        raise FileReadError(status=413, error="too_large")

    try:
        text = resolved.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError as err:
        raise FileReadError(status=404, error="not_found", kind="file_removed") from err
    except PermissionError as err:
        raise FileReadError(status=403, error="permission_denied") from err
    except IsADirectoryError as err:
        raise FileReadError(status=400, error="is_directory") from err

    if "\x00" in text:
        raise FileReadError(status=415, error="binary_content")

    return FileContent(
        path=str(resolved.relative_to(repo_root)).replace("\\", "/"),
        extension=extension,
        bytes_size=size,
        text=text,
    )
