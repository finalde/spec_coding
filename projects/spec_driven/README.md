# spec_driven

A single-user, localhost FastAPI + React viewer/editor for the artifacts produced
by the spec-driven workflow itself. Browse, render, edit, and assemble
copy-paste regeneration prompts for every artifact under the project's exposed
tree (`CLAUDE.md`, `.claude/agents/*.md`, `.claude/skills/**/SKILL.md`, and the
five-stage subfolders under `specs/{task_type}/{task_name}/`).

## Install

```sh
make install
```

Runs `pip install -r backend/requirements.txt` (plus `pytest` and `httpx` for
tests) into the repo's `.venv`, then `npm install` inside `frontend/`. The
backend uses the pre-existing `.venv` at the repo root rather than `uv` —
this avoids `uv run`'s known crash on this Windows host.

## Develop (two-process mode)

Run the backend and frontend in **two separate terminals**:

```sh
make run-backend
```

Starts FastAPI on `http://127.0.0.1:8765` with `--reload` (auto-restart on
backend code changes). Uses uvicorn's `--factory` mode against
`libs.api:create_app`, which discovers the repo root from the file's location.

```sh
make run-frontend
```

Starts the Vite dev server on `http://127.0.0.1:5173`. Vite is configured to
proxy `/api/*` to `http://127.0.0.1:8765`, so open the frontend URL in a
browser and HMR works against the live backend.

## Run (production-style, single process)

```sh
make run-prod
```

Builds the React bundle into `backend/static/` and starts one FastAPI process
serving both the SPA and `/api/`. Open `http://localhost:8765/`.

## Test

```sh
make test
```

Runs the backend `pytest` suite via the repo `.venv`.

## Configuration

- `BACKEND_PORT` — overrides the FastAPI port (default `8765`). Example:
  `BACKEND_PORT=9090 make run-backend`. The same value is forwarded to
  `SPEC_DRIVEN_PORT` for `make run-prod`.
- `FRONTEND_PORT` — overrides the Vite dev port (default `5173`).
- `SPEC_DRIVEN_PORT` — read directly by `main.py` (used by `make run-prod`).
  If the port is unavailable, the process exits non-zero with a clear error.

## Security model

- The backend binds to `127.0.0.1` only. There is no authentication, no CORS
  configuration, and no remote reachability. The deployment is a single-user,
  localhost-only dogfood tool.
- All file-touching endpoints funnel through a single `safe_resolve` helper
  that rejects path traversal, symlinks (including ancestor symlinks),
  absolute paths, and embedded NUL bytes. Only `.md`, `.yaml`, `.yml`,
  `.json`, and `.jsonl` files inside the exposed tree are served. The 2 MB
  per-file ceiling and the NUL-byte rejection are also enforced on `PUT`.
- Sanctioned mutation endpoints are exactly `PUT /api/file` (atomic-replace
  via `tempfile.mkstemp` + `os.fsync` + `os.replace`) and
  `POST /api/regen-prompt` (which only assembles a string and never writes).
  PATCH and DELETE return 405. No upload, no create, no delete.

## Autonomous-mode contract

The web app emits **copy-paste regeneration prompts** that the user pastes
into the Claude Code CLI. Each prompt opens with one of two execution-mode
headers: `# EXECUTION MODE: AUTONOMOUS` or `# EXECUTION MODE: INTERACTIVE`.
Under autonomous mode, Claude must not call `AskUserQuestion`, must use best
judgment for ambiguous choices and record the decision inline in the
artifact, and must produce every requested artifact in the same turn before
stopping. See the **Regeneration prompts & autonomous mode** section in the
repo-root `CLAUDE.md` for the full contract.
