from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


class RepoRootNotFound(Exception):
    pass


@dataclass(frozen=True)
class RepoRootMarkers:
    must_contain: tuple[str, ...] = ("CLAUDE.md", "specs", ".claude")

    def matches(self, candidate: Path) -> bool:
        return all((candidate / name).exists() for name in self.must_contain)


def discover_repo_root(start: Path, markers: RepoRootMarkers | None = None) -> Path:
    markers = markers or RepoRootMarkers()
    current = start if start.is_dir() else start.parent
    for candidate in (current, *current.parents):
        if markers.matches(candidate):
            return candidate.resolve()
    raise RepoRootNotFound(
        f"could not locate repo root above {start}; "
        f"need a directory containing all of {markers.must_contain}"
    )
