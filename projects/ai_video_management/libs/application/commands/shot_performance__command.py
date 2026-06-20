"""Shot-performance command: persist a shot's chosen performance-library
references (the `表演库参考:` annotation group) back into its shot.md."""
from __future__ import annotations

from libs.infrastructure.writers.shot_performance__writer import (
    ShotPerformanceWriteResult,
    ShotPerformanceWriter,
)


class ShotPerformanceCommand:
    def __init__(self, writer: ShotPerformanceWriter) -> None:
        self._writer = writer

    def set_refs(
        self,
        shot_path: str,
        perf_ids: list[str],
        mtime: str | None = None,
    ) -> ShotPerformanceWriteResult:
        return self._writer.write(shot_path, perf_ids, mtime)
