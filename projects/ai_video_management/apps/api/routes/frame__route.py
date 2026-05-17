"""Frame-aggregate routes: POST /api/extract-frames."""
from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

from apps.api.container import Container
from apps.api.routes._helpers import method_not_allowed
from libs.application.commands.frame__command import FrameCommand
from libs.domain.errors.frame__error import (
    FfmpegMissingError,
    FrameExtractFailedError,
    InvalidVideoPathError,
    NotVideoError,
    VideoNotFoundError,
)

router = APIRouter()


class ExtractFramesBody(BaseModel):
    path: str


@router.post("/api/extract-frames")
@inject
def extract_frames(
    body: ExtractFramesBody,
    command: FrameCommand = Depends(Provide[Container.frame_command]),
) -> Response:
    try:
        cdto = command.extract(body.path)
    except InvalidVideoPathError:
        return JSONResponse(status_code=400, content={"detail": {"kind": "invalid_path"}})
    except NotVideoError:
        return JSONResponse(status_code=400, content={"detail": {"kind": "not_a_video"}})
    except VideoNotFoundError:
        return JSONResponse(status_code=404, content={"detail": {"kind": "not_found"}})
    except FfmpegMissingError as exc:
        return JSONResponse(
            status_code=500, content={"detail": {"kind": "ffmpeg_missing", "message": str(exc)}}
        )
    except FrameExtractFailedError as exc:
        return JSONResponse(
            status_code=500, content={"detail": {"kind": "extract_failed", "message": str(exc)}}
        )
    return JSONResponse(status_code=200, content=cdto.to_payload())


@router.api_route("/api/extract-frames", methods=["GET", "PUT", "PATCH", "DELETE"])
def extract_frames_method_not_allowed() -> Response:
    return method_not_allowed("POST")
