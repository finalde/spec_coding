"""Episode-aggregate writer: stitch each shot's newest render into one
`ep{NN}.mp4` placed directly in the episode folder.

Given a path anywhere under `ai_videos/{drama}/episodes/ep{NN}/`, the builder
locates the episode dir, walks `shots/shot*/` in lexicographic order, and for
each shot takes the **newest** mp4 found under that shot's `renders/` subfolder
(`archive/` excluded). Shots whose `renders/` is missing/empty are skipped. The
selected full-length clips are ffmpeg-concatenated — uniform 9:16, with audio —
into `{ep dir name}.mp4` next to the episode's markdown, overwriting any prior
build. Output lives in the episode folder (not under `shots/`), so a re-run
never re-ingests its own previous output.

Implementation mirrors ShotConcatBuilder's concat *filter* approach
(`trim`-free here, so each shot plays at full length): every input is
normalised through `setpts → scale → pad → setsar → fps` for video and
`asetpts → aresample → aformat` for audio, so heterogeneous Kling / Seedance
renders stitch without A/V drift. Inputs lacking an audio stream contribute a
silent `anullsrc` track of matching length.

ffmpeg binary supplied by `imageio-ffmpeg` — no system install required.
"""
from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

import imageio_ffmpeg

from libs.common.exposed_tree import ExposedTree
from libs.common.safe_resolve import SafeResolver
from libs.domain.errors.episode__error import (
    EpisodeConcatFailedError,
    EpisodeFfmpegMissingError,
    EpisodeNotFoundError,
    InvalidEpisodePathError,
    NoShotsError,
    NoShotVideosError,
    NotEpisodePathError,
)

_EP_DIR_RE = re.compile(r"^ep\d+$", re.IGNORECASE)
_SHOT_DIR_RE = re.compile(r"^shot\d+$", re.IGNORECASE)
_RENDERS_DIR_NAME = "renders"
_ARCHIVE_DIR_NAME = "archive"
_MP4_EXT = ".mp4"

_EPISODE_FFMPEG_TIMEOUT_S: int = 600
_CONCAT_TARGET_W: int = 720      # 9:16 reel — 720x1280 is fast to encode + plenty for review
_CONCAT_TARGET_H: int = 1280
_CONCAT_TARGET_FPS: int = 30


@dataclass(frozen=True)
class ShotClip:
    shot: str
    video_rel: str

    def to_payload(self) -> dict[str, object]:
        return {"shot": self.shot, "video": self.video_rel}


@dataclass(frozen=True)
class ShotSkip:
    shot: str
    reason: str

    def to_payload(self) -> dict[str, object]:
        return {"shot": self.shot, "reason": self.reason}


@dataclass(frozen=True)
class EpisodeConcatResult:
    episode_rel: str
    out_rel: str | None
    used: tuple[ShotClip, ...]
    skipped: tuple[ShotSkip, ...]

    def to_payload(self) -> dict[str, object]:
        return {
            "episode": self.episode_rel,
            "out": self.out_rel,
            "used": [u.to_payload() for u in self.used],
            "skipped": [s.to_payload() for s in self.skipped],
        }


