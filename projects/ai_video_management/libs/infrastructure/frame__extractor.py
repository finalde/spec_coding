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

import subprocess
from dataclasses import dataclass
from pathlib import Path

import imageio_ffmpeg

from libs.common.exposed_tree import ExposedTree
from libs.common.safe_resolve import SafeResolver

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


class InvalidPath(Exception):
    pass


class NotFound(Exception):
    pass


class NotVideo(Exception):
    pass


class FfmpegMissing(Exception):
    pass


class ExtractFailed(Exception):
    """Raised when every frame extraction failed."""


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


class FrameExtractor:
    def __init__(self, exposed: ExposedTree, resolver: SafeResolver) -> None:
        self._exposed = exposed
        self._resolver = resolver

    def extract(self, rel: str) -> ExtractResult:
        src = self._validate_video_source(rel)
        try:
            ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        except Exception as exc:  # imageio_ffmpeg raises various on failure
            raise FfmpegMissing(str(exc)) from exc
        # Prefix = scene folder name (parent dir), so any mp4 take in the
        # same folder overwrites the same set of PNGs on re-extract.
        prefix = src.parent.name
        out_dir = src.parent / FRAMES_SUBDIR
        try:
            out_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise ExtractFailed(f"could not create frames dir: {exc}") from exc
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
            raise ExtractFailed(joined or "no frames produced")
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
            raise InvalidPath("path is empty")
        if not self._exposed.is_inside(rel):
            raise NotFound("path outside sandbox")
        ext = Path(rel).suffix.lower()
        if ext not in VIDEO_EXTENSIONS:
            raise NotVideo("extension is not a video type")
        resolved = self._resolver.resolve(rel)
        if resolved is None or not resolved.is_file():
            raise NotFound("file does not exist")
        if resolved.is_symlink():
            raise NotFound("symlink is not allowed")
        return resolved

    def _rel(self, p: Path) -> str:
        try:
            return p.resolve().relative_to(self._resolver.root).as_posix()
        except (OSError, ValueError):
            return p.as_posix()
