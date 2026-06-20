"""Shot-regen query: assemble the copy-paste regeneration prompt for a shot
that references the performance library."""
from __future__ import annotations

from libs.infrastructure.readers.shot_regen__reader import ShotRegenPromptReader


class ShotRegenPromptQuery:
    def __init__(self, reader: ShotRegenPromptReader) -> None:
        self._reader = reader

    def build(
        self,
        rel_shot_path: str,
        selected_perf_ids: list[str] | None = None,
    ) -> dict[str, object]:
        return self._reader.build(rel_shot_path, selected_perf_ids)
