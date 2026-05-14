from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class AuditWriter:
    def __init__(self, repo_root: Path) -> None:
        self._root = repo_root.resolve()

    def emit(self, event_name: str, payload: dict[str, Any]) -> None:
        now = datetime.now(tz=timezone.utc)
        date_str = now.strftime("%Y-%m-%d")
        audit_dir = self._root / ".audit" / "adhoc_agents" / date_str / "manual_ops"
        audit_dir.mkdir(parents=True, exist_ok=True)
        audit_path = audit_dir / "events.jsonl"
        record = {"ts": now.isoformat(timespec="seconds"), "event": event_name, **payload}
        with audit_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
