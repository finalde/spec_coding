"""Per-video frame extraction for scene reference videos.

Extracts 8 reference frames from a 15s walk-through scene mp4 (per
`.claude/agent_refs/project/ai_video.md` rule #12.10 v3): the 5 canonical
dwell anchors (hero / reverse / vert / mid / detail) plus 3 strategic
transition frames (side / threequarter / mediumclose) filling the
orthogonal-angle and focal-length gaps the 5 dwells alone leave open.

Output convention: PNGs land in a `frames/` subfolder of the source's
parent directory. The filename prefix is the **parent directory name**
(the scene folder), NOT the mp4 stem, so any mp4 take in the same scene
folder overwrites the same 8 PNGs on re-extract — only the latest
extraction survives. Filenames embed a priority rank so lexicographic
sort matches upload priority:

  {src.parent}/frames/{src.parent.name}_r{rank}_{role}_{shot_size}.png

Rank semantics: r1 is the single most useful reference image; r1+r2+r3
together cover the three most distinct focal scales (medium / wide /
telephoto). r4–r5 are secondary axes (reverse / vert); r6–r8 are
transition frames that bridge angle and focal-length gaps.

On every extract, the `frames/` subfolder is swept of all `*.png` files
(non-recursive) before writing — so legacy v1 (`_f{N}_{role}.png`) files
and any `MediaRenamer`-mangled `frames{N}.png` residue from before
follow-up 041 are cleaned up automatically.

ffmpeg binary is supplied by the `imageio-ffmpeg` wheel — no system install.
"""
from __future__ import annotations

import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

import imageio_ffmpeg

from libs.common.exposed_tree import ExposedTree
from libs.common.safe_resolve import SafeResolver
from libs.domain.errors.frame__error import (
    FfmpegMissingError,
    FrameExtractFailedError,
    InvalidVideoPathError,
    NotVideoError,
    VideoNotFoundError,
)

VIDEO_EXTENSIONS: frozenset[str] = frozenset(
    {".mp4", ".mov", ".webm", ".mkv", ".avi", ".m4v"}
)

# (timestamp_seconds, role, shot_size, rank)
# Order is by timestamp (sequential ffmpeg seek = fast); the rank field
# is the upload-priority order, not the iteration order.
CANONICAL_FRAMES: tuple[tuple[float, str, str, int], ...] = (
    (0.5,  "hero",         "wide",      2),
    (2.5,  "side",         "wide",      6),
    (4.4,  "reverse",      "wide",      4),
    (7.9,  "vert",         "wide",      5),
    (10.0, "threequarter", "oblique",   7),
    (11.4, "mid",          "medium",    1),
    (13.0, "mediumclose",  "medium",    8),
    (14.6, "detail",       "telephoto", 3),
)

_FFMPEG_TIMEOUT_S: int = 30
FRAMES_SUBDIR: str = "frames"
RENDERS_DIR_NAME: str = "renders"
_SHOT_DIR_RE = re.compile(r"^shot\d+$", re.IGNORECASE)
# Decode only the tail of the clip; `-sseof -N` seeks N seconds before EOF.
_LASTFRAME_TAIL_S: int = 3


@dataclass(frozen=True)
class FrameResult:
    timestamp: float
    role: str
    shot_size: str
    rank: int
    out_rel: str

    def to_payload(self) -> dict[str, object]:
        return {
            "timestamp": self.timestamp,
            "role": self.role,
            "shot_size": self.shot_size,
            "rank": self.rank,
            "path": self.out_rel,
        }


@dataclass(frozen=True)
class ExtractResult:
    src_rel: str
    frames: tuple[FrameResult, ...]
    failures: tuple[tuple[float, str, str], ...]  # (timestamp, role, error_msg)

    def to_payload(self) -> dict[str, object]:
        return {
            "src": self.src_rel,
            "frames": [f.to_payload() for f in self.frames],
            "failures": [
                {"timestamp": t, "role": r, "error": e}
                for (t, r, e) in self.failures
            ],
        }


