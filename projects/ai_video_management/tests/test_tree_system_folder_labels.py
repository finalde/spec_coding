"""The shared library system-folders under `ai_videos/` carry Chinese display
labels (they have no README/concept H1 to derive a title from): `_actors` →
演员库, `_bgm` → 背景音乐库. The UI renders these as their own library pages."""
from __future__ import annotations

from pathlib import Path

from libs.common.exposed_tree import ExposedTree
from libs.infrastructure.readers.tree__reader import TreeReader


def _ai_videos_children(root: Path) -> dict[str, dict]:
    tree = TreeReader(ExposedTree(root)).build()
    section = next(s for s in tree["children"] if s["name"] == "AI Videos")
    return {c["name"]: c for c in section["children"]}


def test_actors_and_bgm_have_chinese_library_labels(tmp_path: Path) -> None:
    (tmp_path / "ai_videos" / "_actors" / "actor_0001").mkdir(parents=True)
    (tmp_path / "ai_videos" / "_bgm" / "warm").mkdir(parents=True)
    by_name = _ai_videos_children(tmp_path)
    assert by_name["_actors"]["display_name"] == "演员库"
    assert by_name["_bgm"]["display_name"] == "背景音乐库"


def test_drama_folder_label_is_untouched(tmp_path: Path) -> None:
    drama = tmp_path / "ai_videos" / "td"
    drama.mkdir(parents=True)
    (drama / "README.md").write_text("# 《测试剧》— pilot", encoding="utf-8")
    by_name = _ai_videos_children(tmp_path)
    # system-folder map must not shadow a real drama's own H1-derived title
    assert by_name["td"].get("display_name") == "测试剧"
