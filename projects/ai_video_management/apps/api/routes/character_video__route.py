"""Character-video aggregate routes: truncate / concat-shot / extract-views."""
from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

from apps.api.container import Container
from libs.application.commands.character_video__command import CharacterVideoCommand

router = APIRouter()


class TruncateCharacterVideoBody(BaseModel):
    path: str


class ConcatShotCharactersBody(BaseModel):
    path: str


class ExtractCharacterViewsBody(BaseModel):
    path: str


@router.post("/api/truncate-character-video")
@inject
def truncate_character_video(
    body: TruncateCharacterVideoBody,
    command: CharacterVideoCommand = Depends(Provide[Container.character_video_command]),
) -> Response:
    return JSONResponse(status_code=200, content=command.truncate(body.path).to_payload())


@router.post("/api/concat-shot-characters")
@inject
def concat_shot_characters(
    body: ConcatShotCharactersBody,
    command: CharacterVideoCommand = Depends(Provide[Container.character_video_command]),
) -> Response:
    return JSONResponse(status_code=200, content=command.concat_shot(body.path).to_payload())


@router.post("/api/extract-character-views")
@inject
def extract_character_views(
    body: ExtractCharacterViewsBody,
    command: CharacterVideoCommand = Depends(Provide[Container.character_video_command]),
) -> Response:
    return JSONResponse(status_code=200, content=command.extract_views(body.path).to_payload())
