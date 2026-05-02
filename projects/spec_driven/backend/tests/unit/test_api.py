from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from libs.api import build_app


def test_get_tree(fake_repo: Path) -> None:
    client = TestClient(build_app(fake_repo))
    resp = client.get("/api/tree")
    assert resp.status_code == 200
    body = resp.json()
    assert "settings" in body and "projects" in body


def test_get_file_md(fake_repo: Path) -> None:
    client = TestClient(build_app(fake_repo))
    resp = client.get("/api/file", params={"path": "CLAUDE.md"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["path"] == "CLAUDE.md"
    assert body["extension"] == ".md"
    assert "fake" in body["text"]


def test_get_file_traversal(fake_repo: Path) -> None:
    client = TestClient(build_app(fake_repo))
    resp = client.get("/api/file", params={"path": "../../../etc/hosts"})
    assert resp.status_code == 400
    assert resp.json()["error"] == "outside_sandbox"


def test_no_post_endpoint(fake_repo: Path) -> None:
    client = TestClient(build_app(fake_repo))
    assert client.post("/api/file", json={"path": "CLAUDE.md"}).status_code == 405
    assert client.put("/api/tree").status_code == 405
    assert client.delete("/api/file", params={"path": "x"}).status_code == 405


def test_get_file_outside_exposed_tree(fake_repo: Path) -> None:
    (fake_repo / "pyproject.toml").write_text("[project]", encoding="utf-8")
    client = TestClient(build_app(fake_repo))
    resp = client.get("/api/file", params={"path": "pyproject.toml"})
    assert resp.status_code == 404
    body = resp.json()
    assert body["error"] == "not_found"
    assert body["kind"] == "outside_exposed_tree"
