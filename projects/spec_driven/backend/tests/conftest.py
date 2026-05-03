from __future__ import annotations

import sys
from pathlib import Path

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
def client(repo_root: RepoRoot, bound: BoundOrigin):
    from fastapi.testclient import TestClient

    app = create_app(repo_root=repo_root, bound=bound, serve_static=False)
    return TestClient(app)


@pytest.fixture()
def scratch_dir(repo_root: RepoRoot) -> Path:
    p = repo_root.path / "specs" / "development" / "spec_driven" / "__scratch__"
    p.mkdir(parents=True, exist_ok=True)
    yield p


@pytest.fixture()
def good_headers() -> dict[str, str]:
    return {"Origin": "http://127.0.0.1:8765", "Host": "127.0.0.1:8765"}
