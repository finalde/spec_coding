"""Actor-aggregate routes: generate / generate-diverse / preview-prompts /
preview-diverse / list / delete / assignments.

All domain errors are translated to JSON by global FastAPI handlers
registered in `apps/api/app_factory.py`. Route bodies stay narrow:
shape the input, call command/query, return success.
"""
from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

from apps.api.container import Container
from libs.application.commands.actor__command import ActorCommand
from libs.application.dtos.actor__dto import (
    GenerateActorsInputCdto,
    GenerateDiverseActorsInputCdto,
)
from libs.application.queries.actor__query import ActorQuery

router = APIRouter()


class GenerateActorsBody(BaseModel):
    count: int
    ethnicity: str
    gender: str
    age_range: str
    look: str
    notes: str = ""
    resolution: str = "normal"
    seeds: list[int] | None = None
    archetype: str | None = None
    batch_seed: int | None = None
    batch_size: int | None = None
    slot_index: int | None = None
    eyes: str = ""
    nose: str = ""
    lips: str = ""
    face: str = ""
    skin: str = ""
    body: str = ""
    qi_zhi: str = ""


class GenerateDiverseActorsBody(BaseModel):
    count: int
    gender: str
    ethnicity: str
    resolution: str = "normal"


class DeleteActorBody(BaseModel):
    actor_id: str


@router.post("/api/actors/generate")
@inject
def actors_generate(
    body: GenerateActorsBody,
    command: ActorCommand = Depends(Provide[Container.actor_command]),
) -> Response:
    cdto = command.generate(GenerateActorsInputCdto(**body.model_dump()))
    return JSONResponse(status_code=200, content=cdto.to_payload())


@router.post("/api/actors/create-prompts")
@inject
def actors_create_prompts(
    body: GenerateActorsBody,
    command: ActorCommand = Depends(Provide[Container.actor_command]),
) -> Response:
    """Per follow-up 124: prompt-only mode — allocate actor folders + write
    id-tagged-prompt sidecars without any Kling call."""
    cdto = command.create_prompts(GenerateActorsInputCdto(**body.model_dump()))
    return JSONResponse(status_code=200, content=cdto.to_payload())


@router.post("/api/actors/generate-diverse")
@inject
def actors_generate_diverse(
    body: GenerateDiverseActorsBody,
    command: ActorCommand = Depends(Provide[Container.actor_command]),
) -> Response:
    cdto = command.generate_diverse(GenerateDiverseActorsInputCdto(**body.model_dump()))
    return JSONResponse(status_code=200, content=cdto.to_payload())


@router.post("/api/actors/preview-prompts")
@inject
def actors_preview_prompts(
    body: GenerateActorsBody,
    query: ActorQuery = Depends(Provide[Container.actor_query]),
) -> Response:
    qdto = query.preview_prompts(GenerateActorsInputCdto(**body.model_dump()))
    return JSONResponse(status_code=200, content=qdto.to_payload())


@router.post("/api/actors/preview-diverse")
@inject
def actors_preview_diverse(
    body: GenerateDiverseActorsBody,
    query: ActorQuery = Depends(Provide[Container.actor_query]),
) -> Response:
    """Dry-run preview for the diverse-mode generator (follow-up 059)."""
    qdto = query.preview_diverse_prompts(GenerateDiverseActorsInputCdto(**body.model_dump()))
    return JSONResponse(status_code=200, content=qdto.to_payload())


@router.get("/api/actors")
@inject
def actors_list(
    include_pending: bool = False,
    query: ActorQuery = Depends(Provide[Container.actor_query]),
) -> Response:
    # include_pending=true also returns prompt-only actors (no jpg yet) so the
    # grid can filter "仅 prompt 无图" and bulk-delete them.
    return JSONResponse(
        status_code=200, content=query.list(include_pending=include_pending).to_payload()
    )


@router.post("/api/actors/delete")
@inject
def actors_delete(
    body: DeleteActorBody,
    command: ActorCommand = Depends(Provide[Container.actor_command]),
) -> Response:
    cdto = command.delete(body.actor_id)
    return JSONResponse(status_code=200, content=cdto.to_payload())


@router.get("/api/actors/assignments")
@inject
def actors_assignments(
    actor_id: str = Query(...),
    query: ActorQuery = Depends(Provide[Container.actor_query]),
) -> Response:
    return JSONResponse(status_code=200, content=query.get_assignments(actor_id).to_payload())
