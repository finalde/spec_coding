"""Voice-aggregate commands: one class, one method per operation."""
from __future__ import annotations

from libs.application.dtos.voice__dto import (
    DeleteVoiceResultCdto,
    ExtractVoiceAudioResultCdto,
    GenerateDiverseVoicesInputCdto,
    GenerateVoicesInputCdto,
    GenerateVoicesResultCdto,
    UploadVoiceAudioResultCdto,
)
from libs.application.mappers.voice__mapper import VoiceMapper
from libs.domain.errors.voice__error import VoiceAlreadyAssignedError
from libs.domain.repositories.casting__repository import CastingRepository
from libs.domain.repositories.voice__repository import VoiceRepository
from libs.domain.value_objects.voice__valueobject import (
    VoiceAttrs,
    validate_voice_id,
)


class VoiceCommand:
    def __init__(self, pool: VoiceRepository, casting: CastingRepository) -> None:
        self._pool = pool
        self._casting = casting

    def generate(self, input_cdto: GenerateVoicesInputCdto) -> GenerateVoicesResultCdto:
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
        result = self._pool.generate_batch(
            attrs,
            input_cdto.count,
            input_cdto.seeds,
            batch_seed=input_cdto.batch_seed,
            batch_size=input_cdto.batch_size,
            slot_index=input_cdto.slot_index,
        )
        return VoiceMapper.generate_to_cdto(result)

    def generate_diverse(
        self, input_cdto: GenerateDiverseVoicesInputCdto
    ) -> GenerateVoicesResultCdto:
        """Diverse mode rolls per-slot archetypes from a 10-archetype
        even-distribution plan (mirrors actor follow-up 053)."""
        result = self._pool.generate_diverse_batch(
            input_cdto.gender,
            input_cdto.age_impression,
            input_cdto.count,
            input_cdto.notes,
        )
        return VoiceMapper.generate_to_cdto(result)

    def delete(self, voice_id: str) -> DeleteVoiceResultCdto:
        """Soft-delete a voice folder; refuses when any drama's casting.md
        still binds this voice to a role (mirrors actor follow-up 043)."""
        validate_voice_id(voice_id)
        assignments = self._casting.find_voice_assignments_for_voice(voice_id)
        if assignments:
            raise VoiceAlreadyAssignedError(voice_id=voice_id, assignments=assignments)
        move = self._pool.delete_voice(voice_id)
        return DeleteVoiceResultCdto(
            src_rel=str(move["from"]),
            dst_rel=str(move["to"]),
        )

    def upload_audio(
        self, voice_id: str, data: bytes, filename: str
    ) -> UploadVoiceAudioResultCdto:
        validate_voice_id(voice_id)
        result = self._pool.upload_audio(voice_id, data, filename)
        return UploadVoiceAudioResultCdto(
            voice_id=str(result["voice_id"]),
            audio_path=str(result["audio_path"]),
            byte_size=int(result["byte_size"]),
        )

    def extract_audio(self, voice_id: str) -> ExtractVoiceAudioResultCdto:
        """Extract mp3 from every `*.mp4` the user manually dropped into the
        voice folder; the lex-last mp4 wins as the persisted sample."""
        validate_voice_id(voice_id)
        result = self._pool.extract_audio_from_mp4s(voice_id)
        return ExtractVoiceAudioResultCdto(
            voice_id=str(result["voice_id"]),
            audio_path=str(result["audio_path"]),
            extracted=list(result.get("extracted", []) or []),  # type: ignore[arg-type]
            failures=list(result.get("failures", []) or []),  # type: ignore[arg-type]
        )
