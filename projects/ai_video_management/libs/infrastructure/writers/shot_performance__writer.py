"""Persist a shot's chosen performance-library references.

Writes/replaces the group of `表演库参考:` annotation lines in a shot.md. Each
line is rendered as::

    表演库参考: perf_NNNN (情绪·强度·风格·载体) — 用于 <角色> <beat>

The metadata in parentheses is read from each perf entry's YAML head; the
`<角色> <beat>` tail is left as a placeholder for the user to fill (or preserved
from the prior annotation line for the same perf_id when one already exists).

Insertion: the annotation group lives between the `## 视频 prompt` block and the
`## 台词配音 prompt` heading. An existing group is replaced in place; otherwise a
new group is inserted just before `## 台词配音 prompt` (falling back to end of
file when that heading is absent).

Atomic temp+os.replace write; If-Unmodified-Since (`mtime`, HTTP date) guard
mirrors FileWriter.
"""
from __future__ import annotations

import os
import re
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import format_datetime, parsedate_to_datetime
from pathlib import Path
from typing import Any

from libs.common.exposed_tree import ExposedTree
from libs.common.safe_resolve import SafeResolver
from libs.domain.errors.file__error import (
    FileNotInSandboxError,
    MissingIfUnmodifiedSinceError,
    StaleWriteError,
)
from libs.infrastructure.readers.performance_library__reader import (
    PerformanceLibraryReader,
)

_PERF_ID = re.compile(r"^perf_\d{4}$")
_REF_LINE = re.compile(r"^\s*表演库参考[:：]\s*(perf_\d{4})\b(.*)$")
_TAIL_AFTER_DASH = re.compile(r"—\s*(.*)$")
_PLACEHOLDER_TAIL = "用于 <角色> <beat>"
_VIDEO_HEADING = "## 视频 prompt"
_VOICE_HEADING = "## 台词配音 prompt"


@dataclass(frozen=True)
class ShotPerformanceWriteResult:
    rel_path: str
    content: str
    mtime_http: str

    def to_payload(self) -> dict[str, Any]:
        return {
            "path": self.rel_path,
            "content": self.content,
            "mtime": self.mtime_http,
        }


class ShotPerformanceWriter:
    def __init__(
        self,
        exposed: ExposedTree,
        resolver: SafeResolver,
        library: PerformanceLibraryReader,
    ) -> None:
        self._exposed = exposed
        self._resolver = resolver
        self._library = library

    def write(
        self,
        rel_shot_path: str,
        perf_ids: list[str],
        if_unmodified_since: str | None = None,
    ) -> ShotPerformanceWriteResult:
        norm = (rel_shot_path or "").replace("\\", "/")
        if not norm or not self._exposed.is_inside(norm):
            raise FileNotInSandboxError()
        shot = self._resolver.resolve(norm)
        if shot is None or not shot.is_file():
            raise FileNotInSandboxError()

        if if_unmodified_since is None:
            raise MissingIfUnmodifiedSinceError()
        current_mtime = shot.stat().st_mtime
        requested = self._parse_http_date(if_unmodified_since)
        if requested is not None and current_mtime > requested + 1.0:
            raise StaleWriteError(current_mtime=current_mtime)

        original = shot.read_text(encoding="utf-8")
        existing_tails = self._existing_tails(original)
        new_lines = [self._ref_line(pid, existing_tails.get(pid)) for pid in perf_ids]
        new_text = self._rewrite(original, new_lines)

        self._atomic_write(shot, new_text)
        stat = shot.stat()
        mtime_dt = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
        return ShotPerformanceWriteResult(
            rel_path=Path(norm).as_posix(),
            content=new_text,
            mtime_http=format_datetime(mtime_dt, usegmt=True),
        )

    def _ref_line(self, perf_id: str, prior_tail: str | None) -> str:
        meta = self._meta(perf_id)
        tail = prior_tail if prior_tail else _PLACEHOLDER_TAIL
        return f"表演库参考: {perf_id} ({meta}) — {tail}"

    def _meta(self, perf_id: str) -> str:
        if not _PERF_ID.match(perf_id):
            return "未知·?·?·?"
        entry = self._library.by_id(perf_id)
        if entry is None:
            return "未知 entry·?·?·?"
        intensity = str(entry.intensity) if entry.intensity is not None else "?"
        return "·".join(
            [
                entry.emotion or "?",
                f"强度{intensity}",
                entry.style or "?",
                entry.carrier or "?",
            ]
        )

    @staticmethod
    def _existing_tails(text: str) -> dict[str, str]:
        out: dict[str, str] = {}
        for line in text.splitlines():
            m = _REF_LINE.match(line)
            if m is None:
                continue
            perf_id = m.group(1)
            rest = m.group(2)
            dash = _TAIL_AFTER_DASH.search(rest)
            if dash:
                tail = dash.group(1).strip()
                if tail and tail != _PLACEHOLDER_TAIL:
                    out[perf_id] = tail
        return out

    def _rewrite(self, original: str, new_lines: list[str]) -> str:
        lines = original.splitlines()
        kept = [ln for ln in lines if not _REF_LINE.match(ln)]
        if not new_lines:
            return self._join(kept, original)

        block = ["", *new_lines, ""]
        voice_idx = self._heading_index(kept, _VOICE_HEADING)
        if voice_idx is not None:
            insert_at = voice_idx
            while insert_at > 0 and kept[insert_at - 1].strip() == "":
                insert_at -= 1
            result = kept[:insert_at] + block + kept[insert_at:]
            return self._join(result, original)

        result = kept + block
        return self._join(result, original)

    @staticmethod
    def _heading_index(lines: list[str], heading: str) -> int | None:
        for i, ln in enumerate(lines):
            if ln.strip() == heading:
                return i
        return None

    @staticmethod
    def _join(lines: list[str], original: str) -> str:
        text = "\n".join(lines)
        if original.endswith("\n") and not text.endswith("\n"):
            text += "\n"
        return text

    def _atomic_write(self, target: Path, body: str) -> None:
        parent = target.parent
        fd, tmp_str = tempfile.mkstemp(prefix=".shotperf_", suffix=".md.tmp", dir=str(parent))
        tmp = Path(tmp_str)
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
                f.write(body)
            os.replace(str(tmp), str(target))
        except OSError:
            try:
                tmp.unlink(missing_ok=True)
            except OSError:
                pass
            raise

    @staticmethod
    def _parse_http_date(value: str) -> float | None:
        try:
            dt = parsedate_to_datetime(value)
        except (TypeError, ValueError):
            return None
        if dt is None:
            return None
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.timestamp()
