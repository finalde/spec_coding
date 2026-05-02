from __future__ import annotations

from pathlib import Path

from libs.tree_walker import build_tree


def test_basic_shape(fake_repo: Path) -> None:
    tree = build_tree(fake_repo)
    assert list(tree.keys()) == ["settings", "projects"]
    settings = tree["settings"]
    assert isinstance(settings, dict)
    assert list(settings.keys()) == ["claude_md", "playbooks", "skills", "agent_refs"]


def test_missing_folder_for_absent_stage(tmp_path: Path) -> None:
    (tmp_path / "CLAUDE.md").write_text("x", encoding="utf-8")
    (tmp_path / ".claude" / "skills" / "agent_team" / "playbooks").mkdir(parents=True)
    (tmp_path / ".claude" / "skills").mkdir(parents=True, exist_ok=True)
    project = tmp_path / "specs" / "development" / "spec_driven"
    (project / "user_input").mkdir(parents=True)
    (project / "user_input" / "raw_prompt.md").write_text("x", encoding="utf-8")
    tree = build_tree(tmp_path)
    projects = tree["projects"]
    assert isinstance(projects, list) and projects
    type_node = projects[0]
    assert type_node["name"] == "development"
    proj_list = type_node["children"]
    assert isinstance(proj_list, list) and proj_list
    stages = proj_list[0]["children"]
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
    proj = tree["projects"][0]["children"][0]
    stages = proj["children"]
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
    proj = tree["projects"][0]["children"][0]
    findings_node = next(s for s in proj["children"] if s["name"] == "findings")
    files = [c["name"] for c in findings_node["children"] if c.get("kind") == "file"]
    lower_seq = [n.lower() for n in files]
    assert lower_seq == sorted(lower_seq)


def test_every_non_leaf_uses_children_field(fake_repo: Path) -> None:
    """Sidebar walks the tree via the single `children` field at every depth.
    Backend MUST NOT use stage-specific names like `projects` or `stages` for descent."""
    tree = build_tree(fake_repo)
    leaves: list[str] = []

    def walk(node: dict[str, object], depth: int) -> None:
        kind = node.get("kind")
        if kind == "file":
            leaves.append(str(node.get("path", "")))
            return
        if kind == "missing-folder":
            return
        children = node.get("children")
        assert isinstance(children, list), (
            f"node kind={kind!r} at depth {depth} missing `children` list "
            f"(got keys {list(node.keys())!r}); frontend Sidebar relies on this single field"
        )
        for c in children:
            assert isinstance(c, dict)
            walk(c, depth + 1)

    for tt in tree["projects"]:
        assert isinstance(tt, dict)
        walk(tt, 1)
    assert leaves, "expected at least one file leaf under projects"
    assert any(p.endswith("/spec.md") for p in leaves)
