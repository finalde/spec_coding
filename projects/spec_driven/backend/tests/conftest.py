from __future__ import annotations

import sys
from pathlib import Path

import pytest

BACKEND_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_ROOT))


@pytest.fixture()
def fake_repo(tmp_path: Path) -> Path:
    (tmp_path / "CLAUDE.md").write_text("# fake claude.md\n", encoding="utf-8")
    (tmp_path / ".claude" / "agents").mkdir(parents=True)
    (tmp_path / ".claude" / "agents" / "agent_team__interview_manager.md").write_text("# i\n", encoding="utf-8")
    (tmp_path / ".claude" / "agents" / "agent_team__research_manager.md").write_text("# r\n", encoding="utf-8")
    skills_dir = tmp_path / ".claude" / "skills" / "agent_team"
    skills_dir.mkdir(parents=True)
    (skills_dir / "SKILL.md").write_text("# skill\n", encoding="utf-8")
    spec_dir = tmp_path / "specs" / "development" / "spec_driven"
    (spec_dir / "user_input").mkdir(parents=True)
    (spec_dir / "user_input" / "raw_prompt.md").write_text("# raw\n", encoding="utf-8")
    (spec_dir / "user_input" / "revised_prompt.md").write_text("# revised\n", encoding="utf-8")
    (spec_dir / "interview").mkdir()
    (spec_dir / "interview" / "qa.md").write_text("# qa\n", encoding="utf-8")
    (spec_dir / "findings").mkdir()
    (spec_dir / "findings" / "dossier.md").write_text("# dossier\n", encoding="utf-8")
    (spec_dir / "findings" / "angle-a.md").write_text("# a\n", encoding="utf-8")
    (spec_dir / "final_specs").mkdir()
    (spec_dir / "final_specs" / "spec.md").write_text("# spec\n", encoding="utf-8")
    val_dir = spec_dir / "validation"
    val_dir.mkdir()
    (val_dir / "strategy.md").write_text("# strategy\n", encoding="utf-8")
    (val_dir / "acceptance_criteria.md").write_text("# ac\n", encoding="utf-8")
    (val_dir / "bdd_scenarios.md").write_text("# bdd\n", encoding="utf-8")
    (val_dir / "extra.md").write_text("# extra\n", encoding="utf-8")
    return tmp_path
