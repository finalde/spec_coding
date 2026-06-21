"""Scan the user OS Downloads folder and import recent media into a drama tree.

Per follow-up 009: enriches the drama-row rename button into a one-click
"import + rename" flow. Filename substring-matches against the drama's
`characters/`, `scenes/`, and `episodes/*/shots/shot*/` folders to choose
a destination. Shot-matched media lands in the shot's `renders/` subfolder
(`shots/shot{NN}/renders/`) with its ORIGINAL filename preserved — so the
start-frame / end-frame / video outputs of one shot coexist without colliding
and stay distinguishable; character/scene media still lands directly in the
asset folder. Scene-matched media is refined one level deeper when the
filename carries a background-plate 方位 token: a scene's `bg{N}_{方位}_{描述}/`
orientation sub-folders are matched on their 方位 segment (the out-of-image
tool names the download from the prompt's `主体:` line, which opens with that
方位 word), so each orientation PNG lands in its own plate folder while the
walk-through `.mp4` (no 方位 token) stays at scene root. A scene-plate folder
holds exactly one canonical image, so re-importing OVERWRITES it: existing
media in the plate folder (including stale `{plate}1/{plate}2` numbered
leftovers) is cleared before the new download is moved in. Unmatched files land in `<drama>/not_matched/` for manual
triage. (Shot folders were renamed `prompts/` → `shots/` per ai_video rule
2 v3; the legacy `prompts/` name is still accepted for unmigrated trees.) Only Downloads' immediate children are scanned, restricted to media
extensions with mtime within the last 7 days; symlinks are skipped.

This module is the first place the backend reads from a path OUTSIDE
EXPOSED_TREE. Source-side hardening: basename validation, symlink refusal,
and shutil.move (never copy + delete in two steps that could leave orphans).
Destination is always inside the drama folder validated by MediaRenamer.
"""
from __future__ import annotations

import os
import re
import shutil
import time
from dataclasses import dataclass, field
from io import BytesIO
from libs.common import drama_layout
from pathlib import Path

from PIL import Image

from libs.common.exposed_tree import MEDIA_EXTENSIONS, ExposedTree
from libs.common.safe_resolve import SafeResolver
from libs.domain.errors.casting__error import DramaNotFoundError, InvalidDramaPathError
from libs.domain.errors.downloads__error import DownloadsDirMissingError
from libs.infrastructure.writers.actor__writer import (
    ACTORS_DIR_NAME,
    ActorPool,
    _ACTOR_DIR_RE,
    _ACTOR_IMPORT_TAG,
    _attrs_to_body_filename,
    _attrs_to_filename,
)
from libs.infrastructure.writers.media__writer import MediaRenamer, RenameResult

ACTOR_NOT_MATCHED_DIR_NAME = "_not_matched"

