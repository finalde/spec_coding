"""Repository Protocol for the Voice aggregate. Concrete implementation
lives in libs/infrastructure/writers/voice__writer.py — the domain only
sees this interface (dependency-inversion seam per development.md §2).

Per spec follow-up 115: voice generation is purely local text composition.
The Protocol intentionally has NO method that touches external HTTP /
provider credentials — that posture is part of the contract."""
from __future__ import annotations

from pathlib import Path
from typing import Protocol, TYPE_CHECKING

from libs.domain.value_objects.voice__valueobject import VoiceAttrs

if TYPE_CHECKING:
    from libs.infrastructure.writers.voice__writer import VoiceInfo


class VoiceRepository(Protocol):
    """Read-and-write surface for AI-generated voice profile prompts.
    Implemented by `libs.infrastructure.writers.voice__writer.VoicePool`."""

    def voice_exists(self, voice_id: str) -> bool: ...

    def list_voices(self) -> "list[VoiceInfo]": ...

    def voice_audio_filename(self, voice_id: str) -> str | None: ...

    def voices_dir(self) -> Path: ...

    def delete_voice(self, voice_id: str) -> dict[str, str]: ...

    def generate_batch(
        self,
        attrs: VoiceAttrs,
        count: int,
        seeds: list[int] | None,
        batch_seed: int | None = None,
        batch_size: int | None = None,
        slot_index: int | None = None,
    ) -> object: ...

    def preview_prompts(
        self,
        attrs: VoiceAttrs,
        count: int,
        seeds: list[int] | None = None,
        batch_seed: int | None = None,
        batch_size: int | None = None,
        slot_index: int | None = None,
    ) -> dict[str, object]: ...

    def generate_diverse_batch(
        self,
        gender: str,
        age_impression: str | None,
        count: int,
        notes: str,
    ) -> object: ...

    def preview_diverse_prompts(
        self,
        gender: str,
        age_impression: str | None,
        count: int,
        notes: str,
    ) -> dict[str, object]: ...

    def upload_audio(self, voice_id: str, data: bytes, filename: str) -> dict[str, str]: ...

    def extract_audio_from_mp4s(self, voice_id: str) -> dict[str, object]: ...
