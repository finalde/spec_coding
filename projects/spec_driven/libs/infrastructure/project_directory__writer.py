from __future__ import annotations

import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libs.domain.project__error import (
    InvalidProjectName,
    ProjectNotFound,
    SelfDeleteRefused,
    UnsupportedTaskType,
)

_SLUG_RE = re.compile(r"^[a-zA-Z0-9_][a-zA-Z0-9_-]*$")

_TASK_TYPE_TO_OUTPUT_DIR: dict[str, str] = {
    "ai_video": "ai_videos",
    "development": "projects",
}
ALLOWED_TASK_TYPES_FOR_DELETE: frozenset[str] = frozenset(_TASK_TYPE_TO_OUTPUT_DIR.keys())

_SELF_PROJECT: tuple[str, str] = ("development", "spec_driven")


@dataclass(frozen=True)
class ProjectDeleteDao:
    project_type: str
    project_name: str
    deleted_paths: tuple[str, ...]
    not_found_paths: tuple[str, ...]

    def to_payload(self) -> dict[str, Any]:
        return {
            "project_type": self.project_type,
            "project_name": self.project_name,
            "deleted_paths": list(self.deleted_paths),
            "not_found_paths": list(self.not_found_paths),
        }


class ProjectDirectoryWriter:
    def __init__(self, repo_root: Path) -> None:
        self._root = repo_root.resolve()

    def delete(self, project_type: str, project_name: str) -> ProjectDeleteDao:
        if project_type not in ALLOWED_TASK_TYPES_FOR_DELETE:
            raise UnsupportedTaskType(project_type)
        if not isinstance(project_name, str) or not _SLUG_RE.match(project_name):
            raise InvalidProjectName(project_name)
        if (project_type, project_name) == _SELF_PROJECT:
            raise SelfDeleteRefused()

        output_dir_name = _TASK_TYPE_TO_OUTPUT_DIR[project_type]
        spec_dir = self._root / "specs" / project_type / project_name
        output_dir = self._root / output_dir_name / project_name
        allowed_top_level = {"specs", *_TASK_TYPE_TO_OUTPUT_DIR.values()}

        targets = [spec_dir, output_dir]
        for t in targets:
            t_resolved = t.resolve(strict=False)
            if t_resolved == self._root:
                raise InvalidProjectName(project_name)
            if self._root not in t_resolved.parents:
                raise InvalidProjectName(project_name)
            try:
                rel = t_resolved.relative_to(self._root)
            except ValueError as e:
                raise InvalidProjectName(project_name) from e
            parts = rel.parts
            if not parts or parts[0] not in allowed_top_level:
                raise InvalidProjectName(project_name)

        any_exists = any(t.is_dir() for t in targets)
        if not any_exists:
            raise ProjectNotFound(f"{project_type}/{project_name}")

        deleted: list[str] = []
        not_found: list[str] = []
        for t in targets:
            rel_str = t.relative_to(self._root).as_posix()
            if t.is_dir():
                if t.is_symlink():
                    raise InvalidProjectName(project_name)
                shutil.rmtree(t)
                deleted.append(rel_str)
            else:
                not_found.append(rel_str)

        return ProjectDeleteDao(
            project_type=project_type,
            project_name=project_name,
            deleted_paths=tuple(deleted),
            not_found_paths=tuple(not_found),
        )
