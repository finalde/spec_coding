from __future__ import annotations

import argparse

import uvicorn

from libs.api import create_app
from libs.api_security import BoundOrigin
from libs.repo_root import RepoRoot

HOST: str = "127.0.0.1"
PORT: int = 8765


def main() -> None:
    parser = argparse.ArgumentParser(description="spec_driven backend (localhost-only)")
    parser.add_argument("--no-static", action="store_true", help="serve only the JSON API")
    args = parser.parse_args()
    repo_root = RepoRoot.find()
    bound = BoundOrigin(host=HOST, port=PORT)
    app = create_app(repo_root, bound, serve_static=not args.no_static)
    uvicorn.run(app, host=HOST, port=PORT, log_level="info")


if __name__ == "__main__":
    main()
