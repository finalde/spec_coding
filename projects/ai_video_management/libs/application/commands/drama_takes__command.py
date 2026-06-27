"""DramaTakes-aggregate command: drama-wide 定版 (lock every episode's takes).
Thin application seam over DramaTakesSelector."""
from __future__ import annotations

from libs.application.dtos.drama_takes__dto import DramaTakesResultCdto
from libs.application.mappers.drama_takes__mapper import DramaTakesMapper
from libs.infrastructure.writers.drama_takes__writer import DramaTakesSelector


class DramaTakesCommand:
    def __init__(self, selector: DramaTakesSelector) -> None:
        self._selector = selector

    def select_all(self, rel_path: str) -> DramaTakesResultCdto:
        return DramaTakesMapper.to_cdto(self._selector.select_all(rel_path))
