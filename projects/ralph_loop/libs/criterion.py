from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .checks import Check, NaturalCheck, ScriptCheck


@dataclass(frozen=True)
class Criterion:
    criterion: str  # what must be true
    check: Check    # how Claude Code will verify it

    @classmethod
    def _from_dict(cls, data: dict[str, Any]) -> Criterion:
        criterion: str = (data.get("criterion") or "").strip()
        if not criterion:
            raise ValueError("Each criterion must have a non-empty 'criterion' field")
        check_data: dict[str, Any] | None = data.get("check")
        if not check_data:
            raise ValueError(
                f"Criterion '{criterion}' has no 'check' — all criteria must be verifiable"
            )
        check_type: str = (check_data.get("type") or "").strip()
        if check_type == "script":
            run: str = (check_data.get("run") or "").strip()
            if not run:
                raise ValueError(f"Script check for '{criterion}' has no 'run' command")
            return cls(criterion=criterion, check=ScriptCheck(run=run))
        if check_type == "natural":
            description: str = (check_data.get("description") or "").strip()
            if not description:
                raise ValueError(f"Natural check for '{criterion}' has no 'description'")
            return cls(criterion=criterion, check=NaturalCheck(description=description))
        raise ValueError(
            f"Unknown check type '{check_type}' for criterion '{criterion}'. "
            "Must be 'script' or 'natural'."
        )
