"""
Group 3 — file_writer (atomic write, body validation, stale-write 409).

Spec anchors: FR-7, FR-7b, FR-8, NFR-6, AC-7, AC-10, AC-13..15.

All tests go through the HTTP surface (PUT /api/file). The route layer wraps
the lib's domain errors into 415/413/409 status codes per spec.
"""

from __future__ import annotations

import os
import time
from email.utils import formatdate
from pathlib import Path

import pytest


@pytest.fixture()
def existing_md(scratch_dir: Path) -> Path:
    f = scratch_dir / "existing.md"
    f.write_text("seed", encoding="utf-8")
    return f


def test_put_happy_path_returns_bytes_and_mtime(client, good_headers, scratch_dir: Path):
    rel = "specs/development/spec_driven/__scratch__/put_happy.md"
    r = client.put(
        "/api/file",
        headers=good_headers,
        json={"path": rel, "content": "hello world"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["bytes"] == len("hello world".encode("utf-8"))
    assert "mtime" in body


def test_put_round_trip_content_matches(client, good_headers, scratch_dir: Path):
    rel = "specs/development/spec_driven/__scratch__/round_trip.md"
    payload = "round-trip body"
    p = client.put(
        "/api/file",
        headers=good_headers,
        json={"path": rel, "content": payload},
    )
    assert p.status_code == 200
    g = client.get(f"/api/file?path={rel}")
    assert g.status_code == 200
    assert g.json()["content"] == payload


@pytest.mark.parametrize(
    "ext",
    [".png", ".jpg", ".svg", ".exe", ".bat", ".sh", ".dll", ".html", ".php"],
)
def test_put_disallowed_extension_returns_415(client, good_headers, ext):
    rel = f"specs/development/spec_driven/__scratch__/foo{ext}"
    r = client.put(
        "/api/file",
        headers=good_headers,
        json={"path": rel, "content": "x"},
    )
    assert r.status_code == 415


def test_put_oversize_body_returns_413(client, good_headers):
    rel = "specs/development/spec_driven/__scratch__/oversize.md"
    big = "a" * (1024 * 1024 + 1)
    r = client.put(
        "/api/file",
        headers=good_headers,
        json={"path": rel, "content": big},
    )
    assert r.status_code == 413


def test_put_body_with_nul_byte_returns_415(client, good_headers):
    rel = "specs/development/spec_driven/__scratch__/binary.md"
    r = client.put(
        "/api/file",
        headers=good_headers,
        json={"path": rel, "content": "ab\x00cd"},
    )
    assert r.status_code == 415


def test_put_outside_tree_returns_404(client, good_headers):
    r = client.put(
        "/api/file",
        headers=good_headers,
        json={"path": "../etc/hosts", "content": "x"},
    )
    assert r.status_code == 404


def test_put_traversal_returns_404(client, good_headers):
    r = client.put(
        "/api/file",
        headers=good_headers,
        json={"path": "specs/../../../etc/passwd", "content": "x"},
    )
    assert r.status_code == 404


def test_put_stale_write_returns_409(client, good_headers, scratch_dir: Path):
    """FR-7b — If-Unmodified-Since stale → 409 with current_mtime."""
    rel_path = scratch_dir / "stale_write.md"
    rel_path.write_text("v1", encoding="utf-8")
    rel = "specs/development/spec_driven/__scratch__/stale_write.md"

    # Get current mtime, then bump disk mtime forward so the on-disk mtime is
    # strictly newer than the If-Unmodified-Since the client claims.
    current = rel_path.stat().st_mtime
    new_mtime = current + 60.0
    os.utime(rel_path, (new_mtime, new_mtime))

    stale_iums = formatdate(timeval=current - 1, usegmt=True)
    headers = dict(good_headers)
    headers["If-Unmodified-Since"] = stale_iums
    r = client.put(
        "/api/file",
        headers=headers,
        json={"path": rel, "content": "user-edit"},
    )
    assert r.status_code == 409
    body = r.json()
    detail = body.get("detail")
    # detail is a dict per spec: {kind, current_mtime}
    if isinstance(detail, dict):
        assert detail.get("kind") == "stale_write"
        assert "current_mtime" in detail


def test_put_with_matching_iums_succeeds(client, good_headers, scratch_dir: Path):
    rel_path = scratch_dir / "matching_iums.md"
    rel_path.write_text("v1", encoding="utf-8")
    rel = "specs/development/spec_driven/__scratch__/matching_iums.md"
    current = rel_path.stat().st_mtime
    iums = formatdate(timeval=current + 1, usegmt=True)
    headers = dict(good_headers)
    headers["If-Unmodified-Since"] = iums
    r = client.put(
        "/api/file",
        headers=headers,
        json={"path": rel, "content": "fresh"},
    )
    assert r.status_code == 200


def test_put_without_iums_proceeds(client, good_headers, scratch_dir: Path):
    """If-Unmodified-Since is optional — when absent, write proceeds."""
    rel = "specs/development/spec_driven/__scratch__/no_iums.md"
    r = client.put(
        "/api/file",
        headers=good_headers,
        json={"path": rel, "content": "no-header"},
    )
    assert r.status_code == 200


def test_put_empty_body_is_allowed(client, good_headers):
    rel = "specs/development/spec_driven/__scratch__/empty_body.md"
    r = client.put(
        "/api/file",
        headers=good_headers,
        json={"path": rel, "content": ""},
    )
    assert r.status_code == 200
    assert r.json()["bytes"] == 0


def test_put_unicode_body_round_trip(client, good_headers, scratch_dir: Path):
    rel = "specs/development/spec_driven/__scratch__/unicode.md"
    payload = "Привет 🚀 漢字"
    r = client.put(
        "/api/file",
        headers=good_headers,
        json={"path": rel, "content": payload},
    )
    assert r.status_code == 200
    assert r.json()["bytes"] == len(payload.encode("utf-8"))
    g = client.get(f"/api/file?path={rel}")
    assert g.json()["content"] == payload


def test_put_overwrites_existing_file(client, good_headers, existing_md: Path):
    rel = "specs/development/spec_driven/__scratch__/existing.md"
    r = client.put(
        "/api/file",
        headers=good_headers,
        json={"path": rel, "content": "overwritten"},
    )
    assert r.status_code == 200
    assert existing_md.read_text(encoding="utf-8") == "overwritten"
