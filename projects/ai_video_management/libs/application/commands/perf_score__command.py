"""Perf-score command: apply a 你/Claude review score to a perf entry and
return the recomputed combined verdict."""
from __future__ import annotations

from libs.infrastructure.writers.perf_score__writer import PerfScorer


class PerfScoreCommand:
    def __init__(self, scorer: PerfScorer) -> None:
        self._scorer = scorer

    def apply(self, rel_path: str, who: str, da_yi: int | None,
              qing_xu: int | None, guo_huo: int | None, note: str) -> dict[str, str]:
        return self._scorer.apply(rel_path, who, da_yi, qing_xu, guo_huo, note)
