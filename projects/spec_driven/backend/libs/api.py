from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from libs.file_reader import FileReadError, read_file
from libs.file_writer import write_file
from libs.regen_prompt import build_regen_prompt, list_stages
from libs.tree_walker import build_tree


class FileWriteBody(BaseModel):
    path: str = Field(..., min_length=1)
    text: str


class RegenPromptBody(BaseModel):
    project_type: str = Field(..., min_length=1)
    project_name: str = Field(..., min_length=1)
    stages: list[str] = Field(default_factory=list)
    modules: dict[str, list[str]] = Field(default_factory=dict)
    autonomous: bool = False


def build_app(repo_root: Path) -> FastAPI:
    app = FastAPI(title="spec_driven", docs_url=None, redoc_url=None, openapi_url=None)
    static_dir = (Path(__file__).resolve().parent.parent / "static")

    @app.get("/api/tree")
    def get_tree() -> dict[str, object]:
        return build_tree(repo_root)

    @app.get("/api/file")
    def get_file(path: str = Query(..., min_length=1)) -> JSONResponse:
        try:
            content = read_file(path, repo_root)
        except FileReadError as err:
            return JSONResponse(status_code=err.status, content=err.to_dict())
        return JSONResponse(
            content={
                "path": content.path,
                "extension": content.extension,
                "bytes": content.bytes_size,
                "text": content.text,
            }
        )

    @app.put("/api/file")
    def put_file(body: FileWriteBody) -> JSONResponse:
        try:
            result = write_file(body.path, body.text, repo_root)
        except FileReadError as err:
            return JSONResponse(status_code=err.status, content=err.to_dict())
        return JSONResponse(
            content={"path": result.path, "bytes": result.bytes_size, "ok": True}
        )

    @app.get("/api/stages")
    def get_stages(
        project_type: str = Query(..., min_length=1),
        project_name: str = Query(..., min_length=1),
    ) -> dict[str, object]:
        return list_stages(project_type, project_name)

    @app.post("/api/regen-prompt")
    def post_regen_prompt(body: RegenPromptBody) -> JSONResponse:
        prompt = build_regen_prompt(
            project_type=body.project_type,
            project_name=body.project_name,
            stage_ids=body.stages,
            module_ids=body.modules,
            autonomous=body.autonomous,
            repo_root=repo_root,
        )
        return JSONResponse(content={"prompt": prompt})

    if static_dir.is_dir():
        app.mount("/assets", StaticFiles(directory=str(static_dir / "assets")), name="assets")

        @app.get("/{full_path:path}")
        def serve_spa(full_path: str) -> FileResponse:
            index_html = static_dir / "index.html"
            if not index_html.exists():
                raise HTTPException(status_code=404, detail="index.html not built")
            return FileResponse(str(index_html))

    return app
