"""Character-aggregate read routes: GET /api/character-videos — newest
turntable mp4 per character, powering the gallery tile preview."""
from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse, Response

from apps.api.container import Container
from libs.application.queries.character__query import CharacterQuery

router = APIRouter()


@router.get("/api/character-videos")
@inject
def character_videos(
    path: str = Query(...),
    query: CharacterQuery = Depends(Provide[Container.character_query]),
) -> Response:
    return JSONResponse(
        status_code=200, content=query.list_latest_videos(path).to_payload()
    )
