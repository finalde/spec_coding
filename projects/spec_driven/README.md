# spec_driven

`spec_driven` is an interactive viewer/editor SPA for the artifacts produced by the spec-driven workflow (`specs/{task_type}/{task_name}/`) plus the cross-cutting context the workflow reads (`CLAUDE.md`, `.claude/skills/**/*.md`, `.claude/agent_refs/**/*.md`). Browse the recursive sidebar, edit whole files or per-Q/A blocks, pin atomic items so they survive regeneration, and emit copy-paste regen prompts (INTERACTIVE or AUTONOMOUS) that drive any subset of the six pipeline stages back through Claude Code.

## Run

The webapp supports three runtime modes. All three bind IPv4 loopback only (`127.0.0.1`) — never `0.0.0.0`.

### Production single-process — `make run-prod`

Builds the frontend bundle into `backend/static/` and serves SPA + API from one FastAPI process.

```
make build-frontend
make run-prod
```

Open `http://127.0.0.1:8765/`.

### Backend-only alias — `make run`

Alias for `make run-backend`. Expects a previously built bundle in `backend/static/` (or treat as API-only).

```
make run
```

### Backend + frontend separately (dev) — two terminals

Terminal 1 (backend on `127.0.0.1:8765`):

```
make run-backend
```

Terminal 2 (Vite dev server on `127.0.0.1:5173`):

```
make run-frontend
```

Open `http://127.0.0.1:5173/`. The Vite proxy forwards `/api/*` to the backend; per follow-up 006 the proxy rewrites `Origin` to `http://127.0.0.1:8765` (and `changeOrigin: true` rewrites `Host` to the target) so the backend's Origin/Host gate sees a same-shape request in both runtime modes. The backend allow-list is NOT widened to the dev-server port.

## Test

| Target | What it runs |
|---|---|
| `make test-backend` | `pytest` over `backend/tests/` (unit + boundary tests against `EXPOSED_TREE`). |
| `make test-frontend` | Frontend unit tests (Vitest / equivalent). |
| `make e2e` | Playwright suite against both runtime modes (one profile per advertised mode). |
| `make boot-smoke` | Boot-smoke pytest: process starts, root endpoint returns 200, `/api/tree` returns the expected shape. |

## Install

| Target | What it does |
|---|---|
| `make install` | Runs both install targets below. |
| `make install-backend` | `pip install -r backend/requirements.txt` (pip-only — no `uv`). |
| `make install-frontend` | `npm install` inside `frontend/`. |

## Clean

`make clean` removes `node_modules/`, `dist/`, `.vite/`, generated `backend/static/` artifacts, `__pycache__/`, and `.pytest_cache/`.

## Architecture

- **Backend.** FastAPI on `127.0.0.1:8765` (IPv4 loopback). Strongly typed Python in `backend/libs/` (`@dataclass(frozen=True)` containers, `str | None` syntax). Single-process mode also serves `backend/static/`.
- **Frontend.** React + Vite (TypeScript). Recursive sidebar walks `node.children` uniformly; render-mode dispatch chooses `MarkdownView` / `QaView` / `JsonlView` / `CodeView` / `ImagePlaceholder`; every parse-on-render component is wrapped in a real React Error Boundary class.
- **Mutation surface.** Exactly four endpoints: `PUT /api/file`, `POST /api/regen-prompt`, `POST /api/promote`, `DELETE /api/promote`. No file create / delete / upload.
- **Regen prompts.** Assembled server-side (`backend/libs/regen_prompt.py`); inline `revised_prompt.md` + every `user_input/follow_ups/*.md` + per-stage pinned items + the read-zero contract verbatim from `CLAUDE.md`. Copy-paste into Claude Code CLI.

## Security model

- Localhost-only, IPv4 (`127.0.0.1`). IPv6 (`[::1]`) and `0.0.0.0` are explicitly out of scope.
- `Origin` and `Host` validated on every state-changing endpoint; foreign / missing / wrong-port → **403** (CSRF / DNS-rebind defense). Loopback aliases (`localhost` ↔ `127.0.0.1` at the bound port) admit because they resolve to the same socket.
- File access sandboxed through `EXPOSED_TREE`. Path traversal probes (`..`, percent-encoded, ADS, Windows reserved names, 8.3 short names, mixed slashes, trailing-backslash per Vite CVE-2025-62522) all collapse to a single **404** (no existence oracle). Symlinks / Windows junctions refused outright.
- Extension allowlist for reads (`.md`, `.json`, `.yaml`, `.yml`, `.jsonl`, `.txt`, `.png`, `.jpg`); SVG NOT in the allowlist (code-execution vector). Image extensions are not writable. 1 MB body cap on writes.
- Markdown render path uses `rehype-sanitize` default schema; raw HTML, event handlers, and `javascript:` URIs are stripped.
- Concurrency guard via `If-Unmodified-Since` (RFC 7232 mtime) on `PUT /api/file` — stale write returns **409** so the SPA can offer "file changed externally — Reload?".

## Light-theme app chrome

App chrome (body, sidebars, toolbars, panels, buttons, form controls) is light-only per `.claude/agent_refs/project/development.md` — `:root { color-scheme: light; }`, no `@media (prefers-color-scheme: dark)` overrides. Dark `<pre>` palettes inside `.regen-prompt-block`, `.markdown-view pre`, and `.code-view pre` are intentional carve-outs (validated WCAG AA).
