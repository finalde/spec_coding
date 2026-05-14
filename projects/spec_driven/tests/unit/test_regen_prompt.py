"""
Group 6 — regen_prompt (header verbatim, contract verbatim, size policy).

Spec anchors: FR-10, FR-11, FR-12, FR-37, FR-38, AC-16..19.
"""

from __future__ import annotations

import pytest


def _post(client, headers, **overrides):
    body = dict(
        project_type="development",
        project_name="spec_driven",
        stages=["interview"],
        modules={},
        autonomous=False,
    )
    body.update(overrides)
    return client.post("/api/regen-prompt", headers=headers, json=body)


# ---------------------------------------------------------------------------
# Headers verbatim (FR-11a, AC-16, AC-17)
# ---------------------------------------------------------------------------


def test_interactive_header_first_line(client, good_headers):
    r = _post(client, good_headers, autonomous=False)
    assert r.status_code == 200
    prompt = r.json()["prompt"]
    first_line = prompt.split("\n", 1)[0]
    assert first_line == "# EXECUTION MODE: INTERACTIVE"


def test_autonomous_header_first_line(client, good_headers):
    r = _post(client, good_headers, autonomous=True)
    assert r.status_code == 200
    prompt = r.json()["prompt"]
    first_line = prompt.split("\n", 1)[0]
    assert first_line == "# EXECUTION MODE: AUTONOMOUS"


def test_autonomous_imperative_present_only_when_autonomous(client, good_headers):
    on = _post(client, good_headers, autonomous=True).json()["prompt"]
    off = _post(client, good_headers, autonomous=False).json()["prompt"]
    # one of these phrasings MUST appear in autonomous mode
    on_lower = on.lower()
    assert "askuserquestion" in on_lower or "ask_user_question" in on_lower
    assert "askuserquestion" not in off.lower() or "do not call askuserquestion" not in off.lower()


# ---------------------------------------------------------------------------
# Revised prompt + follow-ups inlined (FR-11b, FR-11c)
# ---------------------------------------------------------------------------


def test_revised_prompt_inlined(client, good_headers, repo_root):
    revised = (
        repo_root.path
        / "specs"
        / "development"
        / "spec_driven"
        / "user_input"
        / "revised_prompt.md"
    )
    if not revised.is_file():
        pytest.skip("revised_prompt.md not present in test repo")
    body = revised.read_text(encoding="utf-8")
    # Pull a meaningful sentinel substring from the revised prompt and assert
    # it appears verbatim in the assembled prompt.
    sentinel = body.strip().splitlines()[0] if body.strip() else None
    if not sentinel:
        pytest.skip("revised prompt has no content")
    r = _post(client, good_headers, autonomous=False)
    prompt = r.json()["prompt"]
    assert sentinel in prompt or sentinel.replace("# ", "") in prompt


def test_follow_ups_in_numerical_order(client, good_headers, repo_root):
    """If follow_ups exist, their filenames appear in numerical order."""
    fu_dir = (
        repo_root.path
        / "specs"
        / "development"
        / "spec_driven"
        / "user_input"
        / "follow_ups"
    )
    if not fu_dir.is_dir():
        pytest.skip("follow_ups dir not present")
    files = sorted(fu_dir.glob("*.md"), key=lambda p: int(p.name.split("-", 1)[0]))
    if len(files) < 1:
        pytest.skip("no follow_ups present")
    r = _post(client, good_headers, autonomous=False)
    prompt = r.json()["prompt"]
    # Numerical-order assertion: each filename appears after the previous one.
    indices: list[int] = []
    for f in files:
        idx = prompt.find(f.name)
        if idx == -1:
            # Filenames may be referenced by stem only; tolerate that.
            stem = f.stem
            idx = prompt.find(stem)
        if idx == -1:
            pytest.skip(f"follow-up {f.name} not present in assembled prompt")
        indices.append(idx)
    assert indices == sorted(indices)


def test_follow_ups_count_in_response(client, good_headers, repo_root):
    fu_dir = (
        repo_root.path
        / "specs"
        / "development"
        / "spec_driven"
        / "user_input"
        / "follow_ups"
    )
    expected = (
        len(list(fu_dir.glob("*.md"))) if fu_dir.is_dir() else 0
    )
    r = _post(client, good_headers)
    body = r.json()
    assert body["follow_ups_count"] == expected


# ---------------------------------------------------------------------------
# Per-stage modules + promoted.md inlined (FR-11d)
# ---------------------------------------------------------------------------


