from __future__ import annotations

from pathlib import Path

from libs.exposed_tree import ExposedTree


def test_claude_md_inside(fake_repo: Path) -> None:
    tree = ExposedTree(repo_root=fake_repo)
    assert tree.is_inside(fake_repo / "CLAUDE.md")


def test_pyproject_outside(fake_repo: Path) -> None:
    (fake_repo / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
    tree = ExposedTree(repo_root=fake_repo)
    assert not tree.is_inside(fake_repo / "pyproject.toml")


def test_agent_md_inside(fake_repo: Path) -> None:
    tree = ExposedTree(repo_root=fake_repo)
    p = fake_repo / ".claude" / "agents" / "agent_team__interview_manager.md"
    assert tree.is_inside(p)


def test_agents_init_py_outside(fake_repo: Path) -> None:
    p = fake_repo / ".claude" / "agents" / "__init__.py"
    p.write_text("", encoding="utf-8")
    tree = ExposedTree(repo_root=fake_repo)
    assert not tree.is_inside(p)


def test_skill_md_inside(fake_repo: Path) -> None:
    tree = ExposedTree(repo_root=fake_repo)
    p = fake_repo / ".claude" / "skills" / "agent_team" / "SKILL.md"
    assert tree.is_inside(p)


def test_skill_readme_outside(fake_repo: Path) -> None:
    p = fake_repo / ".claude" / "skills" / "agent_team" / "README.md"
    p.write_text("", encoding="utf-8")
    tree = ExposedTree(repo_root=fake_repo)
    assert not tree.is_inside(p)


def test_user_input_md_inside(fake_repo: Path) -> None:
    tree = ExposedTree(repo_root=fake_repo)
    p = fake_repo / "specs" / "development" / "spec_driven" / "user_input" / "raw_prompt.md"
    assert tree.is_inside(p)


def test_non_stage_subfolder_outside(fake_repo: Path) -> None:
    bad = fake_repo / "specs" / "development" / "spec_driven" / "notes"
    bad.mkdir(parents=True)
    p = bad / "scratch.md"
    p.write_text("", encoding="utf-8")
    tree = ExposedTree(repo_root=fake_repo)
    assert not tree.is_inside(p)


def test_jsonl_in_validation_inside(fake_repo: Path) -> None:
    p = fake_repo / "specs" / "development" / "spec_driven" / "validation" / "events.jsonl"
    p.write_text('{"a":1}\n', encoding="utf-8")
    tree = ExposedTree(repo_root=fake_repo)
    assert tree.is_inside(p)


def test_unsupported_extension_outside(fake_repo: Path) -> None:
    p = fake_repo / "specs" / "development" / "spec_driven" / "final_specs" / "diagram.png"
    p.write_bytes(b"\x89PNG")
    tree = ExposedTree(repo_root=fake_repo)
    assert not tree.is_inside(p)
