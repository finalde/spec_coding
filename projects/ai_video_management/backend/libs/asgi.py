"""ASGI app factory for uvicorn reload-mode.

`main.py` passes the import-string `"libs.asgi:app"` to `uvicorn.run`
when reload is enabled (uvicorn's `reload=True` requires an import-string,
not an app instance). The constructed app here mirrors `main.py`'s default
construction: `RepoRoot.find()` anchored, bound on 127.0.0.1:8766, static
serving on (dev workflow tolerates an empty `backend/static/`).

Per follow-up 012: `make run-backend` defaults to `--reload`, eliminating
the class of bug where a new endpoint (e.g. follow-up 009's
`/api/import-from-downloads`) is added but the running Python process is
stale and the browser hits FastAPI's default 405 fallback.
"""
from __future__ import annotations

from pathlib import Path

from libs.env_loader import load_env_file

load_env_file(Path(__file__).resolve().parent.parent / ".env")

from libs.api import create_app
from libs.api_security import BoundOrigin
from libs.repo_root import RepoRoot

HOST: str = "127.0.0.1"
PORT: int = 8766

app = create_app(RepoRoot.find(), BoundOrigin(host=HOST, port=PORT), serve_static=True)
