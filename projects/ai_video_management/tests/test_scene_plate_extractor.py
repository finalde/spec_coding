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
