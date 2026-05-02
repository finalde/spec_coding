from __future__ import annotations

import json
from typing import AsyncIterator

from fastapi import APIRouter, Depends, HTTPException, Request
from sse_starlette.sse import EventSourceResponse

from ..runs import RunNotFoundError, RunRegistry

router = APIRouter()


def _registry(request: Request) -> RunRegistry:
    return request.app.state.runs


def _last_event_id(request: Request) -> int:
    raw = request.headers.get("last-event-id")
    if raw is None:
        return -1
    try:
        return int(raw)
    except ValueError:
        return -1


@router.get("/tasks/{task_id}/runs/{run_id}/events")
async def stream_events(
    task_id: str,
    run_id: str,
    request: Request,
    runs: RunRegistry = Depends(_registry),
) -> EventSourceResponse:
    try:
        state = runs.get(run_id)
    except RunNotFoundError:
        raise HTTPException(status_code=404, detail=f"run {run_id} not found")
    if state.task_id != task_id:
        raise HTTPException(status_code=400, detail="task_id does not match run")

    after = _last_event_id(request)

    async def event_gen() -> AsyncIterator[dict]:
        async for ev in runs.subscribe(run_id, after_seq=after):
            if await request.is_disconnected():
                return
            yield {
                "id": str(ev["seq"]),
                "event": ev.get("type", "message"),
                "data": json.dumps(ev, ensure_ascii=False),
            }

    return EventSourceResponse(event_gen())
