"""
Group 6 — tree_walker (FR-1, FR-2).

The two regression tests from `spec_driven-20260502-clean` are the load-bearing
assertions in this file: 6.1 (uniform `children` field) and 6.2 (consumer-walk
parity with how the frontend Sidebar descends the tree).
"""

from __future__ import annotations

import pytest

from libs.exposed_tree import ExposedTree
from libs.tree_walker import TreeWalker, to_jsonable


@pytest.fixture()
def tree(repo_root):
    return TreeWalker(exposed=ExposedTree(root=repo_root.path)).walk()


def _walk(node):
    """Mirror the frontend Sidebar: descend `node['children']` literally.

    KeyError on a missing children field is the canonical regression failure.
    """
    yield node
    for c in node["children"]:
        yield from _walk(c)


def test_emits_children_field_uniformly(tree):
    """**[regression-2026-05-02-clean]** every non-leaf has a `children` array,
    and NO node has `projects` or `stages` or `task_type.projects` keys."""
    nodes = []
    for top in tree:
        nodes.extend(_walk(top))
    for n in nodes:
        assert "children" in n, f"missing 'children' on node {n.get('name')}"
        for forbidden in ("projects", "stages", "task_type"):
            assert forbidden not in n, f"forbidden field {forbidden!r} on node {n.get('name')}"


def test_tree_consumer_walk(tree):
    """**[regression-2026-05-02-clean]** walking via `node['children']` reaches
    every leaf — KeyError if any non-leaf is missing the field. Asserts the
    frontend's recursion contract on the backend output."""
    leaves: list[str] = []
    for top in tree:
        for n in _walk(top):
            if not n["children"] and n["type"] == "file":
                leaves.append(n["path"])
    assert "CLAUDE.md" in leaves
    assert any("specs/development/spec_driven/final_specs/spec.md" in p for p in leaves)
    assert any("specs/development/spec_driven/interview/qa.md" in p for p in leaves)


def test_top_level_sections(tree):
    names = [n["name"] for n in tree]
    assert names[0] == "Claude Settings & Shared Context"
    assert names[1] == "Projects"


def test_type_tags(tree):
    valid = {"section", "type", "project", "stage", "file"}
    for top in tree:
        for n in _walk(top):
            assert n["type"] in valid


def test_paths_are_forward_slash(tree):
    for top in tree:
        for n in _walk(top):
            assert "\\" not in n["path"], f"backslash in path {n['path']!r}"


def test_includes_required_paths(tree):
    leaves = []
    for top in tree:
        for n in _walk(top):
            if n["type"] == "file":
                leaves.append(n["path"])
    required_substrings = [
        "CLAUDE.md",
        ".claude/skills/agent_team/playbooks/interview.md",
        ".claude/skills/agent_team/playbooks/research.md",
        ".claude/skills/agent_team/playbooks/validation.md",
        ".claude/agent_refs/validation/general.md",
        "specs/development/spec_driven/final_specs/spec.md",
        "specs/development/spec_driven/interview/qa.md",
        "specs/development/spec_driven/validation/strategy.md",
        "specs/development/spec_driven/interview/promoted.md",
    ]
    for needle in required_substrings:
        assert any(needle in p for p in leaves), f"required path missing: {needle}"


def test_deterministic_within_a_directory(repo_root):
    a = TreeWalker(exposed=ExposedTree(root=repo_root.path)).walk()
    b = TreeWalker(exposed=ExposedTree(root=repo_root.path)).walk()
    assert [to_jsonable(n) for n in a] == [to_jsonable(n) for n in b]
