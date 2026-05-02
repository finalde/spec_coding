from __future__ import annotations

from functools import cache
from pathlib import Path


class RepoRootNotFound(Exception):
    pass


_REQUIRED_MARKERS: tuple[str, ...] = ("CLAUDE.md", "specs", ".claude")


@cache
def discover_repo_root(start: Path) -> Path:
    current = start.resolve()
    while True:
        if all((current / marker).exists() for marker in _REQUIRED_MARKERS):
            return current
        parent = current.parent
        if parent == current:
            raise RepoRootNotFound(
                "could not locate REPO_ROOT (no ancestor contains all of: "
                "CLAUDE.md, specs/, .claude/)"
            )
        current = parent
