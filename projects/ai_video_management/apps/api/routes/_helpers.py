"""Shared route helpers (cross-cutting across aggregate route files)."""
from __future__ import annotations


def file_security_headers(filename: str) -> dict[str, str]:
    safe = "".join(c for c in filename if 32 <= ord(c) < 127 and c not in '"\\')
    if not safe:
        safe = "file"
    return {
        "X-Content-Type-Options": "nosniff",
        "Content-Disposition": f'attachment; filename="{safe}"',
    }
