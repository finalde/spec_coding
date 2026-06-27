"""Whole-episode subtitle burn (follow-up 147): concat → segments.json → burn
ONE subtitle track onto the clean ep{NN}.mp4, each shot's cues offset to its
true position in the final timeline.

Asserts: (1) segment offset accumulation, (2) ep-level cue absolute time =
segment.start_s + in-segment relative time, (3) a non-empty ep{NN}_zh.mp4.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import imageio_ffmpeg
import pytest

from libs.common.exposed_tree import ExposedTree
from libs.common.safe_resolve import SafeResolver
from libs.domain.errors.subtitle__error import (
    EpisodeNotConcatenatedError,
    NoEpisodeVideoError,
)
from libs.infrastructure.writers.episode__writer import EpisodeConcatBuilder
from libs.infrastructure.writers.episode_subtitle__writer import EpisodeSubtitleBurner
from libs.infrastructure.writers.subtitle__writer import SubtitleBurner


def _silent_clip(path: Path, dur: float) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run(
        [ff, "-y", "-f", "lavfi",
         "-i", f"testsrc=duration={dur}:size=320x240:rate=30",
         "-pix_fmt", "yuv420p", str(path)],
        capture_output=True, check=True,
    )


def _burner(root: Path) -> EpisodeSubtitleBurner:
    exposed, resolver = ExposedTree(root), SafeResolver(root)
    return EpisodeSubtitleBurner(exposed, resolver, SubtitleBurner(exposed, resolver))


def _shot_with_talk(ep: Path, shot: str, dur: float, talk: str) -> None:
    sd = ep / "shots" / shot
    _silent_clip(sd / "renders" / "take.mp4", dur)
    (sd / f"{shot}.md").write_text(
        f"时长: {int(dur)}秒\n## 台词配音\n台词: {talk}\n", encoding="utf-8"
    )


def test_assemble_cues_offsets_each_shot_by_segment_start(tmp_path: Path) -> None:
    """The core fix: shot N's cues are shifted by its segment start_s, so every
    cue of the 2nd shot sits AFTER the 1st shot ends — no per-shot 0-based reset."""
    root = tmp_path / "repo"
    ep = root / "ai_videos" / "td" / "episodes" / "ep01"
    _shot_with_talk(ep, "shot01", 2.0, "重活一回，我裴知秋绝不再忍。")
    _shot_with_talk(ep, "shot02", 2.0, "你们，都给我等着。")
    segments = [
        {"shot": "shot01", "start_s": 0.0, "end_s": 1.8, "dur_s": 1.8},
        {"shot": "shot02", "start_s": 1.8, "end_s": 3.5, "dur_s": 1.7},
    ]
    cues, n_shots = _burner(root).assemble_cues(ep / "shots", segments)
    assert n_shots == 2 and len(cues) >= 2
    # shot01 cues live in [0, 1.8]; shot02 cues are all shifted to >= 1.8.
    s1 = [c for c in cues if c.start < 1.8]
    s2 = [c for c in cues if c.start >= 1.8]
    assert s1 and s2
    assert max(c.end for c in s1) <= 1.81           # shot01 ends within its segment
    assert min(c.start for c in s2) >= 1.8          # shot02 offset into its segment
    assert max(c.end for c in s2) <= 3.51           # and stays within the reel end
    # cues are globally monotonic (sorted, non-overlapping within a shot)
    for a, b in zip(cues, cues[1:]):
        assert b.start >= a.start


def test_burn_whole_end_to_end_produces_ep_zh_mp4(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    ep = root / "ai_videos" / "td" / "episodes" / "ep01"
    _shot_with_talk(ep, "shot01", 1.2, "重活一回。")
    _shot_with_talk(ep, "shot02", 1.2, "你们等着。")
    (ep / "shotlist.md").write_text("x", encoding="utf-8")

    # Step 2: concat the clean reel + segments.json.
    concat = EpisodeConcatBuilder(ExposedTree(root), SafeResolver(root))
    res = concat.build("ai_videos/td/episodes/ep01/shotlist.md")
    assert (root / res.out_rel).is_file()
    assert res.segments_rel and (root / res.segments_rel).is_file()
    seg_data = json.loads((root / res.segments_rel).read_text(encoding="utf-8"))
    assert [s["shot"] for s in seg_data["segments"]] == ["shot01", "shot02"]
    assert seg_data["segments"][1]["start_s"] > 0  # 2nd shot offset accumulated

    # Step 3: burn ONE subtitle track onto the clean reel.
    out = _burner(root).burn_whole("ai_videos/td/episodes/ep01/shotlist.md", "zh")
    assert out.lang == "zh" and out.shot_count == 2 and out.cue_count >= 2
    burned = root / out.out_rel
    assert burned.name == "ep01_zh.mp4"
    assert burned.is_file() and burned.stat().st_size > 1000


def test_burn_whole_requires_concat_first(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    ep = root / "ai_videos" / "td" / "episodes" / "ep01"
    _shot_with_talk(ep, "shot01", 1.0, "重活一回。")
    (ep / "shotlist.md").write_text("x", encoding="utf-8")
    # No ep01.mp4 yet → must tell the user to concat first.
    with pytest.raises(NoEpisodeVideoError):
        _burner(root).burn_whole("ai_videos/td/episodes/ep01/shotlist.md", "zh")
    # ep01.mp4 present but no segments.json → still blocked.
    (ep / "ep01.mp4").write_bytes(b"x")
    with pytest.raises(EpisodeNotConcatenatedError):
        _burner(root).burn_whole("ai_videos/td/episodes/ep01/shotlist.md", "zh")
