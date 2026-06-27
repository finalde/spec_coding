"""Media-aggregate filesystem writer: archive / unarchive / delete /
hard_delete + drama-scoped batch rename.

Consolidates the former `media__archiver.py` (move operations into archive/,
_deleted/, and real unlink inside _deleted/) and `media__renamer.py`
(drama-scoped recursive rename of media files to match their parent folder
name). One file per aggregate per role, per follow-up 059.
"""
from __future__ import annotations

import shutil
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path

from libs.common.exposed_tree import MEDIA_EXTENSIONS, ExposedTree
from libs.common.safe_resolve import SafeResolver
from libs.domain.errors.casting__error import DramaNotFoundError, InvalidDramaPathError
from libs.domain.errors.media__error import (
    AlreadyArchivedError,
    AlreadyDeletedError,
    InvalidMediaPathError,
    MediaMoveFailedError,
    MediaNotFoundError,
    MediaTargetExistsError,
    NotInArchiveError,
    NotMediaError,
    NotUnderAiVideosError,
    NotUnderDeletedError,
)

ARCHIVE_DIR_NAME = "archive"
DELETED_DIR_NAME = "_deleted"
AI_VIDEOS_ROOT_NAME = "ai_videos"
# The episode subtree is never a rename target. Shot media there lives in the
# name-excluded `renders/` subfolder (original names preserved); the only other
# media under `episodes/` are the episode-root final cuts (`ep{NN}_{lang}.mp4`,
# written by the subtitle-burn / concat feature) whose deliberate language-tagged
# names must be preserved — the folder-name rename would otherwise collapse them
# to `ep{NN}{i}.mp4` (follow-up 128). Only `characters/`, `scenes/`, and scene
# `bg*` plate folders are canonicalized by the rename pass.
EPISODES_DIR_NAME = "episodes"
# Reserved canonical filenames the folder-name rename must NOT touch: a character
# folder's `intro_card.{ext}` (ai_video.md rule 11d) has a fixed name unrelated to
# the folder name — without this guard it gets collapsed to `{folder}{N}.png` and
# the intro-card burn can no longer find it (follow-up wushen_juexing intro-card).
_RESERVED_STEMS = frozenset({"intro_card"})


def _uniquify(target: Path) -> Path:
    if not target.exists():
        return target
    stem = target.stem
    suffix = target.suffix
    ts = time.strftime("%Y%m%d-%H%M%S")
    candidate = target.with_name(f"{stem}.{ts}{suffix}")
    n = 1
    while candidate.exists():
        candidate = target.with_name(f"{stem}.{ts}-{n}{suffix}")
        n += 1
    return candidate


# A media file that is being previewed in the browser is streamed THROUGH this same
# server process (range requests), so the process holds an open read handle on it. On
# Windows that makes an immediate rename fail with "在使用中/Device or resource busy".
# The handle releases the instant the player stops/unloads, so retry across a short
# window: the frontend unloads the <video> right before calling delete, and these
# retries cover the few-hundred-ms it takes the OS to drop the handle.
_DELETE_RETRIES: int = 15
_DELETE_RETRY_DELAY_S: float = 0.2


