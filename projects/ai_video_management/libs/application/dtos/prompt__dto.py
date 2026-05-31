"""DTOs for the Prompt (suggestion) aggregate — follow-up 117.

`SuggestRefinementsInputQdto` carries the per-dimension refinement request
from the route into `PromptQuery`; `SuggestRefinementsQdto` carries the
LLM-produced suggestions back out to the route as a JSON payload.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from libs.domain.errors.prompt__error import InvalidSuggestionRequestError

MAX_COUNT = 6
MIN_COUNT = 1


@dataclass(frozen=True)
class SuggestRefinementsInputQdto:
    """One request for refinement options on a single shot-prompt dimension.

    - `dimension`: the field label being refined (e.g. `镜头` / `光线 / 色调`).
    - `current_value`: what that field currently holds (may be empty / a stub).
    - `shot_context`: the surrounding shot markdown (小说原文 + Shot context +
      reference handles) — gives the model the dramatic beat to write toward.
    - `prompt_body`: the full current code-block body, so suggestions stay
      consistent with the other already-filled dimensions.
    """

    dimension: str
    current_value: str = ""
    shot_context: str = ""
    prompt_body: str = ""
    drama: str | None = None
    scene: str | None = None
    count: int = 4

    def __post_init__(self) -> None:
        if not self.dimension.strip():
            raise InvalidSuggestionRequestError("dimension 不能为空")
        if not (MIN_COUNT <= self.count <= MAX_COUNT):
            raise InvalidSuggestionRequestError(
                f"count 必须在 {MIN_COUNT}–{MAX_COUNT} 之间，收到 {self.count}"
            )


@dataclass(frozen=True)
class RefinementSuggestionQdto:
    """One refinement option: the text to merge + a one-line rationale."""

    value: str
    rationale: str

    def to_dict(self) -> dict[str, Any]:
        return {"value": self.value, "rationale": self.rationale}


@dataclass(frozen=True)
class SuggestRefinementsQdto:
    dimension: str
    suggestions: tuple[RefinementSuggestionQdto, ...]

    def to_payload(self) -> dict[str, Any]:
        return {
            "dimension": self.dimension,
            "suggestions": [s.to_dict() for s in self.suggestions],
        }
