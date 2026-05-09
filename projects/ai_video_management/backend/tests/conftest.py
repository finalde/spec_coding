"""Shared test fixtures."""
from __future__ import annotations

import sys
from pathlib import Path

# Make backend/libs importable as `libs.*` from any test
_BACKEND = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_BACKEND))


def repo_root() -> Path:
    """Walk up from CWD looking for an `ai_videos/` directory — same logic as RepoRoot.find()."""
    cur = Path.cwd().resolve()
    for c in [cur, *cur.parents]:
        if (c / "ai_videos").is_dir():
            return c
    raise RuntimeError(f"workspace root (parent of ai_videos/) not found from {cur}")
