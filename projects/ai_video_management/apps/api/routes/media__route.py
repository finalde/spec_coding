"""Media-aggregate routes: serve / archive / unarchive / delete / hard_delete / rename."""
from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse, JSONResponse, Response
from pydantic import BaseModel

from apps.api.container import Container
from apps.api.routes._helpers import (
    actor_assigned_409,
    file_security_headers,
    map_move_failure,
    method_not_allowed,
)
from libs.application.commands.media__command import MediaCommand
from libs.application.queries.media__query import MediaQuery
from libs.domain.errors.actor__error import ActorAlreadyAssignedError
from libs.domain.errors.casting__error import DramaNotFoundError, InvalidDramaPathError
from libs.domain.errors.file__error import (
    FileNotInSandboxError,
    UnsupportedFileExtensionError,
)
from libs.domain.errors.media__error import (
    AlreadyArchivedError,
    AlreadyDeletedError,
    InvalidMediaPathError,
    MediaNotFoundError,
    NotInArchiveError,
    NotMediaError,
    NotUnderAiVideosError,
    NotUnderDeletedError,
)
from libs.domain.value_objects.media__valueobject import MediaPath

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
    try:
        qdto = query.serve(path)
    except UnsupportedFileExtensionError:
        return JSONResponse(status_code=400, content={"detail": {"kind": "extension_not_allowed"}})
    except FileNotInSandboxError:
        return JSONResponse(status_code=404, content={"detail": {"kind": "not_found"}})
    return FileResponse(
        str(qdto.resolved_path),
        media_type=qdto.media_type,
        headers=file_security_headers(qdto.filename),
    )


@router.api_route("/api/media", methods=["PUT", "PATCH", "DELETE", "POST"])
def media_method_not_allowed() -> Response:
    return method_not_allowed("GET")


@router.post("/api/rename-media")
@inject
def rename_media(
    body: RenameMediaBody,
    command: MediaCommand = Depends(Provide[Container.media_command]),
) -> Response:
    try:
        cdto = command.rename(body.path)
    except InvalidDramaPathError:
        return JSONResponse(status_code=400, content={"detail": {"kind": "invalid_drama_path"}})
    except DramaNotFoundError:
        return JSONResponse(status_code=404, content={"detail": {"kind": "not_found"}})
    return JSONResponse(status_code=200, content=cdto.to_payload())


@router.api_route("/api/rename-media", methods=["GET", "PUT", "PATCH", "DELETE"])
def rename_media_method_not_allowed() -> Response:
    return method_not_allowed("POST")


@router.post("/api/archive-media")
@inject
def archive_media(
    body: ArchiveMediaBody,
    command: MediaCommand = Depends(Provide[Container.media_command]),
) -> Response:
    try:
        command._refuse_if_actor_assigned(MediaPath(rel=body.path))
    except ActorAlreadyAssignedError as exc:
        return actor_assigned_409(exc)
    except (InvalidMediaPathError, NotMediaError):
        pass
    try:
        cdto = command.archive(body.path)
    except InvalidMediaPathError:
        return JSONResponse(status_code=400, content={"detail": {"kind": "invalid_path"}})
    except NotMediaError:
        return JSONResponse(status_code=400, content={"detail": {"kind": "extension_not_allowed"}})
    except AlreadyArchivedError:
        return JSONResponse(status_code=400, content={"detail": {"kind": "already_archived"}})
    except MediaNotFoundError:
        return JSONResponse(status_code=404, content={"detail": {"kind": "not_found"}})
    except Exception as exc:
        return map_move_failure(exc)
    return JSONResponse(status_code=200, content=cdto.to_payload())


@router.api_route("/api/archive-media", methods=["GET", "PUT", "PATCH", "DELETE"])
def archive_media_method_not_allowed() -> Response:
    return method_not_allowed("POST")


@router.post("/api/unarchive-media")
@inject
def unarchive_media(
    body: ArchiveMediaBody,
    command: MediaCommand = Depends(Provide[Container.media_command]),
) -> Response:
    try:
        cdto = command.unarchive(body.path)
    except InvalidMediaPathError:
        return JSONResponse(status_code=400, content={"detail": {"kind": "invalid_path"}})
    except NotMediaError:
        return JSONResponse(status_code=400, content={"detail": {"kind": "extension_not_allowed"}})
    except NotInArchiveError:
        return JSONResponse(status_code=400, content={"detail": {"kind": "not_in_archive"}})
    except MediaNotFoundError:
        return JSONResponse(status_code=404, content={"detail": {"kind": "not_found"}})
    except Exception as exc:
        return map_move_failure(exc)
    return JSONResponse(status_code=200, content=cdto.to_payload())


@router.api_route("/api/unarchive-media", methods=["GET", "PUT", "PATCH", "DELETE"])
def unarchive_media_method_not_allowed() -> Response:
    return method_not_allowed("POST")


@router.post("/api/delete-media")
@inject
def delete_media(
    body: ArchiveMediaBody,
    command: MediaCommand = Depends(Provide[Container.media_command]),
) -> Response:
    try:
        cdto = command.delete(body.path)
    except ActorAlreadyAssignedError as exc:
        return actor_assigned_409(exc)
    except InvalidMediaPathError:
        return JSONResponse(status_code=400, content={"detail": {"kind": "invalid_path"}})
    except NotMediaError:
        return JSONResponse(status_code=400, content={"detail": {"kind": "extension_not_allowed"}})
    except NotUnderAiVideosError:
        return JSONResponse(status_code=400, content={"detail": {"kind": "not_in_ai_videos"}})
    except AlreadyDeletedError:
        return JSONResponse(status_code=400, content={"detail": {"kind": "already_deleted"}})
    except MediaNotFoundError:
        return JSONResponse(status_code=404, content={"detail": {"kind": "not_found"}})
    except Exception as exc:
        return map_move_failure(exc)
    return JSONResponse(status_code=200, content=cdto.to_payload())


@router.api_route("/api/delete-media", methods=["GET", "PUT", "PATCH", "DELETE"])
def delete_media_method_not_allowed() -> Response:
    return method_not_allowed("POST")


@router.post("/api/hard-delete-media")
@inject
def hard_delete_media(
    body: ArchiveMediaBody,
    command: MediaCommand = Depends(Provide[Container.media_command]),
) -> Response:
    try:
        cdto = command.hard_delete(body.path)
    except InvalidMediaPathError:
        return JSONResponse(status_code=400, content={"detail": {"kind": "invalid_path"}})
    except NotMediaError:
        return JSONResponse(status_code=400, content={"detail": {"kind": "extension_not_allowed"}})
    except NotUnderDeletedError:
        return JSONResponse(status_code=400, content={"detail": {"kind": "not_in_deleted"}})
    except MediaNotFoundError:
        return JSONResponse(status_code=404, content={"detail": {"kind": "not_found"}})
    except Exception as exc:
        return JSONResponse(
            status_code=500, content={"detail": {"kind": "delete_failed", "message": str(exc)}}
        )
    return JSONResponse(status_code=200, content=cdto.to_payload())


@router.api_route("/api/hard-delete-media", methods=["GET", "PUT", "PATCH", "DELETE"])
def hard_delete_media_method_not_allowed() -> Response:
    return method_not_allowed("POST")
