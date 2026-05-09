"""Parent-level project deletion.

Per follow-up 010: deletes the spec-pipeline trail under `specs/{type}/{name}/`
plus the generated output under the type-specific output dir.
Per follow-up 011: extended to `task_type ∈ {ai_video, development}`. Output dirs:
  - `ai_video`     → `ai_videos/{name}/`
  - `development`  → `projects/{name}/`

The running spec_driven webapp is hard-protected from UI-driven self-deletion
(`development/spec_driven` → `SelfDeleteRefused`).
"""
from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# Strict slug: must start with alphanumeric or underscore; only [a-zA-Z0-9_-] thereafter.
# Rejects: empty, `..`, `/`, `\`, leading `.`, drive letters, percent-encoding.
_SLUG_RE = re.compile(r"^[a-zA-Z0-9_][a-zA-Z0-9_-]*$")

# Per follow-up 011: generic across the canonical task types.
_TASK_TYPE_TO_OUTPUT_DIR: dict[str, str] = {
    "ai_video": "ai_videos",
    "development": "projects",
}
ALLOWED_TASK_TYPES_FOR_DELETE: frozenset[str] = frozenset(_TASK_TYPE_TO_OUTPUT_DIR.keys())

# Hard-protected: deleting the running webapp's own source via the UI would
# kill the process mid-response and leave a half-deleted tree.
_SELF_PROJECT: tuple[str, str] = ("development", "spec_driven")


class UnsupportedTaskType(Exception):
    """Project type is not allowed for parent-level delete."""

    def __init__(self, task_type: str) -> None:
        super().__init__(f"unsupported task_type for delete: {task_type}")
        self.task_type: str = task_type


class InvalidProjectName(Exception):
    """Project name fails slug validation (path traversal / special chars / empty)."""


class ProjectNotFound(Exception):
    """Neither `specs/{type}/{name}/` nor the output dir exists."""


class SelfDeleteRefused(Exception):
    """Refusing to delete the running webapp's own source via the UI."""

    def __init__(self) -> None:
        super().__init__(
            "refusing UI-driven self-delete of development/spec_driven (the running webapp)"
        )


@dataclass(frozen=True)
class DeleteResult:
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


class ProjectDeleter:
    def __init__(self, repo_root: Path) -> None:
        self._root = repo_root.resolve()

    def delete(self, project_type: str, project_name: str) -> DeleteResult:
        if project_type not in ALLOWED_TASK_TYPES_FOR_DELETE:
            raise UnsupportedTaskType(project_type)
        if not isinstance(project_name, str) or not _SLUG_RE.match(project_name):
            raise InvalidProjectName(project_name)
        if (project_type, project_name) == _SELF_PROJECT:
            raise SelfDeleteRefused()

        # Compute target paths server-side (never trust client-supplied paths).
        output_dir_name = _TASK_TYPE_TO_OUTPUT_DIR[project_type]
        spec_dir = self._root / "specs" / project_type / project_name
        output_dir = self._root / output_dir_name / project_name
        allowed_top_level = {"specs", *_TASK_TYPE_TO_OUTPUT_DIR.values()}

        # Defense in depth: each resolved target must be inside the workspace AND
        # under one of the allowed top-level dirs. (rmtree on the wrong path
        # is catastrophic; we double-check before any FS mutation.)
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

        # Existence check: at least one must exist, otherwise 404.
        any_exists = any(t.is_dir() for t in targets)
        if not any_exists:
            raise ProjectNotFound(f"{project_type}/{project_name}")

        deleted: list[str] = []
        not_found: list[str] = []
        for t in targets:
            rel_str = t.relative_to(self._root).as_posix()
            if t.is_dir():
                # Refuse to follow symlinks at the root level.
                if t.is_symlink():
                    raise InvalidProjectName(project_name)
                shutil.rmtree(t)
                deleted.append(rel_str)
            else:
                not_found.append(rel_str)

        return DeleteResult(
            project_type=project_type,
            project_name=project_name,
            deleted_paths=tuple(deleted),
            not_found_paths=tuple(not_found),
        )


def emit_audit_event(repo_root: Path, result: DeleteResult, audit_dir: Path | None = None) -> None:
    """Append a `project.deleted` event line to the audit JSONL.

    audit_dir defaults to `.audit/adhoc_agents/{YYYY-MM-DD}/manual_ops/`.
    """
    now = datetime.now(tz=timezone.utc)
    date_str = now.strftime("%Y-%m-%d")
    if audit_dir is None:
        audit_dir = repo_root / ".audit" / "adhoc_agents" / date_str / "manual_ops"
    audit_dir.mkdir(parents=True, exist_ok=True)
    audit_path = audit_dir / "events.jsonl"
    event = {
        "ts": now.isoformat(timespec="seconds"),
        "event": "project.deleted",
        "project_type": result.project_type,
        "project_name": result.project_name,
        "deleted_paths": list(result.deleted_paths),
        "not_found_paths": list(result.not_found_paths),
    }
    with audit_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")
