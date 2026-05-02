from __future__ import annotations

from pathlib import Path

from libs.exposed_tree import ExposedTree


def test_claude_md_root_positive(fake_repo: Path) -> None:
    tree = ExposedTree(fake_repo)
    assert tree.is_inside(fake_repo / "CLAUDE.md") is True


def test_claude_md_in_subdir_negative(fake_repo: Path) -> None:
    tree = ExposedTree(fake_repo)
    sub = fake_repo / "projects" / "spec_driven"
    sub.mkdir(parents=True)
    nested = sub / "CLAUDE.md"
    nested.write_text("x", encoding="utf-8")
    assert tree.is_inside(nested) is False


def test_agents_canonical_md_positive(fake_repo: Path) -> None:
    tree = ExposedTree(fake_repo)
    p = fake_repo / ".claude" / "agents" / "agent_team__research_manager.md"
    assert tree.is_inside(p) is True


def test_agents_yaml_negative(fake_repo: Path) -> None:
    tree = ExposedTree(fake_repo)
    p = fake_repo / ".claude" / "agents" / "foo.yaml"
    p.write_text("x", encoding="utf-8")
    assert tree.is_inside(p) is False


def test_skills_canonical_positive(fake_repo: Path) -> None:
    tree = ExposedTree(fake_repo)
    p = fake_repo / ".claude" / "skills" / "agent_team" / "SKILL.md"
    assert tree.is_inside(p) is True


def test_skills_other_md_negative(fake_repo: Path) -> None:
    tree = ExposedTree(fake_repo)
    p = fake_repo / ".claude" / "skills" / "agent_team" / "README.md"
    p.write_text("x", encoding="utf-8")
    assert tree.is_inside(p) is False


def test_specs_final_specs_md_positive(fake_repo: Path) -> None:
    tree = ExposedTree(fake_repo)
    p = fake_repo / "specs" / "development" / "spec_driven" / "final_specs" / "spec.md"
    assert tree.is_inside(p) is True


def test_specs_outside_five_stages_negative(fake_repo: Path) -> None:
    tree = ExposedTree(fake_repo)
    notes = fake_repo / "specs" / "development" / "spec_driven" / "notes"
    notes.mkdir(parents=True)
    p = notes / "scratch.md"
    p.write_text("x", encoding="utf-8")
    assert tree.is_inside(p) is False


def test_specs_unsupported_extension_is_structurally_inside(fake_repo: Path) -> None:
    tree = ExposedTree(fake_repo)
    p = fake_repo / "specs" / "development" / "spec_driven" / "findings" / "diagram.png"
    p.write_text("x", encoding="utf-8")
    assert tree.is_inside(p) is True


def test_specs_jsonl_under_validation_positive(fake_repo: Path) -> None:
    tree = ExposedTree(fake_repo)
    p = fake_repo / "specs" / "development" / "spec_driven" / "validation" / "events.jsonl"
    p.write_text("{}\n", encoding="utf-8")
    assert tree.is_inside(p) is True
