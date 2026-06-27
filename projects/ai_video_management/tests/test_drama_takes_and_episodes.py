"""Drama-level production-console ops:
  - DramaTakesSelector: drama-wide 定版 — lock every episode's newest takes to
    shot{NN}.mp4 in one pass (delegates to the per-episode selector).
  - DramaEpisodesReader: list a drama's episodes (shot count, locked count,
    whether ep{NN}.mp4 master exists) for the dashboard's per-episode concat row.

Pure file ops — no ffmpeg; dummy bytes stand in for the mp4s."""
from __future__ import annotations

from pathlib import Path

import pytest

from libs.common.exposed_tree import ExposedTree
from libs.common.safe_resolve import SafeResolver
from libs.domain.errors.subtitle__error import InvalidBatchScopeError
from libs.infrastructure.readers.drama_episodes__reader import DramaEpisodesReader
from libs.infrastructure.writers.drama_takes__writer import DramaTakesSelector
from libs.infrastructure.writers.episode_takes__writer import EpisodeTakesSelector


def _takes(root: Path) -> DramaTakesSelector:
    exposed, resolver = ExposedTree(root), SafeResolver(root)
    return DramaTakesSelector(exposed, resolver, EpisodeTakesSelector(exposed, resolver))


def _reader(root: Path) -> DramaEpisodesReader:
    return DramaEpisodesReader(ExposedTree(root), SafeResolver(root))


def _shot(root: Path, drama: str, ep: str, shot: str) -> Path:
    d = root / "ai_videos" / drama / "5_6_分镜与prompt" / "episodes" / ep / "shots" / shot
    d.mkdir(parents=True, exist_ok=True)
    return d


def _render(shot_dir: Path, name: str, data: bytes = b"v") -> None:
    renders = shot_dir / "renders"
    renders.mkdir(parents=True, exist_ok=True)
    (renders / name).write_bytes(data)


def test_select_all_locks_every_episode(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    (root / "ai_videos" / "td").mkdir(parents=True, exist_ok=True)
    (root / "ai_videos" / "td" / "README.md").write_text("# td", encoding="utf-8")
    _render(_shot(root, "td", "ep01", "shot01"), "take_a.mp4")
    _render(_shot(root, "td", "ep01", "shot02"), "take_b.mp4")
    _render(_shot(root, "td", "ep02", "shot01"), "take_c.mp4")
    _shot(root, "td", "ep02", "shot02")  # no render → skipped, not fatal

    r = _takes(root).select_all("ai_videos/td/README.md")

    by_ep = {o.episode: o for o in r.outcomes}
    assert by_ep["ep01"].ok and by_ep["ep01"].selected == 2 and by_ep["ep01"].skipped == 0
    assert by_ep["ep02"].ok and by_ep["ep02"].selected == 1 and by_ep["ep02"].skipped == 1
    # the locked canonical shot{NN}.mp4 now exists for rendered shots
    base = root / "ai_videos" / "td" / "5_6_分镜与prompt" / "episodes"
    assert (base / "ep01" / "shots" / "shot01" / "shot01.mp4").is_file()
    assert (base / "ep02" / "shots" / "shot01" / "shot01.mp4").is_file()


def test_select_all_reports_episode_with_no_renders_as_failed(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    (root / "ai_videos" / "td").mkdir(parents=True, exist_ok=True)
    _render(_shot(root, "td", "ep01", "shot01"), "take_a.mp4")
    _shot(root, "td", "ep02", "shot01")  # ep02 has a shot but NO render anywhere

    r = _takes(root).select_all("ai_videos/td")

    by_ep = {o.episode: o for o in r.outcomes}
    assert by_ep["ep01"].ok
    assert not by_ep["ep02"].ok and by_ep["ep02"].reason == "NoShotVideosError"


def test_select_all_rejects_bad_drama_path(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    (root / "ai_videos").mkdir(parents=True, exist_ok=True)
    with pytest.raises(InvalidBatchScopeError):
        _takes(root).select_all("ai_videos/_actors")  # system folder, not a drama


def test_list_episodes_reports_shots_locked_and_master(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    (root / "ai_videos" / "td").mkdir(parents=True, exist_ok=True)
    s1 = _shot(root, "td", "ep01", "shot01")
    s2 = _shot(root, "td", "ep01", "shot02")
    (s1 / "shot01.mp4").write_bytes(b"locked")     # 定版-locked
    # s2 not locked; ep01 has a stitched master
    ep01 = root / "ai_videos" / "td" / "5_6_分镜与prompt" / "episodes" / "ep01"
    (ep01 / "ep01.mp4").write_bytes(b"master")
    _shot(root, "td", "ep02", "shot01")            # ep02: 1 shot, none locked, no master

    r = _reader(root).list("ai_videos/td/README.md")

    by_ep = {e.episode: e for e in r.episodes}
    assert by_ep["ep01"].shots == 2 and by_ep["ep01"].locked == 1 and by_ep["ep01"].has_master
    assert by_ep["ep02"].shots == 1 and by_ep["ep02"].locked == 0 and not by_ep["ep02"].has_master
    # the concat target path is the ep folder, usable by /api/concat-episode
    assert by_ep["ep01"].episode_rel.endswith("episodes/ep01")


def test_list_episodes_empty_drama(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    (root / "ai_videos" / "td").mkdir(parents=True, exist_ok=True)

    r = _reader(root).list("ai_videos/td")

    assert r.episodes == ()
