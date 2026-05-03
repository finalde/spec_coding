"""
Group 4 — tree_walker uniform `children` field (consumer-walk regression).

Spec anchors: FR-3, FR-15. Severity: blocker on consumer-walk regression
(per agent_refs/validation/development.md move 2). The 2026-05-02-clean run
shipped a tree using `task_type.projects` / `project.stages` keys; this group
guards against a regression to that shape.

Test surface: GET /api/tree (HTTP) — implementation-agnostic. The frontend
sidebar walks `node.children` literally; these tests mirror that.
"""

from __future__ import annotations

from typing import Any, Iterator

import pytest


def _walk(node: dict[str, Any]) -> Iterator[dict[str, Any]]:
    yield node
    for c in node.get("children", []) or []:
        yield from _walk(c)


@pytest.fixture()
def tree(client) -> dict[str, Any]:
    r = client.get("/api/tree")
    assert r.status_code == 200
    return r.json()


def test_root_has_two_top_level_sections(tree):
    """FR-3 — top-level `Claude Settings & Shared Context` + `Specs`."""
    children = tree["children"]
    assert isinstance(children, list)
    assert len(children) >= 2
    names = [c["name"] for c in children]
    assert "Claude Settings & Shared Context" in names
    assert "Specs" in names


def test_tree_uniform_children(tree):
    """[regression-2026-05-02-clean / move 2] — every non-leaf has a
    `children` array, and NO node uses legacy keys."""
    for node in _walk(tree):
        if node.get("type") == "file":
            # leaf
            assert "children" not in node, (
                f"leaf node should not carry children: {node.get('path')!r}"
            )
        else:
            # non-leaf
            assert "children" in node, (
                f"non-leaf missing 'children' key: {node.get('name')!r}"
            )
            assert isinstance(node["children"], list)
        for forbidden in ("projects", "stages", "task_type", "files", "items"):
            assert forbidden not in node, (
                f"forbidden legacy field {forbidden!r} on node {node.get('name')!r}"
            )


def test_tree_consumer_walk(tree):
    """Descend ONLY via `node.children` and assert at least one leaf under
    each top-level section."""
    children = tree["children"]
    # locate the two canonical sections
    settings = next(c for c in children if c["name"] == "Claude Settings & Shared Context")
    specs = next(c for c in children if c["name"] == "Specs")

    settings_leaves = [n for n in _walk(settings) if n.get("type") == "file"]
    specs_leaves = [n for n in _walk(specs) if n.get("type") == "file"]
    assert len(settings_leaves) >= 1
    assert len(specs_leaves) >= 1


def test_consumer_walk_finds_known_files(tree):
    leaves = [n for n in _walk(tree) if n.get("type") == "file"]
    paths = [n["path"] for n in leaves]
    assert "CLAUDE.md" in paths
    assert any(
        "specs/development/spec_driven/final_specs/spec.md".replace("/", p[0]) in p
        for p in paths
        if "spec.md" in p
    ) or any(p.endswith("specs/development/spec_driven/final_specs/spec.md") for p in paths) or any(
        "spec_driven/final_specs/spec.md" in p for p in paths
    )


def test_no_path_uses_backslash(tree):
    for node in _walk(tree):
        path = node.get("path", "")
        assert "\\" not in path, f"backslash in path {path!r}"


def test_excludes_node_modules_and_audit(tree):
    for node in _walk(tree):
        path = node.get("path", "")
        assert "node_modules" not in path.split("/")
        assert ".audit" not in path.split("/")
        assert ".git" not in path.split("/")


def test_every_leaf_has_path_and_name(tree):
    for node in _walk(tree):
        if node.get("type") == "file":
            assert "name" in node
            assert "path" in node
            assert isinstance(node["path"], str)
            assert node["path"], "leaf path must be non-empty"


def test_every_non_leaf_children_is_list(tree):
    for node in _walk(tree):
        if node.get("type") != "file":
            assert isinstance(node.get("children"), list)


def test_dotclaude_subtree_includes_agent_refs_recursively(tree):
    """FR-2 — `.claude/agent_refs/**/*.md` recursive discovery."""
    leaves = [n["path"] for n in _walk(tree) if n.get("type") == "file"]
    # The test repo definitely has agent_refs general.md files for at least
    # one of the stages — assert at least one shows up.
    has_agent_refs = any("agent_refs" in p and p.endswith(".md") for p in leaves)
    assert has_agent_refs, "agent_refs/*.md must appear in tree response"
