from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

ANCHOR_DIR_NAME: str = "ai_videos"


@dataclass(frozen=True)
class RepoRoot:
    """Workspace root resolution.

    The webapp's root is the parent directory of `ai_videos/`. `find()` walks
    up from the start directory looking for a directory that contains
    `ai_videos/` as a child; the parent of that match becomes the workspace root.
    """

    path: Path

    @classmethod
    def find(cls, start: Path | None = None) -> "RepoRoot":
        cur = (start or Path.cwd()).resolve()
        for candidate in [cur, *cur.parents]:
            if (candidate / ANCHOR_DIR_NAME).is_dir():
                return cls(path=candidate)
        raise RuntimeError(
            f"workspace root (parent of {ANCHOR_DIR_NAME}/) not found walking up from {cur}"
        )
