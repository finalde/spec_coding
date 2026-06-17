"""Subtitle-aggregate routes: POST /api/burn-subtitles, /api/scaffold-subtitles."""
from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

from apps.api.container import Container
from libs.application.commands.subtitle__command import SubtitleCommand

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
