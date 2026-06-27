"""`tools/seam_concat.py` `_segment_ok` guard: a freshly-built bridge segment is
usable in the final concat ONLY if it carries a decodable Video stream. A forced
RIFE bridge over a big scale/scene jump can encode to a file with no usable video
stream; concatenating it makes the whole filtergraph fail ("matches no streams")
and silently breaks the episode (wushen 2026-06-27: ep1/ep3 拼接成片 produced no
mp4, no error). The guard drops such a bridge so the seam falls back to a clean
butt-join and the episode still builds. These assert the guard distinguishes a
real clip from a no-video file, loading the tool exactly as the webapp does.
"""
from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path
from types import ModuleType

import imageio_ffmpeg


def _load_seam_concat() -> ModuleType:
    # repo root = tests → ai_video_management → projects → spec_coding
    root = Path(__file__).resolve().parents[3]
    path = root / "tools" / "seam_concat.py"
    spec = importlib.util.spec_from_file_location("seam_concat_tool", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _make_real_clip(dst: Path) -> None:
    """A tiny but valid mp4 with a real video stream (1s of testsrc)."""
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run(
        [ff, "-y", "-f", "lavfi", "-i", "testsrc=size=64x64:rate=24:duration=1",
         "-pix_fmt", "yuv420p", "-c:v", "libx264", "-preset", "veryfast",
         "-loglevel", "error", str(dst)],
        capture_output=True, check=True,
    )


def test_segment_ok_true_for_real_video_clip(tmp_path: Path) -> None:
    seam = _load_seam_concat()
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    clip = tmp_path / "ok.mp4"
    _make_real_clip(clip)
    assert seam._segment_ok(ff, clip) is True


def test_segment_ok_false_for_no_video_file(tmp_path: Path) -> None:
    seam = _load_seam_concat()
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    # a degenerate "bridge" with no decodable video stream — here just junk bytes;
    # ffmpeg -i reports no `Video:` stream, so the guard must reject it.
    junk = tmp_path / "broken.mp4"
    junk.write_bytes(b"\x00\x01\x02not-a-video")
    assert seam._segment_ok(ff, junk) is False


def test_segment_ok_false_for_missing_file(tmp_path: Path) -> None:
    seam = _load_seam_concat()
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    assert seam._segment_ok(ff, tmp_path / "nope.mp4") is False
