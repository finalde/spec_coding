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

from libs.common import drama_layout
from libs.common.exposed_tree import ExposedTree
from libs.common.safe_resolve import SafeResolver
from libs.domain.errors.actor__error import InvalidActorIdError
from libs.domain.errors.casting__error import (
    DramaNotFoundError,
    InvalidDramaPathError,
    InvalidRoleError,
)
from libs.domain.errors.voice__error import InvalidVoiceIdError
from libs.infrastructure.writers.actor__writer import ActorPool
from libs.infrastructure.writers.media__writer import MediaRenamer
from libs.infrastructure.writers.voice__writer import VoicePool

CASTING_FILE_NAME: str = "casting.md"
CAST_LINK_FILE_NAME: str = "_cast.md"
CAST_DIR_NAME: str = "cast"
CAST_IMAGE_NAME: str = "cast.jpg"
_ROLE_INVALID_RE = re.compile(r"[\x00-\x1f|]")
_ACTOR_ID_SHAPE_RE = re.compile(r"^actor_\d{4,}$")
_VOICE_ID_SHAPE_RE = re.compile(r"^voice_\d{4,}$")


@dataclass(frozen=True)
class CastEntry:
    role: str
    actor_id: str
    notes: str
    voice_id: str = ""  # Follow-up 115: optional voice binding alongside actor.

    def to_dict(self) -> dict[str, str]:
        return {
            "role": self.role,
            "actor_id": self.actor_id,
            "voice_id": self.voice_id,
            "notes": self.notes,
        }


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
        voice_pool: VoicePool | None = None,
    ) -> None:
        self._exposed = exposed
        self._resolver = resolver
        self._renamer = renamer
        self._actor_pool = actor_pool
        # Follow-up 115: voice_pool is required for voice-side flows; left
        # optional in the signature so existing tests that construct Casting
        # without it still pass. The voice-side endpoints inject the real
        # pool via the DI container.
        self._voice_pool = voice_pool

    def read(self, rel_drama_path: str) -> CastingResult:
        drama_dir = self._renamer.validate_drama(rel_drama_path)
        casting_path = drama_layout.casting_md(drama_dir)
        entries = self._parse(casting_path) if casting_path.is_file() else []
        return CastingResult(path=self._rel(casting_path), entries=[e.to_dict() for e in entries])

    def assign(self, rel_drama_path: str, role: str, actor_id: str, notes: str = "") -> CastingResult:
        drama_dir = self._renamer.validate_drama(rel_drama_path)
        self._validate_role(role)
        if not self._actor_pool.actor_exists(actor_id):
            raise InvalidActorIdError(f"actor_id={actor_id!r} not found in pool")
        casting_path = drama_layout.casting_md(drama_dir)
        entries = self._parse(casting_path) if casting_path.is_file() else []
        # Preserve any existing voice_id on this role — actor assignment
        # never clobbers the voice column (follow-up 115).
        existing_voice = ""
        for e in entries:
            if e.role == role:
                existing_voice = e.voice_id
                break
        entries = [e for e in entries if e.role != role]
        entries.append(
            CastEntry(role=role, actor_id=actor_id, notes=notes, voice_id=existing_voice)
        )
        self._write(casting_path, drama_dir.name, entries)
        self._write_character_link(drama_dir, role, actor_id, existing_voice, notes)
        return CastingResult(path=self._rel(casting_path), entries=[e.to_dict() for e in entries])

    def unassign(self, rel_drama_path: str, role: str) -> CastingResult:
        """Clear the actor_id cell. Per follow-up 115: the row stays alive if
        a voice_id is still bound (only the actor cell goes empty); otherwise
        the whole row is removed and the character _cast.md is deleted."""
        drama_dir = self._renamer.validate_drama(rel_drama_path)
        self._validate_role(role)
        casting_path = drama_layout.casting_md(drama_dir)
        if not casting_path.is_file():
            raise DramaNotFoundError(f"no casting.md at {self._rel(casting_path)}")
        entries = self._parse(casting_path)
        new_entries: list[CastEntry] = []
        touched = False
        for e in entries:
            if e.role == role:
                touched = True
                if e.voice_id:
                    new_entries.append(
                        CastEntry(role=e.role, actor_id="", notes=e.notes, voice_id=e.voice_id)
                    )
            else:
                new_entries.append(e)
        if not touched:
            raise DramaNotFoundError(f"role={role!r} not in casting.md")
        self._write(casting_path, drama_dir.name, new_entries)
        remaining = next((e for e in new_entries if e.role == role), None)
        if remaining is not None:
            # Re-render _cast.md without the actor section (voice stays).
            self._write_character_link(
                drama_dir, role, "", remaining.voice_id, remaining.notes
            )
        else:
            self._remove_character_link(drama_dir, role)
        return CastingResult(
            path=self._rel(casting_path), entries=[e.to_dict() for e in new_entries]
        )

    def assign_voice(
        self,
        rel_drama_path: str,
        role: str,
        voice_id: str,
        notes: str | None = None,
    ) -> CastingResult:
        """Bind a voice profile to a role. Preserves any existing actor_id on
        the same row. If no row exists yet, creates one with actor_id="".
        `notes` overwrites only when non-None (None = keep existing notes)."""
        drama_dir = self._renamer.validate_drama(rel_drama_path)
        self._validate_role(role)
        if self._voice_pool is None or not self._voice_pool.voice_exists(voice_id):
            raise InvalidVoiceIdError(f"voice_id={voice_id!r} not found in pool")
        casting_path = drama_layout.casting_md(drama_dir)
        entries = self._parse(casting_path) if casting_path.is_file() else []
        existing_actor = ""
        existing_notes = ""
        for e in entries:
            if e.role == role:
                existing_actor = e.actor_id
                existing_notes = e.notes
                break
        entries = [e for e in entries if e.role != role]
        final_notes = notes if notes is not None else existing_notes
        entries.append(
            CastEntry(
                role=role,
                actor_id=existing_actor,
                notes=final_notes,
                voice_id=voice_id,
            )
        )
        self._write(casting_path, drama_dir.name, entries)
        self._write_character_link(drama_dir, role, existing_actor, voice_id, final_notes)
        return CastingResult(
            path=self._rel(casting_path), entries=[e.to_dict() for e in entries]
        )

    def unassign_voice(self, rel_drama_path: str, role: str) -> CastingResult:
        """Clear only the voice_id cell. If actor_id is also empty after the
        clear, drop the row entirely."""
        drama_dir = self._renamer.validate_drama(rel_drama_path)
        self._validate_role(role)
        casting_path = drama_layout.casting_md(drama_dir)
        if not casting_path.is_file():
            raise DramaNotFoundError(f"no casting.md at {self._rel(casting_path)}")
        entries = self._parse(casting_path)
        new_entries: list[CastEntry] = []
        touched = False
        for e in entries:
            if e.role == role:
                touched = True
                if e.actor_id:
                    new_entries.append(
                        CastEntry(role=e.role, actor_id=e.actor_id, notes=e.notes, voice_id="")
                    )
            else:
                new_entries.append(e)
        if not touched:
            raise DramaNotFoundError(f"role={role!r} not in casting.md")
        self._write(casting_path, drama_dir.name, new_entries)
        # Rebuild the character link with the cleared voice (and existing actor).
        remaining = next((e for e in new_entries if e.role == role), None)
        if remaining is not None:
            self._write_character_link(
                drama_dir, role, remaining.actor_id, "", remaining.notes
            )
        else:
            self._remove_character_link(drama_dir, role)
        return CastingResult(
            path=self._rel(casting_path), entries=[e.to_dict() for e in new_entries]
        )

    def find_voice_assignments_for_voice(self, voice_id: str) -> list[dict[str, object]]:
        """Mirror of find_assignments_for_actor for voice bindings."""
        if not _VOICE_ID_SHAPE_RE.match(voice_id):
            raise InvalidVoiceIdError(f"voice_id={voice_id!r} does not match shape")
        ai_videos = self._resolver.root / "ai_videos"
        if not ai_videos.is_dir():
            return []
        out: list[dict[str, object]] = []
        for drama_dir in sorted(ai_videos.iterdir(), key=lambda p: p.name):
            if not drama_dir.is_dir() or drama_dir.is_symlink():
                continue
            if drama_dir.name.startswith("_"):
                continue
            casting_path = drama_layout.casting_md(drama_dir)
            if not casting_path.is_file():
                continue
            entries = self._parse(casting_path)
            for e in entries:
                if e.voice_id != voice_id:
                    continue
                character_folder = drama_layout.characters_dir(drama_dir) / e.role
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

    def assigned_voice_ids(self) -> set[str]:
        ai_videos = self._resolver.root / "ai_videos"
        if not ai_videos.is_dir():
            return set()
        ids: set[str] = set()
        for drama_dir in ai_videos.iterdir():
            if not drama_dir.is_dir() or drama_dir.is_symlink():
                continue
            if drama_dir.name.startswith("_"):
                continue
            casting_path = drama_layout.casting_md(drama_dir)
            if not casting_path.is_file():
                continue
            for entry in self._parse(casting_path):
                if entry.voice_id:
                    ids.add(entry.voice_id)
        return ids

    def find_assignments_for_actor(self, actor_id: str) -> list[dict[str, object]]:
        """Scan every drama's casting.md, return rows where actor_id matches.

        Per follow-up 043: backs `GET /api/actors/assignments` and the
        delete/archive refusal in `POST /api/actors/delete`,
        `POST /api/archive-media`, `POST /api/delete-media`. Returns
        `[{drama, role, notes, character_folder, character_folder_exists}, ...]`
        sorted by (drama, role).
        """
        if not _ACTOR_ID_SHAPE_RE.match(actor_id):
            raise InvalidActorIdError(f"actor_id={actor_id!r} does not match shape")
        ai_videos = self._resolver.root / "ai_videos"
        if not ai_videos.is_dir():
            return []
        out: list[dict[str, object]] = []
        for drama_dir in sorted(ai_videos.iterdir(), key=lambda p: p.name):
            if not drama_dir.is_dir() or drama_dir.is_symlink():
                continue
            if drama_dir.name.startswith("_"):
                continue
            casting_path = drama_layout.casting_md(drama_dir)
            if not casting_path.is_file():
                continue
            entries = self._parse(casting_path)
            for e in entries:
                if e.actor_id != actor_id:
                    continue
                character_folder = drama_layout.characters_dir(drama_dir) / e.role
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
            casting_path = drama_layout.casting_md(drama_dir)
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
            casting_path = drama_layout.casting_md(drama_dir)
            if not casting_path.is_file():
                continue
            entries = self._parse(casting_path)
            # Per follow-up 115: clear only the actor_id cell, keep the row
            # when a voice_id is still bound — otherwise drop the row entirely.
            kept: list[CastEntry] = []
            changed = False
            for e in entries:
                if e.actor_id == actor_id:
                    changed = True
                    if e.voice_id:
                        kept.append(
                            CastEntry(role=e.role, actor_id="", notes=e.notes, voice_id=e.voice_id)
                        )
                    else:
                        removed.append({"drama": drama_dir.name, "role": e.role})
                        self._remove_character_link(drama_dir, e.role)
                else:
                    kept.append(e)
            if not changed:
                continue
            self._write(casting_path, drama_dir.name, kept)
        return removed

    def _write_character_link(
        self,
        drama_dir: Path,
        role: str,
        actor_id: str,
        voice_id: str,
        notes: str,
    ) -> None:
        """Per follow-up 043 (+ follow-up 115 voice section): write `_cast.md`
        inside the character folder.

        Silently skipped when `characters/{role}/` is not a directory — the
        role might be free-text not corresponding to a folder; the casting.md
        row is still authoritative. Atomic temp+replace; OSError swallowed
        (the casting.md row is the truth source).
        """
        character_folder = drama_layout.characters_dir(drama_dir) / role
        if not character_folder.is_dir() or character_folder.is_symlink():
            return
        face_filename = self._actor_pool.actor_face_filename(actor_id) if actor_id else None
        audio_filename = (
            self._voice_pool.voice_audio_filename(voice_id)
            if voice_id and self._voice_pool is not None
            else None
        )
        body = self._build_character_link_body(
            drama_dir.name, role, actor_id, voice_id, notes, face_filename, audio_filename
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
        character_folder = drama_layout.characters_dir(drama_dir) / role
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
        drama: str,
        role: str,
        actor_id: str,
        voice_id: str,
        notes: str,
        face_filename: str | None,
        audio_filename: str | None,
    ) -> str:
        notes_cell = notes if notes else "—"
        actor_section = ""
        if actor_id:
            face_md = (
                f"![{actor_id} face](../../../_actors/{actor_id}/{face_filename})\n\n"
                if face_filename
                else ""
            )
            actor_section = (
                f"## 🎭 演员\n"
                "\n"
                "| 字段 | 值 |\n"
                "|---|---|\n"
                f"| Actor ID | {actor_id} |\n"
                "\n"
                f"{face_md}"
                f"[查看演员档案](../../../_actors/{actor_id}/{actor_id}.md)\n"
                "\n"
            )
        voice_section = ""
        if voice_id:
            audio_md = (
                f'<audio controls src="../../../_voices/{voice_id}/{audio_filename}"></audio>\n\n'
                if audio_filename
                else ""
            )
            voice_section = (
                f"## 🎙 配音\n"
                "\n"
                "| 字段 | 值 |\n"
                "|---|---|\n"
                f"| Voice ID | {voice_id} |\n"
                "\n"
                f"{audio_md}"
                f"[查看配音档案](../../../_voices/{voice_id}/{voice_id}.md)\n"
                "\n"
            )
        return (
            f"# 角色分配 — {role}\n"
            "\n"
            "| 字段 | 值 |\n"
            "|---|---|\n"
            f"| 短剧 | {drama} |\n"
            f"| 角色 | {role} |\n"
            f"| 备注 | {notes_cell} |\n"
            "\n"
            f"{actor_section}"
            f"{voice_section}"
            "<!-- 由 webapp 维护（follow-up 043 + 115）。请在 ActorView / VoiceView / CastingView 修改分配；勿手编 -->\n"
        )

    @staticmethod
    def _validate_role(role: str) -> None:
        if not isinstance(role, str) or not role.strip():
            raise InvalidRoleError("role must be a non-empty string")
        if len(role) > 200:
            raise InvalidRoleError("role must be ≤ 200 characters")
        if _ROLE_INVALID_RE.search(role):
            raise InvalidRoleError("role contains control characters or markdown table separator")

    @staticmethod
    def _parse(casting_path: Path) -> list[CastEntry]:
        """Parses both legacy 3-col `(role | actor_id | notes)` rows and the
        4-col `(role | actor_id | voice_id | notes)` rows introduced by
        follow-up 115. Column count is taken from the header row so both
        shapes coexist cleanly across the drama set during migration.
        """
        try:
            text = casting_path.read_text(encoding="utf-8")
        except OSError:
            return []
        out: list[CastEntry] = []
        in_table = False
        has_voice_column = False
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped.startswith("|"):
                in_table = False
                continue
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if len(cells) < 3:
                continue
            if cells[0].lower() == "role":
                in_table = True
                has_voice_column = any(c.lower() == "voice_id" for c in cells)
                continue
            if set(cells[0]) <= {"-", ":"}:
                continue
            if not in_table:
                continue
            role = cells[0]
            actor_id = cells[1]
            if has_voice_column:
                voice_id = cells[2] if len(cells) > 2 else ""
                notes = cells[3] if len(cells) > 3 else ""
            else:
                voice_id = ""
                notes = cells[2] if len(cells) > 2 else ""
            if notes == "—":
                notes = ""
            if voice_id == "—":
                voice_id = ""
            if actor_id == "—":
                actor_id = ""
            if not role or (not actor_id and not voice_id):
                continue
            out.append(CastEntry(role=role, actor_id=actor_id, notes=notes, voice_id=voice_id))
        return out

    @staticmethod
    def _write(casting_path: Path, drama_name: str, entries: list[CastEntry]) -> None:
        lines: list[str] = [
            f"# Casting — {drama_name}",
            "",
            "<!-- Managed by ai_video_management webapp (follow-up 014 + 115). "
            "Edit via CastingView. -->",
            "",
            "| role | actor_id | voice_id | notes |",
            "|---|---|---|---|",
        ]
        for entry in entries:
            notes_cell = entry.notes if entry.notes else "—"
            voice_cell = entry.voice_id if entry.voice_id else "—"
            actor_cell = entry.actor_id if entry.actor_id else "—"
            lines.append(f"| {entry.role} | {actor_cell} | {voice_cell} | {notes_cell} |")
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
]
