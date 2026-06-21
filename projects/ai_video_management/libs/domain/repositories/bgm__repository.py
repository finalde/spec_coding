"""Repository Protocol for the Bgm aggregate. Concrete implementation lives
in libs/infrastructure/writers/bgm__writer.py — the domain only sees this
interface (dependency-inversion seam per development.md §2).

Unlike the voice pool (pure-local composition), BGM generation shells out to
a self-hosted Stable Audio tool (`tools/stableaudio_gen.py`) via subprocess,
so `generate_batch` can fail with `StableAudio*Error`. The torch / GPU
dependency lives entirely in that tool, never in the webapp process."""
from __future__ import annotations

from pathlib import Path
from typing import Protocol, TYPE_CHECKING

from libs.domain.value_objects.bgm__valueobject import BgmAttrs

if TYPE_CHECKING:
    from libs.infrastructure.writers.bgm__writer import BgmInfo


class BgmRepository(Protocol):
    """Read-and-write surface for AI-generated background-music tracks.
    Implemented by `libs.infrastructure.writers.bgm__writer.BgmPool`."""

    def bgm_exists(self, bgm_id: str) -> bool: ...

    def list_bgms(self) -> "list[BgmInfo]": ...

    def bgm_audio_filename(self, bgm_id: str) -> str | None: ...

    def audio_path_for(self, bgm_id: str) -> Path | None: ...

    def bgm_dir(self) -> Path: ...

    def delete_bgm(self, bgm_id: str) -> dict[str, str]: ...

    def generate_batch(
        self,
        attrs: BgmAttrs,
        count: int,
        seeds: list[int] | None,
        batch_seed: int | None = None,
        batch_size: int | None = None,
        slot_index: int | None = None,
    ) -> object: ...

    def create_prompts_batch(
        self,
        attrs: BgmAttrs,
        count: int,
        seeds: list[int] | None,
        batch_seed: int | None = None,
        batch_size: int | None = None,
        slot_index: int | None = None,
    ) -> object: ...

    def generate_audio(self, bgm_id: str) -> dict[str, object]: ...

    def import_audio(self, bgm_id: str) -> dict[str, object]: ...

    def preview_prompts(
        self,
        attrs: BgmAttrs,
        count: int,
        seeds: list[int] | None = None,
        batch_seed: int | None = None,
        batch_size: int | None = None,
        slot_index: int | None = None,
    ) -> dict[str, object]: ...