def _rename_through_lock(src: Path, target: Path) -> None:
    """Move `src` → `target`, retrying through a transient share-lock (a browser
    preview stream releasing). Last resort: copy + unlink. Raises MediaMoveFailedError
    only if the file is still locked after the whole retry window."""
    last: OSError | None = None
    for _ in range(_DELETE_RETRIES):
        try:
            src.rename(target)
            return
        except OSError as exc:
            last = exc
            time.sleep(_DELETE_RETRY_DELAY_S)
    # Fallback: copy then remove the original (a read-shared handle still allows the
    # copy; the unlink then succeeds once the writer/preview handle has dropped).
    try:
        shutil.copy2(src, target)
        src.unlink()
        return
    except OSError:
        target.unlink(missing_ok=True)  # don't leave a half/duplicate copy behind
    raise MediaMoveFailedError(
        f"{src.name} 仍被占用（重试 {_DELETE_RETRIES} 次后仍锁定）: {last}"
    )


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
            raise AlreadyArchivedError("file is already inside an archive/ folder")
        archive_dir = src.parent / ARCHIVE_DIR_NAME
        if archive_dir.exists() and not archive_dir.is_dir():
            raise MediaMoveFailedError(f"{ARCHIVE_DIR_NAME} exists but is not a directory")
        try:
            archive_dir.mkdir(exist_ok=True)
        except OSError as exc:
            raise MediaMoveFailedError(str(exc)) from exc
        dst = _uniquify(archive_dir / src.name)
        try:
            src.rename(dst)
        except OSError as exc:
            raise MediaMoveFailedError(str(exc)) from exc
        return MoveResult(src_rel=self._rel(src), dst_rel=self._rel(dst))

    def unarchive(self, rel: str) -> MoveResult:
        src = self._validate_media_source(rel)
        if src.parent.name != ARCHIVE_DIR_NAME:
            raise NotInArchiveError("file is not inside an archive/ folder")
        target_dir = src.parent.parent
        if not target_dir.is_dir():
            raise MediaMoveFailedError("parent of archive/ is missing")
        dst = target_dir / src.name
        if dst.exists():
            raise MediaTargetExistsError(self._rel(dst))
        try:
            src.rename(dst)
        except OSError as exc:
            raise MediaMoveFailedError(str(exc)) from exc
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
            raise NotUnderAiVideosError("delete only supports ai_videos paths")
        if len(parts) >= 2 and parts[1] == DELETED_DIR_NAME:
            raise AlreadyDeletedError("file is already inside _deleted/")
        rest_parts = parts[1:]
        target = self._resolver.root / AI_VIDEOS_ROOT_NAME / DELETED_DIR_NAME / Path(*rest_parts)
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise MediaMoveFailedError(str(exc)) from exc
        target = _uniquify(target)
        _rename_through_lock(src, target)
        return MoveResult(src_rel=self._rel(src), dst_rel=self._rel(target))

    def hard_delete(self, rel: str) -> str:
        src = self._validate_media_source(rel)
        relative = src.relative_to(self._resolver.root)
        parts = relative.parts
        if len(parts) < 2 or parts[0] != AI_VIDEOS_ROOT_NAME or parts[1] != DELETED_DIR_NAME:
            raise NotUnderDeletedError("hard_delete only operates inside ai_videos/_deleted/")
        rel_str = self._rel(src)
        try:
            src.unlink()
        except OSError as exc:
            raise MediaMoveFailedError(str(exc)) from exc
        return rel_str

    def purge_deleted(self) -> int:
        """Empty the recycle bin: recursively remove EVERYTHING under
        ai_videos/_deleted/ — files of any type (md / json / media / …) plus
        all subfolders — then remove the now-empty _deleted/ itself. Returns
        the count of files removed. Unlike hard_delete this applies no
        media-extension filter: the whole _deleted/ subtree is a purge target,
        which is why per-media purges used to leave the .md sidecars and empty
        folders behind."""
        deleted_root = self._resolver.root / AI_VIDEOS_ROOT_NAME / DELETED_DIR_NAME
        if not deleted_root.is_dir():
            return 0
        count = sum(1 for p in deleted_root.rglob("*") if p.is_file())
        try:
            shutil.rmtree(deleted_root)
        except OSError as exc:
            raise MediaMoveFailedError(str(exc)) from exc
        return count

    def _validate_media_source(self, rel: str) -> Path:
        if not isinstance(rel, str) or rel == "":
            raise InvalidMediaPathError("path is empty")
        if not self._exposed.is_inside(rel):
            raise MediaNotFoundError("path outside sandbox")
        ext = Path(rel).suffix.lower()
        if ext not in MEDIA_EXTENSIONS:
            raise NotMediaError("extension is not a media type")
        resolved = self._resolver.resolve(rel)
        if resolved is None or not resolved.is_file():
            raise MediaNotFoundError("file does not exist")
        if resolved.is_symlink():
            raise MediaNotFoundError("symlink is not allowed")
        return resolved

    def _rel(self, p: Path) -> str:
        try:
            return p.resolve().relative_to(self._resolver.root).as_posix()
        except (OSError, ValueError):
            return p.as_posix()


@dataclass(frozen=True)
class RenameOp:
    src: Path
    dst: Path


@dataclass(frozen=True)
class RenameError:
    path: str
    message: str


@dataclass
class RenameResult:
    renamed: list[dict[str, str]] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    errors: list[dict[str, str]] = field(default_factory=list)

    def to_payload(self) -> dict[str, object]:
        return {
            "renamed": list(self.renamed),
            "skipped": list(self.skipped),
            "errors": list(self.errors),
        }


