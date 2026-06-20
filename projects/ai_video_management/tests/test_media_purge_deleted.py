"""purge_deleted empties the whole ai_videos/_deleted/ recycle bin — every
file type (md / json / media) plus all subfolders — unlike hard_delete which
only unlinks a single media leaf and left .md sidecars + empty dirs behind."""
from __future__ import annotations

from pathlib import Path

from libs.common.exposed_tree import ExposedTree
from libs.common.safe_resolve import SafeResolver
from libs.infrastructure.writers.media__writer import MediaArchiver


def _archiver(root: Path) -> MediaArchiver:
    return MediaArchiver(ExposedTree(root), SafeResolver(root))


def _seed_deleted(root: Path) -> None:
    base = root / "ai_videos" / "_deleted" / "_actors" / "actor_0001"
    base.mkdir(parents=True)
    (base / "actor_0001.md").write_text("# actor", encoding="utf-8")
    (base / "face.jpg").write_bytes(b"\xff\xd8\xff")
    (root / "ai_videos" / "_deleted" / "drama" / "ep01").mkdir(parents=True)
    (root / "ai_videos" / "_deleted" / "drama" / "ep01" / "shot.mp4").write_bytes(b"\x00")


def test_purge_deleted_removes_everything(tmp_path: Path) -> None:
    _seed_deleted(tmp_path)
    deleted_root = tmp_path / "ai_videos" / "_deleted"
    assert deleted_root.is_dir()

    count = _archiver(tmp_path).purge_deleted()

    assert count == 3
    assert not deleted_root.exists()


def test_purge_deleted_on_empty_bin_is_noop(tmp_path: Path) -> None:
    (tmp_path / "ai_videos").mkdir(parents=True)
    assert _archiver(tmp_path).purge_deleted() == 0
