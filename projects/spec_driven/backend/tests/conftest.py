from __future__ import annotations

import sys
from pathlib import Path

import pytest


BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


@pytest.fixture
def fake_repo(tmp_path: Path) -> Path:
    (tmp_path / "CLAUDE.md").write_text("# CLAUDE.md fake\n", encoding="utf-8")

    agents_dir = tmp_path / ".claude" / "agents"
    agents_dir.mkdir(parents=True)
    (agents_dir / "agent_team__interview_manager.md").write_text(
        "# interview manager\n", encoding="utf-8"
    )
    (agents_dir / "agent_team__research_manager.md").write_text(
        "# research manager\n", encoding="utf-8"
    )

    skills_dir = tmp_path / ".claude" / "skills" / "agent_team"
    skills_dir.mkdir(parents=True)
    (skills_dir / "SKILL.md").write_text("# agent_team skill\n", encoding="utf-8")

    project = tmp_path / "specs" / "development" / "spec_driven"

    user_input = project / "user_input"
    user_input.mkdir(parents=True)
    (user_input / "raw_prompt.md").write_text("raw prompt content\n", encoding="utf-8")
    (user_input / "revised_prompt.md").write_text(
        "revised prompt content\n", encoding="utf-8"
    )

    interview = project / "interview"
    interview.mkdir(parents=True)
    (interview / "qa.md").write_text("# qa\n", encoding="utf-8")

    findings = project / "findings"
    findings.mkdir(parents=True)
    (findings / "dossier.md").write_text("# dossier\n", encoding="utf-8")
    (findings / "angle-a.md").write_text("# angle a\n", encoding="utf-8")

    final_specs = project / "final_specs"
    final_specs.mkdir(parents=True)
    (final_specs / "spec.md").write_text("# spec content\n", encoding="utf-8")

    validation = project / "validation"
    validation.mkdir(parents=True)
    (validation / "strategy.md").write_text("# strategy\n", encoding="utf-8")
    (validation / "acceptance_criteria.md").write_text("# ac\n", encoding="utf-8")
    (validation / "bdd_scenarios.md").write_text("# bdd\n", encoding="utf-8")
    (validation / "extra.md").write_text("# extra\n", encoding="utf-8")

    return tmp_path
