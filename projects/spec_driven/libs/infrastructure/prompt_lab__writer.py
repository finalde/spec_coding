from __future__ import annotations

import os
import re
import shutil
import tempfile
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path
from typing import Any

from libs.common.exposed_tree import MAX_FILE_BYTES, ExposedTree
from libs.common.safe_resolve import SafeResolver
from libs.domain.prompt_lab__error import (
    PromptLabFileExists,
    PromptLabFileNotFound,
    PromptLabPathRejected,
)

_SLUG = re.compile(r"^[A-Za-z0-9_-]+$")


def valid_prompt_path(rel: str) -> bool:
    """A structurally well-formed prompt_lab/{cat}/{task}/prompt.md path (no traversal)."""
    if not isinstance(rel, str) or rel != rel.strip():
        return False
    if not rel.startswith("prompt_lab/") or not rel.endswith("/prompt.md"):
        return False
    if "\\" in rel or "\x00" in rel:
        return False
    parts = rel.split("/")
    if len(parts) != 4:
        return False
    return not any(p in ("", "..", ".") for p in parts)


class PromptLabFileTooLarge(Exception):
    pass


class PromptLabWriter:
    """Create / delete prompt_lab items. Each item is a folder {category}/{task}/ whose
    instruction is prompt.md; deleting an item removes its whole folder (FR-43/FR-44)."""

    def __init__(self, exposed: ExposedTree, resolver: SafeResolver) -> None:
        self._exposed = exposed
        self._resolver = resolver
        self._root = resolver.root

    def create(self, category: str, filename: str, content: str) -> dict[str, Any]:
        if not _SLUG.match(category or ""):
            raise PromptLabPathRejected()
        if not filename.endswith(".md") or not _SLUG.match(filename[:-3]):
            raise PromptLabPathRejected()
        task = filename[:-3]

        cat_resolved = self._resolver.resolve(f"prompt_lab/{category}")
        if cat_resolved is None:
            raise PromptLabPathRejected()
        cat_resolved.mkdir(parents=True, exist_ok=True)

        item_resolved = self._resolver.resolve(f"prompt_lab/{category}/{task}")
        if item_resolved is None:
            raise PromptLabPathRejected()
        if (item_resolved / "prompt.md").exists():
            raise PromptLabFileExists()
        item_resolved.mkdir(parents=True, exist_ok=True)

        rel = f"prompt_lab/{category}/{task}/prompt.md"
        resolved = self._resolver.resolve(rel)
        if resolved is None:
            raise PromptLabPathRejected()

        body = content.encode("utf-8")
        if len(body) > MAX_FILE_BYTES:
            raise PromptLabFileTooLarge()

        self._atomic_write(resolved, body)
        return self._result(rel, resolved)

    def delete(self, rel: str) -> dict[str, Any]:
        if not valid_prompt_path(rel):
            raise PromptLabPathRejected()
        resolved = self._resolver.resolve(rel)
        if resolved is None or not resolved.is_file():
            raise PromptLabFileNotFound()
        item_dir = resolved.parent
        shutil.rmtree(item_dir)
        return {"path": "/".join(rel.split("/")[:-1]), "deleted": True}

    @staticmethod
    def _atomic_write(resolved: Path, body: bytes) -> None:
        fd, tmp = tempfile.mkstemp(prefix=".tmp_", dir=str(resolved.parent))
        try:
            with os.fdopen(fd, "wb") as f:
                f.write(body)
            os.replace(tmp, str(resolved))
        except Exception:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise

    @staticmethod
    def _result(rel: str, resolved: Path) -> dict[str, Any]:
        stat = resolved.stat()
        mtime_dt = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
        return {
            "path": Path(rel).as_posix(),
            "bytes": stat.st_size,
            "mtime": stat.st_mtime,
            "mtime_http": format_datetime(mtime_dt, usegmt=True),
        }
