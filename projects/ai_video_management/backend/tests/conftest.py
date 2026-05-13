"""Shared test fixtures."""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Make backend/libs importable as `libs.*` from any test
_BACKEND = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_BACKEND))

# Per follow-up 025: ActorPool requires KLING_ACCESS_KEY + KLING_SECRET_KEY at
# create_app() time. Tests don't hit Kling (TestClient never reaches the
# outbound HTTP path under normal API-security tests), but the failfast still
# fires. Load backend/.env if present; fall back to placeholders so a clean
# checkout without a .env still runs the non-Kling test suite.
os.environ.setdefault("KLING_ACCESS_KEY", "test-ak-placeholder")
os.environ.setdefault("KLING_SECRET_KEY", "test-sk-placeholder")


def repo_root() -> Path:
    """Walk up from CWD looking for an `ai_videos/` directory — same logic as RepoRoot.find()."""
    cur = Path.cwd().resolve()
    for c in [cur, *cur.parents]:
        if (c / "ai_videos").is_dir():
            return c
    raise RuntimeError(f"workspace root (parent of ai_videos/) not found from {cur}")
