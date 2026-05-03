"""
safe_resolve — canonicalize FIRST, then assert containment.

Every file-touching API path passes through `SafeResolver.resolve(rel)`. The resolver
rejects (single error class -> HTTP 404):

- absolute paths
- path segments containing `..` after normalization
- paths with `\\` after Windows -> POSIX normalization that escape the sandbox
- Windows reserved device names (CON, PRN, AUX, NUL, COM1..9, LPT1..9, with or
  without extensions and case-insensitively)
- Alternate Data Streams (`::$DATA`, `:stream`)
- 8.3 short-name aliases (`PROGRA~1`)
- reparse points (junctions on Windows, symlinks on POSIX) at any segment
- NUL bytes / control chars in input
- paths whose canonical absolute form is not contained in EXPOSED_TREE root

Spec refs: FR-3, FR-4, NFR-4, NFR-5, AC-3, AC-4, AC-5, AC-6.
"""

from __future__ import annotations

import os
import re
import stat
import sys
from dataclasses import dataclass
from pathlib import Path

WIN_RESERVED = frozenset(
    {"CON", "PRN", "AUX", "NUL"}
    | {f"COM{i}" for i in range(1, 10)}
    | {f"LPT{i}" for i in range(1, 10)}
)
SHORT_NAME_RE = re.compile(r"^[^.]{1,8}~\d{1,7}(\..*)?$")
CONTROL_CHARS = re.compile(r"[\x00-\x1f]")


class OutsideTreeError(Exception):
    """Raised whenever a path fails sandbox checks. Mapped to HTTP 404."""


@dataclass(frozen=True)
class SafeResolver:
    root: Path

    def resolve(self, rel: str) -> Path:
        if not isinstance(rel, str):
            raise OutsideTreeError("path must be a string")
        if rel == "" or rel is None:
            raise OutsideTreeError("empty path")
        if CONTROL_CHARS.search(rel):
            raise OutsideTreeError("control character in path")
        if "::$" in rel.upper() or self._has_named_stream(rel):
            raise OutsideTreeError("alternate data stream rejected")

        normalized = rel.replace("\\", "/")
        if normalized.startswith("/") or self._is_absolute_windows(normalized):
            raise OutsideTreeError("absolute path rejected")
        if normalized.startswith("//") or normalized.startswith("\\\\"):
            raise OutsideTreeError("UNC path rejected")

        raw_segments = normalized.split("/")
        segments: list[str] = []
        for s in raw_segments:
            if s in ("", "."):
                continue
            if s == "..":
                if not segments:
                    raise OutsideTreeError("path traversal escapes tree root")
                segments.pop()
                continue
            segments.append(s)
        for seg in segments:
            if SHORT_NAME_RE.match(seg):
                raise OutsideTreeError("short-name alias rejected")
            stem = seg.split(".", 1)[0].upper().rstrip(" .")
            if stem in WIN_RESERVED:
                raise OutsideTreeError("windows reserved name rejected")

        candidate = (self.root / "/".join(segments)).resolve()
        try:
            candidate.relative_to(self.root)
        except ValueError as e:
            raise OutsideTreeError("path outside exposed tree") from e

        cur = candidate
        while cur != self.root:
            if cur.exists() and self._is_reparse_point(cur):
                raise OutsideTreeError("reparse point rejected")
            parent = cur.parent
            if parent == cur:
                break
            cur = parent

        return candidate

    @staticmethod
    def _has_named_stream(rel: str) -> bool:
        s = rel.replace("\\", "/")
        for seg in s.split("/"):
            colons = seg.count(":")
            if colons == 0:
                continue
            if colons == 1 and len(seg) >= 2 and seg[1] == ":" and seg[0].isalpha() and len(seg) == 2:
                continue
            return True
        return False

    @staticmethod
    def _is_absolute_windows(s: str) -> bool:
        if len(s) >= 2 and s[1] == ":" and s[0].isalpha():
            return True
        if s.startswith("\\\\?\\") or s.startswith("//?/"):
            return True
        return False

    @staticmethod
    def _is_reparse_point(p: Path) -> bool:
        try:
            st = p.lstat()
        except OSError:
            return False
        if stat.S_ISLNK(st.st_mode):
            return True
        if sys.platform == "win32":
            attrs = getattr(st, "st_file_attributes", 0)
            FILE_ATTRIBUTE_REPARSE_POINT = 0x400
            if attrs & FILE_ATTRIBUTE_REPARSE_POINT:
                return True
        return False
