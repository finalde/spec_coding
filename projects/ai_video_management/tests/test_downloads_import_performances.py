"""DownloadsImporter routes performance-library renders into
`_performances/{emotion}/perf_{NNNN}/` by the `演{NNNN}{克|即|始}` import tag,
renaming each to its canonical name. Guards the one-click import flow for the
表演演技库 (per `_performances/_testrig.md`).
"""
from __future__ import annotations

from pathlib import Path

from libs.common.exposed_tree import ExposedTree
from libs.common.safe_resolve import SafeResolver
from libs.infrastructure.writers.downloads__writer import DownloadsImporter
from libs.infrastructure.writers.media__writer import MediaRenamer


def _make_importer(root: Path, downloads: Path) -> DownloadsImporter:
    exposed = ExposedTree(root)
    resolver = SafeResolver(root)
    renamer = MediaRenamer(exposed, resolver)
    return DownloadsImporter(exposed, resolver, renamer, downloads_dir=downloads)


def _touch(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"x")


def _perf_root(root: Path) -> Path:
    base = root / "ai_videos" / "_performances"
    # two emotions, a few perf folders (only the entry md needs to exist)
    _touch(base / "yayi_yinren" / "perf_0003" / "perf_0003.md")
    _touch(base / "yayi_yinren" / "perf_0001" / "perf_0001.md")
    _touch(base / "shuanggan_fanzhuan" / "perf_0021" / "perf_0021.md")
    return base


def test_import_routes_by_tag(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    _perf_root(root)
    downloads = tmp_path / "Downloads"
    # ONE generic prompt per entry → one video tag `演{NNNN}`; the user may render
    # it on several models, whose downloads coexist in renders/ by original name.
    _touch(downloads / "演0003_kling_8f21a.mp4")    # one model's video for perf_0003
    _touch(downloads / "演0003_seedance_3c0b.mp4")  # another model's video, same entry
    _touch(downloads / "演0001始_aa11.png")          # startframe still for perf_0001
    _touch(downloads / "演0021_zzz.mp4")             # video for perf_0021 (other emotion)

    result = _make_importer(root, downloads).import_performances("ai_videos/_performances")

    assert result.errors == [], result.errors
    assert result.unmatched == [], result.unmatched
    base = root / "ai_videos" / "_performances"
    # both model renders coexist in renders/ with original names
    assert (base / "yayi_yinren" / "perf_0003" / "renders" / "演0003_kling_8f21a.mp4").is_file()
    assert (base / "yayi_yinren" / "perf_0003" / "renders" / "演0003_seedance_3c0b.mp4").is_file()
    # startframe renamed to canonical reference name
    assert (base / "yayi_yinren" / "perf_0001" / "perf_0001__startframe.png").is_file()
    assert (base / "shuanggan_fanzhuan" / "perf_0021" / "renders" / "演0021_zzz.mp4").is_file()
    assert {e["kind"] for e in result.moved} == {"performance_video", "performance_startframe"}


def test_unmatched_is_not_imported(tmp_path: Path) -> None:
    """Unmatched downloads are reported but NOT imported — left in Downloads,
    no `_not_matched/` folder is created."""
    root = tmp_path / "repo"
    _perf_root(root)
    downloads = tmp_path / "Downloads"
    _touch(downloads / "random_clip.mp4")          # no tag
    _touch(downloads / "演9999克_x.mp4")            # tag for a perf that doesn't exist

    result = _make_importer(root, downloads).import_performances("ai_videos/_performances")

    assert result.moved == []
    assert {e["kind"] for e in result.unmatched} == {"unmatched"}
    base = root / "ai_videos" / "_performances"
    assert not (base / "_not_matched").exists()
    assert (downloads / "random_clip.mp4").is_file()
    assert (downloads / "演9999克_x.mp4").is_file()


def test_reimport_overwrites_startframe_canonical(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    base = _perf_root(root)
    existing = base / "yayi_yinren" / "perf_0001" / "perf_0001__startframe.png"
    _touch(existing)
    existing.write_bytes(b"old")
    downloads = tmp_path / "Downloads"
    new = downloads / "演0001始_new.png"
    _touch(new)
    new.write_bytes(b"new-frame")

    result = _make_importer(root, downloads).import_performances("ai_videos/_performances")

    assert result.errors == []
    assert existing.read_bytes() == b"new-frame"
    assert len(result.moved) == 1
