from __future__ import annotations

import os
import sys
from pathlib import Path

import uvicorn

sys.path.insert(0, str(Path(__file__).resolve().parent))

from libs.api import build_app
from libs.repo_root import RepoRootNotFound, discover_repo_root


def main() -> int:
    try:
        repo_root = discover_repo_root(Path(__file__).resolve())
    except RepoRootNotFound as err:
        print(f"spec_driven: {err}", file=sys.stderr)
        return 2
    port = int(os.environ.get("SPEC_DRIVEN_PORT", "8765"))
    app = build_app(repo_root)
    uvicorn.run(app, host="127.0.0.1", port=port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