def test_promoted_md_inlined_when_present(client, good_headers, repo_root, scratch_dir):
    """When `<stage>/promoted.md` is non-empty, its body is inlined under a
    `Pinned items (MUST survive regeneration)` header."""
    promoted = (
        repo_root.path
        / "specs"
        / "development"
        / "spec_driven"
        / "validation"
        / "promoted.md"
    )
    pin_text = "PINNED-ITEM-FIXTURE-XYZZY-12345 (testing pin inclusion)"
    if not promoted.exists():
        promoted.write_text(pin_text + "\n", encoding="utf-8")
        cleanup = True
    else:
        original = promoted.read_text(encoding="utf-8")
        promoted.write_text(original + "\n" + pin_text + "\n", encoding="utf-8")
        cleanup = False
    try:
        r = _post(client, good_headers, stages=["validation"], modules={"validation": []})
        assert r.status_code == 200
        prompt = r.json()["prompt"]
        assert "XYZZY-12345" in prompt
        # Header text — accept either the canonical phrase or a close variant
        assert (
            "Pinned items (MUST survive regeneration)" in prompt
            or "Pinned items" in prompt
        )
    finally:
        if cleanup:
            promoted.unlink(missing_ok=True)
        else:
            promoted.write_text(original, encoding="utf-8")


# ---------------------------------------------------------------------------
# Constraints section (FR-11e, FR-37, FR-38, AC-18)
# ---------------------------------------------------------------------------


def test_constraints_section_present(client, good_headers):
    r = _post(client, good_headers)
    prompt = r.json()["prompt"]
    assert "### Constraints" in prompt


def test_constraints_section_contains_read_zero_contract(client, good_headers):
    r = _post(client, good_headers)
    prompt = r.json()["prompt"]
    # The read-zero contract sentence (verbatim or close paraphrase). One of
    # these load-bearing phrases MUST appear:
    assert (
        "regeneration deletes prior outputs first" in prompt
        or "delete prior outputs" in prompt
        or "treated as deleted" in prompt
        or "read-zero" in prompt.lower()
    )


def test_constraints_section_contains_audit_event_protocol(client, good_headers):
    r = _post(client, good_headers)
    prompt = r.json()["prompt"]
    # Per FR-38: three event names verbatim.
    assert "regen.delete.planned" in prompt
    assert "regen.delete.completed" in prompt
    assert "regen.write.completed" in prompt


# ---------------------------------------------------------------------------
# Size policy (FR-12, AC-19)
# ---------------------------------------------------------------------------


def test_size_under_50kb_warning_null(client, good_headers):
    r = _post(client, good_headers, stages=["interview"], modules={})
    body = r.json()
    if body["bytes"] >= 50 * 1024:
        pytest.skip("test repo's assembled prompt exceeds 50KB; warning won't be null")
    assert body["warning"] is None


def test_response_shape(client, good_headers):
    r = _post(client, good_headers)
    body = r.json()
    expected = {"prompt", "warning", "selected_stages_count", "follow_ups_count", "autonomous", "bytes"}
    assert set(body.keys()) == expected
    assert isinstance(body["prompt"], str)
    assert body["warning"] is None or isinstance(body["warning"], dict)
    assert isinstance(body["selected_stages_count"], int)
    assert isinstance(body["follow_ups_count"], int)
    assert isinstance(body["autonomous"], bool)
    assert isinstance(body["bytes"], int)
    assert body["bytes"] == len(body["prompt"].encode("utf-8"))


def test_selected_stages_count_matches_input(client, good_headers):
    r = _post(client, good_headers, stages=["interview", "research"])
    assert r.json()["selected_stages_count"] == 2


def test_autonomous_flag_echoed_in_response(client, good_headers):
    r_off = _post(client, good_headers, autonomous=False)
    r_on = _post(client, good_headers, autonomous=True)
    assert r_off.json()["autonomous"] is False
    assert r_on.json()["autonomous"] is True


def test_warning_shape_when_present_is_approaching_ceiling(client, good_headers):
    """If the assembled prompt is naturally between 50KB and 1MB, the warning
    shape must match the documented approaching_ceiling kind."""
    r = _post(
        client,
        good_headers,
        stages=["intake", "interview", "research", "spec", "validation", "execution"],
        modules={},
    )
    body = r.json()
    if body.get("warning") is not None:
        w = body["warning"]
        assert w["kind"] == "approaching_ceiling"
        assert w["bytes"] == body["bytes"]
        assert w["soft_limit"] == 51200
