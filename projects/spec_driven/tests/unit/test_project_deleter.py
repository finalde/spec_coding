"""Tests for project_deleter (parent-level project delete).

Covers: slug validation, task-type guard, dual-path delete, non-existent project
handling, Origin/Host gate, prod-mode static-mount-shadowing regression, and
the SelfDeleteRefused guard for the running webapp.

Note on the prod-mode test (test_delete_endpoint_reachable_with_static_mount):
this is the regression that closes the validation gap exposed by follow-up 011 —
when `serve_static=True` and a state-changing route is missing or shadowed,
the static-files mount returns 405 for non-GET methods, masking the bug. Every
new state-changing endpoint MUST have at least one prod-mode integration test.
"""
from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from apps.api.container import Container
from apps.api.routes import create_app
from libs.common.repo_root import RepoRoot
from libs.domain.project__error import (
    InvalidProjectName,
    ProjectNotFound,
    SelfDeleteRefused,
    UnsupportedTaskType,
)
from libs.infrastructure.origin_host__middleware import BoundOrigin
from libs.infrastructure.project_directory__writer import (
    ProjectDirectoryWriter as ProjectDeleter,
    _SLUG_RE,
)


# --- slug validation -------------------------------------------------------


@pytest.mark.parametrize(
    "good",
    ["wukong_juexing", "abc", "a", "abc_def", "a-b-c", "Abc123", "x_y-z_42"],
)
def test_slug_accepts_safe_names(good: str) -> None:
    assert _SLUG_RE.match(good) is not None


@pytest.mark.parametrize(
    "bad",
    [
        "",
        "..",
        "../escape",
        "a/b",
        "a\\b",
        ".hidden",
        "-leading",
        "name with space",
        "name.dot",
        "name%20",
        "C:foo",
        "name\x00",
    ],
)
def test_slug_rejects_unsafe_names(bad: str) -> None:
    assert _SLUG_RE.match(bad) is None


# --- ProjectDeleter --------------------------------------------------------


def test_unsupported_task_type_rejected(repo_root) -> None:
    """Anything outside {ai_video, development} is rejected."""
    deleter = ProjectDeleter(repo_root.path)
    with pytest.raises(UnsupportedTaskType):
        deleter.delete("garbage_type", "anything")


def test_invalid_project_name_rejected(repo_root) -> None:
    deleter = ProjectDeleter(repo_root.path)
    with pytest.raises(InvalidProjectName):
        deleter.delete("ai_video", "../escape")


def test_project_not_found_for_missing_name(repo_root) -> None:
    deleter = ProjectDeleter(repo_root.path)
    with pytest.raises(ProjectNotFound):
        deleter.delete("ai_video", "nonexistent_xyz_abc")


def test_self_delete_refused(repo_root) -> None:
    """The running webapp's own source must NOT be deletable via the UI."""
    deleter = ProjectDeleter(repo_root.path)
    with pytest.raises(SelfDeleteRefused):
        deleter.delete("development", "spec_driven")


def test_delete_synthetic_ai_video_project(tmp_path: Path) -> None:
    """ai_video: deletes specs/ai_video/{name}/ + ai_videos/{name}/."""
    spec_dir = tmp_path / "specs" / "ai_video" / "synthetic_test"
    output_dir = tmp_path / "ai_videos" / "synthetic_test"
    (spec_dir / "interview").mkdir(parents=True)
    (spec_dir / "interview" / "qa.md").write_text("test", encoding="utf-8")
    (output_dir / "characters").mkdir(parents=True)
    (output_dir / "characters" / "main.md").write_text("test", encoding="utf-8")

    deleter = ProjectDeleter(tmp_path)
    result = deleter.delete("ai_video", "synthetic_test")
    assert not spec_dir.exists()
    assert not output_dir.exists()
    assert "specs/ai_video/synthetic_test" in result.deleted_paths
    assert "ai_videos/synthetic_test" in result.deleted_paths
    assert result.not_found_paths == ()


def test_delete_synthetic_development_project(tmp_path: Path) -> None:
    """development: deletes specs/development/{name}/ + projects/{name}/."""
    spec_dir = tmp_path / "specs" / "development" / "synthetic_dev"
    output_dir = tmp_path / "projects" / "synthetic_dev"
    (spec_dir / "interview").mkdir(parents=True)
    (spec_dir / "interview" / "qa.md").write_text("test", encoding="utf-8")
    (output_dir / "backend").mkdir(parents=True)
    (output_dir / "backend" / "main.py").write_text("# placeholder", encoding="utf-8")

    deleter = ProjectDeleter(tmp_path)
    result = deleter.delete("development", "synthetic_dev")
    assert not spec_dir.exists()
    assert not output_dir.exists()
    assert "specs/development/synthetic_dev" in result.deleted_paths
    assert "projects/synthetic_dev" in result.deleted_paths


