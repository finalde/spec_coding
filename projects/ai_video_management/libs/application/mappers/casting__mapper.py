"""CastingMapper — translation between infrastructure CastingResult and CastingQdto."""
from __future__ import annotations

from libs.application.dtos.casting__dto import CastingQdto
from libs.infrastructure.writers.casting__writer import CastingResult


class CastingMapper:
    @staticmethod
    def to_qdto(r: CastingResult) -> CastingQdto:
        return CastingQdto(rel_path=r.path, entries=list(r.entries))
