# Follow-up draft 014 — 2026-05-13

Adopt the solution-layout + DDD + CQRS conventions established in `.claude/agent_refs/project/development.md` (rules §1–6).

## Required structural changes

1. **Top-level reshape** of `projects/spec_driven/` to:
   - `apps/api/` (was `backend/`) — thin FastAPI wrapper. Contains `main.py`, `container.py`, `routes/`. No business logic.
   - `apps/ui/` (was `frontend/`) — React app, native structure preserved.
   - `libs/` — exactly four subfolders: `infrastructure/`, `domain/`, `application/`, `common/`.
   - `tests/` at solution root mirroring the apps/+libs/ tree.
   - `pyproject.toml`, `requirements.txt`, `Makefile`, `README.md` at solution root.

2. **`libs/` layering and dependency arrows** per `development.md` §1: infrastructure→common only; domain→common only; application→all three; common→none. App code only ever imports from `application` and `common`.

3. **DDD inside `libs/domain/`** per §2: rich entities, frozen value objects, aggregate roots, named domain errors (no raw `ValueError`), domain events when state changes warrant publication, repository protocols owned by domain.

4. **CQRS in `libs/infrastructure/` + `libs/application/`** per §3: every operation is a `__query.py`/`__command.py` pair; readers/writers split; DAO/Entity/QDto/CDto have distinct types; mapping concentrated in `__mapper.py` files in the application layer.

5. **`__` filename + classname suffix** per §4 across every layer.

6. **`dependency_injector`** per §5: introduce `apps/api/container.py`, wire it from `apps/api/main.py`, refactor FastAPI handlers to receive Queries/Commands via `@inject`.

## Concrete file moves (initial mapping)

- `backend/main.py` → `apps/api/main.py` (thinner: builds container, mounts routes)
- `backend/libs/api.py` → split into `apps/api/routes/*.py` (transport only) + `libs/application/*` (handlers)
- `backend/libs/api_security.py` → `libs/infrastructure/origin_host__middleware.py`
- `backend/libs/file_reader.py` → `libs/infrastructure/file__reader.py`, with the DAO extracted to `libs/infrastructure/file__dao.py`; a corresponding `libs/application/read_file__query.py` + `read_file__qdto.py` + `file__mapper.py`
- `backend/libs/file_writer.py` → `libs/infrastructure/file__writer.py` + `libs/application/write_file__command.py` + `write_file__cdto.py`
- `backend/libs/exposed_tree.py`, `safe_resolve.py`, `repo_root.py` → `libs/common/` (no domain content; pure utilities + config)
- `backend/libs/promotions.py` → split: `libs/domain/promotion__entity.py` + `libs/domain/promotion__error.py` + `libs/infrastructure/promotion__reader.py` + `promotion__writer.py` + `libs/application/add_promotion__command.py` + `remove_promotion__command.py` + `promotion__cdto.py` + `promotion__mapper.py`
- `backend/libs/regen_prompt.py` → `libs/application/build_regen_prompt__query.py` + `regen_prompt__qdto.py`; the file-reading bits used to assemble the prompt live in infrastructure
- `backend/libs/project_deleter.py` → `libs/application/delete_project__command.py` + `libs/infrastructure/project_directory__writer.py` (destructive infra op) + `delete_project__cdto.py`; domain error `ProjectDeletionError` in `libs/domain/`
- `backend/libs/tree_walker.py` → `libs/infrastructure/tree__reader.py` + `libs/application/get_tree__query.py` + `tree__qdto.py`
- `backend/libs/stages.py` → `libs/common/stages.py` (pure enum + payload constants)

## Out of scope

- API contract changes (HTTP routes, request/response JSON shapes stay byte-identical to v1; only the internal organization changes).
- Frontend code restructure (apps/ui/ keeps its existing structure).
- Test rewrites beyond import-path updates.
