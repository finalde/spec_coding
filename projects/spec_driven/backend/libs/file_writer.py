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
        resolved = safe_resolve(rel, repo_root)
    except OutsideSandbox as err:
        raise FileReadError(status=400, error="outside_sandbox") from err
    except SymlinkRefused as err:
        raise FileReadError(status=400, error="outside_sandbox") from err

    tree = ExposedTree(repo_root=repo_root)
    if not tree.is_inside(resolved):
        raise FileReadError(status=404, error="not_found", kind="outside_exposed_tree")

    extension = resolved.suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise FileReadError(status=415, error="unsupported_extension")

    encoded = text.encode("utf-8")
    if len(encoded) > MAX_FILE_BYTES:
        raise FileReadError(status=413, error="too_large")

    if "\x00" in text:
        raise FileReadError(status=415, error="binary_content")

    parent = resolved.parent
    if not parent.is_dir():
        raise FileReadError(status=404, error="not_found", kind="parent_missing")

    fd, tmp_path = tempfile.mkstemp(prefix=".tmp-", suffix=resolved.suffix, dir=str(parent))
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(encoded)
        os.replace(tmp_path, resolved)
    except PermissionError as err:
        try:
            os.unlink(tmp_path)
        except FileNotFoundError:
            pass
        raise FileReadError(status=403, error="permission_denied") from err
    except OSError as err:
        try:
            os.unlink(tmp_path)
        except FileNotFoundError:
            pass
        raise FileReadError(status=500, error="write_failed") from err

    return FileWriteResult(
        path=str(resolved.relative_to(repo_root)).replace("\\", "/"),
        bytes_size=len(encoded),
    )
