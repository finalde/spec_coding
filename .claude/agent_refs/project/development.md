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
├── libs/                  # the shared backend code — exactly 4 subfolders
│   ├── infrastructure/    # pure engineering: file I/O, DB, HTTP clients, message brokers
│   ├── domain/            # pure business logic — no I/O, no frameworks
│   ├── application/       # orchestration: load via infra, run domain, map results
│   └── common/            # constants, enums, primitive types shared by all three
└── tests/                 # mirrors apps/ + libs/ tree: tests/api/, tests/libs/domain/, ...
```

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
