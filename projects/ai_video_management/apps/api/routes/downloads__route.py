"""Downloads-aggregate routes: POST /api/import-from-downloads."""
from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

from apps.api.container import Container
from libs.application.commands.downloads__command import DownloadsCommand

router = APIRouter()


class ImportFromDownloadsBody(BaseModel):
    path: str


@router.post("/api/import-from-downloads")
@inject
def import_from_downloads(
    body: ImportFromDownloadsBody,
    command: DownloadsCommand = Depends(Provide[Container.downloads_command]),
) -> Response:
    return JSONResponse(status_code=200, content=command.import_drama(body.path).to_payload())
