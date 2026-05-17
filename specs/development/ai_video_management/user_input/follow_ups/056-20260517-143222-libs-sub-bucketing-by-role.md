# Follow-up draft 056 — 2026-05-17

Sub-bucket every `libs/` layer by file role (per-suffix sub-folder). The single-level layout from follow-up 039 packed 40+ files into one folder (`libs/application/`), making the file list hostile to navigation. Group files of the same role into a sub-folder named for the role (plural).

## Required moves

### 1. `libs/application/` gains four sub-folders

- `libs/application/queries/` — every `*__query.py` (7 files)
- `libs/application/commands/` — every `*__command.py` (15 files)
- `libs/application/dtos/` — every `*__qdto.py` + `*__cdto.py` (12 files in one folder; the `Q`/`C` suffix already disambiguates)
- `libs/application/mappers/` — every `*__mapper.py` (7 files)

### 2. `libs/domain/` gains four sub-folders

- `libs/domain/entities/` — every `*__entity.py` (2 files)
- `libs/domain/value_objects/` — every `*__valueobject.py` (6 files)
- `libs/domain/errors/` — every `*__error.py` (7 files)
- `libs/domain/repositories/` — every `*__repository.py` (2 files)

### 3. `libs/infrastructure/` gains three sub-folders for current content

- `libs/infrastructure/readers/` — `file__reader.py`, `tree__reader.py`
- `libs/infrastructure/middleware/` — `origin_host__middleware.py`
- `libs/infrastructure/writers/` — every `*__writer.py` PLUS the legacy mutator-suffix files (`*__importer.py`, `*__extractor.py`, `*__archiver.py`, `*__renamer.py`, `*__truncator.py`, `*__builder.py`). All nine fit the "mutates state" role. Renaming them to the canonical `*__writer.py` suffix per development.md §4 is a separate cleanup; the sub-bucketing rule does NOT require it.

`libs/infrastructure/clients/` and `libs/infrastructure/daos/` are referenced in the common-level rule but stay empty for v1 — no `*__client.py` / `*__dao.py` exist yet (those land when the actor-pool deep §3 split runs; see follow-up 051 deferred items). The empty folders are NOT pre-created in this follow-up — they materialize the moment the first file with that suffix lands.

### 4. `libs/common/` stays flat

No canonical role taxonomy applies (env_loader, exposed_tree, origin, repo_root, safe_resolve, sub_type_lookup are all utility primitives). Per the common-level rule's lone exception.

### 5. All imports updated

Every cross-module import path gains one component:

- `from libs.application.foo__query` → `from libs.application.queries.foo__query`
- `from libs.application.foo__command` → `from libs.application.commands.foo__command`
- `from libs.application.foo__qdto` → `from libs.application.dtos.foo__qdto`
- `from libs.application.foo__cdto` → `from libs.application.dtos.foo__cdto`
- `from libs.application.foo__mapper` → `from libs.application.mappers.foo__mapper`
- `from libs.domain.foo__entity` → `from libs.domain.entities.foo__entity`
- `from libs.domain.foo__valueobject` → `from libs.domain.value_objects.foo__valueobject`
- `from libs.domain.foo__error` → `from libs.domain.errors.foo__error`
- `from libs.domain.foo__repository` → `from libs.domain.repositories.foo__repository`
- `from libs.infrastructure.foo__reader` → `from libs.infrastructure.readers.foo__reader`
- `from libs.infrastructure.foo__{writer|importer|extractor|archiver|renamer|truncator|builder}` → `from libs.infrastructure.writers.foo__…`
- `from libs.infrastructure.foo__middleware` → `from libs.infrastructure.middleware.foo__middleware`

Wiring config in `apps/api/container.py` (`wiring_config = WiringConfiguration(modules=["apps.api.routes"])`) is unchanged — the route module path didn't move.

## Common-level rule update

`agent_refs/project/development.md` §1 + §4 + `CLAUDE.md` § Project rules updated to specify the sub-bucketing convention. Future development projects follow this layout by default.

`agent_refs/validation/development.md` §11b grep paths updated to walk the new tree (`libs/application/queries`, `libs/application/commands`, `libs/application/commands/*__command.py`).

## Out of scope

- Renaming legacy mutator-suffix files to canonical `*__writer.py`. That's tech debt for a separate follow-up; the bucketing rule explicitly does NOT require it.
- Test mirror-tree creation (`tests/libs/application/queries/...` etc.). The four existing tests still pass; deeper test tree lands when new unit tests are added (follow-up 051 §7 deferred).
- HTTP routes + JSON shapes (byte-identical, zero externally observable change).
- Frontend (`apps/ui/`) — unaffected.

## Acceptance trigger

- Pytest baseline preserved: 18 pass / 5 pre-existing wukong fixture failures.
- §11b grep gates pass against the new paths.
- `ls libs/application/` shows 4 sub-folders + `__init__.py` and nothing else (no loose `*__query.py` etc. at the layer root).
