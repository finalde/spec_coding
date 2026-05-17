# Follow-up draft 015 — 2026-05-17

Adopt the **evolved** project-output standard that `ai_video_management` has been progressively pulling into `.claude/agent_refs/project/development.md` (and the parallel `CLAUDE.md § Project rules` bullets) via follow-ups 056 / 060 / 061 / 065 / 068. Follow-up 014 already moved `spec_driven` onto `apps/` + `libs/{infrastructure,domain,application,common}/` with `__suffix` naming, DDD inside `libs/domain/`, CQRS across infrastructure + application, and `dependency_injector` wiring. This follow-up brings `spec_driven` the rest of the way — same standard, same project type (`development`), no carve-outs.

## What the evolved standard adds beyond follow-up 014

All five rules are already canonical in `.claude/agent_refs/project/development.md` §1 — this follow-up makes them load-bearing for `spec_driven` too, with concrete gap notes for the current code.

### 1. Per-role sub-bucketing within each layer (was: flat layer folders)

Each layer is broken out by role into named subfolders. Empty folders for canonical roles are allowed and document the convention. `common/` stays flat.

| Layer | Required sub-buckets |
|---|---|
| `libs/infrastructure/` | `readers/`, `writers/`, `clients/`, `daos/`, `middleware/`, `errors/` |
| `libs/domain/` | `entities/`, `value_objects/`, `errors/`, `repositories/` |
| `libs/application/` | `queries/`, `commands/`, `dtos/`, `mappers/` |

### 2. One file per aggregate per role: `{aggregate}__{role}.py`

The operation name lives on the method, not on the class or the filename. So:

- `libs/application/commands/add_promotion__command.py` (per-operation FILE) becomes `libs/application/commands/promotion__command.py` containing a single `PromotionCommand` class with methods `add(...)` and `remove(...)`. Old: `AddPromotionCommand.execute()` + `RemovePromotionCommand.execute()`. New: `PromotionCommand.add(...)` + `PromotionCommand.remove(...)`.
- `libs/application/queries/build_regen_prompt__query.py`, `get_stages__query.py`, `get_tree__query.py`, `read_file__query.py` collapse to one-per-aggregate where the aggregates align (`regen_prompt__query.py` keeps its own; `stages__query.py`, `tree__query.py`, `file__query.py`). Multi-operation aggregates (e.g., a future `file__query.py` reading metadata + content) get one method per operation.
- `libs/application/commands/delete_project__command.py` + `write_file__command.py` + the two promotion commands become `project__command.py`, `file__command.py`, `promotion__command.py` respectively.

### 3. DTOs consolidated: one `dtos/{aggregate}__dto.py` per aggregate, multi-class allowed

The current split across `*__qdto.py` + `*__cdto.py` collapses into a single per-aggregate dtos file (`promotion__dto.py`, `regen_prompt__dto.py`, `read_file__dto.py` → `file__dto.py`, `write_file__dto.py` → folded into `file__dto.py`, `delete_project__cdto.py` → `project__dto.py`, `tree__qdto.py` → `tree__dto.py`). The `Qdto`/`Cdto` class-name suffix disambiguates.

### 4. Routes split per aggregate

`apps/api/routes/` becomes a package with one file per aggregate (`file__route.py`, `tree__route.py`, `stages__route.py`, `regen_prompt__route.py`, `promotion__route.py`, `project__route.py`) each owning its own `APIRouter()`. `apps/api/routes/__init__.py` exposes a combined `router` that `apps/api/app_factory.py` mounts. The same one-Query-or-Command-per-handler rule applies — handler bodies stay thin.

### 5. SRP — one concern per file

