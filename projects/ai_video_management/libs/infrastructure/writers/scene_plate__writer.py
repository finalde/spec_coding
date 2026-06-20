"""Extract per-direction scene background plates from a scene walk-through mp4.

The scene walk-through video (`scenes/{scene}/*.mp4`) pans through fixed compass
directions on a fixed per-second timeline; this extractor grabs the frame at
each direction's dwell-midpoint and writes it into the matching
`bg{N}_{方位}_*/` sub-folder as that plate's PNG — so each shot can upload the
correct-direction background板.

Canonical direction → timepoint (MUST match the scene video prompt timeline
authored in `scenes/{scene}/{scene}.md` 步骤二):

  北 @1.5s · 东 @4.5s · 南 @7.5s · 西 @10.5s · 中/俯瞰 @13.5s

i.e. a 15s walk-through of 5 dwells (3s each), camera held steady on each
direction, frame grabbed at each dwell's midpoint. The video and this map are
two halves of one contract: if the video's per-second orientation changes, this
map must change with it (and vice-versa), else the grabbed frame won't be
on-direction.

ffmpeg binary is supplied by the `imageio-ffmpeg` wheel — no system install.
"""
from __future__ import annotations

import re
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
from libs.infrastructure.writers.frame__writer import VIDEO_EXTENSIONS

# Direction → (matching tokens, dwell-midpoint seconds). A bg folder is routed
# to a direction if its name contains any of that direction's tokens. Order is
# the canonical compass order; `中` also matches the overhead/center dwell.
DIRECTION_TIMEPOINTS: tuple[tuple[str, tuple[str, ...], float], ...] = (
    ("北", ("北",), 1.5),
    ("东", ("东",), 4.5),
    ("南", ("南",), 7.5),
    ("西", ("西",), 10.5),
    ("中", ("中", "俯瞰", "高位"), 13.5),
)

_BG_DIR_RE = re.compile(r"^bg\d+_")
_FFMPEG_TIMEOUT_S: int = 30

# A full plate-folder token inside the scene md index table, e.g.
# `bg1_朝北_高座主位`. Requires at least one `_{描述}` segment after the number
# so a bare `bg1` name-dropped in prose does NOT match (only the canonical
# folder ids do). Stops at table/markdown delimiters and CJK punctuation.
_PLATE_TOKEN_RE = re.compile(r"bg\d+(?:_[^\s`/|、，（）()]+)+")
# First `N` / `N.N` seconds value in a cell (the 截帧时点 column holds `1.5s`).
_SECONDS_RE = re.compile(r"(\d+(?:\.\d+)?)\s*s")


def _split_md_row(line: str) -> list[str]:
    stripped = line.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    return [c.strip() for c in stripped.split("|")]


def _first_seconds(cell: str) -> float | None:
    m = _SECONDS_RE.search(cell)
    return float(m.group(1)) if m is not None else None


@dataclass(frozen=True)
class PlateResult:
    folder: str          # bg folder name
    direction: str       # 北/东/南/西/中
    timestamp: float
    out_rel: str

    def to_payload(self) -> dict[str, object]:
        return {
            "folder": self.folder,
            "direction": self.direction,
            "timestamp": self.timestamp,
            "path": self.out_rel,
        }


@dataclass(frozen=True)
class ScenePlateResult:
    src_rel: str
    plates: tuple[PlateResult, ...]
    skipped: tuple[str, ...]                       # bg folders no direction matched
    failures: tuple[tuple[str, str], ...]          # (folder, error)

    def to_payload(self) -> dict[str, object]:
        return {
            "src": self.src_rel,
            "plates": [p.to_payload() for p in self.plates],
            "skipped": list(self.skipped),
            "failures": [{"folder": f, "error": e} for (f, e) in self.failures],
        }


