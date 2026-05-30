"""Voice profile pool: generate + manage AI-voice prompt sidecars.

Follow-up 115: maintains `ai_videos/_voices/voice_NNNN/voice_NNNN.md` (the
canonical Chinese 配音 prompt sidecar) and the optional user-uploaded
`voice_NNNN.{mp3,wav,m4a}` audio sample.

CRITICAL CARVE-OUT — local-only by design. This module composes prompts
locally and writes them to disk; it never speaks to any AI voice service.
The user pastes the generated prompt into an external voice model (their
choice) and drops the rendered audio back here. The carve-out is enforced
by `tests/test_voice_no_outbound_http.py` (grep-fails on httpx / requests /
urllib / literal `https://`).

Mirrors `actor__writer.py` structure where it makes sense (race-safe id
allocation via `mkdir(exist_ok=False)`, reaper for incomplete folders,
sidecar parse/write helpers) but drops every actor-side HTTP / Pillow /
JWT / retry concern.
"""
from __future__ import annotations

import os
import random
import re
import shutil
import subprocess
import tempfile
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

import imageio_ffmpeg

from libs.common.exposed_tree import ExposedTree
from libs.common.safe_resolve import SafeResolver
from libs.domain.errors.voice__error import (
    InvalidVoiceAttributeError,
    InvalidVoiceIdError,
    VoiceAudioExtensionNotAllowedError,
    VoiceAudioExtractFailedError,
    VoiceAudioTooLargeError,
    VoiceAudioUploadFailedError,
    VoiceDeleteFailedError,
    VoiceDeleteTargetExistsError,
    VoiceFfmpegMissingError,
    VoiceGenerationDirMissingError,
    VoiceMp4MissingError,
    VoiceNotFoundError,
)
from libs.domain.value_objects.voice__valueobject import (
    AGE_IMPRESSION_OPTIONS,
    ARCHETYPE_LABELS_ZH,
    ARCHETYPE_OPTIONS,
    AUDIO_EXTENSIONS,
    AUDIO_MAX_BYTES,
    EMOTION_OPTIONS,
    GENDER_OPTIONS,
    PACE_OPTIONS,
    PITCH_REGISTER_OPTIONS,
    VoiceAttrs,
    validate_audio_extension,
    validate_voice_id,
)
from libs.infrastructure.writers.voice__chinese_prompt import build_voice_prompt

VOICES_DIR_NAME: str = "_voices"
_VOICE_DIR_RE = re.compile(r"^voice_(\d{4,})$")
_VOICE_ID_RE = re.compile(r"^voice_\d{4,}$")
_MAX_ID_ALLOC_SCAN: int = 1000
# Reaper deletes md-less folders older than this many seconds. Voice
# composition is sub-millisecond so the window can be tight, but keep it
# at the actor-side default for symmetry.
_REAP_MIN_AGE_SECONDS: float = 300.0
_EXTRACT_FFMPEG_TIMEOUT_S: int = 120
_EXTRACT_MP3_QUALITY: str = "4"  # libmp3lame VBR ~165 kbps — mirrors character_video extractor


@dataclass(frozen=True)
class VoiceInfo:
    id: str
    attrs: VoiceAttrs
    sidecar_path: str
    audio_path: str | None
    mtime: float

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "sidecar_path": self.sidecar_path,
            "audio_path": self.audio_path,
            "mtime": self.mtime,
            **asdict(self.attrs),
            "archetype_label": ARCHETYPE_LABELS_ZH.get(self.attrs.archetype, self.attrs.archetype),
        }


@dataclass
class GenerateResult:
    generated: list[dict[str, object]] = field(default_factory=list)
    errors: list[dict[str, str]] = field(default_factory=list)

    def to_payload(self) -> dict[str, object]:
        return {"generated": list(self.generated), "errors": list(self.errors)}


def _find_audio_file(folder: Path) -> Path | None:
    """Return the first audio sample in the folder, or None.

    The user may drop in `.mp3`, `.wav`, or `.m4a`. Lexicographic first wins
    (stable across reloads). Symlinks are refused.
    """
    try:
        children = sorted(folder.iterdir(), key=lambda p: p.name)
    except OSError:
        return None
    for child in children:
        if not child.is_file() or child.is_symlink():
            continue
        ext = child.suffix.lower()
        if ext in AUDIO_EXTENSIONS:
            return child
    return None