class EpisodeConcatBuilder:
    def __init__(self, exposed: ExposedTree, resolver: SafeResolver) -> None:
        self._exposed = exposed
        self._resolver = resolver

    def build(self, rel: str) -> EpisodeConcatResult:
        episode_dir, episode_slug = self._validate_episode(rel)
        shots_dir = episode_dir / "shots"
        if not shots_dir.is_dir():
            raise NoShotsError("episode has no shots/ folder")
        shot_dirs = self._shot_dirs(shots_dir)
        if not shot_dirs:
            raise NoShotsError("shots/ folder contains no shot{NN} subfolders")

        used: list[ShotClip] = []
        skipped: list[ShotSkip] = []
        for shot_dir in shot_dirs:
            clip = self._newest_render(shot_dir)
            if clip is None:
                skipped.append(ShotSkip(shot_dir.name, "no_render_mp4"))
                continue
            used.append(ShotClip(shot_dir.name, self._rel(clip)))

        if not used:
            raise NoShotVideosError("no shot has a renders/ mp4 to concatenate")

        out_path = episode_dir / f"{episode_slug}{_MP4_EXT}"
        self._ffmpeg_concat(
            inputs=[self._resolver.resolve(u.video_rel) for u in used],  # type: ignore[list-item]
            out_path=out_path,
        )
        return EpisodeConcatResult(
            episode_rel=self._rel(episode_dir),
            out_rel=self._rel(out_path),
            used=tuple(used),
            skipped=tuple(skipped),
        )

    def _validate_episode(self, rel: str) -> tuple[Path, str]:
        if not isinstance(rel, str) or rel == "":
            raise InvalidEpisodePathError("path is empty")
        if not self._exposed.is_inside(rel):
            raise InvalidEpisodePathError("path outside sandbox")
        parts = rel.split("/")
        if len(parts) < 4 or parts[0] != "ai_videos" or parts[1].startswith("_"):
            raise NotEpisodePathError("path is not under ai_videos/{drama}/")
        try:
            ep_idx = next(
                i for i in range(1, len(parts) - 1)
                if parts[i] == "episodes" and _EP_DIR_RE.match(parts[i + 1])
            )
        except StopIteration as exc:
            raise NotEpisodePathError("path is not under episodes/ep{NN}/") from exc
        episode_rel = "/".join(parts[: ep_idx + 2])
        resolved = self._resolver.resolve(episode_rel)
        if resolved is None:
            raise InvalidEpisodePathError("episode path failed sandbox resolution")
        if resolved.is_symlink():
            raise InvalidEpisodePathError("symlink is not allowed")
        if not resolved.is_dir():
            raise EpisodeNotFoundError("episode folder does not exist")
        return resolved, parts[ep_idx + 1].lower()

    @staticmethod
    def _shot_dirs(shots_dir: Path) -> list[Path]:
        try:
            entries = sorted(shots_dir.iterdir(), key=lambda p: p.name)
        except OSError:
            return []
        return [
            e for e in entries
            if e.is_dir() and not e.is_symlink() and _SHOT_DIR_RE.match(e.name)
        ]

    @staticmethod
    def _newest_render(shot_dir: Path) -> Path | None:
        """Return the most-recently-modified `.mp4` under `shot_dir/renders/`,
        or None. `archive/` subfolders are excluded; symlinks are skipped."""
        renders = shot_dir / _RENDERS_DIR_NAME
        if not renders.is_dir():
            return None
        candidates: list[Path] = []
        try:
            for entry in renders.rglob(f"*{_MP4_EXT}"):
                if entry.is_symlink() or not entry.is_file():
                    continue
                if entry.suffix.lower() != _MP4_EXT:
                    continue
                if _ARCHIVE_DIR_NAME in entry.relative_to(renders).parts:
                    continue
                candidates.append(entry)
        except OSError:
            return None
        if not candidates:
            return None
        return max(candidates, key=lambda p: (_safe_mtime(p), p.name))

    def _ffmpeg_concat(self, inputs: list[Path], out_path: Path) -> None:
        try:
            ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        except Exception as exc:  # imageio_ffmpeg raises various on failure
            raise EpisodeFfmpegMissingError(str(exc)) from exc

        n = len(inputs)
        has_audio = [self._probe_has_audio(ffmpeg, src) for src in inputs]
        need_null_source = not all(has_audio)
        null_idx = n  # index of the lavfi anullsrc input, if added

        per_segment: list[str] = []
        for i in range(n):
            per_segment.append(
                f"[{i}:v]"
                f"setpts=PTS-STARTPTS,"
                f"scale={_CONCAT_TARGET_W}:{_CONCAT_TARGET_H}:force_original_aspect_ratio=decrease,"
                f"pad={_CONCAT_TARGET_W}:{_CONCAT_TARGET_H}:(ow-iw)/2:(oh-ih)/2:black,"
                f"setsar=1,"
                f"fps={_CONCAT_TARGET_FPS}"
                f"[v{i}]"
            )
            audio_src_idx = i if has_audio[i] else null_idx
            per_segment.append(
                f"[{audio_src_idx}:a]"
                f"asetpts=PTS-STARTPTS,"
                f"aresample=44100,"
                f"aformat=sample_fmts=fltp:channel_layouts=stereo"
                f"[a{i}]"
            )
        concat_pads = "".join(f"[v{i}][a{i}]" for i in range(n))
        concat_node = f"{concat_pads}concat=n={n}:v=1:a=1[outv][outa]"
        filter_complex = ";".join([*per_segment, concat_node])

        cmd: list[str] = [ffmpeg, "-y"]
        for src in inputs:
            cmd.extend(["-i", str(src)])
        if need_null_source:
            cmd.extend([
                "-f", "lavfi",
                "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
            ])
        cmd.extend([
            "-filter_complex", filter_complex,
            "-map", "[outv]",
            "-map", "[outa]",
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "128k",
            "-ar", "44100",
            "-ac", "2",
            "-shortest",
            "-movflags", "+faststart",
            "-loglevel", "error",
            str(out_path),
        ])

        try:
            completed = subprocess.run(
                cmd,
                capture_output=True,
                timeout=_EPISODE_FFMPEG_TIMEOUT_S,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise EpisodeConcatFailedError("ffmpeg_timeout") from exc
        if completed.returncode != 0 or not out_path.is_file():
            err = completed.stderr.decode("utf-8", errors="replace").strip()[:400]
            raise EpisodeConcatFailedError(err or "ffmpeg_failed")

    @staticmethod
    def _probe_has_audio(ffmpeg: str, src: Path) -> bool:
        """Return True iff `src` carries at least one Audio stream.

        `imageio_ffmpeg` doesn't bundle ffprobe, so probe via `ffmpeg -i`
        with no output target — ffmpeg dumps stream metadata to stderr and
        exits non-zero (no output), which is fine for our purpose.
        """
        try:
            result = subprocess.run(
                [ffmpeg, "-i", str(src), "-hide_banner"],
                capture_output=True,
                timeout=15,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return False
        stderr = result.stderr.decode("utf-8", errors="replace")
        for line in stderr.splitlines():
            stripped = line.strip()
            if stripped.startswith("Stream #") and "Audio:" in stripped:
                return True
        return False

    def _rel(self, p: Path) -> str:
        try:
            return p.resolve().relative_to(self._resolver.root).as_posix()
        except (OSError, ValueError):
            return p.as_posix()


def _safe_mtime(p: Path) -> float:
    try:
        return p.stat().st_mtime
    except OSError:
        return 0.0
