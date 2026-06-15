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


def test_chinese_tag_filename_matches_right_shot(tmp_path: Path) -> None:
    """Kling names a render after the first 9 chars of the prompt, i.e. the
    shot block's `{NN}集{NN}镜{视|始|末}` tag. The importer must route those
    into the correct shot's renders/ and NOT confuse shot02 with shot12."""
    root = tmp_path / "repo"
    base = root / "ai_videos" / "td" / "episodes" / "ep01" / "shots"
    (base / "shot02").mkdir(parents=True)
    (base / "shot12").mkdir(parents=True)
    downloads = tmp_path / "Downloads"
    _touch(downloads / "01集02镜视.mp4")   # video → shot02
    _touch(downloads / "01集02镜始.png")   # start frame → shot02
    _touch(downloads / "01集12镜末.png")   # end frame → shot12

    result = _make_importer(root, downloads).import_drama("ai_videos/td")

    assert {e["kind"] for e in result.moved} == {"shot"}, result.moved
    assert result.unmatched == []
    assert (base / "shot02" / "renders" / "01集02镜视.mp4").is_file()
    assert (base / "shot02" / "renders" / "01集02镜始.png").is_file()
    assert (base / "shot12" / "renders" / "01集12镜末.png").is_file()
    # shot02's files did NOT leak into shot12 and vice-versa.
    assert not (base / "shot12" / "renders").exists() or not list(
        (base / "shot12" / "renders").glob("01集02*")
    )


def test_shot_tag_wins_over_embedded_scene_name(tmp_path: Path) -> None:
    """Regression (follow-up wushen_juexing/026): a shot's `参考:` line embeds the
    scene-plate handle it references, so the scene folder name appears in the
    render filename. The shot's compact `{NN}集{NN}镜` tag must still route the
    render into the shot's renders/ — NOT be out-scored by the longer scene token
    and misrouted into scenes/."""
    root = tmp_path / "repo"
    drama = root / "ai_videos" / "td"
    (drama / "episodes" / "ep01" / "shots" / "shot12").mkdir(parents=True)
    (drama / "scenes" / "s4_回忆庭院").mkdir(parents=True)
    downloads = tmp_path / "Downloads"
    # Real-world jimeng name: tag `01集12镜视` followed by the 参考 line which
    # contains the scene handle `s4_回忆庭院·bg1_朝北_正房廊`.
    fname = "jimeng-2026-06-14-4252-01集12镜视 参考_ `裴知秋, 黑衣人(配), s4_回忆庭院·bg1_朝北_正房廊.mp4"
    _touch(downloads / fname)

    result = _make_importer(root, downloads).import_drama("ai_videos/td")

    assert [e["kind"] for e in result.moved] == ["shot"], result.moved
    assert (drama / "episodes" / "ep01" / "shots" / "shot12" / "renders" / fname).is_file()
    # Did NOT leak into the scene folder.
    assert not list((drama / "scenes" / "s4_回忆庭院").rglob("*.mp4"))


def test_scene_plate_routes_by_orientation_token(tmp_path: Path) -> None:
    """Scene background plates live in `scenes/{scene}/bg{N}_{方位}_{desc}/`.
    The out-of-image tool names the download from the prompt's 主体 line, which
    opens with the 方位 word; the importer routes by that 方位 segment into the
    matching plate folder, then renames to the canonical {plate_id}.png."""
    root = tmp_path / "repo"
    scene = root / "ai_videos" / "td" / "scenes" / "s1_hall"
    (scene / "bg1_朝北_主位").mkdir(parents=True)
    (scene / "bg2_朝南_门").mkdir(parents=True)
    downloads = tmp_path / "Downloads"
    _touch(downloads / "hall 朝北视角 reverse 35mm.png")
    _touch(downloads / "hall 朝南视角 28mm.png")

    result = _make_importer(root, downloads).import_drama("ai_videos/td")

    assert {e["kind"] for e in result.moved} == {"scene_plate"}, result.moved
    assert result.unmatched == []
    assert result.errors == []
    assert (scene / "bg1_朝北_主位" / "bg1_朝北_主位.png").is_file()
    assert (scene / "bg2_朝南_门" / "bg2_朝南_门.png").is_file()


def test_scene_plate_reimport_overwrites_and_clears_numbered(tmp_path: Path) -> None:
    """A plate folder holds exactly one canonical image. Re-importing must
    OVERWRITE it and clear stale {plate}1/{plate}2 numbered leftovers (from a
    prior move-then-rename collision), not accumulate duplicates. The co-located
    prompt .md must survive (non-media)."""
    root = tmp_path / "repo"
    plate = root / "ai_videos" / "td" / "scenes" / "s1_hall" / "bg1_朝北_主位"
    plate.mkdir(parents=True)
    (plate / "bg1_朝北_主位.md").write_bytes(b"PROMPT")       # must survive
    (plate / "bg1_朝北_主位.png").write_bytes(b"OLD")          # stale canonical
    (plate / "bg1_朝北_主位1.png").write_bytes(b"OLD1")        # numbered junk
    (plate / "bg1_朝北_主位2.png").write_bytes(b"OLD2")        # numbered junk
    downloads = tmp_path / "Downloads"
    downloads.mkdir(parents=True)
    (downloads / "hall 朝北视角 fresh render.png").write_bytes(b"NEW")

    result = _make_importer(root, downloads).import_drama("ai_videos/td")

    assert [e["kind"] for e in result.moved] == ["scene_plate"], result.moved
    assert result.errors == []
    assert sorted(p.name for p in plate.iterdir()) == [
        "bg1_朝北_主位.md",
        "bg1_朝北_主位.png",
    ]
    assert (plate / "bg1_朝北_主位.png").read_bytes() == b"NEW"  # overwritten


def test_unrelated_file_lands_in_not_matched(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    (root / "ai_videos" / "td" / "episodes" / "ep01" / "shots" / "shot01").mkdir(parents=True)
    downloads = tmp_path / "Downloads"
    _touch(downloads / "totally_unrelated.png")

    result = _make_importer(root, downloads).import_drama("ai_videos/td")

    assert result.moved == []
    assert [e["kind"] for e in result.unmatched] == ["unmatched"]
    assert (root / "ai_videos" / "td" / "not_matched" / "totally_unrelated.png").is_file()
