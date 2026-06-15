"""Subtitle parse / ASS render (pure) + SubtitleBurner scaffold & burn.

The burn test does a real (tiny) ffmpeg encode using the imageio-ffmpeg
binary — fast on a 1s 320x240 clip — to prove the subtitles filter + libx264
pipeline produces a non-empty `*_subtitled.mp4`.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import imageio_ffmpeg
import pytest

from libs.common.exposed_tree import ExposedTree
from libs.common.safe_resolve import SafeResolver
from libs.domain.errors.subtitle__error import (
    EmptySubtitlesError,
    SubtitleAlreadyExistsError,
    SubtitleFileMissingError,
)
from libs.domain.value_objects.subtitle__valueobject import (
    cues_to_ass,
    parse_subtitles,
)
from libs.infrastructure.writers.subtitle__writer import SubtitleBurner


# --- pure value-object tests --------------------------------------------------

def test_parse_subtitles_valid_comments_decimals() -> None:
    text = (
        "# header comment\n"
        "```text\n"
        "0-3      老天爷，竟真让我重活一回。\n"
        "3-5.5    （内心）这一世，我裴知秋绝不再忍。\n"
        "\n"
        "5.5~8    你们，都等着。\n"
        "```\n"
    )
    cues = parse_subtitles(text)
    assert len(cues) == 3
    assert cues[0].start == 0 and cues[0].end == 3
    assert cues[1].end == 5.5
    assert cues[1].text == "（内心）这一世，我裴知秋绝不再忍。"
    assert cues[2].start == 5.5


def test_parse_subtitles_skips_malformed_and_inverted() -> None:
    text = "not a cue line\n5-3 倒置时间窗\n2-4\n2-4   ok\n"
    cues = parse_subtitles(text)
    assert len(cues) == 1
    assert cues[0].text == "ok"


def test_cues_to_ass_has_header_and_one_dialogue_per_cue() -> None:
    cues = parse_subtitles("0-3 甲\n3-5.5 乙\n")
    ass = cues_to_ass(cues)
    assert "[Script Info]" in ass
    assert "[V4+ Styles]" in ass
    assert "微软雅黑" in ass
    dialogues = [ln for ln in ass.splitlines() if ln.startswith("Dialogue:")]
    assert len(dialogues) == 2
    assert "0:00:00.00" in dialogues[0]
    assert "0:00:03.00" in dialogues[0]
    assert "0:00:05.50" in dialogues[1]


# --- writer tests -------------------------------------------------------------

def _shot_render(root: Path) -> tuple[Path, str]:
    """Create a 1s mp4 take under a real shot folder; return (path, rel)."""
    renders = root / "ai_videos" / "td" / "episodes" / "ep01" / "shots" / "shot01" / "renders"
    renders.mkdir(parents=True, exist_ok=True)
    mp4 = renders / "take.mp4"
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run(
        [ffmpeg, "-y", "-f", "lavfi", "-i",
         "testsrc=duration=1:size=320x240:rate=10",
         "-pix_fmt", "yuv420p", "-loglevel", "error", str(mp4)],
        check=True, capture_output=True, timeout=60,
    )
    return mp4, "ai_videos/td/episodes/ep01/shots/shot01/renders/take.mp4"


def _burner(root: Path) -> SubtitleBurner:
    return SubtitleBurner(ExposedTree(root), SafeResolver(root))


def test_burn_missing_subtitles_file_raises(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    _shot_render(root)
    with pytest.raises(SubtitleFileMissingError):
        _burner(root).burn("ai_videos/td/episodes/ep01/shots/shot01/renders/take.mp4")


def test_burn_empty_subtitles_raises(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    mp4, rel = _shot_render(root)
    (mp4.parent.parent / "subtitles.md").write_text("# only a comment\n", encoding="utf-8")
    with pytest.raises(EmptySubtitlesError):
        _burner(root).burn(rel)


def test_burn_produces_subtitled_mp4(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    mp4, rel = _shot_render(root)
    shot_folder = mp4.parent.parent
    (shot_folder / "subtitles.md").write_text(
        "```text\n0-0.5 重活一回\n0.5-1 你们等着\n```\n", encoding="utf-8"
    )
    result = _burner(root).burn(rel)
    assert result.cue_count == 2
    out = mp4.with_name("take_subtitled.mp4")
    assert out.is_file() and out.stat().st_size > 0
    assert result.out_rel.endswith("renders/take_subtitled.mp4")


def test_scaffold_from_shot_md_and_refuses_overwrite(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    mp4, rel = _shot_render(root)
    shot_folder = mp4.parent.parent
    (shot_folder / "shot01.md").write_text(
        '台词 / 字幕: `太监(宣旨):"奉天承运, 女帝诏曰:"`\n时长: `5秒`\n',
        encoding="utf-8",
    )
    result = _burner(root).scaffold(rel)
    assert result.created is True
    sub = shot_folder / "subtitles.md"
    assert sub.is_file()
    body = sub.read_text(encoding="utf-8")
    assert "奉天承运, 女帝诏曰" in body
    cues = parse_subtitles(body)
    assert len(cues) == 1 and cues[0].end == 5
    # second scaffold refuses (file now non-empty)
    with pytest.raises(SubtitleAlreadyExistsError):
        _burner(root).scaffold(rel)


def test_scaffold_placeholder_when_no_shot_md(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    mp4, rel = _shot_render(root)
    result = _burner(root).scaffold(rel)
    assert result.created is True
    body = (mp4.parent.parent / "subtitles.md").read_text(encoding="utf-8")
    assert "（在此填写台词）" in body
