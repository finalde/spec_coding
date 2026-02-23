from __future__ import annotations

import yaml
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Config:
    """Runtime configuration loaded from a project's config.yml."""

    project_name: str
    output_dir: Path  # where generated project files are written

    @classmethod
    def from_file(cls, path: str | Path) -> Config:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Config file not found: {p}")
        project_name: str = p.parent.name
        data: dict[str, Any] = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        raw: str = (data.get("output_dir") or f"projects/{project_name}").strip()
        return cls(project_name=project_name, output_dir=Path(raw))

    @classmethod
    def default(cls, project_name: str) -> Config:
        """Return a Config with all defaults (no file required)."""
        return cls(project_name=project_name, output_dir=Path(f"projects/{project_name}"))
