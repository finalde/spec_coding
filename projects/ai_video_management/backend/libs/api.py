"""API surface for ai_video_management.

16 endpoints: `GET /api/tree`, `GET /api/file`, `PUT /api/file`,
`GET /api/media`, `POST /api/rename-media`, `POST /api/archive-media`,
`POST /api/unarchive-media`, `POST /api/delete-media`,
`POST /api/import-from-downloads`,
`POST /api/actors/generate`, `POST /api/actors/preview-prompts`,
`GET /api/actors`, `POST /api/actors/delete`,
`POST /api/casting/assign`, `DELETE /api/casting/assign`, `GET /api/casting`.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, Header, Query
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from libs import file_reader as fr
from libs import file_writer as fw
from libs.actor_pool import (
    ActorAttrs,
    ActorDeleteFailed,
    ActorDeleteTargetExists,
    ActorNotFound,
    ActorPool,
    GenerationDirMissing,
    InvalidAttribute,
)
from libs.api_security import BoundOrigin, OriginHostMiddleware, SecurityHeadersMiddleware
from libs.casting import Casting, InvalidActorId, InvalidRole
from libs.exposed_tree import MEDIA_EXTENSIONS, ExposedTree
from libs.file_reader import FileReader
from libs.file_writer import FileWriter
from libs.downloads_importer import DownloadsDirMissing, DownloadsImporter
from libs.media_archiver import (
    AlreadyArchived,
    AlreadyDeleted,
    InvalidPath as ArchiveInvalidPath,
    MediaArchiver,
    MoveFailed,
    NotFound as ArchiveNotFound,
    NotInAiVideos,
    NotInArchive,
    NotMedia,
    TargetExists,
)
from libs.media_renamer import DramaNotFound, InvalidDramaPath, MediaRenamer
from libs.repo_root import RepoRoot
from libs.safe_resolve import SafeResolver
from libs.tree_walker import TreeWalker

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


def create_app(
    repo_root: RepoRoot,
    bound: BoundOrigin,
    serve_static: bool = True,
) -> FastAPI:
    app = FastAPI(title="ai_video_management", openapi_url=None, docs_url=None, redoc_url=None)

    exposed = ExposedTree(repo_root.path)
    resolver = SafeResolver(repo_root.path)
    reader = FileReader(exposed, resolver)
    writer = FileWriter(exposed, resolver)
    walker = TreeWalker(exposed)
    media_renamer = MediaRenamer(exposed, resolver)
    media_archiver = MediaArchiver(exposed, resolver)
    downloads_importer = DownloadsImporter(exposed, resolver, media_renamer)
    actor_pool = ActorPool(exposed, resolver)
    # Eager-create the actor pool folder on startup (follow-up 015): the sidebar
    # "🎭 生成演员" button is bound to the `_actors/` tree row, so the folder
    # must exist before the user can trigger the first batch — otherwise the UI
    # entry point is invisible.
    try:
        actor_pool.actors_dir().mkdir(parents=True, exist_ok=True)
    except OSError:
        pass
    casting = Casting(exposed, resolver, media_renamer, actor_pool)

    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(OriginHostMiddleware, bound=bound)

    @app.get("/api/tree")
    def get_tree() -> dict[str, Any]:
        return walker.build()

    @app.get("/api/file")
    def get_file(path: str = Query(...)) -> Response:
        try:
            result = reader.read(path)
        except fr.UnsupportedExtension:
            return JSONResponse(
                status_code=400,
                content={"detail": {"kind": "extension_not_allowed"}},
            )
        except fr.FileTooLarge:
            return JSONResponse(
                status_code=413,
                content={"detail": {"kind": "too_large"}},
            )
        except fr.OutsideSandbox:
            return JSONResponse(
                status_code=404,
                content={"detail": {"kind": "not_found"}},
            )
        headers = FileReader.security_headers(Path(result.rel_path).name)
        return JSONResponse(status_code=200, content=result.to_payload(), headers=headers)

    @app.put("/api/file")
    def put_file(
        body: FilePutBody,
        if_unmodified_since: str | None = Header(default=None, alias="If-Unmodified-Since"),
    ) -> Response:
        try:
            result = writer.write(body.path, body.content, if_unmodified_since)
        except fw.MissingIfUnmodifiedSince:
            return JSONResponse(
                status_code=400,
                content={"detail": {"kind": "missing_if_unmodified_since"}},
            )
        except fw.UnsupportedExtension:
            return JSONResponse(
                status_code=400,
                content={"detail": {"kind": "extension_not_allowed"}},
            )
        except fw.FileTooLarge:
            return JSONResponse(
                status_code=413,
                content={"detail": {"kind": "too_large"}},
            )
        except fw.InvalidBodyEncoding:
            return JSONResponse(
                status_code=400,
                content={"detail": {"kind": "invalid_body_encoding"}},
            )
        except fw.StaleWrite as sw:
            return JSONResponse(
                status_code=409,
                content={"detail": {"kind": "stale_write", "current_mtime": sw.current_mtime}},
            )
        except fw.OutsideSandbox:
            return JSONResponse(
                status_code=404,
                content={"detail": {"kind": "not_found"}},
            )
        return JSONResponse(status_code=200, content=result.to_payload())

    @app.api_route("/api/file", methods=["PATCH", "DELETE", "POST"])
    def file_method_not_allowed() -> Response:
        return JSONResponse(
            status_code=405,
            content={"detail": {"kind": "method_not_allowed"}},
            headers={"Allow": "GET, PUT"},
        )

    @app.get("/api/media")
    def get_media(path: str = Query(...)) -> Response:
        """Serve raw media bytes (image / video) bypassing /api/file's base64 + 1MB limit.

        Per follow-up 005: webapp displays inline images and HTML5 video players.
        Reuses the same EXPOSED_TREE sandbox (only ai_videos/** + research/** paths).
        FastAPI FileResponse handles HTTP range requests for video seeking automatically.
        """
        ext = Path(path).suffix.lower() if isinstance(path, str) else ""
        if ext not in MEDIA_EXTENSIONS:
            return JSONResponse(
                status_code=400,
                content={"detail": {"kind": "extension_not_allowed"}},
            )
        if not exposed.is_inside(path):
            return JSONResponse(
                status_code=404,
                content={"detail": {"kind": "not_found"}},
            )
        resolved = resolver.resolve(path)
        if resolved is None or not resolved.is_file():
            return JSONResponse(
                status_code=404,
                content={"detail": {"kind": "not_found"}},
            )
        media_type = _MEDIA_MIME_MAP.get(ext, "application/octet-stream")
        return FileResponse(
            str(resolved),
            media_type=media_type,
            headers=FileReader.security_headers(resolved.name),
        )

    @app.api_route("/api/media", methods=["PUT", "PATCH", "DELETE", "POST"])
    def media_method_not_allowed() -> Response:
        return JSONResponse(
            status_code=405,
            content={"detail": {"kind": "method_not_allowed"}},
            headers={"Allow": "GET"},
        )

    @app.post("/api/rename-media")
    def rename_media(body: RenameMediaBody) -> Response:
        try:
            result = media_renamer.rename_drama(body.path)
        except InvalidDramaPath:
            return JSONResponse(
                status_code=400,
                content={"detail": {"kind": "invalid_drama_path"}},
            )
        except DramaNotFound:
            return JSONResponse(
                status_code=404,
                content={"detail": {"kind": "not_found"}},
            )
        return JSONResponse(status_code=200, content=result.to_payload())

    @app.api_route("/api/rename-media", methods=["GET", "PUT", "PATCH", "DELETE"])
    def rename_media_method_not_allowed() -> Response:
        return JSONResponse(
            status_code=405,
            content={"detail": {"kind": "method_not_allowed"}},
            headers={"Allow": "POST"},
        )

    @app.post("/api/archive-media")
    def archive_media(body: ArchiveMediaBody) -> Response:
        try:
            result = media_archiver.archive(body.path)
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
                status_code=409,
                content={"detail": {"kind": "target_exists", "target": str(exc)}},
            )
        except MoveFailed as exc:
            return JSONResponse(
                status_code=500,
                content={"detail": {"kind": "move_failed", "message": str(exc)}},
            )
        return JSONResponse(status_code=200, content=result.to_payload())

    @app.api_route("/api/archive-media", methods=["GET", "PUT", "PATCH", "DELETE"])
    def archive_media_method_not_allowed() -> Response:
        return JSONResponse(
            status_code=405,
            content={"detail": {"kind": "method_not_allowed"}},
            headers={"Allow": "POST"},
        )

    @app.post("/api/unarchive-media")
    def unarchive_media(body: ArchiveMediaBody) -> Response:
        try:
            result = media_archiver.unarchive(body.path)
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
                status_code=409,
                content={"detail": {"kind": "target_exists", "target": str(exc)}},
            )
        except MoveFailed as exc:
            return JSONResponse(
                status_code=500,
                content={"detail": {"kind": "move_failed", "message": str(exc)}},
            )
        return JSONResponse(status_code=200, content=result.to_payload())

    @app.api_route("/api/unarchive-media", methods=["GET", "PUT", "PATCH", "DELETE"])
    def unarchive_media_method_not_allowed() -> Response:
        return JSONResponse(
            status_code=405,
            content={"detail": {"kind": "method_not_allowed"}},
            headers={"Allow": "POST"},
        )

    @app.post("/api/delete-media")
    def delete_media(body: ArchiveMediaBody) -> Response:
        try:
            result = media_archiver.delete(body.path)
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
                status_code=409,
                content={"detail": {"kind": "target_exists", "target": str(exc)}},
            )
        except MoveFailed as exc:
            return JSONResponse(
                status_code=500,
                content={"detail": {"kind": "move_failed", "message": str(exc)}},
            )
        return JSONResponse(status_code=200, content=result.to_payload())

    @app.api_route("/api/delete-media", methods=["GET", "PUT", "PATCH", "DELETE"])
    def delete_media_method_not_allowed() -> Response:
        return JSONResponse(
            status_code=405,
            content={"detail": {"kind": "method_not_allowed"}},
            headers={"Allow": "POST"},
        )

    @app.post("/api/import-from-downloads")
    def import_from_downloads(body: ImportFromDownloadsBody) -> Response:
        try:
            result = downloads_importer.import_drama(body.path)
        except InvalidDramaPath:
            return JSONResponse(
                status_code=400,
                content={"detail": {"kind": "invalid_drama_path"}},
            )
        except DramaNotFound:
            return JSONResponse(
                status_code=404,
                content={"detail": {"kind": "not_found"}},
            )
        except DownloadsDirMissing as exc:
            return JSONResponse(
                status_code=500,
                content={"detail": {"kind": "downloads_dir_missing", "path": str(exc)}},
            )
        return JSONResponse(status_code=200, content=result.to_payload())

    @app.api_route("/api/import-from-downloads", methods=["GET", "PUT", "PATCH", "DELETE"])
    def import_from_downloads_method_not_allowed() -> Response:
        return JSONResponse(
            status_code=405,
            content={"detail": {"kind": "method_not_allowed"}},
            headers={"Allow": "POST"},
        )

    @app.post("/api/actors/generate")
    def actors_generate(body: GenerateActorsBody) -> Response:
        try:
            attrs = ActorAttrs(
                ethnicity=body.ethnicity,
                gender=body.gender,
                age_range=body.age_range,
                look=body.look,
                style=body.style,
                notes=body.notes,
            )
            result = actor_pool.generate_batch(attrs, body.count, body.resolution, body.seeds)
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

    @app.api_route("/api/actors/generate", methods=["GET", "PUT", "PATCH", "DELETE"])
    def actors_generate_method_not_allowed() -> Response:
        return JSONResponse(
            status_code=405,
            content={"detail": {"kind": "method_not_allowed"}},
            headers={"Allow": "POST"},
        )

    @app.post("/api/actors/preview-prompts")
    def actors_preview_prompts(body: GenerateActorsBody) -> Response:
        try:
            attrs = ActorAttrs(
                ethnicity=body.ethnicity,
                gender=body.gender,
                age_range=body.age_range,
                look=body.look,
                style=body.style,
                notes=body.notes,
            )
            result = actor_pool.preview_prompts(attrs, body.count, body.resolution)
        except InvalidAttribute as exc:
            return JSONResponse(
                status_code=400,
                content={"detail": {"kind": "invalid_attribute", "message": str(exc)}},
            )
        return JSONResponse(status_code=200, content=result)

    @app.api_route("/api/actors/preview-prompts", methods=["GET", "PUT", "PATCH", "DELETE"])
    def actors_preview_prompts_method_not_allowed() -> Response:
        return JSONResponse(
            status_code=405,
            content={"detail": {"kind": "method_not_allowed"}},
            headers={"Allow": "POST"},
        )

    @app.get("/api/actors")
    def actors_list() -> Response:
        actors = [a.to_dict() for a in actor_pool.list_actors()]
        return JSONResponse(status_code=200, content={"actors": actors})

    @app.api_route("/api/actors", methods=["POST", "PUT", "PATCH", "DELETE"])
    def actors_list_method_not_allowed() -> Response:
        return JSONResponse(
            status_code=405,
            content={"detail": {"kind": "method_not_allowed"}},
            headers={"Allow": "GET"},
        )

    @app.post("/api/actors/delete")
    def actors_delete(body: DeleteActorBody) -> Response:
        try:
            unassigned = casting.unassign_actor_everywhere(body.actor_id)
        except OSError as exc:
            return JSONResponse(
                status_code=500,
                content={"detail": {"kind": "cascade_failed", "message": str(exc)}},
            )
        try:
            move = actor_pool.delete_actor(body.actor_id)
        except InvalidAttribute as exc:
            return JSONResponse(
                status_code=400,
                content={"detail": {"kind": "invalid_actor_id", "message": str(exc)}},
            )
        except ActorNotFound:
            return JSONResponse(
                status_code=404,
                content={"detail": {"kind": "actor_not_found"}},
            )
        except ActorDeleteTargetExists as exc:
            return JSONResponse(
                status_code=409,
                content={"detail": {"kind": "target_exists", "target": str(exc)}},
            )
        except ActorDeleteFailed as exc:
            return JSONResponse(
                status_code=500,
                content={"detail": {"kind": "move_failed", "message": str(exc)}},
            )
        return JSONResponse(
            status_code=200,
            content={"from": move["from"], "to": move["to"], "unassigned": unassigned},
        )

    @app.api_route("/api/actors/delete", methods=["GET", "PUT", "PATCH", "DELETE"])
    def actors_delete_method_not_allowed() -> Response:
        return JSONResponse(
            status_code=405,
            content={"detail": {"kind": "method_not_allowed"}},
            headers={"Allow": "POST"},
        )

    @app.get("/api/casting")
    def casting_read(path: str = Query(...)) -> Response:
        try:
            result = casting.read(path)
        except InvalidDramaPath:
            return JSONResponse(
                status_code=400,
                content={"detail": {"kind": "invalid_drama_path"}},
            )
        except DramaNotFound:
            return JSONResponse(
                status_code=404,
                content={"detail": {"kind": "not_found"}},
            )
        return JSONResponse(status_code=200, content=result.to_payload())

    @app.post("/api/casting/assign")
    def casting_assign(body: CastingAssignBody) -> Response:
        try:
            result = casting.assign(body.path, body.role, body.actor_id, body.notes)
        except InvalidDramaPath:
            return JSONResponse(
                status_code=400,
                content={"detail": {"kind": "invalid_drama_path"}},
            )
        except InvalidRole as exc:
            return JSONResponse(
                status_code=400,
                content={"detail": {"kind": "invalid_role", "message": str(exc)}},
            )
        except InvalidActorId as exc:
            return JSONResponse(
                status_code=400,
                content={"detail": {"kind": "invalid_actor_id", "message": str(exc)}},
            )
        except DramaNotFound:
            return JSONResponse(
                status_code=404,
                content={"detail": {"kind": "not_found"}},
            )
        return JSONResponse(status_code=200, content=result.to_payload())

    @app.delete("/api/casting/assign")
    def casting_unassign(body: CastingUnassignBody) -> Response:
        try:
            result = casting.unassign(body.path, body.role)
        except InvalidDramaPath:
            return JSONResponse(
                status_code=400,
                content={"detail": {"kind": "invalid_drama_path"}},
            )
        except InvalidRole as exc:
            return JSONResponse(
                status_code=400,
                content={"detail": {"kind": "invalid_role", "message": str(exc)}},
            )
        except DramaNotFound:
            return JSONResponse(
                status_code=404,
                content={"detail": {"kind": "not_found"}},
            )
        return JSONResponse(status_code=200, content=result.to_payload())

    @app.api_route("/api/casting/assign", methods=["GET", "PUT", "PATCH"])
    def casting_assign_method_not_allowed() -> Response:
        return JSONResponse(
            status_code=405,
            content={"detail": {"kind": "method_not_allowed"}},
            headers={"Allow": "POST, DELETE"},
        )

    @app.api_route("/api/casting", methods=["POST", "PUT", "PATCH", "DELETE"])
    def casting_read_method_not_allowed() -> Response:
        return JSONResponse(
            status_code=405,
            content={"detail": {"kind": "method_not_allowed"}},
            headers={"Allow": "GET"},
        )

    if serve_static:
        static_dir = Path(__file__).resolve().parent.parent / "static"
        if static_dir.is_dir():
            app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")

    return app