NOT_MATCHED_DIR_NAME = "not_matched"
PERF_NOT_MATCHED_DIR_NAME = "_not_matched"
RENDERS_DIR_NAME = "renders"
PERF_LIBRARY_DIR_NAME = "_performances"
# Performance-library import tag, written as the first line of every render
# prompt block (per `_performances/_testrig.md`). The library uses ONE generic,
# model-agnostic prompt per entry (the user renders it on any model with their
# own uploaded actor), so the tag carries no model marker:
#   `演{NNNN}`   = the generic test video → `perf_{NNNN}/renders/` (original
#                  name kept, so multiple models' renders coexist).
#   `演{NNNN}始`  = the start-frame still → `perf_{NNNN}__startframe.{ext}`.
# Kling names a download from the prompt's first ~9 chars, so this 5–6-char tag
# lands in the filename and routes the file.
_PERF_TAG = re.compile(r"演(\d{4})(始)?")
_PERF_FOLDER_RE = re.compile(r"^perf_(\d{4})$")
# BGM library import: each track's prompt opens with its `bgm_NNNN` id as the
# first line (the routing KEY), so a downloaded music file named after the
# prompt head carries that tag. Route the file to `_bgm/{cat}/bgm_NNNN/`.
BGM_LIBRARY_DIR_NAME = "_bgm"
BGM_NOT_MATCHED_DIR_NAME = "_not_matched"
_BGM_TAG = re.compile(r"bgm_(\d{4,})")
_BGM_FOLDER_RE = re.compile(r"^bgm_(\d{4,})$")
_BGM_AUDIO_EXTS = frozenset({".mp3", ".wav", ".m4a", ".flac", ".ogg", ".aac"})
DEFAULT_TIME_WINDOW_SECONDS = 7 * 24 * 60 * 60
DOWNLOADS_ENV_VAR = "AI_VIDEO_MGMT_DOWNLOADS_DIR"
_BASENAME_INVALID = re.compile(r"[\x00-\x1f/\\:*?\"<>|]")
# Scene background plates live in orientation sub-folders named
# `bg{N}_{方位}_{描述}` (per ai_video scene-plate convention). The 方位
# segment — the FIRST `_`-part after the `bg{N}_` prefix — is the routing key:
# out-of-image tools (jimeng/即梦) name the download from the prompt's `主体:`
# line, which opens with that 方位 word, so it reliably lands in the filename.
# The 描述 segment is NOT used: descriptive words (`厅门`, `东侧`, …) also appear
# as camera-walk references inside OTHER orientations' filenames and would
# cross-match; the 方位 words are mutually exclusive.
_PLATE_PREFIX = re.compile(r"^bg\d+_")
_PLATE_NON_DEST = frozenset({NOT_MATCHED_DIR_NAME, RENDERS_DIR_NAME, "frames", "archive"})
PROPS_DIR_NAME = "props"
# A character-matched download that is an intro-card nameplate (its prompt opens
# with `{角色} · 出场名牌卡 …`, ai_video.md rule 11d) routes to the character
# folder's canonical `intro_card.{ext}` rather than landing under its raw name.
_INTRO_CARD_MARKER = re.compile(r"名牌|出场卡|intro[ _]?card")
# A scene-ROOT asset (whole-scene 立绘 / 全局建场底图 / walk-through), as opposed
# to a directional `bg{N}_{方位}_` plate. Its filename carries one of these
# markers; it must stay at the scene root and NOT be routed into a plate
# sub-folder even when a 方位 token (e.g. `庙内`) appears as a substring of the
# scene description (`小神庙内部` → spurious `庙内` plate match).
_SCENE_ROOT_MARKER = re.compile(r"场景立绘|全局|建场|底图|巡游|环视|walk")
_IMAGE_EXTS_LC = frozenset({".png", ".webp", ".jpg", ".jpeg"})


@dataclass(frozen=True)
class _Candidate:
    folder: Path
    kind: str  # "character" | "scene" | "shot"
    tokens: tuple[str, ...]  # already lowercased


@dataclass
class ImportResult:
    moved: list[dict[str, str]] = field(default_factory=list)
    unmatched: list[dict[str, str]] = field(default_factory=list)
    errors: list[dict[str, str]] = field(default_factory=list)
    rename: dict[str, object] | None = None

    def to_payload(self) -> dict[str, object]:
        return {
            "moved": list(self.moved),
            "unmatched": list(self.unmatched),
            "errors": list(self.errors),
            "rename": self.rename if self.rename is not None else {"renamed": [], "skipped": [], "errors": []},
        }


