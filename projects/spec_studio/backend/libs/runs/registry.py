from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, AsyncIterator
from uuid import uuid4

from ..agents import ClaudeRunner, RunnerEvent, build_phase_prompt
from ..config import Settings
from ..models import Phase, RunHandle, Task, TaskStatus
from ..storage import AuditTail, FileStore


class RunNotFoundError(LookupError):
    pass


@dataclass
class RunState:
    run_id: str
    task_id: str
    phase: Phase
    status: str = "queued"
    started_at: str = ""
    finished_at: str = ""
    next_seq: int = 0
    queue: asyncio.Queue[dict[str, Any] | None] = field(default_factory=asyncio.Queue)


_PHASE_TO_STATUS = {
    Phase.INTERVIEW: TaskStatus.INTERVIEWING,
    Phase.SPEC: TaskStatus.SPECIFYING,
    Phase.RESEARCH: TaskStatus.RESEARCHING,
    Phase.PLAN: TaskStatus.PLANNING,
    Phase.EXECUTE: TaskStatus.EXECUTING,
    Phase.FINAL_VALIDATE: TaskStatus.VALIDATING,
}


class RunRegistry:
    def __init__(self, settings: Settings, store: FileStore, runner: ClaudeRunner) -> None:
        self._settings = settings
        self._store = store
        self._runner = runner
        self._sem = asyncio.Semaphore(settings.max_concurrent_runs)
        self._runs: dict[str, RunState] = {}
        self._tails: dict[str, AuditTail] = {}

    def _now(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def _audit_tail_for(self, task_id: str) -> AuditTail:
        if task_id not in self._tails:
            self._tails[task_id] = AuditTail(self._store.events_path(task_id))
        return self._tails[task_id]

    def get(self, run_id: str) -> RunState:
        try:
            return self._runs[run_id]
        except KeyError as e:
            raise RunNotFoundError(run_id) from e

    async def start_phase(self, task: Task, phase: Phase) -> RunHandle:
        run_id = uuid4().hex[:16]
        state = RunState(run_id=run_id, task_id=task.id, phase=phase, started_at=self._now())
        self._runs[run_id] = state
        prompt = build_phase_prompt(phase, task)
        new_status = _PHASE_TO_STATUS.get(phase, TaskStatus.EXECUTING)
        self._store.update_task(task.id, status=new_status, current_phase=phase, last_run=(phase, run_id))
        asyncio.create_task(self._drive(state, prompt))
        return RunHandle(run_id=run_id, task_id=task.id, phase=phase)

    async def _drive(self, state: RunState, prompt: str) -> None:
        tail = self._audit_tail_for(state.task_id)
        state.status = "running"
        async with self._sem:
            try:
                async for ev in self._runner.stream(prompt):
                    await self._publish(state, tail, ev)
            except Exception as e:
                await self._publish(
                    state,
                    tail,
                    RunnerEvent.now("runner.crashed", {"error": repr(e)}),
                )
                state.status = "crashed"
            else:
                state.status = "completed"
            finally:
                state.finished_at = self._now()
                state.queue.put_nowait(None)

    async def _publish(self, state: RunState, tail: AuditTail, ev: RunnerEvent) -> None:
        seq = state.next_seq
        state.next_seq += 1
        record = {
            "seq": seq,
            "ts": ev.ts,
            "run_id": state.run_id,
            "task_id": state.task_id,
            "source": "sdk",
            "type": ev.type,
            "payload": ev.payload,
        }
        await tail.append(record)
        state.queue.put_nowait(record)

    async def subscribe(self, run_id: str, after_seq: int = -1) -> AsyncIterator[dict[str, Any]]:
        state = self.get(run_id)
        tail = self._audit_tail_for(state.task_id)
        last_seen = after_seq
        for ev in tail.replay_from(after_seq):
            if ev.get("run_id") != run_id:
                continue
            yield ev
            last_seen = max(last_seen, int(ev.get("seq", last_seen)))
        while True:
            item = await state.queue.get()
            if item is None:
                return
            seq = int(item.get("seq", -1))
            if seq <= last_seen:
                continue
            yield item
            last_seen = seq
