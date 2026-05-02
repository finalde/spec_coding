from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request

from ..models import Artifact, ArtifactKind
from ..storage import FileStore
from ..storage.file_store import TaskNotFoundError

router = APIRouter()


def _store(request: Request) -> FileStore:
    return request.app.state.store


_VALID_KINDS: set[str] = {"qa", "spec", "adjustments", "dossier", "plan", "findings_report"}


@router.get("/tasks/{task_id}/artifacts/{kind}", response_model=Artifact)
def get_artifact(
    task_id: str,
    kind: str,
    store: FileStore = Depends(_store),
) -> Artifact:
    if kind not in _VALID_KINDS:
        raise HTTPException(
            status_code=400,
            detail=f"unknown artifact kind '{kind}'. valid: {sorted(_VALID_KINDS)}",
        )
    try:
        store.get_task(task_id)
    except TaskNotFoundError:
        raise HTTPException(status_code=404, detail=f"task {task_id} not found")
    return store.read_artifact(task_id, kind)  # type: ignore[arg-type]
