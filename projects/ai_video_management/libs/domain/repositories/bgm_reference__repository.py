"""Repository Protocol for BGM references — the reverse-lookup surface that
answers "which dramas reference this track?".

BGM cue references live in per-episode / per-short `bgm.md` timelines (the
analog of casting.md for actors/voices). Concrete implementation lives in
libs/infrastructure/readers/bgm_reference__reader.py."""
from __future__ import annotations

from typing import Protocol


class BgmReferenceRepository(Protocol):
    """Read surface over every drama's `bgm.md` cue timeline(s). Implemented
    by `libs.infrastructure.readers.bgm_reference__reader.BgmReferenceReader`."""

    def find_references_for_bgm(self, bgm_id: str) -> list[dict[str, object]]:
        """Every drama/location whose bgm.md references this track id, as
        `[{drama, location, cue_lines}, ...]` sorted by (drama, location)."""
        ...

    def referenced_bgm_ids(self) -> set[str]:
        """Single-pass union of every `bgm_NNNN` token across all bgm.md."""
        ...
