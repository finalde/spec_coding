# Follow-up draft 065 — 2026-05-17

Two coupled changes:

1. **Add a file-size guideline** to `agent_refs/project/development.md` §1: prefer `< 100 lines`, split by sub-concern (matching the layer's role taxonomy) when bigger. Hard cap around `~1000` lines without a clear sub-concern boundary = stage-5 `warning`.
2. **Apply the rule to `apps/api/routes.py`** (847 lines): split into `apps/api/routes/{aggregate}__route.py`, mirroring the per-aggregate layout used in `libs/application/{queries,commands}/`.

## Required moves

### 1. New file-size rule (common-level, in `agent_refs/project/development.md` §1)

Inserted right after the dependency-direction subsection. Guideline only, not a hard cap. Aggregates with genuinely complex business logic (e.g., variance pools + prompt assembly + Kling client wrapper) may legitimately exceed. Split direction is dictated by the layer's existing taxonomy:
- A `routes.py` with all endpoints splits by aggregate into `routes/{aggregate}__route.py`.
- A `*__writer.py` past ~500 lines may split by operation IF operations don't share private state; otherwise size is justified.
- A `*__dto.py` past ~200 lines may split into `__qdto.py` + `__cdto.py` ONLY when it materially helps readability.

### 2. Routes split: `apps/api/routes.py` (847 lines) → `apps/api/routes/{aggregate}__route.py`

8 per-aggregate route files + a shared helpers module + a combined-router package init:

| File | Endpoints | Lines |
|---|---|---|
| `apps/api/routes/tree__route.py` | `GET /api/tree` | ~18 |
| `apps/api/routes/file__route.py` | `GET /api/file`, `PUT /api/file` | ~81 |
| `apps/api/routes/media__route.py` | serve / archive / unarchive / delete / hard-delete / rename + 6 method-not-allowed | ~204 |
| `apps/api/routes/frame__route.py` | `POST /api/extract-frames` | ~54 |
| `apps/api/routes/downloads__route.py` | `POST /api/import-from-downloads` | ~44 |
| `apps/api/routes/actor__route.py` | generate / generate-diverse / preview-prompts / preview-diverse / list / delete / assignments + helpers | ~238 |
| `apps/api/routes/casting__route.py` | read / assign / unassign | ~105 |
| `apps/api/routes/character_video__route.py` | truncate / concat-shot | ~84 |

Plus:
- `apps/api/routes/_helpers.py` (~55 lines): shared `file_security_headers`, `method_not_allowed`, `actor_assigned_409`, `map_move_failure`.
- `apps/api/routes/__init__.py` (~30 lines): combines the 8 sub-routers into a single `router` that `app_factory.py` mounts.

Each per-aggregate file owns its Pydantic request bodies (no shared `_bodies.py`). Aggregate-specific helpers (e.g. actor's `_generate_input` / `_diverse_input`) live with their handlers.

### 3. Container wiring: `wiring_config` switched from `modules=` to `packages=`

`apps/api/container.py`:
```python
wiring_config = containers.WiringConfiguration(packages=["apps.api.routes"])
```
This auto-wires every per-aggregate route module's `@inject` decorators. Same change in `apps/api/asgi.py`, `apps/api/main.py`, `tests/conftest.py` for the explicit `container.wire(...)` calls.

### 4. App factory unchanged

`apps/api/app_factory.py` still `from apps.api.routes import router` — the `routes/__init__.py` exposes the combined router. Single mount line `app.include_router(router)`.

### 5. Test imports updated

`tests/conftest.py`, `tests/test_api_security_three_shapes.py`, `tests/test_boot_smoke.py`: `from apps.api.routes import create_app` → `from apps.api.app_factory import create_app`. (`create_app` has lived in `app_factory.py` since follow-up 051; the tests were still importing from the legacy location.)

### 6. Pre-turn recovery: 11 OLD-path imports + 5 dupe flat infra files

The turn opened in an inconsistent state where some files had been rolled back to pre-056 paths while sub-bucket folders and aggregate Q/C files from follow-ups 056–061 still existed. Resolved by:
- Moving the 5 surviving flat infra files into their sub-folders (`casting__writer.py`, `file__writer.py`, `file__reader.py`, `tree__reader.py`, `origin_host__middleware.py`).
- Deleting the 5 superseded flat infra files (`actor_pool__writer.py`, `downloads__importer.py`, `frame__extractor.py`, `media__archiver.py`, `media__renamer.py`) — the writers/ sub-folder versions are newer (contain follow-up 052/053/054 work).
- Bulk-rewriting 17 OLD-path imports across 7 files via Python regex sweep.
- Restoring `apps/api/container.py` to the post-061 state (aggregate Q/C Factory providers).
- Restoring `agent_refs/project/development.md` §1 sub-bucketing tree + file-per-aggregate / one-class-per-Q/C-file / routes-mirror rules.
- Restoring `CLAUDE.md` § Project rules bullets (solution-layout mandate + commands-via-domain + file-size guideline).

The broader common-ref work from follow-ups 051/056/060/061 (§6b empty-application-layer blocker, §11b validation grep checks, §3 application-layer rewrite, §4 file-pattern table) was NOT fully restored in this follow-up — those can be re-added in a separate cleanup if the user wants the institutional memory back in agent_refs.

## Out of scope

- HTTP route paths + JSON shapes (byte-identical).
- Re-applying the deeper deferred work from follow-up 051 (e.g., splitting `actor__writer.py` 1985 lines into `kling__client.py` + `actor__dao.py` + `actor__reader.py` + `actor__writer.py`).
- Aggressively splitting other >100-line files. The rule is a guideline; existing larger aggregates stay where they are unless a sub-concern axis emerges.

## Acceptance trigger

- Pytest baseline preserved: 18 pass / 5 pre-existing wukong fixture failures.
- App constructs cleanly via `apps.api.app_factory.create_app(container, serve_static=False)`; route count matches pre-split.
- `wc -l apps/api/routes/*.py` shows each file is well under the 800-line legacy size.
- `import apps.api.routes` resolves to the package (with the combined `router` attribute), not a leftover `routes.py`.
