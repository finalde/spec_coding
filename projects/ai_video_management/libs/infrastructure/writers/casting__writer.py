"""Casting table management for `ai_videos/{drama}/casting.md`.

Per follow-up 014: each drama owns one `casting.md` with a single markdown
table mapping each role to one actor in the pool. The file is rewritten
atomically on every assign / unassign — no surgical line edits inside
markdown tables (boundary cases are too easy to get wrong).
"""
from __future__ import annotations

import os
import re
import shutil
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from libs.infrastructure.writers.actor__writer import ActorPool
from libs.common.exposed_tree import ExposedTree
from libs.infrastructure.writers.media__writer import DramaNotFound, InvalidDramaPath, MediaRenamer
from libs.common.safe_resolve import SafeResolver


from libs.infrastructure.errors.casting__error import (  # noqa: F401
    InvalidActorId,
    InvalidRole,
)
CASTING_FILE_NAME: str = "casting.md"
CAST_LINK_FILE_NAME: str = "_cast.md"
CAST_DIR_NAME: str = "cast"
CAST_IMAGE_NAME: str = "cast.jpg"
_ROLE_INVALID_RE = re.compile(r"[\x00-\x1f|]")
_ACTOR_ID_SHAPE_RE = re.compile(r"^actor_\d{4,}$")


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
        self._write_character_link(drama_dir, role, actor_id, notes)
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
        self._remove_character_link(drama_dir, role)
        return CastingResult(path=self._rel(casting_path), entries=[e.to_dict() for e in entries])

    def find_assignments_for_actor(self, actor_id: str) -> list[dict[str, object]]:
        """Scan every drama's casting.md, return rows where actor_id matches.

        Per follow-up 043: backs `GET /api/actors/assignments` and the
        delete/archive refusal in `POST /api/actors/delete`,
        `POST /api/archive-media`, `POST /api/delete-media`. Returns
        `[{drama, role, notes, character_folder, character_folder_exists}, ...]`
        sorted by (drama, role).
        """
        if not _ACTOR_ID_SHAPE_RE.match(actor_id):
            raise InvalidActorId(f"actor_id={actor_id!r} does not match shape")
        ai_videos = self._resolver.root / "ai_videos"
        if not ai_videos.is_dir():
            return []
        out: list[dict[str, object]] = []
        for drama_dir in sorted(ai_videos.iterdir(), key=lambda p: p.name):
            if not drama_dir.is_dir() or drama_dir.is_symlink():
                continue
            if drama_dir.name.startswith("_"):
                continue
            casting_path = drama_dir / CASTING_FILE_NAME
            if not casting_path.is_file():
                continue
            entries = self._parse(casting_path)
            for e in entries:
                if e.actor_id != actor_id:
                    continue
                character_folder = drama_dir / "characters" / e.role
                out.append(
                    {
                        "drama": drama_dir.name,
                        "role": e.role,
                        "notes": e.notes,
                        "character_folder": self._rel(character_folder),
                        "character_folder_exists": character_folder.is_dir(),
                    }
                )
        out.sort(key=lambda r: (str(r["drama"]), str(r["role"])))
        return out

    def assigned_actor_ids(self) -> set[str]:
        """Per follow-up 086: single-pass scan over every drama's casting.md
        returning the union of actor_ids appearing in any row. Used by
        `ActorQuery.list()` to compute each actor's `is_assigned` flag for
        the grid filter without N × `find_assignments_for_actor` round
        trips. O(drama_count × rows_per_casting) total."""
        ai_videos = self._resolver.root / "ai_videos"
        if not ai_videos.is_dir():
            return set()
        ids: set[str] = set()
        for drama_dir in ai_videos.iterdir():
            if not drama_dir.is_dir() or drama_dir.is_symlink():
                continue
            if drama_dir.name.startswith("_"):
                continue
            casting_path = drama_dir / CASTING_FILE_NAME
            if not casting_path.is_file():
                continue
            for entry in self._parse(casting_path):
                if entry.actor_id:
                    ids.add(entry.actor_id)
        return ids

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
                    self._remove_character_link(drama_dir, e.role)
            self._write(casting_path, drama_dir.name, kept)
        return removed

    def _write_character_link(
        self, drama_dir: Path, role: str, actor_id: str, notes: str
    ) -> None:
        """Per follow-up 043: write `_cast.md` inside the character folder.

        Silently skipped when `characters/{role}/` is not a directory — the
        role might be free-text not corresponding to a folder; the casting.md
        row is still authoritative. Atomic temp+replace; OSError swallowed
        with a stderr warning (the casting.md row is the truth source).

        Also refreshes the `cast/cast.jpg` mirror so the picture in the
        character cast folder always reflects the currently-assigned actor.
        """
        character_folder = drama_dir / "characters" / role
        if not character_folder.is_dir() or character_folder.is_symlink():
            return
        face_filename = self._actor_pool.actor_face_filename(actor_id)
        body = self._build_character_link_body(
            drama_dir.name, role, actor_id, notes, face_filename
        )
        cast_path = character_folder / CAST_LINK_FILE_NAME
        try:
            fd, tmp_str = tempfile.mkstemp(
                prefix=".cast_", suffix=".md.tmp", dir=str(character_folder)
            )
            tmp = Path(tmp_str)
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
                f.write(body)
            os.replace(str(tmp), str(cast_path))
        except OSError:
            try:
                tmp.unlink(missing_ok=True)  # type: ignore[possibly-unbound]
            except (OSError, NameError):
                pass
        self._mirror_cast_image(character_folder, actor_id, face_filename)

    def _remove_character_link(self, drama_dir: Path, role: str) -> None:
        """Per follow-up 043: best-effort delete the `_cast.md` sibling of the
        character folder. Missing file / OSError silently ignored — the
        casting.md row removal is the authoritative state change.

        Also clears the `cast/cast.jpg` mirror (and the `cast/` dir if empty)
        so a stale picture doesn't linger after unassign.
        """
        character_folder = drama_dir / "characters" / role
        cast_path = character_folder / CAST_LINK_FILE_NAME
        try:
            cast_path.unlink(missing_ok=True)
        except OSError:
            pass
        self._clear_cast_image(character_folder)

    def _mirror_cast_image(
        self, character_folder: Path, actor_id: str, face_filename: str | None
    ) -> None:
        """Copy the actor's face jpg into `cast/cast.jpg` so the image inside
        the character cast folder always reflects the currently-assigned actor.

        Best-effort: missing source or OSError silently ignored — `_cast.md`
        still carries the canonical relative link to the actor folder.
        """
        if face_filename is None:
            self._clear_cast_image(character_folder)
            return
        src = self._actor_pool.actors_dir() / actor_id / face_filename
        if not src.is_file() or src.is_symlink():
            return
        cast_dir = character_folder / CAST_DIR_NAME
        try:
            cast_dir.mkdir(exist_ok=True)
        except OSError:
            return
        if not cast_dir.is_dir() or cast_dir.is_symlink():
            return
        dst = cast_dir / CAST_IMAGE_NAME
        try:
            fd, tmp_str = tempfile.mkstemp(
                prefix=".cast_img_", suffix=".jpg.tmp", dir=str(cast_dir)
            )
            os.close(fd)
            tmp = Path(tmp_str)
            shutil.copyfile(str(src), str(tmp))
            os.replace(str(tmp), str(dst))
        except OSError:
            try:
                tmp.unlink(missing_ok=True)  # type: ignore[possibly-unbound]
            except (OSError, NameError):
                pass

    def _clear_cast_image(self, character_folder: Path) -> None:
        cast_dir = character_folder / CAST_DIR_NAME
        if not cast_dir.is_dir() or cast_dir.is_symlink():
            return
        cast_image = cast_dir / CAST_IMAGE_NAME
        try:
            cast_image.unlink(missing_ok=True)
        except OSError:
            pass
        try:
            if not any(cast_dir.iterdir()):
                cast_dir.rmdir()
        except OSError:
            pass

    @staticmethod
    def _build_character_link_body(
        drama: str, role: str, actor_id: str, notes: str, face_filename: str | None
    ) -> str:
        notes_cell = notes if notes else "—"
        face_md = (
            f"![{actor_id} face](../../../_actors/{actor_id}/{face_filename})\n\n"
            if face_filename
            else ""
        )
        return (
            f"# 演员分配 — {role}\n"
            "\n"
            "| 字段 | 值 |\n"
            "|---|---|\n"
            f"| 短剧 | {drama} |\n"
            f"| 角色 | {role} |\n"
            f"| Actor ID | {actor_id} |\n"
            f"| 备注 | {notes_cell} |\n"
            "\n"
            f"{face_md}"
            f"[查看演员档案](../../../_actors/{actor_id}/{actor_id}.md)\n"
            "\n"
            "<!-- 由 webapp 维护（follow-up 043）。请在 ActorView 或 CastingView 修改分配；勿手编 -->\n"
        )

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
    "CAST_LINK_FILE_NAME",
    "CAST_DIR_NAME",
    "CAST_IMAGE_NAME",
    "CastEntry",
    "Casting",
    "CastingResult",
    "DramaNotFound",
    "InvalidActorId",
    "InvalidDramaPath",
    "InvalidRole",
]
