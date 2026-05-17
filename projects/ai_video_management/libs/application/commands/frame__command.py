"""Frame-aggregate commands: extract 8 reference PNGs from a scene video.

The 8-frame schedule (timestamps + role + shot_size + rank) is domain
knowledge — libs.domain.value_objects.frame__valueobject CANONICAL_FRAMES.
The ffmpeg subprocess that materialises each PNG lives in infrastructure.
"""
from __future__ import annotations

from libs.application.dtos.frame__dto import ExtractFramesResultCdto
from libs.application.mappers.frame__mapper import FrameMapper
from libs.domain.errors.frame__error import (
    FfmpegMissingError,
    FrameExtractFailedError,
    InvalidVideoPathError,
    NotVideoError,
    VideoNotFoundError,
)
from libs.infrastructure.writers.frame__writer import (
    ExtractFailed,
    FfmpegMissing,
    FrameExtractor,
    InvalidPath,
    NotFound,
    NotVideo,
)


class FrameCommand:
    def __init__(self, extractor: FrameExtractor) -> None:
        self._extractor = extractor

    def extract(self, rel_path: str) -> ExtractFramesResultCdto:
        try:
            result = self._extractor.extract(rel_path)
        except InvalidPath as exc:
            raise InvalidVideoPathError(str(exc)) from exc
        except NotVideo as exc:
            raise NotVideoError(str(exc)) from exc
        except NotFound as exc:
            raise VideoNotFoundError(str(exc)) from exc
        except FfmpegMissing as exc:
            raise FfmpegMissingError(str(exc)) from exc
        except ExtractFailed as exc:
            raise FrameExtractFailedError(str(exc)) from exc
        return FrameMapper.to_cdto(result)
