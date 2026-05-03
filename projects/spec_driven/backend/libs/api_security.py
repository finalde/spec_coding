from __future__ import annotations

import logging
from dataclasses import dataclass

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp

logger = logging.getLogger("spec_driven.api_security")

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
