"""Strip the audio track from a video, producing a silent master.

AI-video shots rendered by Seedance/Kling ship with a baked-in audio track
(auto-TTS or ambient noise) that is NOT consistent across one-by-one renders.
Post-production replaces it: the silent video is the canonical master that
`tools/mux_av.py` later mounts the locked-voice 台词 MP3 (and BGM) onto.

The video stream is copied (`-c:v copy`, no re-encode); only the audio is
dropped (`-an`). Output defaults to `<stem>_silent.mp4` beside each input.

Usage:
  python tools/mute_video.py shots/shot01/shot01.mp4
  python tools/mute_video.py a.mp4 b.mp4 --suffix _silent
  python tools/mute_video.py in.mp4 --out clean.mp4

ffmpeg is located via the bundled imageio_ffmpeg when present, else `ffmpeg`
on PATH.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def _ffmpeg_exe() -> str:
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Strip audio from a video → silent master.")
    p.add_argument("inputs", nargs="+", help="Source video(s).")
    p.add_argument("--suffix", default="_silent", help="Output stem suffix (default _silent).")
    p.add_argument("--out", default=None, help="Explicit output path (single input only).")
    return p.parse_args(argv)


def _out_path(src: Path, suffix: str) -> Path:
    return src.with_name(f"{src.stem}{suffix}{src.suffix}")


def _mute(ffmpeg: str, src: Path, dst: Path) -> int:
    cmd = [ffmpeg, "-y", "-i", str(src), "-c:v", "copy", "-an", str(dst)]
    proc = subprocess.run(cmd, capture_output=True)
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr.decode("utf-8", errors="replace")[-800:])
    return proc.returncode


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
    args = _parse_args(argv)
    if args.out is not None and len(args.inputs) != 1:
        sys.stderr.write("--out requires exactly one input.\n")
        return 2
    ffmpeg = _ffmpeg_exe()
    for raw in args.inputs:
        src = Path(raw)
        if not src.exists():
            sys.stderr.write(f"missing: {src}\n")
            return 1
        dst = Path(args.out) if args.out else _out_path(src, args.suffix)
        rc = _mute(ffmpeg, src, dst)
        if rc != 0:
            return rc
        print(f"{src} -> {dst}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
