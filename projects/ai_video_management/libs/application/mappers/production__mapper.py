"""ProductionMapper — writer-result → Cdto translation for production export."""
from __future__ import annotations

from libs.application.dtos.production__dto import (
    ExportedEpisodeCdto,
    ExportProductionResultCdto,
)
from libs.infrastructure.writers.production__writer import ExportProductionResult


class ProductionMapper:
    @staticmethod
    def to_cdto(r: ExportProductionResult) -> ExportProductionResultCdto:
        return ExportProductionResultCdto(
            drama_rel=r.drama_rel,
            production_rel=r.production_rel,
            exported=tuple(
                ExportedEpisodeCdto(e.lang, e.folder, e.episode, e.src_rel, e.out_rel)
                for e in r.exported
            ),
            by_lang=r.by_lang(),
        )
