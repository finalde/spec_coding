# Follow-up draft 007 — 2026-05-03

Summary: Fix `make run-backend` (and `make run-prod`) crashing with `main.py: error: unrecognized arguments: --host 127.0.0.1 --port 8765`. The `Makefile` invokes `python main.py --host $(HOST) --port $(PORT)`, but `backend/main.py` only declares `--no-static`. Host/port are hardcoded constants in `main.py` per SEC-13 / NFR-7 ("Every target binds `127.0.0.1` — NEVER `0.0.0.0`"). Align the `Makefile` to the spec by dropping the unused flags (and the now-orphaned `HOST` / `PORT` variables); do **not** add CLI overrides on `main.py` because that would create a path to bind a non-loopback host and weaken the audit invariant.

## Root cause

- `backend/main.py` (current): `argparse` declares only `--no-static`. `HOST = "127.0.0.1"` and `PORT = 8765` are module-level constants passed straight to `uvicorn.run`. By design — the security model forbids any runtime override that could land at `0.0.0.0`.
- `projects/spec_driven/Makefile` (current, drifted):
  ```make
  HOST := 127.0.0.1
  PORT := 8765
  ...
  run-backend:
      cd backend && $(PY) main.py --host $(HOST) --port $(PORT)
  run-prod: build-frontend
      cd backend && $(PY) main.py --host $(HOST) --port $(PORT)
  ```
  These flags were never declared on `main.py`, so argparse rejects every invocation. Both `run-backend` and `run-prod` are broken; `run` (alias for `run-backend`) is broken transitively.

Follow-up 003's stated contract for `run-backend` was literal: *"Behaves identically to the current `make run`: `cd backend && python main.py`."* The flag form diverged from that contract during a later edit. `final_specs/spec.md` FR-39 lists the target names but does not specify CLI flags, so the spec itself stays correct.

## Fix

`projects/spec_driven/Makefile`:

1. Remove `HOST := 127.0.0.1` and `PORT := 8765` (no remaining references after the flag strip).
2. `run-backend`: `cd backend && $(PY) main.py`.
3. `run-prod`: `cd backend && $(PY) main.py` (still depends on `build-frontend`).

That's the entire change. `main.py` is untouched — host and port stay hardcoded, SEC-13 / NFR-7 invariants intact, no new audit surface.

## Why not "add `--host` / `--port` to `main.py`"

Adding CLI overrides would let `make run-backend HOST=0.0.0.0 PORT=80` bind a LAN-reachable socket. That contradicts the spec's hard rule (FR-39 trailing clause: *"Every target binds `127.0.0.1` (NEVER `0.0.0.0`)."*) and the security model in `README.md` ("Localhost-only, IPv4 (`127.0.0.1`). IPv6 (`[::1]`) and `0.0.0.0` are explicitly out of scope."). The hardcoded constants are the security boundary; do not move it to a flag.

## Out of scope

- Spec, README, BDD, validation: no edits. FR-39 already names the targets and asserts the loopback bind. The `boot-smoke` and Origin/Host tests already assert behavior at `127.0.0.1:8765`; they pass against the un-flagged invocation.
- No new test. The boot-smoke pytest already covers "process starts and serves on `127.0.0.1:8765`," which would have caught this had it run between the divergence and now.
