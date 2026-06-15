"""Scene-plate routes: POST /api/extract-scene-plates."""
from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

from apps.api.container import Container
from libs.application.commands.scene_plate__command import ScenePlateCommand

router = APIRouter()


class ExtractScenePlatesBody(BaseModel):
    path: str


@router.post("/api/extract-scene-plates")
@inject
def extract_scene_plates(
    body: ExtractScenePlatesBody,
    command: ScenePlateCommand = Depends(Provide[Container.scene_plate_command]),
) -> Response:
    return JSONResponse(status_code=200, content=command.extract(body.path).to_payload())
