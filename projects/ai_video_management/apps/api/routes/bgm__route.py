"""Bgm-aggregate routes: generate / preview-prompts / list / delete /
references.

Generation shells out to a self-hosted Stable Audio tool via subprocess
(`bgm__writer`); the webapp process never imports torch. All domain errors
translate to JSON via the global FastAPI handlers in
`apps/api/app_factory.py`. Route bodies stay narrow: shape the input, call
command/query, return success.
"""
from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

from apps.api.container import Container
from libs.application.commands.bgm__command import BgmCommand
from libs.application.dtos.bgm__dto import GenerateBgmsInputCdto
from libs.application.queries.bgm__query import BgmQuery

router = APIRouter()


class GenerateBgmsBody(BaseModel):
    count: int
    category: str
    mood: str = ""
    bpm: int = 90
    duration: int = 30
    loopable: bool = False
    intensity: int = 3
    instruments: str = ""
    notes: str = ""
    seeds: list[int] | None = None
    batch_seed: int | None = None
    batch_size: int | None = None
    slot_index: int | None = None


class DeleteBgmBody(BaseModel):
    bgm_id: str


@router.post("/api/bgms/generate")
@inject
def bgms_generate(
    body: GenerateBgmsBody,
    command: BgmCommand = Depends(Provide[Container.bgm_command]),
) -> Response:
    cdto = command.generate(GenerateBgmsInputCdto(**body.model_dump()))
    return JSONResponse(status_code=200, content=cdto.to_payload())


@router.post("/api/bgms/create-prompts")
@inject
def bgms_create_prompts(
    body: GenerateBgmsBody,
    command: BgmCommand = Depends(Provide[Container.bgm_command]),
) -> Response:
    """Step 1: allocate tracks + write prompt-only sidecars (no audio)."""
    cdto = command.create_prompts(GenerateBgmsInputCdto(**body.model_dump()))
    return JSONResponse(status_code=200, content=cdto.to_payload())


@router.post("/api/bgms/{bgm_id}/generate-audio")
@inject
def bgms_generate_audio(
    bgm_id: str,
    command: BgmCommand = Depends(Provide[Container.bgm_command]),
) -> Response:
    """Step 2a: render audio locally on GPU for an existing prompt-only track."""
    cdto = command.generate_audio(bgm_id)
    return JSONResponse(status_code=200, content=cdto.to_payload())


@router.post("/api/bgms/{bgm_id}/import-audio")
@inject
def bgms_import_audio(
    bgm_id: str,
    command: BgmCommand = Depends(Provide[Container.bgm_command]),
) -> Response:
    """Step 2b: import the newest Downloads audio file into an existing track."""
    cdto = command.import_audio(bgm_id)
    return JSONResponse(status_code=200, content=cdto.to_payload())


@router.post("/api/bgms/preview-prompts")
@inject
def bgms_preview_prompts(
    body: GenerateBgmsBody,
    query: BgmQuery = Depends(Provide[Container.bgm_query]),
) -> Response:
    qdto = query.preview_prompts(GenerateBgmsInputCdto(**body.model_dump()))
    return JSONResponse(status_code=200, content=qdto.to_payload())


@router.get("/api/bgms")
@inject
def bgms_list(query: BgmQuery = Depends(Provide[Container.bgm_query])) -> Response:
    return JSONResponse(status_code=200, content=query.list().to_payload())


@router.post("/api/bgms/delete")
@inject
def bgms_delete(
    body: DeleteBgmBody,
    command: BgmCommand = Depends(Provide[Container.bgm_command]),
) -> Response:
    cdto = command.delete(body.bgm_id)
    return JSONResponse(status_code=200, content=cdto.to_payload())


@router.get("/api/bgms/references")
@inject
def bgms_references(
    bgm_id: str = Query(...),
    query: BgmQuery = Depends(Provide[Container.bgm_query]),
) -> Response:
    return JSONResponse(status_code=200, content=query.get_references(bgm_id).to_payload())
