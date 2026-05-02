from __future__ import annotations

from pathlib import Path


class OutsideSandbox(Exception):
    pass


class SymlinkRefused(Exception):
    pass


def safe_resolve(rel: str, root: Path) -> Path:
    if rel == "" or "\x00" in rel:
        raise OutsideSandbox("empty or invalid path")
    if rel.startswith("/") or rel.startswith("\\"):
        raise OutsideSandbox("absolute path not allowed")
    if len(rel) >= 2 and rel[1] == ":":
        raise OutsideSandbox("drive-letter absolute path not allowed")
    root_resolved = root.resolve()
    pre_resolve = root / rel
    try:
        joined = pre_resolve.resolve(strict=False)
    except (OSError, ValueError) as exc:
        raise OutsideSandbox(f"could not resolve path: {exc}") from None
    try:
        relative = joined.relative_to(root_resolved)
    except ValueError:
        raise OutsideSandbox("path escapes sandbox") from None
    _check_symlinks_along_path(pre_resolve, root_resolved)
    return relative


def _check_symlinks_along_path(pre_resolve: Path, root: Path) -> None:
    current = pre_resolve
    seen: set[Path] = set()
    while True:
        if current in seen:
            break
        seen.add(current)
        try:
            if current.is_symlink():
                raise SymlinkRefused("symlink refused")
        except OSError:
            pass
        parent = current.parent
        if parent == current:
            break
        try:
            if parent.resolve() == root:
                break
        except OSError:
            break
        current = parent