@dataclass(frozen=True)
class LastFrameResult:
    src_rel: str
    out_rel: str
    # The same PNG copied into the NEXT shot's folder as its first frame, or
    # None when there is no next shot (last shot of the episode).
    first_frame_rel: str | None

    def to_payload(self) -> dict[str, object]:
        return {
            "src": self.src_rel,
            "out": self.out_rel,
            "first_frame": self.first_frame_rel,
        }


class FrameExtractor:
    def __init__(self, exposed: ExposedTree, resolver: SafeResolver) -> None:
        self._exposed = exposed
        self._resolver = resolver

    def extract_last_frame(self, rel: str) -> LastFrameResult:
        """Extract the FINAL frame of a shot render to `{shot}/{shot}_lastframe.png`.

        This is the cross-shot continuity-frame source (ai_video.md 2026-06-21
        跨镜首帧承接): a 承接 shot's first frame = the previous shot's rendered
        last frame. The PNG lands at the shot-folder ROOT so the user can upload
        it as the next shot's first frame. A re-extract overwrites it.

        It is ALSO copied into the next shot's folder as `{nextshot}_firstframe.png`
        so the 承接 hand-off happens in one click — no manual copy. When there is
        no next shot (last shot of the episode), only the lastframe is written.

        ffmpeg trick: `-sseof -N` decodes only the last N seconds; `-update 1`
        rewrites the same PNG for every decoded frame, so the file is left
        holding the LAST decoded frame = the actual final frame."""
        src = self._validate_video_source(rel)
        try:
            ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        except Exception as exc:  # imageio_ffmpeg raises various on failure
            raise FfmpegMissingError(str(exc)) from exc
        shot_folder = self._shot_folder(src)
        out_path = shot_folder / f"{shot_folder.name}_lastframe.png"
        cmd = [
            ffmpeg,
            "-y",
            "-sseof", f"-{_LASTFRAME_TAIL_S}",
            "-i", str(src),
            "-update", "1",
            "-q:v", "1",
            "-loglevel", "error",
            str(out_path),
        ]
        try:
            completed = subprocess.run(
                cmd, capture_output=True, timeout=_FFMPEG_TIMEOUT_S, check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise FrameExtractFailedError("ffmpeg_timeout") from exc
        if completed.returncode != 0 or not out_path.is_file():
            err = completed.stderr.decode("utf-8", errors="replace").strip()[:200]
            raise FrameExtractFailedError(err or "ffmpeg_failed")
        first_frame_rel = self._copy_to_next_shot_firstframe(shot_folder, out_path)
        return LastFrameResult(
            src_rel=self._rel(src),
            out_rel=self._rel(out_path),
            first_frame_rel=first_frame_rel,
        )

    def _copy_to_next_shot_firstframe(
        self, shot_folder: Path, last_frame: Path
    ) -> str | None:
        """Copy the just-written last frame into the next shot's folder as
        `{nextshot}_firstframe.png`. Returns its rel path, or None when there is
        no `shotNN` / no next shot folder."""
        next_shot = self._next_shot_folder(shot_folder)
        if next_shot is None:
            return None
        dest = next_shot / f"{next_shot.name}_firstframe.png"
        try:
            shutil.copy2(str(last_frame), str(dest))
        except OSError as exc:
            raise FrameExtractFailedError(f"firstframe copy failed: {exc}") from exc
        return self._rel(dest)

    def _next_shot_folder(self, shot_folder: Path) -> Path | None:
        """Sibling `shotNN` folder whose number is exactly one more than
        `shot_folder`'s. Matches by numeric value, so zero-padding differences
        (shot09 → shot10) resolve correctly. None if `shot_folder` is not a
        `shotNN` dir or no such next sibling exists."""
        m = re.match(r"^shot(\d+)$", shot_folder.name, re.IGNORECASE)
        if m is None:
            return None
        target = int(m.group(1)) + 1
        try:
            siblings = list(shot_folder.parent.iterdir())
        except OSError:
            return None
        for sib in siblings:
            if not sib.is_dir() or sib.is_symlink():
                continue
            sm = re.match(r"^shot(\d+)$", sib.name, re.IGNORECASE)
            if sm is not None and int(sm.group(1)) == target:
                return sib
        return None

    def _shot_folder(self, src: Path) -> Path:
        """Nearest `shotNN` ancestor (output lands at the shot ROOT, never under
        `renders/`). Falls back to the source's own folder for non-shot videos."""
        for anc in (src.parent, *src.parent.parents):
            if _SHOT_DIR_RE.match(anc.name):
                return anc
        if src.parent.name == RENDERS_DIR_NAME:
            return src.parent.parent
        return src.parent

    def extract(self, rel: str) -> ExtractResult:
        src = self._validate_video_source(rel)
        try:
            ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        except Exception as exc:  # imageio_ffmpeg raises various on failure
            raise FfmpegMissingError(str(exc)) from exc
        # Prefix = scene folder name (parent dir), so any mp4 take in the
        # same folder overwrites the same set of PNGs on re-extract.
        prefix = src.parent.name
        out_dir = src.parent / FRAMES_SUBDIR
        try:
            out_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise FrameExtractFailedError(f"could not create frames dir: {exc}") from exc
        self._sweep_pngs(out_dir)
        frames: list[FrameResult] = []
        failures: list[tuple[float, str, str]] = []
        for t, role, shot_size, rank in CANONICAL_FRAMES:
            out_path = out_dir / f"{prefix}_r{rank}_{role}_{shot_size}.png"
            cmd = [
                ffmpeg,
                "-y",                  # overwrite output
                "-ss", f"{t}",         # seek before -i for fast seek
                "-i", str(src),
                "-frames:v", "1",
                "-q:v", "1",           # PNG: q is ignored but harmless
                "-loglevel", "error",
                str(out_path),
            ]
            try:
                completed = subprocess.run(
                    cmd,
                    capture_output=True,
                    timeout=_FFMPEG_TIMEOUT_S,
                    check=False,
                )
            except subprocess.TimeoutExpired:
                failures.append((t, role, "ffmpeg_timeout"))
                continue
            if completed.returncode != 0 or not out_path.is_file():
                err = completed.stderr.decode("utf-8", errors="replace").strip()[:200]
                failures.append((t, role, err or "ffmpeg_failed"))
                continue
            frames.append(
                FrameResult(
                    timestamp=t,
                    role=role,
                    shot_size=shot_size,
                    rank=rank,
                    out_rel=self._rel(out_path),
                )
            )
        if not frames:
            joined = "; ".join(f"t={t}: {e}" for (t, _r, e) in failures)
            raise FrameExtractFailedError(joined or "no frames produced")
        return ExtractResult(
            src_rel=self._rel(src),
            frames=tuple(frames),
            failures=tuple(failures),
        )

    def _sweep_pngs(self, frames_dir: Path) -> None:
        try:
            entries = list(frames_dir.iterdir())
        except OSError:
            return
        for entry in entries:
            if entry.is_symlink() or not entry.is_file():
                continue
            if entry.suffix.lower() != ".png":
                continue
            try:
                entry.unlink()
            except OSError:
                continue

    def _validate_video_source(self, rel: str) -> Path:
        if not isinstance(rel, str) or rel == "":
            raise InvalidVideoPathError("path is empty")
        if not self._exposed.is_inside(rel):
            raise VideoNotFoundError("path outside sandbox")
        ext = Path(rel).suffix.lower()
        if ext not in VIDEO_EXTENSIONS:
            raise NotVideoError("extension is not a video type")
        resolved = self._resolver.resolve(rel)
        if resolved is None or not resolved.is_file():
            raise VideoNotFoundError("file does not exist")
        if resolved.is_symlink():
            raise VideoNotFoundError("symlink is not allowed")
        return resolved

    def _rel(self, p: Path) -> str:
        try:
            return p.resolve().relative_to(self._resolver.root).as_posix()
        except (OSError, ValueError):
            return p.as_posix()
