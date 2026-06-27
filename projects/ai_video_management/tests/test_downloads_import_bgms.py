"""DownloadsImporter routes BGM-library downloads into
`_bgm/{category}/bgm_NNNN/` by the `bgm_NNNN` key (the prompt's first line,
carried into the downloaded filename by ElevenLabs), renaming each to the
track's canonical `bgm_NNNN.{ext}`. Guards the one-click GLOBAL import flow.
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


def _touch(path: Path, data: bytes = b"x") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def _bgm_root(root: Path) -> Path:
    base = root / "ai_videos" / "_bgm"
    _touch(base / "suspense" / "bgm_0001" / "bgm_0001.md")
    _touch(base / "combat" / "bgm_0002" / "bgm_0002.md")
    return base


def test_import_bgms_routes_by_key(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    base = _bgm_root(root)
    downloads = tmp_path / "Downloads"
    _touch(downloads / "bgm_0001_elevenlabs_ab12.mp3", b"AUDIO1")  # → suspense/bgm_0001
    _touch(downloads / "bgm_0002 (1).wav", b"AUDIO2")              # → combat/bgm_0002

    result = _make_importer(root, downloads).import_bgms("ai_videos/_bgm")

    assert result.errors == [], result.errors
    assert result.unmatched == [], result.unmatched
    assert (base / "suspense" / "bgm_0001" / "bgm_0001.mp3").read_bytes() == b"AUDIO1"
    assert (base / "combat" / "bgm_0002" / "bgm_0002.wav").read_bytes() == b"AUDIO2"
    assert {e["kind"] for e in result.moved} == {"bgm_audio"}


def test_import_bgms_unmatched_and_non_audio(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    base = _bgm_root(root)
    downloads = tmp_path / "Downloads"
    _touch(downloads / "bgm_9999_ghost.mp3")   # tag for a track that doesn't exist
    _touch(downloads / "no_tag_song.mp3")       # audio, no key
    _touch(downloads / "bgm_0001_clip.mp4")     # right key but a VIDEO → ignored

    result = _make_importer(root, downloads).import_bgms("ai_videos/_bgm")

    assert result.moved == []
    assert {e["kind"] for e in result.unmatched} == {"unmatched"}
    # Unmatched audio is NOT imported — left in Downloads, no _not_matched/ folder.
    assert not (base / "_not_matched").exists()
    assert (downloads / "bgm_9999_ghost.mp3").is_file()
    assert (downloads / "no_tag_song.mp3").is_file()
    # video was skipped entirely (not moved, not unmatched)
    assert (downloads / "bgm_0001_clip.mp4").is_file()


def test_import_bgms_overwrites_prior_audio(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    base = _bgm_root(root)
    prior = base / "suspense" / "bgm_0001" / "bgm_0001.mp3"
    _touch(prior, b"old")
    downloads = tmp_path / "Downloads"
    _touch(downloads / "bgm_0001_new.mp3", b"new-audio")

    result = _make_importer(root, downloads).import_bgms("ai_videos/_bgm")

    assert result.errors == []
    assert prior.read_bytes() == b"new-audio"
    assert len(result.moved) == 1
