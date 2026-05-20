"""Character-video aggregate writer: truncate any character mp4 to a
2-second `video.mp4` + build a per-shot character reel by concatenating
each involved character's `video.mp4`.

Consolidates the former `character_video__truncator.py` and
`shot_concat__builder.py`. One file per aggregate per role, per
follow-up 059. The two operations share the same trio of base exceptions
(InvalidPath / NotFound / FfmpegMissing); operation-specific ones
(NotCharacterVideo, TruncateFailed, NotShotMd, NoCharacterTable,
ConcatFailed) remain disjoint.

ffmpeg binary supplied by `imageio-ffmpeg` — no system install required.
"""
from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

import imageio_ffmpeg

from libs.common.exposed_tree import ExposedTree
from libs.common.safe_resolve import SafeResolver



from libs.domain.value_objects.character_video__valueobject import (
    CANONICAL_VIEWS,
    CharacterViewSpec,
    audio_output_filename,
    view_output_filename,
)
from libs.infrastructure.errors.character_video__error import (  # noqa: F401
    AudioExtractFailed,
    ConcatFailed,
    FfmpegMissing,
    InvalidPath,
    NoCharacterTable,
    NotCharacterVideo,
    NotFound,
    NotShotMd,
    TruncateFailed,
    ViewExtractFailed,
)
# --- Shared exceptions ------------------------------------------------------


# --- Truncate (per-character mp4 -> 2-second video.mp4) --------------------


VIDEO_EXTENSIONS: frozenset[str] = frozenset(
    {".mp4", ".mov", ".webm", ".mkv", ".avi", ".m4v"}
)

_TRUNCATE_FFMPEG_TIMEOUT_S: int = 60
_OUTPUT_NAME: str = "video.mp4"
_TRUNCATE_DURATION_S: float = 2.0

# Path shape: ai_videos / {drama} / characters / {cN_xxx} / {filename}.{ext}
_CHARACTER_DIR_RE: re.Pattern[str] = re.compile(r"^c\d+(_.*)?$")


@dataclass(frozen=True)
class TruncateResult:
    src_rel: str
    out_rel: str
    duration_seconds: float

    def to_payload(self) -> dict[str, object]:
        return {
            "src": self.src_rel,
            "out": self.out_rel,
            "duration_seconds": self.duration_seconds,
        }


