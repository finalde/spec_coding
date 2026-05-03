from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import Iterator

import pytest

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from libs.api import create_app  # noqa: E402
from libs.api_security import BoundOrigin  # noqa: E402
from libs.repo_root import RepoRoot  # noqa: E402
from libs.safe_resolve import SafeResolver  # noqa: E402


@pytest.fixture(scope="session")
def repo_root() -> RepoRoot:
    return RepoRoot.find()


@pytest.fixture(scope="session")
def resolver(repo_root: RepoRoot) -> SafeResolver:
    return SafeResolver(root=repo_root.path)


@pytest.fixture(scope="session")
def bound() -> BoundOrigin:
    return BoundOrigin(host="127.0.0.1", port=8765)


@pytest.fixture()
def app(repo_root: RepoRoot, bound: BoundOrigin):
    return create_app(repo_root=repo_root, bound=bound, serve_static=False)


@pytest.fixture()
def client(app):
    from fastapi.testclient import TestClient

    return TestClient(app)


@pytest.fixture()
def good_headers() -> dict[str, str]:
    return {"Origin": "http://127.0.0.1:8765", "Host": "127.0.0.1:8765"}


@pytest.fixture()
def localhost_headers() -> dict[str, str]:
    return {"Origin": "http://localhost:8765", "Host": "localhost:8765"}


@pytest.fixture()
def scratch_dir(repo_root: RepoRoot) -> Iterator[Path]:
    p = repo_root.path / "specs" / "development" / "spec_driven" / "__scratch__"
    p.mkdir(parents=True, exist_ok=True)
    yield p
    # Best-effort cleanup of leftover files inside scratch (don't remove dir
    # itself — other parallel tests may share it within a session run).
    for child in list(p.iterdir()):
        try:
            if child.is_dir():
                shutil.rmtree(child, ignore_errors=True)
            else:
                child.unlink(missing_ok=True)
        except OSError:
            pass


@pytest.fixture()
def scratch_rel(scratch_dir: Path) -> str:
    return "specs/development/spec_driven/__scratch__"
