"""Batch subtitle operations across an episode / a whole drama.

- `scaffold_episode(rel)` — (re)generate `subtitles.md` for every shot under one
  episode (`…/episodes/ep{NN}/shots/shot*/`). Each is overwritten from its
  `shot{NN}.md`; dialogue-free shots are skipped (reported), not seeded with a
  placeholder.
- `burn_drama(rel, lang)` — burn the `{zh|en|zhen}` subtitle master for every
  shot across ALL episodes of a drama. Each shot's NEWEST `renders/` mp4 is
  burned with its sibling `subtitles.md`. Shots lacking a render or a non-empty
  `subtitles.md` are skipped (reported), not failed.

This writer owns only the episode/drama tree-walk; the per-shot work delegates
to `SubtitleBurner`, and newest-render selection to the shared
`libs.common.render_select.newest_render` (the SAME helper episode concat uses,
so "newest take wins" is defined once). The episode/shot/render layout mirrors
`episode__writer.EpisodeConcatBuilder`.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libs.common.exposed_tree import ExposedTree
from libs.common.render_select import newest_render
from libs.common.safe_resolve import SafeResolver
from libs.domain.errors.subtitle__error import (
    EmptySubtitlesError,
    InvalidBatchScopeError,
    InvalidSubtitleLangError,
    NoBatchShotsError,
    SubtitleFileMissingError,
)
from libs.domain.value_objects.subtitle__valueobject import VALID_LANGS
from libs.infrastructure.writers.subtitle__writer import SubtitleBurner

_EP_DIR_RE = re.compile(r"^ep\d+$", re.IGNORECASE)
_SHOT_DIR_RE = re.compile(r"^shot\d+$", re.IGNORECASE)
_EPISODES_DIR_NAME = "episodes"
_SHOTS_DIR_NAME = "shots"


@dataclass(frozen=True)
class BatchShotOutcome:
    episode: str          # ep slug; "" for the single-episode scaffold scope
    shot: str
    ok: bool
    out_rel: str | None   # subtitles.md path (scaffold) or burned mp4 (burn)
    cue_count: int | None
    reason: str | None    # skip / failure reason when not ok

    def to_payload(self) -> dict[str, Any]:
        return {
            "episode": self.episode,
            "shot": self.shot,
            "ok": self.ok,
            "out": self.out_rel,
            "cues": self.cue_count,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class EpisodeScaffoldResult:
    episode_rel: str
    outcomes: tuple[BatchShotOutcome, ...]

    def to_payload(self) -> dict[str, Any]:
        return {
            "episode": self.episode_rel,
            "outcomes": [o.to_payload() for o in self.outcomes],
        }


@dataclass(frozen=True)
class EpisodeBurnResult:
    episode_rel: str
    lang: str
    outcomes: tuple[BatchShotOutcome, ...]

    def to_payload(self) -> dict[str, Any]:
        return {
            "episode": self.episode_rel,
            "lang": self.lang,
            "outcomes": [o.to_payload() for o in self.outcomes],
        }


@dataclass(frozen=True)
class DramaBurnResult:
    drama_rel: str
    lang: str
    outcomes: tuple[BatchShotOutcome, ...]

    def to_payload(self) -> dict[str, Any]:
        return {
            "drama": self.drama_rel,
            "lang": self.lang,
            "outcomes": [o.to_payload() for o in self.outcomes],
        }


class SubtitleBatchBurner:
    def __init__(
        self, exposed: ExposedTree, resolver: SafeResolver, burner: SubtitleBurner
    ) -> None:
        self._exposed = exposed
        self._resolver = resolver
        self._burner = burner

    def scaffold_episode(self, rel: str) -> EpisodeScaffoldResult:
        episode_dir = self._episode_dir(rel)
        shot_dirs = self._shot_dirs(episode_dir / _SHOTS_DIR_NAME)
        if not shot_dirs:
            raise NoBatchShotsError("episode has no shot folders")
        outcomes: list[BatchShotOutcome] = []
        for shot_dir in shot_dirs:
            if not self._burner.spoken_lines(shot_dir):
                outcomes.append(self._skip("", shot_dir.name, "no_dialogue"))
                continue
            try:
                r = self._burner.scaffold_folder(shot_dir)
            except Exception as exc:  # defensive: scaffold is filesystem I/O
                outcomes.append(self._fail("", shot_dir.name, _kind(exc)))
                continue
            outcomes.append(
                BatchShotOutcome("", shot_dir.name, True, r.md_rel, r.cue_count, None)
            )
        return EpisodeScaffoldResult(self._rel(episode_dir), tuple(outcomes))

    def burn_episode(self, rel: str, lang: str = "zh") -> EpisodeBurnResult:
        if lang not in VALID_LANGS:
            raise InvalidSubtitleLangError(lang)
        episode_dir = self._episode_dir(rel)
        shot_dirs = self._shot_dirs(episode_dir / _SHOTS_DIR_NAME)
        if not shot_dirs:
            raise NoBatchShotsError("episode has no shot folders")
        outcomes = [
            self._burn_one(episode_dir.name, shot_dir, lang)
            for shot_dir in shot_dirs
        ]
        return EpisodeBurnResult(self._rel(episode_dir), lang, tuple(outcomes))

    def burn_drama(self, rel: str, lang: str = "zh") -> DramaBurnResult:
        if lang not in VALID_LANGS:
            raise InvalidSubtitleLangError(lang)
        drama_root = self._drama_root(rel)
        episode_dirs = self._episode_dirs(drama_root)
        if not episode_dirs:
            raise NoBatchShotsError("drama has no episodes with shots")
        outcomes: list[BatchShotOutcome] = []
        for episode_dir in episode_dirs:
            for shot_dir in self._shot_dirs(episode_dir / _SHOTS_DIR_NAME):
                outcomes.append(self._burn_one(episode_dir.name, shot_dir, lang))
        if not outcomes:
            raise NoBatchShotsError("drama has no shot folders")
        return DramaBurnResult(self._rel(drama_root), lang, tuple(outcomes))

    def _burn_one(self, ep_slug: str, shot_dir: Path, lang: str) -> BatchShotOutcome:
        render = newest_render(shot_dir)
        if render is None:
            return self._skip(ep_slug, shot_dir.name, "no_render_mp4")
        try:
            r = self._burner.burn(self._rel(render), lang)
        except SubtitleFileMissingError:
            return self._skip(ep_slug, shot_dir.name, "no_subtitles_md")
        except EmptySubtitlesError:
            return self._skip(ep_slug, shot_dir.name, "empty_subtitles")
        except Exception as exc:
            return self._fail(ep_slug, shot_dir.name, _kind(exc))
        return BatchShotOutcome(ep_slug, shot_dir.name, True, r.out_rel, r.cue_count, None)

    @staticmethod
    def _skip(ep: str, shot: str, reason: str) -> BatchShotOutcome:
        return BatchShotOutcome(ep, shot, False, None, None, reason)

    @staticmethod
    def _fail(ep: str, shot: str, reason: str) -> BatchShotOutcome:
        return BatchShotOutcome(ep, shot, False, None, None, reason)

    def _episode_dir(self, rel: str) -> Path:
        if not isinstance(rel, str) or rel == "":
            raise InvalidBatchScopeError("path is empty")
        if not self._exposed.is_inside(rel):
            raise InvalidBatchScopeError("path outside sandbox")
        parts = rel.split("/")
        if len(parts) < 4 or parts[0] != "ai_videos" or parts[1].startswith("_"):
            raise InvalidBatchScopeError("path is not under ai_videos/{drama}/")
        try:
            ep_idx = next(
                i for i in range(1, len(parts) - 1)
                if parts[i] == _EPISODES_DIR_NAME and _EP_DIR_RE.match(parts[i + 1])
            )
        except StopIteration as exc:
            raise InvalidBatchScopeError("path is not under episodes/ep{NN}/") from exc
        return self._resolve_dir("/".join(parts[: ep_idx + 2]))

    def _drama_root(self, rel: str) -> Path:
        if not isinstance(rel, str) or rel == "":
            raise InvalidBatchScopeError("path is empty")
        if not self._exposed.is_inside(rel):
            raise InvalidBatchScopeError("path outside sandbox")
        parts = rel.split("/")
        if len(parts) < 2 or parts[0] != "ai_videos" or parts[1].startswith("_"):
            raise InvalidBatchScopeError("path is not under ai_videos/{drama}/")
        return self._resolve_dir("/".join(parts[:2]))

    def _resolve_dir(self, rel: str) -> Path:
        resolved = self._resolver.resolve(rel)
        if resolved is None:
            raise InvalidBatchScopeError("path failed sandbox resolution")
        if resolved.is_symlink():
            raise InvalidBatchScopeError("symlink is not allowed")
        if not resolved.is_dir():
            raise NoBatchShotsError("scope folder does not exist")
        return resolved

    def _episode_dirs(self, drama_root: Path) -> list[Path]:
        """Every `episodes/ep{NN}` dir under the drama (legacy root layout AND
        staged layout `…/5_6_…/episodes/`), sorted by episode then ancestry."""
        found: list[Path] = []
        try:
            episodes_dirs = [
                d for d in drama_root.rglob(_EPISODES_DIR_NAME)
                if d.is_dir() and not d.is_symlink()
            ]
        except OSError:
            return []
        for episodes_dir in episodes_dirs:
            for ep in self._sorted_children(episodes_dir):
                if _EP_DIR_RE.match(ep.name):
                    found.append(ep)
        return sorted(found, key=lambda p: (p.name.lower(), p.as_posix()))

    def _shot_dirs(self, shots_dir: Path) -> list[Path]:
        if not shots_dir.is_dir():
            return []
        return [
            e for e in self._sorted_children(shots_dir)
            if _SHOT_DIR_RE.match(e.name)
        ]

    @staticmethod
    def _sorted_children(parent: Path) -> list[Path]:
        try:
            entries = sorted(parent.iterdir(), key=lambda p: p.name)
        except OSError:
            return []
        return [e for e in entries if e.is_dir() and not e.is_symlink()]

    def _rel(self, p: Path) -> str:
        try:
            return p.resolve().relative_to(self._resolver.root).as_posix()
        except (OSError, ValueError):
            return p.as_posix()


def _kind(exc: Exception) -> str:
    return type(exc).__name__
