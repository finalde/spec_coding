from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    repo_root: Path
    specs_root: Path
    audit_root: Path
    projects_root: Path
    ai_videos_root: Path
    claude_md: Path
    max_concurrent_runs: int = 3

    @classmethod
    def from_repo_root(cls, repo_root: Path) -> "Settings":
        repo_root = repo_root.resolve()
        return cls(
            repo_root=repo_root,
            specs_root=repo_root / "specs",
            audit_root=repo_root / ".audit" / "adhoc_agents",
            projects_root=repo_root / "projects",
            ai_videos_root=repo_root / "ai_videos",
            claude_md=repo_root / "CLAUDE.md",
        )

    def ensure_dirs(self) -> None:
        for d in (self.specs_root, self.audit_root, self.projects_root, self.ai_videos_root):
            d.mkdir(parents=True, exist_ok=True)
        for sub in ("interviews", "specs", "findings", "execution_plans"):
            (self.specs_root / sub).mkdir(parents=True, exist_ok=True)
        index = self.specs_root / "index.json"
        if not index.exists():
            index.write_text('{"tasks": []}\n', encoding="utf-8")