- **Exception classes never live in writer/reader files.** They move to `libs/infrastructure/errors/{aggregate}__error.py` (NEW sub-bucket — mirrors `libs/domain/errors/`). Concrete extractions for spec_driven:
  - `file__writer.py` exceptions (`OutsideSandbox`, `UnsupportedExtension`, `FileTooLarge`, `InvalidBodyEncoding`, `MissingIfUnmodifiedSince`, `StaleWrite` — any defined inline) → `libs/infrastructure/errors/file__error.py`.
  - `file__reader.py` exceptions (`OutsideSandbox`, `UnsupportedExtension`, `FileTooLarge` — deduped at the file level alongside writer's variants) → same `file__error.py`.
  - `promotion__writer.py` / `promotion__reader.py` exceptions → `promotion__error.py`.
  - `project_directory__writer.py` exceptions (`SelfDeleteRefused`, slug-validation errors) → `project__error.py`.
  - `tree__reader.py` exceptions → `tree__error.py`.
  - `audit__writer.py` exceptions → `audit__error.py`.
  - The writer/reader re-exports its own exceptions for back-compat (`from libs.infrastructure.errors.{aggregate}__error import (...) # noqa: F401`).
- **DAO dataclasses never live in writer/reader files.** Any frozen dataclass mirroring external schema (e.g., a `TreeNodeDAO`, `FileStatDAO`) goes in `libs/infrastructure/daos/{aggregate}__dao.py`.
- **DTOs never live in command/query files** (already enforced via the consolidated `dtos/` sub-bucket above).
- **Pydantic request bodies never live in command/query files.** `ProjectDeleteBody` (currently in `routes` or `commands`) and any sibling Pydantic models stay with their route handler at `apps/api/routes/{aggregate}__route.py` — they're a transport-layer shape, not application-layer.

### 6. File-size guideline (informational, surfaces at stage 5)

Prefer `< 100 lines`. Past that, split by sub-concern using the layer's role taxonomy. Aggregates with genuinely complex logic may legitimately exceed the guideline; > 1000 lines without a clear sub-concern boundary is a stage-5 `warning`. Spec_driven currently has no flagged files (most modules are well under the guideline already); the rule is in place for future drift.

## Required spec / validation patches

1. `final_specs/spec.md` — replace the follow-up-014 amendment block at the top with a stacked block covering 014 + 015, restating the path remap AND adding the per-role-sub-bucket + one-file-per-aggregate + one-class-per-Q/C-file + SRP + routes-split rules. NFR-4 amended to point at `libs/{infrastructure,domain,application,common}/` instead of the legacy `backend/libs/`.
2. `validation/strategy.md` — append to the existing follow-up-014 amendment block: two new stage-5 checks land via this follow-up (mirroring `agent_refs/validation/development.md`):
   - **Sub-bucket presence check** — each non-empty layer MUST have its files inside the canonical role sub-folders for its layer. A file at `libs/application/build_regen_prompt__query.py` (flat) is a stage-5 `blocker`; the fix is to move it to `libs/application/queries/regen_prompt__query.py`.
   - **SRP grep** — `^class \w+\(Exception\):` in any file under `libs/infrastructure/{readers,writers,clients,middleware}/` is a stage-5 `blocker`. The fix is to move the class to `libs/infrastructure/errors/{aggregate}__error.py`.
3. `user_input/revised_prompt.md` — `Last regenerated` header bumped; existing 014 prose for "Stack" and "Layout" sections amended to call out the role sub-buckets and the one-file-per-aggregate rule.
4. `changelog.md` — append the standard entry.

## Out of scope

- API contract changes (HTTP routes, request/response JSON shapes stay byte-identical). External behavior unchanged.
- Frontend (`apps/ui/`) restructure. DDD layering does NOT apply to UI code.
- Test rewrites beyond import-path updates after the file moves land.
- Removing the re-exports from writer/reader files (mechanical follow-up if/when commands switch to import directly from `errors/`).
- Validation strategy file-by-file rewrites (only the amendment block + the two new checks are added; per-level files stay as-is for v1 until their pinned content needs touching).
- Actually executing the code moves under `projects/spec_driven/`. That's a stage-6 regen, not a follow-up patch — this follow-up persists intent only.

## Acceptance trigger

After a future stage-6 regen of `projects/spec_driven/`:

- `find projects/spec_driven/libs/infrastructure -maxdepth 1 -type d` lists at minimum `readers/`, `writers/`, `errors/`, `middleware/` (others may be empty).
- `find projects/spec_driven/libs/application -maxdepth 1 -type d` lists `queries/`, `commands/`, `dtos/`, `mappers/`.
- `find projects/spec_driven/libs/domain -maxdepth 1 -type d` lists `entities/`, `value_objects/`, `errors/`, `repositories/`.
- No file under `libs/infrastructure/{readers,writers,clients,middleware}/` matches `^class \w+\(Exception\):` (use `grep -r`).
- `apps/api/routes/` is a package with `__init__.py` + per-aggregate `*__route.py` files, each exposing its own `APIRouter()`; `app_factory.py` mounts the combined `router` from the package.
- Per-aggregate command/query classes have ONE class per file with method-per-operation (`PromotionCommand.add(...)` + `.remove(...)`, not `AddPromotionCommand.execute()`).
- HTTP routes + JSON shapes byte-identical to pre-regen baseline; existing pytest + vitest + Playwright suites pass with only import-path updates.
