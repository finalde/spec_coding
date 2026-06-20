"""Chinese display_name for staged-pipeline drama + scene folders (tree__reader).

Drama folders are pinyin/English on disk; their Chinese title now lives in
`1_立项/concept.md` (no top-level README). Scene folders are pinyin with the
Chinese name in `{name}.md`'s H1 `（中文）`. Both must surface as `display_name`
so the sidebar shows Chinese.
"""
from __future__ import annotations

from pathlib import Path

from libs.infrastructure.readers.tree__reader import TreeReader


class _FakeExposed:
    def __init__(self, root: Path) -> None:
        self.root = root

    def excluded_dirs(self):
        return set()


def _reader(root: Path) -> TreeReader:
    return TreeReader(_FakeExposed(root))


def test_drama_zh_title_from_concept(tmp_path: Path) -> None:
    proj = tmp_path / "ai_videos" / "wushen_juexing"
    (proj / "1_立项").mkdir(parents=True)
    (proj / "1_立项" / "concept.md").write_text("# 立项策划单 · 武神觉醒\n", encoding="utf-8")
    assert _reader(tmp_path)._project_zh_title(proj) == "武神觉醒"


def test_drama_zh_title_readme_still_wins(tmp_path: Path) -> None:
    proj = tmp_path / "ai_videos" / "foo"
    proj.mkdir(parents=True)
    (proj / "README.md").write_text("# 《重生之总裁夫人》— AI 视频项目\n", encoding="utf-8")
    assert _reader(tmp_path)._project_zh_title(proj) == "重生之总裁夫人"


def test_scene_zh_label_from_paren(tmp_path: Path) -> None:
    scene = tmp_path / "ai_videos" / "d" / "2_世界观人设" / "scenes" / "zhenbei_wangfu_zhengting"
    scene.mkdir(parents=True)
    (scene / "zhenbei_wangfu_zhengting.md").write_text(
        "# zhenbei_wangfu_zhengting（镇北王府正厅）\n", encoding="utf-8"
    )
    assert _reader(tmp_path)._sidecar_zh_label(scene) == "镇北王府正厅"


def test_non_scene_dir_gets_no_label(tmp_path: Path) -> None:
    # a character folder (parent != scenes) must NOT pick up a label from its .md
    char = tmp_path / "ai_videos" / "d" / "2_世界观人设" / "characters" / "c1_裴知秋"
    char.mkdir(parents=True)
    (char / "c1_裴知秋.md").write_text("# 裴知秋 · 角色档\n", encoding="utf-8")
    assert _reader(tmp_path)._sidecar_zh_label(char) is None


def test_missing_sources_return_none(tmp_path: Path) -> None:
    proj = tmp_path / "ai_videos" / "empty"
    proj.mkdir(parents=True)
    assert _reader(tmp_path)._project_zh_title(proj) is None


def test_scene_main_md_leaf_has_zh_display(tmp_path: Path) -> None:
    # the scene's main sidecar .md leaf shows Chinese (name/path stay pinyin)
    scene = tmp_path / "ai_videos" / "d" / "2_世界观人设" / "scenes" / "jishi_changjie"
    scene.mkdir(parents=True)
    f = scene / "jishi_changjie.md"
    f.write_text("# jishi_changjie（集市长街）\n", encoding="utf-8")
    node = _reader(tmp_path)._leaf_for(f)
    assert node["display_name"] == "集市长街"
    assert node["name"] == "jishi_changjie.md"          # name stays pinyin (routing/open)
    assert node["path"].endswith("jishi_changjie.md")   # path stays pinyin


def test_scene_plate_md_leaf_no_display(tmp_path: Path) -> None:
    # a plate .md (parent.parent != scenes) must NOT get a scene display_name
    plate = tmp_path / "ai_videos" / "d" / "2_世界观人设" / "scenes" / "jishi_changjie" / "bg1_顺街_全景"
    plate.mkdir(parents=True)
    f = plate / "bg1_顺街_全景.md"
    f.write_text("# bg1_顺街_全景 · 集市长街 顺街全景\n", encoding="utf-8")
    assert "display_name" not in _reader(tmp_path)._leaf_for(f)


def test_shot_md_leaf_no_display(tmp_path: Path) -> None:
    # ordinary md leaves (not scene main sidecar) unchanged
    d = tmp_path / "ai_videos" / "d" / "5_6_分镜与prompt" / "episodes" / "ep02" / "shots" / "shot01"
    d.mkdir(parents=True)
    f = d / "shot01.md"
    f.write_text("# ep02 / shot01 · 离家上路\n", encoding="utf-8")
    assert "display_name" not in _reader(tmp_path)._leaf_for(f)
