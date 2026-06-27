"""Episode-aggregate routes: POST /api/concat-episode + POST /api/episode-seams."""
from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, ConfigDict, Field

from apps.api.container import Container
from libs.application.commands.episode__command import EpisodeCommand
from libs.application.commands.episode_takes__command import EpisodeTakesCommand
from libs.application.queries.episode__query import EpisodeQuery

router = APIRouter()


class EpisodeTakesBody(BaseModel):
    path: str


class SeamPlanEntry(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    from_: str = Field(alias="from")  # "from" is a Python keyword
    to: str
    method: str = "butt"      # "butt"(硬拼) | "trim"(裁切平滑) | "rife"(补帧)
    trim: float | None = None
    depth: int | None = None  # 补帧密度 override (None = auto; rife only)


class ConcatEpisodeBody(BaseModel):
    path: str
    lang: str = "original"  # "original" | "zh" | "en" | "both"
    rife: bool = False       # RIFE motion-bridge the 承接 seams (slower, needs GPU exe)
    plan: list[SeamPlanEntry] | None = None  # explicit per-seam plan (overrides auto gate)


class EpisodeSeamsBody(BaseModel):
    path: str
    lang: str = "original"


class EpisodeSeamMetricsBody(BaseModel):
    path: str
    lang: str = "original"
    compare: bool = True  # also score+rank the standard method panel (slower)


@router.post("/api/concat-episode")
@inject
def concat_episode(
    body: ConcatEpisodeBody,
    command: EpisodeCommand = Depends(Provide[Container.episode_command]),
) -> Response:
    plan = (
        [e.model_dump(by_alias=True) for e in body.plan]
        if body.plan is not None else None
    )
    return JSONResponse(
        status_code=200,
        content=command.concat(body.path, body.lang, body.rife, plan).to_payload(),
    )


@router.post("/api/select-episode-takes")
@inject
def select_episode_takes(
    body: EpisodeTakesBody,
    command: EpisodeTakesCommand = Depends(Provide[Container.episode_takes_command]),
) -> Response:
    return JSONResponse(status_code=200, content=command.select(body.path).to_payload())


@router.post("/api/episode-seams")
@inject
def episode_seams(
    body: EpisodeSeamsBody,
    query: EpisodeQuery = Depends(Provide[Container.episode_query]),
) -> Response:
    return JSONResponse(
        status_code=200,
        content=query.analyze_seams(body.path, body.lang).to_payload(),
    )


@router.post("/api/episode-seam-metrics")
@inject
def episode_seam_metrics(
    body: EpisodeSeamMetricsBody,
    query: EpisodeQuery = Depends(Provide[Container.episode_query]),
) -> Response:
    return JSONResponse(
        status_code=200,
        content=query.score_seams(body.path, body.lang, body.compare),
    )


@router.post("/api/episode-seam-scores")
@inject
def episode_seam_scores(
    body: EpisodeSeamsBody,
    query: EpisodeQuery = Depends(Provide[Container.episode_query]),
) -> Response:
    """Read the persisted scorecard sidecar (last build) — instant, no recompute."""
    return JSONResponse(status_code=200, content=query.read_seam_scores(body.path))
