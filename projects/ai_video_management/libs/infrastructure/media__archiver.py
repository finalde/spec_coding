"""Per-file archive / unarchive / delete for media files.

Per follow-up 008: a per-tile button moves a single image / video into an
`archive/` subfolder of its current directory (creating the folder on
demand); the inverse moves it back and rmdirs an empty archive/. Atomic
per-file rename — no temp two-pass needed because we only touch one file.

Per follow-up 023: a per-file delete button moves a media file into
`ai_videos/_deleted/{rest-of-relative-path}`, preserving sub-structure for
mental traceability. Soft delete — no rmdir of the source's parent.

Per follow-up 038: hard-delete real-unlinks a media file that already lives
under `ai_videos/_deleted/**`. The DeletedView grid loops this per selected
tile to empty the recycle bin.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from libs.common.exposed_tree import MEDIA_EXTENSIONS, ExposedTree
from libs.common.safe_resolve import SafeResolver

ARCHIVE_DIR_NAME = "archive"
DELETED_DIR_NAME = "_deleted"
AI_VIDEOS_ROOT_NAME = "ai_videos"


class InvalidPath(Exception):
    pass


class NotFound(Exception):
    pass


class NotMedia(Exception):
    pass


class AlreadyArchived(Exception):
    pass


class NotInArchive(Exception):
    pass


class AlreadyDeleted(Exception):
    pass


class NotInAiVideos(Exception):
    pass


class NotInDeleted(Exception):
    pass


class TargetExists(Exception):
    pass


class MoveFailed(Exception):
    pass


@dataclass(frozen=True)
class MoveResult:
    src_rel: str
    dst_rel: str

    def to_payload(self) -> dict[str, str]:
        return {"from": self.src_rel, "to": self.dst_rel}


class MediaArchiver:
    def __init__(self, exposed: ExposedTree, resolver: SafeResolver) -> None:
        self._exposed = exposed
        self._resolver = resolver

    def archive(self, rel: str) -> MoveResult:
        src = self._validate_media_source(rel)
        if src.parent.name == ARCHIVE_DIR_NAME:
            raise AlreadyArchived("file is already inside an archive/ folder")
        archive_dir = src.parent / ARCHIVE_DIR_NAME
        if archive_dir.exists() and not archive_dir.is_dir():
            raise MoveFailed(f"{ARCHIVE_DIR_NAME} exists but is not a directory")
        try:
            archive_dir.mkdir(exist_ok=True)
        except OSError as exc:
            raise MoveFailed(str(exc)) from exc
        dst = archive_dir / src.name
        if dst.exists():
            raise TargetExists(self._rel(dst))
        try:
            src.rename(dst)
        except OSError as exc:
            raise MoveFailed(str(exc)) from exc
        return MoveResult(src_rel=self._rel(src), dst_rel=self._rel(dst))

    def unarchive(self, rel: str) -> MoveResult:
        src = self._validate_media_source(rel)
        if src.parent.name != ARCHIVE_DIR_NAME:
            raise NotInArchive("file is not inside an archive/ folder")
        target_dir = src.parent.parent
        if not target_dir.is_dir():
            raise MoveFailed("parent of archive/ is missing")
        dst = target_dir / src.name
        if dst.exists():
            raise TargetExists(self._rel(dst))
        try:
            src.rename(dst)
        except OSError as exc:
            raise MoveFailed(str(exc)) from exc
        archive_dir = src.parent
        try:
            if not any(archive_dir.iterdir()):
                archive_dir.rmdir()
        except OSError:
            pass
        return MoveResult(src_rel=self._rel(src), dst_rel=self._rel(dst))

    def delete(self, rel: str) -> MoveResult:
        src = self._validate_media_source(rel)
        relative = src.relative_to(self._resolver.root)
        parts = relative.parts
        if not parts or parts[0] != AI_VIDEOS_ROOT_NAME:
            raise NotInAiVideos("delete only supports ai_videos paths")
        if len(parts) >= 2 and parts[1] == DELETED_DIR_NAME:
            raise AlreadyDeleted("file is already inside _deleted/")
        rest_parts = parts[1:]
        target = self._resolver.root / AI_VIDEOS_ROOT_NAME / DELETED_DIR_NAME / Path(*rest_parts)
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise MoveFailed(str(exc)) from exc
        if target.exists():
            raise TargetExists(self._rel(target))
        try:
            src.rename(target)
        except OSError as exc:
            raise MoveFailed(str(exc)) from exc
        return MoveResult(src_rel=self._rel(src), dst_rel=self._rel(target))

    def hard_delete(self, rel: str) -> str:
        src = self._validate_media_source(rel)
        relative = src.relative_to(self._resolver.root)
        parts = relative.parts
        if len(parts) < 2 or parts[0] != AI_VIDEOS_ROOT_NAME or parts[1] != DELETED_DIR_NAME:
            raise NotInDeleted("hard_delete only operates inside ai_videos/_deleted/")
        rel_str = self._rel(src)
        try:
            src.unlink()
        except OSError as exc:
            raise MoveFailed(str(exc)) from exc
        return rel_str

    def _validate_media_source(self, rel: str) -> Path:
        if not isinstance(rel, str) or rel == "":
            raise InvalidPath("path is empty")
        if not self._exposed.is_inside(rel):
            raise NotFound("path outside sandbox")
        ext = Path(rel).suffix.lower()
        if ext not in MEDIA_EXTENSIONS:
            raise NotMedia("extension is not a media type")
        resolved = self._resolver.resolve(rel)
        if resolved is None or not resolved.is_file():
            raise NotFound("file does not exist")
        if resolved.is_symlink():
            raise NotFound("symlink is not allowed")
        return resolved

    def _rel(self, p: Path) -> str:
        try:
            return p.resolve().relative_to(self._resolver.root).as_posix()
        except (OSError, ValueError):
            return p.as_posix()
