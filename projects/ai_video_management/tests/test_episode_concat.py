"""EpisodeConcatBuilder stitches each shot's NEWEST renders/ mp4 into one
ep{NN}.mp4 in the episode folder.

Selection contract (per the 2026-05-31 follow-up):
- per shot, scan ONLY `shots/shotNN/renders/` for *.mp4 and take the most
  recently modified one;
- `archive/` under renders/ is excluded; a stray `shotNN_chars.mp4` sitting
  directly in the shot folder (not renders/) is ignored;
- shots whose renders/ is missing/empty are skipped (not fatal);
- output is `{ep dir name}.mp4` in the episode folder, overwriting any prior.

The real ffmpeg concat is stubbed here — these assert the orchestration
(selection / ordering / skip / output path), not the encode itself.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from libs.common.exposed_tree import ExposedTree
from libs.common.safe_resolve import SafeResolver
from libs.domain.errors.episode__error import (
    NoShotVideosError,
    NotEpisodePathError,
)
from libs.infrastructure.writers.episode__writer import EpisodeConcatBuilder


def _touch(path: Path, mtime: float | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"x")
    if mtime is not None:
        os.utime(path, (mtime, mtime))


def _make_builder(root: Path) -> tuple[EpisodeConcatBuilder, list[list[Path]]]:
    """Builder whose ffmpeg concat is stubbed to just write the output file
    and record the chosen input list."""
    builder = EpisodeConcatBuilder(ExposedTree(root), SafeResolver(root))
    captured: list[list[Path]] = []

    def fake_concat(inputs: list[Path], out_path: Path) -> None:
        captured.append(list(inputs))
        out_path.write_bytes(b"episode")

    builder._ffmpeg_concat = fake_concat  # type: ignore[method-assign]
    return builder, captured


def test_concat_picks_newest_render_per_shot_and_skips_empty(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    ep = root / "ai_videos" / "td" / "episodes" / "ep01"
    # shot01: two renders — the higher-mtime one must win.
    _touch(ep / "shots" / "shot01" / "renders" / "old.mp4", mtime=1000)
    _touch(ep / "shots" / "shot01" / "renders" / "new.mp4", mtime=2000)
    # a derived 2s char reel directly in the shot folder must be ignored.
    _touch(ep / "shots" / "shot01" / "shot01_chars.mp4", mtime=9999)
    # shot02: no renders/ at all → skipped.
    _touch(ep / "shots" / "shot02" / "shot02.md")
    # shot03: one render + an archived (newer) one that must be excluded.
    _touch(ep / "shots" / "shot03" / "renders" / "keep.mp4", mtime=1500)
    _touch(ep / "shots" / "shot03" / "renders" / "archive" / "old_take.mp4", mtime=8888)
    # the episode index file the UI button is anchored on.
    _touch(ep / "shotlist.md")

    builder, captured = _make_builder(root)
    result = builder.build("ai_videos/td/episodes/ep01/shotlist.md")

    assert result.out_rel == "ai_videos/td/episodes/ep01/ep01.mp4"
    assert (ep / "ep01.mp4").is_file()
    # shot01 + shot03 used, in shot order; shot02 skipped.
    assert [u.shot for u in result.used] == ["shot01", "shot03"]
    assert [u.video_rel for u in result.used] == [
        "ai_videos/td/episodes/ep01/shots/shot01/renders/new.mp4",
        "ai_videos/td/episodes/ep01/shots/shot03/renders/keep.mp4",
    ]
    assert [(s.shot, s.reason) for s in result.skipped] == [("shot02", "no_render_mp4")]
    # ffmpeg got exactly the two selected clips, in order.
    assert len(captured) == 1
    assert [p.name for p in captured[0]] == ["new.mp4", "keep.mp4"]


def test_concat_overwrites_existing_episode_mp4(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    ep = root / "ai_videos" / "td" / "episodes" / "ep02"
    _touch(ep / "shots" / "shot01" / "renders" / "a.mp4", mtime=1000)
    stale = ep / "ep02.mp4"
    _touch(stale, mtime=1)
    stale.write_bytes(b"STALE-PRIOR-BUILD")

    builder, _ = _make_builder(root)
    result = builder.build("ai_videos/td/episodes/ep02/shots/shot01/shot01.md")

    assert result.out_rel == "ai_videos/td/episodes/ep02/ep02.mp4"
    assert stale.read_bytes() == b"episode"  # overwritten by the stub


def test_no_shot_has_render_raises(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    ep = root / "ai_videos" / "td" / "episodes" / "ep03"
    _touch(ep / "shots" / "shot01" / "shot01.md")  # no renders/ anywhere
    _touch(ep / "shotlist.md")

    builder, _ = _make_builder(root)
    with pytest.raises(NoShotVideosError):
        builder.build("ai_videos/td/episodes/ep03/shotlist.md")


def test_non_episode_path_rejected(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    _touch(root / "ai_videos" / "td" / "characters" / "c1_x" / "c1_x.md")

    builder, _ = _make_builder(root)
    with pytest.raises(NotEpisodePathError):
        builder.build("ai_videos/td/characters/c1_x/c1_x.md")
