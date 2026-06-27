"""Character read-side: list each character folder's newest turntable mp4.

Read-side (per CLAUDE.md queries may skip the domain layer): walks
`ai_videos/{drama}/.../characters/cN_*` and reports the newest original
turntable mp4 in each — mtime-max, excluding the truncated `video.mp4` reel
and the `views/` outputs, the same rule `CharacterViewExtractor` uses to pick
its extraction source. Powers the gallery tile preview (`GET /api/character-videos`).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from libs.common.exposed_tree import ExposedTree
from libs.common.safe_resolve import SafeResolver
from libs.domain.errors.character_video__error import InvalidCharactersDirError

_CHARACTER_DIR_RE: re.Pattern[str] = re.compile(r"^c\d+(_.*)?$")
_VIDEO_EXTENSIONS: frozenset[str] = frozenset(
    {".mp4", ".mov", ".webm", ".mkv", ".avi", ".m4v"}
)
_TRUNCATE_OUTPUT_NAME: str = "video.mp4"


@dataclass(frozen=True)
class CharacterVideoListing:
    folder: str
    latest_video_rel: str | None

    def to_payload(self) -> dict[str, object]:
        return {"folder": self.folder, "latest_video": self.latest_video_rel}


class CharacterReader:
    def __init__(self, exposed: ExposedTree, resolver: SafeResolver) -> None:
        self._exposed = exposed
        self._resolver = resolver

    def list_latest_videos(
        self, characters_rel: str
    ) -> tuple[CharacterVideoListing, ...]:
        chars_dir = self._validate_characters_dir(characters_rel)
        listings: list[CharacterVideoListing] = []
        for sub in sorted(chars_dir.iterdir(), key=lambda p: p.name):
            if not sub.is_dir() or sub.is_symlink():
                continue
            if not _CHARACTER_DIR_RE.match(sub.name):
                continue
            latest = self._latest_video_in(sub)
            listings.append(
                CharacterVideoListing(
                    folder=sub.name,
                    latest_video_rel=self._rel(latest) if latest is not None else None,
                )
            )
        return tuple(listings)

    def _latest_video_in(self, folder: Path) -> Path | None:
        """Newest original turntable mp4 directly in `folder` by mtime, or None.

        Excludes the truncated `video.mp4` reel; `views/` outputs live in a
        subfolder and are never enumerated here.
        """
        try:
            entries = list(folder.iterdir())
        except OSError:
            return None
        candidates = [
            entry
            for entry in entries
            if entry.is_file()
            and not entry.is_symlink()
            and entry.suffix.lower() in _VIDEO_EXTENSIONS
            and entry.name != _TRUNCATE_OUTPUT_NAME
        ]
        if not candidates:
            return None
        return max(candidates, key=lambda p: p.stat().st_mtime)

    def _validate_characters_dir(self, rel: str) -> Path:
        if not isinstance(rel, str) or rel == "":
            raise InvalidCharactersDirError("path is empty")
        norm = rel.replace("\\", "/")
        if not self._exposed.is_inside(norm):
            raise InvalidCharactersDirError("path outside sandbox")
        parts = norm.split("/")
        if len(parts) < 3 or parts[0] != "ai_videos" or parts[1].startswith("_"):
            raise InvalidCharactersDirError(
                "path must be ai_videos/{drama}/.../characters/"
            )
        if parts[-1] != "characters":
            raise InvalidCharactersDirError("path must end in characters/")
        resolved = self._resolver.resolve(norm)
        if resolved is None:
            raise InvalidCharactersDirError("path failed sandbox resolution")
        if resolved.is_symlink():
            raise InvalidCharactersDirError("symlink is not allowed")
        if not resolved.is_dir():
            raise InvalidCharactersDirError("characters dir does not exist")
        return resolved

    def _rel(self, p: Path) -> str:
        try:
            return p.resolve().relative_to(self._resolver.root).as_posix()
        except (OSError, ValueError):
            return p.as_posix()
