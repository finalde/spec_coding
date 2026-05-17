# Follow-up draft 061 — 2026-05-17

Collapse each `{aggregate}__{command,query}.py` from multi-class-per-file to **one class per aggregate, one method per operation**. After follow-up 060 each aggregate file held N command/query classes (e.g., `actor__command.py` had `GenerateActorsCommand` + `GenerateDiverseActorsCommand` + `DeleteActorCommand` as three sibling classes). This follow-up rolls them into a single `ActorCommand` class with three methods (`generate`, `generate_diverse`, `delete`). The operation name lives on the **method**, not the class or the filename.

## Required moves

### 1. `libs/application/commands/` — one class per file

Every `*__command.py` now defines exactly ONE class `{Aggregate}Command` with one method per operation.

| File | Class | Methods |
|---|---|---|
| `actor__command.py` | `ActorCommand` | `generate`, `generate_diverse`, `delete` |
| `casting__command.py` | `CastingCommand` | `assign`, `unassign` |
| `media__command.py` | `MediaCommand` | `archive`, `unarchive`, `delete`, `hard_delete`, `rename` |
| `file__command.py` | `FileCommand` | `write` |
| `frame__command.py` | `FrameCommand` | `extract` |
| `downloads__command.py` | `DownloadsCommand` | `import_drama` |
| `character_video__command.py` | `CharacterVideoCommand` | `truncate`, `concat_shot` |

Constructor dependencies are the **union** of operation dependencies. `MediaCommand.__init__(archiver, renamer, casting)` carries all three because `archive`/`unarchive`/`delete`/`hard_delete` use `archiver`, `rename` uses `renamer`, `delete` uses `casting` for the cross-aggregate refuse-if-assigned check.

### 2. `libs/application/queries/` — one class per file

| File | Class | Methods |
|---|---|---|
| `actor__query.py` | `ActorQuery` | `list`, `preview_prompts`, `get_assignments` (+ `preview_diverse_prompts` from follow-up 059) |
| `casting__query.py` | `CastingQuery` | `read` |
| `media__query.py` | `MediaQuery` | `serve` |
| `file__query.py` | `FileQuery` | `read` |
| `tree__query.py` | `TreeQuery` | `build` |

### 3. `apps/api/container.py` — 12 Factory providers (down from 22 after follow-up 060's class-per-operation layout)

One Factory per aggregate Q/C class:

```python
actor_command   = Factory(ActorCommand, pool=actor_pool, casting=casting)
casting_command = Factory(CastingCommand, casting=casting)
media_command   = Factory(MediaCommand, archiver=media_archiver, renamer=media_renamer, casting=casting)
file_command    = Factory(FileCommand, writer=file_writer)
frame_command   = Factory(FrameCommand, extractor=frame_extractor)
downloads_command = Factory(DownloadsCommand, importer=downloads_importer)
character_video_command = Factory(CharacterVideoCommand, truncator=…, builder=…)
actor_query     = Factory(ActorQuery, pool=actor_pool, casting=casting)
casting_query   = Factory(CastingQuery, casting=casting)
media_query     = Factory(MediaQuery, exposed=…, resolver=…)
file_query      = Factory(FileQuery, reader=file_reader)
tree_query      = Factory(TreeQuery, reader=tree_reader)
```

### 4. `apps/api/routes.py` — handlers call aggregate methods

Each handler injects the aggregate Q/C and calls the method matching the endpoint's operation:

```python
@router.post("/api/actors/generate")
def actors_generate(body, command: ActorCommand = Depends(Provide[Container.actor_command])):
    cdto = command.generate(_generate_input(body))
    ...

@router.post("/api/archive-media")
def archive_media(body, command: MediaCommand = Depends(Provide[Container.media_command])):
    cdto = command.archive(body.path)
    ...
```

### 5. The `execute()` convention is retired

The earlier development.md draft mandated each Command/Query class expose `execute(...)`. With method-per-operation that no longer fits — `ActorCommand.execute()` would have to dispatch on a discriminator. Replaced by named methods that match the operation.

## Common-level rule update

- `agent_refs/project/development.md` §1 — "One class per aggregate file, one method per operation" rule added (separates Q/C from DTO files: Q/C are single-class; DTOs can be multi-class because they're pure data).
- `agent_refs/project/development.md` §3 — Application layer §3 rewritten: classes are named `{Aggregate}Query` / `{Aggregate}Command`; methods are named after operations; `execute()` convention retired.
- `agent_refs/project/development.md` §4 — file-pattern table rows for `*__command.py` / `*__query.py` updated to show "One class … with methods …"; anti-pattern list extended to retire (a) per-operation FILES, (b) per-operation CLASSES in same file, (c) `execute()` method name.
- `agent_refs/validation/development.md` §11b — grep #2 changed from "class count" to "method count" (`grep -hE "^    def [a-z]\w*\(" ... | grep -v "^    def _"`); new grep #4 enforces "exactly one class per `*__command.py` / `*__query.py`".
- `CLAUDE.md` § Project rules solution-layout bullet — updated to call out one-class-per-file for Q/C, multi-class allowed for DTOs.

## Out of scope

- HTTP route paths + JSON shapes (byte-identical).
- DTOs / mappers / domain / infrastructure layers (unchanged).
- Frontend (`apps/ui/`) — unaffected.

## Acceptance trigger

- Pytest baseline preserved: 18 pass / 5 pre-existing wukong fixture failures.
- §11b updated gates pass: routes.py 0 infra imports; method count ≥ 19; commands import libs.domain; exactly one class per `*__command.py` / `*__query.py`.
- 12 Factory providers in `apps/api/container.py` (one per aggregate Q/C).
- No file under `libs/application/commands/` or `libs/application/queries/` contains more than one `^class \w+(Command|Query)\b` declaration.
