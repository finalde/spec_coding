# Research — editable_artifacts — studio_nav

**Key findings (≤500 tokens):**
- Atomic write pattern is already in the codebase (`FileStore._write_index` uses `tmp.replace(target)`). Generalize it: write to a sibling temp file in the **same directory** (so the rename stays on the same filesystem and is atomic), then `os.replace` over the target. `os.replace` is the right primitive — `os.rename` raises on Windows when the target exists; `os.replace` overwrites on both POSIX and Windows.
- Use `tempfile.NamedTemporaryFile(dir=path.parent, delete=False)` to get a unique temp name, write+flush+`os.fsync`, close, then `os.replace`. The `dir=` argument is load-bearing — without it the temp file may land on a different filesystem and `os.replace` falls back to non-atomic copy.
- `.bak` is a single sibling file (`{path}.bak`), unconditionally overwritten on each save. Copy via `shutil.copy2` to preserve mtime; do this **before** writing the new content and **only if** the target already exists. The first PUT on a non-existent file skips the .bak step.
- Confirm gating belongs in a Pydantic body model (not a route dependency) so it is part of the schema and OpenAPI surface. Repo-level routes (`PUT /api/inputs/{name}`, `PUT /api/agents/{name}`) accept `RepoEditBody(content: str, confirm: bool)` and 400 if `confirm is not True`. Per-task `PUT /api/tasks/{task_id}/artifacts/{kind}` uses a slimmer `ArtifactEditBody(content: str)` — no confirm.
- ETag = strong, lowercase hex of `sha256(content_bytes)`. Return both as a response header `ETag: "<hex>"` and as a field on the `Artifact` body so clients in the UI don't have to read headers. Clients may send `If-Match` on PUT; in v1 the server **records** the mismatch in the response (`stale: true`) but still writes (last-write-wins, see below). This keeps the contract optional and forward-compatible with strict 412 in v2.
- Concurrency stance: single-user local app, no locks across UI ↔ CLI. Threading lock inside `FileStore` only serializes intra-process writes. If a CLI agent (`/agent_team`) is regenerating `spec.md` while the UI saves, the second writer wins and the loser's content survives only as `{path}.bak`. Document this in the response and the README — do not pretend to solve it.
- OOP placement: a new `backend/libs/storage/safe_writer.py` with `AtomicWriter` (atomic write primitive, returns hash) and `BackupWriter` (wraps `AtomicWriter` and also rotates `.bak`). A new `backend/libs/edits/repo_paths.py` with `RepoInputResolver` (resolves `claude_md` / `skill_md` / `agent_team__*_manager.md` paths and validates them against an allowlist). The artifacts route stays thin — calls into `BackupWriter`.

## Atomic write pattern (recommended)
```python
# backend/libs/storage/safe_writer.py
from __future__ import annotations

import hashlib
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class WriteResult:
    path: Path
    sha256: str
    bytes_written: int


class AtomicWriter:
    """Write a UTF-8 text file atomically via tempfile + os.replace.

    Cross-platform: os.replace overwrites on both POSIX and Windows.
    The temp file is created in the *same directory* as the target so
    the rename stays on the same filesystem and is atomic.
    """

    def write_text(self, path: Path, content: str) -> WriteResult:
        path.parent.mkdir(parents=True, exist_ok=True)
        data = content.encode("utf-8")
        digest = hashlib.sha256(data).hexdigest()
        # delete=False: we hand the file off to os.replace, not GC
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as tmp:
            tmp.write(data)
            tmp.flush()
            os.fsync(tmp.fileno())  # durability before rename
            tmp_path = Path(tmp.name)
        try:
            os.replace(tmp_path, path)  # atomic on Windows + POSIX
        except OSError:
            tmp_path.unlink(missing_ok=True)
            raise
        return WriteResult(path=path, sha256=digest, bytes_written=len(data))
```

## .bak snapshot pattern
```python
# backend/libs/storage/safe_writer.py (continued)
import shutil


class BackupWriter:
    """Atomic write with single-slot .bak snapshot of the prior content."""

    def __init__(self, atomic: AtomicWriter | None = None) -> None:
        self._atomic = atomic or AtomicWriter()

    def write_text(self, path: Path, content: str) -> WriteResult:
        if path.exists():
            bak = path.with_suffix(path.suffix + ".bak")
            # copy2 preserves mtime; the bak is a snapshot of the *prior*
            # content — overwriting any older .bak. Single-slot by design.
            shutil.copy2(path, bak)
        return self._atomic.write_text(path, content)
```

