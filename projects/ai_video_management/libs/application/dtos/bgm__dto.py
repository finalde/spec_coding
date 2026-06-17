"""Bgm-aggregate DTOs: queries' Qdtos + commands' Cdtos.

Input Cdtos validate themselves in __post_init__ (actor/voice follow-up 114
pattern) so neither the Command nor the Query re-runs validation. Building a
`GenerateBgmsInputCdto(**body.model_dump())` either yields a valid value or
raises a domain error.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from libs.domain.value_objects.bgm__valueobject import (
    BgmAttrs,
    validate_batch_count,
    validate_seeds,
)


# --- Query DTOs -------------------------------------------------------------


@dataclass(frozen=True)
class BgmListRowQdto:
    bgm_id: str
    category: str
    category_label: str
    sidecar_path: str
    audio_path: str | None
    seed: int
    mtime: float
    mood: str
    bpm: int
    duration: int
    loopable: bool
    intensity: int
    instruments: str
    notes: str
    is_referenced: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.bgm_id,
            "category": self.category,
            "category_label": self.category_label,
            "sidecar_path": self.sidecar_path,
            "audio_path": self.audio_path,
            "seed": self.seed,
            "mtime": self.mtime,
            "mood": self.mood,
            "bpm": self.bpm,
            "duration": self.duration,
            "loopable": self.loopable,
            "intensity": self.intensity,
            "instruments": self.instruments,
            "notes": self.notes,
            "is_referenced": self.is_referenced,
        }


@dataclass(frozen=True)
class BgmListQdto:
    bgms: tuple[BgmListRowQdto, ...]

    def to_payload(self) -> dict[str, Any]:
        return {"bgms": [b.to_dict() for b in self.bgms]}


@dataclass(frozen=True)
class BgmPreviewPromptQdto:
    seed: int
    prompt: str
    category: str | None = None
    category_label: str | None = None
    attrs: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {"seed": self.seed, "prompt": self.prompt}
        if self.category is not None:
            out["category"] = self.category
        if self.category_label is not None:
            out["category_label"] = self.category_label
        if self.attrs is not None:
            out["attrs"] = self.attrs
        return out


@dataclass(frozen=True)
class BgmPreviewPromptsQdto:
    prompts: tuple[BgmPreviewPromptQdto, ...]

    def to_payload(self) -> dict[str, Any]:
        return {"prompts": [p.to_dict() for p in self.prompts]}


@dataclass(frozen=True)
class BgmReferencesQdto:
    bgm_id: str
    references: list[dict[str, Any]]

    def to_payload(self) -> dict[str, Any]:
        return {"bgm_id": self.bgm_id, "references": self.references}


# --- Command DTOs -----------------------------------------------------------


@dataclass(frozen=True)
class GenerateBgmsInputCdto:
    count: int
    category: str
    mood: str = ""
    bpm: int = 90
    duration: int = 30
    loopable: bool = False
    intensity: int = 3
    instruments: str = ""
    notes: str = ""
    seeds: list[int] | None = None
    batch_seed: int | None = None
    batch_size: int | None = None
    slot_index: int | None = None

    def __post_init__(self) -> None:
        # Constructing BgmAttrs runs its own __post_init__ validation.
        BgmAttrs(
            category=self.category,
            mood=self.mood,
            bpm=self.bpm,
            duration=self.duration,
            loopable=self.loopable,
            intensity=self.intensity,
            instruments=self.instruments,
            notes=self.notes,
        )
        validate_batch_count(self.count)
        validate_seeds(self.seeds, self.count)


@dataclass(frozen=True)
class GenerateBgmsResultCdto:
    generated: list[dict[str, Any]]
    errors: list[dict[str, str]]

    def to_payload(self) -> dict[str, Any]:
        return {"generated": list(self.generated), "errors": list(self.errors)}


@dataclass(frozen=True)
class DeleteBgmResultCdto:
    src_rel: str
    dst_rel: str

    def to_payload(self) -> dict[str, Any]:
        return {"from": self.src_rel, "to": self.dst_rel}


@dataclass(frozen=True)
class BgmAudioResultCdto:
    """Result of a per-track audio op (local GPU generate or Downloads import)."""
    bgm_id: str
    audio_path: str
    imported_from: str | None = None

    def to_payload(self) -> dict[str, Any]:
        out: dict[str, Any] = {"id": self.bgm_id, "audio_path": self.audio_path}
        if self.imported_from is not None:
            out["imported_from"] = self.imported_from
        return out
