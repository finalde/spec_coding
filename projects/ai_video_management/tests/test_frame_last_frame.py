"""FrameExtractor.extract_last_frame: the cross-shot continuity-frame source
(ai_video.md 2026-06-21 跨镜首帧承接). A 承接 shot's first frame = the previous
shot's rendered LAST frame; this extracts it to `{shot}/{shot}_lastframe.png`
at the shot ROOT.

The shot-folder resolution + source validation branch without ffmpeg; one real
(tiny) ffmpeg run asserts a valid PNG lands at the shot root.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import imageio_ffmpeg
import pytest

from libs.common.exposed_tree import ExposedTree
from libs.common.safe_resolve import SafeResolver
from libs.domain.errors.frame__error import NotVideoError, VideoNotFoundError
from libs.infrastructure.writers.frame__writer import FrameExtractor

_PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def _ext(root: Path) -> FrameExtractor:
    return FrameExtractor(ExposedTree(root), SafeResolver(root))


def _make_shot_video(
    tmp_path: Path, *, in_renders: bool = True, shot: str = "shot01"
) -> tuple[Path, str]:
    root = tmp_path / "repo"
    shot_dir = root / "ai_videos" / "td" / "episodes" / "ep01" / "shots" / shot
    folder = shot_dir / "renders" if in_renders else shot_dir
    folder.mkdir(parents=True, exist_ok=True)
    mp4 = folder / "take.mp4"
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run(
        [ffmpeg, "-y", "-f", "lavfi", "-i",
         "testsrc=duration=2:size=320x240:rate=10",
         "-pix_fmt", "yuv420p", str(mp4)],
        capture_output=True, check=True,
    )
    return root, str(mp4.relative_to(root).as_posix())


def test_shot_folder_resolves_to_shot_root(tmp_path: Path) -> None:
    ext = _ext(tmp_path)
    # source inside renders/ → shot root
    src = tmp_path / "shots" / "shot07" / "renders" / "take.mp4"
    assert ext._shot_folder(src).name == "shot07"
    # source already at shot root → same
    src2 = tmp_path / "shots" / "shot07" / "shot07.mp4"
    assert ext._shot_folder(src2).name == "shot07"
    # non-shot video → falls back to its own folder
    src3 = tmp_path / "scenes" / "s1" / "walk.mp4"
    assert ext._shot_folder(src3).name == "s1"


def test_extract_last_frame_writes_png_at_shot_root(tmp_path: Path) -> None:
    root, rel = _make_shot_video(tmp_path, in_renders=True)
    result = _ext(root).extract_last_frame(rel)
    assert result.out_rel.endswith("shots/shot01/shot01_lastframe.png")
    out = root / result.out_rel
    assert out.is_file()
    assert out.read_bytes()[:8] == _PNG_MAGIC
    # original render untouched
    assert (root / rel).is_file()


def test_last_frame_copied_into_next_shot_as_firstframe(tmp_path: Path) -> None:
    root, rel = _make_shot_video(tmp_path, in_renders=True, shot="shot01")
    # the next shot must already exist for the copy to land
    (root / "ai_videos" / "td" / "episodes" / "ep01" / "shots" / "shot02").mkdir()
    result = _ext(root).extract_last_frame(rel)
    assert result.first_frame_rel is not None
    assert result.first_frame_rel.endswith("shots/shot02/shot02_firstframe.png")
    ff = root / result.first_frame_rel
    assert ff.read_bytes() == (root / result.out_rel).read_bytes()  # identical copy


def test_no_next_shot_skips_firstframe_copy(tmp_path: Path) -> None:
    # only shot01 exists → nothing to copy into
    root, rel = _make_shot_video(tmp_path, in_renders=True, shot="shot01")
    result = _ext(root).extract_last_frame(rel)
    assert result.first_frame_rel is None


def test_firstframe_copy_resolves_zero_padding(tmp_path: Path) -> None:
    # shot09 → shot10 (numeric match, not string prefix)
    root, rel = _make_shot_video(tmp_path, in_renders=False, shot="shot09")
    (root / "ai_videos" / "td" / "episodes" / "ep01" / "shots" / "shot10").mkdir()
    result = _ext(root).extract_last_frame(rel)
    assert result.first_frame_rel is not None
    assert result.first_frame_rel.endswith("shots/shot10/shot10_firstframe.png")


def test_extract_last_frame_from_shot_root_source(tmp_path: Path) -> None:
    root, rel = _make_shot_video(tmp_path, in_renders=False)
    result = _ext(root).extract_last_frame(rel)
    assert result.out_rel.endswith("shots/shot01/shot01_lastframe.png")
    assert (root / result.out_rel).read_bytes()[:8] == _PNG_MAGIC


def test_extract_last_frame_not_a_video_raises(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    (root / "ai_videos" / "td").mkdir(parents=True)
    (root / "ai_videos" / "td" / "note.md").write_text("x", encoding="utf-8")
    with pytest.raises(NotVideoError):
        _ext(root).extract_last_frame("ai_videos/td/note.md")


def test_extract_last_frame_missing_file_raises(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    (root / "ai_videos").mkdir(parents=True)
    with pytest.raises(VideoNotFoundError):
        _ext(root).extract_last_frame("ai_videos/td/episodes/ep01/shots/shot01/renders/missing.mp4")
