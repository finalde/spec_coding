from __future__ import annotations

import json
import os
import subprocess
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from libs.common.exposed_tree import ExposedTree
from libs.common.safe_resolve import SafeResolver
from libs.domain.prompt_lab__error import (
    PromptLabAlreadyRunning,
    PromptLabExecUnavailable,
    PromptLabFileNotFound,
    PromptLabPathRejected,
)
from libs.infrastructure.prompt_lab__writer import valid_prompt_path

_RUN_PROMPT_HEADER = """# EXECUTION MODE: AUTONOMOUS

You are executing a build task fully autonomously. No human is available to answer questions.
Your current working directory IS your workspace — create ALL output files here.

AUTONOMY CONTRACT (overrides any "ask me / STOP and wait" step in the instructions below):
- NEVER ask a question or wait for input. For every setup question, choice, or ambiguity, choose
  the most sensible default and proceed immediately.
- The instructions may contain a "PHASE 1 — SETUP" step that says to ask questions and STOP. Do NOT
  stop — answer those questions yourself with good defaults and continue straight into the build.
- Log EVERY decision: append one JSON object per line to a file named `decisions.jsonl` in this
  directory, with keys exactly: ts, question, decision, why. Write the decision line BEFORE acting.
- Keep working until the instructions' acceptance checklist is satisfied or its round cap is reached,
  then stop and print a short summary.

--- BUILD INSTRUCTIONS ---

"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class PromptLabExecutor:
    """Spawns a headless, fully-autonomous `claude` session in an item's workspace (FR-44)."""

    def __init__(self, exposed: ExposedTree, resolver: SafeResolver) -> None:
        self._exposed = exposed
        self._resolver = resolver
        self._root = resolver.root

    # ---- public API -----------------------------------------------------

    def execute(self, prompt_rel: str) -> dict[str, Any]:
        item_dir, md = self._item(prompt_rel)
        st = self._read_status(item_dir)
        if st and st.get("state") == "running" and _alive(st.get("pid")):
            raise PromptLabAlreadyRunning()

        prompt = _first_fence(md.read_text(encoding="utf-8", errors="replace"))
        if not prompt:
            raise PromptLabPathRejected()

        exe = _which_claude()
        if not exe:
            raise PromptLabExecUnavailable()

        workspace = item_dir / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        (workspace / "decisions.jsonl").write_text("", encoding="utf-8")
        run_prompt_path = item_dir / ".run_prompt.txt"
        run_prompt_path.write_text(_RUN_PROMPT_HEADER + prompt, encoding="utf-8")
        output_path = item_dir / "output.txt"

        log_fh = open(output_path, "w", encoding="utf-8", errors="replace")
        in_fh = open(run_prompt_path, "r", encoding="utf-8")
        args = ["--print", "--permission-mode", "bypassPermissions"]
        cmd = (
            [os.environ.get("COMSPEC", "cmd.exe"), "/c", exe, *args]
            if os.name == "nt"
            else [exe, *args]
        )
        try:
            proc = subprocess.Popen(
                cmd, stdin=in_fh, stdout=log_fh, stderr=subprocess.STDOUT, cwd=str(workspace)
            )
        except OSError:
            log_fh.close()
            in_fh.close()
            raise PromptLabExecUnavailable()

        run_id = str(int(time.time()))
        started = _now()
        self._write_status(
            item_dir,
            {"state": "running", "pid": proc.pid, "run_id": run_id,
             "started_at": started, "ended_at": None, "exit_code": None},
        )
        threading.Thread(
            target=self._finalize,
            args=(proc, item_dir, log_fh, in_fh, run_id, started),
            daemon=True,
        ).start()
        return {"state": "running", "run_id": run_id, "path": prompt_rel}

    def status(self, prompt_rel: str) -> dict[str, Any]:
        item_dir, _ = self._item(prompt_rel)
        st = self._read_status(item_dir) or {"state": "idle"}
        if st.get("state") == "running" and not _alive(st.get("pid")):
            st["state"] = "stopped"
        return {
            "state": st.get("state", "idle"),
            "run_id": st.get("run_id"),
            "started_at": st.get("started_at"),
            "ended_at": st.get("ended_at"),
            "exit_code": st.get("exit_code"),
            "output": _tail(item_dir / "output.txt", 12000),
            "decisions": _read_jsonl(item_dir / "workspace" / "decisions.jsonl"),
            "files": _workspace_files(item_dir / "workspace"),
        }

    def stop(self, prompt_rel: str) -> dict[str, Any]:
        item_dir, _ = self._item(prompt_rel)
        st = self._read_status(item_dir)
        if st and st.get("state") == "running" and st.get("pid"):
            _kill(int(st["pid"]))
            st["state"] = "stopped"
            st["ended_at"] = _now()
            self._write_status(item_dir, st)
        return {"state": "stopped"}

    # ---- internals ------------------------------------------------------

    def _item(self, prompt_rel: str) -> tuple[Path, Path]:
        if not valid_prompt_path(prompt_rel):
            raise PromptLabPathRejected()
        resolved = self._resolver.resolve(prompt_rel)
        if resolved is None or not resolved.is_file():
            raise PromptLabFileNotFound()
        return resolved.parent, resolved

    def _finalize(self, proc, item_dir, log_fh, in_fh, run_id, started) -> None:
        code = proc.wait()
        for fh in (log_fh, in_fh):
            try:
                fh.close()
            except OSError:
                pass
        self._write_status(
            item_dir,
            {"state": "succeeded" if code == 0 else "failed", "pid": proc.pid,
             "run_id": run_id, "started_at": started, "ended_at": _now(), "exit_code": code},
        )

    @staticmethod
    def _read_status(item_dir: Path) -> dict[str, Any] | None:
        f = item_dir / "status.json"
        if not f.is_file():
            return None
        try:
            return json.loads(f.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None

    @staticmethod
    def _write_status(item_dir: Path, status: dict[str, Any]) -> None:
        (item_dir / "status.json").write_text(json.dumps(status), encoding="utf-8")


def _which_claude() -> str | None:
    import shutil

    return shutil.which("claude")


def _alive(pid: Any) -> bool:
    if not pid:
        return False
    try:
        pid = int(pid)
    except (TypeError, ValueError):
        return False
    try:
        if os.name == "nt":
            import ctypes

            handle = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)
            if handle:
                ctypes.windll.kernel32.CloseHandle(handle)
                return True
            return False
        os.kill(pid, 0)
        return True
    except (OSError, Exception):
        return False


