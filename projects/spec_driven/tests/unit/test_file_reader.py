"""
Group 2 — file_reader (extension allowlist, size cap, security headers).

Spec anchors: FR-4, FR-5, NFR-9, NFR-11. Tested via the HTTP surface so the
contract is enforced end-to-end (the route layer attaches the security
headers; we assert what reaches the client).
"""

from __future__ import annotations

from pathlib import Path

import pytest


def test_get_claude_md_happy_path(client):
    r = client.get("/api/file?path=CLAUDE.md")
    assert r.status_code == 200
    body = r.json()
    assert body["path"] == "CLAUDE.md"
    assert "# CLAUDE.md" in body["content"]
    assert body["bytes"] > 0
    assert "mtime" in body


def test_get_includes_nosniff_header(client):
    r = client.get("/api/file?path=CLAUDE.md")
    assert r.status_code == 200
    assert r.headers.get("x-content-type-options") == "nosniff"


def test_get_includes_content_disposition_attachment(client):
    r = client.get("/api/file?path=CLAUDE.md")
    assert r.status_code == 200
    cd = r.headers.get("content-disposition", "")
    assert "attachment" in cd.lower()


@pytest.mark.parametrize("ext", [".md", ".json", ".yaml", ".yml", ".jsonl", ".txt"])
def test_reads_allowed_text_extensions(client, scratch_dir: Path, ext):
    f = scratch_dir / f"sample{ext}"
    f.write_bytes(b"ok\n")
    rel = f"specs/development/spec_driven/__scratch__/sample{ext}"
    r = client.get(f"/api/file?path={rel}")
    assert r.status_code == 200
    body = r.json()
    assert body["bytes"] == 3


def test_reads_uppercase_extension(client, scratch_dir: Path):
    f = scratch_dir / "Sample.MD"
    f.write_text("ok", encoding="utf-8")
    rel = "specs/development/spec_driven/__scratch__/Sample.MD"
    r = client.get(f"/api/file?path={rel}")
    assert r.status_code == 200


@pytest.mark.parametrize(
    "ext",
    [".exe", ".bat", ".cmd", ".ps1", ".sh", ".html", ".svg", ".dll", ".php", ".zip"],
)
def test_disallowed_extension_returns_415(client, scratch_dir: Path, ext):
    f = scratch_dir / f"blocked{ext}"
    f.write_text("nope", encoding="utf-8")
    rel = f"specs/development/spec_driven/__scratch__/blocked{ext}"
    r = client.get(f"/api/file?path={rel}")
    assert r.status_code == 415


def test_no_extension_returns_415_or_404(client, scratch_dir: Path):
    f = scratch_dir / "noext"
    f.write_text("x", encoding="utf-8")
    rel = "specs/development/spec_driven/__scratch__/noext"
    r = client.get(f"/api/file?path={rel}")
    assert r.status_code in (404, 415)


def test_double_extension_resolves_to_leaf(client, scratch_dir: Path):
    """foo.md.exe → leaf is .exe → 415."""
    f = scratch_dir / "foo.md.exe"
    f.write_text("nope", encoding="utf-8")
    rel = "specs/development/spec_driven/__scratch__/foo.md.exe"
    r = client.get(f"/api/file?path={rel}")
    assert r.status_code == 415


def test_oversize_read_returns_413(client, scratch_dir: Path):
    f = scratch_dir / "huge.md"
    f.write_bytes(b"a" * (1024 * 1024 + 1))
    rel = "specs/development/spec_driven/__scratch__/huge.md"
    r = client.get(f"/api/file?path={rel}")
    assert r.status_code == 413


def test_exact_1mb_file_reads_ok(client, scratch_dir: Path):
    """Boundary: spec says >1MB → 413; exactly 1 MB is allowed."""
    f = scratch_dir / "exactly_1mb.md"
    f.write_bytes(b"a" * (1024 * 1024))
    rel = "specs/development/spec_driven/__scratch__/exactly_1mb.md"
    r = client.get(f"/api/file?path={rel}")
    assert r.status_code == 200


def test_zero_byte_file_reads_ok(client, scratch_dir: Path):
    f = scratch_dir / "empty.md"
    f.write_bytes(b"")
    rel = "specs/development/spec_driven/__scratch__/empty.md"
    r = client.get(f"/api/file?path={rel}")
    assert r.status_code == 200
    assert r.json()["bytes"] == 0


@pytest.mark.parametrize(
    "probe",
    [
        "../etc/passwd",
        "../../etc/passwd",
        "/etc/passwd",
        "specs/../../etc/passwd",
        "specs/development/spec_driven/__scratch__/does_not_exist.md",
    ],
)
def test_outside_tree_or_missing_returns_single_404(client, probe):
    """Same 404 status for all four 'not-found' classes (no existence oracle)."""
    r = client.get(f"/api/file?path={probe}")
    assert r.status_code == 404


def test_404_body_shape_uniform(client):
    """Outside-tree 404 and inside-tree-missing 404 carry same body shape."""
    a = client.get("/api/file?path=../etc/passwd")
    b = client.get(
        "/api/file?path=specs/development/spec_driven/__scratch__/missing_xyz.md"
    )
    assert a.status_code == 404
    assert b.status_code == 404
    # Both must be JSON and carry a `detail` field; we don't pin exact text but
    # the absence of a path/realpath in the body must hold.
    a_body = a.json()
    b_body = b.json()
    assert "detail" in a_body
    assert "detail" in b_body


def test_404_does_not_leak_realpath(client):
    r = client.get("/api/file?path=../../etc/passwd")
    assert r.status_code == 404
    body_text = r.text
    assert "C:\\" not in body_text
    assert "/etc/passwd" not in body_text


def test_reads_under_dotclaude_subtrees(client):
    """FR-2 — recursive `.claude/**/*.md` discovery."""
    rel = ".claude/skills/agent_team/SKILL.md"
    r = client.get(f"/api/file?path={rel}")
    # If the SKILL.md is on disk, we expect 200; if absent, 404 — but never 415.
    assert r.status_code in (200, 404)


def test_get_image_file_reads_ok(client, scratch_dir: Path):
    f = scratch_dir / "tiny.png"
    # Minimum valid PNG signature (just the magic bytes).
    f.write_bytes(b"\x89PNG\r\n\x1a\n")
    rel = "specs/development/spec_driven/__scratch__/tiny.png"
    r = client.get(f"/api/file?path={rel}")
    assert r.status_code == 200
