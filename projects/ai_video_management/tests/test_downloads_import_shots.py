"""DownloadsImporter routes shot-generated media into episodes/*/shots/shot*/renders/.

Regression guard for the `prompts/` → `shots/` rename (ai_video rule 2 v3) and
the renders/ subfolder routing: generated images/videos must land in the shot's
`renders/` subfolder with their ORIGINAL filenames preserved (so a shot's
start-frame / end-frame / video coexist without colliding), and the trailing
rename pass must NOT touch them.
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


def test_import_routes_into_renders_keeping_original_names(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    shot_dir = root / "ai_videos" / "td" / "episodes" / "ep01" / "shots" / "shot01"
    _touch(shot_dir / "shot01.md")  # the shot prompt file co-located
    downloads = tmp_path / "Downloads"
    _touch(downloads / "ep01_shot01_start.png")
    _touch(downloads / "ep01_shot01_end.png")
    _touch(downloads / "ep01_shot01.mp4")

    result = _make_importer(root, downloads).import_drama("ai_videos/td")

    assert {e["kind"] for e in result.moved} == {"shot"}, result.moved
    assert result.unmatched == []
    assert result.errors == []
    renders = shot_dir / "renders"
    # Both frame images AND the video land in renders/, original names intact.
    assert (renders / "ep01_shot01_start.png").is_file()
    assert (renders / "ep01_shot01_end.png").is_file()
    assert (renders / "ep01_shot01.mp4").is_file()
    # Not renamed to canonical shot01.* and NOT left in the shot folder root.
    assert not (shot_dir / "shot01.png").exists()
    assert not (renders / "shot01.png").exists()
    assert sorted(p.name for p in renders.iterdir()) == [
        "ep01_shot01.mp4",
        "ep01_shot01_end.png",
        "ep01_shot01_start.png",
    ]


def test_legacy_prompts_folder_still_accepted(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    shot_dir = root / "ai_videos" / "td" / "episodes" / "ep01" / "prompts" / "shot01"
    shot_dir.mkdir(parents=True)
    downloads = tmp_path / "Downloads"
    _touch(downloads / "ep01_shot01.png")

    result = _make_importer(root, downloads).import_drama("ai_videos/td")

    assert [e["kind"] for e in result.moved] == ["shot"]
    assert (shot_dir / "renders" / "ep01_shot01.png").is_file()


def test_unrelated_file_lands_in_not_matched(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    (root / "ai_videos" / "td" / "episodes" / "ep01" / "shots" / "shot01").mkdir(parents=True)
    downloads = tmp_path / "Downloads"
    _touch(downloads / "totally_unrelated.png")

    result = _make_importer(root, downloads).import_drama("ai_videos/td")

    assert result.moved == []
    assert [e["kind"] for e in result.unmatched] == ["unmatched"]
    assert (root / "ai_videos" / "td" / "not_matched" / "totally_unrelated.png").is_file()
