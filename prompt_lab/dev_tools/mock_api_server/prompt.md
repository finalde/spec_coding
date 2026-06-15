# Pocket REST — instant REST API from a JSON file

**Stack:** Python (stdlib only) · **Est:** 15–25 min · **Output:** a full mock REST API from one db.json, one command

## ✨ 1. Expectation — what you'll get
You write a plain `db.json` with a few top-level keys — `users`, `posts`, `comments` — run `python server.py db.json`, and instantly have a real REST API at `http://localhost:8000`. Every key becomes a collection with full CRUD: `GET /users`, `GET /users/3`, filter with `?role=admin`, paginate with `?_page=2&_limit=10`, sort with `?_sort=name`, and POST/PUT/PATCH/DELETE that actually persist back to the file. No Flask, no FastAPI, no pip install — just Python's standard library doing the whole job.

**Why it's cool:** It reproduces the magic of json-server in a single dependency-free Python file — a throwaway backend for your frontend in fifteen seconds, runnable on any machine that has Python 3.

**Use cases:** Prototyping a frontend before the real backend exists · Stable fixtures for integration tests · Teaching REST semantics (status codes, verbs, query params) without infrastructure · A quick local stub when an upstream service is down.

## ▶️ 2. How to run
Open Claude Code in an empty folder, paste the prompt below, answer the 2–3 setup questions, then walk away while it builds and tests itself. The only prerequisite is Python 3 — no pip install, no virtualenv, nothing from PyPI. When it's done you run `python server.py db.json` and `curl` (or your browser) against `http://localhost:8000`.

## 🔗 3. Reference & prior art

This prompt is original (written for this library) — not copied from any single source. Real, well-known prior art to compare against and learn the technique from:

**Source:** [typicode/json-server](https://github.com/typicode/json-server) · **Expected result:** [json-server README](https://github.com/typicode/json-server#readme)

---

## 📋 COPY-PASTE PROMPT

```
Build me a zero-dependency mock REST API server in a single Python file, `server.py`, using ONLY the Python 3 standard library (http.server, json, urllib, etc.). No Flask, no FastAPI, no pip install, nothing from PyPI. Running `python server.py db.json` must serve a full REST API backed by db.json, where every top-level key is a collection (a list of objects, each with an `id`).

PHASE 1 — SETUP (ask, then STOP and wait for my answers):
1. Default port — 8000 is the default; do you want a different one, and should `--port` be a CLI flag? Default: 8000 + a --port flag.
2. ID strategy for new records — integer auto-increment (max existing id + 1) or string UUIDs? Default: integer auto-increment.
3. Persistence — write changes back to db.json on every mutation (durable), or keep an in-memory copy and only flush on exit? Default: write back atomically on every mutation.
Ask these three, then STOP. Do not start building until I answer.

PHASE 2 — AUTONOMOUS BUILD:
After I answer, DO NOT ask anything else. Loop until the acceptance checklist passes. Treat the file system as your memory — write server.py, create a sample db.json, actually START the server (bind to a port, or run it in the background) and hit it with real HTTP requests using urllib or curl to verify each behavior. Each round: implement, RUN it and send real requests, self-review against the checklist, fix what fails, repeat. Don't ask me to confirm between rounds. Tear down any server you start so ports don't leak.

WHAT TO BUILD:
- `python server.py db.json` loads db.json; each top-level key whose value is a list becomes a REST collection.
- GET /collection — returns the array. Support: field filtering via `?field=value` (multiple allowed, AND-combined); pagination via `?_page=N&_limit=M`; sorting via `?_sort=field` (and optional `?_order=asc|desc`).
- GET /collection/:id — single record, 404 if missing.
- POST /collection — create; auto-assign id per the chosen strategy; return 201 with the created object.
- PUT /collection/:id — full replace (404 if missing). PATCH /collection/:id — partial merge. DELETE /collection/:id — remove, return 204 or the deleted object.
- ALL mutations persist back to db.json ATOMICALLY (write to a temp file in the same dir, then os.replace) so a crash can't corrupt the file.
- Permissive CORS on every response (Access-Control-Allow-Origin: *, allow methods + headers) and handle OPTIONS preflight.
- A helpful index route `GET /` that lists the available collections and example routes.
- If db.json is missing or empty, generate a small sensible sample (e.g. users + posts) and write it, so the server always has something to serve.
- Sane HTTP status codes and JSON error bodies; never return an unhandled 500 stack trace for ordinary bad input.

ACCEPTANCE CHECKLIST (every item must pass before you stop — verify with real HTTP requests):
[ ] GET, POST, PUT, PATCH, DELETE all work and every mutation is persisted to db.json on disk (re-read the file to prove it).
[ ] `?field=value` filtering returns the correct subset; multiple filters AND together.
[ ] `?_page` + `?_limit` pagination and `?_sort` (+ `?_order`) sorting work as specified.
[ ] CORS headers are present on responses and OPTIONS preflight returns success.
[ ] New records get a correctly auto-incremented (or UUID) id; ids don't collide.
[ ] Missing/empty db.json auto-generates a usable sample and the server serves it.
[ ] 404 on unknown id, clear JSON error on malformed body — no raw stack-trace 500s.
[ ] File writes are atomic (temp file + os.replace), confirmed by reading server.py.

STOP CONDITIONS: Stop when EVERY checklist item passes, OR after 6 build rounds — whichever comes first. Make sure no test server is left running. Then give me a short summary: what works, any checklist item still failing (with why), and the exact commands to start it and hit a couple of endpoints.
```

---

## Remix ideas
Add a `--watch` mode that hot-reloads when db.json changes on disk · Add basic relational expansion (`?_embed=comments`, `?_expand=user`) like json-server · Add a tiny request-logging middleware with colored output · Add optional bearer-token auth toggled by an env var.
