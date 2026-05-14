# Follow-up draft 039 — 2026-05-13

Adopt the solution-layout + DDD + CQRS conventions established in `.claude/agent_refs/project/development.md` (rules §1–6).

## Required structural changes

1. **Top-level reshape** of `projects/ai_video_management/` to:
   - `apps/api/` (was `backend/`) — thin FastAPI wrapper. `main.py`, `container.py`, `routes/`.
   - `apps/ui/` (was `frontend/`) — React app, native structure preserved.
   - `libs/` — exactly four subfolders: `infrastructure/`, `domain/`, `application/`, `common/`.
   - `tests/` at solution root mirroring apps/+libs/.
   - `pyproject.toml`, `requirements.txt`, `Makefile`, `README.md` at solution root.

2. **`libs/` layering and dependency arrows** per `development.md` §1: one-way arrows, app code only imports from `application` and `common`.

3. **DDD inside `libs/domain/`** per §2: rich entities, frozen value objects, aggregate roots, named domain errors, repository protocols.

4. **CQRS in `libs/infrastructure/` + `libs/application/`** per §3: queries/commands separated, readers/writers separated, DAO/Entity/QDto/CDto distinct, mappers in application.

5. **`__` filename + classname suffix** per §4.

6. **`dependency_injector`** per §5.

## Concrete file moves (initial mapping)

- `backend/main.py` → `apps/api/main.py`
- `backend/libs/api.py` → split into `apps/api/routes/*.py` + multiple `libs/application/` queries+commands
- `backend/libs/api_security.py` → `libs/infrastructure/origin_host__middleware.py`
- `backend/libs/asgi.py` → `apps/api/asgi.py` (entrypoint helper, app concern)
- `backend/libs/env_loader.py` → `libs/common/env_loader.py` (utility, no domain)
- `backend/libs/repo_root.py`, `safe_resolve.py`, `exposed_tree.py`, `sub_type_lookup.py` → `libs/common/`
- `backend/libs/file_reader.py` / `file_writer.py` → `libs/infrastructure/file__reader.py` / `file__writer.py` + `file__dao.py`; app-layer wrappers `read_file__query.py` / `write_file__command.py` + DTOs + `file__mapper.py`
- `backend/libs/tree_walker.py` → `libs/infrastructure/tree__reader.py` + `libs/application/get_tree__query.py`
- `backend/libs/frame_extractor.py` → split: domain logic in `libs/domain/frame__valueobject.py` (timestamps, ranges) + infra `libs/infrastructure/ffmpeg__client.py` + `frame__writer.py` + `libs/application/extract_frame__command.py` + `extract_frame__cdto.py`
- `backend/libs/media_archiver.py` → `libs/application/archive_media__command.py` + `unarchive_media__command.py` + `libs/infrastructure/media__writer.py` (filesystem moves); domain: `media__entity.py`, `archive_state__valueobject.py`
- `backend/libs/media_renamer.py` → `libs/application/rename_media__command.py` + infrastructure file-rename writer; domain: `MediaName` value object
- `backend/libs/downloads_importer.py` → `libs/application/import_downloads__command.py` + `libs/infrastructure/downloads__reader.py` + classifier domain logic
- `backend/libs/actor_pool.py` + `casting.py` → domain heart: `actor__entity.py`, `actor_pool__aggregate.py`, `casting__valueobject.py`; app-layer commands `pick_actor__query.py`, `assign_actor__command.py`; infra reader/writer for the actor pool folder

## Out of scope

- API contract changes (HTTP routes + JSON shapes stay byte-identical).
- Frontend code restructure.
- Test rewrites beyond import-path updates.
- Mid-flight uncommitted edits in working tree (12 M files at follow-up time) are preserved into the migrated layout.