def test_delete_only_spec_dir_when_output_missing(tmp_path: Path) -> None:
    spec_dir = tmp_path / "specs" / "ai_video" / "spec_only"
    spec_dir.mkdir(parents=True)
    (spec_dir / "ok.md").write_text("x", encoding="utf-8")

    deleter = ProjectDeleter(tmp_path)
    result = deleter.delete("ai_video", "spec_only")
    assert "specs/ai_video/spec_only" in result.deleted_paths
    assert "ai_videos/spec_only" in result.not_found_paths


def test_delete_only_output_dir_when_spec_missing(tmp_path: Path) -> None:
    """development: only projects/{name}/ exists, no specs trail."""
    output_dir = tmp_path / "projects" / "code_only"
    output_dir.mkdir(parents=True)
    (output_dir / "README.md").write_text("x", encoding="utf-8")

    deleter = ProjectDeleter(tmp_path)
    result = deleter.delete("development", "code_only")
    assert "projects/code_only" in result.deleted_paths
    assert "specs/development/code_only" in result.not_found_paths


# --- HTTP integration (dev-mode: serve_static=False) -----------------------


def test_delete_endpoint_origin_host_403(client) -> None:
    """Foreign Origin must be rejected (GUARDED_ROUTES guard)."""
    r = client.request(
        "DELETE",
        "/api/project",
        json={"project_type": "ai_video", "project_name": "wukong_juexing"},
        headers={"Origin": "http://evil.example.com", "Host": "evil.example.com"},
    )
    assert r.status_code == 403


def test_delete_endpoint_self_delete_refused_400(client, good_headers) -> None:
    """development/spec_driven returns 400 with self_delete_refused."""
    r = client.request(
        "DELETE",
        "/api/project",
        json={"project_type": "development", "project_name": "spec_driven"},
        headers=good_headers,
    )
    assert r.status_code == 400
    assert r.json()["detail"]["kind"] == "self_delete_refused"


def test_delete_endpoint_unsupported_task_type_400(client, good_headers) -> None:
    r = client.request(
        "DELETE",
        "/api/project",
        json={"project_type": "garbage_type", "project_name": "x"},
        headers=good_headers,
    )
    assert r.status_code == 400
    assert r.json()["detail"]["kind"] == "unsupported_task_type"


def test_delete_endpoint_invalid_name_400(client, good_headers) -> None:
    r = client.request(
        "DELETE",
        "/api/project",
        json={"project_type": "ai_video", "project_name": "../escape"},
        headers=good_headers,
    )
    assert r.status_code == 400
    assert r.json()["detail"]["kind"] == "invalid_project_name"


def test_delete_endpoint_not_found_404(client, good_headers) -> None:
    r = client.request(
        "DELETE",
        "/api/project",
        json={"project_type": "ai_video", "project_name": "definitely_not_there_xyz"},
        headers=good_headers,
    )
    assert r.status_code == 404


# --- HTTP integration (PROD-MODE: serve_static=True) -----------------------
# Regression test for follow-up 011's class-of-failure: when serve_static=True
# the static-files mount at "/" catches DELETE for any path that doesn't match
# a route, returning 405. Tests with serve_static=False (the default fixture)
# would silently pass even if the route went missing.


@pytest.fixture()
def prod_client(repo_root, bound) -> TestClient:
    """A TestClient with serve_static=True — exercises the static-mount-shadowing path."""
    return TestClient(create_app(repo_root=repo_root, bound=bound, serve_static=True))


def test_delete_endpoint_reachable_with_static_mount(prod_client, good_headers) -> None:
    """The DELETE /api/project route MUST be matched by FastAPI, not shadowed by
    the static-files mount (which would 405 since StaticFiles only allows GET/HEAD)."""
    r = prod_client.request(
        "DELETE",
        "/api/project",
        json={"project_type": "ai_video", "project_name": "definitely_not_there_xyz_prod"},
        headers=good_headers,
    )
    # Must NOT be 405 (static mount shadow). Must be the handler's 404.
    assert r.status_code != 405, (
        f"DELETE /api/project returned 405 in prod mode — the static-files mount is "
        f"shadowing the route. body: {r.text[:300]}"
    )
    assert r.status_code == 404


def test_all_state_changing_endpoints_unshadowed_by_static(prod_client, good_headers) -> None:
    """Class-of-failure regression: every endpoint in GUARDED_ROUTES must be
    reachable when serve_static=True. If any returns 405, the static mount is
    shadowing it (route missing or wrongly registered after the mount)."""
    from libs.infrastructure.origin_host__middleware import GUARDED_ROUTES

    for method, path in GUARDED_ROUTES:
        # Send a deliberately-malformed body so we get fast 4xx instead of side effects.
        r = prod_client.request(
            method,
            path,
            json={},
            headers=good_headers,
        )
        assert r.status_code != 405, (
            f"{method} {path} returned 405 with serve_static=True — "
            f"the static-files mount is shadowing this guarded route."
        )
