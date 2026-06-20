"""Subtitle-aggregate routes: per-shot burn / scaffold, plus batch
scaffold-episode and burn-drama."""
from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

from apps.api.container import Container
from libs.application.commands.subtitle__command import SubtitleCommand
from libs.application.commands.subtitle_batch__command import SubtitleBatchCommand

router = APIRouter()


class SubtitlePathBody(BaseModel):
    path: str


class BurnSubtitlesBody(BaseModel):
    path: str
    lang: str = "zh"  # "zh" | "en" | "both"


@router.post("/api/burn-subtitles")
@inject
def burn_subtitles(
    body: BurnSubtitlesBody,
    command: SubtitleCommand = Depends(Provide[Container.subtitle_command]),
) -> Response:
    return JSONResponse(
        status_code=200, content=command.burn(body.path, body.lang).to_payload()
    )


@router.post("/api/scaffold-subtitles")
@inject
def scaffold_subtitles(
    body: SubtitlePathBody,
    command: SubtitleCommand = Depends(Provide[Container.subtitle_command]),
) -> Response:
    return JSONResponse(status_code=200, content=command.scaffold(body.path).to_payload())


@router.post("/api/scaffold-episode-subtitles")
@inject
def scaffold_episode_subtitles(
    body: SubtitlePathBody,
    command: SubtitleBatchCommand = Depends(Provide[Container.subtitle_batch_command]),
) -> Response:
    return JSONResponse(
        status_code=200, content=command.scaffold_episode(body.path).to_payload()
    )


@router.post("/api/burn-drama-subtitles")
@inject
def burn_drama_subtitles(
    body: BurnSubtitlesBody,
    command: SubtitleBatchCommand = Depends(Provide[Container.subtitle_batch_command]),
) -> Response:
    return JSONResponse(
        status_code=200, content=command.burn_drama(body.path, body.lang).to_payload()
    )
