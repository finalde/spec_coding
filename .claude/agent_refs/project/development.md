# Project refs — `task_type=development`

Cross-cutting rules about the outputs of every development-task project (`projects/{name}/`). Loaded when the current task has `task_type=development`. Per `CLAUDE.md` § Stage playbooks and reference docs: this file overrides `project/general.md`; the per-project spec under `specs/development/{name}/` overrides this file for that one project (with a divergence note).

## Rules

### 1. Solution layout: `apps/` + `libs/` + DDD-layered backend

Every development project is a **solution folder** at `projects/{name}/` with this exact top-level shape:

```
projects/{name}/
├── README.md              # solution-level, kept current with every feature change
├── Makefile               # solution-level entry points (dev, test, lint, build)
├── pyproject.toml         # solution-level Python deps (canonical for this solution)
├── requirements.txt       # mirror of [project].dependencies for pip fallback
├── apps/                  # executables — thin wrappers, NO business logic
│   ├── api/               # webapi (FastAPI) — main.py + container.py + routes/
│   ├── ui/                # React frontend (was `frontend/`)
│   └── {name}_job/        # any batch job exe lives here too
├── libs/                  # the shared backend code — 4 layers, each sub-bucketed by role
│   ├── infrastructure/    # pure engineering: file I/O, DB, HTTP clients, message brokers
│   │   ├── readers/       # *__reader.py
│   │   ├── writers/       # *__writer.py + mutator-suffix legacy names (importer/extractor/archiver/renamer/truncator/builder)
│   │   ├── clients/       # *__client.py (3rd-party HTTP / SDK wrappers)
│   │   ├── daos/          # *__dao.py (frozen dataclasses mirroring external schema)
│   │   └── middleware/    # *__middleware.py (framework adapters at the transport edge)
│   ├── domain/            # pure business logic — no I/O, no frameworks
│   │   ├── entities/      # *__entity.py
│   │   ├── value_objects/ # *__valueobject.py
│   │   ├── errors/        # *__error.py
│   │   └── repositories/  # *__repository.py (Protocols)
│   ├── application/       # orchestration: load via infra, run domain, map results
│   │   ├── queries/       # *__query.py — ONE class per file with method-per-operation
│   │   ├── commands/      # *__command.py — ONE class per file with method-per-operation
│   │   ├── dtos/          # *__dto.py — Qdtos + Cdtos for the aggregate (multi-class OK; pure data)
│   │   └── mappers/       # *__mapper.py
│   └── common/            # constants, enums, primitive types shared by all three (FLAT — no sub-bucketing)
└── tests/                 # mirrors apps/ + libs/ tree (including type sub-folders)
```

**Per-role sub-bucketing within each layer.** Files of the same role live in a folder named for the role (plural). Each role gets its own folder; empty folders for canonical roles are allowed (they document the convention). `common/` is the lone exception.

**One file per aggregate per role.** `{aggregate}__{role}.py` holds all operations of that role for that aggregate. Example: `application/commands/actor__command.py` contains a single `ActorCommand` class with methods `generate(...)`, `generate_diverse(...)`, `delete(...)`. The operation name lives on the method, not on the class or filename. The legacy patterns (per-operation FILE, per-operation CLASS in same file, `execute()` method name) are retired.

**DTOs are exempt from one-class-per-file** because they're pure data with no behavior — `{aggregate}__dto.py` may hold many Qdtos and Cdtos; the class-name `Qdto`/`Cdto` suffix already disambiguates.

**Routes follow the same shape** as application: `apps/api/routes/{aggregate}__route.py`, each with its own `APIRouter()`. `apps/api/routes/__init__.py` exposes a combined `router` that `apps/api/app_factory.py` mounts on the FastAPI app.

**Roles under `apps/`:**
- `apps/api/` is the FastAPI executable. It does **only** wiring: build the DI container, mount routes, start uvicorn. All HTTP handler bodies call one application-layer Query or Command and return its DTO.
- `apps/ui/` is the React frontend. The DDD layering does NOT apply to UI code — `apps/ui/src/` keeps its native React structure (`components/`, `hooks/`, `api.ts`).
- Additional executables (batch jobs, CLIs) get their own `apps/{exe_name}/`. They MUST also be thin wrappers around a single Query / Command.

