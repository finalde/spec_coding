"""
Group 8 — API routes (negative-status surface) + critical Group 5 (api_security).

Spec anchors: FR-4, FR-7..9, NFR-6, NFR-7, AC-11, AC-12.

Group 5 sub-tests are the regression set for run `spec_driven-006` (proxy
rewrite contract). Per agent_refs/validation/development.md move 11, BOTH
shapes (pre-rewrite raw browser request, and post-rewrite Vite-proxied
request) are tested. Missing the pre-rewrite case is a blocker.
"""

from __future__ import annotations

from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Tree
# ---------------------------------------------------------------------------


def test_get_tree_returns_recursive_shape(client):
    r = client.get("/api/tree")
    assert r.status_code == 200
    body = r.json()
    assert body["type"] == "section"
    assert isinstance(body["children"], list)
    assert len(body["children"]) >= 2
    names = [c["name"] for c in body["children"]]
    assert "Claude Settings & Shared Context" in names
    assert "Specs" in names


# ---------------------------------------------------------------------------
# File reader (HTTP)
# ---------------------------------------------------------------------------


def test_get_file_happy_path_includes_security_headers(client):
    r = client.get("/api/file?path=CLAUDE.md")
    assert r.status_code == 200
    assert r.headers.get("x-content-type-options") == "nosniff"
    assert "attachment" in r.headers.get("content-disposition", "").lower()
    body = r.json()
    assert "# CLAUDE.md" in body["content"]
    assert body["bytes"] > 0


@pytest.mark.parametrize(
    "probe",
    [
        "../etc/passwd",
        "specs/../../etc/passwd",
        "/etc/passwd",
        "specs/development/spec_driven/CON.md",
        "specs/development/spec_driven/final_specs/spec.md::$DATA",
    ],
)
def test_traversal_returns_single_404(client, probe):
    r = client.get(f"/api/file?path={probe}")
    assert r.status_code == 404


def test_extension_disallowed_returns_415(client, scratch_dir: Path):
    f = scratch_dir / "blocked.exe"
    f.write_text("nope", encoding="utf-8")
    r = client.get(
        "/api/file?path=specs/development/spec_driven/__scratch__/blocked.exe"
    )
    assert r.status_code == 415


def test_size_cap_returns_413(client, scratch_dir: Path):
    f = scratch_dir / "huge_api.md"
    f.write_bytes(b"a" * (1024 * 1024 + 1))
    r = client.get(
        "/api/file?path=specs/development/spec_driven/__scratch__/huge_api.md"
    )
    assert r.status_code == 413


# ---------------------------------------------------------------------------
# Verb whitelist (NFR-6, AC-12)
# ---------------------------------------------------------------------------


def test_patch_on_file_returns_405(client):
    r = client.request("PATCH", "/api/file?path=CLAUDE.md")
    assert r.status_code == 405
    allow = r.headers.get("allow", "")
    if allow:
        assert "GET" in allow
        assert "PUT" in allow


def test_delete_on_file_returns_405(client):
    r = client.request("DELETE", "/api/file?path=CLAUDE.md")
    assert r.status_code == 405


def test_post_on_file_returns_405(client):
    r = client.post("/api/file", json={"path": "CLAUDE.md", "content": "x"})
    assert r.status_code == 405


# ---------------------------------------------------------------------------
# Origin / Host validation (FR-9, NFR-7) — Group 5 critical surface
# ---------------------------------------------------------------------------


def test_put_without_origin_returns_403(client):
    r = client.put(
        "/api/file",
        json={
            "path": "specs/development/spec_driven/__scratch__/origin_test.md",
            "content": "y",
        },
    )
    assert r.status_code == 403


def test_put_with_foreign_origin_returns_403(client):
    r = client.put(
        "/api/file",
        headers={"Origin": "http://evil.example.com", "Host": "127.0.0.1:8765"},
        json={
            "path": "specs/development/spec_driven/__scratch__/origin_test.md",
            "content": "y",
        },
    )
    assert r.status_code == 403


def test_put_with_bad_host_returns_403(client):
    r = client.put(
        "/api/file",
        headers={"Origin": "http://127.0.0.1:8765", "Host": "evil.com"},
        json={
            "path": "specs/development/spec_driven/__scratch__/origin_test.md",
            "content": "y",
        },
    )
    assert r.status_code == 403


def test_put_wrong_port_origin_returns_403(client):
    r = client.put(
        "/api/file",
        headers={"Origin": "http://127.0.0.1:9999", "Host": "127.0.0.1:8765"},
        json={
            "path": "specs/development/spec_driven/__scratch__/origin_test.md",
            "content": "y",
        },
    )
    assert r.status_code == 403


def test_put_ipv6_loopback_origin_returns_403(client):
    r = client.put(
        "/api/file",
        headers={"Origin": "http://[::1]:8765", "Host": "[::1]:8765"},
        json={
            "path": "specs/development/spec_driven/__scratch__/origin_test.md",
            "content": "y",
        },
    )
    assert r.status_code == 403


