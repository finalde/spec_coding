from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


ALLOWED_EXTENSIONS: frozenset[str] = frozenset({".md", ".yaml", ".yml", ".json", ".jsonl"})

_STAGE_FOLDERS: tuple[str, ...] = (
    "user_input",
    "interview",
    "findings",
    "final_specs",
    "validation",
)


@dataclass(frozen=True)
class ExposedTree:
    repo_root: Path

    def is_inside(self, abs_path: Path) -> bool:
        try:
            rel = abs_path.resolve().relative_to(self.repo_root.resolve())
        except ValueError:
            return False
        parts = rel.parts
        if len(parts) == 0:
            return False
        if parts == ("CLAUDE.md",):
            return True
        if (
            len(parts) == 3
            and parts[0] == ".claude"
            and parts[1] == "agents"
            and parts[2].endswith(".md")
        ):
            return True
        if (
            len(parts) >= 4
            and parts[0] == ".claude"
            and parts[1] == "skills"
            and parts[-1] == "SKILL.md"
        ):
            return True
        if (
            len(parts) >= 4
            and parts[0] == ".claude"
            and parts[1] == "agent_refs"
            and parts[-1].endswith(".md")
        ):
            return True
        if len(parts) >= 5 and parts[0] == "specs":
            stage = parts[3]
            if stage not in _STAGE_FOLDERS:
                return False
            return True
        return False
