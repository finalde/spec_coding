"""Prompt-aggregate routes: per-dimension shot-prompt refinement suggestions
(follow-up 117).

Domain errors (SuggestionProviderUnavailableError / SuggestionGenerationFailedError
/ InvalidSuggestionRequestError) are translated to JSON by the global handlers
in `apps/api/app_factory.py`. The route body stays narrow.
"""
from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

from apps.api.container import Container
from libs.application.dtos.prompt__dto import SuggestRefinementsInputQdto
from libs.application.queries.prompt__query import PromptQuery

router = APIRouter()


class SuggestRefinementsBody(BaseModel):
    dimension: str
    current_value: str = ""
    shot_context: str = ""
    prompt_body: str = ""
    drama: str | None = None
    scene: str | None = None
    count: int = 4


@router.post("/api/prompt/suggest")
@inject
def prompt_suggest(
    body: SuggestRefinementsBody,
    query: PromptQuery = Depends(Provide[Container.prompt_query]),
) -> Response:
    qdto = query.suggest_refinements(SuggestRefinementsInputQdto(**body.model_dump()))
    return JSONResponse(status_code=200, content=qdto.to_payload())
