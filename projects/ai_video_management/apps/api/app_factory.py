"""FastAPI app construction.

Per follow-up 114: every aggregate's domain errors are translated to JSON
responses by global `app.exception_handler` registrations here, replacing
the per-endpoint try/except blocks that used to live in each route file.
The shape — `{"detail": {"kind": <slug>, ...}}` — is byte-identical to the
prior behavior; only the place that produces it has moved.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from apps.api.container import Container
from apps.api.routes import router
from libs.domain.errors.actor__error import (
    ActorAlreadyAssignedError,
    ActorAlreadyDeletedError,
    ActorDeleteFailedError,
    ActorDeleteTargetExistsError,
    ActorGenerationDirMissingError,
    ActorNotFoundError,
    AssignmentsScanFailedError,
    InvalidActorAttributeError,
    InvalidActorIdError,
)
from libs.domain.errors.casting__error import (
    DramaNotFoundError,
    InvalidDramaPathError,
    InvalidRoleError,
)
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
from libs.domain.errors.downloads__error import DownloadsDirMissingError
from libs.domain.errors.file__error import (
    FileNotInSandboxError,
    FileTooLargeError,
    InvalidBodyEncodingError,
    MissingIfUnmodifiedSinceError,
    StaleWriteError,
    UnsupportedFileExtensionError,
)
from libs.domain.errors.frame__error import (
    FfmpegMissingError,
    FrameExtractFailedError,
    InvalidVideoPathError,
    NotVideoError,
    VideoNotFoundError,
)
from libs.domain.errors.media__error import (
    AlreadyArchivedError,
    AlreadyDeletedError,
    InvalidMediaPathError,
    MediaMoveFailedError,
    MediaNotFoundError,
    MediaTargetExistsError,
    NotInArchiveError,
    NotMediaError,
    NotUnderAiVideosError,
    NotUnderDeletedError,
)
from libs.domain.errors.voice__error import (
    InvalidVoiceAttributeError,
    InvalidVoiceIdError,
    VoiceAlreadyAssignedError,
    VoiceAlreadyDeletedError,
    VoiceAudioExtensionNotAllowedError,
    VoiceAudioExtractFailedError,
    VoiceAudioTooLargeError,
    VoiceAudioUploadFailedError,
    VoiceDeleteFailedError,
    VoiceDeleteTargetExistsError,
    VoiceFfmpegMissingError,
    VoiceGenerationDirMissingError,
    VoiceMp4MissingError,
    VoiceNotFoundError,
)
from libs.infrastructure.middleware.origin_host__middleware import (
    OriginHostMiddleware,
    SecurityHeadersMiddleware,
)


def _err(status: int, kind: str, **extras: Any) -> JSONResponse:
    body: dict[str, Any] = {"kind": kind}
    body.update(extras)
    return JSONResponse(status_code=status, content={"detail": body})


# (ErrorClass, status_code, kind, include_message)
_PLAIN: tuple[tuple[type[Exception], int, str, bool], ...] = (
    # actor
    (InvalidActorAttributeError, 400, "invalid_attribute", True),
    (InvalidActorIdError, 400, "invalid_actor_id", True),
    (ActorNotFoundError, 404, "actor_not_found", False),
    (ActorAlreadyDeletedError, 400, "already_deleted", False),
    (ActorDeleteFailedError, 500, "move_failed", True),
    (ActorGenerationDirMissingError, 500, "actors_dir_unwritable", True),
    (AssignmentsScanFailedError, 500, "assignments_scan_failed", True),
    # casting
    (InvalidDramaPathError, 400, "invalid_drama_path", False),
    (DramaNotFoundError, 404, "not_found", False),
    (InvalidRoleError, 400, "invalid_role", True),
    # character_video
    (InvalidCharacterVideoPathError, 400, "invalid_path", False),
    (InvalidShotMdPathError, 400, "invalid_path", False),
    (NotCharacterVideoError, 400, "not_a_character_video", False),
    (NotShotMdError, 400, "not_a_shot_md", False),
    (NoCharacterTableError, 400, "no_character_table", False),
    (CharacterVideoNotFoundError, 404, "not_found", False),
    (ShotMdNotFoundError, 404, "not_found", False),
    (FfmpegMissingForCharacterVideoError, 500, "ffmpeg_missing", True),
    (TruncateFailedError, 500, "truncate_failed", True),
    (ConcatFailedError, 500, "concat_failed", True),
    (ViewExtractFailedError, 500, "view_extract_failed", True),
    (AudioExtractFailedError, 500, "audio_extract_failed", True),
    # downloads
    # (DownloadsDirMissingError handled specially — payload key is `path`, not `message`.)
    # file
    (UnsupportedFileExtensionError, 400, "extension_not_allowed", False),
    (FileTooLargeError, 413, "too_large", False),
    (FileNotInSandboxError, 404, "not_found", False),
    (MissingIfUnmodifiedSinceError, 400, "missing_if_unmodified_since", False),
    (InvalidBodyEncodingError, 400, "invalid_body_encoding", False),
    # frame
    (InvalidVideoPathError, 400, "invalid_path", False),
    (NotVideoError, 400, "not_a_video", False),
    (VideoNotFoundError, 404, "not_found", False),
    (FfmpegMissingError, 500, "ffmpeg_missing", True),
    (FrameExtractFailedError, 500, "extract_failed", True),
    # media
    (InvalidMediaPathError, 400, "invalid_path", False),
    (NotMediaError, 400, "extension_not_allowed", False),
    (NotUnderAiVideosError, 400, "not_in_ai_videos", False),
    (AlreadyDeletedError, 400, "already_deleted", False),
    (AlreadyArchivedError, 400, "already_archived", False),
    (NotInArchiveError, 400, "not_in_archive", False),
    (NotUnderDeletedError, 400, "not_in_deleted", False),
    (MediaNotFoundError, 404, "not_found", False),
    (MediaMoveFailedError, 500, "move_failed", True),
    # voice (follow-up 115)
    (InvalidVoiceAttributeError, 400, "invalid_attribute", True),
    (InvalidVoiceIdError, 400, "invalid_voice_id", True),
    (VoiceNotFoundError, 404, "voice_not_found", False),
    (VoiceAlreadyDeletedError, 400, "already_deleted", False),
    (VoiceDeleteFailedError, 500, "move_failed", True),
    (VoiceGenerationDirMissingError, 500, "voices_dir_unwritable", True),
    (VoiceAudioExtensionNotAllowedError, 400, "extension_not_allowed", True),
    (VoiceAudioTooLargeError, 413, "body_too_large", True),
    (VoiceAudioUploadFailedError, 500, "write_failed", True),
    (VoiceMp4MissingError, 400, "mp4_missing", True),
    (VoiceFfmpegMissingError, 500, "ffmpeg_missing", True),
    (VoiceAudioExtractFailedError, 500, "audio_extract_failed", True),
)


def _make_plain_handler(status: int, kind: str, include_message: bool):
    if include_message:
        def handler(_req: Request, exc: Exception) -> Response:
            return _err(status, kind, message=str(exc))
    else:
        def handler(_req: Request, _exc: Exception) -> Response:
            return _err(status, kind)
    return handler


def _register_exception_handlers(app: FastAPI) -> None:
    for exc_cls, status, kind, include_message in _PLAIN:
        app.add_exception_handler(exc_cls, _make_plain_handler(status, kind, include_message))

    @app.exception_handler(StaleWriteError)
    def _stale_write(_req: Request, exc: StaleWriteError) -> Response:  # type: ignore[unused-function]
        return _err(409, "stale_write", current_mtime=exc.current_mtime)

    @app.exception_handler(ActorAlreadyAssignedError)
    def _actor_assigned(_req: Request, exc: ActorAlreadyAssignedError) -> Response:  # type: ignore[unused-function]
        return _err(409, "actor_is_assigned", actor_id=exc.actor_id, assignments=exc.assignments)

    @app.exception_handler(ActorDeleteTargetExistsError)
    def _actor_target_exists(_req: Request, exc: ActorDeleteTargetExistsError) -> Response:  # type: ignore[unused-function]
        return _err(409, "target_exists", target=str(exc))

    @app.exception_handler(VoiceAlreadyAssignedError)
    def _voice_assigned(_req: Request, exc: VoiceAlreadyAssignedError) -> Response:  # type: ignore[unused-function]
        return _err(409, "voice_is_assigned", voice_id=exc.voice_id, assignments=exc.assignments)

    @app.exception_handler(VoiceDeleteTargetExistsError)
    def _voice_target_exists(_req: Request, exc: VoiceDeleteTargetExistsError) -> Response:  # type: ignore[unused-function]
        return _err(409, "target_exists", target=str(exc))

    @app.exception_handler(MediaTargetExistsError)
    def _media_target_exists(_req: Request, exc: MediaTargetExistsError) -> Response:  # type: ignore[unused-function]
        return _err(409, "target_exists", target=str(exc))

    @app.exception_handler(DownloadsDirMissingError)
    def _downloads_dir_missing(_req: Request, exc: DownloadsDirMissingError) -> Response:  # type: ignore[unused-function]
        return _err(500, "downloads_dir_missing", path=str(exc))

    @app.exception_handler(StarletteHTTPException)
    def _http_exception(_req: Request, exc: StarletteHTTPException) -> Response:  # type: ignore[unused-function]
        if exc.status_code == 405:
            headers = dict(exc.headers or {})
            return JSONResponse(
                status_code=405,
                content={"detail": {"kind": "method_not_allowed"}},
                headers=headers,
            )
        # Fall through to FastAPI's default shape for other HTTPExceptions.
        if isinstance(exc, FastAPIHTTPException):
            return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
        return JSONResponse(status_code=exc.status_code, content={"detail": str(exc.detail)})


def create_app(container: Container, serve_static: bool = True) -> FastAPI:
    app = FastAPI(title="ai_video_management", openapi_url=None, docs_url=None, redoc_url=None)

    # Eager-create the actor pool folder (follow-up 015). If this fails the
    # actor feature is unusable — let the traceback surface at startup
    # rather than silently continuing into a confusing empty-list later.
    container.actor_pool().actors_dir().mkdir(parents=True, exist_ok=True)
    # Same posture for the voice pool folder (follow-up 115).
    container.voice_pool().voices_dir().mkdir(parents=True, exist_ok=True)

    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(OriginHostMiddleware, bound=container.bound_origin())
    _register_exception_handlers(app)
    app.include_router(router)

    if serve_static:
        static_dir = Path(__file__).resolve().parent / "static"
        if static_dir.is_dir():
            app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")

    return app
