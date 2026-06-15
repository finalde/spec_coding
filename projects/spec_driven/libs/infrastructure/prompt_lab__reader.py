from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from libs.common.exposed_tree import MAX_FILE_BYTES, ExposedTree

_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_TITLE = re.compile(r"^#\s+(.+)")


class PromptLabReader:
    """Parses prompt_lab/{category}/{task}/prompt.md into an overview payload (FR-43/FR-44).

    Each task is its own folder (its workspace); the instruction lives in prompt.md and
    the latest run state (if any) in status.json beside it.
    """

    def __init__(self, exposed: ExposedTree) -> None:
        self._exposed = exposed
        self._root = exposed.root

    def overview(self) -> list[dict[str, Any]]:
        base = self._root / "prompt_lab"
        if not base.is_dir():
            return []
        categories: list[dict[str, Any]] = []
        for cat in sorted(p for p in base.iterdir() if p.is_dir() and not p.is_symlink()):
            entries: list[dict[str, Any]] = []
            for item in sorted(p for p in cat.iterdir() if p.is_dir() and not p.is_symlink()):
                md = item / "prompt.md"
                if md.is_file():
                    entries.append(self._parse(md, item))
            if entries:
                categories.append({"name": cat.name, "entries": entries})
        return categories

    def _parse(self, md: Path, item: Path) -> dict[str, Any]:
        try:
            text = (
                "" if md.stat().st_size > MAX_FILE_BYTES
                else md.read_text(encoding="utf-8", errors="replace")
            )
        except OSError:
            text = ""
        lines = text.split("\n")
        title = item.name
        for line in lines:
            m = _TITLE.match(line)
            if m:
                title = m.group(1).strip()
                break
        meta = next((line.strip() for line in lines if line.startswith("**Stack:**")), "")
        return {
            "path": self._rel(md),
            "name": item.name,
            "title": title,
            "meta": meta,
            "source": self._link_after(lines, "**Source:**"),
            "expected": self._link_after(lines, "**Expected result:**"),
            "prompt": self._first_fence(lines),
            "run_state": self._run_state(item),
        }

    @staticmethod
    def _run_state(item: Path) -> str | None:
        status = item / "status.json"
        if not status.is_file():
            return None
        try:
            return json.loads(status.read_text(encoding="utf-8")).get("state")
        except (OSError, ValueError):
            return None

    @staticmethod
    def _link_after(lines: list[str], marker: str) -> dict[str, str] | None:
        for line in lines:
            idx = line.find(marker)
            if idx >= 0:
                m = _LINK.search(line[idx + len(marker):])
                if m:
                    return {"label": m.group(1).strip(), "url": m.group(2).strip()}
                return None
        return None

    @staticmethod
    def _first_fence(lines: list[str]) -> str:
        start = next((i for i, line in enumerate(lines) if line.startswith("```")), -1)
        if start < 0:
            return ""
        out: list[str] = []
        for j in range(start + 1, len(lines)):
            if lines[j].startswith("```"):
                break
            out.append(lines[j])
        return "\n".join(out).strip()

    def _rel(self, p: Path) -> str:
        try:
            return p.resolve().relative_to(self._root).as_posix()
        except ValueError:
            return p.as_posix()
