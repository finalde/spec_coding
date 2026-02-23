from __future__ import annotations

import yaml
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .checks import ScriptCheck
from .task import Task


@dataclass(frozen=True)
class Spec:
    path: str
    goal: str
    tasks: list[Task]
    context: str
    instructions: list[str]
    max_iterations: int | None

    @classmethod
    def from_file(cls, path: str) -> Spec:
        p: Path = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Spec file not found: {p}")
        data: dict[str, Any] = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        goal: str = (data.get("goal") or "").strip()
        if not goal:
            raise ValueError("Spec must have a non-empty 'goal'")
        raw_tasks: list[dict[str, Any]] = data.get("tasks") or []
        if not raw_tasks:
            raise ValueError("Spec must have at least one task")
        tasks: list[Task] = [Task._from_dict(t) for t in raw_tasks]
        _validate_unique_ids(tasks)
        return cls(
            path=path,
            goal=goal,
            context=(data.get("context") or "").strip(),
            instructions=data.get("instructions") or [],
            tasks=tasks,
            max_iterations=data.get("max_iterations"),
        )

    def to_prompt(self) -> str:
        lines: list[str] = [f"## Goal\n{self.goal}"]
        if self.context:
            lines.append(f"\n## Context\n{self.context}")
        if self.instructions:
            lines.append("\n## Global Instructions")
            lines.extend(f"- {instr}" for instr in self.instructions)
        lines.append("\n## Tasks")
        for idx, task in enumerate(self.tasks, 1):
            lines.append(f"\n### Task {idx}: {task.title} [{task.id}]")
            if task.description:
                lines.append(task.description)
            if task.instructions:
                lines.append("\n**Task Instructions:**")
                lines.extend(f"- {instr}" for instr in task.instructions)
            lines.append(
                "\n**Acceptance Criteria — verify each one before marking this task done:**"
            )
            for j, crit in enumerate(task.acceptance_criteria, 1):
                lines.append(f"{j}. {crit.criterion}")
                if isinstance(crit.check, ScriptCheck):
                    lines.append(f"   \u2713 Script check \u2014 run: {crit.check.run}")
                    lines.append("     Pass condition: exit code 0")
                else:
                    lines.append(f"   \u2713 Natural language check:")
                    lines.append(f"     {crit.check.description}")
        lines.append(
            "\n## Completion Signal\n"
            "Work through all tasks in order. For each acceptance criterion:\n"
            "- script checks: run the command and confirm exit code 0\n"
            "- natural checks: interpret and execute the description, confirm the outcome\n\n"
            "When ALL criteria in ALL tasks have been verified, emit:\n\n"
            "<promise>all tasks complete</promise>\n\n"
            "Do NOT emit the promise tag until every criterion has been executed and confirmed."
        )
        return "\n".join(lines)


def _validate_unique_ids(tasks: list[Task]) -> None:
    seen: set[str] = set()
    for task in tasks:
        if task.id in seen:
            raise ValueError(f"Duplicate task id: '{task.id}'")
        seen.add(task.id)
