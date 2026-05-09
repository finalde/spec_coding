"""API surface for ai_video_management.

3 endpoints: `GET /api/tree`, `GET /api/file`, `PUT /api/file`.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, Header, Query
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from libs import file_reader as fr
from libs import file_writer as fw
from libs.api_security import BoundOrigin, OriginHostMiddleware, SecurityHeadersMiddleware
from libs.exposed_tree import ExposedTree
from libs.file_reader import FileReader
from libs.file_writer import FileWriter
from libs.repo_root import RepoRoot
from libs.safe_resolve import SafeResolver
from libs.tree_walker import TreeWalker


class FilePutBody(BaseModel):
    path: str
    content: str


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

    if serve_static:
        static_dir = Path(__file__).resolve().parent.parent / "static"
        if static_dir.is_dir():
            app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")

    return app
