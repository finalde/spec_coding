"""
FastAPI route table for spec_driven.

Routes:
- GET    /api/tree
- GET    /api/file?path=<rel>
- PUT    /api/file
- GET    /api/stages?project_type=&project_name=
- POST   /api/regen-prompt
- POST   /api/promote
- DELETE /api/promote

Mutation routes are gated by Origin/Host middleware (FR-9). 405 for any other
verb on /api/file, including PATCH and DELETE on /api/file (NFR-6, AC-12).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .api_security import BoundOrigin, OriginHostMiddleware
from .exposed_tree import ExposedTree
from .file_reader import (
    FileReader,
    NotFoundError,
    TooLargeError,
    UnsupportedExtensionError,
)
from .file_writer import FileWriter, NotTextError
from .promotions import ALLOWED_STAGE_FOLDERS, PromotionError, Promotions
from .regen_prompt import RegenInputError, RegenPromptAssembler, TooLargePromptError
from .repo_root import RepoRoot
from .safe_resolve import SafeResolver
from .stages import stages_to_jsonable
from .tree_walker import TreeWalker, to_jsonable


class WriteFileBody(BaseModel):
    path: str
    content: str


class RegenPromptBody(BaseModel):
    project_type: str
    project_name: str
    stages: list[str] = Field(default_factory=list)
    modules: dict[str, list[str]] = Field(default_factory=dict)
    autonomous: bool = False


class PromoteBody(BaseModel):
    project_type: str
    project_name: str
    stage_folder: str
    source_file: str
    item_id: str
    item_text: str


class UnpromoteBody(BaseModel):
    project_type: str
    project_name: str
    stage_folder: str
    item_id: str


def create_app(
    repo_root: RepoRoot,
    bound: BoundOrigin,
    serve_static: bool = True,
) -> FastAPI:
    app = FastAPI(title="spec_driven", version="0.1.0")
    app.add_middleware(OriginHostMiddleware, bound=bound)

    resolver = SafeResolver(root=repo_root.path)
    exposed = ExposedTree(root=repo_root.path)
    walker = TreeWalker(exposed=exposed)
    reader = FileReader(resolver=resolver)
    writer = FileWriter(resolver=resolver)
    assembler = RegenPromptAssembler(repo_root=repo_root.path)
    promotions = Promotions(repo_root=repo_root.path)

    @app.get("/api/tree")
    def get_tree() -> dict[str, Any]:
        nodes = walker.walk()
        return {"name": "root", "path": "", "type": "section", "children": [to_jsonable(n) for n in nodes]}

    @app.get("/api/file")
    def get_file(path: str) -> Response:
        try:
            result = reader.read(path)
        except NotFoundError:
            return JSONResponse({"detail": "not_found"}, status_code=404)
        except TooLargeError:
            return JSONResponse({"detail": {"kind": "too_large"}}, status_code=413)
        except UnsupportedExtensionError:
            return JSONResponse({"detail": "unsupported_extension"}, status_code=415)

        return JSONResponse(
            content=result.to_dict(),
            headers={
                "X-Content-Type-Options": "nosniff",
                "Content-Disposition": f'attachment; filename="{Path(result.path).name}"',
            },
        )

    @app.put("/api/file")
    def put_file(body: WriteFileBody) -> Response:
        try:
            result = writer.write(body.path, body.content)
        except NotFoundError:
            return JSONResponse({"detail": "not_found"}, status_code=404)
        except TooLargeError:
            return JSONResponse({"detail": {"kind": "too_large"}}, status_code=413)
        except UnsupportedExtensionError:
            return JSONResponse({"detail": "unsupported_extension"}, status_code=415)
        except NotTextError:
            return JSONResponse({"detail": {"kind": "not_text"}}, status_code=415)
        return JSONResponse(content=result.to_dict(), status_code=200)

    @app.api_route("/api/file", methods=["PATCH", "DELETE"])
    def file_disallowed_verbs() -> Response:
        return JSONResponse(
            {"detail": "method_not_allowed"},
            status_code=405,
            headers={"Allow": "GET, PUT"},
        )

    @app.get("/api/stages")
    def get_stages(project_type: str | None = None, project_name: str | None = None) -> dict[str, Any]:
        return {"stages": stages_to_jsonable(), "project_type": project_type, "project_name": project_name}

    @app.post("/api/regen-prompt")
    def post_regen_prompt(body: RegenPromptBody) -> Response:
        try:
            result = assembler.assemble(
                project_type=body.project_type,
                project_name=body.project_name,
                stage_ids=body.stages,
                modules=body.modules,
                autonomous=body.autonomous,
            )
        except RegenInputError as e:
            return JSONResponse({"detail": str(e)}, status_code=422)
        except TooLargePromptError as e:
            return JSONResponse({"detail": {"kind": "too_large", "bytes": e.bytes_count}}, status_code=413)
        return JSONResponse(content=result.to_dict(), status_code=200)

    @app.post("/api/promote")
    def post_promote(body: PromoteBody) -> Response:
        if body.stage_folder not in ALLOWED_STAGE_FOLDERS:
            return JSONResponse({"detail": "stage_folder not allowed"}, status_code=422)
        try:
            result = promotions.post(
                project_type=body.project_type,
                project_name=body.project_name,
                stage_folder=body.stage_folder,
                source_file=body.source_file,
                item_id=body.item_id,
                item_text=body.item_text,
            )
        except PromotionError as e:
            return JSONResponse({"detail": str(e)}, status_code=422)
        return JSONResponse(content=result, status_code=200)

    @app.delete("/api/promote")
    def delete_promote(body: UnpromoteBody) -> Response:
        if body.stage_folder not in ALLOWED_STAGE_FOLDERS:
            return JSONResponse({"detail": "stage_folder not allowed"}, status_code=422)
        try:
            result = promotions.delete(
                project_type=body.project_type,
                project_name=body.project_name,
                stage_folder=body.stage_folder,
                item_id=body.item_id,
            )
        except PromotionError as e:
            msg = str(e)
            if "not found" in msg:
                return JSONResponse({"detail": msg}, status_code=404)
            return JSONResponse({"detail": msg}, status_code=422)
        return JSONResponse(content=result, status_code=200)

    if serve_static:
        static_dir = Path(__file__).resolve().parent.parent / "static"
        if static_dir.is_dir():

            @app.get("/")
            def index() -> Response:
                index_html = static_dir / "index.html"
                if index_html.is_file():
                    return FileResponse(str(index_html), headers={"Cache-Control": "no-cache"})
                return JSONResponse({"detail": "frontend not built"}, status_code=503)

            @app.get("/file/{full_path:path}")
            def spa_file_route(full_path: str) -> Response:
                index_html = static_dir / "index.html"
                if index_html.is_file():
                    return FileResponse(str(index_html), headers={"Cache-Control": "no-cache"})
                return JSONResponse({"detail": "frontend not built"}, status_code=503)

            @app.get("/project/{full_path:path}")
            def spa_project_route(full_path: str) -> Response:
                index_html = static_dir / "index.html"
                if index_html.is_file():
                    return FileResponse(str(index_html), headers={"Cache-Control": "no-cache"})
                return JSONResponse({"detail": "frontend not built"}, status_code=503)

            assets_dir = static_dir / "assets"
            if assets_dir.is_dir():
                app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    return app
