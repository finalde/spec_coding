"""Casting-aggregate routes: read / assign / unassign."""
from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

from apps.api.container import Container
from libs.application.commands.casting__command import CastingCommand
from libs.application.dtos.casting__dto import AssignActorInputCdto, UnassignActorInputCdto
from libs.application.queries.casting__query import CastingQuery

router = APIRouter()


class CastingAssignBody(BaseModel):
    path: str
    role: str
    actor_id: str
    notes: str = ""


class CastingUnassignBody(BaseModel):
    path: str
    role: str


@router.get("/api/casting")
@inject
def casting_read(
    path: str = Query(...),
    query: CastingQuery = Depends(Provide[Container.casting_query]),
) -> Response:
    return JSONResponse(status_code=200, content=query.read(path).to_payload())


@router.post("/api/casting/assign")
@inject
def casting_assign(
    body: CastingAssignBody,
    command: CastingCommand = Depends(Provide[Container.casting_command]),
) -> Response:
    qdto = command.assign(
        AssignActorInputCdto(
            rel_drama_path=body.path, role=body.role, actor_id=body.actor_id, notes=body.notes,
        )
    )
    return JSONResponse(status_code=200, content=qdto.to_payload())


@router.delete("/api/casting/assign")
@inject
def casting_unassign(
    body: CastingUnassignBody,
    command: CastingCommand = Depends(Provide[Container.casting_command]),
) -> Response:
    qdto = command.unassign(UnassignActorInputCdto(rel_drama_path=body.path, role=body.role))
    return JSONResponse(status_code=200, content=qdto.to_payload())
