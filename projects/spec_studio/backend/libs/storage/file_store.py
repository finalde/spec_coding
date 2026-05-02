from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from ..config import Settings
from ..models import (
    Adjustments,
    Artifact,
    ArtifactKind,
    CreateTask,
    Phase,
    RootFolder,
    Task,
    TaskStatus,
    TaskSummary,
)


class TaskNotFoundError(LookupError):
    pass


class FileStore:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._lock = threading.RLock()
        settings.ensure_dirs()

    @property
    def index_path(self) -> Path:
        return self._settings.specs_root / "index.json"

    def _now(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def _read_index(self) -> dict:
        with self._lock:
            raw = self.index_path.read_text(encoding="utf-8")
            return json.loads(raw)

    def _write_index(self, data: dict) -> None:
        with self._lock:
            tmp = self.index_path.with_suffix(".json.tmp")
            tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            tmp.replace(self.index_path)

    def list_tasks(self) -> list[TaskSummary]:
        idx = self._read_index()
        return [TaskSummary(**t) for t in idx.get("tasks", [])]

    def get_task(self, task_id: str) -> Task:
        idx = self._read_index()
        for t in idx.get("tasks", []):
            if t["id"] == task_id:
                return Task(**t, artifacts=self._artifact_status(task_id))
        raise TaskNotFoundError(task_id)

    def create_task(self, payload: CreateTask) -> Task:
        with self._lock:
            idx = self._read_index()
            short = uuid4().hex[:6]
            task_id = f"{payload.name}__{short}"
            now = self._now()
            record = {
                "id": task_id,
                "name": payload.name,
                "root_folder": payload.root_folder.value,
                "current_phase": Phase.INTERVIEW.value,
                "status": TaskStatus.CREATED.value,
                "created_at": now,
                "updated_at": now,
                "initial_prompt": payload.initial_prompt,
                "last_run_ids": {},
            }
            idx.setdefault("tasks", []).append(record)
            self._write_index(idx)
            self._ensure_task_dirs(task_id)
            self._write_initial_prompt(task_id, payload.initial_prompt)
            return Task(**record, artifacts=self._artifact_status(task_id))

    def update_task(
        self,
        task_id: str,
        *,
        current_phase: Phase | None = None,
        status: TaskStatus | None = None,
        last_run: tuple[Phase, str] | None = None,
    ) -> Task:
        with self._lock:
            idx = self._read_index()
            for t in idx.get("tasks", []):
                if t["id"] == task_id:
                    if current_phase is not None:
                        t["current_phase"] = current_phase.value
                    if status is not None:
                        t["status"] = status.value
                    if last_run is not None:
                        phase, run_id = last_run
                        t.setdefault("last_run_ids", {})[phase.value] = run_id
                    t["updated_at"] = self._now()
                    self._write_index(idx)
                    return Task(**t, artifacts=self._artifact_status(task_id))
            raise TaskNotFoundError(task_id)

    def _ensure_task_dirs(self, task_id: str) -> None:
        for sub in ("interviews", "specs", "findings", "execution_plans"):
            (self._settings.specs_root / sub / task_id).mkdir(parents=True, exist_ok=True)
        date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        (self._settings.audit_root / date / task_id / "spawns").mkdir(parents=True, exist_ok=True)

    def _write_initial_prompt(self, task_id: str, prompt: str) -> None:
        path = self._settings.specs_root / "interviews" / task_id / "initial_prompt.md"
        path.write_text(f"# Initial prompt — {task_id}\n\n{prompt}\n", encoding="utf-8")

    def write_adjustments(self, task_id: str, adj: Adjustments) -> Path:
        path = self._settings.specs_root / "specs" / task_id / "adjustments.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# Adjustments — {task_id}\n\n{adj.notes}\n", encoding="utf-8")
        return path

    def artifact_path(self, task_id: str, kind: ArtifactKind) -> Path:
        roots = self._settings.specs_root
        date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        match kind:
            case "qa":
                return roots / "interviews" / task_id / "qa.md"
            case "spec":
                return roots / "specs" / task_id / "spec.md"
            case "adjustments":
                return roots / "specs" / task_id / "adjustments.md"
            case "dossier":
                return roots / "findings" / task_id / "dossier.md"
            case "plan":
                return roots / "execution_plans" / task_id / "plan.yaml"
            case "findings_report":
                return self._settings.audit_root / date / task_id / "findings_report.md"
            case "initial_prompt":
                return roots / "interviews" / task_id / "initial_prompt.md"
        raise ValueError(f"unknown artifact kind: {kind}")

    def read_artifact(self, task_id: str, kind: ArtifactKind) -> Artifact:
        import hashlib
        path = self.artifact_path(task_id, kind)
        exists = path.exists()
        content = path.read_text(encoding="utf-8") if exists else None
        sha = hashlib.sha256(content.encode("utf-8")).hexdigest() if content is not None else None
        mime = "application/x-yaml" if kind == "plan" else "text/markdown"
        return Artifact(kind=kind, path=str(path), exists=exists, content=content, mime=mime, sha256=sha)

    def current_phase_manager_path(self, task_id: str) -> Path:
        task = self.get_task(task_id)
        agents_dir = self._settings.repo_root / ".claude" / "agents"
        phase_to_agent = {
            Phase.INTERVIEW: "agent_team__interview_manager.md",
            Phase.SPEC: "agent_team__spec_compiler.md",
            Phase.RESEARCH: "agent_team__research_manager.md",
            Phase.ADJUSTMENTS: "agent_team__interview_manager.md",
            Phase.PLAN: "agent_team__execution_plan_compiler.md",
            Phase.EXECUTE: "agent_team__execution_manager.md",
            Phase.FINAL_VALIDATE: "agent_team__validation_manager.md",
            Phase.DONE: "agent_team__validation_manager.md",
        }
        filename = phase_to_agent.get(task.current_phase, "agent_team__interview_manager.md")
        return agents_dir / filename

    def skill_md_path(self) -> Path:
        return self._settings.repo_root / ".claude" / "skills" / "agent_team" / "SKILL.md"

    def claude_md_path(self) -> Path:
        return self._settings.repo_root / "CLAUDE.md"

    def events_path(self, task_id: str) -> Path:
        date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        d = self._settings.audit_root / date / task_id
        d.mkdir(parents=True, exist_ok=True)
        return d / "events.jsonl"

    def _artifact_status(self, task_id: str) -> dict[str, bool]:
        kinds: list[ArtifactKind] = [
            "qa",
            "spec",
            "adjustments",
            "dossier",
            "plan",
            "findings_report",
            "initial_prompt",
        ]
        return {k: self.artifact_path(task_id, k).exists() for k in kinds}
