"""API surface for ai_video_management.

5 endpoints: `GET /api/tree`, `GET /api/file`, `PUT /api/file`,
`GET /api/media`, `POST /api/rename-media`.
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
from libs.api_security import BoundOrigin, OriginHostMiddleware, SecurityHeadersMiddleware
from libs.exposed_tree import MEDIA_EXTENSIONS, ExposedTree
from libs.file_reader import FileReader
from libs.file_writer import FileWriter
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

    if serve_static:
        static_dir = Path(__file__).resolve().parent.parent / "static"
        if static_dir.is_dir():
            app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")

    return app
