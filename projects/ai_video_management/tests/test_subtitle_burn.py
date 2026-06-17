"""Subtitle parse / ASS render (pure) + SubtitleBurner scaffold & burn.

The burn test does a real (tiny) ffmpeg encode using the imageio-ffmpeg
binary — fast on a 1s 320x240 clip — to prove the subtitles filter + libx264
pipeline produces a non-empty `*_subtitled_{lang}.mp4`.
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
    InvalidSubtitleLangError,
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
    assert cues[1].zh == "（内心）这一世，我裴知秋绝不再忍。"
    assert cues[1].en == ""
    assert cues[2].start == 5.5


def test_parse_subtitles_bilingual_split() -> None:
    text = "0-3  重活一回。 || Lived again.\n3-5 你们等着 ||\n5-7 || only english\n"
    cues = parse_subtitles(text)
    assert len(cues) == 3
    assert cues[0].zh == "重活一回。" and cues[0].en == "Lived again."
    assert cues[1].zh == "你们等着" and cues[1].en == ""
    assert cues[2].zh == "" and cues[2].en == "only english"


def test_parse_subtitles_skips_malformed_and_inverted() -> None:
    text = "not a cue line\n5-3 倒置时间窗\n2-4\n2-4   ok\n"
    cues = parse_subtitles(text)
    assert len(cues) == 1
    assert cues[0].zh == "ok"


def test_cues_to_ass_zh_only_default_lang() -> None:
    cues = parse_subtitles("0-3 甲 || A\n3-5.5 乙 || B\n")
    ass = cues_to_ass(cues)  # default zh
    assert "[Script Info]" in ass and "[V4+ Styles]" in ass
    assert "微软雅黑" in ass
    dialogues = [ln for ln in ass.splitlines() if ln.startswith("Dialogue:")]
    assert len(dialogues) == 2
    assert "甲" in dialogues[0] and "A" not in dialogues[0]
    assert "0:00:05.50" in dialogues[1]


def test_cues_to_ass_en_only() -> None:
    cues = parse_subtitles("0-3 甲 || Alpha\n3-5 乙 || Beta\n")
    ass = cues_to_ass(cues, "en")
    dialogues = [ln for ln in ass.splitlines() if ln.startswith("Dialogue:")]
    assert len(dialogues) == 2
    assert "Alpha" in dialogues[0] and "甲" not in dialogues[0]


def test_cues_to_ass_both_one_block_zh_above_en() -> None:
    cues = parse_subtitles("0-3 甲 || Alpha\n")
    ass = cues_to_ass(cues, "both")
    dialogues = [ln for ln in ass.splitlines() if ln.startswith("Dialogue:")]
    assert len(dialogues) == 1  # single bottom-anchored block (no overlap)
    text = dialogues[0].rsplit(",,", 1)[1]
    assert text == r"甲\NAlpha"  # zh line above en line


def test_cues_to_ass_rejects_unknown_lang() -> None:
    cues = parse_subtitles("0-3 甲\n")
    with pytest.raises(ValueError):
        cues_to_ass(cues, "fr")


def test_long_zh_line_wraps_into_multiple_lines() -> None:
    # 30-char Chinese line must wrap (no spaces) so it fits the safe width.
    long_zh = "宿主你眼下只有两条路一条是继续苟活做一辈子被人随意践踏的废物"
    cues = parse_subtitles(f"0-5 {long_zh}\n")
    dialogue = [ln for ln in cues_to_ass(cues, "zh").splitlines() if ln.startswith("Dialogue:")][0]
    assert r"\N" in dialogue  # wrapped to >=2 lines
    # Text field = everything after the final ",," (Effect is empty).
    body = dialogue.rsplit(",,", 1)[1]
    for seg in body.split(r"\N"):
        assert len(seg) <= 13


def test_short_line_not_wrapped() -> None:
    cues = parse_subtitles("0-3 觉醒武神我喜欢\n")
    dialogue = [ln for ln in cues_to_ass(cues, "zh").splitlines() if ln.startswith("Dialogue:")][0]
    assert r"\N" not in dialogue


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


def test_burn_invalid_lang_raises(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    mp4, rel = _shot_render(root)
    (mp4.parent.parent / "subtitles.md").write_text("0-1 甲 || A\n", encoding="utf-8")
    with pytest.raises(InvalidSubtitleLangError):
        _burner(root).burn(rel, "fr")


def test_burn_en_only_missing_english_raises(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    mp4, rel = _shot_render(root)
    (mp4.parent.parent / "subtitles.md").write_text("0-1 只有中文\n", encoding="utf-8")
    with pytest.raises(EmptySubtitlesError):
        _burner(root).burn(rel, "en")


def test_burn_produces_subtitled_mp4_per_lang(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    mp4, rel = _shot_render(root)
    shot_folder = mp4.parent.parent
    (shot_folder / "subtitles.md").write_text(
        "```text\n0-0.5 重活一回 || Lived again\n0.5-1 你们等着 || Just wait\n```\n",
        encoding="utf-8",
    )
    shot_folder = mp4.parent.parent  # …/shots/shot01 (parent of renders/)
    for lang, suffix in (("zh", "zh"), ("en", "en"), ("both", "zhen")):
        result = _burner(root).burn(rel, lang)
        assert result.cue_count == 2 and result.lang == lang
        out = shot_folder / f"shot01_{suffix}.mp4"
        assert out.is_file() and out.stat().st_size > 0
        assert result.out_rel.endswith(f"shots/shot01/shot01_{suffix}.mp4")


def test_scaffold_from_shot_md_bilingual_and_refuses_overwrite(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    mp4, rel = _shot_render(root)
    shot_folder = mp4.parent.parent
    (shot_folder / "shot01.md").write_text(
        "时长: 6秒\n## 台词配音\n台词: 重活一回\n台词: 你们等着\n",
        encoding="utf-8",
    )
    result = _burner(root).scaffold(rel)
    assert result.created is True
    body = (shot_folder / "subtitles.md").read_text(encoding="utf-8")
    assert "重活一回 ||" in body and "你们等着 ||" in body
    cues = parse_subtitles(body)
    assert len(cues) == 2 and cues[-1].end == 6
    with pytest.raises(SubtitleAlreadyExistsError):
        _burner(root).scaffold(rel)


def test_scaffold_placeholder_when_no_shot_md(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    mp4, rel = _shot_render(root)
    result = _burner(root).scaffold(rel)
    assert result.created is True
    body = (mp4.parent.parent / "subtitles.md").read_text(encoding="utf-8")
    assert "（在此填写中文台词）" in body
