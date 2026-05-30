"""File-aggregate routes: GET /api/file, PUT /api/file."""
from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Header, Query
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

from apps.api.container import Container
from apps.api.routes._helpers import file_security_headers
from libs.application.commands.file__command import FileCommand
from libs.application.dtos.file__dto import WriteFileInputCdto
from libs.application.queries.file__query import FileQuery

router = APIRouter()


class FilePutBody(BaseModel):
    path: str
    content: str


@router.get("/api/file")
@inject
def get_file(
    path: str = Query(...),
    query: FileQuery = Depends(Provide[Container.file_query]),
) -> Response:
    qdto = query.read(path)
    headers = file_security_headers(qdto.rel_path.split("/")[-1])
    return JSONResponse(status_code=200, content=qdto.to_payload(), headers=headers)


@router.put("/api/file")
@inject
def put_file(
    body: FilePutBody,
    if_unmodified_since: str | None = Header(default=None, alias="If-Unmodified-Since"),
    command: FileCommand = Depends(Provide[Container.file_command]),
) -> Response:
    cdto = command.write(
        WriteFileInputCdto(
            rel_path=body.path,
            content=body.content,
            if_unmodified_since=if_unmodified_since,
        )
    )
    return JSONResponse(status_code=200, content=cdto.to_payload())
