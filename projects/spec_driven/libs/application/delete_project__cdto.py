from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class DeleteProjectCdto:
    project_type: str
    project_name: str
    deleted_paths: tuple[str, ...]
    not_found_paths: tuple[str, ...]

    def to_payload(self) -> dict[str, Any]:
        return {
            "project_type": self.project_type,
            "project_name": self.project_name,
            "deleted_paths": list(self.deleted_paths),
            "not_found_paths": list(self.not_found_paths),
        }
