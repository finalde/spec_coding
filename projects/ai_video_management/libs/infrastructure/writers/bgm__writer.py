"""Background-music pool: generate + manage AI-generated BGM tracks.

Maintains `ai_videos/_bgm/{category}/bgm_NNNN/{bgm_NNNN.md, bgm_NNNN.mp3}`.
The `{category}/` folder layer is the one structural divergence from the
flat actor / voice libraries: the `bgm_NNNN` id is still GLOBALLY unique
(unique across categories, so a drama references a track by bare id like an
actor), which means id allocation scans EVERY category for the max number.

Generation backend: self-hosted Stable Audio (open weights, Stability AI
Community License — commercial-safe). The torch / GPU dependency lives
entirely in `tools/stableaudio_gen.py`; this module shells out to it via
subprocess (arg list, never shell=True), so the webapp process never imports
torch. A track is "complete" only when both its `.md` sidecar and `.mp3`
audio exist; a folder left without an mp3 is reaped.

Mirrors `voice__writer.py` structure (race-safe mkdir id allocation, reaper,
atomic sidecar writes, soft-delete to `_deleted/`) and `actor__command`'s
assignment-guarded delete (the reference check lives in the application
layer, scanning `bgm.md` instead of `casting.md`).
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

from libs.common.exposed_tree import ExposedTree
from libs.common.safe_resolve import SafeResolver
from libs.domain.errors.bgm__error import (
    BgmDeleteFailedError,
    BgmDeleteTargetExistsError,
    BgmGenerationDirMissingError,
    BgmNotFoundError,
    BgmSidecarUnreadableError,
    StableAudioFailedError,
    StableAudioMissingError,
)
from libs.domain.value_objects.bgm__valueobject import (
    CATEGORY_LABELS_ZH,
    CATEGORY_OPTIONS,
    DEFAULT_GENERATOR,
    DEFAULT_LICENSE,
    DEFAULT_MODEL,
    BgmAttrs,
    validate_bgm_id,
    validate_category,
)
from libs.infrastructure.writers.bgm__prompt import build_bgm_prompt, build_bgm_prompt_keyed

BGM_DIR_NAME: str = "_bgm"
_BGM_DIR_RE = re.compile(r"^bgm_(\d{4,})$")
_BGM_ID_RE = re.compile(r"^bgm_\d{4,}$")
_MAX_ID_ALLOC_SCAN: int = 1000
# Reaper deletes mp3-less folders older than this. Stable Audio GPU
# generation of a 30s clip is seconds-to-tens-of-seconds, but the duration
# is user-controlled and uncapped (stage-5 sign-off), so keep a generous
# window past worst-case in-flight generation.
_REAP_MIN_AGE_SECONDS: float = 1800.0

_GEN_SCRIPT_REL: tuple[str, ...] = ("tools", "stableaudio_gen.py")
# Generous ceiling — Stable Audio on GPU is fast, but duration is uncapped.
_GEN_TIMEOUT_S: int = 1800
# The interpreter that has torch + stable-audio-tools installed. Defaults to
# the webapp's own interpreter for `--dry-run` / CI; production points it at
# the tool's dedicated venv via env so torch stays out of the webapp env.
_BGM_PYTHON_ENV: str = "BGM_PYTHON"


def _fenced_block_under_header(text: str, header_token: str) -> str | None:
    """Return the first fenced code block that appears under a markdown header
    (`## …`) whose text contains `header_token`. None if no such header / fence.
    Used to read back the 英文 (model) prompt independently of block order."""
    lines = text.splitlines()
    in_section = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("#"):
            in_section = header_token in stripped
            continue
        if in_section and stripped.startswith("```"):
            body: list[str] = []
            for nxt in lines[i + 1:]:
                if nxt.strip().startswith("```"):
                    return "\n".join(body).strip()
                body.append(nxt)
            return "\n".join(body).strip()
    return None


@dataclass(frozen=True)
class BgmInfo:
    id: str
    category: str
    attrs: BgmAttrs
    sidecar_path: str
    audio_path: str | None
    seed: int
    mtime: float

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "category": self.category,
            "category_label": CATEGORY_LABELS_ZH.get(self.category, self.category),
            "sidecar_path": self.sidecar_path,
            "audio_path": self.audio_path,
            "seed": self.seed,
            "mtime": self.mtime,
            **asdict(self.attrs),
        }


@dataclass
class GenerateResult:
    generated: list[dict[str, object]] = field(default_factory=list)
    errors: list[dict[str, str]] = field(default_factory=list)

    def to_payload(self) -> dict[str, object]:
        return {"generated": list(self.generated), "errors": list(self.errors)}


def _find_mp3(folder: Path) -> Path | None:
    try:
        children = sorted(folder.iterdir(), key=lambda p: p.name)
    except OSError:
        return None
    for child in children:
        if child.is_file() and not child.is_symlink() and child.suffix.lower() == ".mp3":
            return child
    return None


class BgmPool:
    """Implements `BgmRepository`. Generation shells out to a self-hosted
    Stable Audio tool; the webapp process never imports torch."""

    def __init__(self, exposed: ExposedTree, resolver: SafeResolver) -> None:
        self._exposed = exposed
        self._resolver = resolver

    # ------------------------------------------------------------------ paths
    def bgm_dir(self) -> Path:
        return self._exposed.root / "ai_videos" / BGM_DIR_NAME

    def _category_dir(self, category: str) -> Path:
        return self.bgm_dir() / category

    def _rel(self, p: Path) -> str:
        try:
            return p.resolve().relative_to(self._resolver.root).as_posix()
        except (OSError, ValueError):
            return p.as_posix()

    def _find_bgm_folder(self, bgm_id: str) -> Path | None:
        """Locate `bgm_NNNN`'s folder across every category. Returns None if
        no live folder holds that id."""
        if not _BGM_ID_RE.match(bgm_id):
            return None
        root = self.bgm_dir()
        if not root.is_dir():
            return None
        for cat_dir in root.iterdir():
            if not cat_dir.is_dir() or cat_dir.is_symlink():
                continue
            if cat_dir.name not in CATEGORY_OPTIONS:
                continue
            folder = cat_dir / bgm_id
            if folder.is_dir() and not folder.is_symlink():
                return folder
        return None

    # ------------------------------------------------------------------ reads
    def bgm_exists(self, bgm_id: str) -> bool:
        folder = self._find_bgm_folder(bgm_id)
        if folder is None:
            return False
        return _find_mp3(folder) is not None

    def bgm_audio_filename(self, bgm_id: str) -> str | None:
        folder = self._find_bgm_folder(bgm_id)
        if folder is None:
            return None
        mp3 = _find_mp3(folder)
        return mp3.name if mp3 is not None else None

    def audio_path_for(self, bgm_id: str) -> Path | None:
        """Absolute path to `bgm_NNNN`'s rendered mp3 across any category, or
        None if the track folder / mp3 is absent. Used by the episode BGM
        muxer to resolve an assigned cue id to its audio file."""
        folder = self._find_bgm_folder(bgm_id)
        if folder is None:
            return None
        return _find_mp3(folder)

    def list_bgms(self) -> list[BgmInfo]:
        root = self.bgm_dir()
        if not root.is_dir():
            return []
        out: list[BgmInfo] = []
        for cat_dir in sorted(root.iterdir(), key=lambda p: p.name):
            if not cat_dir.is_dir() or cat_dir.is_symlink():
                continue
            category = cat_dir.name
            if category not in CATEGORY_OPTIONS:
                continue
            for child in sorted(cat_dir.iterdir(), key=lambda p: p.name):
                if not child.is_dir() or child.is_symlink():
                    continue
                if not _BGM_DIR_RE.match(child.name):
                    continue
                bgm_id = child.name
                md_path = child / f"{bgm_id}.md"
                if not md_path.is_file():
                    continue
                parsed = self._parse_sidecar(md_path)
                if parsed is None:
                    continue
                attrs, seed = parsed
                try:
                    mtime = md_path.stat().st_mtime
                except OSError:
                    continue
                mp3 = _find_mp3(child)
                out.append(
                    BgmInfo(
                        id=bgm_id,
                        category=category,
                        attrs=attrs,
                        sidecar_path=self._rel(md_path),
                        audio_path=self._rel(mp3) if mp3 is not None else None,
                        seed=seed,
                        mtime=mtime,
                    )
                )
        return out

    # ------------------------------------------------------------------ delete
    def delete_bgm(self, bgm_id: str) -> dict[str, str]:
        """Soft-delete a track folder to
        `ai_videos/_deleted/_bgm/{category}/bgm_NNNN/`. The caller (application
        layer) refuses the delete first if any drama's bgm.md still references
        the id, so a live cue never dangles."""
        validate_bgm_id(bgm_id)
        src = self._find_bgm_folder(bgm_id)
        if src is None:
            raise BgmNotFoundError(f"bgm folder not found: {bgm_id}")
        category = src.parent.name
        target = (
            self._resolver.root / "ai_videos" / "_deleted" / BGM_DIR_NAME / category / bgm_id
        )
        if target.exists():
            raise BgmDeleteTargetExistsError(self._rel(target))
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise BgmDeleteFailedError(f"mkdir failed: {exc}") from exc
        try:
            src.rename(target)
        except OSError as exc:
            raise BgmDeleteFailedError(f"rename failed: {exc}") from exc
        return {"from": self._rel(src), "to": self._rel(target)}

    # ------------------------------------------------------------------ generate
    def generate_batch(
        self,
        attrs: BgmAttrs,
        count: int,
        seeds: list[int] | None,
        batch_seed: int | None = None,
        batch_size: int | None = None,
        slot_index: int | None = None,
    ) -> GenerateResult:
        """Generate `count` tracks in `attrs.category` via the Stable Audio
        subprocess. Each slot allocates its own globally-unique `bgm_NNNN/`
        folder, runs generation to an mp3, then writes the sidecar — so a
        failed generation never leaves an mp3-less orphan (the folder is
        removed). Per-slot failures land in `errors[]` without aborting the
        batch. A missing tool / interpreter aborts the whole batch (it would
        fail identically for every slot)."""
        validate_category(attrs.category)
        bgm_root = self.bgm_dir()
        cat_dir = self._category_dir(attrs.category)
        try:
            cat_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise BgmGenerationDirMissingError(str(exc)) from exc
        self._reap_incomplete_folders(bgm_root)
        script = self._gen_script_path()  # raises StableAudioMissingError if absent
        python_exe = self._gen_python_exe()
        result = GenerateResult()
        base_seed = batch_seed if batch_seed is not None else int(time.time() * 1000)
        for i in range(count):
            slot_seed = seeds[i] if seeds is not None and i < len(seeds) else base_seed + i
            try:
                bgm_id, folder = self._allocate_bgm_id(attrs.category)
            except BgmGenerationDirMissingError as exc:
                result.errors.append({"requested_id": "", "message": f"alloc_failed: {exc}"})
                continue
            attrs_d = asdict(attrs)
            prompt_model = build_bgm_prompt(attrs_d, slot_seed)
            prompt_keyed = build_bgm_prompt_keyed(attrs_d, slot_seed, bgm_id)
            out_mp3 = folder / f"{bgm_id}.mp3"
            ok, err = self._run_stableaudio(
                python_exe, script, prompt_model, slot_seed, attrs.duration, out_mp3
            )
            if not ok:
                shutil.rmtree(folder, ignore_errors=True)
                result.errors.append({"requested_id": bgm_id, "message": f"generate_failed: {err}"})
                continue
            try:
                sidecar_body = self._build_sidecar(
                    bgm_id, attrs, prompt_keyed, slot_seed, out_mp3.name
                )
                sidecar_path = folder / f"{bgm_id}.md"
                self._atomic_write_text(sidecar_path, sidecar_body)
            except OSError as exc:
                shutil.rmtree(folder, ignore_errors=True)
                result.errors.append({"requested_id": bgm_id, "message": f"write_failed: {exc}"})
                continue
            result.generated.append(
                {
                    "id": bgm_id,
                    "category": attrs.category,
                    "category_label": CATEGORY_LABELS_ZH.get(attrs.category, attrs.category),
                    "sidecar_path": self._rel(sidecar_path),
                    "audio_path": self._rel(out_mp3),
                    "attrs": asdict(attrs),
                    "seed": slot_seed,
                }
            )
        return result

    # --------------------------------------------------- prompt-only (step 1)
    def create_prompts_batch(
        self,
        attrs: BgmAttrs,
        count: int,
        seeds: list[int] | None,
        batch_seed: int | None = None,
        batch_size: int | None = None,
        slot_index: int | None = None,
    ) -> GenerateResult:
        """Two-step flow, step 1: allocate `count` track folders and write each
        sidecar (carrying the resolved prompt + seed) WITHOUT any audio
        generation. The user then renders each track's audio externally
        (ElevenLabs) and bulk-imports the downloads via the global Downloads
        importer (`DownloadsImporter.import_bgms`), or generates locally on GPU
        (`generate_audio`). Mirrors `generate_batch` minus the subprocess; each
        result entry is flagged `pending_audio: True` with `audio_path: None`."""
        validate_category(attrs.category)
        bgm_root = self.bgm_dir()
        cat_dir = self._category_dir(attrs.category)
        try:
            cat_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise BgmGenerationDirMissingError(str(exc)) from exc
        self._reap_incomplete_folders(bgm_root)
        result = GenerateResult()
        base_seed = batch_seed if batch_seed is not None else int(time.time() * 1000)
        for i in range(count):
            slot_seed = seeds[i] if seeds is not None and i < len(seeds) else base_seed + i
            try:
                bgm_id, folder = self._allocate_bgm_id(attrs.category)
            except BgmGenerationDirMissingError as exc:
                result.errors.append({"requested_id": "", "message": f"alloc_failed: {exc}"})
                continue
            attrs_d = asdict(attrs)
            prompt_keyed = build_bgm_prompt_keyed(attrs_d, slot_seed, bgm_id)
            try:
                sidecar_body = self._build_sidecar(
                    bgm_id, attrs, prompt_keyed, slot_seed, ""
                )
                sidecar_path = folder / f"{bgm_id}.md"
                self._atomic_write_text(sidecar_path, sidecar_body)
            except OSError as exc:
                shutil.rmtree(folder, ignore_errors=True)
                result.errors.append({"requested_id": bgm_id, "message": f"write_failed: {exc}"})
                continue
            result.generated.append(
                {
                    "id": bgm_id,
                    "category": attrs.category,
                    "category_label": CATEGORY_LABELS_ZH.get(attrs.category, attrs.category),
                    "sidecar_path": self._rel(sidecar_path),
                    "audio_path": None,
                    "pending_audio": True,
                    "prompt": prompt_keyed,
                    "attrs": asdict(attrs),
                    "seed": slot_seed,
                }
            )
        return result

    # ------------------------------------------- per-track audio (step 2)
    def generate_audio(self, bgm_id: str) -> dict[str, object]:
        """Two-step flow, step 2a: render audio for an EXISTING prompt-only
        track locally via the Stable Audio GPU subprocess. Reads the prompt /
        seed / duration back from the track's sidecar, writes `bgm_NNNN.mp3`
        into its folder (overwriting any prior render)."""
        validate_bgm_id(bgm_id)
        folder = self._find_bgm_folder(bgm_id)
        if folder is None:
            raise BgmNotFoundError(f"bgm folder not found: {bgm_id}")
        prompt, seed, duration = self._read_sidecar_generation(folder / f"{bgm_id}.md")
        script = self._gen_script_path()
        python_exe = self._gen_python_exe()
        out_mp3 = folder / f"{bgm_id}.mp3"
        ok, err = self._run_stableaudio(python_exe, script, prompt, seed, duration, out_mp3)
        if not ok:
            raise StableAudioFailedError(err)
        return {"id": bgm_id, "audio_path": self._rel(out_mp3)}

    # ------------------------------------------------------------------ preview
    def preview_prompts(
        self,
        attrs: BgmAttrs,
        count: int,
        seeds: list[int] | None = None,
        batch_seed: int | None = None,
        batch_size: int | None = None,
        slot_index: int | None = None,
    ) -> dict[str, object]:
        validate_category(attrs.category)
        base_seed = batch_seed if batch_seed is not None else int(time.time() * 1000)
        prompts: list[dict[str, object]] = []
        for i in range(count):
            slot_seed = seeds[i] if seeds is not None and i < len(seeds) else base_seed + i
            attrs_d = asdict(attrs)
            prompts.append(
                {
                    "seed": slot_seed,
                    "prompt": build_bgm_prompt(attrs_d, slot_seed),
                    "category": attrs.category,
                    "category_label": CATEGORY_LABELS_ZH.get(attrs.category, attrs.category),
                    "attrs": attrs_d,
                }
            )
        return {"prompts": prompts}

    # ------------------------------------------------------------------ helpers
    def _gen_script_path(self) -> Path:
        script = self._resolver.root.joinpath(*_GEN_SCRIPT_REL)
        if not script.is_file():
            raise StableAudioMissingError(f"generation tool not found: {self._rel(script)}")
        return script

    @staticmethod
    def _gen_python_exe() -> str:
        return os.environ.get(_BGM_PYTHON_ENV) or sys.executable

    @staticmethod
    def _read_sidecar_generation(md_path: Path) -> tuple[str, int, int]:
        """Read back (prompt, seed, duration) a prompt-only sidecar carries, so
        local audio generation reproduces exactly what step 1 resolved."""
        parsed = BgmPool._parse_sidecar(md_path)
        if parsed is None:
            raise BgmSidecarUnreadableError(f"cannot parse sidecar: {md_path.name}")
        attrs, seed = parsed
        try:
            text = md_path.read_text(encoding="utf-8")
        except OSError as exc:
            raise BgmSidecarUnreadableError(str(exc)) from exc
        # Prefer the fenced block under the 英文 header; fall back to the first
        # fence (legacy sidecars).
        prompt = _fenced_block_under_header(text, "英文") or ""
        if not prompt:
            m = re.search(r"```[\w-]*\n(.*?)```", text, re.DOTALL)
            prompt = m.group(1).strip() if m is not None else ""
        if not prompt:
            raise BgmSidecarUnreadableError(f"no 生成 prompt block in {md_path.name}")
        # Drop the leading `bgm_NNNN` KEY line (a copy/import routing token, not
        # part of the music description) before handing the prompt to the model.
        prompt = re.sub(r"^\s*bgm_\d{4,}\s*\n", "", prompt, count=1)
        return prompt.strip(), seed, attrs.duration

    def _run_stableaudio(
        self,
        python_exe: str,
        script: Path,
        prompt: str,
        seed: int,
        duration: int,
        out_mp3: Path,
    ) -> tuple[bool, str]:
        """Run the Stable Audio generation subprocess as an arg list (never
        shell=True — the prompt is user-influenced text). Returns (ok, error).
        """
        cmd = [
            python_exe,
            str(script),
            "--prompt", prompt,
            "--seed", str(seed),
            "--duration", str(duration),
            "--model", DEFAULT_MODEL,
            "--out", str(out_mp3),
        ]
        try:
            completed = subprocess.run(
                cmd,
                capture_output=True,
                timeout=_GEN_TIMEOUT_S,
                check=False,
            )
        except FileNotFoundError as exc:
            raise StableAudioMissingError(f"interpreter not found: {exc}") from exc
        except subprocess.TimeoutExpired:
            return False, "stableaudio_timeout"
        if completed.returncode != 0 or not out_mp3.is_file():
            raw = completed.stderr.decode("utf-8", errors="replace").strip()
            # Surface the TAIL of stderr: a Python traceback's final line is the
            # actual exception (e.g. `ModuleNotFoundError: No module named
            # 'torchaudio'`). Slicing the first 300 chars showed only the
            # uninformative traceback header and hid the real cause.
            lines = [ln for ln in raw.splitlines() if ln.strip()]
            err = lines[-1].strip()[:300] if lines else ""
            return False, err or "stableaudio_failed"
        return True, ""

    def _allocate_bgm_id(self, category: str) -> tuple[str, Path]:
        """Race-safe global id allocation: the next free `bgm_NNNN` (max over
        ALL categories + 1) claimed via mkdir(exist_ok=False) inside the
        target category. Walks forward on collision so concurrent requests
        across categories never reuse a number."""
        cat_dir = self._category_dir(category)
        candidate = self._next_bgm_id_num()
        attempts = 0
        while attempts < _MAX_ID_ALLOC_SCAN:
            bgm_id = f"bgm_{candidate:04d}"
            folder = cat_dir / bgm_id
            try:
                folder.mkdir(parents=True, exist_ok=False)
                return bgm_id, folder
            except FileExistsError:
                candidate += 1
                attempts += 1
                continue
            except OSError as exc:
                raise BgmGenerationDirMissingError(str(exc)) from exc
        raise BgmGenerationDirMissingError(
            f"exhausted {_MAX_ID_ALLOC_SCAN} id-allocation attempts starting from bgm_{candidate:04d}"
        )

    def _deleted_bgm_dir(self) -> Path:
        return self._resolver.root / "ai_videos" / "_deleted" / BGM_DIR_NAME

    @staticmethod
    def _max_bgm_num_under(root: Path) -> int:
        """Highest `bgm_NNNN` number under any category folder of `root` (0 if
        none). A folder counts as occupied regardless of mp3 presence."""
        max_num = 0
        try:
            cat_dirs = list(root.iterdir())
        except OSError:
            return 0
        for cat_dir in cat_dirs:
            if not cat_dir.is_dir() or cat_dir.is_symlink():
                continue
            if cat_dir.name not in CATEGORY_OPTIONS:
                continue
            try:
                entries = list(cat_dir.iterdir())
            except OSError:
                continue
            for entry in entries:
                if not entry.is_dir():
                    continue
                m = _BGM_DIR_RE.match(entry.name)
                if not m:
                    continue
                n = int(m.group(1))
                if n > max_num:
                    max_num = n
        return max_num

    def _next_bgm_id_num(self) -> int:
        """max+1 across every `bgm_NNNN` folder in EVERY category — counting both
        the LIVE library AND the `_deleted/_bgm` recycle bin, so a soft-deleted
        track's number is never reused. Reuse would silently rebind any drama's
        `bgm.md` cue that still references the retired id to a different track."""
        live = self._max_bgm_num_under(self.bgm_dir())
        retired = self._max_bgm_num_under(self._deleted_bgm_dir())
        return max(live, retired) + 1

    @staticmethod
    def _reap_incomplete_folders(bgm_root: Path) -> None:
        """Drop `bgm_NNNN` folders (in any category) that have NEITHER a sidecar
        NOR an mp3 and are older than the threshold — true leftovers from a
        crash between mkdir and the first write. A prompt-only track (sidecar
        present, audio pending) is intentional and MUST survive; folders younger
        than the threshold are likely a concurrent in-flight slot."""
        try:
            cat_dirs = list(bgm_root.iterdir())
        except OSError:
            return
        cutoff = time.time() - _REAP_MIN_AGE_SECONDS
        for cat_dir in cat_dirs:
            if not cat_dir.is_dir() or cat_dir.is_symlink():
                continue
            if cat_dir.name not in CATEGORY_OPTIONS:
                continue
            try:
                entries = list(cat_dir.iterdir())
            except OSError:
                continue
            for entry in entries:
                if not entry.is_dir():
                    continue
                if not _BGM_DIR_RE.match(entry.name):
                    continue
                if _find_mp3(entry) is not None:
                    continue
                if (entry / f"{entry.name}.md").is_file():
                    continue  # prompt-only track — audio intentionally pending
                try:
                    if entry.stat().st_mtime > cutoff:
                        continue
                except OSError:
                    continue
                shutil.rmtree(entry, ignore_errors=True)

    @staticmethod
    def _atomic_write_text(path: Path, body: str) -> None:
        parent = path.parent
        parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_str = tempfile.mkstemp(prefix=".bgm_", suffix=".md.tmp", dir=str(parent))
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
        bgm_id: str,
        attrs: BgmAttrs,
        prompt: str,
        seed: int,
        audio_filename: str,
    ) -> str:
        mood_display = attrs.mood if attrs.mood else "—"
        instruments_display = attrs.instruments if attrs.instruments else "—"
        notes_display = attrs.notes if attrs.notes else "—"
        category_label = CATEGORY_LABELS_ZH.get(attrs.category, attrs.category)
        # Single English prompt block (follow-up 2026-06-21): `prompt` carries a
        # leading `bgm_NNNN` KEY line then the music description. Copied into
        # ElevenLabs; the local read-back strips the key line before the model.
        return (
            f"# {bgm_id}\n"
            f"\n"
            f"AI-generated background-music track. "
            f"全局唯一 id，可被任意剧的 bgm.md 按 `{bgm_id}` 引用。\n"
            f"\n"
            f"| 字段 | 值 |\n"
            f"|---|---|\n"
            f"| category | {attrs.category} |\n"
            f"| category_label | {category_label} |\n"
            f"| mood | {mood_display} |\n"
            f"| bpm | {attrs.bpm} |\n"
            f"| duration | {attrs.duration} |\n"
            f"| loopable | {'true' if attrs.loopable else 'false'} |\n"
            f"| intensity | {attrs.intensity} |\n"
            f"| instruments | {instruments_display} |\n"
            f"| generator | {DEFAULT_GENERATOR} |\n"
            f"| model | {DEFAULT_MODEL} |\n"
            f"| seed | {seed} |\n"
            f"| license | {DEFAULT_LICENSE} |\n"
            f"| notes | {notes_display} |\n"
            f"| audio | {audio_filename} |\n"
            f"\n"
            f"## 生成提示词（英文 · 复制到 ElevenLabs）\n"
            f"\n"
            f"```\n"
            f"{prompt}\n"
            f"```\n"
        )

    @staticmethod
    def _parse_sidecar(md_path: Path) -> tuple[BgmAttrs, int] | None:
        """Parse the sidecar table back into `(BgmAttrs, seed)`. Returns None
        on read error or missing required fields."""
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
            if key in {"字段"} or set(key) <= {"-", ":"}:
                continue
            fields[key] = value
        if "category" not in fields:
            return None

        def _clean(v: str) -> str:
            return "" if v == "—" else v

        def _int(key: str, default: int) -> int:
            try:
                return int(fields[key])
            except (KeyError, ValueError):
                return default

        try:
            attrs = BgmAttrs(
                category=fields["category"],
                mood=_clean(fields.get("mood", "")),
                bpm=_int("bpm", 90),
                duration=_int("duration", 30),
                loopable=fields.get("loopable", "false").strip().lower() == "true",
                intensity=_int("intensity", 3),
                instruments=_clean(fields.get("instruments", "")),
                notes=_clean(fields.get("notes", "")),
            )
        except Exception:
            return None
        return attrs, _int("seed", 0)
