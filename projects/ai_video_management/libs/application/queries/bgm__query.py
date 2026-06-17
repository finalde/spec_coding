"""Bgm-aggregate queries: list / preview / references."""
from __future__ import annotations

from libs.application.dtos.bgm__dto import (
    BgmListQdto,
    BgmPreviewPromptsQdto,
    BgmReferencesQdto,
    GenerateBgmsInputCdto,
)
from libs.application.mappers.bgm__mapper import BgmMapper
from libs.domain.repositories.bgm__repository import BgmRepository
from libs.domain.repositories.bgm_reference__repository import BgmReferenceRepository
from libs.domain.value_objects.bgm__valueobject import BgmAttrs, validate_bgm_id


class BgmQuery:
    def __init__(self, pool: BgmRepository, references: BgmReferenceRepository) -> None:
        self._pool = pool
        self._references = references

    def list(self) -> BgmListQdto:
        """Tags each track with `is_referenced` via one bulk scan of every
        drama's bgm.md cue timelines."""
        referenced_ids = self._references.referenced_bgm_ids()
        return BgmMapper.list_to_qdto(self._pool.list_bgms(), referenced_ids=referenced_ids)

    def preview_prompts(self, input_cdto: GenerateBgmsInputCdto) -> BgmPreviewPromptsQdto:
        """Dry-run prompt preview: the same {seed, prompt} pairs `generate`
        would send to Stable Audio, without allocating folders or generating."""
        attrs = BgmAttrs(
            category=input_cdto.category,
            mood=input_cdto.mood,
            bpm=input_cdto.bpm,
            duration=input_cdto.duration,
            loopable=input_cdto.loopable,
            intensity=input_cdto.intensity,
            instruments=input_cdto.instruments,
            notes=input_cdto.notes,
        )
        raw = self._pool.preview_prompts(
            attrs,
            input_cdto.count,
            seeds=input_cdto.seeds,
            batch_seed=input_cdto.batch_seed,
            batch_size=input_cdto.batch_size,
            slot_index=input_cdto.slot_index,
        )
        return BgmMapper.preview_to_qdto(raw)

    def get_references(self, bgm_id: str) -> BgmReferencesQdto:
        """List every drama/location whose bgm.md references this track."""
        validate_bgm_id(bgm_id)
        references = self._references.find_references_for_bgm(bgm_id)
        return BgmReferencesQdto(bgm_id=bgm_id, references=references)
