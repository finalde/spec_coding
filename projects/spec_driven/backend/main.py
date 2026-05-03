"""
spec_driven backend entrypoint (FR-38, AC-29).

Binds 127.0.0.1:8765 only (loopback). Run with:

    python main.py
"""

from __future__ import annotations

import sys

import uvicorn

from libs.api import create_app
from libs.api_security import BoundOrigin
from libs.repo_root import RepoRoot

HOST = "127.0.0.1"
PORT = 8765


def main() -> int:
    repo_root = RepoRoot.find()
    bound = BoundOrigin(host=HOST, port=PORT)
    app = create_app(repo_root=repo_root, bound=bound, serve_static=True)
    uvicorn.run(app, host=HOST, port=PORT, log_level="info")
    return 0


if __name__ == "__main__":
    sys.exit(main())
