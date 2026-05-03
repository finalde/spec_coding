"""
Group 4 — regen_prompt (FR-10, FR-11, FR-12, AC-13..AC-17).

Most-load-bearing assertions:
- 4.1/4.2 first-line + autonomous imperative line VERBATIM
- 4.3 INTERACTIVE header has no imperative
- 4.5 follow-ups numerical order
- 4.6 promoted.md inlined under "### Pinned items (MUST survive regeneration)"
- 4.7 size policy 50KB-warn / 1MB-413 (warn-don't-truncate)
- 4.8 read-zero sentence in Constraints section
"""

from __future__ import annotations

import pytest

from libs.regen_prompt import (
    AUTONOMOUS_IMPERATIVE,
    HARD_LIMIT,
    READ_ZERO_SENTENCE,
    RegenInputError,
    RegenPromptAssembler,
    TooLargePromptError,
    WARN_THRESHOLD,
)


def _assemble(repo_root, **kwargs):
    asm = RegenPromptAssembler(repo_root=repo_root.path)
    defaults = dict(
        project_type="development",
        project_name="spec_driven",
        stage_ids=["interview"],
        modules={},
        autonomous=False,
    )
    defaults.update(kwargs)
    return asm.assemble(**defaults)


def test_first_line_autonomous_header(repo_root):
    r = _assemble(repo_root, autonomous=True)
    first_line = r.prompt.split("\n", 1)[0]
    assert first_line == "# EXECUTION MODE: AUTONOMOUS"


def test_autonomous_imperative_line_verbatim(repo_root):
    r = _assemble(repo_root, autonomous=True)
    assert AUTONOMOUS_IMPERATIVE in r.prompt
    assert (
        "Do not call AskUserQuestion. For anything unclear, use your best judgment, "
        "record the choice inline in the artifact, and keep going. "
        "Produce every requested artifact below in this single turn before stopping."
        in r.prompt
    )


def test_interactive_header_no_imperative(repo_root):
    r = _assemble(repo_root, autonomous=False)
    first_line = r.prompt.split("\n", 1)[0]
    assert first_line == "# EXECUTION MODE: INTERACTIVE"
    assert "Do not call AskUserQuestion" not in r.prompt


def test_inlines_revised_prompt(repo_root):
    r = _assemble(repo_root)
    assert "## Revised prompt" in r.prompt
    assert "spec_driven" in r.prompt


def test_follow_ups_in_numerical_order(repo_root):
    r = _assemble(repo_root)
    assert r.follow_ups_count >= 0
    if r.follow_ups_count >= 2:
        section = r.prompt.split("## Follow-ups", 1)[1].split("## Stage:", 1)[0]
        last_idx = -1
        for line in section.splitlines():
            if line.startswith("- `user_input/follow_ups/"):
                name = line.split("/")[-1].rstrip("`")
                num = int(name.split("-", 1)[0])
                assert num >= last_idx
                last_idx = num


def test_promoted_md_inlined_under_pinned_items(repo_root):
    r = _assemble(repo_root, stage_ids=["interview"])
    assert "### Pinned items (MUST survive regeneration)" in r.prompt
    assert "All discovered (Recommended)" in r.prompt


def test_constraints_section_includes_read_zero(repo_root):
    r = _assemble(repo_root)
    assert "### Constraints" in r.prompt
    assert READ_ZERO_SENTENCE in r.prompt
    for marker in ("regen.delete.planned", "regen.delete.completed", "regen.write.completed"):
        assert marker in r.prompt
    for surface in ("CLAUDE.md", "specs/{type}/{name}/", ".audit/adhoc_agents/"):
        assert surface in r.prompt
    assert "parent-direct" in r.prompt.lower()


def test_response_shape(repo_root):
    r = _assemble(repo_root)
    d = r.to_dict()
    assert set(d.keys()) == {"prompt", "warning", "selected_stages_count", "follow_ups_count", "autonomous", "bytes"}
    assert d["bytes"] == len(d["prompt"].encode("utf-8"))


def test_size_policy_warn_threshold(repo_root):
    r = _assemble(repo_root, stage_ids=["interview"])
    if r.bytes <= WARN_THRESHOLD:
        assert r.warning is None
    else:
        assert r.warning is not None


def test_size_policy_full_pipeline_might_warn(repo_root):
    r = _assemble(repo_root, stage_ids=["intake", "interview", "research", "spec", "validation", "execution"])
    if r.bytes > WARN_THRESHOLD:
        assert r.warning is not None
        assert r.bytes == len(r.prompt.encode("utf-8"))


def test_unknown_stage_id_rejected(repo_root):
    with pytest.raises(RegenInputError):
        _assemble(repo_root, stage_ids=["bogus_stage"])


def test_empty_stages_rejected(repo_root):
    with pytest.raises(RegenInputError):
        _assemble(repo_root, stage_ids=[])


def test_bytes_match_prompt_length_no_truncation(repo_root):
    r = _assemble(repo_root, stage_ids=["interview", "research", "validation"])
    assert r.bytes == len(r.prompt.encode("utf-8"))


def test_too_large_raises(repo_root, monkeypatch):
    """When the assembled prompt would exceed 1 MB, raise TooLargePromptError."""
    from libs import regen_prompt

    monkeypatch.setattr(regen_prompt, "HARD_LIMIT", 1024)
    asm = RegenPromptAssembler(repo_root=repo_root.path)
    with pytest.raises(TooLargePromptError):
        asm.assemble(
            project_type="development",
            project_name="spec_driven",
            stage_ids=["interview", "research"],
            modules={},
            autonomous=False,
        )


def test_walks_each_selected_stage_with_invocation_and_modules(repo_root):
    r = _assemble(repo_root, stage_ids=["interview", "validation"])
    assert "## Stage: interview" in r.prompt
    assert "## Stage: validation strategy" in r.prompt
    assert "_Invocation_:" in r.prompt
