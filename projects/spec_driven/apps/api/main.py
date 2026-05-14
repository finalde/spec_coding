from __future__ import annotations

import argparse

import uvicorn

from apps.api.container import Container
from apps.api.routes import create_app
from libs.common.repo_root import RepoRoot
from libs.infrastructure.origin_host__middleware import BoundOrigin

HOST: str = "127.0.0.1"
PORT: int = 8765


def main() -> None:
    parser = argparse.ArgumentParser(description="spec_driven backend (localhost-only)")
    parser.add_argument("--no-static", action="store_true", help="serve only the JSON API")
    args = parser.parse_args()

    repo_root = RepoRoot.find()
    bound = BoundOrigin(host=HOST, port=PORT)

    container = Container()
    container.repo_root_path.override(repo_root.path)
    container.bound_origin.override(bound)
    container.wire(modules=["apps.api.routes"])

    app = create_app(container, serve_static=not args.no_static)
    uvicorn.run(app, host=HOST, port=PORT, log_level="info")


if __name__ == "__main__":
    main()
