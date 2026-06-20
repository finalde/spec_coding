"""ScenePlateExtractor: per-direction bg-plate extraction from a scene
walk-through mp4. Tests cover direction→timepoint routing, bg-folder
discovery, and source validation — without invoking ffmpeg (the
direction/discovery/validation logic is the part with branching).
"""
from __future__ import annotations

from pathlib import Path

import pytest

from libs.common.exposed_tree import ExposedTree
from libs.common.safe_resolve import SafeResolver
from libs.domain.errors.frame__error import (
    FrameExtractFailedError,
    NotVideoError,
    VideoNotFoundError,
)
from libs.infrastructure.writers.scene_plate__writer import ScenePlateExtractor


def _ext(root: Path) -> ScenePlateExtractor:
    return ScenePlateExtractor(ExposedTree(root), SafeResolver(root))


def test_route_direction_canonical_timepoints() -> None:
    f = ScenePlateExtractor._route_direction
    assert f("bg1_朝北_家主高座") == ("北", 1.5)
    assert f("bg2_朝东_东列长案") == ("东", 4.5)
    assert f("bg3_朝南_厅门逆光") == ("南", 7.5)
    assert f("bg4_朝西_西列长案") == ("西", 10.5)
    assert f("bg5_中_中轴俯瞰") == ("中", 13.5)
    # legacy/alt naming for the 5th overhead/center dwell still routes to 中
    assert f("bg5_高位俯瞰_中轴全景") == ("中", 13.5)
    # non-direction folder → unrouted
    assert f("bg9_unknown") is None


def test_parse_scene_timepoints_reads_index_table(tmp_path: Path) -> None:
    """The per-scene 截帧时点 column is the source of truth — the dwell order
    (and thus direction→second) is authored per scene, so the parser must read
    each plate's second from the table, not the global compass map."""
    scene = tmp_path / "repo" / "ai_videos" / "d" / "scenes" / "s1"
    scene.mkdir(parents=True, exist_ok=True)
    (scene / "s1.md").write_text(
        "# s1\n\n"
        "# 背景图系统 index（方位 ↔ 视频秒段 ↔ 截帧时点 ↔ plate folder）\n\n"
        "| plate_id | 方位 | 视频秒段 | 截帧时点 | plate folder |\n"
        "|---|---|---|---|---|\n"
        "| `bg1_朝北_主位` | 朝北 | #1 建场 0.0-1.0s | 1.5s | `bg1_朝北_主位/` |\n"
        "| `bg4_朝西_西窗` | 朝西 | #2 西窗 4.0-4.8s | 4.5s | `bg4_朝西_西窗/` |\n"
        "| `bg5_高位俯瞰` | 俯瞰 | #3 俯瞰 7.5-8.3s | 7.5s | `bg5_高位俯瞰/` |\n"
        "| `bg2_朝南_厅门` / `bg1` 中景 | 中景 | #4 中景 11.0-11.8s | 10.5s | `bg2_朝南_厅门/` |\n"
        "| `bg3_朝东_列柱` / `bg6_座前_虚化` | 朝东 | #5 长焦 14.2-15.0s | 13.5s | `bg3/` `bg6/` |\n",
        encoding="utf-8",
    )
    ext = _ext(tmp_path / "repo")
    m = ext._parse_scene_timepoints(scene)
    # direction order is 北→西→俯瞰→南(中景)→东 — NOT the compass default order
    assert m["bg1_朝北_主位"] == 1.5
    assert m["bg4_朝西_西窗"] == 4.5
    assert m["bg5_高位俯瞰"] == 7.5
    assert m["bg2_朝南_厅门"] == 10.5
    assert m["bg3_朝东_列柱"] == 13.5
    assert m["bg6_座前_虚化"] == 13.5
    # bare `bg1` name-dropped in row 4 prose must NOT override row 1's 1.5s
    assert m["bg1_朝北_主位"] == 1.5


def test_parse_scene_timepoints_missing_md_returns_empty(tmp_path: Path) -> None:
    scene = tmp_path / "repo" / "ai_videos" / "d" / "scenes" / "s1"
    scene.mkdir(parents=True, exist_ok=True)
    assert _ext(tmp_path / "repo")._parse_scene_timepoints(scene) == {}


def test_direction_segment_extracts_方位() -> None:
    f = ScenePlateExtractor._direction_segment
    assert f("bg6_座前_虚化背景") == "座前"
    assert f("bg1_朝北_高座主位") == "朝北"


def test_find_bg_dirs_only_bg_prefixed(tmp_path: Path) -> None:
    scene = tmp_path / "repo" / "ai_videos" / "d" / "scenes" / "s1"
    for name in ["bg1_朝北_x", "bg2_朝东_x", "frames", "notbg", "ref_images"]:
        (scene / name).mkdir(parents=True, exist_ok=True)
    (scene / "s1.mp4").write_bytes(b"x")
    ext = _ext(tmp_path / "repo")
    dirs = ext._find_bg_dirs(scene)
    assert [d.name for d in dirs] == ["bg1_朝北_x", "bg2_朝东_x"]


def test_extract_no_bg_dirs_raises(tmp_path: Path) -> None:
    scene = tmp_path / "repo" / "ai_videos" / "d" / "scenes" / "s1"
    scene.mkdir(parents=True, exist_ok=True)
    mp4 = scene / "s1.mp4"
    mp4.write_bytes(b"not-a-real-video")  # validation only checks ext + is_file
    ext = _ext(tmp_path / "repo")
    with pytest.raises(FrameExtractFailedError):
        ext.extract("ai_videos/d/scenes/s1/s1.mp4")


def test_validate_rejects_non_video(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    (root / "ai_videos").mkdir(parents=True, exist_ok=True)
    (root / "ai_videos" / "x.txt").write_text("hi", encoding="utf-8")
    ext = _ext(root)
    with pytest.raises(NotVideoError):
        ext.extract("ai_videos/x.txt")


def test_validate_rejects_missing(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    (root / "ai_videos").mkdir(parents=True, exist_ok=True)
    ext = _ext(root)
    with pytest.raises(VideoNotFoundError):
        ext.extract("ai_videos/nope.mp4")
