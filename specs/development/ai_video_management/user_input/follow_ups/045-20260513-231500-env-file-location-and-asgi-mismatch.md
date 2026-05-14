# Follow-up draft 045 — 2026-05-13

**Summary:** Backend boot fails with `RuntimeError: kling env keys missing; set KLING_ACCESS_KEY + KLING_SECRET_KEY` because (a) after the follow-up 039 migration the project's `.env` file was never recreated at the new canonical path `apps/api/.env`, and (b) `apps/api/asgi.py` reads `Path(__file__).resolve().parent.parent / ".env"` (= `apps/.env`) while `apps/api/main.py` reads `Path(__file__).resolve().parent / ".env"` (= `apps/api/.env`) — the two entry points disagree.

## Source

> got error: `Process SpawnProcess-1: ... RuntimeError: kling env keys missing; set KLING_ACCESS_KEY + KLING_SECRET_KEY (e.g. via backend/.env loaded by env_loader)`. User also supplied the Kling Access Key + Secret Key with the instruction "put it in a local env file not tracked by git".

## Abstracted instruction

1. **Canonical env-file location post-039 = `apps/api/.env`** (sits next to `main.py` / `asgi.py`). The follow-up 025 convention was `backend/.env`; the 039 migration moves `backend/main.py` → `apps/api/main.py`, so `.env` follows suit and lives at `apps/api/.env`. **Update references** in `revised_prompt.md` + downstream specs that still say `backend/.env`.
2. **`apps/api/asgi.py` env-path bug**: fix `Path(__file__).resolve().parent.parent / ".env"` → `Path(__file__).resolve().parent / ".env"` so it agrees with `main.py`. Both entry points must load the same `.env`.
3. **Create the actual `.env` file at `apps/api/.env`** containing `KLING_ACCESS_KEY` and `KLING_SECRET_KEY` (concrete values supplied by user privately; **NOT to be persisted in this follow-up or any spec artifact**). The file is already covered by the repo root `.gitignore` (line 138: `.env`).
4. **No other code changes.** `env_loader.load_env_file` already returns 0 silently if the file is missing; the boot-time `RuntimeError` from `KlingProvider.from_env()` is the intended failfast.

## Why now

After the apps/+libs/ migration, the entry-point pair (`main.py` + `asgi.py`) both load env-vars before importing the rest of the app — the path needed to be stable across both. The migration left `asgi.py` with a stale `.parent.parent` from when it lived at `backend/libs/asgi.py` (relative to which `.parent.parent` = `backend/`, the correct location at the time). At the new path `apps/api/asgi.py`, the same expression yields `apps/`, one level too high.

## Acceptance

- `cd projects/ai_video_management && python -m apps.api.main` boots without `kling env keys missing` (given a populated `apps/api/.env`).
- `python -m apps.api.main` (default reload mode) and `python -m apps.api.main --no-reload` both pick up the same `.env`.
- `git status` does NOT list `apps/api/.env` as untracked (gitignore catches it).
- The Kling key values do NOT appear in any committed file (spec, code, or changelog).

## Out of scope

- No change to `env_loader` itself.
- No change to `KlingProvider.from_env()` or its error message.
- No promoting `.env` to a per-environment config system; the simple `KEY=VALUE` loader still suffices.
