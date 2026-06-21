"""FrameMapper — DAO↔Cdto translation for frame extraction results."""
from __future__ import annotations

from libs.application.dtos.frame__dto import (
    ExtractFramesResultCdto,
    ExtractLastFrameResultCdto,
    FrameFailureCdto,
    FrameRowCdto,
)
from libs.infrastructure.writers.frame__writer import ExtractResult, LastFrameResult


class FrameMapper:
    @staticmethod
    def last_frame_to_cdto(r: LastFrameResult) -> ExtractLastFrameResultCdto:
        return ExtractLastFrameResultCdto(src_rel=r.src_rel, out_rel=r.out_rel)

    @staticmethod
    def to_cdto(r: ExtractResult) -> ExtractFramesResultCdto:
        rows = tuple(
            FrameRowCdto(
                timestamp=f.timestamp,
                role=f.role,
                shot_size=f.shot_size,
                rank=f.rank,
                rel_path=f.out_rel,
            )
            for f in r.frames
        )
        fails = tuple(
            FrameFailureCdto(timestamp=t, role=role, error=err)
            for (t, role, err) in r.failures
        )
        return ExtractFramesResultCdto(src_rel=r.src_rel, frames=rows, failures=fails)
