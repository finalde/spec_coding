from __future__ import annotations

from pathlib import Path

CANONICAL_STAGES: list[str] = [
    "user_input",
    "interview",
    "findings",
    "final_specs",
    "validation",
]
SCRATCH_DIRNAME: str = "__scratch__"
ALLOWED_EXTENSIONS: frozenset[str] = frozenset(
    {".md", ".json", ".yaml", ".yml", ".jsonl", ".txt", ".png", ".jpg"}
)
MAX_FILE_BYTES: int = 1_048_576

_EXCLUDED_DIRS: frozenset[str] = frozenset(
    {"node_modules", ".git", ".audit", "__pycache__", ".pytest_cache", "dist", "build", ".vite"}
)


class ExposedTree:
    def __init__(self, repo_root: Path) -> None:
        self._root = repo_root.resolve()

    @property
    def root(self) -> Path:
        return self._root

    def claude_root_files(self) -> list[Path]:
        cm = self._root / "CLAUDE.md"
        return [cm] if cm.is_file() else []

    def claude_skill_files(self) -> list[Path]:
        skills_dir = self._root / ".claude" / "skills"
        out: list[Path] = []
        if not skills_dir.is_dir():
            return out
        for p in skills_dir.rglob("SKILL.md"):
            if p.is_file():
                out.append(p)
        playbooks_dir = self._root / ".claude" / "skills" / "agent_team" / "playbooks"
        if playbooks_dir.is_dir():
            for p in sorted(playbooks_dir.glob("*.md")):
                if p.is_file():
                    out.append(p)
        return out

    def claude_agent_refs(self) -> list[Path]:
        refs_dir = self._root / ".claude" / "agent_refs"
        if not refs_dir.is_dir():
            return []
        return sorted(p for p in refs_dir.rglob("*.md") if p.is_file())

    def project_dirs(self) -> list[Path]:
        projects_root = self._root / "projects"
        if not projects_root.is_dir():
            return []
        return sorted(p for p in projects_root.iterdir() if p.is_dir())

    def project_stage_dirs(self, project_dir: Path) -> list[Path]:
        return [project_dir / s for s in CANONICAL_STAGES if (project_dir / s).is_dir()]

    def is_inside(self, rel: str) -> bool:
        if not rel or rel.startswith("/") or "\\" in rel or "\x00" in rel:
            return False
        candidate = (self._root / rel).resolve(strict=False)
        if not (candidate == self._root or self._root in candidate.parents):
            return False
        try:
            relative = candidate.relative_to(self._root)
        except ValueError:
            return False
        parts = relative.parts
        if not parts:
            return False
        first = parts[0]
        if first == "CLAUDE.md":
            return True
        if first == ".claude":
            if len(parts) >= 2 and parts[1] in {"skills", "agent_refs"}:
                return True
            return False
        if first == "specs":
            return True
        if first == "projects":
            for seg in parts:
                if seg in _EXCLUDED_DIRS:
                    return False
            return True
        return False

    def excluded_dirs(self) -> frozenset[str]:
        return _EXCLUDED_DIRS