def test_put_with_legitimate_origin_succeeds(client, good_headers, scratch_dir: Path):
    rel = "specs/development/spec_driven/__scratch__/api_put_legit.md"
    r = client.put(
        "/api/file",
        headers=good_headers,
        json={"path": rel, "content": "hello"},
    )
    assert r.status_code == 200
    assert r.json()["bytes"] == 5
    g = client.get(f"/api/file?path={rel}")
    assert g.status_code == 200
    assert g.json()["content"] == "hello"


def test_put_with_localhost_origin_succeeds(client, localhost_headers, scratch_dir: Path):
    """AC-11 (iii) — `localhost` ↔ `127.0.0.1` are loopback aliases."""
    rel = "specs/development/spec_driven/__scratch__/api_put_localhost.md"
    r = client.put(
        "/api/file",
        headers=localhost_headers,
        json={"path": rel, "content": "loopback"},
    )
    assert r.status_code == 200


def test_put_with_127_origin_localhost_host_succeeds(client, scratch_dir: Path):
    """Cross-product 127.0.0.1 origin + localhost host is admitted."""
    rel = "specs/development/spec_driven/__scratch__/api_put_cross.md"
    r = client.put(
        "/api/file",
        headers={"Origin": "http://127.0.0.1:8765", "Host": "localhost:8765"},
        json={"path": rel, "content": "cross-product"},
    )
    assert r.status_code == 200


def test_put_with_dev_server_origin_pre_rewrite_returns_403(client, scratch_dir: Path):
    """[regression-spec_driven-006 / move 11] — raw browser-shape direct-to-backend.

    The Vite proxy MUST rewrite Origin to http://127.0.0.1:8765 before the
    request hits the backend. A request with `Origin: http://localhost:5173`
    direct-to-backend is the exact shape produced when the proxy rewrite hook
    is missing — it MUST be rejected with 403. Missing this test is a blocker.
    """
    rel = "specs/development/spec_driven/__scratch__/api_put_pre_rewrite.md"
    r = client.put(
        "/api/file",
        headers={"Origin": "http://localhost:5173", "Host": "127.0.0.1:8765"},
        json={"path": rel, "content": "pre-rewrite"},
    )
    assert r.status_code == 403


def test_put_with_dev_server_host_returns_403(client, scratch_dir: Path):
    """A `Host: localhost:5173` is also outside the bound-port allow-list."""
    rel = "specs/development/spec_driven/__scratch__/api_put_dev_host.md"
    r = client.put(
        "/api/file",
        headers={"Origin": "http://localhost:5173", "Host": "localhost:5173"},
        json={"path": rel, "content": "x"},
    )
    assert r.status_code == 403


def test_get_file_foreign_origin_still_succeeds(client):
    """GET endpoints are NOT origin-validated (FR-9 lists state-changing routes only)."""
    r = client.get("/api/file?path=CLAUDE.md", headers={"Origin": "http://evil.example.com"})
    assert r.status_code == 200


def test_get_tree_foreign_origin_still_succeeds(client):
    r = client.get("/api/tree", headers={"Origin": "http://evil.example.com"})
    assert r.status_code == 200


def test_get_stages_foreign_origin_still_succeeds(client):
    r = client.get(
        "/api/stages?project_type=development&project_name=spec_driven",
        headers={"Origin": "http://evil.example.com"},
    )
    assert r.status_code == 200


# ---------------------------------------------------------------------------
# Regen-prompt route surface (FR-10, FR-11)
# ---------------------------------------------------------------------------


def _regen_body(**overrides):
    body = dict(
        project_type="development",
        project_name="spec_driven",
        stages=["interview"],
        modules={},
        autonomous=False,
    )
    body.update(overrides)
    return body


def test_post_regen_prompt_with_localhost_origin_succeeds(client, localhost_headers):
    """Loopback alias on the bound port — same socket → admitted."""
    r = client.post(
        "/api/regen-prompt",
        headers=localhost_headers,
        json=_regen_body(),
    )
    assert r.status_code == 200


def test_post_regen_prompt_returns_documented_shape(client, good_headers):
    r = client.post(
        "/api/regen-prompt",
        headers=good_headers,
        json=_regen_body(),
    )
    assert r.status_code == 200
    body = r.json()
    assert set(body.keys()) == {
        "prompt",
        "warning",
        "selected_stages_count",
        "follow_ups_count",
        "autonomous",
        "bytes",
    }
    assert body["selected_stages_count"] == 1
    assert body["autonomous"] is False
    assert body["prompt"].startswith("# EXECUTION MODE: INTERACTIVE")
    assert body["bytes"] == len(body["prompt"].encode("utf-8"))


def test_post_regen_prompt_autonomous_header(client, good_headers):
    r = client.post(
        "/api/regen-prompt",
        headers=good_headers,
        json=_regen_body(autonomous=True),
    )
    assert r.status_code == 200
    body = r.json()
    assert body["prompt"].startswith("# EXECUTION MODE: AUTONOMOUS")
    assert body["autonomous"] is True


