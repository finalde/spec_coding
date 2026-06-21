"""DTOs for the episode-BGM aggregate (read cues + burn result).

Qdto carries the parsed cue timeline + the source/output status the UI needs to
render the arrangement panel; Cdto carries the burn outcome (output path + which
cues were used / skipped). Both are thin envelopes over the infrastructure
result payload — the application seam the route depends on."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EpisodeBgmReadQdto:
    payload: dict[str, object]

    def to_payload(self) -> dict[str, object]:
        return self.payload


@dataclass(frozen=True)
class BurnEpisodeBgmResultCdto:
    payload: dict[str, object]

    def to_payload(self) -> dict[str, object]:
        return self.payload
