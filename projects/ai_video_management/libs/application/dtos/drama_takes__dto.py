"""DramaTakes-aggregate DTO: result of locking every episode's takes in one
drama-wide 定版 pass. Cdto only — no Qdto."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class EpisodeTakesOutcomeCdto:
    episode: str
    episode_rel: str
    ok: bool
    selected: int
    skipped: int
    reason: str | None

    def to_payload(self) -> dict[str, Any]:
        return {
            "episode": self.episode,
            "episode_rel": self.episode_rel,
            "ok": self.ok,
            "selected": self.selected,
            "skipped": self.skipped,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class DramaTakesResultCdto:
    drama_rel: str
    outcomes: tuple[EpisodeTakesOutcomeCdto, ...]

    def to_payload(self) -> dict[str, Any]:
        return {
            "drama": self.drama_rel,
            "outcomes": [o.to_payload() for o in self.outcomes],
        }
