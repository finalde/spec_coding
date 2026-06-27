"""EpisodeTakes-aggregate DTO: result of locking each shot's selected take
(newest renders/ mp4 copied to shot{NN}.mp4). Cdto only — no Qdto."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class TakeSelectionCdto:
    shot: str
    src_rel: str
    out_rel: str

    def to_payload(self) -> dict[str, Any]:
        return {"shot": self.shot, "src": self.src_rel, "out": self.out_rel}


@dataclass(frozen=True)
class TakeSkipCdto:
    shot: str
    reason: str

    def to_payload(self) -> dict[str, Any]:
        return {"shot": self.shot, "reason": self.reason}


@dataclass(frozen=True)
class SelectTakesResultCdto:
    episode_rel: str
    selected: tuple[TakeSelectionCdto, ...]
    skipped: tuple[TakeSkipCdto, ...]

    def to_payload(self) -> dict[str, Any]:
        return {
            "episode": self.episode_rel,
            "selected": [s.to_payload() for s in self.selected],
            "skipped": [s.to_payload() for s in self.skipped],
        }
