"""follow-up 124: prompt-only actor generation + downloads re-import round-trip.

`create_prompts_batch` allocates the actor folder + writes an id-tagged sidecar
WITHOUT any Kling call (no jpg). `DownloadsImporter.import_actors` then routes a
downloaded face/body image back to that folder by the `id{NNNN}{f|b}` tag the
prompt carried, transcoding it to the canonical `{attrs}.jpg` / `{attrs}__body.jpg`
name so `list_actors` surfaces it exactly like a Kling-generated actor.
"""
from __future__ import annotations

from io import BytesIO
from pathlib import Path

from PIL import Image

from libs.common.exposed_tree import ExposedTree
from libs.common.safe_resolve import SafeResolver
from libs.infrastructure.writers.actor__writer import (
    ActorAttrs,
    ActorPool,
    _attrs_to_filename,
    _find_actor_jpg,
)
from libs.infrastructure.writers.downloads__writer import DownloadsImporter
from libs.infrastructure.writers.media__writer import MediaRenamer


def _pool(root: Path) -> ActorPool:
    exposed = ExposedTree(root)
    resolver = SafeResolver(root)
    return ActorPool(exposed, resolver, provider=object())


def _importer(root: Path, downloads: Path) -> DownloadsImporter:
    exposed = ExposedTree(root)
    resolver = SafeResolver(root)
    renamer = MediaRenamer(exposed, resolver)
    return DownloadsImporter(exposed, resolver, renamer, downloads_dir=downloads)


def _png(path: Path, color: tuple[int, int, int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    buf = BytesIO()
    Image.new("RGB", (8, 8), color).save(buf, format="PNG")
    path.write_bytes(buf.getvalue())


def test_create_prompts_then_import(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    pool = _pool(root)
    attrs = ActorAttrs(ethnicity="asian", gender="female", age_range="26-35", look="beautiful")

    result = pool.create_prompts_batch(attrs, count=1, resolution="normal", seeds=[12345])

    assert result.errors == [], result.errors
    assert len(result.generated) == 1
    entry = result.generated[0]
    actor_id = entry["id"]
    assert entry["pending_import"] is True
    assert entry["image_path"] is None
    # Single combined prompt per actor (user req 2026-06-14); carries the
    # id-routing face tag so the one downloaded image routes back.
    num = int(actor_id.rsplit("_", 1)[1])
    assert entry["prompt"].startswith(f"id{num:04d}f")
    assert "body_prompt" not in entry

    actor_dir = root / "ai_videos" / "_actors" / actor_id
    md_text = (actor_dir / f"{actor_id}.md").read_text(encoding="utf-8")
    # exactly one prompt block, not the legacy face shot + body shot pair
    assert md_text.count("## 生成 prompt") == 1
    assert "face shot" not in md_text and "body shot" not in md_text
    assert _find_actor_jpg(actor_dir) is None  # no jpg yet — pending import
    # prompt-only actors are hidden from the pool until their image lands
    assert pool.list_actors() == []

    # user renders ONE external image; download carries the face tag
    downloads = tmp_path / "Downloads"
    _png(downloads / f"id{num:04d}f_portrait_a1b2.png", (200, 10, 10))

    imp = _importer(root, downloads).import_actors("ai_videos/_actors")

    assert imp.errors == [], imp.errors
    assert imp.unmatched == [], imp.unmatched
    assert {e["kind"] for e in imp.moved} == {"actor_face"}
    # canonical name → list_actors / _find_actor_jpg pick it up
    assert (actor_dir / _attrs_to_filename(attrs)).is_file()
    assert _find_actor_jpg(actor_dir) is not None
    listed = pool.list_actors()
    assert [a.id for a in listed] == [actor_id]
    # source file consumed from Downloads
    assert not (downloads / f"id{num:04d}f_portrait_a1b2.png").exists()


def test_import_unmatched_goes_to_not_matched(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    _pool(root).create_prompts_batch(
        ActorAttrs(ethnicity="asian", gender="male", age_range="26-35", look="cunning"),
        count=1,
        seeds=[7],
    )
    downloads = tmp_path / "Downloads"
    _png(downloads / "no_tag_image.png", (5, 5, 5))           # no id tag
    _png(downloads / "id9999f_ghost.png", (5, 5, 5))          # tag for a missing actor

    imp = _importer(root, downloads).import_actors("ai_videos/_actors")

    assert imp.moved == []
    assert {e["kind"] for e in imp.unmatched} == {"unmatched"}
    # Unmatched downloads are NOT imported — left in Downloads, no _not_matched/.
    assert not (root / "ai_videos" / "_actors" / "_not_matched").exists()
    assert (downloads / "no_tag_image.png").is_file()
    assert (downloads / "id9999f_ghost.png").is_file()
