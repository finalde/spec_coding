from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

ALLOWED_EXTENSIONS: frozenset[str] = frozenset({".md", ".yaml", ".yml", ".json", ".jsonl"})

STAGE_SUBFOLDERS: tuple[str, ...] = (
    "user_input",
    "interview",
    "findings",
    "final_specs",
    "validation",
)


@dataclass(frozen=True)
class ExposedTree:
    repo_root: Path

    def claude_md(self) -> Path:
        return (self.repo_root / "CLAUDE.md").resolve()

    def agent_files(self) -> list[Path]:
        agents_dir = (self.repo_root / ".claude" / "agents").resolve()
        if not agents_dir.is_dir():
            return []
        return sorted(
            (p.resolve() for p in agents_dir.glob("*.md") if p.is_file() and not p.is_symlink()),
            key=lambda p: p.name.lower(),
        )

    def skill_files(self) -> list[Path]:
        skills_dir = (self.repo_root / ".claude" / "skills").resolve()
        if not skills_dir.is_dir():
            return []
        results: list[Path] = []
        for entry in sorted(skills_dir.iterdir(), key=lambda p: p.name.lower()):
            if not entry.is_dir() or entry.is_symlink():
                continue
            skill_md = entry / "SKILL.md"
            if skill_md.is_file() and not skill_md.is_symlink():
                results.append(skill_md.resolve())
        return results

    def specs_root(self) -> Path:
        return (self.repo_root / "specs").resolve()

    def is_inside(self, path: Path) -> bool:
        try:
            resolved = path.resolve()
        except (OSError, RuntimeError):
            return False
        if resolved == self.claude_md() and resolved.exists():
            return True
        if resolved in self.agent_files():
            return True
        if resolved in self.skill_files():
            return True
        specs_root = self.specs_root()
        if not specs_root.exists():
            return False
        try:
            relative = resolved.relative_to(specs_root)
        except ValueError:
            return False
        parts = relative.parts
        if len(parts) < 4:
            return False
        if parts[2] not in STAGE_SUBFOLDERS:
            return False
        if resolved.suffix.lower() not in ALLOWED_EXTENSIONS:
            return False
        return True
