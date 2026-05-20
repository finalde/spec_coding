"""Character-video aggregate routes: truncate / concat-shot."""
from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

from apps.api.container import Container
from libs.application.commands.character_video__command import CharacterVideoCommand
from libs.domain.errors.character_video__error import (
    AudioExtractFailedError,
    CharacterVideoNotFoundError,
    ConcatFailedError,
    FfmpegMissingForCharacterVideoError,
    InvalidCharacterVideoPathError,
    InvalidShotMdPathError,
    NoCharacterTableError,
    NotCharacterVideoError,
    NotShotMdError,
    ShotMdNotFoundError,
    TruncateFailedError,
    ViewExtractFailedError,
)

router = APIRouter()


class TruncateCharacterVideoBody(BaseModel):
    path: str


class ConcatShotCharactersBody(BaseModel):
    path: str


class ExtractCharacterViewsBody(BaseModel):
    path: str


@router.post("/api/truncate-character-video")
@inject
def truncate_character_video(
    body: TruncateCharacterVideoBody,
    command: CharacterVideoCommand = Depends(Provide[Container.character_video_command]),
) -> Response:
    try:
        cdto = command.truncate(body.path)
    except InvalidCharacterVideoPathError:
        return JSONResponse(status_code=400, content={"detail": {"kind": "invalid_path"}})
    except NotCharacterVideoError:
        return JSONResponse(status_code=400, content={"detail": {"kind": "not_a_character_video"}})
    except CharacterVideoNotFoundError:
        return JSONResponse(status_code=404, content={"detail": {"kind": "not_found"}})
    except FfmpegMissingForCharacterVideoError as exc:
        return JSONResponse(
            status_code=500, content={"detail": {"kind": "ffmpeg_missing", "message": str(exc)}}
        )
    except TruncateFailedError as exc:
        return JSONResponse(
            status_code=500, content={"detail": {"kind": "truncate_failed", "message": str(exc)}}
        )
    return JSONResponse(status_code=200, content=cdto.to_payload())


@router.post("/api/concat-shot-characters")
@inject
def concat_shot_characters(
    body: ConcatShotCharactersBody,
    command: CharacterVideoCommand = Depends(Provide[Container.character_video_command]),
) -> Response:
    try:
        cdto = command.concat_shot(body.path)
    except InvalidShotMdPathError:
        return JSONResponse(status_code=400, content={"detail": {"kind": "invalid_path"}})
    except NotShotMdError:
        return JSONResponse(status_code=400, content={"detail": {"kind": "not_a_shot_md"}})
    except ShotMdNotFoundError:
        return JSONResponse(status_code=404, content={"detail": {"kind": "not_found"}})
    except NoCharacterTableError:
        return JSONResponse(status_code=400, content={"detail": {"kind": "no_character_table"}})
    except FfmpegMissingForCharacterVideoError as exc:
        return JSONResponse(
            status_code=500, content={"detail": {"kind": "ffmpeg_missing", "message": str(exc)}}
        )
    except ConcatFailedError as exc:
        return JSONResponse(
            status_code=500, content={"detail": {"kind": "concat_failed", "message": str(exc)}}
        )
    return JSONResponse(status_code=200, content=cdto.to_payload())


@router.post("/api/extract-character-views")
@inject
def extract_character_views(
    body: ExtractCharacterViewsBody,
    command: CharacterVideoCommand = Depends(Provide[Container.character_video_command]),
) -> Response:
    try:
        cdto = command.extract_views(body.path)
    except InvalidCharacterVideoPathError:
        return JSONResponse(status_code=400, content={"detail": {"kind": "invalid_path"}})
    except NotCharacterVideoError:
        return JSONResponse(status_code=400, content={"detail": {"kind": "not_a_character_video"}})
    except CharacterVideoNotFoundError:
        return JSONResponse(status_code=404, content={"detail": {"kind": "not_found"}})
    except FfmpegMissingForCharacterVideoError as exc:
        return JSONResponse(
            status_code=500, content={"detail": {"kind": "ffmpeg_missing", "message": str(exc)}}
        )
    except ViewExtractFailedError as exc:
        return JSONResponse(
            status_code=500, content={"detail": {"kind": "view_extract_failed", "message": str(exc)}}
        )
    except AudioExtractFailedError as exc:
        return JSONResponse(
            status_code=500, content={"detail": {"kind": "audio_extract_failed", "message": str(exc)}}
        )
    return JSONResponse(status_code=200, content=cdto.to_payload())
