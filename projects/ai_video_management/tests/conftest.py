"""Shared test fixtures."""
from __future__ import annotations

import os
import sys
from pathlib import Path

_SOLUTION_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_SOLUTION_ROOT))

os.environ.setdefault("KLING_ACCESS_KEY", "test-ak-placeholder")
os.environ.setdefault("KLING_SECRET_KEY", "test-sk-placeholder")


def repo_root() -> Path:
    """Walk up from CWD looking for an `ai_videos/` directory — same logic as RepoRoot.find()."""
    cur = Path.cwd().resolve()
    for c in [cur, *cur.parents]:
        if (c / "ai_videos").is_dir():
            return c
    raise RuntimeError(f"workspace root (parent of ai_videos/) not found from {cur}")


def make_app(rr, bound, serve_static: bool = False):
    """Build a wired Container + FastAPI app for tests.

    Mirrors apps.api.main._build_container without uvicorn/argparse.
    """
    from apps.api.container import Container
    from apps.api.routes import create_app

    container = Container()
    container.repo_root_path.override(rr.path)
    container.bound_origin.override(bound)
    container.wire(modules=["apps.api.routes"])
    return create_app(container, serve_static=serve_static)
