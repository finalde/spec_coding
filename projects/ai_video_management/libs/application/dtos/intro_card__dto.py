"""Intro-card-aggregate DTOs: burn result Cdto."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class BurnIntroCardsResultCdto:
    src_rel: str
    out_rel: str
    card_count: int
    names: tuple[str, ...]

    def to_payload(self) -> dict[str, Any]:
        return {
            "src": self.src_rel,
            "out": self.out_rel,
            "cards": self.card_count,
            "names": list(self.names),
        }
