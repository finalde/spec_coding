"""Perf-check routes: POST /api/perf-check-prompt — locate the entry's
downloaded MP4 and assemble a copy-paste "让 Claude 检查并打分" prompt
(errors when zero or multiple MP4s are present)."""
from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

from apps.api.container import Container
from libs.application.queries.perf_check__query import PerfCheckPromptQuery

router = APIRouter()


class PerfCheckBody(BaseModel):
    path: str


@router.post("/api/perf-check-prompt")
@inject
def perf_check_prompt(
    body: PerfCheckBody,
    query: PerfCheckPromptQuery = Depends(Provide[Container.perf_check_query]),
) -> Response:
    return JSONResponse(status_code=200, content=query.build(body.path))
