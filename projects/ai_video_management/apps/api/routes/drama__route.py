"""Drama-level routes for the production console (main page):
POST /api/list-drama-episodes + POST /api/select-drama-takes (全局定版)."""
from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

from apps.api.container import Container
from libs.application.commands.drama_takes__command import DramaTakesCommand
from libs.application.queries.drama_episodes__query import DramaEpisodesQuery

router = APIRouter()


class DramaScopeBody(BaseModel):
    path: str  # any file or folder under ai_videos/{drama}/


@router.post("/api/list-drama-episodes")
@inject
def list_drama_episodes(
    body: DramaScopeBody,
    query: DramaEpisodesQuery = Depends(Provide[Container.drama_episodes_query]),
) -> Response:
    return JSONResponse(status_code=200, content=query.list(body.path).to_payload())


@router.post("/api/select-drama-takes")
@inject
def select_drama_takes(
    body: DramaScopeBody,
    command: DramaTakesCommand = Depends(Provide[Container.drama_takes_command]),
) -> Response:
    return JSONResponse(
        status_code=200, content=command.select_all(body.path).to_payload()
    )
