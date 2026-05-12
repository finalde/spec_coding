from __future__ import annotations

import argparse

import uvicorn

from libs.api import create_app
from libs.api_security import BoundOrigin
from libs.repo_root import RepoRoot

HOST: str = "127.0.0.1"
PORT: int = 8766


def main() -> None:
    parser = argparse.ArgumentParser(description="ai_video_management backend (localhost-only)")
    parser.add_argument("--no-static", action="store_true", help="serve only the JSON API")
    parser.add_argument(
        "--no-reload",
        action="store_true",
        help="disable uvicorn auto-reload (default: reload on libs/ changes for dev workflow)",
    )
    args = parser.parse_args()
    if args.no_reload:
        repo_root = RepoRoot.find()
        bound = BoundOrigin(host=HOST, port=PORT)
        app = create_app(repo_root, bound, serve_static=not args.no_static)
        uvicorn.run(app, host=HOST, port=PORT, log_level="info")
    else:
        uvicorn.run(
            "libs.asgi:app",
            host=HOST,
            port=PORT,
            log_level="info",
            reload=True,
            reload_dirs=["libs"],
        )


if __name__ == "__main__":
    main()
