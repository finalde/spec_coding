# Follow-up draft 051 — 2026-05-17

Implement the application + domain layers that follow-up 039 promised but never produced. Currently `apps/api/routes.py` imports and depends on `libs.infrastructure.*` classes directly; `libs/application/` and `libs/domain/` contain only empty `__init__.py`. This violates `.claude/agent_refs/project/development.md` §1 (dependency arrows: apps may NOT import from infrastructure) and §3 (every endpoint is a Query or Command).

## Required moves

### 1. `libs/application/` populated with one Query or Command per endpoint

Every route handler in `apps/api/routes.py` must call exactly one application-layer Query or Command. Mapping (read = Query, state-change = Command):

| Endpoint | Class | File |
|---|---|---|
| `GET /api/tree` | `GetTreeQuery` | `libs/application/get_tree__query.py` |
| `GET /api/file` | `ReadFileQuery` | `libs/application/read_file__query.py` |
| `PUT /api/file` | `WriteFileCommand` | `libs/application/write_file__command.py` |
| `GET /api/media` | `ServeMediaQuery` | `libs/application/serve_media__query.py` |
| `POST /api/rename-media` | `RenameMediaCommand` | `libs/application/rename_media__command.py` |
| `POST /api/archive-media` | `ArchiveMediaCommand` | `libs/application/archive_media__command.py` |
| `POST /api/unarchive-media` | `UnarchiveMediaCommand` | `libs/application/unarchive_media__command.py` |
| `POST /api/delete-media` | `DeleteMediaCommand` | `libs/application/delete_media__command.py` |
| `POST /api/hard-delete-media` | `HardDeleteMediaCommand` | `libs/application/hard_delete_media__command.py` |
| `POST /api/extract-frames` | `ExtractFramesCommand` | `libs/application/extract_frames__command.py` |
| `POST /api/import-from-downloads` | `ImportFromDownloadsCommand` | `libs/application/import_from_downloads__command.py` |
| `POST /api/actors/generate` | `GenerateActorsCommand` | `libs/application/generate_actors__command.py` |
| `POST /api/actors/preview-prompts` | `PreviewActorPromptsQuery` | `libs/application/preview_actor_prompts__query.py` |
| `GET /api/actors` | `ListActorsQuery` | `libs/application/list_actors__query.py` |
| `POST /api/actors/delete` | `DeleteActorCommand` | `libs/application/delete_actor__command.py` |
| `GET /api/actors/assignments` | `GetActorAssignmentsQuery` | `libs/application/get_actor_assignments__query.py` |
| `GET /api/casting` | `ReadCastingQuery` | `libs/application/read_casting__query.py` |
| `POST /api/casting/assign` | `AssignActorCommand` | `libs/application/assign_actor__command.py` |
| `DELETE /api/casting/assign` | `UnassignActorCommand` | `libs/application/unassign_actor__command.py` |

Per development.md §3 read-side simplification: every Query may bypass aggregates and load via Reader → Qdto. Every Command MUST go through the domain layer (load aggregate via Reader → invoke method that enforces invariants → persist via Writer).

### 2. `libs/domain/` populated with entities + value objects + repository protocols

Carve out from existing infrastructure modules into `libs/domain/`:

- **Actor aggregate** — `actor__entity.py` (`ActorEntity` — has identity `actor_id`, holds `ActorAttrs`), `actor_attrs__valueobject.py` (`ActorAttrs` — already exists as frozen dataclass in `actor_pool__writer.py`; move to domain), `actor__repository.py` (`ActorRepository` Protocol — `exists`, `load`, `list`, `next_id`, `save`, `delete`), `actor__error.py` (`InvalidActorAttribute`, `ActorNotFoundError`, `ActorAlreadyAssignedError`, ...). Move the prompt-building (`_build_prompt`, `_variance_for`, `_build_sidecar`) into a domain service `actor_prompt__valueobject.py` — the prompt text IS business logic (anti-wax recipe per follow-up 031, variance pools per 029, ≥1000-char invariant); it is NOT physical I/O. The Kling HTTP client stays in infrastructure (`kling__client.py`).
- **Casting aggregate** — `casting__entity.py` (`CastingEntity` — per-drama aggregate root, holds `list[CastEntryValueObject]`; methods `assign(role, actor_id, notes)`, `unassign(role)` enforce uniqueness invariants), `cast_entry__valueobject.py` (`CastEntryValueObject` — role+actor_id+notes frozen), `casting__repository.py` (Protocol — `load_by_drama`, `save`, `scan_assignments_for_actor`), `casting__error.py` (`InvalidRoleError`, `RoleNotFoundError`).
- **Media value objects** — `media_path__valueobject.py` (path classification: ai_video, archived, deleted, actor), `archive_state__valueobject.py` (enum-ish: LIVE/ARCHIVED/SOFT_DELETED). Infrastructure `MediaArchiver` becomes a Writer over these; the LIVE→ARCHIVED→SOFT_DELETED→HARD_DELETED transitions are enforced in domain.
- **Frame extraction value object** — `frame_spec__valueobject.py` (the 8-frame rank/shot_size schedule from follow-up 041 is domain knowledge, not infrastructure). `ffmpeg__client.py` stays in infrastructure.
- **Drama path value object** — `drama_path__valueobject.py` (the `ai_videos/{drama}/...` invariants currently scattered across `MediaRenamer.validate_drama`, `Casting.assign`, archiver path checks).

Domain code imports nothing from `libs.infrastructure` or `libs.application` — pure Python + `libs.common`. The Protocols in `domain/{aggregate}__repository.py` are the only dependency-inversion seam.

