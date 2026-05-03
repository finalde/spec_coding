from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, Header, HTTPException, Query, Request
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from libs import file_reader as fr
from libs import file_writer as fw
from libs import promotions as prom
from libs.api_security import BoundOrigin, OriginHostMiddleware
from libs.exposed_tree import ExposedTree, MAX_FILE_BYTES
from libs.file_reader import FileReader
from libs.file_writer import FileWriter
from libs.promotions import Promotions
from libs.regen_prompt import PromptTooLarge, RegenPromptBuilder
from libs.repo_root import RepoRoot
from libs.safe_resolve import SafeResolver
from libs.stages import Stages
from libs.tree_walker import TreeWalker


class FilePutBody(BaseModel):
    path: str
    content: str


class PromotePostBody(BaseModel):
    project_type: str
    project_name: str
    stage_folder: str
    source_file: str
    item_id: str
    item_text: str


class PromoteDeleteBody(BaseModel):
    project_type: str
    project_name: str
    stage_folder: str
    item_id: str


class RegenPromptBody(BaseModel):
    project_type: str
    project_name: str
    stages: list[str] = Field(default_factory=list)
    modules: dict[str, list[str]] = Field(default_factory=dict)
    autonomous: bool = False


def create_app(
    repo_root: RepoRoot,
    bound: BoundOrigin,
    serve_static: bool = True,
) -> FastAPI:
    app = FastAPI(title="spec_driven", openapi_url=None, docs_url=None, redoc_url=None)

    exposed = ExposedTree(repo_root.path)
    resolver = SafeResolver(repo_root.path)
    reader = FileReader(exposed, resolver)
    writer = FileWriter(exposed, resolver)
    promotions = Promotions(exposed, resolver)
    regen_builder = RegenPromptBuilder(exposed, resolver)
    walker = TreeWalker(exposed)

    app.add_middleware(OriginHostMiddleware, bound=bound)

    @app.get("/api/tree")
    def get_tree() -> dict[str, Any]:
        return walker.build()

    @app.get("/api/stages")
    def get_stages(
        project_type: str | None = Query(default=None),
        project_name: str | None = Query(default=None),
    ) -> dict[str, Any]:
        return {"stages": Stages.to_payload()}

    @app.get("/api/file")
    def get_file(path: str = Query(...)) -> Response:
        try:
            result = reader.read(path)
        except fr.UnsupportedExtension:
            return JSONResponse(
                status_code=415,
                content={"detail": {"kind": "extension_not_allowed"}},
                headers={"X-Content-Type-Options": "nosniff"},
            )
        except fr.FileTooLarge:
            return JSONResponse(
                status_code=413,
                content={"detail": {"kind": "too_large"}},
                headers={"X-Content-Type-Options": "nosniff"},
            )
        except fr.OutsideSandbox:
            return JSONResponse(
                status_code=404,
                content={"detail": {"kind": "not_found"}},
                headers={"X-Content-Type-Options": "nosniff"},
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
        except fw.UnsupportedExtension:
            return JSONResponse(
                status_code=415,
                content={"detail": {"kind": "extension_not_allowed"}},
            )
        except fw.FileTooLarge:
            return JSONResponse(
                status_code=413,
                content={"detail": {"kind": "too_large"}},
            )
        except fw.InvalidBodyEncoding:
            return JSONResponse(
                status_code=415,
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

    @app.api_route("/api/file", methods=["PATCH", "DELETE"])
    def file_method_not_allowed() -> Response:
        return JSONResponse(
            status_code=405,
            content={"detail": {"kind": "method_not_allowed"}},
            headers={"Allow": "GET, PUT"},
        )

    @app.post("/api/regen-prompt")
    def post_regen_prompt(body: RegenPromptBody) -> Response:
        try:
            assembled = regen_builder.build(
                project_type=body.project_type,
                project_name=body.project_name,
                stages=body.stages,
                modules=body.modules,
                autonomous=body.autonomous,
            )
        except PromptTooLarge:
            return JSONResponse(
                status_code=413,
                content={"detail": {"kind": "too_large"}},
            )
        return JSONResponse(status_code=200, content=assembled.to_payload())

    @app.post("/api/promote")
    def post_promote(body: PromotePostBody) -> Response:
        try:
            result = promotions.add(
                project_type=body.project_type,
                project_name=body.project_name,
                stage_folder=body.stage_folder,
                source_file=body.source_file,
                item_id=body.item_id,
                item_text=body.item_text,
            )
        except prom.StageFolderRejected:
            return JSONResponse(
                status_code=400,
                content={"detail": {"kind": "stage_folder_rejected"}},
            )
        except prom.PromotionPathRejected:
            return JSONResponse(
                status_code=404,
                content={"detail": {"kind": "not_found"}},
            )
        return JSONResponse(status_code=200, content=result)

    @app.delete("/api/promote")
    def delete_promote(body: PromoteDeleteBody) -> Response:
        try:
            result = promotions.remove(
                project_type=body.project_type,
                project_name=body.project_name,
                stage_folder=body.stage_folder,
                item_id=body.item_id,
            )
        except prom.StageFolderRejected:
            return JSONResponse(
                status_code=400,
                content={"detail": {"kind": "stage_folder_rejected"}},
            )
        except prom.PromotionPathRejected:
            return JSONResponse(
                status_code=404,
                content={"detail": {"kind": "not_found"}},
            )
        return JSONResponse(status_code=200, content=result)

    if serve_static:
        static_dir = Path(__file__).resolve().parent.parent / "static"
        if static_dir.is_dir():
            app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")

    return app
