"""Downloads-aggregate routes: POST /api/import-from-downloads."""
from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

from apps.api.container import Container
from apps.api.routes._helpers import method_not_allowed
from libs.application.commands.downloads__command import DownloadsCommand
from libs.domain.errors.casting__error import DramaNotFoundError, InvalidDramaPathError
from libs.domain.errors.downloads__error import DownloadsDirMissingError

router = APIRouter()


class ImportFromDownloadsBody(BaseModel):
    path: str


@router.post("/api/import-from-downloads")
@inject
def import_from_downloads(
    body: ImportFromDownloadsBody,
    command: DownloadsCommand = Depends(Provide[Container.downloads_command]),
) -> Response:
    try:
        cdto = command.import_drama(body.path)
    except InvalidDramaPathError:
        return JSONResponse(status_code=400, content={"detail": {"kind": "invalid_drama_path"}})
    except DramaNotFoundError:
        return JSONResponse(status_code=404, content={"detail": {"kind": "not_found"}})
    except DownloadsDirMissingError as exc:
        return JSONResponse(
            status_code=500,
            content={"detail": {"kind": "downloads_dir_missing", "path": str(exc)}},
        )
    return JSONResponse(status_code=200, content=cdto.to_payload())


@router.api_route("/api/import-from-downloads", methods=["GET", "PUT", "PATCH", "DELETE"])
def import_from_downloads_method_not_allowed() -> Response:
    return method_not_allowed("POST")
