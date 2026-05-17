# Follow-up draft 059 — 2026-05-17

Consolidate per-operation files into one-file-per-aggregate within each role sub-folder. After follow-up 056 the per-role sub-folders were created (`application/{queries,commands,dtos,mappers}`, etc.) but each sub-folder still held one file per operation: 15 commands, 12 DTOs, 7 queries. Roll them up so each aggregate gets a single file per role.

## Required moves

### 1. `libs/application/commands/` — 15 files → 7

- `actor__command.py` ← `generate_actors__command.py` + `generate_diverse_actors__command.py` + `delete_actor__command.py`
- `casting__command.py` ← `assign_actor__command.py` + `unassign_actor__command.py`
- `media__command.py` ← `archive_media__command.py` + `unarchive_media__command.py` + `delete_media__command.py` + `hard_delete_media__command.py` + `rename_media__command.py`
- `file__command.py` ← `write_file__command.py`
- `frame__command.py` ← `extract_frames__command.py`
- `downloads__command.py` ← `import_from_downloads__command.py`
- `character_video__command.py` ← `truncate_character_video__command.py` + `concat_shot_characters__command.py`

### 2. `libs/application/queries/` — 7 files → 5

- `actor__query.py` ← `list_actors__query.py` + `preview_actor_prompts__query.py` + `get_actor_assignments__query.py`
- `casting__query.py` ← `read_casting__query.py`
- `media__query.py` ← `serve_media__query.py`
- `file__query.py` ← `read_file__query.py`
- `tree__query.py` ← `get_tree__query.py`

### 3. `libs/application/dtos/` — 12 files → 8

Each aggregate gets one `{aggregate}__dto.py` holding BOTH its Qdtos and Cdtos. The `Qdto` / `Cdto` suffix on each class name already disambiguates Query-vs-Command intent within the file.

- `actor__dto.py` ← `actor__qdto.py` + `actor__cdto.py`
- `casting__dto.py` ← `casting__qdto.py` + `casting__cdto.py`
- `media__dto.py` ← `media__qdto.py` + `media__cdto.py`
- `file__dto.py` ← `file__qdto.py` + `file__cdto.py`
- `frame__dto.py` ← `frame__cdto.py` (renamed)
- `downloads__dto.py` ← `downloads__cdto.py` (renamed)
- `tree__dto.py` ← `tree__qdto.py` (renamed)
- `character_video__dto.py` ← `character_video__cdto.py` (renamed)

### 4. `libs/application/mappers/` — already aggregate-named, no change

`actor__mapper.py`, `casting__mapper.py`, `media__mapper.py`, `file__mapper.py`, `frame__mapper.py`, `downloads__mapper.py`, `character_video__mapper.py` — these already followed the per-aggregate convention; only their import paths shift to the new DTO names.

### 5. `libs/domain/value_objects/` — 6 files → 5

- `actor__valueobject.py` ← `actor_attrs__valueobject.py` (renamed)
- `casting__valueobject.py` ← `cast_entry__valueobject.py` (renamed)
- `drama__valueobject.py` ← `drama_path__valueobject.py` (renamed)
- `frame__valueobject.py` ← `frame_spec__valueobject.py` (renamed)
- `media__valueobject.py` ← `media_path__valueobject.py` + `archive_state__valueobject.py` (merged — both belong to media aggregate)

### 6. `libs/domain/errors/` — 7 files → 7 (rename only)

- `file__error.py` ← `file_resource__error.py` (renamed for naming consistency)
- All others (`actor__error.py`, `casting__error.py`, `character_video__error.py`, `downloads__error.py`, `frame__error.py`, `media__error.py`) already follow the convention.

### 7. `libs/domain/entities/` + `libs/domain/repositories/` — no change

Already aggregate-named.

### 8. `libs/infrastructure/writers/` — 9 files → 7

- `actor__writer.py` ← `actor_pool__writer.py` (renamed)
- `casting__writer.py` (no change)
- `character_video__writer.py` ← `character_video__truncator.py` + `shot_concat__builder.py` (merged — both belong to character_video aggregate; shared exceptions `InvalidPath` / `NotFound` / `FfmpegMissing` deduplicated)
- `downloads__writer.py` ← `downloads__importer.py` (renamed)
- `file__writer.py` (no change)
- `frame__writer.py` ← `frame__extractor.py` (renamed)
- `media__writer.py` ← `media__archiver.py` + `media__renamer.py` (merged — both belong to media aggregate; no name conflicts)

### 9. `libs/infrastructure/readers/` + `libs/infrastructure/middleware/` — no change

Already aggregate-named.

### 10. All imports rewritten

A single Python regex sweep across `apps/`, `libs/`, `tests/` updates every `from libs.X.{old_module} import` to point at the new aggregate file. Wiring config in `apps/api/container.py` (`wiring_config = WiringConfiguration(modules=["apps.api.routes"])`) unchanged.

## Common-level rule update

`agent_refs/project/development.md` §1 gains:
- **File-per-aggregate rule**: each role sub-folder holds `{aggregate}__{role}.py` files; one file per aggregate per role; all operations of that role for that aggregate live in the same file, disambiguated by class name.
- **DTO consolidation note**: `{aggregate}__dto.py` holds BOTH Qdtos and Cdtos — the class-name suffix is the disambiguator.
- **Legacy-name merge note**: two legacy-suffix files for the same aggregate (e.g., `media__archiver.py` + `media__renamer.py`) merge into `{aggregate}__writer.py`.

§4 file-pattern table updated to show one row per aggregate-named file with example class lists. Anti-pattern callout: do NOT use the old one-file-per-operation layout.

`agent_refs/validation/development.md` §11b grep #2 changed from "file count ≥ 19" to **class count via `grep -hE "^class \\w+(Command|Query)\\b" libs/application/{commands,queries}/*.py`** — the new layout's file count is #aggregates, so estimating endpoint coverage requires counting classes.

`CLAUDE.md` § Project rules solution-layout bullet expanded to mention the file-per-aggregate rule.

## Out of scope

- Renaming class names within the aggregate files. `GenerateActorsCommand` and `DeleteActorCommand` stay as-is — the file name aggregates them; the class name remains the operation name.
- Changing HTTP route paths or JSON shapes (byte-identical).
- Frontend (`apps/ui/`) — unaffected.
- Test mirror-tree creation (deferred per follow-up 051 §7).

## Acceptance trigger

- Pytest baseline preserved: 18 pass / 5 pre-existing wukong fixture failures.
- §11b updated gates pass: routes.py 0 infra imports; Q+C class count ≥ 19; every `*__command.py` imports from `libs.domain`.
- `ls libs/application/commands/` shows 7 aggregate files + `__init__.py`. `ls libs/application/queries/` shows 5. `ls libs/application/dtos/` shows 8.
- No file with `generate_actors__command.py` / `archive_media__command.py` / `actor__qdto.py` / `actor__cdto.py` / etc. shape remains under `libs/`.