class MediaRenamer:
    def __init__(self, exposed: ExposedTree, resolver: SafeResolver) -> None:
        self._exposed = exposed
        self._resolver = resolver

    def rename_drama(
        self,
        rel_drama_path: str,
        excluded_folder_names: frozenset[str] | None = None,
    ) -> RenameResult:
        drama_dir = self._validate_drama(rel_drama_path)
        result = RenameResult()
        excluded = self._exposed.excluded_dirs() | {EPISODES_DIR_NAME}
        if excluded_folder_names:
            excluded = frozenset(excluded | excluded_folder_names)
        ops: list[RenameOp] = []
        skipped_paths: list[str] = []
        for folder in self._iter_folders(drama_dir, excluded):
            folder_ops, folder_skipped = self._plan_folder(folder)
            ops.extend(folder_ops)
            skipped_paths.extend(folder_skipped)
        self._apply_ops(ops, result)
        for sk in skipped_paths:
            result.skipped.append(sk)
        return result

    def validate_drama(self, rel: str) -> Path:
        """Public wrapper around _validate_drama for use by sibling modules
        (e.g. DownloadsImporter) that need the same drama-path validation."""
        return self._validate_drama(rel)

    def _validate_drama(self, rel: str) -> Path:
        if not isinstance(rel, str) or rel == "":
            raise InvalidDramaPathError("path is empty")
        normalized = rel.rstrip("/")
        parts = normalized.split("/")
        if len(parts) != 2 or parts[0] != "ai_videos" or parts[1] == "":
            raise InvalidDramaPathError("path must be 'ai_videos/{drama}'")
        if not self._exposed.is_inside(normalized):
            raise DramaNotFoundError("path outside sandbox")
        resolved = self._resolver.resolve(normalized)
        if resolved is None or not resolved.is_dir():
            raise DramaNotFoundError("drama directory does not exist")
        return resolved

    def _iter_folders(self, root: Path, excluded: frozenset[str]) -> list[Path]:
        out: list[Path] = [root]
        stack: list[Path] = [root]
        while stack:
            current = stack.pop()
            try:
                children = list(current.iterdir())
            except OSError:
                continue
            for child in children:
                if child.is_symlink():
                    continue
                if not child.is_dir():
                    continue
                if child.name in excluded:
                    continue
                out.append(child)
                stack.append(child)
        return out

    def _plan_folder(self, folder: Path) -> tuple[list[RenameOp], list[str]]:
        ops: list[RenameOp] = []
        skipped: list[str] = []
        try:
            entries = sorted(
                (p for p in folder.iterdir() if p.is_file() and not p.is_symlink()),
                key=lambda p: p.name,
            )
        except OSError:
            return ops, skipped
        by_ext: dict[str, list[Path]] = {}
        for p in entries:
            if p.stem.lower() in _RESERVED_STEMS:
                continue  # leave intro_card.* etc. at their fixed canonical name
            ext = p.suffix.lower()
            if ext in MEDIA_EXTENSIONS:
                by_ext.setdefault(ext, []).append(p)
        parent_name = folder.name
        for ext, files in by_ext.items():
            if len(files) == 1:
                target_names = [f"{parent_name}{ext}"]
            else:
                target_names = [f"{parent_name}{i + 1}{ext}" for i in range(len(files))]
            for src, target_name in zip(files, target_names):
                if src.name == target_name:
                    skipped.append(self._rel(src))
                    continue
                ops.append(RenameOp(src=src, dst=src.with_name(target_name)))
        return ops, skipped

    def _apply_ops(self, ops: list[RenameOp], result: RenameResult) -> None:
        if not ops:
            return
        token = uuid.uuid4().hex[:12]
        temp_paths: list[tuple[RenameOp, Path]] = []
        for idx, op in enumerate(ops):
            tmp = op.src.with_name(f".__rename_tmp_{token}_{idx}{op.src.suffix}")
            try:
                op.src.rename(tmp)
            except OSError as exc:
                result.errors.append({"path": self._rel(op.src), "message": str(exc)})
                continue
            temp_paths.append((op, tmp))
        for op, tmp in temp_paths:
            try:
                tmp.rename(op.dst)
                result.renamed.append({"from": self._rel(op.src), "to": self._rel(op.dst)})
            except OSError as exc:
                try:
                    tmp.rename(op.src)
                except OSError:
                    result.errors.append({
                        "path": self._rel(tmp),
                        "message": f"orphan temp after failed rename to {op.dst.name}: {exc}",
                    })
                    continue
                result.errors.append({"path": self._rel(op.src), "message": str(exc)})

    def _rel(self, p: Path) -> str:
        try:
            return p.resolve().relative_to(self._resolver.root).as_posix()
        except (OSError, ValueError):
            return p.as_posix()
