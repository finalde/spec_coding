"""Boot-smoke: process starts cleanly, GET /api/tree returns expected shape.
Failure here is `critical` — halts the whole pipeline.
"""
from __future__ import annotations

from fastapi.testclient import TestClient

from libs.api import create_app
from libs.api_security import BoundOrigin
from libs.repo_root import RepoRoot
from tests.conftest import repo_root


def test_boot_creates_app_without_error() -> None:
    rr = RepoRoot(path=repo_root())
    bound = BoundOrigin(host="127.0.0.1", port=8766)
    app = create_app(rr, bound, serve_static=False)
    assert app is not None
    assert app.title == "ai_video_management"


def test_get_tree_returns_expected_sections() -> None:
    """FR-18 / FR-43 (post follow-up 003): AI Videos + Research live, in order."""
    rr = RepoRoot(path=repo_root())
    bound = BoundOrigin(host="127.0.0.1", port=8766)
    client = TestClient(create_app(rr, bound, serve_static=False))
    r = client.get("/api/tree")
    assert r.status_code == 200
    payload = r.json()
    assert payload["type"] == "section"
    sections = payload["children"]
    assert [s["name"] for s in sections] == ["AI Videos", "Research"], sections


def test_stages_endpoint_dropped() -> None:
    """No /api/stages endpoint exists."""
    rr = RepoRoot(path=repo_root())
    bound = BoundOrigin(host="127.0.0.1", port=8766)
    client = TestClient(create_app(rr, bound, serve_static=False))
    r = client.get("/api/stages")
    assert r.status_code == 404


def test_regen_prompt_endpoint_dropped() -> None:
    rr = RepoRoot(path=repo_root())
    bound = BoundOrigin(host="127.0.0.1", port=8766)
    client = TestClient(create_app(rr, bound, serve_static=False))
    r = client.post(
        "/api/regen-prompt",
        json={"project_type": "ai_video", "project_name": "wukong_juexing"},
        headers={"Origin": "http://127.0.0.1:8766", "Host": "127.0.0.1:8766"},
    )
    assert r.status_code == 404


def test_promote_endpoint_dropped() -> None:
    rr = RepoRoot(path=repo_root())
    bound = BoundOrigin(host="127.0.0.1", port=8766)
    client = TestClient(create_app(rr, bound, serve_static=False))
    r = client.post(
        "/api/promote",
        json={"project_name": "wukong_juexing", "stage_folder": "interview", "source_file": "qa.md", "item_id": "x", "item_text": "y"},
        headers={"Origin": "http://127.0.0.1:8766", "Host": "127.0.0.1:8766"},
    )
    assert r.status_code == 404


def test_csp_header_on_responses() -> None:
    rr = RepoRoot(path=repo_root())
    bound = BoundOrigin(host="127.0.0.1", port=8766)
    client = TestClient(create_app(rr, bound, serve_static=False))
    r = client.get("/api/tree")
    assert "content-security-policy" in {k.lower() for k in r.headers.keys()}
    csp = r.headers.get("content-security-policy", "")
    assert "default-src 'self'" in csp
    assert "img-src 'self'" in csp


def test_all_post_endpoints_registered() -> None:
    """Follow-up 012: catch stale-route regressions early.

    If a state-changing endpoint disappears (rename / typo / accidental
    removal), the failure mode is FastAPI returning a default 405 to the
    browser — confusing for users. Boot-smoke asserts every documented
    POST route is present so this regression trips CI rather than UX.
    """
    rr = RepoRoot(path=repo_root())
    bound = BoundOrigin(host="127.0.0.1", port=8766)
    app = create_app(rr, bound, serve_static=False)
    registered: set[tuple[str, str]] = set()
    for route in app.routes:
        methods = getattr(route, "methods", None)
        path = getattr(route, "path", None)
        if methods and path:
            for m in methods:
                registered.add((m, path))
    expected = {
        ("POST", "/api/rename-media"),
        ("POST", "/api/archive-media"),
        ("POST", "/api/unarchive-media"),
        ("POST", "/api/import-from-downloads"),
        ("POST", "/api/actors/generate"),
        ("GET", "/api/actors"),
        ("POST", "/api/casting/assign"),
        ("DELETE", "/api/casting/assign"),
        ("GET", "/api/casting"),
    }
    missing = expected - registered
    assert not missing, f"endpoints missing from app.routes: {sorted(missing)}"
