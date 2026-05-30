"""Novel-aggregate routes: GET /api/novels (list download status per novel).

Per follow-up 096. Download is CLI-only (`apps/cli/novel_download.py`) to
keep browser clients from spawning multi-hour scrapes; this route is read-only.
"""
from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, Response

from apps.api.container import Container
from libs.application.queries.novel__query import NovelQuery

router = APIRouter()


@router.get("/api/novels")
@inject
def list_novels(
    query: NovelQuery = Depends(Provide[Container.novel_query]),
) -> Response:
    items = query.list()
    return JSONResponse(
        status_code=200,
        content={"items": [q.to_payload() for q in items]},
    )
