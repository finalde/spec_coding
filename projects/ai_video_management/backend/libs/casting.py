"""Casting table management for `ai_videos/{drama}/casting.md`.

Per follow-up 014: each drama owns one `casting.md` with a single markdown
table mapping each role to one actor in the pool. The file is rewritten
atomically on every assign / unassign — no surgical line edits inside
markdown tables (boundary cases are too easy to get wrong).
"""
from __future__ import annotations

import os
import re
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from libs.actor_pool import ActorPool
from libs.exposed_tree import ExposedTree
from libs.media_renamer import DramaNotFound, InvalidDramaPath, MediaRenamer
from libs.safe_resolve import SafeResolver

CASTING_FILE_NAME: str = "casting.md"
_ROLE_INVALID_RE = re.compile(r"[\x00-\x1f|]")


class InvalidActorId(Exception):
    pass


class InvalidRole(Exception):
    pass


@dataclass(frozen=True)
class CastEntry:
    role: str
    actor_id: str
    notes: str

    def to_dict(self) -> dict[str, str]:
        return {"role": self.role, "actor_id": self.actor_id, "notes": self.notes}


@dataclass
class CastingResult:
    path: str
    entries: list[dict[str, str]] = field(default_factory=list)

    def to_payload(self) -> dict[str, object]:
        return {"path": self.path, "entries": list(self.entries)}


class Casting:
    def __init__(
        self,
        exposed: ExposedTree,
        resolver: SafeResolver,
        renamer: MediaRenamer,
        actor_pool: ActorPool,
    ) -> None:
        self._exposed = exposed
        self._resolver = resolver
        self._renamer = renamer
        self._actor_pool = actor_pool

    def read(self, rel_drama_path: str) -> CastingResult:
        drama_dir = self._renamer.validate_drama(rel_drama_path)
        casting_path = drama_dir / CASTING_FILE_NAME
        entries = self._parse(casting_path) if casting_path.is_file() else []
        return CastingResult(path=self._rel(casting_path), entries=[e.to_dict() for e in entries])

    def assign(self, rel_drama_path: str, role: str, actor_id: str, notes: str = "") -> CastingResult:
        drama_dir = self._renamer.validate_drama(rel_drama_path)
        self._validate_role(role)
        if not self._actor_pool.actor_exists(actor_id):
            raise InvalidActorId(f"actor_id={actor_id!r} not found in pool")
        casting_path = drama_dir / CASTING_FILE_NAME
        entries = self._parse(casting_path) if casting_path.is_file() else []
        entries = [e for e in entries if e.role != role]
        entries.append(CastEntry(role=role, actor_id=actor_id, notes=notes))
        self._write(casting_path, drama_dir.name, entries)
        return CastingResult(path=self._rel(casting_path), entries=[e.to_dict() for e in entries])

    def unassign(self, rel_drama_path: str, role: str) -> CastingResult:
        drama_dir = self._renamer.validate_drama(rel_drama_path)
        self._validate_role(role)
        casting_path = drama_dir / CASTING_FILE_NAME
        if not casting_path.is_file():
            raise DramaNotFound(f"no casting.md at {self._rel(casting_path)}")
        entries = self._parse(casting_path)
        before = len(entries)
        entries = [e for e in entries if e.role != role]
        if len(entries) == before:
            raise DramaNotFound(f"role={role!r} not in casting.md")
        self._write(casting_path, drama_dir.name, entries)
        return CastingResult(path=self._rel(casting_path), entries=[e.to_dict() for e in entries])

    def unassign_actor_everywhere(self, actor_id: str) -> list[dict[str, str]]:
        """Sweep every drama's casting.md, remove rows where actor_id matches.

        Per follow-up 026 cascade requirement: called by `POST /api/actors/delete`
        before the actor folder is moved so casting.md never references a deleted
        actor. Best-effort over the drama set: missing casting.md → skip;
        OS error on read / write → propagates (endpoint maps to 500).
        Returns a list of `{drama, role}` removed entries for the endpoint's
        response so the UI can report how many casting references were cleared.
        """
        ai_videos = self._resolver.root / "ai_videos"
        if not ai_videos.is_dir():
            return []
        removed: list[dict[str, str]] = []
        for drama_dir in sorted(ai_videos.iterdir(), key=lambda p: p.name):
            if not drama_dir.is_dir() or drama_dir.is_symlink():
                continue
            if drama_dir.name.startswith("_"):
                continue
            casting_path = drama_dir / CASTING_FILE_NAME
            if not casting_path.is_file():
                continue
            entries = self._parse(casting_path)
            kept = [e for e in entries if e.actor_id != actor_id]
            if len(kept) == len(entries):
                continue
            for e in entries:
                if e.actor_id == actor_id:
                    removed.append({"drama": drama_dir.name, "role": e.role})
            self._write(casting_path, drama_dir.name, kept)
        return removed

    @staticmethod
    def _validate_role(role: str) -> None:
        if not isinstance(role, str) or not role.strip():
            raise InvalidRole("role must be a non-empty string")
        if len(role) > 200:
            raise InvalidRole("role must be ≤ 200 characters")
        if _ROLE_INVALID_RE.search(role):
            raise InvalidRole("role contains control characters or markdown table separator")

    @staticmethod
    def _parse(casting_path: Path) -> list[CastEntry]:
        try:
            text = casting_path.read_text(encoding="utf-8")
        except OSError:
            return []
        out: list[CastEntry] = []
        in_table = False
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped.startswith("|"):
                in_table = False
                continue
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if len(cells) < 3:
                continue
            if cells[0].lower() == "role" or set(cells[0]) <= {"-", ":"}:
                in_table = True
                continue
            if not in_table:
                continue
            role, actor_id = cells[0], cells[1]
            notes = cells[2] if len(cells) > 2 else ""
            if not role or not actor_id:
                continue
            if notes == "—":
                notes = ""
            out.append(CastEntry(role=role, actor_id=actor_id, notes=notes))
        return out

    @staticmethod
    def _write(casting_path: Path, drama_name: str, entries: list[CastEntry]) -> None:
        lines: list[str] = [
            f"# Casting — {drama_name}",
            "",
            "<!-- Managed by ai_video_management webapp (follow-up 014). Edit via CastingView. -->",
            "",
            "| role | actor_id | notes |",
            "|---|---|---|",
        ]
        for entry in entries:
            notes_cell = entry.notes if entry.notes else "—"
            lines.append(f"| {entry.role} | {entry.actor_id} | {notes_cell} |")
        body = "\n".join(lines) + "\n"
        parent = casting_path.parent
        parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_str = tempfile.mkstemp(prefix=".casting_", suffix=".md.tmp", dir=str(parent))
        tmp = Path(tmp_str)
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
                f.write(body)
            os.replace(str(tmp), str(casting_path))
        except OSError:
            try:
                tmp.unlink(missing_ok=True)
            except OSError:
                pass
            raise

    def _rel(self, p: Path) -> str:
        try:
            return p.resolve().relative_to(self._resolver.root).as_posix()
        except (OSError, ValueError):
            return p.as_posix()


__all__ = [
    "CASTING_FILE_NAME",
    "CastEntry",
    "Casting",
    "CastingResult",
    "DramaNotFound",
    "InvalidActorId",
    "InvalidDramaPath",
    "InvalidRole",
]
