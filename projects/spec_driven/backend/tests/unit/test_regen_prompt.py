from __future__ import annotations

from pathlib import Path

import pytest

from libs.file_reader import FileReadError
from libs.regen_prompt import (
    AUTONOMOUS_IMPERATIVE,
    REGEN_HARD_CEILING_BYTES,
    REGEN_WARN_BYTES,
    build_regen_prompt,
    build_regen_prompt_result,
)


def test_under_warn_no_warning(fake_repo: Path) -> None:
    result = build_regen_prompt_result(
        project_type="development",
        project_name="spec_driven",
        stage_ids=["spec_compilation"],
        module_ids={"spec_compilation": ["spec"]},
        autonomous=False,
        repo_root=fake_repo,
    )
    assert result.warning is None


def test_autonomous_includes_verbatim_imperative(fake_repo: Path) -> None:
    prompt = build_regen_prompt(
        project_type="development",
        project_name="spec_driven",
        stage_ids=["spec_compilation"],
        module_ids={"spec_compilation": ["spec"]},
        autonomous=True,
        repo_root=fake_repo,
    )
    lines = [ln for ln in prompt.splitlines() if ln.strip()]
    assert lines[0] == "# EXECUTION MODE: AUTONOMOUS"
    assert lines[1] == AUTONOMOUS_IMPERATIVE


def test_interactive_no_imperative(fake_repo: Path) -> None:
    prompt = build_regen_prompt(
        project_type="development",
        project_name="spec_driven",
        stage_ids=["spec_compilation"],
        module_ids={"spec_compilation": ["spec"]},
        autonomous=False,
        repo_root=fake_repo,
    )
    lines = [ln for ln in prompt.splitlines() if ln.strip()]
    assert lines[0] == "# EXECUTION MODE: INTERACTIVE"
    assert AUTONOMOUS_IMPERATIVE not in prompt


def test_above_warn_emits_warning_full_prompt(fake_repo: Path) -> None:
    revised = fake_repo / "specs" / "development" / "spec_driven" / "user_input" / "revised_prompt.md"
    revised.write_text("X" * (REGEN_WARN_BYTES + 5_000), encoding="utf-8")
    result = build_regen_prompt_result(
        project_type="development",
        project_name="spec_driven",
        stage_ids=["spec_compilation"],
        module_ids={"spec_compilation": ["spec"]},
        autonomous=False,
        repo_root=fake_repo,
    )
    assert result.warning is not None
    assert len(result.prompt.encode("utf-8")) > REGEN_WARN_BYTES


def test_above_hard_ceiling_raises_413(fake_repo: Path) -> None:
    revised = fake_repo / "specs" / "development" / "spec_driven" / "user_input" / "revised_prompt.md"
    revised.write_text("X" * (REGEN_HARD_CEILING_BYTES + 5_000), encoding="utf-8")
    with pytest.raises(FileReadError) as ei:
        build_regen_prompt_result(
            project_type="development",
            project_name="spec_driven",
            stage_ids=["spec_compilation"],
            module_ids={"spec_compilation": ["spec"]},
            autonomous=False,
            repo_root=fake_repo,
        )
    assert ei.value.status == 413
    assert ei.value.kind == "too_large"


def test_breakdown_counts(fake_repo: Path) -> None:
    fu_dir = fake_repo / "specs" / "development" / "spec_driven" / "user_input" / "follow_ups"
    fu_dir.mkdir(parents=True)
    (fu_dir / "001-foo.md").write_text("foo", encoding="utf-8")
    (fu_dir / "002-bar.md").write_text("bar", encoding="utf-8")
    result = build_regen_prompt_result(
        project_type="development",
        project_name="spec_driven",
        stage_ids=["spec_compilation", "validation_strategy"],
        module_ids={},
        autonomous=False,
        repo_root=fake_repo,
    )
    assert result.selected_stages_count == 2
    assert result.follow_ups_count == 2


def test_read_zero_constraint_in_prompt(fake_repo: Path) -> None:
    prompt = build_regen_prompt(
        project_type="development",
        project_name="spec_driven",
        stage_ids=["spec_compilation"],
        module_ids={},
        autonomous=False,
        repo_root=fake_repo,
    )
    assert "Read-zero" in prompt or "read-zero" in prompt
    assert "deletes prior outputs first" in prompt
    assert "reads only the inputs" in prompt
