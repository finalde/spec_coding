r"""BgmReferenceReader — reverse-lookup over every drama's `bgm.md` cue
timelines. Answers "which dramas reference this track?" for the BGM library
UI and the assignment-guarded delete.

BGM cues live in per-episode `episodes/epNN/bgm.md` (novel) or a project-root
`bgm.md` (short). Each cue line carries a `bgm_NNNN` token:

    起-止(秒) bgm_NNNN | vol= | duck=on/off | fade=in/out

This reader only needs the token, so it greps `bgm_\d{4,}` per line —
matching the cue grammar without parsing the full line. Mirrors the shape of
`Casting.find_assignments_for_actor` / `assigned_actor_ids` (iterate dramas,
skip `_`-prefixed dirs, parse) but over bgm.md instead of casting.md.
"""
from __future__ import annotations

import re
from pathlib import Path

from libs.common.exposed_tree import ExposedTree
from libs.common.safe_resolve import SafeResolver
from libs.domain.value_objects.bgm__valueobject import validate_bgm_id

BGM_CUE_FILE_NAME: str = "bgm.md"
_BGM_TOKEN_RE = re.compile(r"\bbgm_\d{4,}\b")


class BgmReferenceReader:
    """Implements `BgmReferenceRepository`."""

    def __init__(self, exposed: ExposedTree, resolver: SafeResolver) -> None:
        self._exposed = exposed
        self._resolver = resolver

    def _rel(self, p: Path) -> str:
        try:
            return p.resolve().relative_to(self._resolver.root).as_posix()
        except (OSError, ValueError):
            return p.as_posix()

    def _iter_cue_files(self) -> list[tuple[str, str, Path]]:
        """Every `bgm.md` under a live drama, as (drama, location, path).

        location = "(root)" for a short's project-root bgm.md, or the
        episode folder name (e.g. "episodes/ep01") for a novel.
        """
        ai_videos = self._exposed.root / "ai_videos"
        if not ai_videos.is_dir():
            return []
        out: list[tuple[str, str, Path]] = []
        for drama_dir in sorted(ai_videos.iterdir(), key=lambda p: p.name):
            if not drama_dir.is_dir() or drama_dir.is_symlink():
                continue
            if drama_dir.name.startswith("_"):
                continue
            root_cue = drama_dir / BGM_CUE_FILE_NAME
            if root_cue.is_file():
                out.append((drama_dir.name, "(root)", root_cue))
            episodes = drama_dir / "episodes"
            if episodes.is_dir():
                for ep_dir in sorted(episodes.iterdir(), key=lambda p: p.name):
                    if not ep_dir.is_dir() or ep_dir.is_symlink():
                        continue
                    ep_cue = ep_dir / BGM_CUE_FILE_NAME
                    if ep_cue.is_file():
                        out.append((drama_dir.name, f"episodes/{ep_dir.name}", ep_cue))
        return out

    def find_references_for_bgm(self, bgm_id: str) -> list[dict[str, object]]:
        validate_bgm_id(bgm_id)
        out: list[dict[str, object]] = []
        for drama, location, path in self._iter_cue_files():
            try:
                text = path.read_text(encoding="utf-8")
            except OSError:
                continue
            cue_lines = [
                line.strip()
                for line in text.splitlines()
                if bgm_id in _BGM_TOKEN_RE.findall(line)
            ]
            if cue_lines:
                out.append(
                    {
                        "drama": drama,
                        "location": location,
                        "cue_file": self._rel(path),
                        "cue_lines": cue_lines,
                    }
                )
        out.sort(key=lambda r: (str(r["drama"]), str(r["location"])))
        return out

    def referenced_bgm_ids(self) -> set[str]:
        ids: set[str] = set()
        for _drama, _location, path in self._iter_cue_files():
            try:
                text = path.read_text(encoding="utf-8")
            except OSError:
                continue
            for token in _BGM_TOKEN_RE.findall(text):
                ids.add(token)
        return ids