**Dependency direction (one-way, enforced):**
- `infrastructure` → may import from `common` only. **Never** imports `domain` or `application`.
- `domain` → may import from `common` only. **Never** imports `infrastructure` or `application`. Domain code has no notion of files, databases, or HTTP.
- `application` → may import from `infrastructure`, `domain`, `common`. This is the ONLY layer that knows all three.
- `common` → imports from nothing inside `libs/`. Leaf.
- `apps/*` → may import from `application` and `common`. **Never** imports `infrastructure` or `domain` directly.

A cross-layer import that violates the arrows is a `blocker` at stage 5 validation.

**Single Responsibility Principle — one concern per file.** A `.py` file does ONE thing well. If you find a file mixing two unrelated concerns (e.g., a writer that also defines its own exception classes; a reader that also defines DAO dataclasses; a command that also defines its input/output DTOs), extract the second concern to its proper file. Concrete extractions:

- **Exception classes never live in writer/reader files.** They go in `libs/infrastructure/errors/{aggregate}__error.py` (mirroring `libs/domain/errors/{aggregate}__error.py` on the domain side). The writer/reader imports its own exceptions via `from libs.infrastructure.errors.{aggregate}__error import (...)`. Anti-pattern: `class InvalidPath(Exception): ...` defined at the top of `{aggregate}__writer.py`.
- **DAO dataclasses don't live in writer/reader files.** They go in `libs/infrastructure/daos/{aggregate}__dao.py`. The writer/reader imports the DAO.
- **DTOs don't live in command/query files.** They go in `libs/application/dtos/{aggregate}__dto.py` (already enforced — see DTO consolidation rule above).
- **Pydantic request bodies don't live in command/query files** either. They live with the route handler (`apps/api/routes/{aggregate}__route.py`) since they're a transport-layer shape, not application-layer.

The rule's purpose: when you grep for "where does class X live" you find one place. When you `git log` a file, the history is about one concern, not interleaved unrelated changes. When the file grows, the split direction is dictated by the concern boundary, not invented case-by-case.

**File size — prefer < 100 lines, split by sub-concern when bigger.** A file that grows past ~100 lines is a signal: the aggregate or module is doing too much. Split it the same way layers split — pick the sub-concern axis that matches the layer's existing taxonomy:

- A `routes.py` with all endpoints (e.g., 800+ lines) splits into `apps/api/routes/{aggregate}__route.py` (one file per aggregate, mirroring `libs/application/{queries,commands}/`). The package's `__init__.py` exposes a single combined `router` that `app_factory.py` mounts.
- An `{aggregate}__writer.py` that grows past ~500 lines (e.g., one with multiple distinct operations like generate + delete + migrate + reap) is a candidate for splitting along the operation boundary IF the operations don't share much private state; otherwise the size is justified by the aggregate's complexity.
- A `{aggregate}__dto.py` past ~200 lines means too many DTOs share a file — split by query-side vs command-side (`{aggregate}__qdto.py` + `{aggregate}__cdto.py`) ONLY if the split materially helps readability; otherwise accept the size (DTOs are flat data, low cognitive cost).