class ScenePlateExtractor:
    def __init__(self, exposed: ExposedTree, resolver: SafeResolver) -> None:
        self._exposed = exposed
        self._resolver = resolver

    def extract(self, rel: str) -> ScenePlateResult:
        src = self._validate_video_source(rel)
        scene_dir = src.parent
        bg_dirs = self._find_bg_dirs(scene_dir)
        if not bg_dirs:
            raise FrameExtractFailedError(
                "no bg{N}_{方位}_ direction folders found next to the video"
            )
        try:
            ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        except Exception as exc:
            raise FfmpegMissingError(str(exc)) from exc

        scene_timepoints = self._parse_scene_timepoints(scene_dir)
        plates: list[PlateResult] = []
        skipped: list[str] = []
        failures: list[tuple[str, str]] = []
        for d in bg_dirs:
            routed = self._route_direction(d.name)
            table_t = scene_timepoints.get(d.name)
            if routed is not None:
                direction, default_t = routed
                # The scene md's 背景图系统 index table is the per-scene source
                # of truth for 截帧时点 (the walk-through dwell order is authored
                # per scene; the global compass map is only a fallback).
                t = table_t if table_t is not None else default_t
            elif table_t is not None:
                # Folder not compass-routable (e.g. 座前 虚化背景) but the scene
                # table assigns it a dwell timepoint → extract at that second.
                direction = self._direction_segment(d.name)
                t = table_t
            else:
                skipped.append(d.name)
                continue
            out_path = d / f"{d.name}.png"
            cmd = [
                ffmpeg, "-y",
                "-ss", f"{t}",
                "-i", str(src),
                "-frames:v", "1",
                "-q:v", "1",
                "-loglevel", "error",
                str(out_path),
            ]
            try:
                completed = subprocess.run(
                    cmd, capture_output=True, timeout=_FFMPEG_TIMEOUT_S, check=False,
                )
            except subprocess.TimeoutExpired:
                failures.append((d.name, "ffmpeg_timeout"))
                continue
            if completed.returncode != 0 or not out_path.is_file():
                err = completed.stderr.decode("utf-8", errors="replace").strip()[:200]
                failures.append((d.name, err or "ffmpeg_failed"))
                continue
            plates.append(PlateResult(
                folder=d.name, direction=direction, timestamp=t, out_rel=self._rel(out_path),
            ))
        if not plates:
            joined = "; ".join(f"{f}: {e}" for (f, e) in failures) or "no plates produced"
            raise FrameExtractFailedError(joined)
        return ScenePlateResult(
            src_rel=self._rel(src),
            plates=tuple(plates),
            skipped=tuple(skipped),
            failures=tuple(failures),
        )

    @staticmethod
    def _route_direction(folder_name: str) -> tuple[str, float] | None:
        for direction, tokens, t in DIRECTION_TIMEPOINTS:
            if any(tok in folder_name for tok in tokens):
                return direction, t
        return None

    @staticmethod
    def _direction_segment(folder_name: str) -> str:
        """The 方位 segment of a `bg{N}_{方位}_{描述}` folder name (first token
        after the `bg\\d+_` prefix), used as the display direction when the name
        isn't compass-routable (e.g. `bg6_座前_虚化背景` → `座前`)."""
        rest = _BG_DIR_RE.sub("", folder_name)
        return rest.split("_", 1)[0] if rest else folder_name

    def _parse_scene_timepoints(self, scene_dir: Path) -> dict[str, float]:
        """Read the scene md's `背景图系统 index（… 截帧时点 …）` table and return
        `{bg_folder_name: 截帧时点_seconds}`.

        This table is the per-scene contract that keeps THIS extractor's grab
        seconds in lock-step with the walk-through video prompt authored in the
        same file (步骤二). The dwell order — and therefore which compass
        direction sits at which second — is chosen per scene (the 5 dwells are
        framing-roles: hero/reverse/vert/mid/detail), so a global compass map
        can't stay consistent; the table can. Best-effort: any parse failure
        returns `{}` and the caller falls back to the compass default.
        """
        scene_md = scene_dir / f"{scene_dir.name}.md"
        try:
            text = scene_md.read_text(encoding="utf-8")
        except OSError:
            return {}
        lines = text.splitlines()
        # Locate the table header row carrying a 截帧时点 column.
        header_idx: int | None = None
        time_col: int | None = None
        for i, ln in enumerate(lines):
            if "|" not in ln or "截帧时点" not in ln:
                continue
            cells = _split_md_row(ln)
            for j, c in enumerate(cells):
                if "截帧时点" in c:
                    header_idx, time_col = i, j
                    break
            if header_idx is not None:
                break
        if header_idx is None or time_col is None:
            return {}
        out: dict[str, float] = {}
        # Data rows start two lines down (skip the `---` separator row).
        for ln in lines[header_idx + 2:]:
            if "|" not in ln:
                break
            cells = _split_md_row(ln)
            if time_col >= len(cells):
                continue
            t = _first_seconds(cells[time_col])
            if t is None:
                continue
            for token in _PLATE_TOKEN_RE.findall(cells[0]):
                # Keep the first timepoint seen per folder (a folder may be
                # name-dropped in a later row's prose — e.g. `/ bg1 中景`).
                out.setdefault(token, t)
        return out

    def _find_bg_dirs(self, scene_dir: Path) -> list[Path]:
        try:
            entries = sorted(scene_dir.iterdir(), key=lambda p: p.name)
        except OSError:
            return []
        return [
            d for d in entries
            if d.is_dir() and not d.is_symlink() and _BG_DIR_RE.match(d.name)
        ]

    def _validate_video_source(self, rel: str) -> Path:
        if not isinstance(rel, str) or rel == "":
            raise InvalidVideoPathError("path is empty")
        if not self._exposed.is_inside(rel):
            raise VideoNotFoundError("path outside sandbox")
        if Path(rel).suffix.lower() not in VIDEO_EXTENSIONS:
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
