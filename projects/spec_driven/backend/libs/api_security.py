"""
api_security — Origin/Host validation middleware (FR-9, NFR-7, AC-11).

Applies ONLY to the four sanctioned mutation endpoints:
- PUT /api/file
- POST /api/regen-prompt
- POST /api/promote
- DELETE /api/promote

Any other (method, path) combination falls through unchecked, so PATCH /api/file
and DELETE /api/file reach the route handler and receive 405 (NFR-6, AC-12,
SEC-15).

Loopback equivalence (FR-9 follow-up 004): when the bound host is a loopback
literal (`127.0.0.1` or `localhost`), both literals are admitted at the bound
port. The browser sends whatever the user typed in the address bar, so opening
the SPA at `http://localhost:8765/` must not 403 the mutation calls. IPv6
(`::1`) is NOT admitted — uvicorn binds IPv4-only in v1.
"""

from __future__ import annotations

from dataclasses import dataclass

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

GUARDED_ROUTES: frozenset[tuple[str, str]] = frozenset(
    {
        ("PUT", "/api/file"),
        ("POST", "/api/regen-prompt"),
        ("POST", "/api/promote"),
        ("DELETE", "/api/promote"),
    }
)

LOOPBACK_HOST_LITERALS: frozenset[str] = frozenset({"127.0.0.1", "localhost"})


@dataclass(frozen=True)
class BoundOrigin:
    host: str
    port: int

    @property
    def origin(self) -> str:
        return f"http://{self.host}:{self.port}"

    @property
    def host_header(self) -> str:
        return f"{self.host}:{self.port}"

    def origin_allow_list(self) -> frozenset[str]:
        if self.host in LOOPBACK_HOST_LITERALS:
            return frozenset(f"http://{h}:{self.port}" for h in LOOPBACK_HOST_LITERALS)
        return frozenset({self.origin})

    def host_allow_list(self) -> frozenset[str]:
        if self.host in LOOPBACK_HOST_LITERALS:
            return frozenset(f"{h}:{self.port}" for h in LOOPBACK_HOST_LITERALS)
        return frozenset({self.host_header})


class OriginHostMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, bound: BoundOrigin) -> None:
        super().__init__(app)
        self.bound = bound
        self._allowed_origins = bound.origin_allow_list()
        self._allowed_hosts = bound.host_allow_list()

    async def dispatch(self, request: Request, call_next):
        if (request.method, request.url.path) in GUARDED_ROUTES:
            origin = request.headers.get("origin")
            host = request.headers.get("host")
            if origin not in self._allowed_origins:
                return JSONResponse({"detail": "forbidden"}, status_code=403)
            if host not in self._allowed_hosts:
                return JSONResponse({"detail": "forbidden"}, status_code=403)
        return await call_next(request)
