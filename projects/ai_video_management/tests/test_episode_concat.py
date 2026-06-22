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
import subprocess
from pathlib import Path

import imageio_ffmpeg
import pytest

from libs.common.exposed_tree import ExposedTree
from libs.common.safe_resolve import SafeResolver
from libs.domain.errors.episode__error import (
    NoShotVideosError,
    NotEpisodePathError,
)
from libs.infrastructure.writers.episode__writer import (
    _SEAM_MIN_EDGE_TRIM_S,
    EpisodeConcatBuilder,
)


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

    def fake_concat(
        ffmpeg: str,
        inputs: list[Path],
        out_path: Path,
        head_trims: list[float],
        tail_trims: list[float],
    ) -> None:
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


def test_concat_lang_variant_picks_language_master_and_names_output(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    ep = root / "ai_videos" / "td" / "episodes" / "ep01"
    # shot01 has a burned zh master in the shot-folder root (not renders/).
    _touch(ep / "shots" / "shot01" / "renders" / "raw.mp4", mtime=1000)
    _touch(ep / "shots" / "shot01" / "shot01_zh.mp4", mtime=2000)
    # shot02 has a raw render but NO zh master → skipped for the zh build.
    _touch(ep / "shots" / "shot02" / "renders" / "raw.mp4", mtime=1000)
    _touch(ep / "shotlist.md")

    builder, captured = _make_builder(root)
    result = builder.build("ai_videos/td/episodes/ep01/shotlist.md", "zh")

    assert result.lang == "zh"
    assert result.out_rel == "ai_videos/td/episodes/ep01/ep01_zh.mp4"
    assert [u.shot for u in result.used] == ["shot01"]
    assert result.used[0].video_rel == "ai_videos/td/episodes/ep01/shots/shot01/shot01_zh.mp4"
    assert [(s.shot, s.reason) for s in result.skipped] == [("shot02", "no_zh_subtitle_mp4")]
    assert [p.name for p in captured[0]] == ["shot01_zh.mp4"]


def test_concat_both_variant_output_name(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    ep = root / "ai_videos" / "td" / "episodes" / "ep01"
    _touch(ep / "shots" / "shot01" / "shot01_zhen.mp4", mtime=2000)
    _touch(ep / "shotlist.md")
    builder, _ = _make_builder(root)
    result = builder.build("ai_videos/td/episodes/ep01/shotlist.md", "both")
    assert result.out_rel == "ai_videos/td/episodes/ep01/ep01_zhen.mp4"


def test_non_episode_path_rejected(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    _touch(root / "ai_videos" / "td" / "characters" / "c1_x" / "c1_x.md")

    builder, _ = _make_builder(root)
    with pytest.raises(NotEpisodePathError):
        builder.build("ai_videos/td/characters/c1_x/c1_x.md")


# --- 承接 seam de-stutter (跨镜首帧承接) ----------------------------------

def _bare(root: Path) -> EpisodeConcatBuilder:
    return EpisodeConcatBuilder(ExposedTree(root), SafeResolver(root))


def _freeze_out(starts: list[str], ends: list[str]) -> str:
    """Synthesise freezedetect stderr (start lines, then end lines)."""
    lines = [f"[freezedetect @ 0x0] lavfi.freezedetect.freeze_start: {s}" for s in starts]
    lines += [f"[freezedetect @ 0x0] lavfi.freezedetect.freeze_end: {e}" for e in ends]
    return "\n".join(lines)


def _static_head_clip(path: Path) -> None:
    """A clip that holds a frozen frame for ~0.4s, then moves — mimics a 承接
    shot whose first frame is the previous shot's held last frame."""
    path.parent.mkdir(parents=True, exist_ok=True)
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run(
        [ff, "-y",
         "-f", "lavfi", "-i", "color=c=green:size=320x240:rate=10:duration=0.4",
         "-f", "lavfi", "-i", "color=c=gray:size=320x240:rate=10:duration=1",
         "-filter_complex",
         "[1:v]noise=alls=100:allf=t[m];[0:v][m]concat=n=2:v=1[v]",
         "-map", "[v]", "-pix_fmt", "yuv420p", str(path)],
        capture_output=True, check=True,
    )


def test_is_continuity_shot_reads_衔接_line(tmp_path: Path) -> None:
    shot = tmp_path / "shots" / "shot02"
    shot.mkdir(parents=True)
    ext = _bare(tmp_path)
    (shot / "shot02.md").write_text(
        "## Shot context\n- **衔接**：承接 shot01 末帧（首帧＝上一镜末帧）\n", encoding="utf-8"
    )
    assert ext._is_continuity_shot(shot) is True
    (shot / "shot02.md").write_text(
        "## Shot context\n- **衔接**：硬切（独立首帧·无承接帧）\n", encoding="utf-8"
    )
    assert ext._is_continuity_shot(shot) is False
    (shot / "shot02.md").write_text("## Shot context\n- **Summary**：x\n", encoding="utf-8")
    assert ext._is_continuity_shot(shot) is False  # no 衔接 line → hard cut default


def test_parse_head_freeze_head_freeze_trimmed() -> None:
    # clip starts frozen (start=0), motion resumes at 0.22 → trim 0.22
    out = _freeze_out(["0"], ["0.22"])
    assert EpisodeConcatBuilder._parse_head_freeze(out) == 0.22


def test_parse_head_freeze_non_head_freeze_ignored() -> None:
    # first freeze begins at 0.5s (past the head eps) → not a seam dup → 0
    out = _freeze_out(["0.5"], ["0.7"])
    assert EpisodeConcatBuilder._parse_head_freeze(out) == 0.0


def test_parse_head_freeze_no_freeze_is_zero() -> None:
    assert EpisodeConcatBuilder._parse_head_freeze("no freeze lines here") == 0.0


def test_parse_head_freeze_caps_long_freeze() -> None:
    # a clip frozen for 1.4s at the head is capped so it isn't gutted
    out = _freeze_out(["0"], ["1.4"])
    assert EpisodeConcatBuilder._parse_head_freeze(out) == 1.0


def test_detect_head_freeze_on_static_head(tmp_path: Path) -> None:
    clip = tmp_path / "b.mp4"
    _static_head_clip(clip)
    t = _bare(tmp_path)._detect_head_freeze(imageio_ffmpeg.get_ffmpeg_exe(), clip)
    assert t > 0.15  # the ~0.4s frozen head is detected and would be trimmed


def test_snap_fps_snaps_to_nearest_standard_rate() -> None:
    snap = EpisodeConcatBuilder._snap_fps
    assert snap(24.05) == 24          # ~24fps i2v renders → native 24, not up to 30
    assert snap(23.89) == 24
    assert snap(29.97) == 30
    assert snap(25.10) == 25
    assert snap(47.0) == 47           # outside tolerance of any standard → rounded


def test_target_fps_matches_24fps_source_not_30(tmp_path: Path) -> None:
    """The output rate follows the source: 24fps clips must NOT be up-converted to
    30 (that duplicates ~1 in 5 frames = global judder). 24fps in → 24fps target."""
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    clips = []
    for name in ("a.mp4", "b.mp4"):
        p = tmp_path / name
        subprocess.run(
            [ff, "-y", "-f", "lavfi",
             "-i", "testsrc=duration=0.5:size=320x240:rate=24",
             "-pix_fmt", "yuv420p", str(p)],
            capture_output=True, check=True,
        )
        clips.append(p)
    assert _bare(tmp_path)._target_fps(ff, clips) == 24


def test_target_fps_falls_back_when_unprobeable(tmp_path: Path) -> None:
    (tmp_path / "x.mp4").write_bytes(b"not a video")
    assert _bare(tmp_path)._target_fps(
        imageio_ffmpeg.get_ffmpeg_exe(), [tmp_path / "x.mp4"]
    ) == 30  # _CONCAT_FALLBACK_FPS


def test_build_trims_承接_shot_head_freeze(tmp_path: Path) -> None:
    """Integration: a 承接 shot's head freeze is detected and recorded as a trim,
    and its predecessor's tail gets the fixed seam bite. (ffmpeg concat stubbed.)"""
    root = tmp_path / "repo"
    ep = root / "ai_videos" / "td" / "episodes" / "ep01"
    # shot01 is the first clip (i=0) → never probed → a fake byte-file suffices.
    _touch(ep / "shots" / "shot01" / "renders" / "a.mp4", mtime=1000)
    _static_head_clip(ep / "shots" / "shot02" / "renders" / "b.mp4")
    (ep / "shots" / "shot01" / "shot01.md").write_text(
        "- **衔接**：硬切（独立首帧·无承接帧）\n", encoding="utf-8"
    )
    (ep / "shots" / "shot02" / "shot02.md").write_text(
        "- **衔接**：承接 shot01 末帧（首帧＝上一镜末帧）\n", encoding="utf-8"
    )
    (ep / "shotlist.md").write_text("x", encoding="utf-8")

    builder, captured = _make_builder(root)
    result = builder.build("ai_videos/td/episodes/ep01/shotlist.md")

    used = {u.shot: u.trimmed_s for u in result.used}
    assert used["shot01"] == _SEAM_MIN_EDGE_TRIM_S  # tail bite (successor is 承接)
    assert used["shot02"] > 0.15            # 承接 head freeze trimmed
    assert len(captured) == 1               # concat still ran once with both clips


def test_build_承接_min_trims_structural_duplicate_when_no_freeze(tmp_path: Path) -> None:
    """Even when freezedetect measures NO head freeze, a 承接 shot still drops the
    minimum (its first frame == previous shot's last frame by construction, so a
    1-frame duplicate remains). Detector stubbed to 0 → trim must equal the min."""
    root = tmp_path / "repo"
    ep = root / "ai_videos" / "td" / "episodes" / "ep01"
    _touch(ep / "shots" / "shot01" / "renders" / "a.mp4", mtime=1000)
    _touch(ep / "shots" / "shot02" / "renders" / "b.mp4", mtime=1000)
    (ep / "shots" / "shot02" / "shot02.md").write_text(
        "- **衔接**：承接 shot01 末帧\n", encoding="utf-8"
    )
    (ep / "shotlist.md").write_text("x", encoding="utf-8")

    builder, _ = _make_builder(root)
    builder._detect_head_freeze = lambda ffmpeg, src: 0.0  # type: ignore[assignment,method-assign]
    result = builder.build("ai_videos/td/episodes/ep01/shotlist.md")

    used = {u.shot: u.trimmed_s for u in result.used}
    assert used["shot01"] == _SEAM_MIN_EDGE_TRIM_S     # tail bite (successor is 承接)
    assert used["shot02"] == _SEAM_MIN_EDGE_TRIM_S     # structural min head trim


def test_build_no_trim_for_硬切_shot(tmp_path: Path) -> None:
    """硬切 shots are intended cuts — never probed, never trimmed (deterministic,
    no ffmpeg detection runs)."""
    root = tmp_path / "repo"
    ep = root / "ai_videos" / "td" / "episodes" / "ep01"
    _touch(ep / "shots" / "shot01" / "renders" / "a.mp4", mtime=1000)
    _touch(ep / "shots" / "shot02" / "renders" / "b.mp4", mtime=1000)
    (ep / "shots" / "shot02" / "shot02.md").write_text(
        "- **衔接**：硬切（独立首帧·无承接帧）\n", encoding="utf-8"
    )
    (ep / "shotlist.md").write_text("x", encoding="utf-8")

    builder, _ = _make_builder(root)
    result = builder.build("ai_videos/td/episodes/ep01/shotlist.md")
    assert all(u.trimmed_s == 0.0 for u in result.used)


def _silent_clip(path: Path, dur: float) -> None:
    """A short silent (audio-less) test clip — exercises the per-clip anullsrc
    fallback in the concat."""
    path.parent.mkdir(parents=True, exist_ok=True)
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run(
        [ff, "-y", "-f", "lavfi",
         "-i", f"testsrc=duration={dur}:size=320x240:rate=30",
         "-pix_fmt", "yuv420p", str(path)],
        capture_output=True, check=True,
    )


def test_real_concat_trims_both_sides_at_承接_and_skips_硬切(tmp_path: Path) -> None:
    """End-to-end: the concat filtergraph runs in ffmpeg over 3 audio-less clips —
    one 承接 seam (shot02←shot01) + one 硬切 seam (shot03). Both sides of the 承接
    seam are trimmed (shot02's head AND shot01's tail); the 硬切 predecessor's tail
    is left alone. Asserts a valid mp4 + timeline shortened below the naive 3.6s."""
    root = tmp_path / "repo"
    ep = root / "ai_videos" / "td" / "episodes" / "ep01"
    _silent_clip(ep / "shots" / "shot01" / "renders" / "a.mp4", 1.2)
    _silent_clip(ep / "shots" / "shot02" / "renders" / "b.mp4", 1.2)
    _silent_clip(ep / "shots" / "shot03" / "renders" / "c.mp4", 1.2)
    (ep / "shots" / "shot02" / "shot02.md").write_text(
        "- **衔接**：承接 shot01 末帧\n", encoding="utf-8"
    )
    (ep / "shots" / "shot03" / "shot03.md").write_text(
        "- **衔接**：硬切（独立首帧·无承接帧）\n", encoding="utf-8"
    )
    (ep / "shotlist.md").write_text("x", encoding="utf-8")

    builder = _bare(root)
    result = builder.build("ai_videos/td/episodes/ep01/shotlist.md")

    out = root / result.out_rel
    assert out.is_file() and out.stat().st_size > 1000
    dur = builder._probe_duration(imageio_ffmpeg.get_ffmpeg_exe(), out)
    assert 2.0 < dur < 3.55          # shortened below the naive 1.2*3 = 3.6
    tm = {u.shot: u.trimmed_s for u in result.used}
    assert tm["shot01"] > 0.0        # tail trimmed (its successor shot02 is 承接)
    assert tm["shot02"] > 0.0        # 承接 head trimmed
    assert tm["shot03"] == 0.0       # 硬切, and last clip → untouched


def test_real_concat_consecutive_承接_seams(tmp_path: Path) -> None:
    """Two consecutive 承接 seams (each head-trimmed) butt-join into one clean
    continuous cut. No cross-fade — both a near-identical-frame seam dissolve
    (follow-up 135/136) and a whole-episode cross-dissolve (follow-up 142/143) were
    tried and reverted; plain concat reads best."""
    root = tmp_path / "repo"
    ep = root / "ai_videos" / "td" / "episodes" / "ep01"
    for s in ("shot01", "shot02", "shot03"):
        _silent_clip(ep / "shots" / s / "renders" / "x.mp4", 1.2)
    for s in ("shot02", "shot03"):  # both 承接 → consecutive xfades
        (ep / "shots" / s / f"{s}.md").write_text(
            "- **衔接**：承接 末帧\n", encoding="utf-8"
        )
    (ep / "shotlist.md").write_text("x", encoding="utf-8")

    builder = _bare(root)
    result = builder.build("ai_videos/td/episodes/ep01/shotlist.md")
    out = root / result.out_rel
    assert out.is_file() and out.stat().st_size > 1000


def _clip_audio_longer(path: Path, vdur: float, adur: float) -> None:
    """A clip whose AUDIO is longer than its VIDEO → container Duration (=audio)
    overstates the video timeline. Reproduces the real-render bug where xfade
    offsets, computed from container duration, overshot the video end and
    dropped everything after the first 承接 seam."""
    path.parent.mkdir(parents=True, exist_ok=True)
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run(
        [ff, "-y",
         "-f", "lavfi", "-i", f"testsrc=duration={vdur}:size=320x240:rate=30",
         "-f", "lavfi", "-i", f"sine=frequency=440:duration={adur}",
         "-map", "0:v", "-map", "1:a", "-pix_fmt", "yuv420p", str(path)],
        capture_output=True, check=True,
    )


def test_real_concat_preserves_length_when_audio_longer_than_video(tmp_path: Path) -> None:
    """Regression for the '少了很多内容' bug: clips whose container Duration
    (audio) exceeds the video must NOT truncate. Three clips (1s video / 1.4s
    audio), two consecutive 承接 seams → output must keep ~all 3 (>2s). Guards
    the video-stream probe so an over-long audio track can't drop content."""
    root = tmp_path / "repo"
    ep = root / "ai_videos" / "td" / "episodes" / "ep01"
    for s in ("shot01", "shot02", "shot03"):
        _clip_audio_longer(ep / "shots" / s / "renders" / "x.mp4", 1.0, 1.4)
    for s in ("shot02", "shot03"):
        (ep / "shots" / s / f"{s}.md").write_text("- **衔接**：承接 末帧\n", encoding="utf-8")
    (ep / "shotlist.md").write_text("x", encoding="utf-8")

    builder = _bare(root)
    result = builder.build("ai_videos/td/episodes/ep01/shotlist.md")
    dur = builder._probe_duration(imageio_ffmpeg.get_ffmpeg_exe(), root / result.out_rel)
    assert dur > 2.0  # all three clips present, not truncated to the first
