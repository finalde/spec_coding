"""VoiceMapper — DAO↔Qdto/Cdto translation for the voice pool."""
from __future__ import annotations

from libs.application.dtos.voice__dto import (
    GenerateVoicesResultCdto,
    VoiceListQdto,
    VoiceListRowQdto,
    VoicePreviewPromptQdto,
    VoicePreviewPromptsQdto,
)
from libs.domain.value_objects.voice__valueobject import ARCHETYPE_LABELS_ZH
from libs.infrastructure.writers.voice__writer import GenerateResult, VoiceInfo


class VoiceMapper:
    @staticmethod
    def info_to_qdto(info: VoiceInfo, is_assigned: bool = False) -> VoiceListRowQdto:
        return VoiceListRowQdto(
            voice_id=info.id,
            sidecar_path=info.sidecar_path,
            audio_path=info.audio_path,
            mtime=info.mtime,
            archetype=info.attrs.archetype,
            archetype_label=ARCHETYPE_LABELS_ZH.get(info.attrs.archetype, info.attrs.archetype),
            gender=info.attrs.gender,
            age_impression=info.attrs.age_impression,
            pace=info.attrs.pace,
            pitch_register=info.attrs.pitch_register,
            emotion_default=info.attrs.emotion_default,
            tone=info.attrs.tone,
            signature_inflection=info.attrs.signature_inflection,
            notes=info.attrs.notes,
            is_assigned=is_assigned,
        )

    @staticmethod
    def list_to_qdto(
        infos: list[VoiceInfo], assigned_ids: set[str] | None = None
    ) -> VoiceListQdto:
        ids = assigned_ids or set()
        return VoiceListQdto(
            voices=tuple(VoiceMapper.info_to_qdto(i, is_assigned=i.id in ids) for i in infos)
        )

    @staticmethod
    def generate_to_cdto(r: GenerateResult) -> GenerateVoicesResultCdto:
        return GenerateVoicesResultCdto(generated=list(r.generated), errors=list(r.errors))

    @staticmethod
    def preview_to_qdto(raw: dict[str, object]) -> VoicePreviewPromptsQdto:
        prompts_in = raw.get("prompts", [])
        prompts: list[VoicePreviewPromptQdto] = []
        if isinstance(prompts_in, list):
            for entry in prompts_in:
                if not isinstance(entry, dict):
                    continue
                seed = entry.get("seed")
                prompt = entry.get("prompt")
                if not (isinstance(seed, int) and isinstance(prompt, str)):
                    continue
                archetype = entry.get("archetype")
                archetype_label = entry.get("archetype_label")
                attrs = entry.get("attrs")
                prompts.append(
                    VoicePreviewPromptQdto(
                        seed=seed,
                        prompt=prompt,
                        archetype=archetype if isinstance(archetype, str) else None,
                        archetype_label=archetype_label if isinstance(archetype_label, str) else None,
                        attrs=attrs if isinstance(attrs, dict) else None,
                    )
                )
        return VoicePreviewPromptsQdto(prompts=tuple(prompts))
