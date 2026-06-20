"""Pick a shot's canonical raw render.

Shared by episode concat (`episode__writer`) and batch subtitle burn
(`subtitle_batch__writer`) so both ALWAYS select the SAME take when a shot's
`renders/` folder holds several: the NEWEST by modification time, with the file
name as a stable tie-break. `archive/` takes and symlinks are excluded.

Centralising this guarantees the two call sites can't drift — "newest wins" is
defined once.
"""
from __future__ import annotations

from pathlib import Path

RENDERS_DIR_NAME = "renders"
ARCHIVE_DIR_NAME = "archive"
_MP4_EXT = ".mp4"


def newest_render(shot_dir: Path) -> Path | None:
    """The most-recently-modified `.mp4` under `shot_dir/renders/`, or None.

    `archive/` subfolders are excluded; symlinks are skipped. Ties on mtime
    break on file name so selection is deterministic."""
    renders = shot_dir / RENDERS_DIR_NAME
    if not renders.is_dir():
        return None
    candidates: list[Path] = []
    try:
        for entry in renders.rglob(f"*{_MP4_EXT}"):
            if entry.is_symlink() or not entry.is_file():
                continue
            if entry.suffix.lower() != _MP4_EXT:
                continue
            if ARCHIVE_DIR_NAME in entry.relative_to(renders).parts:
                continue
            candidates.append(entry)
    except OSError:
        return None
    if not candidates:
        return None
    return max(candidates, key=lambda p: (_safe_mtime(p), p.name))


def _safe_mtime(p: Path) -> float:
    try:
        return p.stat().st_mtime
    except OSError:
        return 0.0
