"""Performance-library routes:
- POST /api/performance-candidates  — rank top-N library entries for a shot.
- POST /api/shot-performance-refs    — persist chosen perf_ids into the shot.md.
"""
from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

from apps.api.container import Container
from libs.application.commands.shot_performance__command import ShotPerformanceCommand
from libs.application.queries.performance_candidate__query import (
    PerformanceCandidateQuery,
)

router = APIRouter()


class PerformanceCandidatesBody(BaseModel):
    shot_path: str
    emotion: str | None = None
    intensity: int | None = None
    duration_s: float | None = None
    top_n: int = 8


class ShotPerformanceRefsBody(BaseModel):
    shot_path: str
    perf_ids: list[str]
    mtime: str | None = None


@router.post("/api/performance-candidates")
@inject
def performance_candidates(
    body: PerformanceCandidatesBody,
    query: PerformanceCandidateQuery = Depends(Provide[Container.performance_candidate_query]),
) -> Response:
    qdto = query.recommend(
        shot_path=body.shot_path,
        emotion=body.emotion,
        intensity=body.intensity,
        duration_s=body.duration_s,
        top_n=body.top_n,
    )
    return JSONResponse(status_code=200, content=qdto.to_payload())


@router.post("/api/shot-performance-refs")
@inject
def shot_performance_refs(
    body: ShotPerformanceRefsBody,
    command: ShotPerformanceCommand = Depends(Provide[Container.shot_performance_command]),
) -> Response:
    result = command.set_refs(
        shot_path=body.shot_path,
        perf_ids=body.perf_ids,
        mtime=body.mtime,
    )
    return JSONResponse(status_code=200, content=result.to_payload())
