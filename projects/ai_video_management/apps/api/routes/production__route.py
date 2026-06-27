"""Production-aggregate route: POST /api/export-production."""
from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

from apps.api.container import Container
from libs.application.commands.production__command import ProductionCommand

router = APIRouter()


class ExportProductionBody(BaseModel):
    path: str


@router.post("/api/export-production")
@inject
def export_production(
    body: ExportProductionBody,
    command: ProductionCommand = Depends(Provide[Container.production_command]),
) -> Response:
    return JSONResponse(
        status_code=200, content=command.export(body.path).to_payload()
    )
