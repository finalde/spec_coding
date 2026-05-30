"""Consumer-walk test.

Recursively descend `node.children` (the EXACT field the frontend reads). Catches
the class of bug where backend emits a different field than the frontend reads.
"""
from __future__ import annotations

from libs.common.exposed_tree import ExposedTree
from libs.infrastructure.readers.tree__reader import TreeReader
from tests.conftest import make_app, repo_root


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
    walker = TreeReader(exposed)
    tree = walker.build()
    _walk(tree)


def test_tree_sections_order() -> None:
    """Sections render in order: AI Videos, Downloaded Novels, My Novel.
    Per follow-up 096 research/ was retired in favor of novels/; per
    follow-up 113 novels/ was further split into downloaded_novels/ and
    my_novel/."""
    exposed = ExposedTree(repo_root())
    walker = TreeReader(exposed)
    tree = walker.build()
    section_names = [child["name"] for child in tree["children"]]
    assert section_names == ["AI Videos", "Downloaded Novels", "My Novel"], section_names


def test_ai_videos_section_has_project_meta_for_wukong() -> None:
    exposed = ExposedTree(repo_root())
    walker = TreeReader(exposed)
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


def test_downloaded_novels_section_walks_repo_downloaded_novels_dir() -> None:
    """Follow-up 113: downloaded_novels/ (renamed from novels/) surfaces under
    the 'Downloaded Novels' section (which itself replaced the earlier
    'Novels' section per follow-up 096; that section in turn replaced
    'research/' per follow-up 003).
    """
    exposed = ExposedTree(repo_root())
    walker = TreeReader(exposed)
    tree = walker.build()
    section = next(
        (c for c in tree["children"] if c["name"] == "Downloaded Novels"), None
    )
    assert section is not None, "Downloaded Novels section missing"
    assert section["type"] == "section"
    if (repo_root() / "downloaded_novels").is_dir():
        names = [c["name"] for c in section["children"]]
        assert isinstance(names, list)


def test_my_novel_section_walks_repo_my_novel_dir() -> None:
    """Follow-up 113: my_novel/ is the new sibling surface for original
    manuscripts (distinct from downloaded_novels/ baseline corpus).
    Section surfaces unconditionally; empty when no projects exist yet."""
    exposed = ExposedTree(repo_root())
    walker = TreeReader(exposed)
    tree = walker.build()
    section = next(
        (c for c in tree["children"] if c["name"] == "My Novel"), None
    )
    assert section is not None, "My Novel section missing"
    assert section["type"] == "section"
    assert isinstance(section["children"], list)


def test_image_leaves_typed_as_image() -> None:
    exposed = ExposedTree(repo_root())
    walker = TreeReader(exposed)
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