def test_post_regen_prompt_constraints_section(client, good_headers):
    r = client.post(
        "/api/regen-prompt",
        headers=good_headers,
        json=_regen_body(),
    )
    body = r.json()
    assert "### Constraints" in body["prompt"]
    # one of the load-bearing read-zero phrasings
    assert (
        "regeneration deletes prior outputs first" in body["prompt"]
        or "delete prior outputs" in body["prompt"]
        or "treated as deleted" in body["prompt"]
    )
    # audit-event protocol verbatim per FR-38
    assert "regen.delete.planned" in body["prompt"]
    assert "regen.delete.completed" in body["prompt"]
    assert "regen.write.completed" in body["prompt"]


def test_post_regen_prompt_foreign_origin_403(client):
    r = client.post(
        "/api/regen-prompt",
        headers={"Origin": "http://evil.com", "Host": "127.0.0.1:8765"},
        json=_regen_body(),
    )
    assert r.status_code == 403


def test_post_regen_prompt_dev_server_origin_pre_rewrite_403(client):
    """Same regression as the PUT version — POST regen also gated."""
    r = client.post(
        "/api/regen-prompt",
        headers={"Origin": "http://localhost:5173", "Host": "127.0.0.1:8765"},
        json=_regen_body(),
    )
    assert r.status_code == 403


def test_post_regen_prompt_validates_body_shape(client, good_headers):
    r = client.post(
        "/api/regen-prompt",
        headers=good_headers,
        json={"project_type": "development"},  # missing project_name + stages
    )
    assert r.status_code == 422


# ---------------------------------------------------------------------------
# Stages
# ---------------------------------------------------------------------------


def test_get_stages_returns_six(client):
    r = client.get("/api/stages?project_type=development&project_name=spec_driven")
    assert r.status_code == 200
    body = r.json()
    stages = body.get("stages", body) if isinstance(body, dict) else body
    assert len(stages) == 6
    ids = [s["id"] for s in stages]
    # The canonical six per FR-6
    expected_six = ["intake", "interview", "research", "spec", "validation", "execution"]
    # Allow either the canonical id list or a documented re-ordering
    assert sorted(ids) == sorted(expected_six)


def test_get_stages_each_has_modules(client):
    r = client.get("/api/stages?project_type=development&project_name=spec_driven")
    assert r.status_code == 200
    body = r.json()
    stages = body.get("stages", body) if isinstance(body, dict) else body
    for s in stages:
        assert "id" in s
        assert "label" in s
        assert "folder" in s
        assert "invocation" in s
        assert "modules" in s
        assert isinstance(s["modules"], list)


# ---------------------------------------------------------------------------
# Promotions
# ---------------------------------------------------------------------------


def test_promote_post_then_delete(client, good_headers):
    body = {
        "project_type": "development",
        "project_name": "spec_driven",
        "stage_folder": "validation",
        "source_file": "validation/strategy.md",
        "item_id": "test-promote-api-1",
        "item_text": "Test pin body for api roundtrip.",
    }
    r = client.post("/api/promote", headers=good_headers, json=body)
    assert r.status_code == 200
    r2 = client.request(
        "DELETE",
        "/api/promote",
        headers=good_headers,
        json={
            "project_type": "development",
            "project_name": "spec_driven",
            "stage_folder": "validation",
            "item_id": "test-promote-api-1",
        },
    )
    assert r2.status_code == 200


def test_promote_stage_folder_allowlist(client, good_headers):
    """user_input is not in the allowlist → 422 (FastAPI default for enum)."""
    r = client.post(
        "/api/promote",
        headers=good_headers,
        json={
            "project_type": "development",
            "project_name": "spec_driven",
            "stage_folder": "user_input",
            "source_file": "raw_prompt.md",
            "item_id": "x",
            "item_text": "y",
        },
    )
    assert r.status_code in (400, 422)


def test_promote_post_foreign_origin_403(client):
    r = client.post(
        "/api/promote",
        headers={"Origin": "http://evil.com", "Host": "127.0.0.1:8765"},
        json={
            "project_type": "development",
            "project_name": "spec_driven",
            "stage_folder": "validation",
            "source_file": "validation/strategy.md",
            "item_id": "anything",
            "item_text": "anything",
        },
    )
    assert r.status_code == 403


def test_promote_delete_foreign_origin_403(client):
    r = client.request(
        "DELETE",
        "/api/promote",
        headers={"Origin": "http://evil.com", "Host": "127.0.0.1:8765"},
        json={
            "project_type": "development",
            "project_name": "spec_driven",
            "stage_folder": "validation",
            "item_id": "x",
        },
    )
    assert r.status_code == 403


# ---------------------------------------------------------------------------
# Unknown route
# ---------------------------------------------------------------------------


def test_unknown_route_returns_404(client):
    r = client.get("/api/this-does-not-exist")
    assert r.status_code == 404


def test_unknown_post_route_returns_404_or_405(client):
    r = client.post("/api/foo", json={})
    assert r.status_code in (404, 405)
