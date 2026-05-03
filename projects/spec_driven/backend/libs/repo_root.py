from __future__ import annotations

from pathlib import Path


class RepoRootNotFoundError(RuntimeError):
    pass


class RepoRoot:
    def __init__(self, path: Path) -> None:
        self._path = path.resolve()

    @property
    def path(self) -> Path:
        return self._path

    def __fspath__(self) -> str:
        return str(self._path)

    def __str__(self) -> str:
        return self._path.as_posix()

    @classmethod
    def find(cls, start: Path | None = None) -> "RepoRoot":
        cur = (start or Path(__file__)).resolve()
        for candidate in [cur, *cur.parents]:
            if (candidate / "CLAUDE.md").is_file() and (candidate / ".claude").is_dir():
                return cls(candidate)
        raise RepoRootNotFoundError(
            f"could not locate repo root from {cur}: no ancestor contains both CLAUDE.md and .claude/"
        )
