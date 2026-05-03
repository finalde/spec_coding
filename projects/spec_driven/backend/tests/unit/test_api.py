"""
Group 7 — api (FR-9, NFR-6, NFR-7, AC-11, AC-12, plus 413/415/404 error mapping).
"""

from __future__ import annotations

import pytest


def test_get_tree_returns_recursive_shape(client):
    r = client.get("/api/tree")
    assert r.status_code == 200
    body = r.json()
    assert body["type"] == "section"
    assert isinstance(body["children"], list)
    assert len(body["children"]) >= 2
    names = [c["name"] for c in body["children"]]
    assert "Claude Settings & Shared Context" in names
    assert "Projects" in names


def test_get_file_happy_path_includes_security_headers(client):
    r = client.get("/api/file?path=CLAUDE.md")
    assert r.status_code == 200
    assert r.headers["x-content-type-options"] == "nosniff"
    assert "attachment" in r.headers["content-disposition"]
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


def test_extension_disallowed_returns_415(client, scratch_dir):
    f = scratch_dir / "blocked.exe"
    f.write_text("nope", encoding="utf-8")
    try:
        r = client.get("/api/file?path=specs/development/spec_driven/__scratch__/blocked.exe")
        assert r.status_code == 415
    finally:
        f.unlink()


def test_size_cap_returns_413(client, scratch_dir):
    f = scratch_dir / "huge.md"
    f.write_bytes(b"a" * (1024 * 1024 + 1))
    try:
        r = client.get("/api/file?path=specs/development/spec_driven/__scratch__/huge.md")
        assert r.status_code == 413
    finally:
        f.unlink()


def test_patch_on_file_returns_405(client):
    r = client.request("PATCH", "/api/file")
    assert r.status_code == 405
    assert "GET" in r.headers.get("allow", "")
    assert "PUT" in r.headers.get("allow", "")


def test_delete_on_file_returns_405(client):
    r = client.request("DELETE", "/api/file?path=foo.md")
    assert r.status_code == 405


def test_put_without_origin_returns_403(client):
    r = client.put("/api/file", json={"path": "specs/development/spec_driven/__scratch__/x.md", "content": "y"})
    assert r.status_code == 403


def test_put_with_foreign_origin_returns_403(client):
    r = client.put(
        "/api/file",
        headers={"Origin": "http://evil.example.com", "Host": "127.0.0.1:8765"},
        json={"path": "specs/development/spec_driven/__scratch__/x.md", "content": "y"},
    )
    assert r.status_code == 403


def test_put_with_bad_host_returns_403(client):
    r = client.put(
        "/api/file",
        headers={"Origin": "http://127.0.0.1:8765", "Host": "evil.com"},
        json={"path": "specs/development/spec_driven/__scratch__/x.md", "content": "y"},
    )
    assert r.status_code == 403


def test_put_with_legitimate_origin_succeeds(client, good_headers, scratch_dir):
    rel = "specs/development/spec_driven/__scratch__/api_put.md"
    r = client.put("/api/file", headers=good_headers, json={"path": rel, "content": "hello"})
    assert r.status_code == 200
    body = r.json()
    assert body["bytes"] == 5
    g = client.get(f"/api/file?path={rel}")
    assert g.status_code == 200
    assert g.json()["content"] == "hello"
    (scratch_dir / "api_put.md").unlink(missing_ok=True)


def test_put_with_localhost_origin_succeeds(client, scratch_dir):
    """FR-9 follow-up 004: `localhost` is admitted as a loopback alias of `127.0.0.1`."""
    rel = "specs/development/spec_driven/__scratch__/api_put_localhost.md"
    r = client.put(
        "/api/file",
        headers={"Origin": "http://localhost:8765", "Host": "localhost:8765"},
        json={"path": rel, "content": "hello-localhost"},
    )
    assert r.status_code == 200
    (scratch_dir / "api_put_localhost.md").unlink(missing_ok=True)