The < 100 line target is a **guideline**, not a hard cap. Aggregates with genuinely complex business logic (e.g., the actor pool's variance pools + prompt assembly + Kling client wrapper) may legitimately exceed it. The rule's purpose: when a file feels uncomfortable to navigate, the split direction is already implied by the layer's role taxonomy. A `*.py` file passing 1000 lines without a clear sub-concern boundary IS a stage-5 reviewer flag (`warning`, not `blocker`).

### 2. `libs/domain/` follows Domain-Driven Design

Domain code is a Rich Domain Model: business invariants live on the objects themselves, not in service classes.

- **Entities** (`{name}__entity.py` / class `{Name}Entity`) — have identity (`entity_id`), mutable state guarded by methods that enforce invariants. Use `@dataclass` (not frozen) with private setters or method-based mutation.
- **Value objects** (`{name}__valueobject.py` / class `{Name}`) — immutable, identity-less, equality by attribute value. Use `@dataclass(frozen=True)`. Examples: `Money`, `EmailAddress`, `SafePath`.
- **Aggregates** — pick an aggregate root (an Entity) that owns and protects a cluster of entities + value objects. Outside code references the aggregate root ONLY (by id). Cross-aggregate references are by id, never by object reference. The root's public methods are the only mutation surface; child entities are not exposed for direct mutation.
- **Domain errors** (`{name}__error.py` / class `{Name}Error(Exception)`) — raised by the domain when an invariant is violated. Never `ValueError` or generic exceptions; always a named domain error. Application catches and maps to transport-layer errors.
- **Domain events** (`{name}__event.py` / class `{Name}Event`) — immutable `@dataclass(frozen=True)`, named in past tense (`OrderPlaced`, `PromotionAdded`). Raised by aggregates as the result of a command's state change. Collected by the application layer; published via infrastructure if needed.
- **Repository interfaces** — defined as `Protocol` classes in `domain/{aggregate}__repository.py`. The concrete implementation lives in `infrastructure/`; the domain only sees the protocol. (This is the only dependency-inversion point.)
- Domain code is plain Python — no FastAPI, no SQLAlchemy, no Pydantic. If you import a framework into `domain/`, you've made a mistake.

### 3. `libs/infrastructure/` + `libs/application/` follow CQRS strictly

Reads and writes are split into separate files and classes.

**Infrastructure layer — physical I/O, split by direction:**
- `{name}__reader.py` / class `{Name}Reader` — pulls data from outside (file, DB, API). Returns DAOs.
- `{name}__writer.py` / class `{Name}Writer` — pushes data to outside (file, DB, API). Accepts DAOs.
- `{name}__dao.py` / class `{Name}Dao` — Data Access Object: `@dataclass(frozen=True)`, mirrors the external schema. NOT a domain object. NOT a DTO. Lives only inside infrastructure.
- `{name}__client.py` / class `{Name}Client` — wraps a third-party SDK or HTTP API. May be referenced by a Reader/Writer.

**Application layer — orchestration, split by intent:**
- `{name}__query.py` / class `{Name}Query` — read-only operation. `execute(...)` returns a `{Name}Qdto`.
- `{name}__command.py` / class `{Name}Command` — state-changing operation. `execute(...)` returns a `{Name}Cdto` or `None`.
- `{name}__qdto.py` / class `{Name}Qdto` — Query Data Transfer Object. `@dataclass(frozen=True)`. Shape designed for the consumer (UI / API response).
- `{name}__cdto.py` / class `{Name}Cdto` — Command Data Transfer Object. `@dataclass(frozen=True)`. Shape captures input/output of a state change.
- `{name}__mapper.py` / class `{Name}Mapper` — owns ALL mapping among DAO ↔ Entity/ValueObject ↔ QDto/CDto. Mapping never lives on the data objects themselves. Mapping never happens in `apps/`, `domain/`, or `infrastructure/`.

**Strictness:** every application-layer operation is a Query OR a Command. No `service.py`, no `manager.py`, no in-between. An operation that genuinely needs to both read and write atomically is a Command — model the read as part of the command's invariant check.

**Read-side simplification (allowed):** A Query may bypass aggregates and read directly via a Reader into a Qdto, skipping the domain layer entirely (classic CQRS read-side). A Command MUST go through the domain (load aggregate → invoke method → persist via Writer).

### 4. Filename + classname `__` suffix convention

Every layer-specific file ends with a double-underscore suffix tag that names its role. The class inside ends with the same suffix in PascalCase (no underscores in the class name).

| Layer | File pattern | Class pattern |
|---|---|---|
| infrastructure | `user__reader.py` | `UserReader` |
| infrastructure | `user__writer.py` | `UserWriter` |
| infrastructure | `user__dao.py` | `UserDao` |
| infrastructure | `stripe__client.py` | `StripeClient` |
| domain | `order__entity.py` | `OrderEntity` |
| domain | `money__valueobject.py` | `Money` |
| domain | `order__error.py` | `OrderError` (or specific `OrderNotPaidError`) |
| domain | `order__event.py` | `OrderPlacedEvent` |
| domain | `order__repository.py` | `OrderRepository` (Protocol) |
| application | `place_order__command.py` | `PlaceOrderCommand` |
| application | `list_orders__query.py` | `ListOrdersQuery` |
| application | `order__qdto.py` | `OrderQdto` |
| application | `place_order__cdto.py` | `PlaceOrderCdto` |
| application | `order__mapper.py` | `OrderMapper` |
| common | (no suffix) `constants.py`, `enums.py`, `types.py` | `OrderStatus`, etc. |

One file = one primary class. Helper classes for the same concept may share the file. Files without a `__suffix` are only allowed in `common/`.

### 5. Backend apps use `dependency_injector`

Every Python app under `apps/*/` (api, batch jobs, CLIs) wires its components with the [`dependency_injector`](https://python-dependency-injector.ets-labs.org/) library.

- One `apps/{exe}/container.py` per executable. Containers compose `Factory`/`Singleton` providers for Readers, Writers, Queries, Commands, Mappers.
- `apps/{exe}/main.py` builds the container, calls `container.wire(modules=[...])`, then starts the executable.
- For FastAPI, route handlers use `@inject` + `Annotated[Type, Depends(Provide[Container.x])]` to receive Query/Command instances. The handler body is two lines: call `execute(...)`, return the DTO.
- Test isolation: tests override providers (`container.x.override(stub)`) rather than monkey-patching imports.
- Add `dependency-injector` to `pyproject.toml` `[project].dependencies` of every solution that has a Python app.

### 6. Tests live at solution root, mirroring source

Tests live at `projects/{name}/tests/`, with subfolders mirroring `apps/` and `libs/`:

```
tests/
├── api/                   # tests for apps/api/
├── libs/
│   ├── infrastructure/
│   ├── domain/
│   ├── application/
│   └── common/
└── ui/                    # frontend tests (if any)
```

Domain tests are unit tests with no I/O. Application tests use overridden DI providers. Infrastructure tests may touch the file system / test DB; never mock the boundary (per § 1 of `agent_refs/validation/development.md` if present, else: integration tests prefer real boundaries).

*(Rules 1–6 originated from the 2026-05-13 cross-project follow-up establishing apps/+libs/ DDD+CQRS layout.)*

---

### 7. UI theme: light only on app chrome

All webapps under `projects/` ship a **light theme** for app chrome — every surface the user navigates and clicks: `body`, sidebars / navigators, toolbars, panels, buttons, form controls, table chrome, breadcrumbs.

**Implementation:**
- `:root { color-scheme: light; }` exclusively. Do NOT include `dark`.
- NO `@media (prefers-color-scheme: dark) { ... }` block targeting app-chrome surfaces. The rule forbids OS-driven dark-mode toggling of chrome, NOT dark color anywhere on the page.

**Carve-outs (allowed dark surfaces):**
Intentional dark surfaces *inside* an otherwise-light UI are permitted when:
- The spec calls for them (e.g., a syntax-highlighted `<pre>`, a code-view panel, a regen-prompt assembled-output panel).
- Contrast meets WCAG AA against foreground colors.
- They are NOT triggered by `prefers-color-scheme: dark` — the dark palette is the unconditional default for that element, not an OS-toggled override.

Concrete `spec_driven` example: `<pre>` blocks inside `.regen-prompt-block`, `.markdown-view pre`, `.code-view pre` ship with a fixed dark palette regardless of OS theme — fine. NOT fine: wrapping `body { background: #fff; }` in `@media (prefers-color-scheme: light)` with a dark counterpart.

**Severity:** generated frontend with `prefers-color-scheme: dark` overrides on `body` / sidebar / toolbar / panels / buttons = `blocker` at stage 5. Fix: delete the dark `@media` block, not add a user toggle.

**v1 out of scope:** user-toggleable theme picker. If a future follow-up adds one, this rule will be revised here, not bypassed.

*(Originated from follow-up 004 of run `spec_driven`; relocated from `CLAUDE.md` to this file by follow-up 005.)*

## Update protocol

Surgical: one new rule per lesson, citing the source run / follow-up. When a class of cross-project regression surfaces (analogous to API-shape-drift in `validation/development.md`), promote the prevention rule here rather than embedding in any single project's spec.
