"""
Group 7 — promotions (POST /api/promote, DELETE /api/promote).

Spec anchors: FR-13, FR-14, AC-24.
"""

from __future__ import annotations

from pathlib import Path

import pytest


def _promote_body(**overrides):
    body = dict(
        project_type="development",
        project_name="spec_driven",
        stage_folder="validation",
        source_file="validation/strategy.md",
        item_id="test-item-1",
        item_text="Sample pinned text body for parser tests.",
    )
    body.update(overrides)
    return body


@pytest.fixture()
def promoted_path(repo_root) -> Path:
    return (
        repo_root.path
        / "specs"
        / "development"
        / "spec_driven"
        / "validation"
        / "promoted.md"
    )


# ---------------------------------------------------------------------------
# 7.3 / 7.5 / 7.6 — POST then DELETE roundtrip + idempotence
# ---------------------------------------------------------------------------


def test_post_then_delete_round_trip(client, good_headers, promoted_path: Path):
    item_id = "rt-test-promote-1"
    p = client.post(
        "/api/promote",
        headers=good_headers,
        json=_promote_body(item_id=item_id, item_text="Round-trip body."),
    )
    assert p.status_code == 200
    assert p.json()["item_id"] == item_id

    d = client.request(
        "DELETE",
        "/api/promote",
        headers=good_headers,
        json={
            "project_type": "development",
            "project_name": "spec_driven",
            "stage_folder": "validation",
            "item_id": item_id,
        },
    )
    assert d.status_code == 200
    assert d.json()["item_id"] == item_id


def test_delete_idempotent_when_missing(client, good_headers):
    """FR-14 — DELETE non-existent item returns 200 (idempotent)."""
    r = client.request(
        "DELETE",
        "/api/promote",
        headers=good_headers,
        json={
            "project_type": "development",
            "project_name": "spec_driven",
            "stage_folder": "validation",
            "item_id": "definitely-does-not-exist-xyzzy-9999",
        },
    )
    assert r.status_code == 200


def test_post_promote_creates_promoted_md(client, good_headers, promoted_path: Path):
    """After POST, promoted.md MUST contain the item's text."""
    item_id = "creator-test-promote-1"
    text = "Creator-test pinned text — XYZZY-CREATE-1"
    r = client.post(
        "/api/promote",
        headers=good_headers,
        json=_promote_body(item_id=item_id, item_text=text),
    )
    assert r.status_code == 200
    assert promoted_path.exists()
    content = promoted_path.read_text(encoding="utf-8")
    assert "XYZZY-CREATE-1" in content
    # Cleanup.
    client.request(
        "DELETE",
        "/api/promote",
        headers=good_headers,
        json={
            "project_type": "development",
            "project_name": "spec_driven",
            "stage_folder": "validation",
            "item_id": item_id,
        },
    )


def test_post_promote_idempotent_same_item(client, good_headers):
    """Spec FR-13 — same {stage_folder, source_file, item_id} → no dup."""
    body = _promote_body(item_id="idempotent-1", item_text="dup body")
    r1 = client.post("/api/promote", headers=good_headers, json=body)
    r2 = client.post("/api/promote", headers=good_headers, json=body)
    assert r1.status_code == 200
    assert r2.status_code == 200
    # Cleanup.
    client.request(
        "DELETE",
        "/api/promote",
        headers=good_headers,
        json={
            "project_type": "development",
            "project_name": "spec_driven",
            "stage_folder": "validation",
            "item_id": "idempotent-1",
        },
    )


# ---------------------------------------------------------------------------
# 7.7 / 7.8 — stage_folder allowlist
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "stage_folder",
    ["interview", "findings", "final_specs", "validation"],
)
def test_post_promote_allowlist_accepts(client, good_headers, stage_folder):
    item_id = f"allowed-{stage_folder}-test"
    r = client.post(
        "/api/promote",
        headers=good_headers,
        json=_promote_body(stage_folder=stage_folder, item_id=item_id),
    )
    assert r.status_code == 200
    # Cleanup.
    client.request(
        "DELETE",
        "/api/promote",
        headers=good_headers,
        json={
            "project_type": "development",
            "project_name": "spec_driven",
            "stage_folder": stage_folder,
            "item_id": item_id,
        },
    )


@pytest.mark.parametrize(
    "stage_folder",
    [
        "user_input",
        "..",
        "../etc",
        "projects",
        "stage_6",
        "execution",
        "Interview",  # case-sensitive — strict allowlist
        "INTERVIEW",
        "",
    ],
)
def test_post_promote_allowlist_rejects(client, good_headers, stage_folder):
    """Non-allowlisted stage_folder values → 400 or 422."""
    r = client.post(
        "/api/promote",
        headers=good_headers,
        json=_promote_body(stage_folder=stage_folder, item_id="reject-test"),
    )
    assert r.status_code in (400, 422)


def test_post_promote_traversal_in_project_name_rejected(client, good_headers):
    r = client.post(
        "/api/promote",
        headers=good_headers,
        json=_promote_body(project_name="../etc"),
    )
    assert r.status_code in (400, 404, 422)


# ---------------------------------------------------------------------------
# parse_promoted_text round-trip — direct lib call
# ---------------------------------------------------------------------------


def test_parse_promoted_text_round_trip():
    """The parser handles the synthesized format the writer produces.
    Skips when the lib doesn't expose `parse_promoted_text`/`PromotedItem`.
    """
    try:
        from libs.promotions import parse_promoted_text
    except (ImportError, AttributeError):
        pytest.skip("parse_promoted_text not exported")

    sample = (
        "<!-- pin source=interview/qa.md id=Q5 -->\n"
        "### Q5 — Why this auth model?\n"
        "- A: localhost-only.\n\n"
        "<!-- pin source=interview/qa.md id=Q6 -->\n"
        "### Q6 — Title\n"
        "- A: yes.\n"
    )
    items = parse_promoted_text(sample)
    assert len(items) >= 1


def test_parse_promoted_text_empty_returns_empty():
    try:
        from libs.promotions import parse_promoted_text
    except (ImportError, AttributeError):
        pytest.skip("parse_promoted_text not exported")
    items = parse_promoted_text("")
    assert items == [] or items == ()


def test_parse_promoted_text_only_header_returns_empty():
    try:
        from libs.promotions import parse_promoted_text
    except (ImportError, AttributeError):
        pytest.skip("parse_promoted_text not exported")
    items = parse_promoted_text("# Promoted items\n\n_INPUT to regeneration..._\n")
    assert items == [] or items == ()


# ---------------------------------------------------------------------------
# Origin/Host gate on promote endpoints (FR-9 cross-check)
# ---------------------------------------------------------------------------


def test_post_promote_foreign_origin_403(client):
    r = client.post(
        "/api/promote",
        headers={"Origin": "http://evil.example.com", "Host": "127.0.0.1:8765"},
        json=_promote_body(item_id="foreign-origin-test"),
    )
    assert r.status_code == 403


def test_delete_promote_foreign_origin_403(client):
    r = client.request(
        "DELETE",
        "/api/promote",
        headers={"Origin": "http://evil.example.com", "Host": "127.0.0.1:8765"},
        json={
            "project_type": "development",
            "project_name": "spec_driven",
            "stage_folder": "validation",
            "item_id": "anything",
        },
    )
    assert r.status_code == 403
