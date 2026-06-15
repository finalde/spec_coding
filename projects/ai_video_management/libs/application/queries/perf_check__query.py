"""Perf-check query: assemble the copy-paste prompt that has Claude check a
downloaded MP4 for a performance-library entry and score it."""
from __future__ import annotations

from libs.infrastructure.readers.perf_check__reader import PerfCheckPromptReader


class PerfCheckPromptQuery:
    def __init__(self, reader: PerfCheckPromptReader) -> None:
        self._reader = reader

    def build(self, rel_path: str) -> dict[str, object]:
        return self._reader.build(rel_path)
