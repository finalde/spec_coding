"""Media value objects: path classification + archive-state lifecycle.

Consolidates the former `media_path__valueobject.py` (MediaPath +
classification helpers) and `archive_state__valueobject.py` (ArchiveState
enum + transitions). One file per aggregate per role, per follow-up 059.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from libs.domain.errors.media__error import (
    InvalidMediaPathError,
    NotMediaError,
)

AI_VIDEOS_ROOT_NAME: str = "ai_videos"
DELETED_DIR_NAME: str = "_deleted"
ARCHIVE_DIR_NAME: str = "archive"
ACTORS_DIR_NAME: str = "_actors"

MEDIA_EXTENSIONS_SET: frozenset[str] = frozenset(
    {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp",
     ".mp4", ".mov", ".webm", ".mkv", ".avi", ".m4v"}
)


@dataclass(frozen=True)
class MediaPath:
    rel: str

    def __post_init__(self) -> None:
        if not isinstance(self.rel, str) or self.rel == "":
            raise InvalidMediaPathError("path is empty")
        ext = Path(self.rel).suffix.lower()
        if ext not in MEDIA_EXTENSIONS_SET:
            raise NotMediaError(f"extension {ext!r} is not a media type")

    @property
    def extension(self) -> str:
        return Path(self.rel).suffix.lower()

    @property
    def is_under_ai_videos(self) -> bool:
        return self.rel.split("/", 1)[0] == AI_VIDEOS_ROOT_NAME

    @property
    def is_under_deleted(self) -> bool:
        parts = self.rel.split("/")
        return len(parts) >= 2 and parts[0] == AI_VIDEOS_ROOT_NAME and parts[1] == DELETED_DIR_NAME

    @property
    def is_under_actors(self) -> bool:
        parts = self.rel.split("/")
        return len(parts) >= 2 and parts[0] == AI_VIDEOS_ROOT_NAME and parts[1] == ACTORS_DIR_NAME

    @property
    def actor_id_if_under_actors(self) -> str | None:
        parts = self.rel.split("/")
        if not self.is_under_actors or len(parts) < 3:
            return None
        return parts[2]


class ArchiveState(Enum):
    """Legal transitions for a media file's lifecycle.

    LIVE → ARCHIVED → LIVE   (archive / unarchive — sibling archive/)
    LIVE → SOFT_DELETED      (delete — moves into ai_videos/_deleted/{path})
    SOFT_DELETED → (gone)    (hard_delete — real unlink, only inside _deleted/)
    """

    LIVE = "live"
    ARCHIVED = "archived"
    SOFT_DELETED = "soft_deleted"


def classify_state(media: MediaPath) -> ArchiveState:
    if media.is_under_deleted:
        return ArchiveState.SOFT_DELETED
    parts = media.rel.split("/")
    if len(parts) >= 2 and parts[-2] == ARCHIVE_DIR_NAME:
        return ArchiveState.ARCHIVED
    return ArchiveState.LIVE
