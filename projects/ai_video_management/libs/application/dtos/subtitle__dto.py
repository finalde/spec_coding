"""Subtitle-aggregate DTOs: burn / scaffold result Cdtos (no Qdtos)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class BurnSubtitlesResultCdto:
    src_rel: str
    out_rel: str
    cue_count: int
    lang: str

    def to_payload(self) -> dict[str, Any]:
        return {
            "src": self.src_rel,
            "out": self.out_rel,
            "cues": self.cue_count,
            "lang": self.lang,
        }


@dataclass(frozen=True)
class ScaffoldSubtitlesResultCdto:
    md_rel: str
    cue_count: int
    created: bool

    def to_payload(self) -> dict[str, Any]:
        return {
            "path": self.md_rel,
            "cues": self.cue_count,
            "created": self.created,
        }
