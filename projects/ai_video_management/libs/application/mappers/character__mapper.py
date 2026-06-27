"""Mapper: CharacterReader listings -> application Qdtos."""
from __future__ import annotations

from libs.application.dtos.character__dto import (
    CharacterVideoListingQdto,
    CharacterVideoListQdto,
)
from libs.infrastructure.readers.character__reader import CharacterVideoListing


class CharacterMapper:
    @staticmethod
    def list_to_qdto(
        rows: tuple[CharacterVideoListing, ...],
    ) -> CharacterVideoListQdto:
        return CharacterVideoListQdto(
            items=tuple(
                CharacterVideoListingQdto(
                    folder=r.folder, latest_video=r.latest_video_rel
                )
                for r in rows
            )
        )
