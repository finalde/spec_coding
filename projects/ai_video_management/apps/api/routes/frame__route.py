"""Frame-aggregate routes: POST /api/extract-frames, POST /api/extract-last-frame."""
from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

from apps.api.container import Container
from libs.application.commands.frame__command import FrameCommand

router = APIRouter()


class ExtractFramesBody(BaseModel):
    path: str


@router.post("/api/extract-frames")
@inject
def extract_frames(
    body: ExtractFramesBody,
    command: FrameCommand = Depends(Provide[Container.frame_command]),
) -> Response:
    return JSONResponse(status_code=200, content=command.extract(body.path).to_payload())


@router.post("/api/extract-last-frame")
@inject
def extract_last_frame(
    body: ExtractFramesBody,
    command: FrameCommand = Depends(Provide[Container.frame_command]),
) -> Response:
    return JSONResponse(
        status_code=200, content=command.extract_last_frame(body.path).to_payload()
    )
