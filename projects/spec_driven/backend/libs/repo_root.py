from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RepoRoot:
    path: Path

    @classmethod
    def find(cls, start: Path | None = None) -> "RepoRoot":
        cur = (start or Path.cwd()).resolve()
        for candidate in [cur, *cur.parents]:
            if (candidate / "CLAUDE.md").is_file() and (candidate / ".claude").is_dir():
                return cls(path=candidate)
        raise RuntimeError(
            f"repo root (CLAUDE.md + .claude/) not found walking up from {cur}"
        )
