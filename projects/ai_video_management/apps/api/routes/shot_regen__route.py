"""Shot-regen routes: POST /api/regen-shot-prompt — assemble a copy-paste
regeneration prompt re-weaving the referenced performance-library entries."""
from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

from apps.api.container import Container
from libs.application.queries.shot_regen__query import ShotRegenPromptQuery

router = APIRouter()


class RegenShotPromptBody(BaseModel):
    path: str
    selected_perf_ids: list[str] | None = None


@router.post("/api/regen-shot-prompt")
@inject
def regen_shot_prompt(
    body: RegenShotPromptBody,
    query: ShotRegenPromptQuery = Depends(Provide[Container.shot_regen_query]),
) -> Response:
    return JSONResponse(
        status_code=200,
        content=query.build(body.path, body.selected_perf_ids),
    )
