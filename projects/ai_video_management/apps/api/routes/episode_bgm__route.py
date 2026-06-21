"""Episode-BGM-aggregate routes: read cues / assign / unassign / burn.

The arrangement is the per-episode sparse cue timeline `episodes/ep{NN}/bgm/
bgm.md`. Burn muxes assigned cues onto `ep{NN}_zh.mp4` → `ep{NN}_zh_bgm.mp4`.
Domain errors translate to JSON via the global handlers in app_factory.
"""
from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

from apps.api.container import Container
from libs.application.commands.episode_bgm__command import EpisodeBgmCommand
from libs.application.queries.episode_bgm__query import EpisodeBgmQuery

router = APIRouter()


class AssignBgmCueBody(BaseModel):
    path: str
    start: float
    end: float
    bgm_id: str


class UnassignBgmCueBody(BaseModel):
    path: str
    start: float
    end: float


class BurnEpisodeBgmBody(BaseModel):
    path: str


@router.get("/api/episode-bgm")
@inject
def episode_bgm_read(
    path: str = Query(...),
    query: EpisodeBgmQuery = Depends(Provide[Container.episode_bgm_query]),
) -> Response:
    return JSONResponse(status_code=200, content=query.read(path).to_payload())


@router.post("/api/episode-bgm/assign")
@inject
def episode_bgm_assign(
    body: AssignBgmCueBody,
    command: EpisodeBgmCommand = Depends(Provide[Container.episode_bgm_command]),
) -> Response:
    qdto = command.assign(body.path, body.start, body.end, body.bgm_id)
    return JSONResponse(status_code=200, content=qdto.to_payload())


@router.delete("/api/episode-bgm/assign")
@inject
def episode_bgm_unassign(
    body: UnassignBgmCueBody,
    command: EpisodeBgmCommand = Depends(Provide[Container.episode_bgm_command]),
) -> Response:
    qdto = command.unassign(body.path, body.start, body.end)
    return JSONResponse(status_code=200, content=qdto.to_payload())


@router.post("/api/episode-bgm/burn")
@inject
def episode_bgm_burn(
    body: BurnEpisodeBgmBody,
    command: EpisodeBgmCommand = Depends(Provide[Container.episode_bgm_command]),
) -> Response:
    cdto = command.burn(body.path)
    return JSONResponse(status_code=200, content=cdto.to_payload())