class CharacterVideoTruncator:
    def __init__(self, exposed: ExposedTree, resolver: SafeResolver) -> None:
        self._exposed = exposed
        self._resolver = resolver

    def truncate(self, rel: str) -> TruncateResult:
        src = self._validate_character_video_source(rel)
        try:
            ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        except Exception as exc:
            raise FfmpegMissing(str(exc)) from exc
        out_path = src.parent / _OUTPUT_NAME
        cmd = [
            ffmpeg,
            "-y",
            "-i", str(src),
            "-t", str(_TRUNCATE_DURATION_S),
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-movflags", "+faststart",
            "-loglevel", "error",
            str(out_path),
        ]
        try:
            completed = subprocess.run(
                cmd,
                capture_output=True,
                timeout=_TRUNCATE_FFMPEG_TIMEOUT_S,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise TruncateFailed("ffmpeg_timeout") from exc
        if completed.returncode != 0 or not out_path.is_file():
            err = completed.stderr.decode("utf-8", errors="replace").strip()[:300]
            raise TruncateFailed(err or "ffmpeg_failed")
        return TruncateResult(
            src_rel=self._rel(src),
            out_rel=self._rel(out_path),
            duration_seconds=_TRUNCATE_DURATION_S,
        )

    def _validate_character_video_source(self, rel: str) -> Path:
        if not isinstance(rel, str) or rel == "":
            raise InvalidPath("path is empty")
        if not self._exposed.is_inside(rel):
            raise InvalidPath("path outside sandbox")
        ext = Path(rel).suffix.lower()
        if ext not in VIDEO_EXTENSIONS:
            raise NotCharacterVideo("extension is not a video type")
        if not self._is_under_character_folder(rel):
            raise NotCharacterVideo(
                "path must be under ai_videos/{drama}/characters/{cN_xxx}/"
            )
        resolved = self._resolver.resolve(rel)
        if resolved is None:
            raise InvalidPath("path failed sandbox resolution")
        if resolved.is_symlink():
            raise InvalidPath("symlink is not allowed")
        if not resolved.is_file():
            raise NotFound("file does not exist")
        return resolved

    @staticmethod
    def _is_under_character_folder(rel: str) -> bool:
        parts = rel.split("/")
        if len(parts) < 5:
            return False
        if parts[0] != "ai_videos":
            return False
        if parts[1].startswith("_"):
            return False
        if parts[2] != "characters":
            return False
        if not _CHARACTER_DIR_RE.match(parts[3]):
            return False
        return True

    def _rel(self, p: Path) -> str:
        try:
            return p.resolve().relative_to(self._resolver.root).as_posix()
        except (OSError, ValueError):
            return p.as_posix()


# --- Shot concat (parse shot md -> concat involved characters' video.mp4) --


_CONCAT_FFMPEG_TIMEOUT_S: int = 180
_CONCAT_SEGMENT_S: float = 2.0  # per-character clip length in the reel
_CONCAT_TARGET_W: int = 720     # 9:16 reel — 720x1280 is fast to encode + plenty for review
_CONCAT_TARGET_H: int = 1280
_CONCAT_TARGET_FPS: int = 30
_SHOT_DIR_RE: re.Pattern[str] = re.compile(r"^shot\d+$", re.IGNORECASE)
_SHOT_MD_NAME_RE: re.Pattern[str] = re.compile(r"^(shot\d+)\.md$", re.IGNORECASE)
_HEADER_ROW_RE: re.Pattern[str] = re.compile(r"角色.*character\s*file", re.IGNORECASE)
# Matches a per-character placeholder token like `{ref_c1_沧冥}` or
# `{ref_c10_司空玄}` (with optional trailing whitespace so the gap left
# behind doesn't leave a double space). `{ref_chars_reel}` is NOT matched
# (the `c` is not followed by a digit) and `{ref_s1_…}` scene refs are
# left alone. Inline-code backticks around the token are also consumed.
_CHAR_REF_TOKEN_RE: re.Pattern[str] = re.compile(r"`?\{ref_c\d+(?:_[^}]+)?\}`?[\t ]*")
# Strips prose after a `场景: {ref_sN_xxx}` token on the same line, leaving
# only the section header + placeholder.
_SCENE_LINE_RE: re.Pattern[str] = re.compile(
    r"^(\s*场景\s*[:：]\s*`?\{ref_s\d+(?:_[^}]+)?\}`?).*$"
)
# Matches a `时长:` / `时长：` line so the per-shot duration can be normalised
# to 15s (Kling/Seedance per-shot cap).
_DURATION_LINE_RE: re.Pattern[str] = re.compile(r"^(\s*时长\s*[:：]).*$")
# Recognises section-header lines inside the prompt code block. Used when
# deleting the `角色:` section to know where the next section begins.
_SECTION_HEADER_PREFIXES: tuple[str, ...] = (
    "场景", "镜头", "运镜", "动作", "台词", "字幕",
    "光线", "色调", "节奏", "渲染样式", "比例", "时长", "负向",
)
_PER_SHOT_DURATION_S: int = 15
# Lines that the new shot-prompt schema removes entirely from the prompt
# code block. `比例:` (aspect ratio) and any explicit clarity / resolution
# parameter belong in Seedance's UI, not in the prompt text.
_DROP_LINE_PREFIXES: tuple[str, ...] = ("比例", "分辨率", "清晰度")
# Resolution / quality tokens to scrub from any other line. Matched
# case-insensitively, with optional ` + ` separator cleanup afterwards.
_RESOLUTION_TOKEN_RE: re.Pattern[str] = re.compile(
    r"\s*\+?\s*(?:4K\s*HDR|8K\s*HDR|2K\s*HDR|4K|8K|2K|1080p|720p|HDR)\b\s*\+?",
    re.IGNORECASE,
)
# Collapses any leftover `+ +` or trailing `+` produced by the resolution-token
# strip into a single clean separator.
_PLUS_CLEANUP_RE: re.Pattern[str] = re.compile(r"\s*\+\s*\+\s*")


@dataclass(frozen=True)
class CharacterUsage:
    role: str
    character_folder: str
    video_rel: str

    def to_payload(self) -> dict[str, object]:
        return {
            "role": self.role,
            "character_folder": self.character_folder,
            "rel_path": self.video_rel,
        }


@dataclass(frozen=True)
class CharacterSkip:
    role: str
    character_folder: str
    reason: str

    def to_payload(self) -> dict[str, object]:
        return {
            "role": self.role,
            "character_folder": self.character_folder,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class ConcatResult:
    shot_rel: str
    out_rel: str | None
    used: tuple[CharacterUsage, ...]
    skipped: tuple[CharacterSkip, ...]

    def to_payload(self) -> dict[str, object]:
        return {
            "shot_path": self.shot_rel,
            "out": self.out_rel,
            "used": [u.to_payload() for u in self.used],
            "skipped": [s.to_payload() for s in self.skipped],
        }


class ShotConcatBuilder:
    def __init__(self, exposed: ExposedTree, resolver: SafeResolver) -> None:
        self._exposed = exposed
        self._resolver = resolver

    def build(self, rel: str) -> ConcatResult:
        shot_md, shot_slug, drama = self._validate_shot_md(rel)
        rows = self._parse_character_table(shot_md.read_text(encoding="utf-8"))
        if not rows:
            raise NoCharacterTable("no 出场角色 table found in shot md")
        used: list[CharacterUsage] = []
        skipped: list[CharacterSkip] = []
        for role, char_file_rel in rows:
            folder_rel = self._character_folder_for(drama, char_file_rel)
            if folder_rel is None:
                skipped.append(CharacterSkip(role, char_file_rel, "invalid_character_path"))
                continue
            folder_path = self._resolver.resolve(folder_rel)
            if folder_path is None or not folder_path.is_dir():
                skipped.append(CharacterSkip(role, folder_rel, "character_folder_missing"))
                continue
            clip = self._first_mp4_in_folder(folder_path)
            if clip is None:
                skipped.append(CharacterSkip(role, folder_rel, "no_mp4_in_folder"))
                continue
            used.append(CharacterUsage(role, folder_rel, f"{folder_rel}/{clip.name}"))
        if not used:
            return ConcatResult(
                shot_rel=self._rel(shot_md),
                out_rel=None,
                used=tuple(used),
                skipped=tuple(skipped),
            )
        out_path = shot_md.parent / f"{shot_slug}_chars.mp4"
        self._ffmpeg_concat(
            inputs=[self._resolver.resolve(u.video_rel) for u in used],  # type: ignore[list-item]
            out_path=out_path,
        )
        # Patch the shot md so the prompt code block carries a per-segment
        # character timing annotation referencing {ref_chars_reel}. Failures
        # here are non-fatal — the mp4 is already on disk.
        try:
            self._patch_chars_ref_line(shot_md, used)
        except OSError:
            pass
        return ConcatResult(
            shot_rel=self._rel(shot_md),
            out_rel=self._rel(out_path),
            used=tuple(used),
            skipped=tuple(skipped),
        )

    def _validate_shot_md(self, rel: str) -> tuple[Path, str, str]:
        if not isinstance(rel, str) or rel == "":
            raise InvalidPath("path is empty")
        if not self._exposed.is_inside(rel):
            raise InvalidPath("path outside sandbox")
        parts = rel.split("/")
        if len(parts) < 4:
            raise NotShotMd("path is too shallow to be a shot md")
        if parts[0] != "ai_videos" or parts[1].startswith("_"):
            raise NotShotMd("path is not under ai_videos/{drama}/")
        if Path(rel).suffix.lower() != ".md":
            raise NotShotMd("path is not a .md file")
        shot_dir_name = parts[-2]
        file_name = parts[-1]
        if not _SHOT_DIR_RE.match(shot_dir_name):
            raise NotShotMd("parent folder is not shot{NN}")
        md_match = _SHOT_MD_NAME_RE.match(file_name)
        if md_match is None:
            raise NotShotMd("filename is not shot{NN}.md")
        if parts[-3].lower() != "prompts":
            raise NotShotMd("shot folder is not under prompts/")
        drama = parts[1]
        resolved = self._resolver.resolve(rel)
        if resolved is None:
            raise InvalidPath("path failed sandbox resolution")
        if resolved.is_symlink():
            raise InvalidPath("symlink is not allowed")
        if not resolved.is_file():
            raise NotFound("file does not exist")
        return resolved, md_match.group(1).lower(), drama

    @staticmethod
    def _parse_character_table(text: str) -> list[tuple[str, str]]:
        lines = text.splitlines()
        header_idx: int | None = None
        for i, ln in enumerate(lines):
            if "|" not in ln:
                continue
            if _HEADER_ROW_RE.search(ln):
                header_idx = i
                break
        if header_idx is None:
            return []
        header_cells = _split_md_row(lines[header_idx])
        try:
            role_col = next(i for i, c in enumerate(header_cells) if "角色" in c)
        except StopIteration:
            return []
        try:
            file_col = next(
                i for i, c in enumerate(header_cells)
                if re.search(r"character\s*file", c, re.IGNORECASE)
            )
        except StopIteration:
            return []
        rows: list[tuple[str, str]] = []
        for ln in lines[header_idx + 2:]:
            if "|" not in ln:
                break
            stripped = ln.strip()
            if stripped == "":
                break
            cells = _split_md_row(ln)
            if max(role_col, file_col) >= len(cells):
                continue
            role = cells[role_col].strip()
            file_cell = _unwrap_inline_code(cells[file_col]).strip()
            if file_cell == "":
                continue
            rows.append((role, file_cell))
        return rows

    @staticmethod
    def _first_mp4_in_folder(folder: Path) -> Path | None:
        """Return the alphabetically-first mp4 directly in `folder`, or None.

        Excludes subdirectories (so `archive/` and any other nested folders
        are ignored automatically). Skips symlinks. Extension match is
        case-insensitive across the project's full video allowlist so a
        character folder holding `clip1.MOV` still resolves.
        """
        try:
            entries = sorted(folder.iterdir(), key=lambda p: p.name)
        except OSError:
            return None
        for entry in entries:
            if entry.is_symlink():
                continue
            if not entry.is_file():
                continue
            if entry.suffix.lower() not in VIDEO_EXTENSIONS:
                continue
            return entry
        return None

    @staticmethod
    def _patch_chars_ref_line(shot_md: Path, used: list[CharacterUsage]) -> None:
        """Patch the first ```text fenced block inside the `## 视频 prompt`
        section so the shot prompt follows the new schema:

        1. Insert / update a `参考: 请参考视频 {ref_chars_reel}, ...` line at
           the very top — match-by-prefix update makes re-runs idempotent.
        2. Drop the entire `角色:` section (header + bullet list). Every
           character is already named in the 参考 line above; the prose
           descriptions are redundant once the chars-reel ref carries the
           visual identity.
        3. Strip prose after `场景: {ref_sN_xxx}`, keeping only the section
           header + placeholder. The actual scene image is uploaded to
           Seedance separately.
        4. Strip per-character `{ref_cN_xxx}` tokens from any remaining line
           (the chars reel covers them).
        5. Normalise `时长:` to `时长: 15s` (per-shot Kling/Seedance cap).
        6. Delete `比例:` / `分辨率:` / `清晰度:` lines — these are Seedance
           UI knobs, not prompt content.
        7. Scrub resolution / quality tokens (4K HDR, 8K, 1080p, HDR, …)
           from any remaining line + collapse leftover `+` separators.

        The transform is fully idempotent: every re-run on the same file
        produces the same bytes. Authored content (镜头 / 运镜 / 动作 /
        台词 / 光线-色调 / 节奏 / 渲染样式 minus res tokens / 负向) is
        preserved verbatim — those carry creative intent the writer cannot
        synthesize. If the md lacks the expected section / fence, the
        function silently no-ops (mp4 already written; best-effort).
        """
        if not used:
            return
        timing = "，".join(
            f"{2 * i + 1}~{2 * i + 2}s 为 {u.role or u.character_folder.split('/')[-1]}"
            for i, u in enumerate(used)
        )
        ref_line = f"参考: 请参考视频 {{ref_chars_reel}}，{timing}。"
        try:
            text = shot_md.read_text(encoding="utf-8")
        except OSError:
            return
        lines = text.splitlines(keepends=False)
        # Find the `## 视频 prompt …` header (Chinese colon-tolerant).
        header_idx: int | None = None
        for i, ln in enumerate(lines):
            stripped = ln.strip()
            if stripped.startswith("##") and "视频 prompt" in stripped:
                header_idx = i
                break
        if header_idx is None:
            return
        # Find the first ```text fence after that header.
        fence_open: int | None = None
        for i in range(header_idx + 1, len(lines)):
            if lines[i].lstrip().startswith("```"):
                fence_open = i
                break
        if fence_open is None:
            return
        # Locate the matching closing fence.
        fence_close: int | None = None
        for i in range(fence_open + 1, len(lines)):
            if lines[i].lstrip().startswith("```"):
                fence_close = i
                break
        if fence_close is None:
            return
        body_start, body_end = fence_open + 1, fence_close

        # Step 1: insert/update the 参考 line at the top of the code block.
        replaced = False
        for i in range(body_start, body_end):
            if lines[i].startswith("参考: 请参考视频 {ref_chars_reel}"):
                lines[i] = ref_line
                replaced = True
                break
        if not replaced:
            lines.insert(body_start, ref_line)
            body_end += 1

        # Step 2: drop the entire `角色:` section (header + bullet list).
        ja_start = ShotConcatBuilder._find_role_section_start(lines, body_start, body_end)
        if ja_start is not None:
            ja_end = ShotConcatBuilder._find_role_section_end(lines, ja_start + 1, body_end)
            del lines[ja_start:ja_end]
            body_end -= (ja_end - ja_start)

        # Steps 3-7: per-line transforms within the (possibly shrunk) block.
        new_block: list[str] = []
        for i in range(body_start, body_end):
            ln = lines[i]
            # Step 6: drop 比例/分辨率/清晰度 lines entirely.
            stripped = ln.lstrip()
            if any(stripped.startswith(p) for p in _DROP_LINE_PREFIXES):
                continue
            # Step 3: scene line → keep only `场景: {ref_sN_xxx}`.
            scene_match = _SCENE_LINE_RE.match(ln)
            if scene_match is not None:
                new_block.append(scene_match.group(1))
                continue
            # Step 5: normalise 时长 to 15s.
            dur_match = _DURATION_LINE_RE.match(ln)
            if dur_match is not None:
                new_block.append(f"{dur_match.group(1)} {_PER_SHOT_DURATION_S}s")
                continue
            # Step 4 + 7: strip per-character refs and resolution tokens.
            if ln.startswith("参考: 请参考视频 {ref_chars_reel}"):
                new_block.append(ln)
                continue
            cleaned = _CHAR_REF_TOKEN_RE.sub("", ln)
            cleaned = _RESOLUTION_TOKEN_RE.sub(" + ", cleaned)
            cleaned = _PLUS_CLEANUP_RE.sub(" + ", cleaned)
            # Trim a `+` left dangling at end / start of the value side of `: ...`.
            cleaned = re.sub(r"\s*\+\s*$", "", cleaned)
            cleaned = re.sub(r"([:：])\s*\+\s*", r"\1 ", cleaned)
            # Collapse stray double-spaces produced by the token strip.
            cleaned = re.sub(r"[ \t]{2,}", " ", cleaned)
            new_block.append(cleaned)
        lines[body_start:body_end] = new_block

        # Preserve trailing newline if the source had one.
        new_text = "\n".join(lines)
        if text.endswith("\n"):
            new_text += "\n"
        try:
            shot_md.write_text(new_text, encoding="utf-8")
        except OSError:
            return

    @staticmethod
    def _find_role_section_start(lines: list[str], lo: int, hi: int) -> int | None:
        for i in range(lo, hi):
            stripped = lines[i].lstrip()
            if stripped.startswith("角色") and ("：" in stripped[:6] or ":" in stripped[:6]):
                return i
        return None

    @staticmethod
    def _find_role_section_end(lines: list[str], lo: int, hi: int) -> int:
        """Return the index of the first line at or after `lo` that ends the
        `角色:` section. Bullet (`-` …) and continuation (leading whitespace)
        lines belong to the section; the first non-bullet, non-continuation
        line (or a blank line) is where the section ends.
        """
        for i in range(lo, hi):
            ln = lines[i]
            stripped = ln.lstrip()
            if stripped == "":
                return i
            if stripped.startswith("-"):
                continue
            # Leading whitespace → continuation of previous bullet.
            if ln != stripped:
                continue
            # Otherwise this is a new section header → stop.
            if any(stripped.startswith(p) for p in _SECTION_HEADER_PREFIXES):
                return i
            # Any other non-bullet line is treated as section-ending too,
            # to be safe.
            return i
        return hi

    @staticmethod
    def _character_folder_for(drama: str, character_file_cell: str) -> str | None:
        cell = character_file_cell.strip()
        if cell == "":
            return None
        if cell.startswith("/") or ".." in cell.split("/"):
            return None
        parts = cell.split("/")
        if parts[0] == "ai_videos":
            if len(parts) < 5 or parts[1] != drama or parts[2] != "characters":
                return None
            char_dir = parts[3]
            if not _CHARACTER_DIR_RE.match(char_dir):
                return None
            return f"ai_videos/{drama}/characters/{char_dir}"
        if parts[0] == "characters":
            if len(parts) < 3:
                return None
            char_dir = parts[1]
            if not _CHARACTER_DIR_RE.match(char_dir):
                return None
            return f"ai_videos/{drama}/characters/{char_dir}"
        return None

    def _ffmpeg_concat(self, inputs: list[Path], out_path: Path) -> None:
        """Concatenate `inputs` into `out_path` as a uniform 9:16 reel with audio.

        Implementation note: the previous version used the concat *demuxer*
        (`-f concat -safe 0 -i list.txt`). That assumes inputs share
        resolution / timebase / sample-rate; mismatched character mp4s
        produced A/V drift (audio finished while video froze on the last
        frame of a segment). This version uses the concat *filter* via
        `-filter_complex`, which normalises each input through
        `trim → setpts → scale → pad → setsar → fps` for video and
        `atrim → asetpts → aresample → aformat` for audio, so heterogeneous
        sources stitch cleanly. Each input is trimmed to the first
        `_CONCAT_SEGMENT_S` seconds (default 2s).

        Audio handling: each source is probed for an Audio stream by parsing
        `ffmpeg -i` stderr. Inputs with audio contribute their real audio
        (trimmed + resampled to 44.1 kHz stereo). Inputs without audio
        contribute a `-f lavfi -i anullsrc` silent track of the same length,
        so the concat filter (`a=1`) sees an audio stream for every segment.
        Final encode: H.264 + AAC + faststart.
        """
        try:
            ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        except Exception as exc:
            raise FfmpegMissing(str(exc)) from exc

        n = len(inputs)
        has_audio = [self._probe_has_audio(ffmpeg, src) for src in inputs]
        need_null_source = not all(has_audio)
        null_idx = n  # index of the lavfi anullsrc input, if added

        per_segment: list[str] = []
        for i in range(n):
            per_segment.append(
                f"[{i}:v]"
                f"trim=duration={_CONCAT_SEGMENT_S},"
                f"setpts=PTS-STARTPTS,"
                f"scale={_CONCAT_TARGET_W}:{_CONCAT_TARGET_H}:force_original_aspect_ratio=decrease,"
                f"pad={_CONCAT_TARGET_W}:{_CONCAT_TARGET_H}:(ow-iw)/2:(oh-ih)/2:black,"
                f"setsar=1,"
                f"fps={_CONCAT_TARGET_FPS}"
                f"[v{i}]"
            )
            audio_src_idx = i if has_audio[i] else null_idx
            per_segment.append(
                f"[{audio_src_idx}:a]"
                f"atrim=duration={_CONCAT_SEGMENT_S},"
                f"asetpts=PTS-STARTPTS,"
                f"aresample=44100,"
                f"aformat=sample_fmts=fltp:channel_layouts=stereo"
                f"[a{i}]"
            )
        concat_pads = "".join(f"[v{i}][a{i}]" for i in range(n))
        concat_node = f"{concat_pads}concat=n={n}:v=1:a=1[outv][outa]"
        filter_complex = ";".join([*per_segment, concat_node])

        cmd: list[str] = [ffmpeg, "-y"]
        for src in inputs:
            cmd.extend(["-i", str(src)])
        if need_null_source:
            cmd.extend([
                "-f", "lavfi",
                "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
            ])
        cmd.extend([
            "-filter_complex", filter_complex,
            "-map", "[outv]",
            "-map", "[outa]",
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "128k",
            "-ar", "44100",
            "-ac", "2",
            "-movflags", "+faststart",
            "-loglevel", "error",
            str(out_path),
        ])

        try:
            completed = subprocess.run(
                cmd,
                capture_output=True,
                timeout=_CONCAT_FFMPEG_TIMEOUT_S,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise ConcatFailed("ffmpeg_timeout") from exc
        if completed.returncode != 0 or not out_path.is_file():
            err = completed.stderr.decode("utf-8", errors="replace").strip()[:400]
            raise ConcatFailed(err or "ffmpeg_failed")

    @staticmethod
    def _probe_has_audio(ffmpeg: str, src: Path) -> bool:
        """Return True iff `src` carries at least one Audio stream.

        `imageio_ffmpeg` doesn't bundle ffprobe, so probe via `ffmpeg -i`
        with no output target — ffmpeg dumps stream metadata to stderr and
        exits non-zero (no output), which is fine for our purpose.
        """
        try:
            result = subprocess.run(
                [ffmpeg, "-i", str(src), "-hide_banner"],
                capture_output=True,
                timeout=15,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return False
        stderr = result.stderr.decode("utf-8", errors="replace")
        for line in stderr.splitlines():
            stripped = line.strip()
            if stripped.startswith("Stream #") and "Audio:" in stripped:
                return True
        return False

    def _rel(self, p: Path) -> str:
        try:
            return p.resolve().relative_to(self._resolver.root).as_posix()
        except (OSError, ValueError):
            return p.as_posix()


def _split_md_row(line: str) -> list[str]:
    stripped = line.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    return [c.strip() for c in stripped.split("|")]


def _unwrap_inline_code(cell: str) -> str:
    s = cell.strip()
    if len(s) >= 2 and s.startswith("`") and s.endswith("`"):
        return s[1:-1]
    return s


# --- View + audio extraction (Feature 3, per follow-up 093) -----------------


_VIEW_FFMPEG_TIMEOUT_S: int = 30
_AUDIO_FFMPEG_TIMEOUT_S: int = 60
_VIEWS_SUBDIR: str = "views"
_AUDIO_MP3_QUALITY: str = "4"  # libmp3lame VBR ~165 kbps — small, transparent for speech


@dataclass(frozen=True)
class ViewResult:
    timestamp: float
    role: str
    out_rel: str

    def to_payload(self) -> dict[str, object]:
        return {"timestamp": self.timestamp, "role": self.role, "path": self.out_rel}


@dataclass(frozen=True)
class AudioResult:
    out_rel: str

    def to_payload(self) -> dict[str, object]:
        return {"path": self.out_rel}


@dataclass(frozen=True)
class ViewExtractResult:
    src_rel: str
    views: tuple[ViewResult, ...]
    audio: AudioResult | None
    failures: tuple[tuple[str, str], ...]  # (target, error_msg) where target is "front"/"side"/"back"/"audio"

    def to_payload(self) -> dict[str, object]:
        return {
            "src": self.src_rel,
            "views": [v.to_payload() for v in self.views],
            "audio": self.audio.to_payload() if self.audio is not None else None,
            "failures": [{"target": t, "error": e} for (t, e) in self.failures],
        }


class CharacterViewExtractor:
    """Extracts 3 angle PNGs (front/side/back) + the full audio (mp3) from a
    v9 character turntable mp4. Outputs land in `{src.parent}/views/` with
    `{src.parent.name}_{role}.png` + `{src.parent.name}_audio.mp3` naming so
    re-extraction in the same character folder overwrites the same outputs
    regardless of mp4 stem (the latest extraction is the single source of
    truth in `views/`).

    Per follow-up 093. The 3 timestamps live in
    `libs/domain/value_objects/character_video__valueobject.py` and are
    pinned to rule #12.5 v9's camera path.
    """

    def __init__(self, exposed: ExposedTree, resolver: SafeResolver) -> None:
        self._exposed = exposed
        self._resolver = resolver

    def extract(self, rel: str) -> ViewExtractResult:
        src = self._validate_character_video_source(rel)
        try:
            ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        except Exception as exc:
            raise FfmpegMissing(str(exc)) from exc
        prefix = src.parent.name
        out_dir = src.parent / _VIEWS_SUBDIR
        try:
            out_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise ViewExtractFailed(f"could not create views dir: {exc}") from exc
        self._sweep_outputs(out_dir)
        views: list[ViewResult] = []
        failures: list[tuple[str, str]] = []
        for spec in CANONICAL_VIEWS:
            out_path = out_dir / view_output_filename(prefix, spec)
            ok, err = self._run_view(ffmpeg, src, spec.timestamp, out_path)
            if ok:
                views.append(
                    ViewResult(
                        timestamp=spec.timestamp,
                        role=spec.role,
                        out_rel=self._rel(out_path),
                    )
                )
            else:
                failures.append((spec.role, err))
        audio_path = out_dir / audio_output_filename(prefix)
        audio: AudioResult | None
        ok, err = self._run_audio(ffmpeg, src, audio_path)
        if ok:
            audio = AudioResult(out_rel=self._rel(audio_path))
        else:
            audio = None
            failures.append(("audio", err))
        if not views and audio is None:
            joined = "; ".join(f"{tgt}: {e}" for (tgt, e) in failures)
            raise ViewExtractFailed(joined or "no outputs produced")
        return ViewExtractResult(
            src_rel=self._rel(src),
            views=tuple(views),
            audio=audio,
            failures=tuple(failures),
        )

    def _run_view(
        self,
        ffmpeg: str,
        src: Path,
        timestamp: float,
        out_path: Path,
    ) -> tuple[bool, str]:
        cmd = [
            ffmpeg,
            "-y",
            "-ss", f"{timestamp}",
            "-i", str(src),
            "-frames:v", "1",
            "-q:v", "1",
            "-loglevel", "error",
            str(out_path),
        ]
        try:
            completed = subprocess.run(
                cmd,
                capture_output=True,
                timeout=_VIEW_FFMPEG_TIMEOUT_S,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return False, "ffmpeg_timeout"
        if completed.returncode != 0 or not out_path.is_file():
            err = completed.stderr.decode("utf-8", errors="replace").strip()[:200]
            return False, err or "ffmpeg_failed"
        return True, ""

    def _run_audio(
        self,
        ffmpeg: str,
        src: Path,
        out_path: Path,
    ) -> tuple[bool, str]:
        cmd = [
            ffmpeg,
            "-y",
            "-i", str(src),
            "-vn",
            "-c:a", "libmp3lame",
            "-q:a", _AUDIO_MP3_QUALITY,
            "-loglevel", "error",
            str(out_path),
        ]
        try:
            completed = subprocess.run(
                cmd,
                capture_output=True,
                timeout=_AUDIO_FFMPEG_TIMEOUT_S,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return False, "ffmpeg_timeout"
        if completed.returncode != 0 or not out_path.is_file():
            err = completed.stderr.decode("utf-8", errors="replace").strip()[:200]
            return False, err or "ffmpeg_failed"
        return True, ""

    def _sweep_outputs(self, views_dir: Path) -> None:
        try:
            entries = list(views_dir.iterdir())
        except OSError:
            return
        for entry in entries:
            if entry.is_symlink() or not entry.is_file():
                continue
            suffix = entry.suffix.lower()
            if suffix not in (".png", ".mp3"):
                continue
            try:
                entry.unlink()
            except OSError:
                continue

    def _validate_character_video_source(self, rel: str) -> Path:
        if not isinstance(rel, str) or rel == "":
            raise InvalidPath("path is empty")
        if not self._exposed.is_inside(rel):
            raise InvalidPath("path outside sandbox")
        ext = Path(rel).suffix.lower()
        if ext not in VIDEO_EXTENSIONS:
            raise NotCharacterVideo("extension is not a video type")
        if not CharacterVideoTruncator._is_under_character_folder(rel):
            raise NotCharacterVideo(
                "path must be under ai_videos/{drama}/characters/{cN_xxx}/"
            )
        resolved = self._resolver.resolve(rel)
        if resolved is None:
            raise InvalidPath("path failed sandbox resolution")
        if resolved.is_symlink():
            raise InvalidPath("symlink is not allowed")
        if not resolved.is_file():
            raise NotFound("file does not exist")
        return resolved

    def _rel(self, p: Path) -> str:
        try:
            return p.resolve().relative_to(self._resolver.root).as_posix()
        except (OSError, ValueError):
            return p.as_posix()
