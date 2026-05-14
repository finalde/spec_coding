"""Force-exit watchdog for uvicorn graceful-shutdown hangs.

Per follow-up 042: follow-up 037's `timeout_graceful_shutdown=2` makes uvicorn's
asyncio loop bail in 2s, but FastAPI sync `def` endpoints run in anyio's
threadpool — cancelling the asyncio task wrapping a sync call does NOT kill
the underlying OS thread. A blocking Kling HTTP POST (30–120s), an
`/api/media` range-stream, an ffmpeg subprocess in `frame_extractor`, etc.
keeps a non-daemon thread alive, and Python's normal `sys.exit` waits for
those threads → uvicorn's `Waiting for connections to close. (CTRL+C to
force quit)` hangs after WatchFiles triggers a reload.

`install()` monkey-patches `uvicorn.Server.handle_exit` so that the FIRST
signal (SIGTERM / SIGINT / SIGBREAK) — in addition to setting uvicorn's
`should_exit` — also arms a daemon `threading.Timer` that calls
`os._exit(0)` after `timeout_graceful_shutdown + FORCE_EXIT_GRACE` seconds.
uvicorn's normal graceful path still runs first; the watchdog only fires
when Python's interpreter would otherwise be blocked by stuck threadpool
threads. Idempotent — second `install()` is a no-op.
"""
from __future__ import annotations

import os
import threading
from typing import Any

import uvicorn

FORCE_EXIT_GRACE: float = 2.0


def install() -> None:
    if getattr(uvicorn.Server, "_force_exit_installed", False):
        return
    original = uvicorn.Server.handle_exit

    def patched(self: uvicorn.Server, sig: int, frame: Any) -> None:
        original(self, sig, frame)
        graceful = getattr(self.config, "timeout_graceful_shutdown", None)
        deadline = (float(graceful) if graceful is not None else 0.0) + FORCE_EXIT_GRACE
        timer = threading.Timer(deadline, lambda: os._exit(0))
        timer.daemon = True
        timer.start()

    uvicorn.Server.handle_exit = patched  # type: ignore[method-assign]
    uvicorn.Server._force_exit_installed = True  # type: ignore[attr-defined]
