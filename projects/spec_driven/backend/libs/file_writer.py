from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

from libs.exposed_tree import ALLOWED_EXTENSIONS, ExposedTree
from libs.file_reader import MAX_FILE_BYTES, FileReadError
from libs.safe_resolve import OutsideSandbox, SymlinkRefused, safe_resolve


@dataclass(frozen=True)
class FileWriteResult:
    path: str
    bytes_size: int


def write_file(rel: str, text: str, repo_root: Path) -> FileWriteResult:
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

    if "\x00" in text:
        raise FileReadError(415, "binary_content", kind="binary_content")

    encoded = text.encode("utf-8")
    if len(encoded) > MAX_FILE_BYTES:
        raise FileReadError(413, "too_large", kind="too_large")

    parent = resolved.parent
    if not parent.exists():
        raise FileReadError(404, "not_found", kind="parent_missing")

    tmp_fd, tmp_path = tempfile.mkstemp(prefix=".tmp-", suffix=ext, dir=str(parent))
    try:
        with os.fdopen(tmp_fd, "wb") as fh:
            fh.write(encoded)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp_path, resolved)
    except PermissionError:
        _cleanup(tmp_path)
        raise FileReadError(403, "permission_denied", kind="permission_denied")
    except OSError:
        _cleanup(tmp_path)
        raise FileReadError(500, "write_failed", kind="write_failed")

    return FileWriteResult(path=relative.as_posix(), bytes_size=len(encoded))


def _cleanup(tmp_path: str) -> None:
    try:
        os.unlink(tmp_path)
    except OSError:
        pass
