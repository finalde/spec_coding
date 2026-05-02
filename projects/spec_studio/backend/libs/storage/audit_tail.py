from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import AsyncIterator


class AuditTail:
    """Append-only JSONL writer + tailer for events.jsonl."""

    def __init__(self, path: Path) -> None:
        self._path = path
        self._lock = asyncio.Lock()
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.touch(exist_ok=True)

    @property
    def path(self) -> Path:
        return self._path

    async def append(self, event: dict) -> None:
        line = json.dumps(event, ensure_ascii=False) + "\n"
        async with self._lock:
            with self._path.open("a", encoding="utf-8") as f:
                f.write(line)

    def replay_from(self, after_seq: int) -> list[dict]:
        events: list[dict] = []
        if not self._path.exists():
            return events
        with self._path.open("r", encoding="utf-8") as f:
            for raw in f:
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    ev = json.loads(raw)
                except json.JSONDecodeError:
                    continue
                if ev.get("seq", -1) > after_seq:
                    events.append(ev)
        return events

    async def tail(self, after_seq: int = -1, poll_interval: float = 0.25) -> AsyncIterator[dict]:
        last_seen = after_seq
        for ev in self.replay_from(last_seen):
            last_seen = max(last_seen, ev.get("seq", last_seen))
            yield ev
        while True:
            await asyncio.sleep(poll_interval)
            new_events = self.replay_from(last_seen)
            for ev in new_events:
                last_seen = max(last_seen, ev.get("seq", last_seen))
                yield ev
