"""Pure value object for the backend's bound origin (host + port) and the
static security constants (GUARDED_ROUTES, CSP_HEADER). Used by both the
middleware adapter in libs/infrastructure/ and the container/app_factory
wiring in apps/api/.

These are pure data — no framework, no I/O — so they live in libs/common/
where domain, infrastructure, and apps can all import them without
violating the dependency arrows in development.md §1.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BoundOrigin:
    host: str
    port: int

    def origin_allow_list(self) -> frozenset[str]:
        if self.host in {"127.0.0.1", "localhost"}:
            return frozenset(
                {
                    f"http://127.0.0.1:{self.port}",
                    f"http://localhost:{self.port}",
                }
            )
        return frozenset({f"http://{self.host}:{self.port}"})

    def host_allow_list(self) -> frozenset[str]:
        if self.host in {"127.0.0.1", "localhost"}:
            return frozenset(
                {
                    f"127.0.0.1:{self.port}",
                    f"localhost:{self.port}",
                }
            )
        return frozenset({f"{self.host}:{self.port}"})


# Only PUT /api/file is a state-changing endpoint that requires the
# Origin/Host gate; everything else is read-only or session-isolated.
GUARDED_ROUTES: frozenset[tuple[str, str]] = frozenset({("PUT", "/api/file")})


CSP_HEADER: str = (
    "default-src 'self'; "
    "img-src 'self'; "
    "style-src 'self' 'unsafe-inline'; "
    "script-src 'self'; "
    "connect-src 'self'; "
    "object-src 'none'; "
    "base-uri 'self'"
)