## Confirm gating pattern
- Body schema for PUT: two Pydantic models — `ArtifactEditBody(content: str)` for per-task artifacts, `RepoEditBody(content: str, confirm: bool)` for repo-level files.
- Where to enforce: **in the body model + a tiny `_require_confirm` helper called at the top of the repo-level handlers**. Route-level `Depends` would also work, but a Pydantic-level check keeps the failure mode visible in the OpenAPI schema and surfaces a 422 from FastAPI's own validator when `confirm` is missing entirely. Use an explicit 400 only for the `confirm == false` case.
- Sketch:
```python
# backend/libs/routes/repo_inputs.py
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException


class RepoEditBody(BaseModel):
    content: str
    confirm: bool  # missing -> 422; false -> 400 (below)


def _require_confirm(body: RepoEditBody) -> None:
    if body.confirm is not True:
        raise HTTPException(
            status_code=400,
            detail="repo-level edits require confirm: true in the body",
        )
```
The per-task route uses `ArtifactEditBody` (no `confirm` field) and skips this check — gating is data-shaped, not logic-shaped.

## Content hash / ETag
- **Algorithm:** SHA-256 of the UTF-8 bytes of the saved content. Strong ETag (byte-equality semantics fits a markdown/yaml file). Hex digest, lowercase, full 64 chars — no truncation; storage is cheap and collision resistance matters more than header size for a local app.
- **Header:** `ETag: "<sha256-hex>"` (quoted, no `W/` prefix).
- **Response body:** extend `Artifact` with an optional `sha256: str | None = None` field so the UI can compare without reading headers. PUT response returns the freshly-computed hash of what was written.
- **Optional client check:** clients may send `If-Match: "<hex>"` on PUT. In v1 the server compares but does **not** reject — instead it includes `{stale_etag: true}` in the response when the client's `If-Match` did not match the on-disk content the server saw before its write. This is advisory only; v2 can flip it to a hard 412.

## Conflict semantics
- **v1 stance:** last-write-wins, no locking across UI and CLI agents. The intra-process `threading.RLock` in `FileStore` serializes UI writes against each other but does **nothing** to coordinate with a `claude --print` subprocess editing the same file via `/agent_team`.
- **Failure mode:** if a CLI run and a UI save race, one of them lands in the file and the other's prior version survives as `{path}.bak`. The user sees this only by reading `.bak`. Document in `projects/spec_studio/README.md` under a "Concurrency" subsection, and surface `stale_etag: true` in the response when the optional `If-Match` mismatched.
- **Why this is OK in v1:** single-user, single-host, low collision probability. Adding fcntl/`msvcrt.locking` would be Windows/POSIX-divergent and out of proportion for the use case.

## Module placement
Per CLAUDE.md § "Project rules" (OOP for stateful concepts, classes for domain concepts), propose three classes across two new modules:

1. `backend/libs/storage/safe_writer.py`
   - `AtomicWriter` — single responsibility: temp-file + `os.replace`. Returns `WriteResult` (frozen dataclass with `path`, `sha256`, `bytes_written`).
   - `BackupWriter` — composes `AtomicWriter`; adds the single-slot `.bak` rotation. This is the class the routes call.
2. `backend/libs/edits/repo_paths.py` (new package)
   - `RepoInputResolver` — given a repo root and a name (`claude_md` / `skill_md` / agent name), returns the absolute path **only if** it matches an explicit allowlist (`{"claude_md": "CLAUDE.md", "skill_md": ".claude/skills/agent_team/SKILL.md", ...}`). Rejects path traversal. Pairs with `FileStore.current_phase_manager_path()` (already specced) for the per-task manager path.

Routes (`routes/artifacts.py`, new `routes/repo_inputs.py`, new `routes/agents.py`) stay thin: validate body, resolve path via `FileStore` or `RepoInputResolver`, hand off to `BackupWriter`, return `Artifact` with `sha256`. No I/O logic in handlers.

## Sources
- [Python os.replace Function — zetcode](https://zetcode.com/python/os-replace/)
- [Safely and atomically write to a file — ActiveState recipe 579097](https://code.activestate.com/recipes/579097-safely-and-atomically-write-to-a-file/)
- [python-atomicwrites (GitHub) — discussion of os.replace vs os.rename on Windows](https://github.com/untitaker/python-atomicwrites)
- [tempfile — Python docs](https://docs.python.org/3/library/tempfile.html)
- [Showcasing Weak and Strong ETag Headers with FastAPI — BugFactory](https://bugfactory.io/articles/showcasing-weak-and-strong-etag-headers-with-fastapi/)
- [HTTP Caching with ETag and If-None-Match — BugFactory](https://bugfactory.io/articles/http-caching-with-etag-and-if-none-match-headers/)
- [HTTP ETag — Wikipedia](https://en.wikipedia.org/wiki/HTTP_ETag)
