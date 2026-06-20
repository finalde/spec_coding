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


def test_scene_plate_routes_by_orientation_when_no_scene_token(tmp_path: Path) -> None:
    """Real-world: kling truncates the download to the prompt's first ~10 chars.
    For a plate prompt whose first line is the plate_id (`bg{N}_{方位}_…`) the
    EARLY 方位 survives but the pinyin scene handle (`zhenbei_wangfu_zhengting`)
    does NOT — so the filename has a 方位 token but no scene-name token. The
    importer must still route it to the matching plate folder by 方位 alone."""
    root = tmp_path / "repo"
    scene = root / "ai_videos" / "wushen" / "2_世界观人设" / "scenes" / "zhenbei_wangfu_zhengting"
    for p in ["bg1_朝北_高座主位", "bg2_朝南_厅门", "bg3_朝东_东侧列柱",
              "bg4_朝西_西窗", "bg5_高位俯瞰", "bg6_座前_虚化背景"]:
        (scene / p).mkdir(parents=True)
    downloads = tmp_path / "Downloads"
    # exact kling truncation shapes observed in the field (no scene handle):
    _touch(downloads / "kling_20260619_IMAGE_bg1_朝北_高座主_3614_1.png")
    _touch(downloads / "kling_20260619_IMAGE_bg2_朝南_厅门参_3610_6.png")
    _touch(downloads / "kling_20260619_IMAGE_bg3_朝东_东侧列_3623_2.png")
    _touch(downloads / "kling_20260619_IMAGE_bg4_朝西_西窗参_3604_2.png")
    _touch(downloads / "kling_20260619_IMAGE_bg5_高位俯瞰参考_3609_4.png")
    _touch(downloads / "kling_20260619_IMAGE_bg6_座前_虚化背_3619_1.png")

    result = _make_importer(root, downloads).import_drama("ai_videos/wushen")

    assert result.unmatched == [], result.unmatched
    assert result.errors == []
    assert {e["kind"] for e in result.moved} == {"scene_plate"}, result.moved
    for p in ["bg1_朝北_高座主位", "bg2_朝南_厅门", "bg3_朝东_东侧列柱",
              "bg4_朝西_西窗", "bg5_高位俯瞰", "bg6_座前_虚化背景"]:
        assert (scene / p / f"{p}.png").is_file(), p


def test_global_plate_image_with_scene_handle_lands_at_scene_root(tmp_path: Path) -> None:
    """The 步骤一 全局立绘 prompt's first line is the pinyin scene handle. Even
    truncated to `zhenbei_wangf…` the `zhenbei` scene token survives → routes to
    scene root (no 方位 token → not deeper into a plate)."""
    root = tmp_path / "repo"
    scene = root / "ai_videos" / "wushen" / "2_世界观人设" / "scenes" / "zhenbei_wangfu_zhengting"
    (scene / "bg1_朝北_高座主位").mkdir(parents=True)
    downloads = tmp_path / "Downloads"
    _touch(downloads / "kling_20260619_IMAGE_zhenbei_wangf_3511_1.png")

    result = _make_importer(root, downloads).import_drama("ai_videos/wushen")

    assert result.unmatched == [], result.unmatched
    assert [e["kind"] for e in result.moved] == ["scene"], result.moved
    # lands directly in scene root (not a bg plate sub-folder, not not_matched);
    # the trailing rename pass may canonicalise the basename.
    root_pngs = [p for p in scene.iterdir() if p.is_file() and p.suffix == ".png"]
    assert len(root_pngs) == 1, root_pngs


def test_orientation_fallback_ambiguous_across_scenes_is_not_matched(tmp_path: Path) -> None:
    """When two scenes both own a `朝北` plate and the filename carries no scene
    token, the 方位 is ambiguous → not_matched (never a silent misroute)."""
    root = tmp_path / "repo"
    base = root / "ai_videos" / "wushen" / "2_世界观人设" / "scenes"
    (base / "hall_a" / "bg1_朝北_x").mkdir(parents=True)
    (base / "hall_b" / "bg1_朝北_y").mkdir(parents=True)
    downloads = tmp_path / "Downloads"
    _touch(downloads / "kling_20260619_IMAGE_bg1_朝北_zzz_1_1.png")

    result = _make_importer(root, downloads).import_drama("ai_videos/wushen")

    assert {e["kind"] for e in result.moved} == set() or all(
        e["kind"] != "scene_plate" for e in result.moved
    )
    assert len(result.unmatched) == 1, result.unmatched


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


def test_rename_pass_preserves_episode_final_cuts(tmp_path: Path) -> None:
    """Regression (follow-up 128): the trailing rename pass must NOT touch
    episode-root final cuts. The subtitle-burn / concat feature writes
    `ep{NN}_{lang}.mp4` directly into `episodes/ep{NN}/`; the folder-name rename
    would collapse two such files (folder `ep01`) to `ep011.mp4` / `ep012.mp4`,
    destroying their language-tagged names. Importing must leave them intact."""
    root = tmp_path / "repo"
    ep_dir = root / "ai_videos" / "td" / "episodes" / "ep01"
    _touch(ep_dir / "ep01_zh.mp4")
    _touch(ep_dir / "ep01_en.mp4")
    _touch(ep_dir / "script.md")
    downloads = tmp_path / "Downloads"
    downloads.mkdir(parents=True)

    result = _make_importer(root, downloads).import_drama("ai_videos/td")

    assert result.errors == []
    # Final cuts keep their deliberate names — NOT renamed to ep01{1,2}.mp4.
    assert (ep_dir / "ep01_zh.mp4").is_file()
    assert (ep_dir / "ep01_en.mp4").is_file()
    assert not (ep_dir / "ep011.mp4").exists()
    assert not (ep_dir / "ep012.mp4").exists()
    renamed_to = {r["to"] for r in result.rename["renamed"]}
    assert not any("episodes/" in t for t in renamed_to), renamed_to


def test_unrelated_file_lands_in_not_matched(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    (root / "ai_videos" / "td" / "episodes" / "ep01" / "shots" / "shot01").mkdir(parents=True)
    downloads = tmp_path / "Downloads"
    _touch(downloads / "totally_unrelated.png")

    result = _make_importer(root, downloads).import_drama("ai_videos/td")

    assert result.moved == []
    assert [e["kind"] for e in result.unmatched] == ["unmatched"]
    assert (root / "ai_videos" / "td" / "not_matched" / "totally_unrelated.png").is_file()
