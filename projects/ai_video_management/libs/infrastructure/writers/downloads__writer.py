"""Scan the user OS Downloads folder and import recent media into a drama tree.

Per follow-up 009: enriches the drama-row rename button into a one-click
"import + rename" flow. Filename substring-matches against the drama's
`characters/`, `scenes/`, and `episodes/*/prompts/shot*/` folders to choose
a destination; unmatched files land in `<drama>/not_matched/` for manual
triage. Only Downloads' immediate children are scanned, restricted to media
extensions with mtime within the last 7 days; symlinks are skipped.

This module is the first place the backend reads from a path OUTSIDE
EXPOSED_TREE. Source-side hardening: basename validation, symlink refusal,
and shutil.move (never copy + delete in two steps that could leave orphans).
Destination is always inside the drama folder validated by MediaRenamer.
"""
from __future__ import annotations

import os
import re
import shutil
import time
from dataclasses import dataclass, field
from pathlib import Path

from libs.common.exposed_tree import MEDIA_EXTENSIONS, ExposedTree
from libs.common.safe_resolve import SafeResolver
from libs.domain.errors.casting__error import DramaNotFoundError, InvalidDramaPathError
from libs.domain.errors.downloads__error import DownloadsDirMissingError
from libs.infrastructure.writers.media__writer import MediaRenamer, RenameResult

NOT_MATCHED_DIR_NAME = "not_matched"
DEFAULT_TIME_WINDOW_SECONDS = 7 * 24 * 60 * 60
DOWNLOADS_ENV_VAR = "AI_VIDEO_MGMT_DOWNLOADS_DIR"
_BASENAME_INVALID = re.compile(r"[\x00-\x1f/\\:*?\"<>|]")


@dataclass(frozen=True)
class _Candidate:
    folder: Path
    kind: str  # "character" | "scene" | "shot"
    tokens: tuple[str, ...]  # already lowercased


@dataclass
class ImportResult:
    moved: list[dict[str, str]] = field(default_factory=list)
    unmatched: list[dict[str, str]] = field(default_factory=list)
    errors: list[dict[str, str]] = field(default_factory=list)
    rename: dict[str, object] | None = None

    def to_payload(self) -> dict[str, object]:
        return {
            "moved": list(self.moved),
            "unmatched": list(self.unmatched),
            "errors": list(self.errors),
            "rename": self.rename if self.rename is not None else {"renamed": [], "skipped": [], "errors": []},
        }


