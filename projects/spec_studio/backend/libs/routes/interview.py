from __future__ import annotations

import hashlib

from fastapi import APIRouter, Depends, HTTPException, Request

from ..models import (
    ArtifactSaveResult,
    InterviewOption,
    InterviewQA,
    InterviewQuestion,
    InterviewRound,
)
from ..parsers import (
    InterviewOptionData,
    InterviewQAData,
    InterviewQuestionData,
    QAParseError,
    parse_qa,
    render_qa,
)
from ..parsers.qa_parser import InterviewRoundData
from ..storage import FileStore
from ..storage.file_store import TaskNotFoundError
from ..storage.safe_writer import BackupWriter

router = APIRouter()


def _store(request: Request) -> FileStore:
    return request.app.state.store


def _writer(request: Request) -> BackupWriter:
    return request.app.state.backup_writer


def _to_model(data: InterviewQAData, sha: str | None) -> InterviewQA:
    rounds = [
        InterviewRound(
            number=r.number,
            questions=[
                InterviewQuestion(
                    qid=q.qid,
                    perspective=q.perspective,
                    text=q.text,
                    kind=q.kind,
                    options=[
                        InterviewOption(
                            key=o.key,
                            text=o.text,
                            picked=o.picked,
                            freeform_value=o.freeform_value,
                        )
                        for o in q.options
                    ],
                    notes=q.notes,
                )
                for q in r.questions
            ],
        )
        for r in data.rounds
    ]
    return InterviewQA(
        task_id=data.task_id,
        initial_prompt_ref=data.initial_prompt_ref,
        rounds=rounds,
        open_questions=list(data.open_questions),
        sha256=sha,
    )


def _to_data(model: InterviewQA) -> InterviewQAData:
    rounds: list[InterviewRoundData] = []
    for rnd in model.rounds:
        rounds.append(InterviewRoundData(
            number=rnd.number,
            questions=[
                InterviewQuestionData(
                    qid=q.qid,
                    perspective=q.perspective,
                    text=q.text,
                    kind=q.kind,
                    options=[
                        InterviewOptionData(
                            key=o.key,
                            text=o.text,
                            picked=o.picked,
                            freeform_value=o.freeform_value,
                        )
                        for o in q.options
                    ],
                    notes=q.notes,
                )
                for q in rnd.questions
            ],
        ))
    return InterviewQAData(
        task_id=model.task_id,
        initial_prompt_ref=model.initial_prompt_ref,
        rounds=rounds,
        open_questions=list(model.open_questions),
    )


@router.get("/tasks/{task_id}/interview", response_model=InterviewQA)
def get_interview(
    task_id: str,
    store: FileStore = Depends(_store),
) -> InterviewQA:
    try:
        store.get_task(task_id)
    except TaskNotFoundError:
        raise HTTPException(status_code=404, detail=f"task {task_id} not found")
    artifact = store.read_artifact(task_id, "qa")
    if not artifact.exists or not artifact.content:
        return InterviewQA(task_id=task_id, rounds=[], open_questions=[])
    try:
        data = parse_qa(artifact.content)
    except QAParseError as e:
        raise HTTPException(status_code=422, detail=f"qa.md parse error: {e}")
    sha = hashlib.sha256(artifact.content.encode("utf-8")).hexdigest()
    return _to_model(data, sha)


@router.put("/tasks/{task_id}/interview", response_model=ArtifactSaveResult)
def put_interview(
    task_id: str,
    payload: InterviewQA,
    store: FileStore = Depends(_store),
    writer: BackupWriter = Depends(_writer),
) -> ArtifactSaveResult:
    try:
        store.get_task(task_id)
    except TaskNotFoundError:
        raise HTTPException(status_code=404, detail=f"task {task_id} not found")
    rendered = render_qa(_to_data(payload))
    path = store.artifact_path(task_id, "qa")
    result = writer.write(path, rendered)
    return ArtifactSaveResult(
        path=str(result.path),
        sha256=result.sha256,
        bytes_written=result.bytes_written,
        backed_up=result.backed_up,
    )
