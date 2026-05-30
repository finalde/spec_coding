"""Voice-aggregate queries: list / preview / preview-diverse / assignments."""
from __future__ import annotations

from libs.application.dtos.voice__dto import (
    GenerateDiverseVoicesInputCdto,
    GenerateVoicesInputCdto,
    VoiceAssignmentsQdto,
    VoiceListQdto,
    VoicePreviewPromptsQdto,
)
from libs.application.mappers.voice__mapper import VoiceMapper
from libs.domain.repositories.casting__repository import CastingRepository
from libs.domain.repositories.voice__repository import VoiceRepository
from libs.domain.value_objects.voice__valueobject import VoiceAttrs, validate_voice_id


class VoiceQuery:
    def __init__(self, pool: VoiceRepository, casting: CastingRepository) -> None:
        self._pool = pool
        self._casting = casting

    def list(self) -> VoiceListQdto:
        assigned_ids = self._casting.assigned_voice_ids()
        return VoiceMapper.list_to_qdto(self._pool.list_voices(), assigned_ids=assigned_ids)

    def preview_prompts(
        self, input_cdto: GenerateVoicesInputCdto
    ) -> VoicePreviewPromptsQdto:
        attrs = VoiceAttrs(
            archetype=input_cdto.archetype,
            gender=input_cdto.gender,
            age_impression=input_cdto.age_impression,
            pace=input_cdto.pace,
            pitch_register=input_cdto.pitch_register,
            emotion_default=input_cdto.emotion_default,
            tone=input_cdto.tone,
            signature_inflection=input_cdto.signature_inflection,
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
        return VoiceMapper.preview_to_qdto(raw)

    def preview_diverse_prompts(
        self, input_cdto: GenerateDiverseVoicesInputCdto
    ) -> VoicePreviewPromptsQdto:
        raw = self._pool.preview_diverse_prompts(
            input_cdto.gender,
            input_cdto.age_impression,
            input_cdto.count,
            input_cdto.notes,
        )
        return VoiceMapper.preview_to_qdto(raw)

    def get_assignments(self, voice_id: str) -> VoiceAssignmentsQdto:
        validate_voice_id(voice_id)
        assignments = self._casting.find_voice_assignments_for_voice(voice_id)
        return VoiceAssignmentsQdto(voice_id=voice_id, assignments=assignments)
