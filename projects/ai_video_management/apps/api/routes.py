"""FastAPI route surface for ai_video_management — module-level @inject handlers.

18 endpoints, per follow-up 039 layout: apps/api/routes.py is the transport
layer; route bodies are 1–2 lines that call into application/infrastructure
services injected via dependency_injector.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, FastAPI, Header, Query
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from apps.api.container import Container
from libs.common.exposed_tree import MEDIA_EXTENSIONS, ExposedTree
from libs.common.safe_resolve import SafeResolver
from libs.infrastructure import file__reader as fr
from libs.infrastructure import file__writer as fw
from libs.infrastructure.actor_pool__writer import (
    ActorAttrs,
    ActorDeleteFailed,
    ActorDeleteTargetExists,
    ActorNotFound,
    ActorPool,
    GenerationDirMissing,
    InvalidAttribute,
)
from libs.infrastructure.casting__writer import Casting, InvalidActorId, InvalidRole
from libs.infrastructure.downloads__importer import DownloadsDirMissing, DownloadsImporter
from libs.infrastructure.file__reader import FileReader
from libs.infrastructure.file__writer import FileWriter
from libs.infrastructure.frame__extractor import (
    ExtractFailed,
    FfmpegMissing,
    FrameExtractor,
    InvalidPath as FrameInvalidPath,
    NotFound as FrameNotFound,
    NotVideo,
)
from libs.infrastructure.media__archiver import (
    AlreadyArchived,
    AlreadyDeleted,
    InvalidPath as ArchiveInvalidPath,
    MediaArchiver,
    MoveFailed,
    NotFound as ArchiveNotFound,
    NotInAiVideos,
    NotInArchive,
    NotInDeleted,
    NotMedia,
    TargetExists,
)
from libs.infrastructure.media__renamer import DramaNotFound, InvalidDramaPath, MediaRenamer
from libs.infrastructure.origin_host__middleware import (
    OriginHostMiddleware,
    SecurityHeadersMiddleware,
)
from libs.infrastructure.tree__reader import TreeReader

_MEDIA_MIME_MAP: dict[str, str] = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".gif": "image/gif",
    ".bmp": "image/bmp",
    ".mp4": "video/mp4",
    ".mov": "video/quicktime",
    ".webm": "video/webm",
    ".mkv": "video/x-matroska",
    ".avi": "video/x-msvideo",
    ".m4v": "video/mp4",
}


class FilePutBody(BaseModel):
    path: str
    content: str


class RenameMediaBody(BaseModel):
    path: str


class ArchiveMediaBody(BaseModel):
    path: str


class ExtractFramesBody(BaseModel):
    path: str


class ImportFromDownloadsBody(BaseModel):
    path: str


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


class CastingAssignBody(BaseModel):
    path: str
    role: str
    actor_id: str
    notes: str = ""


class CastingUnassignBody(BaseModel):
    path: str
    role: str


class DeleteActorBody(BaseModel):
    actor_id: str


router = APIRouter()


def _refuse_if_actor_assigned(casting: Casting, path: str) -> Response | None:
    if not isinstance(path, str):
        return None
    parts = path.split("/")
    if len(parts) < 3 or parts[0] != "ai_videos" or parts[1] != "_actors":
        return None
    actor_id = parts[2]
    try:
        assignments = casting.find_assignments_for_actor(actor_id)
    except (InvalidActorId, OSError):
        return None
    if not assignments:
        return None
    return JSONResponse(
        status_code=409,
        content={
            "detail": {
                "kind": "actor_is_assigned",
                "actor_id": actor_id,
                "assignments": assignments,
            }
        },
    )


@router.get("/api/tree")
@inject
def get_tree(reader: TreeReader = Depends(Provide[Container.tree_reader])) -> dict[str, Any]:
    return reader.build()


@router.get("/api/file")
@inject
def get_file(
    path: str = Query(...),
    reader: FileReader = Depends(Provide[Container.file_reader]),
) -> Response:
    try:
        result = reader.read(path)
    except fr.UnsupportedExtension:
        return JSONResponse(status_code=400, content={"detail": {"kind": "extension_not_allowed"}})
    except fr.FileTooLarge:
        return JSONResponse(status_code=413, content={"detail": {"kind": "too_large"}})
    except fr.OutsideSandbox:
        return JSONResponse(status_code=404, content={"detail": {"kind": "not_found"}})
    headers = FileReader.security_headers(Path(result.rel_path).name)
    return JSONResponse(status_code=200, content=result.to_payload(), headers=headers)


@router.put("/api/file")
@inject
def put_file(
    body: FilePutBody,
    if_unmodified_since: str | None = Header(default=None, alias="If-Unmodified-Since"),
    writer: FileWriter = Depends(Provide[Container.file_writer]),
) -> Response:
    try:
        result = writer.write(body.path, body.content, if_unmodified_since)
    except fw.MissingIfUnmodifiedSince:
        return JSONResponse(status_code=400, content={"detail": {"kind": "missing_if_unmodified_since"}})
    except fw.UnsupportedExtension:
        return JSONResponse(status_code=400, content={"detail": {"kind": "extension_not_allowed"}})
    except fw.FileTooLarge:
        return JSONResponse(status_code=413, content={"detail": {"kind": "too_large"}})
    except fw.InvalidBodyEncoding:
        return JSONResponse(status_code=400, content={"detail": {"kind": "invalid_body_encoding"}})
    except fw.StaleWrite as sw:
        return JSONResponse(
            status_code=409,
            content={"detail": {"kind": "stale_write", "current_mtime": sw.current_mtime}},
        )
    except fw.OutsideSandbox:
        return JSONResponse(status_code=404, content={"detail": {"kind": "not_found"}})
    return JSONResponse(status_code=200, content=result.to_payload())


@router.api_route("/api/file", methods=["PATCH", "DELETE", "POST"])
def file_method_not_allowed() -> Response:
    return JSONResponse(
        status_code=405,
        content={"detail": {"kind": "method_not_allowed"}},
        headers={"Allow": "GET, PUT"},
    )


@router.get("/api/media")
@inject
def get_media(
    path: str = Query(...),
    exposed: ExposedTree = Depends(Provide[Container.exposed_tree]),
    resolver: SafeResolver = Depends(Provide[Container.safe_resolver]),
) -> Response:
    ext = Path(path).suffix.lower() if isinstance(path, str) else ""
    if ext not in MEDIA_EXTENSIONS:
        return JSONResponse(status_code=400, content={"detail": {"kind": "extension_not_allowed"}})
    if not exposed.is_inside(path):
        return JSONResponse(status_code=404, content={"detail": {"kind": "not_found"}})
    resolved = resolver.resolve(path)
    if resolved is None or not resolved.is_file():
        return JSONResponse(status_code=404, content={"detail": {"kind": "not_found"}})
    media_type = _MEDIA_MIME_MAP.get(ext, "application/octet-stream")
    return FileResponse(
        str(resolved),
        media_type=media_type,
        headers=FileReader.security_headers(resolved.name),
    )


@router.api_route("/api/media", methods=["PUT", "PATCH", "DELETE", "POST"])
def media_method_not_allowed() -> Response:
    return JSONResponse(
        status_code=405,
        content={"detail": {"kind": "method_not_allowed"}},
        headers={"Allow": "GET"},
    )


@router.post("/api/rename-media")
@inject
def rename_media(
    body: RenameMediaBody,
    renamer: MediaRenamer = Depends(Provide[Container.media_renamer]),
) -> Response:
    try:
        result = renamer.rename_drama(body.path, excluded_folder_names=frozenset({"frames"}))
    except InvalidDramaPath:
        return JSONResponse(status_code=400, content={"detail": {"kind": "invalid_drama_path"}})
    except DramaNotFound:
        return JSONResponse(status_code=404, content={"detail": {"kind": "not_found"}})
    return JSONResponse(status_code=200, content=result.to_payload())


@router.api_route("/api/rename-media", methods=["GET", "PUT", "PATCH", "DELETE"])
def rename_media_method_not_allowed() -> Response:
    return JSONResponse(
        status_code=405,
        content={"detail": {"kind": "method_not_allowed"}},
        headers={"Allow": "POST"},
    )


@router.post("/api/archive-media")
@inject
def archive_media(
    body: ArchiveMediaBody,
    archiver: MediaArchiver = Depends(Provide[Container.media_archiver]),
    casting: Casting = Depends(Provide[Container.casting]),
) -> Response:
    blocked = _refuse_if_actor_assigned(casting, body.path)
    if blocked is not None:
        return blocked
    try:
        result = archiver.archive(body.path)
    except ArchiveInvalidPath:
        return JSONResponse(status_code=400, content={"detail": {"kind": "invalid_path"}})
    except NotMedia:
        return JSONResponse(status_code=400, content={"detail": {"kind": "extension_not_allowed"}})
    except AlreadyArchived:
        return JSONResponse(status_code=400, content={"detail": {"kind": "already_archived"}})
    except ArchiveNotFound:
        return JSONResponse(status_code=404, content={"detail": {"kind": "not_found"}})
    except TargetExists as exc:
        return JSONResponse(
            status_code=409, content={"detail": {"kind": "target_exists", "target": str(exc)}}
        )
    except MoveFailed as exc:
        return JSONResponse(
            status_code=500, content={"detail": {"kind": "move_failed", "message": str(exc)}}
        )
    return JSONResponse(status_code=200, content=result.to_payload())


@router.api_route("/api/archive-media", methods=["GET", "PUT", "PATCH", "DELETE"])
def archive_media_method_not_allowed() -> Response:
    return JSONResponse(
        status_code=405,
        content={"detail": {"kind": "method_not_allowed"}},
        headers={"Allow": "POST"},
    )


@router.post("/api/unarchive-media")
@inject
def unarchive_media(
    body: ArchiveMediaBody,
    archiver: MediaArchiver = Depends(Provide[Container.media_archiver]),
) -> Response:
    try:
        result = archiver.unarchive(body.path)
    except ArchiveInvalidPath:
        return JSONResponse(status_code=400, content={"detail": {"kind": "invalid_path"}})
    except NotMedia:
        return JSONResponse(status_code=400, content={"detail": {"kind": "extension_not_allowed"}})
    except NotInArchive:
        return JSONResponse(status_code=400, content={"detail": {"kind": "not_in_archive"}})
    except ArchiveNotFound:
        return JSONResponse(status_code=404, content={"detail": {"kind": "not_found"}})
    except TargetExists as exc:
        return JSONResponse(
            status_code=409, content={"detail": {"kind": "target_exists", "target": str(exc)}}
        )
    except MoveFailed as exc:
        return JSONResponse(
            status_code=500, content={"detail": {"kind": "move_failed", "message": str(exc)}}
        )
    return JSONResponse(status_code=200, content=result.to_payload())


@router.api_route("/api/unarchive-media", methods=["GET", "PUT", "PATCH", "DELETE"])
def unarchive_media_method_not_allowed() -> Response:
    return JSONResponse(
        status_code=405,
        content={"detail": {"kind": "method_not_allowed"}},
        headers={"Allow": "POST"},
    )


@router.post("/api/extract-frames")
@inject
def extract_frames(
    body: ExtractFramesBody,
    extractor: FrameExtractor = Depends(Provide[Container.frame_extractor]),
) -> Response:
    try:
        result = extractor.extract(body.path)
    except FrameInvalidPath:
        return JSONResponse(status_code=400, content={"detail": {"kind": "invalid_path"}})
    except NotVideo:
        return JSONResponse(status_code=400, content={"detail": {"kind": "not_a_video"}})
    except FrameNotFound:
        return JSONResponse(status_code=404, content={"detail": {"kind": "not_found"}})
    except FfmpegMissing as exc:
        return JSONResponse(
            status_code=500, content={"detail": {"kind": "ffmpeg_missing", "message": str(exc)}}
        )
    except ExtractFailed as exc:
        return JSONResponse(
            status_code=500, content={"detail": {"kind": "extract_failed", "message": str(exc)}}
        )
    return JSONResponse(status_code=200, content=result.to_payload())


@router.api_route("/api/extract-frames", methods=["GET", "PUT", "PATCH", "DELETE"])
def extract_frames_method_not_allowed() -> Response:
    return JSONResponse(
        status_code=405,
        content={"detail": {"kind": "method_not_allowed"}},
        headers={"Allow": "POST"},
    )


@router.post("/api/delete-media")
@inject
def delete_media(
    body: ArchiveMediaBody,
    archiver: MediaArchiver = Depends(Provide[Container.media_archiver]),
    casting: Casting = Depends(Provide[Container.casting]),
) -> Response:
    blocked = _refuse_if_actor_assigned(casting, body.path)
    if blocked is not None:
        return blocked
    try:
        result = archiver.delete(body.path)
    except ArchiveInvalidPath:
        return JSONResponse(status_code=400, content={"detail": {"kind": "invalid_path"}})
    except NotMedia:
        return JSONResponse(status_code=400, content={"detail": {"kind": "extension_not_allowed"}})
    except NotInAiVideos:
        return JSONResponse(status_code=400, content={"detail": {"kind": "not_in_ai_videos"}})
    except AlreadyDeleted:
        return JSONResponse(status_code=400, content={"detail": {"kind": "already_deleted"}})
    except ArchiveNotFound:
        return JSONResponse(status_code=404, content={"detail": {"kind": "not_found"}})
    except TargetExists as exc:
        return JSONResponse(
            status_code=409, content={"detail": {"kind": "target_exists", "target": str(exc)}}
        )
    except MoveFailed as exc:
        return JSONResponse(
            status_code=500, content={"detail": {"kind": "move_failed", "message": str(exc)}}
        )
    return JSONResponse(status_code=200, content=result.to_payload())


@router.api_route("/api/delete-media", methods=["GET", "PUT", "PATCH", "DELETE"])
def delete_media_method_not_allowed() -> Response:
    return JSONResponse(
        status_code=405,
        content={"detail": {"kind": "method_not_allowed"}},
        headers={"Allow": "POST"},
    )


@router.post("/api/hard-delete-media")
@inject
def hard_delete_media(
    body: ArchiveMediaBody,
    archiver: MediaArchiver = Depends(Provide[Container.media_archiver]),
) -> Response:
    try:
        deleted_rel = archiver.hard_delete(body.path)
    except ArchiveInvalidPath:
        return JSONResponse(status_code=400, content={"detail": {"kind": "invalid_path"}})
    except NotMedia:
        return JSONResponse(status_code=400, content={"detail": {"kind": "extension_not_allowed"}})
    except NotInDeleted:
        return JSONResponse(status_code=400, content={"detail": {"kind": "not_in_deleted"}})
    except ArchiveNotFound:
        return JSONResponse(status_code=404, content={"detail": {"kind": "not_found"}})
    except MoveFailed as exc:
        return JSONResponse(
            status_code=500, content={"detail": {"kind": "delete_failed", "message": str(exc)}}
        )
    return JSONResponse(status_code=200, content={"deleted": deleted_rel})


@router.api_route("/api/hard-delete-media", methods=["GET", "PUT", "PATCH", "DELETE"])
def hard_delete_media_method_not_allowed() -> Response:
    return JSONResponse(
        status_code=405,
        content={"detail": {"kind": "method_not_allowed"}},
        headers={"Allow": "POST"},
    )


@router.post("/api/import-from-downloads")
@inject
def import_from_downloads(
    body: ImportFromDownloadsBody,
    importer: DownloadsImporter = Depends(Provide[Container.downloads_importer]),
) -> Response:
    try:
        result = importer.import_drama(body.path)
    except InvalidDramaPath:
        return JSONResponse(status_code=400, content={"detail": {"kind": "invalid_drama_path"}})
    except DramaNotFound:
        return JSONResponse(status_code=404, content={"detail": {"kind": "not_found"}})
    except DownloadsDirMissing as exc:
        return JSONResponse(
            status_code=500,
            content={"detail": {"kind": "downloads_dir_missing", "path": str(exc)}},
        )
    return JSONResponse(status_code=200, content=result.to_payload())


@router.api_route("/api/import-from-downloads", methods=["GET", "PUT", "PATCH", "DELETE"])
def import_from_downloads_method_not_allowed() -> Response:
    return JSONResponse(
        status_code=405,
        content={"detail": {"kind": "method_not_allowed"}},
        headers={"Allow": "POST"},
    )


@router.post("/api/actors/generate")
@inject
def actors_generate(
    body: GenerateActorsBody,
    pool: ActorPool = Depends(Provide[Container.actor_pool]),
) -> Response:
    try:
        attrs = ActorAttrs(
            ethnicity=body.ethnicity,
            gender=body.gender,
            age_range=body.age_range,
            look=body.look,
            style=body.style,
            notes=body.notes,
        )
        result = pool.generate_batch(attrs, body.count, body.resolution, body.seeds)
    except InvalidAttribute as exc:
        return JSONResponse(
            status_code=400,
            content={"detail": {"kind": "invalid_attribute", "message": str(exc)}},
        )
    except GenerationDirMissing as exc:
        return JSONResponse(
            status_code=500,
            content={"detail": {"kind": "actors_dir_unwritable", "message": str(exc)}},
        )
    return JSONResponse(status_code=200, content=result.to_payload())


@router.api_route("/api/actors/generate", methods=["GET", "PUT", "PATCH", "DELETE"])
def actors_generate_method_not_allowed() -> Response:
    return JSONResponse(
        status_code=405,
        content={"detail": {"kind": "method_not_allowed"}},
        headers={"Allow": "POST"},
    )


@router.post("/api/actors/preview-prompts")
@inject
def actors_preview_prompts(
    body: GenerateActorsBody,
    pool: ActorPool = Depends(Provide[Container.actor_pool]),
) -> Response:
    try:
        attrs = ActorAttrs(
            ethnicity=body.ethnicity,
            gender=body.gender,
            age_range=body.age_range,
            look=body.look,
            style=body.style,
            notes=body.notes,
        )
        result = pool.preview_prompts(attrs, body.count, body.resolution)
    except InvalidAttribute as exc:
        return JSONResponse(
            status_code=400,
            content={"detail": {"kind": "invalid_attribute", "message": str(exc)}},
        )
    return JSONResponse(status_code=200, content=result)


@router.api_route("/api/actors/preview-prompts", methods=["GET", "PUT", "PATCH", "DELETE"])
def actors_preview_prompts_method_not_allowed() -> Response:
    return JSONResponse(
        status_code=405,
        content={"detail": {"kind": "method_not_allowed"}},
        headers={"Allow": "POST"},
    )


@router.get("/api/actors")
@inject
def actors_list(pool: ActorPool = Depends(Provide[Container.actor_pool])) -> Response:
    actors = [a.to_dict() for a in pool.list_actors()]
    return JSONResponse(status_code=200, content={"actors": actors})


@router.api_route("/api/actors", methods=["POST", "PUT", "PATCH", "DELETE"])
def actors_list_method_not_allowed() -> Response:
    return JSONResponse(
        status_code=405,
        content={"detail": {"kind": "method_not_allowed"}},
        headers={"Allow": "GET"},
    )


@router.post("/api/actors/delete")
@inject
def actors_delete(
    body: DeleteActorBody,
    pool: ActorPool = Depends(Provide[Container.actor_pool]),
    casting: Casting = Depends(Provide[Container.casting]),
) -> Response:
    try:
        assignments = casting.find_assignments_for_actor(body.actor_id)
    except InvalidActorId as exc:
        return JSONResponse(
            status_code=400,
            content={"detail": {"kind": "invalid_actor_id", "message": str(exc)}},
        )
    except OSError as exc:
        return JSONResponse(
            status_code=500,
            content={"detail": {"kind": "assignments_scan_failed", "message": str(exc)}},
        )
    if assignments:
        return JSONResponse(
            status_code=409,
            content={"detail": {"kind": "actor_is_assigned", "assignments": assignments}},
        )
    try:
        move = pool.delete_actor(body.actor_id)
    except InvalidAttribute as exc:
        return JSONResponse(
            status_code=400,
            content={"detail": {"kind": "invalid_actor_id", "message": str(exc)}},
        )
    except ActorNotFound:
        return JSONResponse(status_code=404, content={"detail": {"kind": "actor_not_found"}})
    except ActorDeleteTargetExists as exc:
        return JSONResponse(
            status_code=409, content={"detail": {"kind": "target_exists", "target": str(exc)}}
        )
    except ActorDeleteFailed as exc:
        return JSONResponse(
            status_code=500, content={"detail": {"kind": "move_failed", "message": str(exc)}}
        )
    return JSONResponse(
        status_code=200,
        content={"from": move["from"], "to": move["to"], "unassigned": []},
    )


@router.get("/api/actors/assignments")
@inject
def actors_assignments(
    actor_id: str = Query(...),
    casting: Casting = Depends(Provide[Container.casting]),
) -> Response:
    try:
        assignments = casting.find_assignments_for_actor(actor_id)
    except InvalidActorId as exc:
        return JSONResponse(
            status_code=400,
            content={"detail": {"kind": "invalid_actor_id", "message": str(exc)}},
        )
    return JSONResponse(
        status_code=200,
        content={"actor_id": actor_id, "assignments": assignments},
    )


@router.api_route("/api/actors/assignments", methods=["POST", "PUT", "PATCH", "DELETE"])
def actors_assignments_method_not_allowed() -> Response:
    return JSONResponse(
        status_code=405,
        content={"detail": {"kind": "method_not_allowed"}},
        headers={"Allow": "GET"},
    )


@router.api_route("/api/actors/delete", methods=["GET", "PUT", "PATCH", "DELETE"])
def actors_delete_method_not_allowed() -> Response:
    return JSONResponse(
        status_code=405,
        content={"detail": {"kind": "method_not_allowed"}},
        headers={"Allow": "POST"},
    )


@router.get("/api/casting")
@inject
def casting_read(
    path: str = Query(...),
    casting: Casting = Depends(Provide[Container.casting]),
) -> Response:
    try:
        result = casting.read(path)
    except InvalidDramaPath:
        return JSONResponse(status_code=400, content={"detail": {"kind": "invalid_drama_path"}})
    except DramaNotFound:
        return JSONResponse(status_code=404, content={"detail": {"kind": "not_found"}})
    return JSONResponse(status_code=200, content=result.to_payload())


@router.post("/api/casting/assign")
@inject
def casting_assign(
    body: CastingAssignBody,
    casting: Casting = Depends(Provide[Container.casting]),
) -> Response:
    try:
        result = casting.assign(body.path, body.role, body.actor_id, body.notes)
    except InvalidDramaPath:
        return JSONResponse(status_code=400, content={"detail": {"kind": "invalid_drama_path"}})
    except InvalidRole as exc:
        return JSONResponse(
            status_code=400, content={"detail": {"kind": "invalid_role", "message": str(exc)}}
        )
    except InvalidActorId as exc:
        return JSONResponse(
            status_code=400,
            content={"detail": {"kind": "invalid_actor_id", "message": str(exc)}},
        )
    except DramaNotFound:
        return JSONResponse(status_code=404, content={"detail": {"kind": "not_found"}})
    return JSONResponse(status_code=200, content=result.to_payload())


@router.delete("/api/casting/assign")
@inject
def casting_unassign(
    body: CastingUnassignBody,
    casting: Casting = Depends(Provide[Container.casting]),
) -> Response:
    try:
        result = casting.unassign(body.path, body.role)
    except InvalidDramaPath:
        return JSONResponse(status_code=400, content={"detail": {"kind": "invalid_drama_path"}})
    except InvalidRole as exc:
        return JSONResponse(
            status_code=400, content={"detail": {"kind": "invalid_role", "message": str(exc)}}
        )
    except DramaNotFound:
        return JSONResponse(status_code=404, content={"detail": {"kind": "not_found"}})
    return JSONResponse(status_code=200, content=result.to_payload())


@router.api_route("/api/casting/assign", methods=["GET", "PUT", "PATCH"])
def casting_assign_method_not_allowed() -> Response:
    return JSONResponse(
        status_code=405,
        content={"detail": {"kind": "method_not_allowed"}},
        headers={"Allow": "POST, DELETE"},
    )


@router.api_route("/api/casting", methods=["POST", "PUT", "PATCH", "DELETE"])
def casting_read_method_not_allowed() -> Response:
    return JSONResponse(
        status_code=405,
        content={"detail": {"kind": "method_not_allowed"}},
        headers={"Allow": "GET"},
    )


def create_app(container: "Container", serve_static: bool = True) -> FastAPI:
    app = FastAPI(title="ai_video_management", openapi_url=None, docs_url=None, redoc_url=None)

    # Eager-create the actor pool folder (follow-up 015).
    try:
        container.actor_pool().actors_dir().mkdir(parents=True, exist_ok=True)
    except OSError:
        pass

    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(OriginHostMiddleware, bound=container.bound_origin())
    app.include_router(router)

    if serve_static:
        static_dir = Path(__file__).resolve().parent / "static"
        if static_dir.is_dir():
            app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")

    return app
