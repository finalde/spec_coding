"""Lock each shot's selected take: copy the newest `renders/` mp4 to a stable
`shot{NN}.mp4` in the shot-folder root (follow-up 147, step 1 of 3).

`renders/` keeps every raw take untouched; `shot{NN}.mp4` is the chosen one the
episode concat then stitches (`EpisodeConcatBuilder._select_clip` prefers it).
Re-running re-copies the current newest (overwrites). Shots with no render are
skipped (reported), not fatal — unless NO shot has one.

Selection reuses the shared `newest_render` (the SAME "newest take wins" rule
episode concat + batch subtitle use), so the locked take never drifts from what
those would have picked. A plain `shutil.copy2` (not symlink) per the decision —
robust + cross-platform, renders/ left intact.
"""
from __future__ import annotations

import re
import shutil
from dataclasses import dataclass
from pathlib import Path

from libs.common.exposed_tree import ExposedTree
from libs.common.render_select import newest_render
from libs.common.safe_resolve import SafeResolver
from libs.domain.errors.episode__error import (
    EpisodeNotFoundError,
    InvalidEpisodePathError,
    NoShotsError,
    NoShotVideosError,
    NotEpisodePathError,
)

_EP_DIR_RE = re.compile(r"^ep\d+$", re.IGNORECASE)
_SHOT_DIR_RE = re.compile(r"^shot\d+$", re.IGNORECASE)
_MP4_EXT = ".mp4"


@dataclass(frozen=True)
class TakeSelection:
    shot: str
    src_rel: str   # the newest renders/ take that was copied
    out_rel: str   # the locked shot{NN}.mp4


@dataclass(frozen=True)
class TakeSkip:
    shot: str
    reason: str


@dataclass(frozen=True)
class SelectTakesResult:
    episode_rel: str
    selected: tuple[TakeSelection, ...]
    skipped: tuple[TakeSkip, ...]

    def to_payload(self) -> dict[str, object]:
        return {
            "episode": self.episode_rel,
            "selected": [
                {"shot": s.shot, "src": s.src_rel, "out": s.out_rel}
                for s in self.selected
            ],
            "skipped": [{"shot": s.shot, "reason": s.reason} for s in self.skipped],
        }


class EpisodeTakesSelector:
    def __init__(self, exposed: ExposedTree, resolver: SafeResolver) -> None:
        self._exposed = exposed
        self._resolver = resolver

    def select(self, rel: str) -> SelectTakesResult:
        episode_dir = self._validate_episode(rel)
        shots_dir = episode_dir / "shots"
        if not shots_dir.is_dir():
            raise NoShotsError("episode has no shots/ folder")
        shot_dirs = self._shot_dirs(shots_dir)
        if not shot_dirs:
            raise NoShotsError("shots/ folder contains no shot{NN} subfolders")
        selected: list[TakeSelection] = []
        skipped: list[TakeSkip] = []
        for shot_dir in shot_dirs:
            take = newest_render(shot_dir)
            if take is None:
                skipped.append(TakeSkip(shot_dir.name, "no_render_mp4"))
                continue
            dst = shot_dir / f"{shot_dir.name}{_MP4_EXT}"
            shutil.copy2(take, dst)
            selected.append(
                TakeSelection(shot_dir.name, self._rel(take), self._rel(dst))
            )
        if not selected:
            raise NoShotVideosError("no shot has a renders/ mp4 to select")
        return SelectTakesResult(self._rel(episode_dir), tuple(selected), tuple(skipped))

    def _validate_episode(self, rel: str) -> Path:
        if not isinstance(rel, str) or rel == "":
            raise InvalidEpisodePathError("path is empty")
        if not self._exposed.is_inside(rel):
            raise InvalidEpisodePathError("path outside sandbox")
        parts = rel.split("/")
        if len(parts) < 4 or parts[0] != "ai_videos" or parts[1].startswith("_"):
            raise NotEpisodePathError("path is not under ai_videos/{drama}/")
        try:
            ep_idx = next(
                i for i in range(1, len(parts) - 1)
                if parts[i] == "episodes" and _EP_DIR_RE.match(parts[i + 1])
            )
        except StopIteration as exc:
            raise NotEpisodePathError("path is not under episodes/ep{NN}/") from exc
        resolved = self._resolver.resolve("/".join(parts[: ep_idx + 2]))
        if resolved is None:
            raise InvalidEpisodePathError("episode path failed sandbox resolution")
        if resolved.is_symlink():
            raise InvalidEpisodePathError("symlink is not allowed")
        if not resolved.is_dir():
            raise EpisodeNotFoundError("episode folder does not exist")
        return resolved

    @staticmethod
    def _shot_dirs(shots_dir: Path) -> list[Path]:
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
