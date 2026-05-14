"""Drama-scoped batch rename for media (image + video) files.

Per follow-up 007: a single button at the drama level triggers a recursive
walk that renames each image / video file to match its immediate parent
folder's name. Multiple files of the same extension in the same folder get
1-based numeric suffixes in lexicographic order; a single file of an
extension gets the bare folder name. Files already on their target name are
skipped. Two-pass via temp names avoids intra-folder collisions.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from pathlib import Path

from libs.common.exposed_tree import ExposedTree, MEDIA_EXTENSIONS
from libs.common.safe_resolve import SafeResolver


class InvalidDramaPath(Exception):
    pass


class DramaNotFound(Exception):
    pass


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
        excluded = self._exposed.excluded_dirs()
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
            raise InvalidDramaPath("path is empty")
        normalized = rel.rstrip("/")
        parts = normalized.split("/")
        if len(parts) != 2 or parts[0] != "ai_videos" or parts[1] == "":
            raise InvalidDramaPath("path must be 'ai_videos/{drama}'")
        if not self._exposed.is_inside(normalized):
            raise DramaNotFound("path outside sandbox")
        resolved = self._resolver.resolve(normalized)
        if resolved is None or not resolved.is_dir():
            raise DramaNotFound("drama directory does not exist")
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