### 3. `libs/infrastructure/` becomes Reader / Writer / Dao only

Existing files split / rename:

- `actor_pool__writer.py` (1248 lines) → `actor__reader.py` (`ActorReader.list`, `load`, `exists`, `next_id`, `find_jpg`) + `actor__writer.py` (`ActorWriter.save`, `delete`, `migrate_filenames`, `reap_incomplete`) + `actor__dao.py` (`ActorDao` mirroring on-disk md+jpg) + `kling__client.py` (HTTP only — `submit`, `poll`, `download`). The classes implement the domain `ActorRepository` Protocol.
- `casting__writer.py` → `casting__reader.py` (`load_by_drama`, `scan_for_actor`) + `casting__writer.py` (`save`, `write_cast_link`, `remove_cast_link`, `copy_face`, `sweep_cast_dir`) + `cast_entry__dao.py`.
- `media__archiver.py` → `media__writer.py` (the four file-move operations).
- `media__renamer.py` → `drama__reader.py` (`validate_drama` → load aggregate) + `media__writer.py` rename method.
- `frame__extractor.py` → `frame__writer.py` (writes jpgs into `frames/`) + `ffmpeg__client.py` (subprocess wrapper). Frame-rank/shot_size selection moves to domain.
- `downloads__importer.py` → `downloads__reader.py` (Downloads dir scan) + reuses `media__writer.py`.
- `file__reader.py`, `file__writer.py`, `tree__reader.py` stay as is (already pure I/O — but their result objects move out into `__dao.py` if they currently double as DTOs).
- `origin_host__middleware.py` stays (FastAPI middleware — naturally lives at the transport edge but accepted under `infrastructure/` since it's framework adapter code).

### 4. `libs/application/` gets `__qdto.py`, `__cdto.py`, `__mapper.py` files

Per development.md §3:

- Every Query writes its own `{name}__qdto.py` (frozen dataclass) — for the API response shape.
- Every Command writes its own `{name}__cdto.py` (frozen dataclass) — for input + output.
- Every aggregate gets a `{name}__mapper.py` in `libs/application/` — owns ALL mapping among DAO ↔ Entity/ValueObject ↔ QDto/CDto. The `.to_payload()` / `.to_dict()` methods currently scattered across infrastructure result classes (`CastingResult.to_payload`, `GenerateResult.to_payload`, `ExtractedFrame.to_payload`, etc.) move into mappers; the DAOs and Entities themselves don't know about JSON shape.

### 5. `apps/api/routes.py` becomes thin transport

After the refactor:

- Zero `from libs.infrastructure` imports in `routes.py`. (If a route handler still needs an infrastructure type, the application-layer Query/Command did not absorb the responsibility — fix the application layer, not the route.)
- Every handler body is ≤ 3 lines: try → call `query.execute(...)` or `command.execute(...)` → return DTO; except → map domain error to HTTP shape.
- Pydantic request bodies stay in `routes.py` (transport-layer shapes); they are constructed into `__cdto` inputs before calling `.execute()`.
- HTTP-error-mapping table (which domain error → which HTTP status / `kind` payload) lives in one helper in `routes.py` — the application layer has no knowledge of HTTP.

### 6. `apps/api/container.py` exposes application-layer providers

- Keep current infrastructure Singletons (Readers / Writers / Clients).
- Add Factory providers for every Query, Command, Mapper.
- `wiring_config` already targets `apps.api.routes`; no change needed.
- Route handlers receive Query / Command instances, NOT infrastructure instances.

### 7. Tests updated for layered import paths

Existing tests (`test_boot_smoke.py`, `test_api_security_three_shapes.py`, `test_tree_walker_consumer_walk.py`, `test_sub_type_lookup.py`, `conftest.py`) currently override or import from `libs.infrastructure.*`. After the refactor:

- Boot smoke + api security tests should not need changes (they hit HTTP).
- Tree walker test moves to `tests/libs/application/test_get_tree__query.py` (queries the application layer) plus a `tests/libs/infrastructure/test_tree__reader.py` for pure infra.
- New unit tests for each Query / Command using `container.x.override(stub)` per development.md §5.
- Add `tests/libs/domain/` with pure unit tests for entities + value objects (no I/O).

### 8. Common refs sharpened so this never silently re-happens

- `.claude/agent_refs/project/development.md` gains a new rule: empty `libs/application/` while `apps/*` imports from `libs/infrastructure/` is a stage-5 `blocker`. Cite this incident.
- `.claude/agent_refs/validation/development.md` gains a matching severity row.

## Out of scope

- HTTP route paths + JSON response shapes (byte-identical contracts).
- Frontend (`apps/ui/`) — unaffected; consumes the same JSON shapes.
- Cross-aggregate refactors beyond what's needed to make commands go through domain (e.g., we don't introduce domain events in v1 — the rule allows it but no current endpoint demands it).
- Migrating to async route handlers (sync `def` is the established convention per follow-up 042's uvicorn watchdog rationale).

## Acceptance trigger

After this follow-up lands:

- `grep -E "^from libs\\.infrastructure" projects/ai_video_management/apps/api/routes.py` returns zero lines.
- `find projects/ai_video_management/libs/application -name "*.py" -type f | wc -l ≥ 19` (one Query / Command per endpoint, ignoring `__init__.py`).
- `find projects/ai_video_management/libs/domain -name "*.py" -type f | wc -l ≥ 1` (at least the carved-out aggregates).
- Existing `pytest` suite passes without functional changes (only import-path updates).
