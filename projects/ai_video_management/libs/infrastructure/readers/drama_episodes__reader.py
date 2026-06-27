"""List a drama's episodes for the main-page production console.

Walks `episodes/ep{NN}/` (both the flat root layout and the staged
`…/5_6_分镜与prompt/episodes/` one, via `drama_layout.episodes_dir`) and reports
each episode's shot count, how many shots are already 定版-locked
(`shot{NN}.mp4` present), and whether the stitched master `ep{NN}.mp4` exists —
enough for the dashboard to render a per-episode 拼接成片 row with status.

Read-only: no copies, no mutation.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from libs.common import drama_layout
from libs.common.exposed_tree import ExposedTree
from libs.common.safe_resolve import SafeResolver
from libs.domain.errors.subtitle__error import InvalidBatchScopeError

_EP_DIR_RE = re.compile(r"^ep\d+$", re.IGNORECASE)
_SHOT_DIR_RE = re.compile(r"^shot\d+$", re.IGNORECASE)
_MP4_EXT = ".mp4"


@dataclass(frozen=True)
class EpisodeInfo:
    episode: str         # ep folder name, e.g. "ep04"
    episode_rel: str     # repo-relative ep folder path (concat target)
    shots: int           # shot{NN} subfolders
    locked: int          # shots with a 定版 shot{NN}.mp4
    has_master: bool     # stitched ep{NN}.mp4 exists


@dataclass(frozen=True)
class DramaEpisodesResult:
    drama_rel: str
    episodes: tuple[EpisodeInfo, ...]

    def to_payload(self) -> dict[str, object]:
        return {
            "drama": self.drama_rel,
            "episodes": [
                {
                    "episode": e.episode,
                    "episode_rel": e.episode_rel,
                    "shots": e.shots,
                    "locked": e.locked,
                    "has_master": e.has_master,
                }
                for e in self.episodes
            ],
        }


class DramaEpisodesReader:
    def __init__(self, exposed: ExposedTree, resolver: SafeResolver) -> None:
        self._exposed = exposed
        self._resolver = resolver

    def list(self, rel: str) -> DramaEpisodesResult:
        drama_root = self._drama_root(rel)
        episodes_dir = drama_layout.episodes_dir(drama_root)
        episodes: list[EpisodeInfo] = []
        if episodes_dir.is_dir():
            for ep_dir in self._sorted_ep_dirs(episodes_dir):
                shots = self._shot_dirs(ep_dir / "shots")
                locked = sum(
                    1 for s in shots if (s / f"{s.name}{_MP4_EXT}").is_file()
                )
                master = ep_dir / f"{ep_dir.name.lower()}{_MP4_EXT}"
                episodes.append(
                    EpisodeInfo(
                        ep_dir.name,
                        self._rel(ep_dir),
                        len(shots),
                        locked,
                        master.is_file() and not master.is_symlink(),
                    )
                )
        return DramaEpisodesResult(self._rel(drama_root), tuple(episodes))

    def _drama_root(self, rel: str) -> Path:
        if not isinstance(rel, str) or rel == "":
            raise InvalidBatchScopeError("path is empty")
        if not self._exposed.is_inside(rel):
            raise InvalidBatchScopeError("path outside sandbox")
        parts = rel.split("/")
        if len(parts) < 2 or parts[0] != "ai_videos" or parts[1].startswith("_"):
            raise InvalidBatchScopeError("path is not under ai_videos/{drama}/")
        resolved = self._resolver.resolve("/".join(parts[:2]))
        if resolved is None:
            raise InvalidBatchScopeError("path failed sandbox resolution")
        if resolved.is_symlink():
            raise InvalidBatchScopeError("symlink is not allowed")
        if not resolved.is_dir():
            raise InvalidBatchScopeError("drama folder does not exist")
        return resolved

    @staticmethod
    def _sorted_ep_dirs(episodes_dir: Path) -> list[Path]:
        try:
            entries = sorted(episodes_dir.iterdir(), key=lambda p: p.name)
        except OSError:
            return []
        return [
            e for e in entries
            if e.is_dir() and not e.is_symlink() and _EP_DIR_RE.match(e.name)
        ]

    @staticmethod
    def _shot_dirs(shots_dir: Path) -> list[Path]:
        if not shots_dir.is_dir():
            return []
        try:
            entries = sorted(shots_dir.iterdir(), key=lambda p: p.name)
        except OSError:
            return []
        return [
            e for e in entries
            if e.is_dir() and not e.is_symlink() and _SHOT_DIR_RE.match(e.name)
        ]

    def _rel(self, p: Path) -> str:
        try:
            return p.resolve().relative_to(self._resolver.root).as_posix()
        except (OSError, ValueError):
            return p.as_posix()
