from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal


InputName = Literal["claude_md", "skill_md"]
AgentName = str


class RepoPathError(LookupError):
    pass


@dataclass(frozen=True)
class ResolvedRepoFile:
    name: str
    path: Path
    requires_confirm: bool


class RepoInputResolver:
    """Allowlist-based resolver for repo files editable from the studio UI.

    Each resolved path is guaranteed to live inside the repo root and to be
    on the explicit allowlist. Anything outside the allowlist raises
    RepoPathError; we never resolve paths from arbitrary user strings.
    """

    def __init__(self, repo_root: Path) -> None:
        self._repo_root = repo_root.resolve()
        self._inputs: dict[str, Path] = {
            "claude_md": self._repo_root / "CLAUDE.md",
            "skill_md": self._repo_root / ".claude" / "skills" / "agent_team" / "SKILL.md",
        }
        self._agents_dir = self._repo_root / ".claude" / "agents"

    @property
    def repo_root(self) -> Path:
        return self._repo_root

    @property
    def claude_md(self) -> Path:
        return self._inputs["claude_md"]

    @property
    def skill_md(self) -> Path:
        return self._inputs["skill_md"]

    def resolve_input(self, name: str) -> ResolvedRepoFile:
        if name not in self._inputs:
            raise RepoPathError(f"unknown repo input '{name}'. valid: {sorted(self._inputs)}")
        return ResolvedRepoFile(name=name, path=self._inputs[name], requires_confirm=True)

    def resolve_agent(self, agent_name: str) -> ResolvedRepoFile:
        if not agent_name.startswith("agent_team__"):
            raise RepoPathError(f"agent '{agent_name}' must start with 'agent_team__'")
        if "/" in agent_name or "\\" in agent_name or ".." in agent_name:
            raise RepoPathError(f"agent name '{agent_name}' contains invalid characters")
        candidate = (self._agents_dir / f"{agent_name}.md").resolve()
        try:
            candidate.relative_to(self._agents_dir.resolve())
        except ValueError as e:
            raise RepoPathError(f"agent path traversal blocked: {agent_name}") from e
        if not candidate.exists():
            raise RepoPathError(f"agent file not found: {candidate}")
        return ResolvedRepoFile(name=agent_name, path=candidate, requires_confirm=True)

    def list_agents(self) -> list[str]:
        if not self._agents_dir.is_dir():
            return []
        names: list[str] = []
        for child in sorted(self._agents_dir.glob("agent_team__*.md")):
            names.append(child.stem)
        return names