class VoicePool:
    """Implements `VoiceRepository`. Pure-local: no HTTP, no provider env vars."""

    def __init__(self, exposed: ExposedTree, resolver: SafeResolver) -> None:
        self._exposed = exposed
        self._resolver = resolver

    # ------------------------------------------------------------------ paths
    def voices_dir(self) -> Path:
        return self._exposed.root / "ai_videos" / VOICES_DIR_NAME

    def _rel(self, p: Path) -> str:
        try:
            return p.resolve().relative_to(self._resolver.root).as_posix()
        except (OSError, ValueError):
            return p.as_posix()

    # ------------------------------------------------------------------ reads
    def voice_exists(self, voice_id: str) -> bool:
        if not _VOICE_ID_RE.match(voice_id):
            return False
        folder = self.voices_dir() / voice_id
        if not folder.is_dir():
            return False
        sidecar = folder / f"{voice_id}.md"
        return sidecar.is_file()

    def voice_audio_filename(self, voice_id: str) -> str | None:
        if not _VOICE_ID_RE.match(voice_id):
            return None
        folder = self.voices_dir() / voice_id
        if not folder.is_dir():
            return None
        audio = _find_audio_file(folder)
        return audio.name if audio is not None else None

    def list_voices(self) -> list[VoiceInfo]:
        voices_dir = self.voices_dir()
        if not voices_dir.is_dir():
            return []
        out: list[VoiceInfo] = []
        for child in sorted(voices_dir.iterdir(), key=lambda p: p.name):
            if not child.is_dir() or child.is_symlink():
                continue
            if not _VOICE_DIR_RE.match(child.name):
                continue
            voice_id = child.name
            md_path = child / f"{voice_id}.md"
            if not md_path.is_file():
                continue
            attrs = self._parse_sidecar(md_path)
            if attrs is None:
                continue
            try:
                mtime = md_path.stat().st_mtime
            except OSError:
                continue
            audio = _find_audio_file(child)
            out.append(
                VoiceInfo(
                    id=voice_id,
                    attrs=attrs,
                    sidecar_path=self._rel(md_path),
                    audio_path=self._rel(audio) if audio is not None else None,
                    mtime=mtime,
                )
            )
        return out

    # ------------------------------------------------------------------ delete
    def delete_voice(self, voice_id: str) -> dict[str, str]:
        """Soft-delete a voice folder to ai_videos/_deleted/_voices/voice_NNNN/."""
        validate_voice_id(voice_id)
        src = self.voices_dir() / voice_id
        if not src.is_dir() or src.is_symlink():
            raise VoiceNotFoundError(f"voice folder not found: {voice_id}")
        target = self._resolver.root / "ai_videos" / "_deleted" / VOICES_DIR_NAME / voice_id
        if target.exists():
            raise VoiceDeleteTargetExistsError(self._rel(target))
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise VoiceDeleteFailedError(f"mkdir failed: {exc}") from exc
        try:
            src.rename(target)
        except OSError as exc:
            raise VoiceDeleteFailedError(f"rename failed: {exc}") from exc
        return {"from": self._rel(src), "to": self._rel(target)}

    # ------------------------------------------------------------------ audio
    def upload_audio(self, voice_id: str, data: bytes, filename: str) -> dict[str, str]:
        """Write a user-supplied audio sample into the voice folder.

        Replaces any prior sample with the same stem (only one sample per
        voice in v1). Updates the sidecar's `audio_sample` row atomically
        AFTER the audio write so a partial failure leaves a consistent state.
        """
        validate_voice_id(voice_id)
        folder = self.voices_dir() / voice_id
        if not folder.is_dir() or folder.is_symlink():
            raise VoiceNotFoundError(f"voice folder not found: {voice_id}")
        try:
            ext = validate_audio_extension(filename)
        except InvalidVoiceAttributeError as exc:
            raise VoiceAudioExtensionNotAllowedError(str(exc)) from exc
        if not isinstance(data, (bytes, bytearray)):
            raise VoiceAudioUploadFailedError("audio payload must be bytes")
        if len(data) > AUDIO_MAX_BYTES:
            raise VoiceAudioTooLargeError(
                f"audio {len(data)} bytes exceeds cap {AUDIO_MAX_BYTES}"
            )
        # Strip any prior sample (any extension) so only one stays around.
        for prior in folder.iterdir():
            if prior.is_file() and prior.suffix.lower() in AUDIO_EXTENSIONS:
                try:
                    prior.unlink()
                except OSError:
                    pass
        dst = folder / f"{voice_id}{ext}"
        if dst.exists() and dst.is_symlink():
            raise VoiceAudioUploadFailedError(f"target is a symlink: {dst.name}")
        fd, tmp_str = tempfile.mkstemp(prefix=".voice_audio_", suffix=ext + ".tmp", dir=str(folder))
        tmp = Path(tmp_str)
        try:
            with os.fdopen(fd, "wb") as f:
                f.write(bytes(data))
            os.replace(str(tmp), str(dst))
        except OSError as exc:
            try:
                tmp.unlink(missing_ok=True)
            except OSError:
                pass
            raise VoiceAudioUploadFailedError(f"write failed: {exc}") from exc
        # Refresh sidecar audio_sample row.
        self._refresh_audio_row(folder / f"{voice_id}.md", dst.name)
        return {
            "voice_id": voice_id,
            "audio_path": self._rel(dst),
            "byte_size": str(len(data)),
        }

    def extract_audio_from_mp4s(self, voice_id: str) -> dict[str, object]:
        """Extract audio (mp3) from every `*.mp4` in the voice folder.

        Each extraction overwrites `voice_NNNN.mp3` in turn (lexicographic
        order), so the lex-last mp4 wins as the persisted sample. Mirrors
        the existing `upload_audio` contract: any prior `.mp3/.wav/.m4a`
        sample is swept first, and the sidecar `audio_sample` row is
        refreshed after the final write.

        Raises:
          VoiceNotFoundError — voice folder missing.
          VoiceMp4MissingError — no `*.mp4` in the folder.
          VoiceFfmpegMissingError — imageio_ffmpeg cannot find an ffmpeg.
          VoiceAudioExtractFailedError — ffmpeg failed for every mp4.
        """
        validate_voice_id(voice_id)
        folder = self.voices_dir() / voice_id
        if not folder.is_dir() or folder.is_symlink():
            raise VoiceNotFoundError(f"voice folder not found: {voice_id}")
        mp4s = self._list_mp4s(folder)
        if not mp4s:
            raise VoiceMp4MissingError(f"no mp4 in {voice_id}")
        try:
            ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        except Exception as exc:  # imageio_ffmpeg raises various on failure
            raise VoiceFfmpegMissingError(str(exc)) from exc
        for prior in folder.iterdir():
            if prior.is_file() and prior.suffix.lower() in AUDIO_EXTENSIONS:
                try:
                    prior.unlink()
                except OSError:
                    pass
        dst = folder / f"{voice_id}.mp3"
        if dst.exists() and dst.is_symlink():
            raise VoiceAudioExtractFailedError(f"target is a symlink: {dst.name}")
        extracted: list[dict[str, object]] = []
        failures: list[dict[str, str]] = []
        for src in mp4s:
            ok, err, size = self._run_extract_audio(ffmpeg, src, dst)
            if ok:
                extracted.append(
                    {
                        "source": src.name,
                        "mp3_path": self._rel(dst),
                        "byte_size": size,
                    }
                )
            else:
                failures.append({"source": src.name, "error": err})
        if not extracted:
            joined = "; ".join(f"{f['source']}: {f['error']}" for f in failures)
            raise VoiceAudioExtractFailedError(joined or "no audio produced")
        self._refresh_audio_row(folder / f"{voice_id}.md", dst.name)
        return {
            "voice_id": voice_id,
            "audio_path": self._rel(dst),
            "extracted": extracted,
            "failures": failures,
        }

    # ------------------------------------------------------------------ generate
    def generate_batch(
        self,
        attrs: VoiceAttrs,
        count: int,
        seeds: list[int] | None,
        batch_seed: int | None = None,
        batch_size: int | None = None,
        slot_index: int | None = None,
    ) -> GenerateResult:
        """Compose `count` voice prompt sidecars and write them to disk.

        Pure local composition — no network. Each slot allocates its own
        voice_NNNN/ folder via `mkdir(exist_ok=False)` so concurrent worker
        pool requests cannot collide. Per-slot failures land in `errors[]`
        without aborting the batch.
        """
        voices_dir = self.voices_dir()
        try:
            voices_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise VoiceGenerationDirMissingError(str(exc)) from exc
        self._reap_incomplete_folders(voices_dir)
        result = GenerateResult()
        base_seed = batch_seed if batch_seed is not None else int(time.time() * 1000)
        for i in range(count):
            slot_seed = seeds[i] if seeds is not None and i < len(seeds) else base_seed + i
            try:
                voice_id, folder = self._allocate_voice_id(voices_dir)
            except VoiceGenerationDirMissingError as exc:
                result.errors.append({"requested_id": "", "message": f"alloc_failed: {exc}"})
                continue
            try:
                prompt = build_voice_prompt(asdict(attrs), slot_seed)
                sidecar_body = self._build_sidecar(voice_id, attrs, prompt, slot_seed, audio_filename=None)
                sidecar_path = folder / f"{voice_id}.md"
                self._atomic_write_text(sidecar_path, sidecar_body)
                result.generated.append(
                    {
                        "id": voice_id,
                        "sidecar_path": self._rel(sidecar_path),
                        "attrs": asdict(attrs),
                        "seed": slot_seed,
                        "archetype_label": ARCHETYPE_LABELS_ZH.get(
                            attrs.archetype, attrs.archetype
                        ),
                    }
                )
            except OSError as exc:
                result.errors.append({"requested_id": voice_id, "message": f"write_failed: {exc}"})
        return result

    def generate_diverse_batch(
        self,
        gender: str,
        age_impression: str | None,
        count: int,
        notes: str,
    ) -> GenerateResult:
        """Spread `count` voices evenly across the archetype enum."""
        if gender not in GENDER_OPTIONS:
            raise InvalidVoiceAttributeError(f"gender={gender!r} not in schema")
        if age_impression is not None and age_impression not in AGE_IMPRESSION_OPTIONS:
            raise InvalidVoiceAttributeError(f"age_impression={age_impression!r} not in schema")
        voices_dir = self.voices_dir()
        try:
            voices_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise VoiceGenerationDirMissingError(str(exc)) from exc
        self._reap_incomplete_folders(voices_dir)
        result = GenerateResult()
        plan = self._distribute_archetypes(count)
        for slot_index, archetype in enumerate(plan):
            attrs = VoiceAttrs(
                archetype=archetype,
                gender=gender,
                age_impression=age_impression or _archetype_default_age(archetype),
                notes=notes,
            )
            slot_seed = int(time.time() * 1000) + slot_index
            try:
                voice_id, folder = self._allocate_voice_id(voices_dir)
            except VoiceGenerationDirMissingError as exc:
                result.errors.append({"requested_id": "", "message": f"alloc_failed: {exc}"})
                continue
            try:
                prompt = build_voice_prompt(asdict(attrs), slot_seed)
                sidecar_body = self._build_sidecar(voice_id, attrs, prompt, slot_seed, audio_filename=None)
                sidecar_path = folder / f"{voice_id}.md"
                self._atomic_write_text(sidecar_path, sidecar_body)
                result.generated.append(
                    {
                        "id": voice_id,
                        "sidecar_path": self._rel(sidecar_path),
                        "attrs": asdict(attrs),
                        "seed": slot_seed,
                        "archetype": archetype,
                        "archetype_label": ARCHETYPE_LABELS_ZH.get(archetype, archetype),
                    }
                )
            except OSError as exc:
                result.errors.append({"requested_id": voice_id, "message": f"write_failed: {exc}"})
        return result

    # ------------------------------------------------------------------ preview
    def preview_prompts(
        self,
        attrs: VoiceAttrs,
        count: int,
        seeds: list[int] | None = None,
        batch_seed: int | None = None,
        batch_size: int | None = None,
        slot_index: int | None = None,
    ) -> dict[str, object]:
        base_seed = batch_seed if batch_seed is not None else int(time.time() * 1000)
        prompts: list[dict[str, object]] = []
        for i in range(count):
            slot_seed = seeds[i] if seeds is not None and i < len(seeds) else base_seed + i
            prompts.append(
                {
                    "seed": slot_seed,
                    "prompt": build_voice_prompt(asdict(attrs), slot_seed),
                    "archetype": attrs.archetype,
                    "archetype_label": ARCHETYPE_LABELS_ZH.get(
                        attrs.archetype, attrs.archetype
                    ),
                    "attrs": asdict(attrs),
                }
            )
        return {"prompts": prompts}

    def preview_diverse_prompts(
        self,
        gender: str,
        age_impression: str | None,
        count: int,
        notes: str,
    ) -> dict[str, object]:
        if gender not in GENDER_OPTIONS:
            raise InvalidVoiceAttributeError(f"gender={gender!r} not in schema")
        if age_impression is not None and age_impression not in AGE_IMPRESSION_OPTIONS:
            raise InvalidVoiceAttributeError(f"age_impression={age_impression!r} not in schema")
        plan = self._distribute_archetypes(count)
        prompts: list[dict[str, object]] = []
        base_seed = int(time.time() * 1000)
        for slot_index, archetype in enumerate(plan):
            attrs = VoiceAttrs(
                archetype=archetype,
                gender=gender,
                age_impression=age_impression or _archetype_default_age(archetype),
                notes=notes,
            )
            seed = base_seed + slot_index
            prompts.append(
                {
                    "seed": seed,
                    "prompt": build_voice_prompt(asdict(attrs), seed),
                    "archetype": archetype,
                    "archetype_label": ARCHETYPE_LABELS_ZH.get(archetype, archetype),
                    "attrs": asdict(attrs),
                }
            )
        return {"prompts": prompts}

    # ------------------------------------------------------------------ helpers
    def _allocate_voice_id(self, voices_dir: Path) -> tuple[str, Path]:
        """Race-safe id allocation via mkdir(exist_ok=False)."""
        start = self._next_voice_id_num(voices_dir)
        candidate = start
        attempts = 0
        while attempts < _MAX_ID_ALLOC_SCAN:
            voice_id = f"voice_{candidate:04d}"
            folder = voices_dir / voice_id
            try:
                folder.mkdir(parents=True, exist_ok=False)
                return voice_id, folder
            except FileExistsError:
                candidate += 1
                attempts += 1
                continue
            except OSError as exc:
                raise VoiceGenerationDirMissingError(str(exc)) from exc
        raise VoiceGenerationDirMissingError(
            f"exhausted {_MAX_ID_ALLOC_SCAN} id-allocation attempts starting from voice_{start:04d}"
        )

    @staticmethod
    def _next_voice_id_num(voices_dir: Path) -> int:
        max_num = 0
        try:
            entries = list(voices_dir.iterdir())
        except OSError:
            return 1
        for entry in entries:
            if not entry.is_dir():
                continue
            m = _VOICE_DIR_RE.match(entry.name)
            if not m:
                continue
            n = int(m.group(1))
            if n > max_num:
                max_num = n
        return max_num + 1

    @staticmethod
    def _reap_incomplete_folders(voices_dir: Path) -> None:
        """Drop voice_NNNN folders left behind by killed batches (no md sidecar)."""
        try:
            entries = list(voices_dir.iterdir())
        except OSError:
            return
        cutoff = time.time() - _REAP_MIN_AGE_SECONDS
        for entry in entries:
            if not entry.is_dir():
                continue
            if not _VOICE_DIR_RE.match(entry.name):
                continue
            sidecar = entry / f"{entry.name}.md"
            if sidecar.is_file():
                continue
            try:
                if entry.stat().st_mtime > cutoff:
                    continue  # in-flight — skip
            except OSError:
                continue
            try:
                for child in entry.iterdir():
                    try:
                        child.unlink()
                    except OSError:
                        pass
                entry.rmdir()
            except OSError:
                pass

    @staticmethod
    def _distribute_archetypes(count: int) -> tuple[str, ...]:
        """Round-robin spread across the archetype set in a stable order."""
        ordered = sorted(ARCHETYPE_OPTIONS)
        out: list[str] = []
        for i in range(count):
            out.append(ordered[i % len(ordered)])
        return tuple(out)

    @staticmethod
    def _atomic_write_text(path: Path, body: str) -> None:
        parent = path.parent
        parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_str = tempfile.mkstemp(prefix=".voice_", suffix=".md.tmp", dir=str(parent))
        tmp = Path(tmp_str)
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
                f.write(body)
            os.replace(str(tmp), str(path))
        except OSError:
            try:
                tmp.unlink(missing_ok=True)
            except OSError:
                pass
            raise

    @staticmethod
    def _build_sidecar(
        voice_id: str,
        attrs: VoiceAttrs,
        prompt: str,
        seed: int,
        audio_filename: str | None,
    ) -> str:
        tone_display = attrs.tone if attrs.tone else "—"
        sig_display = attrs.signature_inflection if attrs.signature_inflection else "—"
        notes_display = attrs.notes if attrs.notes else "—"
        audio_display = audio_filename if audio_filename else "—"
        archetype_label = ARCHETYPE_LABELS_ZH.get(attrs.archetype, attrs.archetype)
        return (
            f"# {voice_id}\n"
            f"\n"
            f"AI-generated 配音 prompt for character voice casting (local "
            f"composition; paste into any external AI voice model — follow-up 115).\n"
            f"\n"
            f"| 字段 | 值 |\n"
            f"|---|---|\n"
            f"| archetype | {attrs.archetype} |\n"
            f"| archetype_label | {archetype_label} |\n"
            f"| gender | {attrs.gender} |\n"
            f"| age_impression | {attrs.age_impression} |\n"
            f"| pace | {attrs.pace} |\n"
            f"| pitch_register | {attrs.pitch_register} |\n"
            f"| emotion_default | {attrs.emotion_default} |\n"
            f"| tone | {tone_display} |\n"
            f"| signature_inflection | {sig_display} |\n"
            f"| notes | {notes_display} |\n"
            f"| seed | {seed} |\n"
            f"| audio_sample | {audio_display} |\n"
            f"\n"
            f"## 生成 prompt (配音)\n"
            f"\n"
            f"```\n"
            f"{prompt}\n"
            f"```\n"
        )

    @staticmethod
    def _parse_sidecar(md_path: Path) -> VoiceAttrs | None:
        try:
            text = md_path.read_text(encoding="utf-8")
        except OSError:
            return None
        fields: dict[str, str] = {}
        for line in text.splitlines():
            line = line.strip()
            if not line.startswith("|"):
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) != 2:
                continue
            key, value = cells[0], cells[1]
            if key in {"字段", "---"} or set(key) <= {"-", ":"}:
                continue
            fields[key] = value
        required = ("archetype", "gender", "age_impression")
        if not all(f in fields for f in required):
            return None
        try:
            return VoiceAttrs(
                archetype=fields["archetype"],
                gender=fields["gender"],
                age_impression=fields["age_impression"],
                pace=fields.get("pace", "medium"),
                pitch_register=fields.get("pitch_register", "mid"),
                emotion_default=fields.get("emotion_default", "calm"),
                tone=fields.get("tone", "") if fields.get("tone", "—") != "—" else "",
                signature_inflection=fields.get("signature_inflection", "") if fields.get("signature_inflection", "—") != "—" else "",
                notes=fields.get("notes", "") if fields.get("notes", "—") != "—" else "",
            )
        except InvalidVoiceAttributeError:
            return None

    @staticmethod
    def _list_mp4s(folder: Path) -> list[Path]:
        try:
            children = sorted(folder.iterdir(), key=lambda p: p.name)
        except OSError:
            return []
        return [
            c for c in children
            if c.is_file() and not c.is_symlink() and c.suffix.lower() == ".mp4"
        ]

    @staticmethod
    def _run_extract_audio(
        ffmpeg: str, src: Path, out_path: Path
    ) -> tuple[bool, str, int]:
        cmd = [
            ffmpeg,
            "-y",
            "-i", str(src),
            "-vn",
            "-c:a", "libmp3lame",
            "-q:a", _EXTRACT_MP3_QUALITY,
            "-loglevel", "error",
            str(out_path),
        ]
        try:
            completed = subprocess.run(
                cmd,
                capture_output=True,
                timeout=_EXTRACT_FFMPEG_TIMEOUT_S,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return False, "ffmpeg_timeout", 0
        if completed.returncode != 0 or not out_path.is_file():
            err = completed.stderr.decode("utf-8", errors="replace").strip()[:200]
            return False, err or "ffmpeg_failed", 0
        try:
            size = out_path.stat().st_size
        except OSError:
            size = 0
        return True, "", size

    def _refresh_audio_row(self, md_path: Path, audio_filename: str) -> None:
        """Atomically rewrite the `| audio_sample | ... |` row of the sidecar."""
        try:
            text = md_path.read_text(encoding="utf-8")
        except OSError:
            return
        lines = text.split("\n")
        replaced = False
        for idx, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("| audio_sample |"):
                lines[idx] = f"| audio_sample | {audio_filename} |"
                replaced = True
                break
        if not replaced:
            return
        try:
            self._atomic_write_text(md_path, "\n".join(lines))
        except OSError:
            pass


_ARCHETYPE_DEFAULT_AGE: dict[str, str] = {
    "effeminate_eunuch": "middle_aged",
    "mighty_general": "middle_aged",
    "gentle_palace_mistress": "young_adult",
    "aged_master": "elderly",
    "young_jianghu_swordsman": "young_adult",
    "noble_emperor": "middle_aged",
    "cold_assassin": "young_adult",
    "coquettish_concubine": "young_adult",
    "wise_elder_monk": "elderly",
    "cunning_advisor": "middle_aged",
}


def _archetype_default_age(archetype: str) -> str:
    return _ARCHETYPE_DEFAULT_AGE.get(archetype, "young_adult")
