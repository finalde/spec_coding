from __future__ import annotations

from pathlib import Path


class OutsideSandbox(Exception):
    pass


class SymlinkRefused(Exception):
    pass


def safe_resolve(rel: str, root: Path) -> Path:
    if not rel:
        raise OutsideSandbox("empty path")
    if "\x00" in rel:
        raise OutsideSandbox("null byte in path")
    candidate_rel = Path(rel)
    if candidate_rel.is_absolute() or (rel.startswith("\\\\") or rel.startswith("//")):
        raise OutsideSandbox("absolute paths are not accepted")
    root_resolved = root.resolve()
    candidate = (root_resolved / rel).resolve(strict=False)
    try:
        candidate.relative_to(root_resolved)
    except ValueError as err:
        raise OutsideSandbox(f"resolved path escapes root: {candidate}") from err
    if candidate.is_symlink():
        raise SymlinkRefused(f"refusing to follow symlink: {candidate}")
    return candidate
