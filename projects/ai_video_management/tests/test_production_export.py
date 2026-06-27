"""Production export (follow-up 148): copy each subtitled episode master into a
per-language production sub-folder (中文/英文/中英), stripping the lang suffix.

Pure file-copy — no ffmpeg; dummy bytes stand in for the mp4s."""
from __future__ import annotations

from pathlib import Path

import pytest

from libs.common.exposed_tree import ExposedTree
from libs.common.safe_resolve import SafeResolver
from libs.domain.errors.subtitle__error import InvalidBatchScopeError
from libs.infrastructure.writers.production__writer import ProductionExporter


def _exporter(root: Path) -> ProductionExporter:
    return ProductionExporter(ExposedTree(root), SafeResolver(root))


def _ep_dir(root: Path, drama: str, ep: str) -> Path:
    # staged layout: ai_videos/{drama}/5_6_分镜与prompt/episodes/ep{NN}
    d = root / "ai_videos" / drama / "5_6_分镜与prompt" / "episodes" / ep
    d.mkdir(parents=True, exist_ok=True)
    return d


def test_export_routes_by_language_and_strips_suffix(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    (root / "ai_videos" / "td").mkdir(parents=True, exist_ok=True)
    (root / "ai_videos" / "td" / "README.md").write_text("# td", encoding="utf-8")
    ep1 = _ep_dir(root, "td", "ep01")
    (ep1 / "ep01.mp4").write_bytes(b"clean")        # unsubtitled — must be skipped
    (ep1 / "ep01_zh.mp4").write_bytes(b"zh1")
    (ep1 / "ep01_en.mp4").write_bytes(b"en1")
    ep2 = _ep_dir(root, "td", "ep02")
    (ep2 / "ep02_zh.mp4").write_bytes(b"zh2")
    (ep2 / "ep02_zhen.mp4").write_bytes(b"zhen2")

    r = _exporter(root).export("ai_videos/td/README.md")

    prod = root / "ai_videos" / "td" / "production"
    assert (prod / "中文" / "ep01.mp4").read_bytes() == b"zh1"
    assert (prod / "中文" / "ep02.mp4").read_bytes() == b"zh2"
    assert (prod / "英文" / "ep01.mp4").read_bytes() == b"en1"
    assert (prod / "中英" / "ep02.mp4").read_bytes() == b"zhen2"
    # the unsubtitled clean master is NOT exported (suffix-less name absent)
    assert not (prod / "英文" / "ep02.mp4").exists()
    assert r.by_lang() == {"中文": 2, "英文": 1, "中英": 1}
    assert len(r.exported) == 4


def test_export_empty_when_no_subtitled_masters(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    (root / "ai_videos" / "td").mkdir(parents=True, exist_ok=True)
    (root / "ai_videos" / "td" / "README.md").write_text("# td", encoding="utf-8")
    ep1 = _ep_dir(root, "td", "ep01")
    (ep1 / "ep01.mp4").write_bytes(b"clean")  # only the unsubtitled master

    r = _exporter(root).export("ai_videos/td/README.md")

    assert r.exported == ()
    assert r.by_lang() == {"中文": 0, "英文": 0, "中英": 0}
    # no lang files → production sub-folders are never created
    assert not (root / "ai_videos" / "td" / "production").exists()


def test_export_rejects_underscore_drama_and_empty_path(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    (root / "ai_videos").mkdir(parents=True, exist_ok=True)
    ex = _exporter(root)
    with pytest.raises(InvalidBatchScopeError):
        ex.export("")
    with pytest.raises(InvalidBatchScopeError):
        ex.export("ai_videos/_actors/actor_0001/actor_0001.md")
