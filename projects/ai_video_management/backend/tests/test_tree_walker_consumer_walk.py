"""Consumer-walk test.

Recursively descend `node.children` (the EXACT field the frontend reads). Catches
the class of bug where backend emits a different field than the frontend reads.
"""
from __future__ import annotations

from libs.exposed_tree import ExposedTree
from libs.tree_walker import TreeWalker
from tests.conftest import repo_root


def _walk(node: dict) -> None:
    assert "type" in node, f"node missing 'type': {node}"
    assert "name" in node, f"node missing 'name': {node}"
    assert "path" in node, f"node missing 'path': {node}"
    if node["type"] in ("section", "directory"):
        assert "children" in node, f"non-leaf missing 'children': {node!r}"
        for child in node["children"]:
            _walk(child)


def test_tree_consumer_walk() -> None:
    exposed = ExposedTree(repo_root())
    walker = TreeWalker(exposed)
    tree = walker.build()
    _walk(tree)


def test_tree_single_ai_videos_section() -> None:
    """Only AI Videos section renders."""
    exposed = ExposedTree(repo_root())
    walker = TreeWalker(exposed)
    tree = walker.build()
    section_names = [child["name"] for child in tree["children"]]
    assert section_names == ["AI Videos"], section_names


def test_ai_videos_section_has_project_meta_for_wukong() -> None:
    exposed = ExposedTree(repo_root())
    walker = TreeWalker(exposed)
    tree = walker.build()
    ai_videos_section = tree["children"][0]
    assert ai_videos_section["name"] == "AI Videos"
    wukong = next(
        (c for c in ai_videos_section["children"] if c["name"] == "wukong_juexing"),
        None,
    )
    assert wukong is not None, "wukong_juexing project missing from AI Videos section"
    assert "project_meta" in wukong
    assert wukong["project_meta"] is not None
    assert wukong["project_meta"]["sub_type"] == "short"


def test_no_other_sections_in_tree() -> None:
    """Sidebar emits exactly one section."""
    exposed = ExposedTree(repo_root())
    walker = TreeWalker(exposed)
    tree = walker.build()
    section_names = [child["name"] for child in tree["children"]]
    assert section_names == ["AI Videos"]
    assert len(section_names) == 1


def test_image_leaves_typed_as_image() -> None:
    exposed = ExposedTree(repo_root())
    walker = TreeWalker(exposed)
    tree = walker.build()

    def collect_images(node: dict, out: list) -> None:
        if node.get("type") == "image":
            out.append(node)
        for c in node.get("children", []):
            collect_images(c, out)

    images: list = []
    collect_images(tree, images)
    for img in images:
        assert img["name"].lower().endswith((".png", ".jpg")), f"non-image typed as image: {img}"
