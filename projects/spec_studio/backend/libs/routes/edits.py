from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request

from ..edits import RepoInputResolver, RepoPathError
from ..models import (
    ArtifactEditBody,
    ArtifactSaveResult,
    EditableArtifactKind,
    RepoEditBody,
)
from ..storage import FileStore
from ..storage.file_store import TaskNotFoundError
from ..storage.safe_writer import BackupWriter, hash_text

router = APIRouter()

_VALID_EDITABLE: set[str] = {"qa", "spec", "plan", "initial_prompt"}


def _store(request: Request) -> FileStore:
    return request.app.state.store


def _resolver(request: Request) -> RepoInputResolver:
    return request.app.state.repo_resolver


def _writer(request: Request) -> BackupWriter:
    return request.app.state.backup_writer


def _save_with_etag(
    writer: BackupWriter,
    path: Path,
    content: str,
    if_match: str | None,
) -> ArtifactSaveResult:
    stale = False
    if if_match is not None and path.exists():
        existing_hash = hash_text(path.read_text(encoding="utf-8"))
        if existing_hash != if_match:
            stale = True
    result = writer.write(path, content)
    return ArtifactSaveResult(
        path=str(result.path),
        sha256=result.sha256,
        bytes_written=result.bytes_written,
        backed_up=result.backed_up,
        stale_etag=stale,
    )


@router.put("/tasks/{task_id}/artifacts/{kind}", response_model=ArtifactSaveResult)
def put_artifact(
    task_id: str,
    kind: str,
    payload: ArtifactEditBody,
    store: FileStore = Depends(_store),
    writer: BackupWriter = Depends(_writer),
) -> ArtifactSaveResult:
    if kind not in _VALID_EDITABLE:
        raise HTTPException(
            status_code=400,
            detail=f"artifact '{kind}' is not editable. valid: {sorted(_VALID_EDITABLE)}",
        )
    try:
        store.get_task(task_id)
    except TaskNotFoundError:
        raise HTTPException(status_code=404, detail=f"task {task_id} not found")
    path = store.artifact_path(task_id, kind)  # type: ignore[arg-type]
    return _save_with_etag(writer, path, payload.content, payload.if_match)


@router.put("/inputs/{name}", response_model=ArtifactSaveResult)
def put_input(
    name: str,
    payload: RepoEditBody,
    resolver: RepoInputResolver = Depends(_resolver),
    writer: BackupWriter = Depends(_writer),
) -> ArtifactSaveResult:
    if not payload.confirm:
        raise HTTPException(
            status_code=400,
            detail=f"editing repo input '{name}' requires confirm: true in body",
        )
    try:
        resolved = resolver.resolve_input(name)
    except RepoPathError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return _save_with_etag(writer, resolved.path, payload.content, payload.if_match)


@router.put("/agents/{agent_name}", response_model=ArtifactSaveResult)
def put_agent(
    agent_name: str,
    payload: RepoEditBody,
    resolver: RepoInputResolver = Depends(_resolver),
    writer: BackupWriter = Depends(_writer),
) -> ArtifactSaveResult:
    if not payload.confirm:
        raise HTTPException(
            status_code=400,
            detail=f"editing agent '{agent_name}' requires confirm: true in body",
        )
    try:
        resolved = resolver.resolve_agent(agent_name)
    except RepoPathError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return _save_with_etag(writer, resolved.path, payload.content, payload.if_match)
