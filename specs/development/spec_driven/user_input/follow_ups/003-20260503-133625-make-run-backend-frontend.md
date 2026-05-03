# Follow-up draft 003 — 2026-05-03

Summary: Split the `Makefile` `run` story into two distinct dev-server targets — `make run-backend` (the existing FastAPI on `127.0.0.1:8765`) and `make run-frontend` (the Vite dev server on `127.0.0.1:5173`) — so the operator can launch each tier in its own terminal during development.

## New / changed requirements

### 1. `make run-backend` target

- Behaves identically to the current `make run`: `cd backend && python main.py`, binding `127.0.0.1:8765`.
- The pre-existing `run` target stays in place as a backend-only alias so AC-29 / SYS-17 (which spell `make run` literally and assert localhost-only binding) remain valid without text edits.

### 2. `make run-frontend` target

- Launches the Vite dev server: `cd frontend && npm run dev`.
- The dev server already binds `127.0.0.1:5173` in `frontend/package.json` (`vite --host 127.0.0.1 --port 5173`); the Makefile target inherits that. No LAN bind. No new ports.
- This target is a developer convenience for hot-reload work on the React side. Production / single-process serving (FR-39 `run-prod`) is unchanged.

### 3. Spec / README updates

- `final_specs/spec.md` FR-39: add `run-backend` and `run-frontend` to the published target list.
- `projects/spec_driven/README.md` Run section: add a short "Run backend + frontend separately (dev)" subsection naming both targets.
- No new acceptance criteria, system tests, or BDD scenarios. `make run` semantics are unchanged; the new targets are additive dev convenience and do not introduce a new behavior worth a dedicated test gate (the underlying `python main.py` and `npm run dev` already have their own coverage).

## Out of scope

- Combined "run both at once" target (the operator can open two terminals; concurrent-process orchestration via `&` / `tmux` / `concurrently` is intentionally not added).
- Auto-proxy from the Vite dev server to `127.0.0.1:8765` for `/api/*`. Not needed for v1; the frontend dev experience for `spec_driven` is primarily exercised against the single-process `make run-prod` build.
