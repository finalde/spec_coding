from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request

from ..models import CreateTask, RootFolder, Task, TaskSummary
from ..storage import FileStore
from ..storage.file_store import TaskNotFoundError

router = APIRouter()


def _store(request: Request) -> FileStore:
    return request.app.state.store


@router.get("/enums/root-folders", response_model=list[str])
def get_root_folders() -> list[str]:
    return [rf.value for rf in RootFolder]


@router.get("/tasks", response_model=list[TaskSummary])
def list_tasks(store: FileStore = Depends(_store)) -> list[TaskSummary]:
    return store.list_tasks()


@router.post("/tasks", response_model=Task, status_code=201)
def create_task(payload: CreateTask, store: FileStore = Depends(_store)) -> Task:
    return store.create_task(payload)


@router.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: str, store: FileStore = Depends(_store)) -> Task:
    try:
        return store.get_task(task_id)
    except TaskNotFoundError:
        raise HTTPException(status_code=404, detail=f"task {task_id} not found")
