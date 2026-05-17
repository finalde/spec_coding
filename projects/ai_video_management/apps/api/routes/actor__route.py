"""Actor-aggregate routes: generate / generate-diverse / preview-prompts /
preview-diverse / list / delete / assignments."""
from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

from apps.api.container import Container
from apps.api.routes._helpers import (
    actor_assigned_409,
    map_move_failure,
    method_not_allowed,
)
from libs.application.commands.actor__command import ActorCommand
from libs.application.dtos.actor__dto import (
    GenerateActorsInputCdto,
    GenerateDiverseActorsInputCdto,
)
from libs.application.queries.actor__query import ActorQuery
from libs.domain.errors.actor__error import (
    ActorAlreadyAssignedError,
    ActorNotFoundError,
    InvalidActorAttributeError,
    InvalidActorIdError,
)

router = APIRouter()


class GenerateActorsBody(BaseModel):
    count: int
    ethnicity: str
    gender: str
    age_range: str
    look: str
    style: str
    notes: str = ""
    resolution: str = "normal"
    seeds: list[int] | None = None
    # Per follow-up 059: diverse-mode confirm path forwards the rolled
    # archetype slug per slot so each actor's sidecar carries the archetype
    # row from first write. Standard-mode UI omits this field.
    archetype: str | None = None


class GenerateDiverseActorsBody(BaseModel):
    count: int
    gender: str
    ethnicity: str
    resolution: str = "normal"


class DeleteActorBody(BaseModel):
    actor_id: str


def _generate_input(body: GenerateActorsBody) -> GenerateActorsInputCdto:
    return GenerateActorsInputCdto(
        count=body.count,
        ethnicity=body.ethnicity,
        gender=body.gender,
        age_range=body.age_range,
        look=body.look,
        style=body.style,
        notes=body.notes,
        resolution=body.resolution,
        seeds=body.seeds,
    )


def _diverse_input(body: GenerateDiverseActorsBody) -> GenerateDiverseActorsInputCdto:
    return GenerateDiverseActorsInputCdto(
        count=body.count,
        gender=body.gender,
        ethnicity=body.ethnicity,
        resolution=body.resolution,
    )


@router.post("/api/actors/generate")
@inject
def actors_generate(
    body: GenerateActorsBody,
    command: ActorCommand = Depends(Provide[Container.actor_command]),
) -> Response:
    try:
        cdto = command.generate(_generate_input(body))
    except InvalidActorAttributeError as exc:
        return JSONResponse(
            status_code=400,
            content={"detail": {"kind": "invalid_attribute", "message": str(exc)}},
        )
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={"detail": {"kind": "actors_dir_unwritable", "message": str(exc)}},
        )
    return JSONResponse(status_code=200, content=cdto.to_payload())


@router.api_route("/api/actors/generate", methods=["GET", "PUT", "PATCH", "DELETE"])
def actors_generate_method_not_allowed() -> Response:
    return method_not_allowed("POST")


@router.post("/api/actors/generate-diverse")
@inject
def actors_generate_diverse(
    body: GenerateDiverseActorsBody,
    command: ActorCommand = Depends(Provide[Container.actor_command]),
) -> Response:
    try:
        cdto = command.generate_diverse(_diverse_input(body))
    except InvalidActorAttributeError as exc:
        return JSONResponse(
            status_code=400,
            content={"detail": {"kind": "invalid_attribute", "message": str(exc)}},
        )
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={"detail": {"kind": "actors_dir_unwritable", "message": str(exc)}},
        )
    return JSONResponse(status_code=200, content=cdto.to_payload())


@router.api_route("/api/actors/generate-diverse", methods=["GET", "PUT", "PATCH", "DELETE"])
def actors_generate_diverse_method_not_allowed() -> Response:
    return method_not_allowed("POST")


@router.post("/api/actors/preview-prompts")
@inject
def actors_preview_prompts(
    body: GenerateActorsBody,
    query: ActorQuery = Depends(Provide[Container.actor_query]),
) -> Response:
    try:
        qdto = query.preview_prompts(_generate_input(body))
    except InvalidActorAttributeError as exc:
        return JSONResponse(
            status_code=400,
            content={"detail": {"kind": "invalid_attribute", "message": str(exc)}},
        )
    return JSONResponse(status_code=200, content=qdto.to_payload())


@router.api_route("/api/actors/preview-prompts", methods=["GET", "PUT", "PATCH", "DELETE"])
def actors_preview_prompts_method_not_allowed() -> Response:
    return method_not_allowed("POST")


@router.post("/api/actors/preview-diverse")
@inject
def actors_preview_diverse(
    body: GenerateDiverseActorsBody,
    query: ActorQuery = Depends(Provide[Container.actor_query]),
) -> Response:
    """Per follow-up 059: dry-run preview for the diverse-mode generator."""
    try:
        qdto = query.preview_diverse_prompts(_diverse_input(body))
    except InvalidActorAttributeError as exc:
        return JSONResponse(
            status_code=400,
            content={"detail": {"kind": "invalid_attribute", "message": str(exc)}},
        )
    return JSONResponse(status_code=200, content=qdto.to_payload())


@router.api_route("/api/actors/preview-diverse", methods=["GET", "PUT", "PATCH", "DELETE"])
def actors_preview_diverse_method_not_allowed() -> Response:
    return method_not_allowed("POST")


@router.get("/api/actors")
@inject
def actors_list(query: ActorQuery = Depends(Provide[Container.actor_query])) -> Response:
    return JSONResponse(status_code=200, content=query.list().to_payload())


@router.api_route("/api/actors", methods=["POST", "PUT", "PATCH", "DELETE"])
def actors_list_method_not_allowed() -> Response:
    return method_not_allowed("GET")


@router.post("/api/actors/delete")
@inject
def actors_delete(
    body: DeleteActorBody,
    command: ActorCommand = Depends(Provide[Container.actor_command]),
) -> Response:
    try:
        cdto = command.delete(body.actor_id)
    except InvalidActorIdError as exc:
        return JSONResponse(
            status_code=400,
            content={"detail": {"kind": "invalid_actor_id", "message": str(exc)}},
        )
    except ActorAlreadyAssignedError as exc:
        return actor_assigned_409(exc)
    except ActorNotFoundError:
        return JSONResponse(status_code=404, content={"detail": {"kind": "actor_not_found"}})
    except OSError as exc:
        return JSONResponse(
            status_code=500,
            content={"detail": {"kind": "assignments_scan_failed", "message": str(exc)}},
        )
    except Exception as exc:
        return map_move_failure(exc)
    return JSONResponse(status_code=200, content=cdto.to_payload())


@router.api_route("/api/actors/delete", methods=["GET", "PUT", "PATCH", "DELETE"])
def actors_delete_method_not_allowed() -> Response:
    return method_not_allowed("POST")


@router.get("/api/actors/assignments")
@inject
def actors_assignments(
    actor_id: str = Query(...),
    query: ActorQuery = Depends(Provide[Container.actor_query]),
) -> Response:
    try:
        qdto = query.get_assignments(actor_id)
    except InvalidActorIdError as exc:
        return JSONResponse(
            status_code=400,
            content={"detail": {"kind": "invalid_actor_id", "message": str(exc)}},
        )
    return JSONResponse(status_code=200, content=qdto.to_payload())


@router.api_route("/api/actors/assignments", methods=["POST", "PUT", "PATCH", "DELETE"])
def actors_assignments_method_not_allowed() -> Response:
    return method_not_allowed("GET")
