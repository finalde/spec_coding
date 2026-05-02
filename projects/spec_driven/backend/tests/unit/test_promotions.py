from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from libs.api import build_app
from libs.file_reader import FileReadError
from libs.promotions import (
    Pin,
    PROMOTED_FILENAME,
    add_promotion,
    list_promotions,
    parse_promoted_text,
    remove_promotion,
    render_promoted_text,
)


def test_parse_empty_text_returns_empty_tuple() -> None:
    assert parse_promoted_text("") == ()
    assert parse_promoted_text("\n\n   \n") == ()


def test_parse_round_trip() -> None:
    rendered = render_promoted_text(
        "interview",
        (
            Pin(
                pin_id="pin-001",
                location="interview/qa.md / Round 1 / functional-scope",
                body="**Q:** Section 1?\n- A: Fixed three globs.",
            ),
            Pin(
                pin_id="pin-002",
                location="interview/qa.md / Round 2 / success-criteria",
                body="**Q:** e2e framework?\n- A: Playwright.",
            ),
        ),
    )
    pins = parse_promoted_text(rendered)
    assert len(pins) == 2
    assert pins[0].pin_id == "pin-001"
    assert "Section 1" in pins[0].body
    assert pins[1].pin_id == "pin-002"
    assert "Playwright" in pins[1].body


def test_add_first_pin_creates_file(fake_repo: Path) -> None:
    stage_path = "specs/development/spec_driven/interview"
    pin = add_promotion(
        stage_path=stage_path,
        location="interview/qa.md / Round 1 / scope",
        body="**Q:** test?\n- A: ok.",
        repo_root=fake_repo,
    )
    assert pin.pin_id == "pin-001"
    target = fake_repo / "specs" / "development" / "spec_driven" / "interview" / PROMOTED_FILENAME
    assert target.is_file()
    text = target.read_text(encoding="utf-8")
    assert "pin-001" in text
    assert "test?" in text


def test_add_two_pins_assigns_sequential_ids(fake_repo: Path) -> None:
    stage_path = "specs/development/spec_driven/interview"
    p1 = add_promotion(stage_path, "loc-a", "body-a", fake_repo)
    p2 = add_promotion(stage_path, "loc-b", "body-b", fake_repo)
    assert p1.pin_id == "pin-001"
    assert p2.pin_id == "pin-002"
    listing = list_promotions(stage_path, fake_repo)
    assert [p.pin_id for p in listing.pins] == ["pin-001", "pin-002"]


def test_remove_pin(fake_repo: Path) -> None:
    stage_path = "specs/development/spec_driven/interview"
    add_promotion(stage_path, "loc-a", "body-a", fake_repo)
    p2 = add_promotion(stage_path, "loc-b", "body-b", fake_repo)
    remove_promotion(stage_path, p2.pin_id, fake_repo)
    listing = list_promotions(stage_path, fake_repo)
    assert [p.pin_id for p in listing.pins] == ["pin-001"]


def test_remove_last_pin_deletes_file(fake_repo: Path) -> None:
    stage_path = "specs/development/spec_driven/interview"
    p = add_promotion(stage_path, "loc-a", "body-a", fake_repo)
    target = fake_repo / "specs" / "development" / "spec_driven" / "interview" / PROMOTED_FILENAME
    assert target.is_file()
    remove_promotion(stage_path, p.pin_id, fake_repo)
    assert not target.exists()


def test_remove_unknown_pin_raises(fake_repo: Path) -> None:
    stage_path = "specs/development/spec_driven/interview"
    add_promotion(stage_path, "loc-a", "body-a", fake_repo)
    with pytest.raises(FileReadError) as ei:
        remove_promotion(stage_path, "pin-999", fake_repo)
    assert ei.value.status == 404
    assert ei.value.kind == "pin_not_found"


def test_invalid_stage_path_rejected(fake_repo: Path) -> None:
    with pytest.raises(FileReadError) as ei:
        add_promotion("specs/development/spec_driven/notes", "loc", "body", fake_repo)
    assert ei.value.status in (400, 404)
    assert ei.value.kind in ("not_a_stage_dir", "stage_dir_missing")


def test_path_traversal_rejected(fake_repo: Path) -> None:
    with pytest.raises(FileReadError) as ei:
        add_promotion("../../../etc/passwd", "loc", "body", fake_repo)
    assert ei.value.status == 400


def test_empty_body_rejected(fake_repo: Path) -> None:
    with pytest.raises(FileReadError) as ei:
        add_promotion("specs/development/spec_driven/interview", "loc", "   ", fake_repo)
    assert ei.value.status == 400


def test_list_returns_empty_when_no_file(fake_repo: Path) -> None:
    payload = list_promotions("specs/development/spec_driven/interview", fake_repo)
    assert payload.pins == ()


def test_api_promotions_round_trip(fake_repo: Path) -> None:
    client = TestClient(build_app(fake_repo))
    stage_path = "specs/development/spec_driven/interview"

    resp = client.get("/api/promotions", params={"stage_path": stage_path})
    assert resp.status_code == 200
    assert resp.json()["pins"] == []

    resp = client.post(
        "/api/promote",
        json={
            "stage_path": stage_path,
            "location": "interview/qa.md / Round 1 / scope",
            "body": "**Q:** test?\n- A: ok.",
        },
    )
    assert resp.status_code == 200
    pin1 = resp.json()
    assert pin1["pin_id"] == "pin-001"

    resp = client.get("/api/promotions", params={"stage_path": stage_path})
    assert resp.status_code == 200
    assert len(resp.json()["pins"]) == 1

    resp = client.request(
        "DELETE",
        "/api/promote",
        json={"stage_path": stage_path, "pin_id": "pin-001"},
    )
    assert resp.status_code == 200
    assert resp.json() == {"ok": True}

    resp = client.get("/api/promotions", params={"stage_path": stage_path})
    assert resp.json()["pins"] == []


def test_api_post_promote_path_traversal_returns_400(fake_repo: Path) -> None:
    client = TestClient(build_app(fake_repo))
    resp = client.post(
        "/api/promote",
        json={"stage_path": "../../etc", "location": "x", "body": "y"},
    )
    assert resp.status_code == 400
