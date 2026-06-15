"""Perf-score routes: POST /api/perf-score — record a 你/Claude review score."""
from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

from apps.api.container import Container
from libs.application.commands.perf_score__command import PerfScoreCommand

router = APIRouter()


class PerfScoreBody(BaseModel):
    path: str
    who: str  # 你 | Claude
    da_yi: int | None = None
    qing_xu: int | None = None
    guo_huo: int | None = None
    note: str = ""


@router.post("/api/perf-score")
@inject
def perf_score(
    body: PerfScoreBody,
    command: PerfScoreCommand = Depends(Provide[Container.perf_score_command]),
) -> Response:
    result = command.apply(
        body.path, body.who, body.da_yi, body.qing_xu, body.guo_huo, body.note
    )
    return JSONResponse(status_code=200, content=result)
