"""Resolve a drama's asset locations across the two on-disk layouts.

Two structures coexist under `ai_videos/{drama}/`:

* **legacy / flat** — `casting.md`, `characters/`, `scenes/`, `episodes/`
  directly at the drama root.
* **staged pipeline** (`全流程编排`) — assets live under numbered stage
  folders: `2_世界观人设/{casting.md, characters/, scenes/}`, script
  episodes under `4_剧本/episodes/`, and the shot/render episodes (the
  `episodes/{ep}/shots/shot{NN}/` tree the downloads-import, bgm-cue scan
  and episode-compose all operate on) under `5_6_分镜与prompt/episodes/`.

Every consumer (casting assign, downloads import, sub-type lookup, bgm-cue
scan, …) must work for both. These helpers take the drama root dir and return
the *actual* location — preferring whichever exists, falling back to the flat
root so first-time `create` still lands somewhere sane.
"""
from __future__ import annotations

from pathlib import Path

WORLD_STAGE: str = "2_世界观人设"
SCRIPT_STAGE: str = "4_剧本"
SHOTS_STAGE: str = "5_6_分镜与prompt"


def _first_existing_dir(*candidates: Path) -> Path:
    for c in candidates:
        if c.is_dir():
            return c
    return candidates[0]


def _first_existing_file(*candidates: Path) -> Path:
    for c in candidates:
        if c.is_file():
            return c
    return candidates[0]


def casting_md(drama_dir: Path) -> Path:
    """`casting.md` — flat root or `2_世界观人设/`. Falls back to flat root."""
    return _first_existing_file(
        drama_dir / "casting.md", drama_dir / WORLD_STAGE / "casting.md"
    )


def characters_dir(drama_dir: Path) -> Path:
    return _first_existing_dir(
        drama_dir / "characters", drama_dir / WORLD_STAGE / "characters"
    )


def scenes_dir(drama_dir: Path) -> Path:
    return _first_existing_dir(
        drama_dir / "scenes", drama_dir / WORLD_STAGE / "scenes"
    )


def episodes_dir(drama_dir: Path) -> Path:
    """The episodes tree the render-side consumers walk (downloads import,
    episode compose, bgm-cue scan). The staged pipeline puts the shot/render
    episodes — `episodes/{ep}/shots/shot{NN}/` — under `5_6_分镜与prompt/`, so
    that stage is preferred over the script-only `4_剧本/episodes/` (which has
    no `shots/` and previously caused shot renders to misroute). Legacy flat
    `episodes/` still wins when present."""
    return _first_existing_dir(
        drama_dir / "episodes",
        drama_dir / SHOTS_STAGE / "episodes",
        drama_dir / SCRIPT_STAGE / "episodes",
    )
