"""Mappers for character-video results: infra dataclasses → application CDTOs."""
from __future__ import annotations

from libs.application.dtos.character_video__dto import (
    ConcatShotCharactersResultCdto,
    ShotConcatSkippedCdto,
    ShotConcatUsedCdto,
    TruncateCharacterVideoResultCdto,
)
from libs.infrastructure.writers.character_video__writer import TruncateResult
from libs.infrastructure.writers.character_video__writer import ConcatResult


class CharacterVideoMapper:
    @staticmethod
    def truncate_to_cdto(r: TruncateResult) -> TruncateCharacterVideoResultCdto:
        return TruncateCharacterVideoResultCdto(
            src_rel=r.src_rel,
            out_rel=r.out_rel,
            duration_seconds=r.duration_seconds,
        )

    @staticmethod
    def concat_to_cdto(r: ConcatResult) -> ConcatShotCharactersResultCdto:
        used = tuple(
            ShotConcatUsedCdto(
                role=u.role,
                character_folder=u.character_folder,
                rel_path=u.video_rel,
            )
            for u in r.used
        )
        skipped = tuple(
            ShotConcatSkippedCdto(
                role=s.role,
                character_folder=s.character_folder,
                reason=s.reason,
            )
            for s in r.skipped
        )
        return ConcatShotCharactersResultCdto(
            shot_rel=r.shot_rel,
            out_rel=r.out_rel,
            used=used,
            skipped=skipped,
        )
