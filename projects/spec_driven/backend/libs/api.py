from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from libs.file_reader import FileReadError, read_file
from libs.file_writer import write_file
from libs.regen_prompt import build_regen_prompt_result, list_stages
from libs.tree_walker import build_tree


class FileWriteBody(BaseModel):
    path: str
    text: str


class RegenPromptBody(BaseModel):
    project_type: str
    project_name: str
    stages: list[str] = []
    modules: dict[str, list[str]] = {}
    autonomous: bool = False


def _err_response(exc: FileReadError) -> JSONResponse:
    return JSONResponse(status_code=exc.status, content={"detail": exc.to_dict()})


def build_app(repo_root: Path) -> FastAPI:
    app = FastAPI(
        title="spec_driven",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )

    @app.get("/api/tree")
    def get_tree() -> dict[str, object]:
        return build_tree(repo_root)

    @app.get("/api/file")
    def get_file(path: str) -> dict[str, object]:
        try:
            content = read_file(path, repo_root)
        except FileReadError as exc:
            raise _AsHttp(exc)
        return {
            "path": content.path,
            "extension": content.extension,
            "bytes": content.bytes_size,
            "text": content.text,
        }

    @app.put("/api/file")
    def put_file(body: FileWriteBody) -> dict[str, object]:
        try:
            result = write_file(body.path, body.text, repo_root)
        except FileReadError as exc:
            raise _AsHttp(exc)
        return {"path": result.path, "bytes": result.bytes_size}

    @app.get("/api/stages")
    def get_stages(project_type: str, project_name: str) -> dict[str, object]:
        return list_stages(project_type, project_name)

    @app.post("/api/regen-prompt")
    def post_regen(body: RegenPromptBody) -> dict[str, object]:
        try:
            result = build_regen_prompt_result(
                project_type=body.project_type,
                project_name=body.project_name,
                stage_ids=body.stages,
                module_ids=body.modules,
                autonomous=body.autonomous,
                repo_root=repo_root,
            )
        except FileReadError as exc:
            raise _AsHttp(exc)
        return {
            "prompt": result.prompt,
            "warning": result.warning,
            "selected_stages_count": result.selected_stages_count,
            "follow_ups_count": result.follow_ups_count,
            "autonomous": result.autonomous,
            "bytes": len(result.prompt.encode("utf-8")),
        }

    @app.exception_handler(_AsHttp)
    async def _handle_as_http(_: Request, exc: _AsHttp) -> JSONResponse:
        return _err_response(exc.inner)

    static_dir = (Path(__file__).resolve().parent.parent / "static")
    if static_dir.exists() and static_dir.is_dir():
        assets_dir = static_dir / "assets"
        if assets_dir.exists() and assets_dir.is_dir():
            app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

        @app.get("/{full_path:path}")
        def spa_fallback(full_path: str) -> FileResponse:
            index_html = static_dir / "index.html"
            return FileResponse(str(index_html))

    return app


class _AsHttp(Exception):
    def __init__(self, inner: FileReadError) -> None:
        super().__init__(inner.error)
        self.inner: FileReadError = inner


def create_app() -> FastAPI:
    from libs.repo_root import discover_repo_root
    repo_root = discover_repo_root(Path(__file__).resolve())
    return build_app(repo_root)