class DownloadsImporter:
    def __init__(
        self,
        exposed: ExposedTree,
        resolver: SafeResolver,
        renamer: MediaRenamer,
        downloads_dir: Path | None = None,
        time_window_seconds: int = DEFAULT_TIME_WINDOW_SECONDS,
    ) -> None:
        self._exposed = exposed
        self._resolver = resolver
        self._renamer = renamer
        self._downloads_dir = (downloads_dir or self._resolve_default_downloads_dir()).resolve()
        self._window = time_window_seconds

    @staticmethod
    def _resolve_default_downloads_dir() -> Path:
        override = os.environ.get(DOWNLOADS_ENV_VAR, "").strip()
        if override:
            return Path(override)
        return Path.home() / "Downloads"

    def import_drama(self, rel_drama_path: str) -> ImportResult:
        drama_dir = self._renamer.validate_drama(rel_drama_path)
        if not self._downloads_dir.is_dir():
            raise DownloadsDirMissingError(str(self._downloads_dir))
        candidates = self._collect_candidates(drama_dir)
        cutoff = time.time() - self._window
        result = ImportResult()
        not_matched_dir = drama_dir / NOT_MATCHED_DIR_NAME
        for src in self._iter_downloads(cutoff):
            if not self._is_safe_basename(src.name):
                result.errors.append({"path": self._display_src(src), "message": "invalid_basename"})
                continue
            chosen = self._classify(src.name, candidates)
            if chosen is None:
                dst_folder = not_matched_dir
                kind = "unmatched"
            else:
                dst_folder, kind = chosen.folder, chosen.kind
            try:
                dst_folder.mkdir(parents=True, exist_ok=True)
            except OSError as exc:
                result.errors.append({"path": self._display_src(src), "message": f"mkdir_failed: {exc}"})
                continue
            dst = dst_folder / src.name
            if dst.exists():
                result.errors.append({"path": self._display_src(src), "message": f"target_exists: {self._rel(dst)}"})
                continue
            try:
                shutil.move(str(src), str(dst))
            except OSError as exc:
                result.errors.append({"path": self._display_src(src), "message": f"move_failed: {exc}"})
                continue
            entry = {"from": self._display_src(src), "to": self._rel(dst), "kind": kind}
            if chosen is None:
                result.unmatched.append(entry)
            else:
                result.moved.append(entry)
        rename_result = self._renamer.rename_drama(
            rel_drama_path,
            excluded_folder_names=frozenset({NOT_MATCHED_DIR_NAME, "frames"}),
        )
        result.rename = rename_result.to_payload()
        return result

    def _collect_candidates(self, drama_dir: Path) -> list[_Candidate]:
        out: list[_Candidate] = []
        characters_dir = drama_dir / "characters"
        if characters_dir.is_dir():
            for child in sorted(characters_dir.iterdir()):
                if child.is_dir() and not child.is_symlink():
                    out.append(_Candidate(folder=child, kind="character", tokens=self._tokens(child.name)))
        scenes_dir = drama_dir / "scenes"
        if scenes_dir.is_dir():
            for child in sorted(scenes_dir.iterdir()):
                if child.is_dir() and not child.is_symlink():
                    out.append(_Candidate(folder=child, kind="scene", tokens=self._tokens(child.name)))
        episodes_dir = drama_dir / "episodes"
        if episodes_dir.is_dir():
            for ep in sorted(episodes_dir.iterdir()):
                if not ep.is_dir() or ep.is_symlink():
                    continue
                prompts_dir = ep / "prompts"
                if not prompts_dir.is_dir():
                    continue
                for shot in sorted(prompts_dir.iterdir()):
                    if not shot.is_dir() or shot.is_symlink():
                        continue
                    tokens = self._tokens(shot.name)
                    ep_name = ep.name
                    extra: list[str] = []
                    if ep_name:
                        extra.append(f"{ep_name}_{shot.name}".lower())
                        extra.append(ep_name.lower())
                    tokens = tuple(dict.fromkeys((*tokens, *extra)))
                    out.append(_Candidate(folder=shot, kind="shot", tokens=tokens))
        return out

    @staticmethod
    def _tokens(folder_name: str) -> tuple[str, ...]:
        tokens: list[str] = [folder_name.lower()]
        if "_" in folder_name:
            for part in folder_name.split("_"):
                part = part.strip().lower()
                if len(part) >= 2:
                    tokens.append(part)
        seen: dict[str, None] = {}
        for t in tokens:
            if t and t not in seen:
                seen[t] = None
        return tuple(seen)

    @staticmethod
    def _classify(filename: str, candidates: list[_Candidate]) -> _Candidate | None:
        name = filename.lower()
        kind_priority = {"shot": 3, "scene": 2, "character": 1}
        best: tuple[int, int, str, _Candidate] | None = None  # (score, kind_rank, folder_name_lex, candidate)
        for cand in candidates:
            score = 0
            for token in cand.tokens:
                if token and token in name:
                    if len(token) > score:
                        score = len(token)
            if score == 0:
                continue
            key = (score, kind_priority[cand.kind], -ord_seq(cand.folder.name))
            if best is None or key > best[:3]:
                best = (*key, cand)
        return best[3] if best is not None else None

    def _iter_downloads(self, cutoff: float) -> list[Path]:
        out: list[Path] = []
        try:
            entries = sorted(self._downloads_dir.iterdir(), key=lambda p: p.name)
        except OSError:
            return out
        for child in entries:
            try:
                if child.is_symlink():
                    continue
                if not child.is_file():
                    continue
            except OSError:
                continue
            if child.suffix.lower() not in MEDIA_EXTENSIONS:
                continue
            try:
                stat = child.stat()
            except OSError:
                continue
            if stat.st_mtime < cutoff:
                continue
            out.append(child)
        return out

    @staticmethod
    def _is_safe_basename(name: str) -> bool:
        if not name or name in (".", ".."):
            return False
        if _BASENAME_INVALID.search(name):
            return False
        if len(name) > 255:
            return False
        return True

    def _rel(self, p: Path) -> str:
        try:
            return p.resolve().relative_to(self._resolver.root).as_posix()
        except (OSError, ValueError):
            return p.as_posix()

    def _display_src(self, p: Path) -> str:
        try:
            home = Path.home().resolve()
            rel = p.resolve().relative_to(home)
            return f"~/{rel.as_posix()}"
        except (OSError, ValueError):
            return p.name


def ord_seq(s: str) -> int:
    # Stable lex-tiebreaker hashed to a single int (higher = lexicographically smaller wins via negation).
    total = 0
    for ch in s[:32]:
        total = (total << 8) | (ord(ch) & 0xff)
    return total


__all__ = [
    "DEFAULT_TIME_WINDOW_SECONDS",
    "DOWNLOADS_ENV_VAR",
    "DownloadsImporter",
    "ImportResult",
    "NOT_MATCHED_DIR_NAME",
    "RenameResult",
]
