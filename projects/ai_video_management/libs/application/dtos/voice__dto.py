"""Voice-aggregate DTOs: queries' Qdtos + commands' Cdtos.

Per follow-up 114 pattern: input Cdtos validate themselves in __post_init__
so neither the Command nor the Query has to re-run the same validate_*
calls. Constructing a `GenerateVoicesInputCdto(**body.model_dump())`
either yields a valid value or raises a domain error.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from libs.domain.value_objects.voice__valueobject import (
    VoiceAttrs,
    validate_batch_count,
    validate_seeds,
)


# --- Query DTOs -------------------------------------------------------------


@dataclass(frozen=True)
class VoiceListRowQdto:
    voice_id: str
    sidecar_path: str
    audio_path: str | None
    mtime: float
    archetype: str
    archetype_label: str
    gender: str
    age_impression: str
    pace: str
    pitch_register: str
    emotion_default: str
    tone: str
    signature_inflection: str
    notes: str
    is_assigned: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.voice_id,
            "sidecar_path": self.sidecar_path,
            "audio_path": self.audio_path,
            "mtime": self.mtime,
            "archetype": self.archetype,
            "archetype_label": self.archetype_label,
            "gender": self.gender,
            "age_impression": self.age_impression,
            "pace": self.pace,
            "pitch_register": self.pitch_register,
            "emotion_default": self.emotion_default,
            "tone": self.tone,
            "signature_inflection": self.signature_inflection,
            "notes": self.notes,
            "is_assigned": self.is_assigned,
        }


@dataclass(frozen=True)
class VoiceListQdto:
    voices: tuple[VoiceListRowQdto, ...]

    def to_payload(self) -> dict[str, Any]:
        return {"voices": [v.to_dict() for v in self.voices]}


@dataclass(frozen=True)
class VoicePreviewPromptQdto:
    seed: int
    prompt: str
    archetype: str | None = None
    archetype_label: str | None = None
    attrs: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {"seed": self.seed, "prompt": self.prompt}
        if self.archetype is not None:
            out["archetype"] = self.archetype
        if self.archetype_label is not None:
            out["archetype_label"] = self.archetype_label
        if self.attrs is not None:
            out["attrs"] = self.attrs
        return out


@dataclass(frozen=True)
class VoicePreviewPromptsQdto:
    prompts: tuple[VoicePreviewPromptQdto, ...]

    def to_payload(self) -> dict[str, Any]:
        return {"prompts": [p.to_dict() for p in self.prompts]}


@dataclass(frozen=True)
class VoiceAssignmentsQdto:
    voice_id: str
    assignments: list[dict[str, Any]]

    def to_payload(self) -> dict[str, Any]:
        return {"voice_id": self.voice_id, "assignments": self.assignments}


# --- Command DTOs -----------------------------------------------------------


@dataclass(frozen=True)
class GenerateVoicesInputCdto:
    count: int
    archetype: str
    gender: str
    age_impression: str
    pace: str = "medium"
    pitch_register: str = "mid"
    emotion_default: str = "calm"
    tone: str = ""
    signature_inflection: str = ""
    notes: str = ""
    seeds: list[int] | None = None
    batch_seed: int | None = None
    batch_size: int | None = None
    slot_index: int | None = None

    def __post_init__(self) -> None:
        # Constructing VoiceAttrs runs its own __post_init__ validation.
        VoiceAttrs(
            archetype=self.archetype,
            gender=self.gender,
            age_impression=self.age_impression,
            pace=self.pace,
            pitch_register=self.pitch_register,
            emotion_default=self.emotion_default,
            tone=self.tone,
            signature_inflection=self.signature_inflection,
            notes=self.notes,
        )
        validate_batch_count(self.count)
        validate_seeds(self.seeds, self.count)


@dataclass(frozen=True)
class GenerateDiverseVoicesInputCdto:
    count: int
    gender: str
    age_impression: str | None = None
    notes: str = ""

    def __post_init__(self) -> None:
        validate_batch_count(self.count)


@dataclass(frozen=True)
class GenerateVoicesResultCdto:
    generated: list[dict[str, Any]]
    errors: list[dict[str, str]]

    def to_payload(self) -> dict[str, Any]:
        return {"generated": list(self.generated), "errors": list(self.errors)}


@dataclass(frozen=True)
class DeleteVoiceResultCdto:
    src_rel: str
    dst_rel: str

    def to_payload(self) -> dict[str, Any]:
        return {"from": self.src_rel, "to": self.dst_rel}


@dataclass(frozen=True)
class UploadVoiceAudioResultCdto:
    voice_id: str
    audio_path: str
    byte_size: int

    def to_payload(self) -> dict[str, Any]:
        return {
            "voice_id": self.voice_id,
            "audio_path": self.audio_path,
            "byte_size": self.byte_size,
        }


@dataclass(frozen=True)
class ExtractVoiceAudioResultCdto:
    voice_id: str
    audio_path: str
    extracted: list[dict[str, Any]]
    failures: list[dict[str, str]]

    def to_payload(self) -> dict[str, Any]:
        return {
            "voice_id": self.voice_id,
            "audio_path": self.audio_path,
            "extracted": list(self.extracted),
            "failures": list(self.failures),
        }
