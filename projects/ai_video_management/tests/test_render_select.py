"""newest_render — the shared "newest take wins" selector used by both episode
concat and batch subtitle burn."""
from __future__ import annotations

import os
from pathlib import Path

from libs.common.render_select import newest_render


def _touch(p: Path, mtime: float) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(b"x")
    os.utime(p, (mtime, mtime))


def test_picks_newest_by_mtime(tmp_path: Path) -> None:
    shot = tmp_path / "shot01"
    renders = shot / "renders"
    _touch(renders / "take_a.mp4", 1000.0)
    _touch(renders / "take_b.mp4", 3000.0)  # newest
    _touch(renders / "take_c.mp4", 2000.0)
    assert newest_render(shot) == (renders / "take_b.mp4")


def test_excludes_archive_and_non_mp4(tmp_path: Path) -> None:
    shot = tmp_path / "shot01"
    renders = shot / "renders"
    _touch(renders / "old.mp4", 1000.0)
    _touch(renders / "archive" / "newer_but_archived.mp4", 9000.0)  # excluded
    _touch(renders / "newest.txt", 9999.0)  # not mp4
    assert newest_render(shot) == (renders / "old.mp4")


def test_none_when_no_renders(tmp_path: Path) -> None:
    assert newest_render(tmp_path / "shot01") is None
    (tmp_path / "shot02" / "renders").mkdir(parents=True)
    assert newest_render(tmp_path / "shot02") is None
