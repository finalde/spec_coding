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


class OriginHostMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, bound: BoundOrigin) -> None:
        super().__init__(app)
        self.bound = bound

    async def dispatch(self, request: Request, call_next):
        if (request.method, request.url.path) in GUARDED_ROUTES:
            origin = request.headers.get("origin")
            host = request.headers.get("host")
            if origin != self.bound.origin:
                return JSONResponse({"detail": "forbidden"}, status_code=403)
            if host != self.bound.host_header:
                return JSONResponse({"detail": "forbidden"}, status_code=403)
        return await call_next(request)
