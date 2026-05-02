from __future__ import annotations

import hashlib
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request

from ..edits import RepoInputResolver
from ..models import InputBundle, InputSource, InputSourceKind
from ..storage import FileStore
from ..storage.file_store import TaskNotFoundError

router = APIRouter()


def _store(request: Request) -> FileStore:
    return request.app.state.store


def _resolver(request: Request) -> RepoInputResolver:
    return request.app.state.repo_resolver


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _read_source(kind: InputSourceKind, path: Path, requires_confirm: bool) -> InputSource:
    content = path.read_text(encoding="utf-8") if path.exists() else ""
    return InputSource(
        kind=kind,
        path=str(path),
        content=content,
        editable=True,
        sha256=_hash(content),
        requires_confirm=requires_confirm,
    )


@router.get("/tasks/{task_id}/inputs", response_model=InputBundle)
def get_inputs(
    task_id: str,
    store: FileStore = Depends(_store),
    resolver: RepoInputResolver = Depends(_resolver),
) -> InputBundle:
    try:
        store.get_task(task_id)
    except TaskNotFoundError:
        raise HTTPException(status_code=404, detail=f"task {task_id} not found")

    sources = [
        _read_source("claude_md", resolver.claude_md, requires_confirm=True),
        _read_source("skill_md", resolver.skill_md, requires_confirm=True),
        _read_source("phase_manager_md", store.current_phase_manager_path(task_id), requires_confirm=True),
        _read_source("initial_prompt", store.artifact_path(task_id, "initial_prompt"), requires_confirm=False),
    ]
    return InputBundle(task_id=task_id, sources=sources)
