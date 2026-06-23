"""Episode-aggregate routes: POST /api/concat-episode."""
from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

from apps.api.container import Container
from libs.application.commands.episode__command import EpisodeCommand

router = APIRouter()


class ConcatEpisodeBody(BaseModel):
    path: str
    lang: str = "original"  # "original" | "zh" | "en" | "both"
    rife: bool = False       # RIFE motion-bridge the 承接 seams (slower, needs GPU exe)


@router.post("/api/concat-episode")
@inject
def concat_episode(
    body: ConcatEpisodeBody,
    command: EpisodeCommand = Depends(Provide[Container.episode_command]),
) -> Response:
    return JSONResponse(
        status_code=200,
        content=command.concat(body.path, body.lang, body.rife).to_payload(),
    )
