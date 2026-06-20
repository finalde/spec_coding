"""Intro-card-aggregate route: POST /api/burn-intro-cards."""
from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

from apps.api.container import Container
from libs.application.commands.intro_card__command import IntroCardCommand

router = APIRouter()


class IntroCardPathBody(BaseModel):
    path: str


@router.post("/api/burn-intro-cards")
@inject
def burn_intro_cards(
    body: IntroCardPathBody,
    command: IntroCardCommand = Depends(Provide[Container.intro_card_command]),
) -> Response:
    return JSONResponse(status_code=200, content=command.burn(body.path).to_payload())
