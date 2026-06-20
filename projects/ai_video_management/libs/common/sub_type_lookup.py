"""Sub_type detection for ai_video projects.

Heuristic (does not look outside `ai_videos/{name}/`):

- If `ai_videos/{name}/episodes/` exists with at least one `epNN/` child → `novel`.
- Else if `ai_videos/{name}/script.md` or `ai_videos/{name}/shotlist.md` exists → `short`.
- Else → `None` (project shape not yet recognisable).

Trade-off: a novel project mid-creation without any episode folders yet would
mis-detect as short. Acceptable; user can fix downstream by adding the first
`epNN/` placeholder.
"""
from __future__ import annotations

from dataclasses import dataclass
from libs.common import drama_layout
from pathlib import Path
from typing import Literal

import re

SubType = Literal["novel", "short"]

_EPISODE_DIR_RE = re.compile(r"^ep\d+$")


@dataclass(frozen=True)
class ProjectMeta:
    sub_type: SubType | None
    shot_count: int | None
    episode_count: int | None


def lookup(repo_root: Path, project_name: str) -> ProjectMeta:
    project_dir = repo_root / "ai_videos" / project_name
    if not project_dir.is_dir():
        return ProjectMeta(sub_type=None, shot_count=None, episode_count=None)
    episode_count = _count_episodes(project_dir)
    sub_type: SubType | None
    if episode_count is not None and episode_count > 0:
        sub_type = "novel"
    elif _looks_like_short(project_dir):
        sub_type = "short"
    else:
        sub_type = None
    shot_count = _count_shots(project_dir)
    return ProjectMeta(sub_type=sub_type, shot_count=shot_count, episode_count=episode_count)


def _count_episodes(project_dir: Path) -> int | None:
    episodes_dir = drama_layout.episodes_dir(project_dir)
    if not episodes_dir.is_dir():
        return None
    count = sum(1 for p in episodes_dir.iterdir() if p.is_dir() and _EPISODE_DIR_RE.match(p.name))
    return count


def _looks_like_short(project_dir: Path) -> bool:
    """Short layout: README + script.md + shotlist.md at project root, no episodes/."""
    has_shotlist = (project_dir / "shotlist.md").is_file()
    has_script = (project_dir / "script.md").is_file()
    return has_shotlist or has_script


def _count_shots(project_dir: Path) -> int | None:
    shotlist = project_dir / "shotlist.md"
    if not shotlist.is_file():
        return None
    try:
        text = shotlist.read_text(encoding="utf-8")
    except OSError:
        return None
    pattern = re.compile(r"^\|\s*`?(shot\d+)`?\s*\|", re.MULTILINE)
    shots = set(pattern.findall(text))
    return len(shots) if shots else None
