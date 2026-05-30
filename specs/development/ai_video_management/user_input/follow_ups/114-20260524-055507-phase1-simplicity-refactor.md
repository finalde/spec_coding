# Follow-up draft 114 — 2026-05-24

Phase 1 of a multi-phase simplicity refactor: collapse the parallel error hierarchies, centralize HTTP-error mapping at the FastAPI boundary, delete the empty `ActorEntity` holder, and remove a long tail of duplicated / boilerplate code. Splitting `actor__writer.py` and rewriting the mapper/Protocol layer are explicitly deferred to a later phase.

---
target_stage: 6
target_artifacts:
  - projects/ai_video_management/libs/infrastructure/errors/
  - projects/ai_video_management/libs/domain/errors/
  - projects/ai_video_management/libs/domain/entities/actor__entity.py
  - projects/ai_video_management/libs/domain/repositories/actor__repository.py
  - projects/ai_video_management/libs/application/commands/
  - projects/ai_video_management/libs/application/queries/
  - projects/ai_video_management/libs/application/dtos/actor__dto.py
  - projects/ai_video_management/libs/domain/value_objects/actor__valueobject.py
  - projects/ai_video_management/libs/infrastructure/writers/
  - projects/ai_video_management/libs/infrastructure/readers/
  - projects/ai_video_management/apps/api/app_factory.py
  - projects/ai_video_management/apps/api/routes/
severity: high
---

## Intent

The current backend keeps two parallel exception hierarchies for every aggregate (`libs/domain/errors/{X}__error.py` + `libs/infrastructure/errors/{X}__error.py`). Every Command/Query wraps each infra call in a `try / except InfraErr / raise DomainErr` block. Every route then wraps the Command/Query call in another `try / except DomainErr / return JSONResponse(...)` block. Adding a new error requires touching five places (infra class, domain class, command translator, route handler, kind string) with no compile-time help keeping them aligned.

There is no second adapter behind any of these infrastructures. The layering is buying drift risk without buying optionality.

## Phase 1 scope (this follow-up)

1. **Collapse parallel error hierarchies, all aggregates.** Infrastructure raises domain errors directly. The `libs/infrastructure/errors/` package is deleted in its entirety. For infra exceptions that did not have a domain counterpart (e.g. `GenerationDirMissing`, `TargetExists`, `MoveFailed`, `NovelNotFound`), add a named domain class so the boundary still has a stable name.
2. **Centralize HTTP-error mapping at the FastAPI boundary.** Replace the per-endpoint `try / except DomainErr / return JSONResponse(...)` blocks with a single `app.exception_handler(DomainErr)` per error class, registered in `apps/api/app_factory.py`. Status code and `{"detail": {"kind": ...}}` shape stay identical to today.
3. **Drop `*_method_not_allowed` per-endpoint shims.** Replace with a single 405 exception handler that emits the same `{"detail": {"kind": "method_not_allowed"}}` body. The `Allow` header still comes from FastAPI's default. Per-endpoint shims are deleted from every route file.
4. **Drop manual input-DTO builders in routes.** `_generate_input(body)` and `WriteFileInputCdto(rel_path=body.path, ...)` collapse to `Cdto(**body.model_dump())` where field names match (they do — they were renamed to match exactly when the Cdto layer was introduced).
5. **Move validation into the input Cdto's `__post_init__`.** `attrs.validate()`, `validate_batch_count(...)`, `validate_resolution(...)`, `validate_seeds(...)` currently run in both `ActorCommand.generate` and `ActorQuery.preview_prompts`. After this change they run exactly once, when the Cdto is constructed. Same pattern for any other Cdto that has duplicate validation across Command + Query.
6. **Drop the parallel `LOOK_OPTIONS` frozenset in `actor__writer.py`.** Import from `libs.domain.value_objects.actor__valueobject` instead. Any other shadow enum in the infrastructure layer follows the same rule: domain is the single source of truth.
7. **Drop `ActorAttrs.to_dict`.** Use `dataclasses.asdict(attrs)` at the call sites — the manual to_dict adds no value and drifts when fields are added.
8. **Delete `libs/domain/entities/actor__entity.py`.** The file is a 32-line holder with no methods; the docstring itself concedes "currently a thin holder — most actor business logic lives on `ActorAttrs`". The `ActorRepository.list_actors()` Protocol signature lies about returning `list[ActorEntity]` (the actual return is `list[ActorInfo]`). Move `validate_actor_id` (the only meaningful piece of the entity file) into `libs/domain/value_objects/actor__valueobject.py`. Update the Protocol return type to match what `ActorPool` actually returns (a transitional step — Phase 2 will retype the Protocol properly).
9. **Drop `@runtime_checkable` from `ActorRepository`.** No runtime `isinstance(x, ActorRepository)` check exists.
10. **Fix the swallowed `OSError` in `apps/api/app_factory.py`.** If `_actors/` cannot be created at startup, the actor feature is broken — fail loudly with a clear traceback rather than silently continuing.

## Phase 1 explicitly does NOT do

- Splitting `libs/infrastructure/writers/actor__writer.py` (2,431 lines) into `clients/kling__client.py` + archetype valueobject + sidecar file + a slimmed `ActorPool`. Deferred to Phase 2.
- Retyping `ActorRepository.preview_prompts() -> dict[str, object]` to a real dataclass so the `preview_to_qdto` mapper can drop its isinstance gauntlet. Deferred to Phase 2.
- Collapsing the mapper layer's pure-boilerplate methods (`generate_to_cdto`, `info_to_qdto`) into direct field copies / `asdict`. Deferred to Phase 2.
- The `from __future__ import annotations` line at the top of every Python file. Cosmetic-only; not worth the noise in this diff.

## Constraints

- HTTP response shapes (status codes + `{"detail": {"kind": ..., ...}}` bodies) MUST be byte-identical to today's behavior. The existing test suite (`tests/test_api_security_three_shapes.py`, `tests/test_boot_smoke.py`, etc.) is the contract.
- No new dependencies.
- All changes land inside `projects/ai_video_management/`; no edits to `CLAUDE.md` or `.claude/agent_refs/` in this phase (Phase 2 will revisit `agent_refs/project/development.md` §1 if needed to soften the entity-mandatory rule).

## Why now

Three reviews of this codebase have repeatedly identified the same friction points; the layering is not earning its boilerplate. Collapsing the error hierarchies is the highest leverage change available and is a prerequisite for any of the Phase 2 work.
