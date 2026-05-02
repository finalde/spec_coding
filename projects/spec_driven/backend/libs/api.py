from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from libs.file_reader import FileReadError, read_file
from libs.tree_walker import build_tree


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

    if static_dir.is_dir():
        app.mount("/assets", StaticFiles(directory=str(static_dir / "assets")), name="assets")

        @app.get("/{full_path:path}")
        def serve_spa(full_path: str) -> FileResponse:
            index_html = static_dir / "index.html"
            if not index_html.exists():
                raise HTTPException(status_code=404, detail="index.html not built")
            return FileResponse(str(index_html))

    return app
