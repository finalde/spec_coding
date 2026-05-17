"""DramaPath value object — canonical form `ai_videos/{drama}` with
validation. Used by every operation that operates on a single drama.
"""
from __future__ import annotations

from dataclasses import dataclass

from libs.domain.errors.casting__error import InvalidDramaPathError


@dataclass(frozen=True)
class DramaPath:
    rel: str

    def __post_init__(self) -> None:
        if not isinstance(self.rel, str) or self.rel == "":
            raise InvalidDramaPathError("path is empty")
        normalized = self.rel.rstrip("/")
        parts = normalized.split("/")
        if len(parts) != 2 or parts[0] != "ai_videos" or parts[1] == "":
            raise InvalidDramaPathError("path must be 'ai_videos/{drama}'")
        object.__setattr__(self, "rel", normalized)

    @property
    def drama_name(self) -> str:
        return self.rel.split("/", 1)[1]
