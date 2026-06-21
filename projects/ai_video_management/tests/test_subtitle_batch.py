"""Batch subtitle ops: scaffold every shot in an episode, burn every shot
across a whole drama. The burn test does a real (tiny) ffmpeg encode per shot.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import imageio_ffmpeg
import pytest

from libs.common.exposed_tree import ExposedTree
from libs.common.safe_resolve import SafeResolver
from libs.domain.errors.subtitle__error import (
    InvalidBatchScopeError,
    NoBatchShotsError,
)
from libs.infrastructure.writers.subtitle__writer import SubtitleBurner
from libs.infrastructure.writers.subtitle_batch__writer import SubtitleBatchBurner


def _batch(root: Path) -> SubtitleBatchBurner:
    resolver = SafeResolver(root)
    exposed = ExposedTree(root)
    return SubtitleBatchBurner(exposed, resolver, SubtitleBurner(exposed, resolver))


def _make_render(shot_dir: Path) -> None:
    renders = shot_dir / "renders"
    renders.mkdir(parents=True, exist_ok=True)
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run(
        [ffmpeg, "-y", "-f", "lavfi", "-i",
         "testsrc=duration=1:size=320x240:rate=10",
         "-pix_fmt", "yuv420p", "-loglevel", "error", str(renders / "take.mp4")],
        check=True, capture_output=True, timeout=60,
    )


def _shot(root: Path, ep: str, shot: str, *, talk: str | None) -> Path:
    shot_dir = root / "ai_videos" / "td" / "episodes" / ep / "shots" / shot
    shot_dir.mkdir(parents=True, exist_ok=True)
    body = "时长: 6秒\n"
    if talk is not None:
        body += f"## 台词配音\n台词: {talk}\n"
    (shot_dir / f"{shot}.md").write_text(body, encoding="utf-8")
    return shot_dir


# --- scaffold_episode ---------------------------------------------------------

def test_scaffold_episode_writes_each_shot_and_skips_silent(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    _shot(root, "ep01", "shot01", talk="老天爷，竟真让我重活一回。")
    _shot(root, "ep01", "shot02", talk="你们，都等着。")
    _shot(root, "ep01", "shot03", talk=None)  # silent → skipped

    result = _batch(root).scaffold_episode(
        "ai_videos/td/episodes/ep01/shots/shot01/shot01.md"
    )
    by_shot = {o.shot: o for o in result.outcomes}
    assert by_shot["shot01"].ok and by_shot["shot02"].ok
    assert (root / "ai_videos/td/episodes/ep01/shots/shot01/subtitles.md").is_file()
    assert (root / "ai_videos/td/episodes/ep01/shots/shot02/subtitles.md").is_file()
    assert by_shot["shot03"].ok is False and by_shot["shot03"].reason == "no_dialogue"
    assert not (root / "ai_videos/td/episodes/ep01/shots/shot03/subtitles.md").exists()


def test_scaffold_episode_rejects_non_episode_path(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    (root / "ai_videos" / "td").mkdir(parents=True, exist_ok=True)
    with pytest.raises(InvalidBatchScopeError):
        _batch(root).scaffold_episode("ai_videos/td/README.md")


def test_scaffold_episode_no_shots_raises(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    (root / "ai_videos" / "td" / "episodes" / "ep01").mkdir(parents=True, exist_ok=True)
    with pytest.raises(NoBatchShotsError):
        _batch(root).scaffold_episode("ai_videos/td/episodes/ep01/episode.md")


# --- burn_drama ---------------------------------------------------------------

def test_burn_drama_burns_every_shot_across_episodes(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    # ep01/shot01: render + subtitles → burns.
    s1 = _shot(root, "ep01", "shot01", talk="重活一回。")
    _make_render(s1)
    (s1 / "subtitles.md").write_text(
        "```text\n0-0.5 重活一回 || Lived again\n0.5-1 你们等着 || Just wait\n```\n",
        encoding="utf-8",
    )
    # ep02/shot01: render but NO subtitles → skipped.
    s2 = _shot(root, "ep02", "shot01", talk="你们等着。")
    _make_render(s2)
    # ep02/shot02: subtitles but NO render → skipped.
    s3 = _shot(root, "ep02", "shot02", talk="等着。")
    (s3 / "subtitles.md").write_text("```text\n0-1 等着 || wait\n```\n", encoding="utf-8")

    result = _batch(root).burn_drama("ai_videos/td/README.md", "zh")
    assert result.lang == "zh"
    by_key = {(o.episode, o.shot): o for o in result.outcomes}
    assert by_key[("ep01", "shot01")].ok
    assert (s1 / "shot01_zh.mp4").is_file()
    assert by_key[("ep02", "shot01")].reason == "no_subtitles_md"
    assert by_key[("ep02", "shot02")].reason == "no_render_mp4"


# --- burn_episode -------------------------------------------------------------

def test_burn_episode_burns_only_named_episode(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    # ep01/shot01: render + subtitles → burns.
    s1 = _shot(root, "ep01", "shot01", talk="重活一回。")
    _make_render(s1)
    (s1 / "subtitles.md").write_text(
        "```text\n0-0.5 重活一回 || Lived again\n```\n", encoding="utf-8",
    )
    # ep02/shot01: render + subtitles, but a DIFFERENT episode → must be untouched.
    s2 = _shot(root, "ep02", "shot01", talk="你们等着。")
    _make_render(s2)
    (s2 / "subtitles.md").write_text(
        "```text\n0-1 你们等着 || Just wait\n```\n", encoding="utf-8",
    )

    result = _batch(root).burn_episode(
        "ai_videos/td/episodes/ep01/shotlist.md", "zh"
    )
    assert result.lang == "zh"
    by_shot = {o.shot: o for o in result.outcomes}
    assert by_shot["shot01"].ok
    assert (s1 / "shot01_zh.mp4").is_file()
    # ep02 was outside scope → not burned.
    assert not (s2 / "shot01_zh.mp4").exists()
    assert len(result.outcomes) == 1


def test_burn_episode_rejects_non_episode_path(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    (root / "ai_videos" / "td").mkdir(parents=True, exist_ok=True)
    with pytest.raises(InvalidBatchScopeError):
        _batch(root).burn_episode("ai_videos/td/README.md", "zh")


def test_burn_drama_rejects_actor_root(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    (root / "ai_videos" / "_actors").mkdir(parents=True, exist_ok=True)
    with pytest.raises(InvalidBatchScopeError):
        _batch(root).burn_drama("ai_videos/_actors/actor_x/actor_x.md", "zh")
