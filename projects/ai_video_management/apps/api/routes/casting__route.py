"""Casting-aggregate routes: read / assign / unassign."""
from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

from apps.api.container import Container
from apps.api.routes._helpers import method_not_allowed
from libs.application.commands.casting__command import CastingCommand
from libs.application.dtos.casting__dto import AssignActorInputCdto, UnassignActorInputCdto
from libs.application.queries.casting__query import CastingQuery
from libs.domain.errors.actor__error import InvalidActorIdError
from libs.domain.errors.casting__error import (
    DramaNotFoundError,
    InvalidDramaPathError,
    InvalidRoleError,
)

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
    try:
        qdto = query.read(path)
    except InvalidDramaPathError:
        return JSONResponse(status_code=400, content={"detail": {"kind": "invalid_drama_path"}})
    except DramaNotFoundError:
        return JSONResponse(status_code=404, content={"detail": {"kind": "not_found"}})
    return JSONResponse(status_code=200, content=qdto.to_payload())


@router.post("/api/casting/assign")
@inject
def casting_assign(
    body: CastingAssignBody,
    command: CastingCommand = Depends(Provide[Container.casting_command]),
) -> Response:
    input_cdto = AssignActorInputCdto(
        rel_drama_path=body.path, role=body.role, actor_id=body.actor_id, notes=body.notes,
    )
    try:
        qdto = command.assign(input_cdto)
    except InvalidDramaPathError:
        return JSONResponse(status_code=400, content={"detail": {"kind": "invalid_drama_path"}})
    except InvalidRoleError as exc:
        return JSONResponse(
            status_code=400, content={"detail": {"kind": "invalid_role", "message": str(exc)}}
        )
    except InvalidActorIdError as exc:
        return JSONResponse(
            status_code=400,
            content={"detail": {"kind": "invalid_actor_id", "message": str(exc)}},
        )
    except DramaNotFoundError:
        return JSONResponse(status_code=404, content={"detail": {"kind": "not_found"}})
    return JSONResponse(status_code=200, content=qdto.to_payload())


@router.delete("/api/casting/assign")
@inject
def casting_unassign(
    body: CastingUnassignBody,
    command: CastingCommand = Depends(Provide[Container.casting_command]),
) -> Response:
    input_cdto = UnassignActorInputCdto(rel_drama_path=body.path, role=body.role)
    try:
        qdto = command.unassign(input_cdto)
    except InvalidDramaPathError:
        return JSONResponse(status_code=400, content={"detail": {"kind": "invalid_drama_path"}})
    except InvalidRoleError as exc:
        return JSONResponse(
            status_code=400, content={"detail": {"kind": "invalid_role", "message": str(exc)}}
        )
    except DramaNotFoundError:
        return JSONResponse(status_code=404, content={"detail": {"kind": "not_found"}})
    return JSONResponse(status_code=200, content=qdto.to_payload())


@router.api_route("/api/casting/assign", methods=["GET", "PUT", "PATCH"])
def casting_assign_method_not_allowed() -> Response:
    return method_not_allowed("POST, DELETE")


@router.api_route("/api/casting", methods=["POST", "PUT", "PATCH", "DELETE"])
def casting_read_method_not_allowed() -> Response:
    return method_not_allowed("GET")
