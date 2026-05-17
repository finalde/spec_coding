"""MediaMapper — DAO↔Cdto translation for media file moves + renames."""
from __future__ import annotations

from libs.application.dtos.media__dto import (
    MediaMoveCdto,
    RenameMediaResultCdto,
)
from libs.infrastructure.writers.media__writer import MoveResult
from libs.infrastructure.writers.media__writer import RenameResult


class MediaMapper:
    @staticmethod
    def move_to_cdto(r: MoveResult) -> MediaMoveCdto:
        return MediaMoveCdto(src_rel=r.src_rel, dst_rel=r.dst_rel)

    @staticmethod
    def rename_to_cdto(r: RenameResult) -> RenameMediaResultCdto:
        return RenameMediaResultCdto(
            renamed=list(r.renamed),
            skipped=list(r.skipped),
            errors=list(r.errors),
        )
