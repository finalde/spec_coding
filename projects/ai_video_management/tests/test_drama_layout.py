"""drama_layout resolves assets for both on-disk layouts (legacy flat root +
staged pipeline `2_世界观人设/` & `4_剧本/`). Regression guard for the bug where
assign-actor / import / sub-type broke after a drama was migrated to the
staged structure.
"""
from __future__ import annotations

from pathlib import Path

from libs.common import drama_layout as dl


def _mk(base: Path, *rel: str) -> None:
    for r in rel:
        p = base / r
        if r.endswith(".md"):
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("x", encoding="utf-8")
        else:
            p.mkdir(parents=True, exist_ok=True)


def test_flat_layout(tmp_path: Path) -> None:
    d = tmp_path / "legacy"
    _mk(d, "casting.md", "characters", "scenes", "episodes")
    assert dl.casting_md(d) == d / "casting.md"
    assert dl.characters_dir(d) == d / "characters"
    assert dl.scenes_dir(d) == d / "scenes"
    assert dl.episodes_dir(d) == d / "episodes"


def test_staged_layout(tmp_path: Path) -> None:
    d = tmp_path / "staged"
    _mk(
        d,
        "2_世界观人设/casting.md",
        "2_世界观人设/characters",
        "2_世界观人设/scenes",
        "4_剧本/episodes",
    )
    assert dl.casting_md(d) == d / "2_世界观人设" / "casting.md"
    assert dl.characters_dir(d) == d / "2_世界观人设" / "characters"
    assert dl.scenes_dir(d) == d / "2_世界观人设" / "scenes"
    assert dl.episodes_dir(d) == d / "4_剧本" / "episodes"


def test_shots_stage_episodes_wins_over_script_stage(tmp_path: Path) -> None:
    # The shot/render episodes live under 5_6_分镜与prompt/episodes/ (with
    # shots/shot{NN}/), while 4_剧本/episodes/ is script-only. Render-side
    # consumers (downloads import, episode compose, bgm scan) must resolve to
    # the 5_6 stage — routing to 4_剧本 was the shot-render misroute bug.
    d = tmp_path / "staged_5_6"
    _mk(d, "4_剧本/episodes", "5_6_分镜与prompt/episodes/ep01/shots/shot01")
    assert dl.episodes_dir(d) == d / "5_6_分镜与prompt" / "episodes"


def test_flat_wins_when_both_present(tmp_path: Path) -> None:
    d = tmp_path / "both"
    _mk(d, "characters", "2_世界观人设/characters")
    assert dl.characters_dir(d) == d / "characters"


def test_missing_falls_back_to_flat_root(tmp_path: Path) -> None:
    d = tmp_path / "empty"
    d.mkdir()
    # nothing on disk → default to flat root so first-time create lands sanely
    assert dl.casting_md(d) == d / "casting.md"
    assert dl.characters_dir(d) == d / "characters"
