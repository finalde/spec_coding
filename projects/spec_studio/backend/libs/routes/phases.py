from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request

from ..models import (
    Adjustments,
    InterviewAnswers,
    Phase,
    RunHandle,
    Task,
    TaskStatus,
)
from ..runs import RunRegistry
from ..storage import FileStore
from ..storage.file_store import TaskNotFoundError

router = APIRouter()


def _store(request: Request) -> FileStore:
    return request.app.state.store


def _registry(request: Request) -> RunRegistry:
    return request.app.state.runs


def _get_task(task_id: str, store: FileStore) -> Task:
    try:
        return store.get_task(task_id)
    except TaskNotFoundError:
        raise HTTPException(status_code=404, detail=f"task {task_id} not found")


_PHASE_BY_NAME = {
    "interview": Phase.INTERVIEW,
    "spec": Phase.SPEC,
    "research": Phase.RESEARCH,
    "plan": Phase.PLAN,
    "execute": Phase.EXECUTE,
    "validate-final": Phase.FINAL_VALIDATE,
}


@router.post("/tasks/{task_id}/{phase_name}/start", response_model=RunHandle)
async def start_phase(
    task_id: str,
    phase_name: str,
    store: FileStore = Depends(_store),
    runs: RunRegistry = Depends(_registry),
) -> RunHandle:
    phase = _PHASE_BY_NAME.get(phase_name)
    if phase is None:
        raise HTTPException(
            status_code=400,
            detail=f"unknown phase '{phase_name}'. valid: {sorted(_PHASE_BY_NAME)}",
        )
    task = _get_task(task_id, store)
    return await runs.start_phase(task, phase)


@router.post("/tasks/{task_id}/interview/answers", response_model=Task)
def submit_interview_answers(
    task_id: str,
    payload: InterviewAnswers,
    store: FileStore = Depends(_store),
) -> Task:
    task = _get_task(task_id, store)
    qa_path = store.artifact_path(task_id, "qa")
    qa_path.parent.mkdir(parents=True, exist_ok=True)
    header = "" if qa_path.exists() else f"# Interview — {task_id}\n\n"
    block = [header, f"## Round {payload.round} answers\n\n"]
    for ans in payload.answers:
        selected = ", ".join(ans.selected) if ans.selected else "(no selection)"
        block.append(f"### {ans.question_id}\n- selected: {selected}\n")
        if ans.notes:
            block.append(f"- notes: {ans.notes}\n")
        block.append("\n")
    with qa_path.open("a", encoding="utf-8") as f:
        f.write("".join(block))
    return store.update_task(task.id, status=TaskStatus.INTERVIEWING)


@router.post("/tasks/{task_id}/adjustments", response_model=Task)
def save_adjustments(
    task_id: str,
    payload: Adjustments,
    store: FileStore = Depends(_store),
) -> Task:
    task = _get_task(task_id, store)
    store.write_adjustments(task.id, payload)
    return store.update_task(
        task.id,
        status=TaskStatus.ADJUSTING,
        current_phase=Phase.PLAN,
    )