class DownloadsImporter:
    def __init__(
        self,
        exposed: ExposedTree,
        resolver: SafeResolver,
        renamer: MediaRenamer,
        downloads_dir: Path | None = None,
        time_window_seconds: int = DEFAULT_TIME_WINDOW_SECONDS,
    ) -> None:
        self._exposed = exposed
        self._resolver = resolver
        self._renamer = renamer
        self._downloads_dir = (downloads_dir or self._resolve_default_downloads_dir()).resolve()
        self._window = time_window_seconds

    @staticmethod
    def _resolve_default_downloads_dir() -> Path:
        override = os.environ.get(DOWNLOADS_ENV_VAR, "").strip()
        if override:
            return Path(override)
        return Path.home() / "Downloads"

    def import_drama(self, rel_drama_path: str) -> ImportResult:
        drama_dir = self._renamer.validate_drama(rel_drama_path)
        if not self._downloads_dir.is_dir():
            raise DownloadsDirMissingError(str(self._downloads_dir))
        candidates = self._collect_candidates(drama_dir)
        cutoff = time.time() - self._window
        result = ImportResult()
        not_matched_dir = drama_dir / NOT_MATCHED_DIR_NAME
        for src in self._iter_downloads(cutoff):
            if not self._is_safe_basename(src.name):
                result.errors.append({"path": self._display_src(src), "message": "invalid_basename"})
                continue
            chosen = self._classify(src.name, candidates)
            if chosen is None:
                # Fallback: a scene background-plate download often carries only
                # the 方位 token (`bg1_朝北_…`) with NO pinyin scene-name token —
                # the out-of-image tool (kling/jimeng) truncates the filename to
                # the prompt's first ~10 chars, where the early 方位 survives but
                # the scene handle does not. Route by 方位 to the unique matching
                # plate folder across the drama's scenes.
                plate = self._match_plate_any_scene(src.name, drama_dir)
                if plate is not None:
                    dst_folder, kind, unmatched = plate, "scene_plate", False
                else:
                    dst_folder, kind, unmatched = not_matched_dir, "unmatched", True
            else:
                dst_folder, kind, unmatched = chosen.folder, chosen.kind, False
                if chosen.kind == "scene":
                    plate = self._match_scene_plate(src.name, chosen.folder)
                    if plate is not None:
                        dst_folder, kind = plate, "scene_plate"
            # Canonical-named destinations (one image per folder): an intro-card
            # nameplate matched to a character → `{char}/intro_card.{ext}`; a prop
            # download → `props/{道具}/{道具}.{ext}`. Everything else keeps its
            # original download name (shot renders,立绘, scene plates).
            ext = src.suffix.lower()
            dst_name = src.name
            if kind == "character" and _INTRO_CARD_MARKER.search(src.name.lower()):
                kind, dst_name = "intro_card", f"intro_card{ext}"
            elif kind == "prop":
                dst_name = f"{dst_folder.name}{ext}"
            try:
                dst_folder.mkdir(parents=True, exist_ok=True)
            except OSError as exc:
                result.errors.append({"path": self._display_src(src), "message": f"mkdir_failed: {exc}"})
                continue
            # Overwrite semantics: a scene-plate folder holds exactly ONE
            # canonical image ({plate_id}.ext) → clear stale media first. An
            # intro card replaces only `intro_card.*` (NOT the立绘 etc. in the
            # same character folder).
            if kind == "scene_plate":
                self._clear_folder_media(dst_folder)
            elif kind == "intro_card":
                self._clear_named_media(dst_folder, "intro_card")
            dst = dst_folder / dst_name
            if dst.exists():
                try:
                    dst.unlink()
                except OSError as exc:
                    result.errors.append({"path": self._display_src(src), "message": f"overwrite_failed: {exc}"})
                    continue
            try:
                shutil.move(str(src), str(dst))
            except OSError as exc:
                result.errors.append({"path": self._display_src(src), "message": f"move_failed: {exc}"})
                continue
            entry = {"from": self._display_src(src), "to": self._rel(dst), "kind": kind}
            if unmatched:
                result.unmatched.append(entry)
            else:
                result.moved.append(entry)
        rename_result = self._renamer.rename_drama(
            rel_drama_path,
            excluded_folder_names=frozenset({NOT_MATCHED_DIR_NAME, RENDERS_DIR_NAME, "frames"}),
        )
        result.rename = rename_result.to_payload()
        return result

    def import_performances(self, rel_path: str) -> ImportResult:
        """One-click import for the performance library (`ai_videos/_performances`).

        Unlike `import_drama` (which routes by drama character/scene/shot folder
        names), this routes by the `演{NNNN}{克|即|始}` import tag carried in the
        download filename (Kling/Seedance name the file from the prompt's first
        chars, where the tag lives). The file lands in `{emotion}/perf_{NNNN}/`
        renamed to its canonical name (`perf_{NNNN}__kling.mp4` /
        `__seedance.mp4` / `__startframe.png`). Unmatched files go to
        `_performances/_not_matched/`. No folder-name rename pass — perf folders
        are ID-named and stable.
        """
        perf_root = self._renamer.validate_drama(rel_path)
        if not self._downloads_dir.is_dir():
            raise DownloadsDirMissingError(str(self._downloads_dir))
        perf_folders = self._collect_perf_folders(perf_root)
        cutoff = time.time() - self._window
        result = ImportResult()
        not_matched_dir = perf_root / PERF_NOT_MATCHED_DIR_NAME
        for src in self._iter_downloads(cutoff):
            if not self._is_safe_basename(src.name):
                result.errors.append({"path": self._display_src(src), "message": "invalid_basename"})
                continue
            tag = _PERF_TAG.search(src.name)
            matched = tag is not None and tag.group(1) in perf_folders
            if matched:
                num, is_startframe = tag.group(1), tag.group(2) == "始"
                perf_dir = perf_folders[num]
                if is_startframe:
                    # single canonical reference frame
                    dst_folder = perf_dir
                    dst = perf_dir / f"perf_{num}__startframe{src.suffix.lower()}"
                    kind = "performance_startframe"
                else:
                    # generic test video → renders/ keeping the original name so
                    # multiple models' renders for the same entry coexist.
                    dst_folder = perf_dir / RENDERS_DIR_NAME
                    dst = dst_folder / src.name
                    kind = "performance_video"
            else:
                dst_folder = not_matched_dir
                dst = not_matched_dir / src.name
                kind = "unmatched"
            try:
                dst_folder.mkdir(parents=True, exist_ok=True)
            except OSError as exc:
                result.errors.append({"path": self._display_src(src), "message": f"mkdir_failed: {exc}"})
                continue
            if dst.exists():
                # Re-render of the same (perf, role): overwrite the canonical file.
                try:
                    dst.unlink()
                except OSError as exc:
                    result.errors.append({"path": self._display_src(src), "message": f"overwrite_failed: {exc}"})
                    continue
            try:
                shutil.move(str(src), str(dst))
            except OSError as exc:
                result.errors.append({"path": self._display_src(src), "message": f"move_failed: {exc}"})
                continue
            entry = {"from": self._display_src(src), "to": self._rel(dst), "kind": kind}
            if matched:
                result.moved.append(entry)
            else:
                result.unmatched.append(entry)
        return result

    def import_actors(self, rel_path: str) -> ImportResult:
        """One-click import for the actor pool (`ai_videos/_actors`), follow-up 124.

        Counterpart to prompt-only generation: each prompt-only actor's face /
        body prompt was prefixed with an `id{NNNN}{f|b}` tag, which Kling /
        Seedance carry into the downloaded filename (named from the prompt's
        first chars). This routes each download back to its `actor_{NNNN}/`
        folder by that tag, re-encodes it to the actor's canonical
        `{ethnicity}__{gender}__{age_range}.jpg` (face) or `...__body.jpg`
        (body) — the names `_find_actor_jpg` / `list_actors` look for — so an
        externally-rendered actor surfaces in the pool exactly like a
        Kling-generated one. Unmatched files go to `_actors/_not_matched/`.
        No folder-name rename pass: actor folders are ID-named and stable.
        """
        actors_root = (self._exposed.root / "ai_videos" / ACTORS_DIR_NAME).resolve()
        if not self._downloads_dir.is_dir():
            raise DownloadsDirMissingError(str(self._downloads_dir))
        actor_folders = self._collect_actor_folders(actors_root)
        cutoff = time.time() - self._window
        result = ImportResult()
        not_matched_dir = actors_root / ACTOR_NOT_MATCHED_DIR_NAME
        for src in self._iter_downloads(cutoff):
            if not self._is_safe_basename(src.name):
                result.errors.append({"path": self._display_src(src), "message": "invalid_basename"})
                continue
            tag = _ACTOR_IMPORT_TAG.search(src.name)
            num = int(tag.group(1)) if tag is not None else None
            matched = num is not None and num in actor_folders
            if matched:
                is_body = tag.group(2).lower() == "b"
                actor_dir = actor_folders[num]
                attrs = ActorPool._parse_sidecar(actor_dir / f"{actor_dir.name}.md")
                if attrs is None:
                    result.errors.append({"path": self._display_src(src), "message": "sidecar_unreadable"})
                    continue
                fname = _attrs_to_body_filename(attrs) if is_body else _attrs_to_filename(attrs)
                dst = actor_dir / fname
                kind = "actor_body" if is_body else "actor_face"
                try:
                    self._reencode_to_jpeg(src, dst)
                except (OSError, ValueError) as exc:
                    result.errors.append({"path": self._display_src(src), "message": f"convert_failed: {exc}"})
                    continue
                result.moved.append({"from": self._display_src(src), "to": self._rel(dst), "kind": kind})
            else:
                try:
                    not_matched_dir.mkdir(parents=True, exist_ok=True)
                except OSError as exc:
                    result.errors.append({"path": self._display_src(src), "message": f"mkdir_failed: {exc}"})
                    continue
                dst = not_matched_dir / src.name
                if dst.exists():
                    try:
                        dst.unlink()
                    except OSError as exc:
                        result.errors.append({"path": self._display_src(src), "message": f"overwrite_failed: {exc}"})
                        continue
                try:
                    shutil.move(str(src), str(dst))
                except OSError as exc:
                    result.errors.append({"path": self._display_src(src), "message": f"move_failed: {exc}"})
                    continue
                result.unmatched.append({"from": self._display_src(src), "to": self._rel(dst), "kind": "unmatched"})
        return result

    def import_bgms(self, rel_path: str) -> ImportResult:
        """One-click GLOBAL import for the BGM library (`ai_videos/_bgm`).

        Counterpart to prompt-only BGM generation: each track's prompt opens
        with its `bgm_NNNN` id as the first line, which ElevenLabs carries into
        the downloaded filename. This routes each recent audio download back to
        its `_bgm/{category}/bgm_NNNN/` folder by that tag, naming it
        `bgm_NNNN.{ext}` (one audio file per track — prior audio is cleared).
        Unmatched files go to `_bgm/_not_matched/`. No folder-rename pass: bgm
        folders are id-named and stable."""
        bgm_root = (self._exposed.root / "ai_videos" / BGM_LIBRARY_DIR_NAME).resolve()
        if not self._downloads_dir.is_dir():
            raise DownloadsDirMissingError(str(self._downloads_dir))
        folders = self._collect_bgm_folders(bgm_root)
        cutoff = time.time() - self._window
        result = ImportResult()
        not_matched_dir = bgm_root / BGM_NOT_MATCHED_DIR_NAME
        for src in self._iter_downloads(cutoff):
            if src.suffix.lower() not in _BGM_AUDIO_EXTS:
                continue
            if not self._is_safe_basename(src.name):
                result.errors.append({"path": self._display_src(src), "message": "invalid_basename"})
                continue
            tag = _BGM_TAG.search(src.name)
            num = tag.group(1) if tag is not None else None
            matched = num is not None and num in folders
            if matched:
                bgm_dir = folders[num]
                self._clear_audio_files(bgm_dir)
                dst_folder, dst = bgm_dir, bgm_dir / f"bgm_{num}{src.suffix.lower()}"
                kind = "bgm_audio"
            else:
                dst_folder, dst = not_matched_dir, not_matched_dir / src.name
                kind = "unmatched"
            try:
                dst_folder.mkdir(parents=True, exist_ok=True)
            except OSError as exc:
                result.errors.append({"path": self._display_src(src), "message": f"mkdir_failed: {exc}"})
                continue
            if dst.exists():
                try:
                    dst.unlink()
                except OSError as exc:
                    result.errors.append({"path": self._display_src(src), "message": f"overwrite_failed: {exc}"})
                    continue
            try:
                shutil.move(str(src), str(dst))
            except OSError as exc:
                result.errors.append({"path": self._display_src(src), "message": f"move_failed: {exc}"})
                continue
            entry = {"from": self._display_src(src), "to": self._rel(dst), "kind": kind}
            if matched:
                result.moved.append(entry)
            else:
                result.unmatched.append(entry)
        return result

    @staticmethod
    def _collect_bgm_folders(bgm_root: Path) -> dict[str, Path]:
        """Map each track's numeric id (as string) to its
        `_bgm/{category}/bgm_NNNN/` folder, across all categories."""
        folders: dict[str, Path] = {}
        try:
            cats = sorted(bgm_root.iterdir(), key=lambda p: p.name)
        except OSError:
            return folders
        for cat in cats:
            if not cat.is_dir() or cat.is_symlink() or cat.name.startswith("_"):
                continue
            try:
                tracks = sorted(cat.iterdir(), key=lambda p: p.name)
            except OSError:
                continue
            for t in tracks:
                if not t.is_dir() or t.is_symlink():
                    continue
                m = _BGM_FOLDER_RE.match(t.name)
                if m:
                    folders[m.group(1)] = t
        return folders

    @staticmethod
    def _clear_audio_files(folder: Path) -> None:
        """Delete top-level audio files in a track folder (one canonical audio
        per track — overwrite on re-import)."""
        try:
            entries = list(folder.iterdir())
        except OSError:
            return
        for child in entries:
            try:
                if child.is_file() and not child.is_symlink() and child.suffix.lower() in _BGM_AUDIO_EXTS:
                    child.unlink()
            except OSError:
                pass

    @staticmethod
    def _collect_actor_folders(actors_root: Path) -> dict[int, Path]:
        """Map each actor's numeric id to its `actor_{NNNN}/` folder."""
        folders: dict[int, Path] = {}
        try:
            entries = sorted(actors_root.iterdir(), key=lambda p: p.name)
        except OSError:
            return folders
        for entry in entries:
            if not entry.is_dir() or entry.is_symlink():
                continue
            m = _ACTOR_DIR_RE.match(entry.name)
            if m:
                folders[int(m.group(1))] = entry
        return folders

    @staticmethod
    def _reencode_to_jpeg(src: Path, dst: Path) -> None:
        """Transcode a downloaded image to JPEG at `dst` (overwriting any
        existing canonical jpg), then delete the source. Actor lookup keys off
        a `.jpg` canonical name, so a downloaded png/webp must be re-encoded,
        not merely moved — and re-encoding a same-name jpg is harmless."""
        with Image.open(src) as im:
            buf = BytesIO()
            im.convert("RGB").save(buf, format="JPEG", quality=92)
        dst.write_bytes(buf.getvalue())
        try:
            src.unlink()
        except OSError:
            pass

    @staticmethod
    def _collect_perf_folders(perf_root: Path) -> dict[str, Path]:
        """Map each 4-digit perf number to its `{emotion}/perf_{NNNN}/` folder."""
        folders: dict[str, Path] = {}
        try:
            emotion_dirs = sorted(perf_root.iterdir(), key=lambda p: p.name)
        except OSError:
            return folders
        for emotion_dir in emotion_dirs:
            if not emotion_dir.is_dir() or emotion_dir.is_symlink():
                continue
            if emotion_dir.name.startswith("_"):
                continue
            try:
                perf_dirs = sorted(emotion_dir.iterdir(), key=lambda p: p.name)
            except OSError:
                continue
            for perf_dir in perf_dirs:
                if not perf_dir.is_dir() or perf_dir.is_symlink():
                    continue
                m = _PERF_FOLDER_RE.match(perf_dir.name)
                if m:
                    folders[m.group(1)] = perf_dir
        return folders

    def _collect_candidates(self, drama_dir: Path) -> list[_Candidate]:
        out: list[_Candidate] = []
        characters_dir = drama_layout.characters_dir(drama_dir)
        if characters_dir.is_dir():
            for child in sorted(characters_dir.iterdir()):
                if child.is_dir() and not child.is_symlink():
                    out.append(_Candidate(folder=child, kind="character", tokens=self._tokens(child.name)))
        scenes_dir = drama_layout.scenes_dir(drama_dir)
        if scenes_dir.is_dir():
            for child in sorted(scenes_dir.iterdir()):
                if child.is_dir() and not child.is_symlink():
                    out.append(_Candidate(folder=child, kind="scene", tokens=self._tokens(child.name)))
        # Props (`2_世界观人设/props/{道具名}/`) — a sibling of characters/scenes;
        # one canonical image per prop folder (e.g. `props/玉佩/玉佩.png`).
        props_dir = drama_layout.characters_dir(drama_dir).parent / PROPS_DIR_NAME
        if props_dir.is_dir():
            for child in sorted(props_dir.iterdir()):
                if child.is_dir() and not child.is_symlink():
                    out.append(_Candidate(folder=child, kind="prop", tokens=self._tokens(child.name)))
        episodes_dir = drama_layout.episodes_dir(drama_dir)
        if episodes_dir.is_dir():
            for ep in sorted(episodes_dir.iterdir()):
                if not ep.is_dir() or ep.is_symlink():
                    continue
                # Shot folders live under episodes/{ep}/shots/ (renamed from
                # the legacy prompts/ per ai_video rule 2 v3). Accept either.
                shots_dir = ep / "shots"
                if not shots_dir.is_dir():
                    shots_dir = ep / "prompts"
                if not shots_dir.is_dir():
                    continue
                for shot in sorted(shots_dir.iterdir()):
                    if not shot.is_dir() or shot.is_symlink():
                        continue
                    tokens = self._tokens(shot.name)
                    ep_name = ep.name
                    extra: list[str] = []
                    if ep_name:
                        extra.append(f"{ep_name}_{shot.name}".lower())
                        extra.append(ep_name.lower())
                    # Compact Chinese tag `{NN}集{NN}镜` — matches the filename
                    # Kling derives from the shot block's first line
                    # `{NN}集{NN}镜{视|始|末}` (ai_video rule 12.4). The ASCII
                    # `epNN_shotNN` first line truncated to Kling's 9-char window
                    # as `ep01_shot` (shot number lost → every episode render
                    # collided); the Chinese tag fits ep+shot inside 9 chars.
                    ep_digits = re.sub(r"\D", "", ep_name)
                    shot_digits = re.sub(r"\D", "", shot.name)
                    if ep_digits and shot_digits:
                        extra.append(f"{ep_digits}集{shot_digits}镜")
                    tokens = tuple(dict.fromkeys((*tokens, *extra)))
                    # Shot media goes into the shot's renders/ subfolder so the
                    # start/end/video outputs coexist with original names and
                    # don't clutter or collide with shot{NN}.md.
                    out.append(
                        _Candidate(folder=shot / RENDERS_DIR_NAME, kind="shot", tokens=tokens)
                    )
        return out

    @staticmethod
    def _tokens(folder_name: str) -> tuple[str, ...]:
        tokens: list[str] = [folder_name.lower()]
        if "_" in folder_name:
            for part in folder_name.split("_"):
                part = part.strip().lower()
                if len(part) >= 2:
                    tokens.append(part)
        seen: dict[str, None] = {}
        for t in tokens:
            if t and t not in seen:
                seen[t] = None
        return tuple(seen)

    @staticmethod
    def _classify(filename: str, candidates: list[_Candidate]) -> _Candidate | None:
        name = filename.lower()
        # The compact shot tag `{NN}集{NN}镜` is the AUTHORITATIVE routing key for
        # a shot render: Kling/jimeng name the download from the shot block's
        # first line `{NN}集{NN}镜{视|始|末}` (ai_video rule 12.4 / 2026-05-30), so
        # its presence unambiguously identifies the owning shot. It MUST win
        # outright over length-based scoring — a shot's `参考:` line now embeds
        # the scene-plate handle it references (e.g. `s4_回忆庭院·bg1_…`), so the
        # scene name appears in the render filename and, being a longer token,
        # would otherwise out-score the shot tag and misroute the render into the
        # scene folder (follow-up wushen_juexing/026).
        tag_m = re.search(r"(\d+)集(\d+)镜", filename)
        if tag_m is not None:
            tag = f"{tag_m.group(1)}集{tag_m.group(2)}镜"
            for cand in candidates:
                if cand.kind == "shot" and tag in cand.tokens:
                    return cand
        kind_priority = {"shot": 4, "prop": 3, "scene": 2, "character": 1}
        best: tuple[int, int, str, _Candidate] | None = None  # (score, kind_rank, folder_name_lex, candidate)
        for cand in candidates:
            score = 0
            for token in cand.tokens:
                if token and token in name:
                    if len(token) > score:
                        score = len(token)
            if score == 0:
                continue
            key = (score, kind_priority[cand.kind], -ord_seq(cand.folder.name))
            if best is None or key > best[:3]:
                best = (*key, cand)
        return best[3] if best is not None else None

    @staticmethod
    def _clear_folder_media(folder: Path) -> None:
        """Delete top-level media files in a folder (overwrite support for
        single-image scene-plate folders). Subfolders, non-media, and symlinks
        are left untouched."""
        try:
            entries = list(folder.iterdir())
        except OSError:
            return
        for child in entries:
            try:
                if child.is_file() and not child.is_symlink() and child.suffix.lower() in MEDIA_EXTENSIONS:
                    child.unlink()
            except OSError:
                pass

    @staticmethod
    def _clear_named_media(folder: Path, stem: str) -> None:
        """Delete `{stem}.{img ext}` files in a folder (intro-card re-import:
        replace only `intro_card.*`, never the character's other images)."""
        try:
            entries = list(folder.iterdir())
        except OSError:
            return
        for child in entries:
            try:
                if (child.is_file() and not child.is_symlink()
                        and child.stem == stem and child.suffix.lower() in _IMAGE_EXTS_LC):
                    child.unlink()
            except OSError:
                pass

    @staticmethod
    def _plate_orientation_token(folder_name: str) -> str | None:
        """The 方位 routing token of a `bg{N}_{方位}_{描述}` plate folder:
        the first `_`-segment after the `bg{N}_` prefix. Returns None for
        folders that don't follow the plate convention."""
        m = _PLATE_PREFIX.match(folder_name)
        if m is None:
            return None
        token = folder_name[m.end():].split("_", 1)[0].strip().lower()
        return token or None

    @classmethod
    def _match_scene_plate(cls, filename: str, scene_folder: Path) -> Path | None:
        """When a file matched a scene, route it deeper into the orientation
        plate sub-folder whose 方位 token appears in the filename. Files with
        no 方位 token (e.g. the scene walk-through `.mp4`) — or whole-scene assets
        (场景立绘 / 全局建场底图), whose description can spuriously contain a 方位
        substring — stay at the scene root."""
        if _SCENE_ROOT_MARKER.search(filename):
            return None
        name = filename.lower()
        best: tuple[int, str, Path] | None = None
        try:
            children = sorted(scene_folder.iterdir(), key=lambda p: p.name)
        except OSError:
            return None
        for child in children:
            if not child.is_dir() or child.is_symlink() or child.name in _PLATE_NON_DEST:
                continue
            token = cls._plate_orientation_token(child.name)
            if token is None or token not in name:
                continue
            key = (len(token), child.name)
            if best is None or key > best[:2]:
                best = (len(token), child.name, child)
        return best[2] if best is not None else None

    def _match_plate_any_scene(self, filename: str, drama_dir: Path) -> Path | None:
        """Route a scene background-plate download by its 方位 token alone, when
        `_classify` found no scene-name match.

        Out-of-image tools truncate the download filename to the prompt's first
        ~10 chars; for a plate prompt whose first line is the plate_id
        (`bg{N}_{方位}_…`) the EARLY 方位 token survives but the pinyin scene
        handle does not — so the file never matches a scene by name. This scans
        every plate folder under `scenes/*/bg{N}_{方位}_…/` and routes the file
        to the one whose 方位 token appears in the filename. Disambiguation when
        more than one scene owns the same 方位: keep only plates whose SCENE name
        token also appears in the filename; route iff that leaves exactly one
        plate folder (else None → not_matched, never a silent misroute).
        """
        name = filename.lower()
        scenes_dir = drama_layout.scenes_dir(drama_dir)
        if not scenes_dir.is_dir():
            return None
        all_hits: list[Path] = []
        scene_scoped_hits: list[Path] = []
        try:
            scenes = sorted(scenes_dir.iterdir(), key=lambda p: p.name)
        except OSError:
            return None
        for scene in scenes:
            if not scene.is_dir() or scene.is_symlink():
                continue
            scene_present = any(tok in name for tok in self._tokens(scene.name))
            try:
                children = sorted(scene.iterdir(), key=lambda p: p.name)
            except OSError:
                continue
            for child in children:
                if not child.is_dir() or child.is_symlink() or child.name in _PLATE_NON_DEST:
                    continue
                token = self._plate_orientation_token(child.name)
                if token is None or token not in name:
                    continue
                all_hits.append(child)
                if scene_present:
                    scene_scoped_hits.append(child)
        pool = scene_scoped_hits or all_hits
        unique = {p.resolve() for p in pool}
        return pool[0] if len(unique) == 1 else None

    def _iter_downloads(self, cutoff: float) -> list[Path]:
        out: list[Path] = []
        try:
            entries = sorted(self._downloads_dir.iterdir(), key=lambda p: p.name)
        except OSError:
            return out
        for child in entries:
            try:
                if child.is_symlink():
                    continue
                if not child.is_file():
                    continue
            except OSError:
                continue
            if child.suffix.lower() not in MEDIA_EXTENSIONS:
                continue
            try:
                stat = child.stat()
            except OSError:
                continue
            if stat.st_mtime < cutoff:
                continue
            out.append(child)
        return out

    @staticmethod
    def _is_safe_basename(name: str) -> bool:
        if not name or name in (".", ".."):
            return False
        if _BASENAME_INVALID.search(name):
            return False
        if len(name) > 255:
            return False
        return True

    def _rel(self, p: Path) -> str:
        try:
            return p.resolve().relative_to(self._resolver.root).as_posix()
        except (OSError, ValueError):
            return p.as_posix()

    def _display_src(self, p: Path) -> str:
        try:
            home = Path.home().resolve()
            rel = p.resolve().relative_to(home)
            return f"~/{rel.as_posix()}"
        except (OSError, ValueError):
            return p.name


def ord_seq(s: str) -> int:
    # Stable lex-tiebreaker hashed to a single int (higher = lexicographically smaller wins via negation).
    total = 0
    for ch in s[:32]:
        total = (total << 8) | (ord(ch) & 0xff)
    return total


__all__ = [
    "DEFAULT_TIME_WINDOW_SECONDS",
    "DOWNLOADS_ENV_VAR",
    "DownloadsImporter",
    "ImportResult",
    "NOT_MATCHED_DIR_NAME",
    "RENDERS_DIR_NAME",
    "RenameResult",
]
