from __future__ import annotations

import logging
from dataclasses import dataclass

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.types import ASGIApp

logger = logging.getLogger("ai_video_management.api_security")

# Only PUT /api/file is a state-changing endpoint.
GUARDED_ROUTES: frozenset[tuple[str, str]] = frozenset({("PUT", "/api/file")})


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


class OriginHostMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, bound: BoundOrigin) -> None:
        super().__init__(app)
        self._origin_allow: frozenset[str] = bound.origin_allow_list()
        self._host_allow: frozenset[str] = bound.host_allow_list()

    async def dispatch(self, request: Request, call_next):  # type: ignore[no-untyped-def]
        method = request.method.upper()
        path = request.url.path
        if (method, path) in GUARDED_ROUTES:
            origin = request.headers.get("origin")
            host = request.headers.get("host")
            if origin not in self._origin_allow or host not in self._host_allow:
                logger.warning(
                    "origin_host_403",
                    extra={
                        "kind": "origin_host_403",
                        "method": method,
                        "path": path,
                        "origin": origin,
                        "host": host,
                    },
                )
                return JSONResponse(
                    status_code=403,
                    content={"detail": {"kind": "origin_blocked"}},
                )
        return await call_next(request)


CSP_HEADER: str = (
    "default-src 'self'; "
    "img-src 'self'; "
    "style-src 'self' 'unsafe-inline'; "
    "script-src 'self'; "
    "connect-src 'self'; "
    "object-src 'none'; "
    "base-uri 'self'"
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Attach CSP + X-Content-Type-Options + Referrer-Policy on every response."""

    async def dispatch(self, request: Request, call_next):  # type: ignore[no-untyped-def]
        response = await call_next(request)
        response.headers.setdefault("Content-Security-Policy", CSP_HEADER)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        return response