def test_post_regen_prompt_with_localhost_origin_succeeds(client):
    """Regression for the bug the user hit clicking Build prompt at http://localhost:8765/."""
    r = client.post(
        "/api/regen-prompt",
        headers={"Origin": "http://localhost:8765", "Host": "localhost:8765"},
        json={
            "project_type": "development",
            "project_name": "spec_driven",
            "stages": ["interview"],
            "modules": {},
            "autonomous": False,
        },
    )
    assert r.status_code == 200


def test_get_file_foreign_origin_still_succeeds(client):
    """GET endpoints are NOT origin-validated (FR-9 lists state-changing routes only)."""
    r = client.get("/api/file?path=CLAUDE.md", headers={"Origin": "http://evil.example.com"})
    assert r.status_code == 200


def test_post_regen_prompt_returns_documented_shape(client, good_headers):
    r = client.post(
        "/api/regen-prompt",
        headers=good_headers,
        json={
            "project_type": "development",
            "project_name": "spec_driven",
            "stages": ["interview"],
            "modules": {},
            "autonomous": False,
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert set(body.keys()) == {"prompt", "warning", "selected_stages_count", "follow_ups_count", "autonomous", "bytes"}
    assert body["selected_stages_count"] == 1
    assert body["autonomous"] is False
    assert body["prompt"].startswith("# EXECUTION MODE: INTERACTIVE")
    assert body["bytes"] == len(body["prompt"].encode("utf-8"))


def test_post_regen_prompt_autonomous_header(client, good_headers):
    r = client.post(
        "/api/regen-prompt",
        headers=good_headers,
        json={
            "project_type": "development",
            "project_name": "spec_driven",
            "stages": ["interview"],
            "modules": {},
            "autonomous": True,
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["prompt"].startswith("# EXECUTION MODE: AUTONOMOUS")
    assert "Do not call AskUserQuestion" in body["prompt"]


def test_post_regen_prompt_constraints_section(client, good_headers):
    r = client.post(
        "/api/regen-prompt",
        headers=good_headers,
        json={
            "project_type": "development",
            "project_name": "spec_driven",
            "stages": ["interview"],
            "modules": {},
            "autonomous": False,
        },
    )
    body = r.json()
    assert "### Constraints" in body["prompt"]
    assert "regeneration deletes prior outputs first; new generation reads only the inputs." in body["prompt"]


def test_post_regen_prompt_foreign_origin_403(client):
    r = client.post(
        "/api/regen-prompt",
        headers={"Origin": "http://evil.com", "Host": "127.0.0.1:8765"},
        json={
            "project_type": "development",
            "project_name": "spec_driven",
            "stages": ["interview"],
            "modules": {},
            "autonomous": False,
        },
    )
    assert r.status_code == 403


def test_get_stages_returns_six(client):
    r = client.get("/api/stages?project_type=development&project_name=spec_driven")
    assert r.status_code == 200
    body = r.json()
    assert len(body["stages"]) == 6
    ids = [s["id"] for s in body["stages"]]
    assert ids == ["intake", "interview", "research", "spec", "validation", "execution"]


def test_promote_post_then_delete(client, good_headers):
    r = client.post(
        "/api/promote",
        headers=good_headers,
        json={
            "project_type": "development",
            "project_name": "spec_driven",
            "stage_folder": "validation",
            "source_file": "validation/strategy.md",
            "item_id": "test-promote-1",
            "item_text": "Test pin body.",
        },
    )
    assert r.status_code == 200
    r2 = client.request(
        "DELETE",
        "/api/promote",
        headers=good_headers,
        json={
            "project_type": "development",
            "project_name": "spec_driven",
            "stage_folder": "validation",
            "item_id": "test-promote-1",
        },
    )
    assert r2.status_code == 200


def test_promote_stage_folder_allowlist(client, good_headers):
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
    assert r.status_code == 422
