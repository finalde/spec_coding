"""Media-aggregate routes: serve / archive / unarchive / delete / hard_delete / rename."""
from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse, JSONResponse, Response
from pydantic import BaseModel

from apps.api.container import Container
from apps.api.routes._helpers import file_security_headers
from libs.application.commands.media__command import MediaCommand
from libs.application.queries.media__query import MediaQuery

router = APIRouter()


class RenameMediaBody(BaseModel):
    path: str


class ArchiveMediaBody(BaseModel):
    path: str


@router.get("/api/media")
@inject
def get_media(
    path: str = Query(...),
    query: MediaQuery = Depends(Provide[Container.media_query]),
) -> Response:
    qdto = query.serve(path)
    return FileResponse(
        str(qdto.resolved_path),
        media_type=qdto.media_type,
        headers=file_security_headers(qdto.filename),
    )


@router.post("/api/rename-media")
@inject
def rename_media(
    body: RenameMediaBody,
    command: MediaCommand = Depends(Provide[Container.media_command]),
) -> Response:
    return JSONResponse(status_code=200, content=command.rename(body.path).to_payload())


@router.post("/api/archive-media")
@inject
def archive_media(
    body: ArchiveMediaBody,
    command: MediaCommand = Depends(Provide[Container.media_command]),
) -> Response:
    return JSONResponse(status_code=200, content=command.archive(body.path).to_payload())


@router.post("/api/unarchive-media")
@inject
def unarchive_media(
    body: ArchiveMediaBody,
    command: MediaCommand = Depends(Provide[Container.media_command]),
) -> Response:
    return JSONResponse(status_code=200, content=command.unarchive(body.path).to_payload())


@router.post("/api/delete-media")
@inject
def delete_media(
    body: ArchiveMediaBody,
    command: MediaCommand = Depends(Provide[Container.media_command]),
) -> Response:
    return JSONResponse(status_code=200, content=command.delete(body.path).to_payload())


@router.post("/api/hard-delete-media")
@inject
def hard_delete_media(
    body: ArchiveMediaBody,
    command: MediaCommand = Depends(Provide[Container.media_command]),
) -> Response:
    return JSONResponse(status_code=200, content=command.hard_delete(body.path).to_payload())
