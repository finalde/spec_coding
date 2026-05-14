"""sub_type lookup tests.

Heuristic: episodes/ exists with epNN dirs → novel; else (script.md OR shotlist.md present)
→ short; else None. Looks only inside `ai_videos/{name}/`.
"""
from __future__ import annotations

from pathlib import Path

from libs.common.sub_type_lookup import lookup
from tests.conftest import make_app, repo_root


def test_lookup_wukong_juexing_is_short() -> None:
    """wukong_juexing has shotlist.md and no episodes/ → short."""
    root = repo_root()
    meta = lookup(root, "wukong_juexing")
    assert meta.sub_type == "short", f"expected short, got {meta.sub_type!r}"


def test_lookup_missing_project_returns_none() -> None:
    root = repo_root()
    meta = lookup(root, "nonexistent_project_xyz")
    assert meta.sub_type is None
    assert meta.shot_count is None
    assert meta.episode_count is None


def test_lookup_shot_count_for_wukong_juexing() -> None:
    root = repo_root()
    meta = lookup(root, "wukong_juexing")
    assert meta.shot_count == 5, f"expected 5 shots, got {meta.shot_count}"


def test_lookup_synthetic_novel_with_episodes(tmp_path: Path) -> None:
    """When episodes/epNN/ exists, the project is detected as novel."""
    project = tmp_path / "ai_videos" / "synthetic_novel"
    (project / "episodes" / "ep01").mkdir(parents=True)
    (project / "episodes" / "ep02").mkdir()
    meta = lookup(tmp_path, "synthetic_novel")
    assert meta.sub_type == "novel"
    assert meta.episode_count == 2


def test_lookup_synthetic_short_with_shotlist(tmp_path: Path) -> None:
    """script.md OR shotlist.md present + no episodes/ → short."""
    project = tmp_path / "ai_videos" / "synthetic_short"
    project.mkdir(parents=True)
    (project / "shotlist.md").write_text("| `shot01` |\n", encoding="utf-8")
    meta = lookup(tmp_path, "synthetic_short")
    assert meta.sub_type == "short"
    assert meta.episode_count is None


def test_lookup_empty_project_returns_none(tmp_path: Path) -> None:
    """Empty project dir (no episodes/, no script/shotlist) → sub_type=None."""
    project = tmp_path / "ai_videos" / "empty_project"
    project.mkdir(parents=True)
    meta = lookup(tmp_path, "empty_project")
    assert meta.sub_type is None
