from __future__ import annotations

from pathlib import Path

from libs.tree_walker import build_tree


def _names(nodes: list[dict[str, object]]) -> list[str]:
    return [n["name"] for n in nodes]  # type: ignore[index]


def test_tree_top_level_keys(fake_repo: Path) -> None:
    result = build_tree(fake_repo)
    assert set(result.keys()) == {"settings", "projects"}


def test_tree_settings_three_subgroups(fake_repo: Path) -> None:
    settings = build_tree(fake_repo)["settings"]
    assert isinstance(settings, dict)
    assert set(settings.keys()) == {"claude_md", "agents", "skills"}
    assert _names(settings["claude_md"]) == ["CLAUDE.md"]  # type: ignore[arg-type]
    assert _names(settings["agents"]) == [  # type: ignore[arg-type]
        "agent_team__interview_manager.md",
        "agent_team__research_manager.md",
    ]
    assert _names(settings["skills"]) == ["agent_team"]  # type: ignore[arg-type]


def test_tree_projects_section_shape(fake_repo: Path) -> None:
    projects = build_tree(fake_repo)["projects"]
    assert isinstance(projects, list)
    assert _names(projects) == ["development"]  # type: ignore[arg-type]
    project_children = projects[0]["children"]  # type: ignore[index]
    assert _names(project_children) == ["spec_driven"]  # type: ignore[arg-type]
    stages = projects[0]["children"][0]["children"]  # type: ignore[index]
    assert _names(stages) == [  # type: ignore[arg-type]
        "user_input",
        "interview",
        "findings",
        "final_specs",
        "validation",
    ]


def test_validation_priority_ordering(fake_repo: Path) -> None:
    projects = build_tree(fake_repo)["projects"]
    validation_node = projects[0]["children"][0]["children"][4]  # type: ignore[index]
    assert validation_node["name"] == "validation"
    children = validation_node["children"]
    assert _names(children) == [  # type: ignore[arg-type]
        "strategy.md",
        "acceptance_criteria.md",
        "bdd_scenarios.md",
        "extra.md",
    ]


def test_missing_stage_present_false(fake_repo: Path) -> None:
    import shutil

    shutil.rmtree(fake_repo / "specs" / "development" / "spec_driven" / "validation")
    projects = build_tree(fake_repo)["projects"]
    validation_node = projects[0]["children"][0]["children"][4]  # type: ignore[index]
    assert validation_node["name"] == "validation"
    assert validation_node["kind"] == "missing-folder"
    assert validation_node["present"] is False


def test_files_alphabetical_in_findings(fake_repo: Path) -> None:
    findings = fake_repo / "specs" / "development" / "spec_driven" / "findings"
    (findings / "z-late.md").write_text("", encoding="utf-8")
    (findings / "B-mid.md").write_text("", encoding="utf-8")
    projects = build_tree(fake_repo)["projects"]
    findings_node = projects[0]["children"][0]["children"][2]  # type: ignore[index]
    assert _names(findings_node["children"]) == [  # type: ignore[arg-type]
        "angle-a.md",
        "B-mid.md",
        "dossier.md",
        "z-late.md",
    ]