def _kill(pid: int) -> None:
    try:
        if os.name == "nt":
            subprocess.run(["taskkill", "/T", "/F", "/PID", str(pid)], capture_output=True)
        else:
            os.kill(pid, 15)
    except OSError:
        pass


def _tail(path: Path, max_bytes: int) -> str:
    try:
        data = path.read_bytes()
    except OSError:
        return ""
    if len(data) > max_bytes:
        data = data[-max_bytes:]
    return data.decode("utf-8", errors="replace")


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return out
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            if isinstance(obj, dict):
                out.append(obj)
        except ValueError:
            continue
    return out


def _workspace_files(workspace: Path) -> list[dict[str, Any]]:
    if not workspace.is_dir():
        return []
    out: list[dict[str, Any]] = []
    for p in sorted(workspace.rglob("*")):
        if p.is_file() and p.name != "decisions.jsonl":
            try:
                out.append({"name": p.relative_to(workspace).as_posix(), "bytes": p.stat().st_size})
            except OSError:
                continue
    return out[:200]


def _first_fence(text: str) -> str:
    lines = text.split("\n")
    start = next((i for i, line in enumerate(lines) if line.startswith("```")), -1)
    if start < 0:
        return ""
    out: list[str] = []
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("```"):
            break
        out.append(lines[j])
    return "\n".join(out).strip()
