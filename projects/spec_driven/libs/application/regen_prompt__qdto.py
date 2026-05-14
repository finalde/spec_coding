from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RegenPromptQdto:
    prompt: str
    warning: dict[str, Any] | None
    selected_stages_count: int
    follow_ups_count: int
    autonomous: bool
    bytes_len: int

    def to_payload(self) -> dict[str, Any]:
        return {
            "prompt": self.prompt,
            "warning": self.warning,
            "selected_stages_count": self.selected_stages_count,
            "follow_ups_count": self.follow_ups_count,
            "autonomous": self.autonomous,
            "bytes": self.bytes_len,
        }
