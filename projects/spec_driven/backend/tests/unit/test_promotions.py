"""
Group 5 — promotions (FR-13, FR-14, FR-37).
"""

from __future__ import annotations

import pytest

from libs.promotions import (
    ALLOWED_STAGE_FOLDERS,
    PromotionError,
    Promotions,
    parse_promoted_text,
)


@pytest.fixture()
def temp_project(repo_root, tmp_path, monkeypatch):
    fake_root = tmp_path / "fake_repo"
    (fake_root / ".claude").mkdir(parents=True)
    (fake_root / "CLAUDE.md").write_text("ok", encoding="utf-8")
    (fake_root / "specs" / "development" / "test_proj" / "interview").mkdir(parents=True)
    return fake_root


def test_post_appends_block(temp_project):
    p = Promotions(repo_root=temp_project)
    p.post("development", "test_proj", "interview", "qa.md", "qa-r1-c1-q1", "First Q body.")
    f = temp_project / "specs" / "development" / "test_proj" / "interview" / "promoted.md"
    text = f.read_text(encoding="utf-8")
    assert "qa-r1-c1-q1" in text
    assert "First Q body." in text


def test_post_idempotent_same_id_replaces(temp_project):
    p = Promotions(repo_root=temp_project)
    p.post("development", "test_proj", "interview", "qa.md", "id-1", "v1")
    p.post("development", "test_proj", "interview", "qa.md", "id-1", "v2")
    f = temp_project / "specs" / "development" / "test_proj" / "interview" / "promoted.md"
    text = f.read_text(encoding="utf-8")
    items = parse_promoted_text(text)
    assert len([it for it in items if it.item_id == "id-1"]) == 1
    assert "v2" in text
    assert "v1" not in text


def test_delete_removes_only_matching(temp_project):
    p = Promotions(repo_root=temp_project)
    p.post("development", "test_proj", "interview", "qa.md", "A", "Pin A body.")
    p.post("development", "test_proj", "interview", "qa.md", "B", "Pin B body.")
    p.post("development", "test_proj", "interview", "qa.md", "C", "Pin C body.")
    p.delete("development", "test_proj", "interview", "B")
    text = (temp_project / "specs" / "development" / "test_proj" / "interview" / "promoted.md").read_text(encoding="utf-8")
    assert "Pin A body." in text
    assert "Pin B body." not in text
    assert "Pin C body." in text


def test_delete_unknown_id_raises(temp_project):
    p = Promotions(repo_root=temp_project)
    p.post("development", "test_proj", "interview", "qa.md", "A", "x")
    with pytest.raises(PromotionError):
        p.delete("development", "test_proj", "interview", "ghost")


def test_post_delete_roundtrip(temp_project):
    p = Promotions(repo_root=temp_project)
    p.post("development", "test_proj", "interview", "qa.md", "id-x", "Pin body.")
    p.delete("development", "test_proj", "interview", "id-x")
    text = (temp_project / "specs" / "development" / "test_proj" / "interview" / "promoted.md").read_text(encoding="utf-8")
    assert "Pin body." not in text
    assert parse_promoted_text(text) == []


@pytest.mark.parametrize("bad", ["user_input", "projects", "../etc", "INTERVIEW", ""])
def test_stage_folder_allowlist(temp_project, bad):
    p = Promotions(repo_root=temp_project)
    with pytest.raises(PromotionError):
        p.post("development", "test_proj", bad, "qa.md", "id", "body")


def test_stage_folder_allowlist_constants():
    assert ALLOWED_STAGE_FOLDERS == frozenset({"interview", "findings", "final_specs", "validation"})


def test_parse_promoted_text_round_trips(temp_project):
    p = Promotions(repo_root=temp_project)
    p.post("development", "test_proj", "interview", "qa.md", "alpha", "Body A with ## inside.")
    p.post("development", "test_proj", "interview", "qa.md", "beta", "Body B\n\nMultiline.")
    text = (temp_project / "specs" / "development" / "test_proj" / "interview" / "promoted.md").read_text(encoding="utf-8")
    items = parse_promoted_text(text)
    ids = {it.item_id for it in items}
    assert ids == {"alpha", "beta"}
