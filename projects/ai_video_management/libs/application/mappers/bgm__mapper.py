"""BgmMapper — DAO↔Qdto/Cdto translation for the bgm pool."""
from __future__ import annotations

from libs.application.dtos.bgm__dto import (
    BgmAudioResultCdto,
    BgmListQdto,
    BgmListRowQdto,
    BgmPreviewPromptQdto,
    BgmPreviewPromptsQdto,
    GenerateBgmsResultCdto,
)
from libs.domain.value_objects.bgm__valueobject import CATEGORY_LABELS_ZH
from libs.infrastructure.writers.bgm__writer import BgmInfo, GenerateResult


class BgmMapper:
    @staticmethod
    def info_to_qdto(info: BgmInfo, is_referenced: bool = False) -> BgmListRowQdto:
        return BgmListRowQdto(
            bgm_id=info.id,
            category=info.category,
            category_label=CATEGORY_LABELS_ZH.get(info.category, info.category),
            sidecar_path=info.sidecar_path,
            audio_path=info.audio_path,
            seed=info.seed,
            mtime=info.mtime,
            mood=info.attrs.mood,
            bpm=info.attrs.bpm,
            duration=info.attrs.duration,
            loopable=info.attrs.loopable,
            intensity=info.attrs.intensity,
            instruments=info.attrs.instruments,
            notes=info.attrs.notes,
            is_referenced=is_referenced,
        )

    @staticmethod
    def list_to_qdto(
        infos: list[BgmInfo], referenced_ids: set[str] | None = None
    ) -> BgmListQdto:
        ids = referenced_ids or set()
        return BgmListQdto(
            bgms=tuple(BgmMapper.info_to_qdto(i, is_referenced=i.id in ids) for i in infos)
        )

    @staticmethod
    def generate_to_cdto(r: GenerateResult) -> GenerateBgmsResultCdto:
        return GenerateBgmsResultCdto(generated=list(r.generated), errors=list(r.errors))

    @staticmethod
    def audio_to_cdto(raw: dict[str, object]) -> BgmAudioResultCdto:
        imported = raw.get("from")
        return BgmAudioResultCdto(
            bgm_id=str(raw.get("id", "")),
            audio_path=str(raw.get("audio_path", "")),
            imported_from=str(imported) if isinstance(imported, str) else None,
        )

    @staticmethod
    def preview_to_qdto(raw: dict[str, object]) -> BgmPreviewPromptsQdto:
        prompts_in = raw.get("prompts", [])
        prompts: list[BgmPreviewPromptQdto] = []
        if isinstance(prompts_in, list):
            for entry in prompts_in:
                if not isinstance(entry, dict):
                    continue
                seed = entry.get("seed")
                prompt = entry.get("prompt")
                if not (isinstance(seed, int) and isinstance(prompt, str)):
                    continue
                category = entry.get("category")
                category_label = entry.get("category_label")
                attrs = entry.get("attrs")
                prompts.append(
                    BgmPreviewPromptQdto(
                        seed=seed,
                        prompt=prompt,
                        category=category if isinstance(category, str) else None,
                        category_label=category_label if isinstance(category_label, str) else None,
                        attrs=attrs if isinstance(attrs, dict) else None,
                    )
                )
        return BgmPreviewPromptsQdto(prompts=tuple(prompts))
