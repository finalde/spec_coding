"""FastAPI app construction.

Per follow-up 051: this module wires the FastAPI app — middleware, router
mount, static file serving. It is part of the apps/api/ bootstrap set
(alongside container.py, asgi.py, main.py) — these are the ONLY files
under apps/ that may import from libs.infrastructure (per `agent_refs/
project/development.md` §6b carve-out for app-construction wiring).
Business-handler code lives in routes.py, which has zero infra imports.
"""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from apps.api.container import Container
from apps.api.routes import router
from libs.infrastructure.middleware.origin_host__middleware import (
    OriginHostMiddleware,
    SecurityHeadersMiddleware,
)


def create_app(container: Container, serve_static: bool = True) -> FastAPI:
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
