from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from libs.api import build_app


@pytest.fixture
def client(fake_repo: Path) -> TestClient:
    app = build_app(fake_repo)
    return TestClient(app)


def test_get_tree_shape(client: TestClient) -> None:
    resp = client.get("/api/tree")
    assert resp.status_code == 200
    body = resp.json()
    assert list(body.keys()) == ["settings", "projects"]


def test_get_file_happy_path(client: TestClient) -> None:
    resp = client.get(
        "/api/file",
        params={"path": "specs/development/spec_driven/final_specs/spec.md"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "spec content" in body["text"]


def test_get_file_traversal_returns_400(client: TestClient) -> None:
    resp = client.get("/api/file", params={"path": "../../etc/hosts"})
    assert resp.status_code == 400
    body = resp.json()
    assert body["detail"]["kind"] == "outside_sandbox"


def test_get_file_outside_exposed_tree_returns_404(
    client: TestClient, fake_repo: Path
) -> None:
    (fake_repo / "pyproject.toml").write_text("[project]\n", encoding="utf-8")
    resp = client.get("/api/file", params={"path": "pyproject.toml"})
    assert resp.status_code == 404
    assert resp.json()["detail"]["kind"] == "outside_exposed_tree"


def test_put_file_round_trip(client: TestClient) -> None:
    rel = "specs/development/spec_driven/final_specs/spec.md"
    resp = client.put("/api/file", json={"path": rel, "text": "# new content\n"})
    assert resp.status_code == 200
    again = client.get("/api/file", params={"path": rel})
    assert "new content" in again.json()["text"]


def test_patch_and_delete_return_405(client: TestClient) -> None:
    rel = "specs/development/spec_driven/final_specs/spec.md"
    p = client.patch("/api/file", params={"path": rel})
    assert p.status_code == 405
    d = client.delete("/api/file", params={"path": rel})
    assert d.status_code == 405
