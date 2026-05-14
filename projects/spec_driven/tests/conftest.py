from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import Iterator

import pytest

SOLUTION_DIR = Path(__file__).resolve().parent.parent
if str(SOLUTION_DIR) not in sys.path:
    sys.path.insert(0, str(SOLUTION_DIR))

from apps.api.container import Container  # noqa: E402
from apps.api.routes import create_app  # noqa: E402
from libs.common.repo_root import RepoRoot  # noqa: E402
from libs.common.safe_resolve import SafeResolver  # noqa: E402
from libs.infrastructure.origin_host__middleware import BoundOrigin  # noqa: E402


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
def container(repo_root: RepoRoot, bound: BoundOrigin) -> Container:
    c = Container()
    c.repo_root_path.override(repo_root.path)
    c.bound_origin.override(bound)
    c.wire(modules=["apps.api.routes"])
    return c


@pytest.fixture()
def app(container: Container):
    return create_app(container, serve_static=False)


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
