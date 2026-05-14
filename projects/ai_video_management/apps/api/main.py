from __future__ import annotations

import argparse
from pathlib import Path

import uvicorn

from libs.common.env_loader import load_env_file

load_env_file(Path(__file__).resolve().parent / ".env")

from apps.api.container import Container
from apps.api.routes import create_app
from apps.api.uvicorn_force_exit import install as _install_force_exit_watchdog
from libs.common.repo_root import RepoRoot
from libs.infrastructure.origin_host__middleware import BoundOrigin

HOST: str = "127.0.0.1"
PORT: int = 8766


def _build_container(serve_static: bool) -> Container:
    container = Container()
    container.repo_root_path.override(RepoRoot.find().path)
    container.bound_origin.override(BoundOrigin(host=HOST, port=PORT))
    container.wire(modules=["apps.api.routes"])
    return container


def main() -> None:
    parser = argparse.ArgumentParser(description="ai_video_management backend (localhost-only)")
    parser.add_argument("--no-static", action="store_true", help="serve only the JSON API")
    parser.add_argument(
        "--no-reload",
        action="store_true",
        help="disable uvicorn auto-reload (default: reload on libs/ changes for dev workflow)",
    )
    args = parser.parse_args()
    _install_force_exit_watchdog()
    if args.no_reload:
        container = _build_container(serve_static=not args.no_static)
        app = create_app(container, serve_static=not args.no_static)
        uvicorn.run(app, host=HOST, port=PORT, log_level="info", timeout_graceful_shutdown=2)
    else:
        uvicorn.run(
            "apps.api.asgi:app",
            host=HOST,
            port=PORT,
            log_level="info",
            reload=True,
            reload_dirs=["libs", "apps"],
            timeout_graceful_shutdown=2,
        )


if __name__ == "__main__":
    main()
