"""ASGI app factory for uvicorn reload-mode.

`main.py` passes the import-string `"apps.api.asgi:app"` to `uvicorn.run`
when reload is enabled (uvicorn's `reload=True` requires an import-string,
not an app instance).
"""
from __future__ import annotations

from pathlib import Path

from libs.common.env_loader import load_env_file

load_env_file(Path(__file__).resolve().parent / ".env")

from apps.api.container import Container
from apps.api.app_factory import create_app
from apps.api.uvicorn_force_exit import install as _install_force_exit_watchdog
from libs.common.repo_root import RepoRoot
from libs.common.origin import BoundOrigin

_install_force_exit_watchdog()

HOST: str = "127.0.0.1"
PORT: int = 8766


def _build_app():
    container = Container()
    container.repo_root_path.override(RepoRoot.find().path)
    container.bound_origin.override(BoundOrigin(host=HOST, port=PORT))
    container.wire(packages=["apps.api.routes"])
    return create_app(container, serve_static=True)


app = _build_app()
