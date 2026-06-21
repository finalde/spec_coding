"""Bgm-aggregate commands: one class, one method per operation."""
from __future__ import annotations

from libs.application.dtos.bgm__dto import (
    BgmAudioResultCdto,
    DeleteBgmResultCdto,
    GenerateBgmsInputCdto,
    GenerateBgmsResultCdto,
)
from libs.application.mappers.bgm__mapper import BgmMapper
from libs.domain.errors.bgm__error import (
    BgmAlreadyAssignedError,
    BgmReferenceScanFailedError,
)
from libs.domain.repositories.bgm__repository import BgmRepository
from libs.domain.repositories.bgm_reference__repository import BgmReferenceRepository
from libs.domain.value_objects.bgm__valueobject import BgmAttrs, validate_bgm_id


class BgmCommand:
    def __init__(self, pool: BgmRepository, references: BgmReferenceRepository) -> None:
        self._pool = pool
        self._references = references

    def generate(self, input_cdto: GenerateBgmsInputCdto) -> GenerateBgmsResultCdto:
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
        result = self._pool.generate_batch(
            attrs,
            input_cdto.count,
            input_cdto.seeds,
            batch_seed=input_cdto.batch_seed,
            batch_size=input_cdto.batch_size,
            slot_index=input_cdto.slot_index,
        )
        return BgmMapper.generate_to_cdto(result)

    def create_prompts(self, input_cdto: GenerateBgmsInputCdto) -> GenerateBgmsResultCdto:
        """Two-step flow step 1: allocate tracks + write prompt-only sidecars,
        no audio. Same input shape as `generate`; result entries carry
        `pending_audio` + the resolved prompt instead of an audio path."""
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
        result = self._pool.create_prompts_batch(
            attrs,
            input_cdto.count,
            input_cdto.seeds,
            batch_seed=input_cdto.batch_seed,
            batch_size=input_cdto.batch_size,
            slot_index=input_cdto.slot_index,
        )
        return BgmMapper.generate_to_cdto(result)

    def generate_audio(self, bgm_id: str) -> BgmAudioResultCdto:
        """Two-step flow step 2a: render audio locally on GPU for an existing
        prompt-only track."""
        validate_bgm_id(bgm_id)
        return BgmMapper.audio_to_cdto(self._pool.generate_audio(bgm_id))

    def delete(self, bgm_id: str) -> DeleteBgmResultCdto:
        """Soft-delete a track folder; refuses when any drama's bgm.md still
        references this track id (stage-5 sign-off: 有引用则拒删)."""
        validate_bgm_id(bgm_id)
        try:
            references = self._references.find_references_for_bgm(bgm_id)
        except OSError as exc:
            raise BgmReferenceScanFailedError(str(exc)) from exc
        if references:
            raise BgmAlreadyAssignedError(bgm_id=bgm_id, assignments=references)
        move = self._pool.delete_bgm(bgm_id)
        return DeleteBgmResultCdto(
            src_rel=str(move["from"]),
            dst_rel=str(move["to"]),
        )
