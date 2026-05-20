"""Mappers for character-video results: infra dataclasses → application CDTOs."""
from __future__ import annotations

from libs.application.dtos.character_video__dto import (
    CharacterAudioCdto,
    CharacterViewCdto,
    CharacterViewFailureCdto,
    ConcatShotCharactersResultCdto,
    ExtractCharacterViewsResultCdto,
    ShotConcatSkippedCdto,
    ShotConcatUsedCdto,
    TruncateCharacterVideoResultCdto,
)
from libs.infrastructure.writers.character_video__writer import (
    ConcatResult,
    TruncateResult,
    ViewExtractResult,
)


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

    @staticmethod
    def views_to_cdto(r: ViewExtractResult) -> ExtractCharacterViewsResultCdto:
        views = tuple(
            CharacterViewCdto(timestamp=v.timestamp, role=v.role, path=v.out_rel)
            for v in r.views
        )
        audio = CharacterAudioCdto(path=r.audio.out_rel) if r.audio is not None else None
        failures = tuple(
            CharacterViewFailureCdto(target=t, error=e) for (t, e) in r.failures
        )
        return ExtractCharacterViewsResultCdto(
            src_rel=r.src_rel,
            views=views,
            audio=audio,
            failures=failures,
        )
