from __future__ import annotations

from pathlib import Path

from libs.tree_walker import build_tree


def test_basic_shape(fake_repo: Path) -> None:
    tree = build_tree(fake_repo)
    assert list(tree.keys()) == ["settings", "projects"]
    settings = tree["settings"]
    assert isinstance(settings, dict)
    assert list(settings.keys()) == ["claude_md", "agents", "skills"]


def test_missing_folder_for_absent_stage(tmp_path: Path) -> None:
    (tmp_path / "CLAUDE.md").write_text("x", encoding="utf-8")
    (tmp_path / ".claude" / "agents").mkdir(parents=True)
    (tmp_path / ".claude" / "skills").mkdir(parents=True)
    project = tmp_path / "specs" / "development" / "spec_driven"
    (project / "user_input").mkdir(parents=True)
    (project / "user_input" / "raw_prompt.md").write_text("x", encoding="utf-8")
    tree = build_tree(tmp_path)
    projects = tree["projects"]
    assert isinstance(projects, list) and projects
    type_node = projects[0]
    assert type_node["name"] == "development"
    proj_list = type_node["projects"]
    assert isinstance(proj_list, list) and proj_list
    stages = proj_list[0]["stages"]
    stage_names = [s["name"] for s in stages]
    assert stage_names == ["user_input", "interview", "findings", "final_specs", "validation"]
    validation = stages[-1]
    assert validation["kind"] == "missing-folder"
    assert validation["present"] is False


def test_validation_priority_order(fake_repo: Path) -> None:
    val_dir = fake_repo / "specs" / "development" / "spec_driven" / "validation"
    (val_dir / "system_tests.md").write_text("x", encoding="utf-8")
    (val_dir / "unit_tests.md").write_text("x", encoding="utf-8")
    (val_dir / "security.md").write_text("x", encoding="utf-8")
    tree = build_tree(fake_repo)
    proj = tree["projects"][0]["projects"][0]
    stages = proj["stages"]
    validation = next(s for s in stages if s["name"] == "validation")
    files = [c["name"] for c in validation["children"] if c.get("kind") == "file"]
    assert files[0] == "strategy.md"
    assert files[1] == "acceptance_criteria.md"
    assert files[2] == "bdd_scenarios.md"
    tail = files[3:]
    assert tail == sorted(tail, key=lambda n: n.lower())


def test_alphabetical_within_stage_case_insensitive(fake_repo: Path) -> None:
    findings = fake_repo / "specs" / "development" / "spec_driven" / "findings"
    (findings / "Zebra.md").write_text("x", encoding="utf-8")
    (findings / "alpha.md").write_text("x", encoding="utf-8")
    (findings / "Alpha-2.md").write_text("x", encoding="utf-8")
    (findings / "beta.md").write_text("x", encoding="utf-8")
    tree = build_tree(fake_repo)
    proj = tree["projects"][0]["projects"][0]
    findings_node = next(s for s in proj["stages"] if s["name"] == "findings")
    files = [c["name"] for c in findings_node["children"] if c.get("kind") == "file"]
    lower_seq = [n.lower() for n in files]
    assert lower_seq == sorted(lower_seq)
