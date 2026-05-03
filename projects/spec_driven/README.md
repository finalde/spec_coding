# spec_driven

Interactive viewer / editor for the artifacts produced by the spec-driven workflow,
plus a regeneration-prompt assembler that emits copy-paste prompts for the
Claude Code CLI.

Single project at `projects/spec_driven/` with `backend/` + `frontend/` sharing this
README. Localhost-only — binds `127.0.0.1:8765` (loopback only).

## Stack

- Backend: FastAPI (Python 3.10+) — single process serves both `/api/*` and the
  pre-built React SPA from `backend/static/`.
- Frontend: React + Vite + react-router-dom.

## Install

```sh
make install
```

(Alternatively: `pip install -r backend/requirements.txt && (cd frontend && npm install)`.)

## Run

Dev (no SPA build needed) — backend only, serves API + a no-SPA fallback:

```sh
make run            # alias for `make run-backend`
```

Dev — backend + Vite dev server in two terminals (hot reload on the React side):

```sh
# terminal 1
make run-backend    # FastAPI on http://127.0.0.1:8765
# terminal 2
make run-frontend   # Vite on http://127.0.0.1:5173
```

Production (single process, SPA built and served from `backend/static/`):

```sh
make build-frontend
make run-prod
```

Open http://127.0.0.1:8765/ in a browser.

## Test

```sh
make test-backend     # pytest under backend/tests/
make test-frontend    # vitest under frontend/test/
make e2e              # Playwright system tests
make boot-smoke       # SYS-1 only (fast smoke)
```

## Routes

- `GET /api/tree` — recursive `{name, path, type, children[]}` for the EXPOSED_TREE.
- `GET /api/file?path=<rel>` — read a file inside the EXPOSED_TREE.
- `PUT /api/file` — write a file inside the EXPOSED_TREE.
- `GET /api/stages?project_type=&project_name=` — canonical six-stage definition.
- `POST /api/regen-prompt` — assemble a copy-paste regeneration prompt.
- `POST /api/promote` / `DELETE /api/promote` — pin / unpin atomic items into
  `<stage>/promoted.md`.

## Security model

- All file-touching paths run through `safe_resolve` (see `backend/libs/safe_resolve.py`).
  Reparse points (junctions, symlinks), Windows reserved device names, ADS, 8.3 short
  names, and absolute paths are rejected. Disallowed extensions return 415, files
  larger than 1 MB return 413, anything outside the EXPOSED_TREE returns a single 404.
- State-changing routes validate `Origin` and `Host` headers (FR-9). Foreign Origin
  or Host mismatch returns 403.
- Markdown is rendered through `react-markdown` + `rehype-sanitize` with no raw-HTML
  escape hatch. SVG is NOT in the file-extension allowlist.

## Spec

The canonical spec for this project lives at
`specs/development/spec_driven/final_specs/spec.md`. Every functional requirement
(FR-NN), non-functional requirement (NFR-NN), and acceptance criterion (AC-NN) in
the test files cites it.
