"""Shared route helpers (cross-cutting across aggregate route files).

Per follow-up 062: routes were split from one 850-line `routes.py` into
per-aggregate `{aggregate}__route.py` files. The helpers used by more
than one aggregate live here; aggregate-specific helpers stay in the
aggregate's route file.
"""
from __future__ import annotations

from fastapi.responses import JSONResponse, Response

from libs.domain.errors.actor__error import ActorAlreadyAssignedError


def file_security_headers(filename: str) -> dict[str, str]:
    safe = "".join(c for c in filename if 32 <= ord(c) < 127 and c not in '"\\')
    if not safe:
        safe = "file"
    return {
        "X-Content-Type-Options": "nosniff",
        "Content-Disposition": f'attachment; filename="{safe}"',
    }


def method_not_allowed(allow: str) -> Response:
    return JSONResponse(
        status_code=405,
        content={"detail": {"kind": "method_not_allowed"}},
        headers={"Allow": allow},
    )


def actor_assigned_409(exc: ActorAlreadyAssignedError) -> Response:
    return JSONResponse(
        status_code=409,
        content={
            "detail": {
                "kind": "actor_is_assigned",
                "actor_id": exc.actor_id,
                "assignments": exc.assignments,
            }
        },
    )


def map_move_failure(exc: Exception) -> Response:
    msg = str(exc)
    cls = type(exc).__name__
    if "TargetExists" in cls:
        return JSONResponse(
            status_code=409, content={"detail": {"kind": "target_exists", "target": msg}}
        )
    return JSONResponse(
        status_code=500, content={"detail": {"kind": "move_failed", "message": msg}}
    )
