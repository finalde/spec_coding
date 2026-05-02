from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .agents import ClaudeRunner
from .config import Settings
from .edits import RepoInputResolver
from .routes import (
    artifacts_router,
    edits_router,
    events_router,
    inputs_router,
    interview_router,
    phases_router,
    tasks_router,
)
from .runs import RunRegistry
from .storage import FileStore
from .storage.safe_writer import BackupWriter


def _find_repo_root(start: Path) -> Path:
    p = start.resolve()
    for candidate in [p, *p.parents]:
        if (candidate / ".claude").is_dir() and (candidate / "CLAUDE.md").is_file():
            return candidate
    raise RuntimeError(f"could not locate repo root from {start} (looked for .claude/ + CLAUDE.md)")


REPO_ROOT = _find_repo_root(Path(__file__).parent)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings.from_repo_root(REPO_ROOT)
    settings.ensure_dirs()

    app = FastAPI(title="spec_studio", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r"^https?://(127\.0\.0\.1|localhost)(:\d+)?$",
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    store = FileStore(settings)
    runner = ClaudeRunner(settings.repo_root)
    registry = RunRegistry(settings, store, runner)
    repo_resolver = RepoInputResolver(settings.repo_root)
    backup_writer = BackupWriter()

    app.state.settings = settings
    app.state.store = store
    app.state.runner = runner
    app.state.runs = registry
    app.state.repo_resolver = repo_resolver
    app.state.backup_writer = backup_writer

    app.include_router(tasks_router, prefix="/api", tags=["tasks"])
    app.include_router(phases_router, prefix="/api", tags=["phases"])
    app.include_router(events_router, prefix="/api", tags=["events"])
    app.include_router(artifacts_router, prefix="/api", tags=["artifacts"])
    app.include_router(inputs_router, prefix="/api", tags=["inputs"])
    app.include_router(edits_router, prefix="/api", tags=["edits"])
    app.include_router(interview_router, prefix="/api", tags=["interview"])

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "repo_root": str(settings.repo_root)}

    return app
