"""File-aggregate routes: GET /api/file, PUT /api/file."""
from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Header, Query
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

from apps.api.container import Container
from apps.api.routes._helpers import file_security_headers, method_not_allowed
from libs.application.commands.file__command import FileCommand
from libs.application.dtos.file__dto import WriteFileInputCdto
from libs.application.queries.file__query import FileQuery
from libs.domain.errors.file__error import (
    FileNotInSandboxError,
    FileTooLargeError,
    InvalidBodyEncodingError,
    MissingIfUnmodifiedSinceError,
    StaleWriteError,
    UnsupportedFileExtensionError,
)

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
    try:
        qdto = query.read(path)
    except UnsupportedFileExtensionError:
        return JSONResponse(status_code=400, content={"detail": {"kind": "extension_not_allowed"}})
    except FileTooLargeError:
        return JSONResponse(status_code=413, content={"detail": {"kind": "too_large"}})
    except FileNotInSandboxError:
        return JSONResponse(status_code=404, content={"detail": {"kind": "not_found"}})
    headers = file_security_headers(qdto.rel_path.split("/")[-1])
    return JSONResponse(status_code=200, content=qdto.to_payload(), headers=headers)


@router.put("/api/file")
@inject
def put_file(
    body: FilePutBody,
    if_unmodified_since: str | None = Header(default=None, alias="If-Unmodified-Since"),
    command: FileCommand = Depends(Provide[Container.file_command]),
) -> Response:
    input_cdto = WriteFileInputCdto(
        rel_path=body.path, content=body.content, if_unmodified_since=if_unmodified_since,
    )
    try:
        cdto = command.write(input_cdto)
    except MissingIfUnmodifiedSinceError:
        return JSONResponse(status_code=400, content={"detail": {"kind": "missing_if_unmodified_since"}})
    except UnsupportedFileExtensionError:
        return JSONResponse(status_code=400, content={"detail": {"kind": "extension_not_allowed"}})
    except FileTooLargeError:
        return JSONResponse(status_code=413, content={"detail": {"kind": "too_large"}})
    except InvalidBodyEncodingError:
        return JSONResponse(status_code=400, content={"detail": {"kind": "invalid_body_encoding"}})
    except StaleWriteError as exc:
        return JSONResponse(
            status_code=409,
            content={"detail": {"kind": "stale_write", "current_mtime": exc.current_mtime}},
        )
    except FileNotInSandboxError:
        return JSONResponse(status_code=404, content={"detail": {"kind": "not_found"}})
    return JSONResponse(status_code=200, content=cdto.to_payload())


@router.api_route("/api/file", methods=["PATCH", "DELETE", "POST"])
def file_method_not_allowed() -> Response:
    return method_not_allowed("GET, PUT")
