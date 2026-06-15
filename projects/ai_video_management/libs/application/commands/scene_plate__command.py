"""Scene-plate command: extract per-direction background plates from a scene
walk-through mp4 into the scene's `bg{N}_{方位}_` folders.

Thin application-layer wrapper; the direction→timepoint schedule and the
ffmpeg subprocess live in infrastructure (`scene_plate__writer.py`). The
extractor's `ScenePlateResult` is already a payload-shaped boundary object,
so no separate mapper/dto is needed.
"""
from __future__ import annotations

from libs.infrastructure.writers.scene_plate__writer import (
    ScenePlateExtractor,
    ScenePlateResult,
)


class ScenePlateCommand:
    def __init__(self, extractor: ScenePlateExtractor) -> None:
        self._extractor = extractor

    def extract(self, rel_path: str) -> ScenePlateResult:
        return self._extractor.extract(rel_path)
