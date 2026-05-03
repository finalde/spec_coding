from __future__ import annotations

import re
from pathlib import Path

_WIN_RESERVED = re.compile(
    r"^(con|prn|aux|nul|com[1-9]|lpt[1-9])(\..*)?$",
    re.IGNORECASE,
)
_SHORT_NAME = re.compile(r"~\d")
_EXCLUDED_TOP_LEVEL: frozenset[str] = frozenset(
    {"node_modules", ".git", ".audit", "__pycache__", ".pytest_cache", "dist", "build", ".vite"}
)
_ALLOWED_TOP_LEVEL: frozenset[str] = frozenset(
    {"CLAUDE.md", ".claude", "specs", "projects"}
)


class SandboxViolation(Exception):
    pass


class SafeResolver:
    def __init__(self, root: Path) -> None:
        self._root = root.resolve()

    def resolve(self, rel: str) -> Path | None:
        if not isinstance(rel, str):
            return None
        if rel == "":
            return None
        if rel != rel.strip():
            return None
        if any(ord(c) < 32 for c in rel):
            return None
        if "\\" in rel:
            return None
        if "%" in rel:
            return None
        if rel.startswith("/") or rel.startswith("~"):
            return None
        p = Path(rel)
        if p.is_absolute():
            return None
        parts = rel.split("/")
        for seg in parts:
            if seg == "":
                return None
            if seg == ".":
                continue
            if seg == "..":
                return None
            if ":" in seg:
                return None
            if _SHORT_NAME.search(seg):
                return None
            if _WIN_RESERVED.match(seg):
                return None

        first = parts[0]
        if first in _EXCLUDED_TOP_LEVEL:
            return None
        if first not in _ALLOWED_TOP_LEVEL:
            return None
        if first == ".claude":
            if len(parts) < 2 or parts[1] not in {"skills", "agent_refs"}:
                return None
        for seg in parts:
            if seg in _EXCLUDED_TOP_LEVEL:
                return None

        candidate = self._root / rel
        try:
            for ancestor in [candidate, *list(candidate.parents)]:
                if ancestor == self._root:
                    break
                try:
                    if ancestor.exists() and ancestor.is_symlink():
                        return None
                except OSError:
                    return None
        except OSError:
            return None

        try:
            resolved = candidate.resolve(strict=False)
        except OSError:
            return None

        if not (resolved == self._root or self._root in resolved.parents):
            return None

        try:
            if resolved.is_symlink():
                return None
        except OSError:
            return None

        if not resolved.exists():
            try:
                parent = resolved.parent
            except (OSError, ValueError):
                return None
            if not parent.is_dir():
                return None
            try:
                if parent.is_symlink():
                    return None
            except OSError:
                return None

        return resolved

    @property
    def root(self) -> Path:
        return self._root
