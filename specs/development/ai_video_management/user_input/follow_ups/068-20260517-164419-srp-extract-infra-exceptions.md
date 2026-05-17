# Follow-up draft 068 — 2026-05-17

Apply the **Single Responsibility Principle** to infrastructure files: a `.py` file does one thing well. Exception classes don't live in writer/reader files — extract them to `libs/infrastructure/errors/{aggregate}__error.py`, mirroring the `libs/domain/errors/{aggregate}__error.py` layout on the domain side.

## Required moves

### 1. Add the SRP rule to `agent_refs/project/development.md` §1

A new paragraph just after the dependency-direction subsection (and before the file-size guideline added in 065). Calls out four concrete extractions:

1. **Exception classes** → `libs/infrastructure/errors/{aggregate}__error.py` (not in the writer file).
2. **DAO dataclasses** → `libs/infrastructure/daos/{aggregate}__dao.py` (not in the writer file).
3. **DTOs** → `libs/application/dtos/{aggregate}__dto.py` (already enforced by the DTO consolidation rule).
4. **Pydantic request bodies** → with the route handler, not in command/query files (transport-layer concern).

`CLAUDE.md` § Project rules gets a parallel SRP bullet.

### 2. Extract every infra exception class

Walk every file under `libs/infrastructure/writers/` and `libs/infrastructure/readers/`. For each `class Xxx(Exception): ...` block, move it to `libs/infrastructure/errors/{aggregate}__error.py`. Total: **43 exception classes across 8 source files → 7 errors files**.

| Source | Exceptions extracted | Destination |
|---|---|---|
| `writers/actor__writer.py` | 6 (InvalidAttribute, GenerationDirMissing, ActorNotFound, ActorAlreadyDeleted, ActorDeleteTargetExists, ActorDeleteFailed) | `errors/actor__error.py` |
| `writers/casting__writer.py` | 2 (InvalidActorId, InvalidRole) | `errors/casting__error.py` |
| `writers/character_video__writer.py` | 8 (InvalidPath, NotFound, FfmpegMissing — shared; NotCharacterVideo, TruncateFailed, NotShotMd, NoCharacterTable, ConcatFailed) | `errors/character_video__error.py` |
| `writers/downloads__writer.py` | 1 (DownloadsDirMissing) | `errors/downloads__error.py` |
| `writers/file__writer.py` + `readers/file__reader.py` | 9 (UnsupportedExtension, FileTooLarge, InvalidBodyEncoding, OutsideSandbox, MissingIfUnmodifiedSince, StaleWrite from writer; FileTooLarge, OutsideSandbox, UnsupportedExtension from reader — dedup at file level) | `errors/file__error.py` |
| `writers/frame__writer.py` | 5 (InvalidPath, NotFound, NotVideo, FfmpegMissing, ExtractFailed) | `errors/frame__error.py` |
| `writers/media__writer.py` | 12 (InvalidPath, NotFound, NotMedia, AlreadyArchived, NotInArchive, AlreadyDeleted, NotInAiVideos, NotInDeleted, TargetExists, MoveFailed, InvalidDramaPath, DramaNotFound) | `errors/media__error.py` |

Each writer/reader now starts with:
```python
from libs.infrastructure.errors.{aggregate}__error import (
    Exception1, Exception2, ...,
)  # re-exported from the writer for back-compat with commands that import from the writer
```

The `# noqa: F401` flag is set because the writer's `__init__`-level imports look "unused" to lint but ARE used by external callers via the writer's `from libs.infrastructure.writers.{aggregate}__writer import Xxx` shape.

### 3. No command rewrites required

Commands currently import exceptions from the writers (e.g., `from libs.infrastructure.writers.media__writer import InvalidPath, NotMedia, ...`). These imports still resolve because the writer re-exports them. A future cleanup can switch each command to import directly from `libs.infrastructure.errors.{aggregate}__error` — that's mechanical and orthogonal.

### 4. Domain side unchanged

`libs/domain/errors/{aggregate}__error.py` already exists for each aggregate and holds domain-level errors (e.g., `InvalidActorAttributeError`, `ActorNotFoundError`, `FileNotInSandboxError`). The new infra files DON'T duplicate them — they hold the raw infrastructure-side exceptions (`InvalidAttribute`, `ActorNotFound`, `OutsideSandbox`, etc., bare names without `Error` suffix). The semantic distinction is: domain errors are what the application layer raises to communicate business-rule violations; infra exceptions are what the filesystem / HTTP / ffmpeg subprocesses raise. Commands catch infra exceptions and re-raise as domain errors.

## Out of scope

- DAO dataclass extractions (item 2 of the SRP rule). Many DAOs still live in writer files (e.g., `TruncateResult`, `ConcatResult`, `MoveResult`, `RenameResult`, `GenerateResult`, `ActorInfo`, etc.). Each can move to `libs/infrastructure/daos/{aggregate}__dao.py` in a future follow-up; the SRP rule is in place to flag them next time someone touches these files.
- Switching command imports from writers → errors files (mechanical, see §3).
- HTTP route paths + JSON shapes (byte-identical).

## Acceptance trigger

- Pytest baseline preserved: 18 pass / 5 pre-existing wukong fixture failures.
- `python -c "import apps.api.main"` and `import apps.api.asgi` boot cleanly.
- `find libs/infrastructure/errors -name "*.py" -not -name "__init__.py" | wc -l` ≥ 7.
- No file under `libs/infrastructure/writers/` or `libs/infrastructure/readers/` defines `^class \w+(Exception):` (use grep to verify).
