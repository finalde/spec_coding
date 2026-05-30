"""Voice-aggregate routes (follow-up 115).

generate / generate-diverse / preview-prompts / preview-diverse / list /
delete / assignments / audio-upload + casting assign-voice / unassign-voice.

All voice flows are LOCAL — no outbound HTTP. Domain errors translate to JSON
via the global FastAPI handlers in `apps/api/app_factory.py`.
"""
from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

from apps.api.container import Container
from libs.application.commands.casting__command import CastingCommand
from libs.application.commands.voice__command import VoiceCommand
from libs.application.dtos.voice__dto import (
    GenerateDiverseVoicesInputCdto,
    GenerateVoicesInputCdto,
)
from libs.application.queries.voice__query import VoiceQuery
from libs.domain.value_objects.voice__valueobject import AUDIO_MAX_BYTES
from libs.domain.errors.voice__error import VoiceAudioTooLargeError

router = APIRouter()


class GenerateVoicesBody(BaseModel):
    count: int
    archetype: str
    gender: str
    age_impression: str
    pace: str = "medium"
    pitch_register: str = "mid"
    emotion_default: str = "calm"
    tone: str = ""
    signature_inflection: str = ""
    notes: str = ""
    seeds: list[int] | None = None
    batch_seed: int | None = None
    batch_size: int | None = None
    slot_index: int | None = None


class GenerateDiverseVoicesBody(BaseModel):
    count: int
    gender: str
    age_impression: str | None = None
    notes: str = ""


class DeleteVoiceBody(BaseModel):
    voice_id: str


class AssignVoiceBody(BaseModel):
    path: str
    role: str
    voice_id: str
    notes: str | None = None


class UnassignVoiceBody(BaseModel):
    path: str
    role: str


@router.post("/api/voices/generate")
@inject
def voices_generate(
    body: GenerateVoicesBody,
    command: VoiceCommand = Depends(Provide[Container.voice_command]),
) -> Response:
    cdto = command.generate(GenerateVoicesInputCdto(**body.model_dump()))
    return JSONResponse(status_code=200, content=cdto.to_payload())


@router.post("/api/voices/generate-diverse")
@inject
def voices_generate_diverse(
    body: GenerateDiverseVoicesBody,
    command: VoiceCommand = Depends(Provide[Container.voice_command]),
) -> Response:
    cdto = command.generate_diverse(GenerateDiverseVoicesInputCdto(**body.model_dump()))
    return JSONResponse(status_code=200, content=cdto.to_payload())


@router.post("/api/voices/preview-prompts")
@inject
def voices_preview_prompts(
    body: GenerateVoicesBody,
    query: VoiceQuery = Depends(Provide[Container.voice_query]),
) -> Response:
    qdto = query.preview_prompts(GenerateVoicesInputCdto(**body.model_dump()))
    return JSONResponse(status_code=200, content=qdto.to_payload())


@router.post("/api/voices/preview-diverse")
@inject
def voices_preview_diverse(
    body: GenerateDiverseVoicesBody,
    query: VoiceQuery = Depends(Provide[Container.voice_query]),
) -> Response:
    qdto = query.preview_diverse_prompts(
        GenerateDiverseVoicesInputCdto(**body.model_dump())
    )
    return JSONResponse(status_code=200, content=qdto.to_payload())


@router.get("/api/voices")
@inject
def voices_list(query: VoiceQuery = Depends(Provide[Container.voice_query])) -> Response:
    return JSONResponse(status_code=200, content=query.list().to_payload())


@router.post("/api/voices/delete")
@inject
def voices_delete(
    body: DeleteVoiceBody,
    command: VoiceCommand = Depends(Provide[Container.voice_command]),
) -> Response:
    cdto = command.delete(body.voice_id)
    return JSONResponse(status_code=200, content=cdto.to_payload())


@router.get("/api/voices/assignments")
@inject
def voices_assignments(
    voice_id: str = Query(...),
    query: VoiceQuery = Depends(Provide[Container.voice_query]),
) -> Response:
    return JSONResponse(
        status_code=200, content=query.get_assignments(voice_id).to_payload()
    )


@router.post("/api/voices/{voice_id}/audio")
@inject
async def voices_upload_audio(
    voice_id: str,
    audio: UploadFile = File(...),
    command: VoiceCommand = Depends(Provide[Container.voice_command]),
) -> Response:
    """Multipart upload of a user-rendered audio sample (.mp3 / .wav / .m4a,
    ≤ 10 MiB). The webapp never generates audio — this endpoint just stores
    whatever the user already rendered externally."""
    # Read the multipart body with an explicit size cap so we never accept a
    # payload larger than AUDIO_MAX_BYTES into memory.
    data = await audio.read(AUDIO_MAX_BYTES + 1)
    if len(data) > AUDIO_MAX_BYTES:
        raise VoiceAudioTooLargeError(
            f"audio {len(data)} bytes exceeds cap {AUDIO_MAX_BYTES}"
        )
    cdto = command.upload_audio(voice_id, data, audio.filename or "")
    return JSONResponse(status_code=200, content=cdto.to_payload())


@router.post("/api/voices/{voice_id}/extract-audio")
@inject
def voices_extract_audio(
    voice_id: str,
    command: VoiceCommand = Depends(Provide[Container.voice_command]),
) -> Response:
    """Extract mp3 from any `*.mp4` the user manually dropped into the voice
    folder. The lex-last mp4 wins as the persisted sample (`voice_NNNN.mp3`);
    the sidecar's `audio_sample` row is refreshed. Local-only — uses the
    bundled imageio_ffmpeg binary, no outbound HTTP."""
    cdto = command.extract_audio(voice_id)
    return JSONResponse(status_code=200, content=cdto.to_payload())


@router.post("/api/casting/assign-voice")
@inject
def casting_assign_voice(
    body: AssignVoiceBody,
    command: CastingCommand = Depends(Provide[Container.casting_command]),
) -> Response:
    result = command.assign_voice(body.path, body.role, body.voice_id, body.notes)
    return JSONResponse(status_code=200, content=result.to_payload())


@router.delete("/api/casting/assign-voice")
@inject
def casting_unassign_voice(
    body: UnassignVoiceBody,
    command: CastingCommand = Depends(Provide[Container.casting_command]),
) -> Response:
    result = command.unassign_voice(body.path, body.role)
    return JSONResponse(status_code=200, content=result.to_payload())
