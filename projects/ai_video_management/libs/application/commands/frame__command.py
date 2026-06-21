"""Frame-aggregate commands: extract 8 reference PNGs from a scene video.

The 8-frame schedule (timestamps + role + shot_size + rank) is domain
knowledge — libs.domain.value_objects.frame__valueobject CANONICAL_FRAMES.
The ffmpeg subprocess that materialises each PNG lives in infrastructure.
"""
from __future__ import annotations

from libs.application.dtos.frame__dto import (
    ExtractFramesResultCdto,
    ExtractLastFrameResultCdto,
)
from libs.application.mappers.frame__mapper import FrameMapper
from libs.infrastructure.writers.frame__writer import FrameExtractor


class FrameCommand:
    def __init__(self, extractor: FrameExtractor) -> None:
        self._extractor = extractor

    def extract(self, rel_path: str) -> ExtractFramesResultCdto:
        return FrameMapper.to_cdto(self._extractor.extract(rel_path))

    def extract_last_frame(self, rel_path: str) -> ExtractLastFrameResultCdto:
        return FrameMapper.last_frame_to_cdto(
            self._extractor.extract_last_frame(rel_path)
        )
