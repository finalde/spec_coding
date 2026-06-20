"""Burn per-shot dialogue subtitles into a rendered shot mp4, and scaffold
the per-shot `subtitles.md` dialogue-timeline file.

Layout contract (per `.claude/agent_refs/project/ai_video.md`): a shot lives
at `…/shots/shot{NN}/`, holding `shot{NN}.md` plus one or more rendered takes
under `…/shots/shot{NN}/renders/`. The dialogue timeline is a single
`…/shots/shot{NN}/subtitles.md` shared by every take.

`burn(rel, lang)` takes a render mp4, finds the sibling `subtitles.md`, parses
its bilingual cues, renders an ASS script in the requested language mode
(zh / en / both), and burns it via ffmpeg into a stable per-shot master named
`shot{NN}_{zh|en|zhen}.mp4` in the shot-folder root (originals untouched). Any
imported take can be burned; the language master name is fixed so a re-burn
overwrites it, and episode concat selects masters by language.

`scaffold(rel)` writes a starter bilingual `subtitles.md` from the shot's
`shot{NN}.md`. Each spoken `台词:` line is segmented into short phrases (split
on Chinese/Latin punctuation, long punctuation-free runs hard-capped) and the
shot's `时长:` is distributed across all phrases proportional to character
count (≈ constant speaking rate). This yields phrase-level cues that advance as
the line is spoken — instead of one whole line sitting on screen for the entire
window — each seeded as `中文 || ` with an empty English slot for the author to
fine-tune.

ffmpeg binary is supplied by the `imageio-ffmpeg` wheel — no system install.
"""
from __future__ import annotations

import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

import imageio_ffmpeg

from libs.common.exposed_tree import ExposedTree
from libs.common.safe_resolve import SafeResolver
from libs.domain.errors.frame__error import (
    FfmpegMissingError,
    InvalidVideoPathError,
    NotVideoError,
    VideoNotFoundError,
)
from libs.domain.errors.subtitle__error import (
    BurnFailedError,
    EmptySubtitlesError,
    InvalidSubtitleLangError,
    SubtitleFileMissingError,
)
from libs.domain.value_objects.subtitle__valueobject import (
    VALID_LANGS,
    cues_to_ass,
    has_text_for,
    parse_subtitles,
)

# burn-mode lang -> output filename suffix
_LANG_SUFFIX: dict[str, str] = {"zh": "zh", "en": "en", "both": "zhen"}

VIDEO_EXTENSIONS: frozenset[str] = frozenset(
    {".mp4", ".mov", ".webm", ".mkv", ".avi", ".m4v"}
)
RENDERS_DIR_NAME: str = "renders"
_SHOT_DIR_RE = re.compile(r"^shot\d+$", re.IGNORECASE)
SUBTITLE_FILE_NAME: str = "subtitles.md"
_FFMPEG_TIMEOUT_S: int = 300

_QUOTE_RE = re.compile(r"[\"“]([^\"”]+)[\"”]")
_DURATION_RE = re.compile(r"(\d+(?:\.\d+)?)")

# Phrase segmentation for speech-synced cues: break a spoken line at Chinese /
# Latin punctuation and whitespace, then hard-cap any punctuation-free run so a
# long unpunctuated line still advances. Trailing punctuation is dropped from
# each phrase (subtitles read cleaner without it).
_PHRASE_SPLIT_RE = re.compile(r"[，。！？；：、,.!?;:…—\-\s]+")
_MAX_PHRASE_CHARS: int = 18


def _split_phrases(text: str) -> list[str]:
    phrases: list[str] = []
    for seg in _PHRASE_SPLIT_RE.split(text):
        seg = seg.strip()
        if not seg:
            continue
        if len(seg) <= _MAX_PHRASE_CHARS:
            phrases.append(seg)
            continue
        # Hard-cap long punctuation-free runs into balanced chunks.
        n_chunks = -(-len(seg) // _MAX_PHRASE_CHARS)
        per = -(-len(seg) // n_chunks)
        for i in range(0, len(seg), per):
            chunk = seg[i:i + per].strip()
            if chunk:
                phrases.append(chunk)
    return phrases


@dataclass(frozen=True)
class BurnResult:
    src_rel: str
    out_rel: str
    cue_count: int
    lang: str


@dataclass(frozen=True)
class ScaffoldResult:
    md_rel: str
    cue_count: int
    created: bool


class SubtitleBurner:
    def __init__(self, exposed: ExposedTree, resolver: SafeResolver) -> None:
        self._exposed = exposed
        self._resolver = resolver

    def burn(self, rel: str, lang: str = "zh") -> BurnResult:
        if lang not in VALID_LANGS:
            raise InvalidSubtitleLangError(lang)
        src = self._validate_video_source(rel)
        shot_folder = self._shot_folder(src)
        sub_md = shot_folder / SUBTITLE_FILE_NAME
        if not sub_md.is_file():
            raise SubtitleFileMissingError(self._rel(sub_md))
        cues = parse_subtitles(sub_md.read_text(encoding="utf-8"))
        if not cues or not has_text_for(cues, lang):
            raise EmptySubtitlesError(self._rel(sub_md))
        try:
            ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        except Exception as exc:  # imageio_ffmpeg raises various on failure
            raise FfmpegMissingError(str(exc)) from exc
        # Canonical per-shot, per-language master in the shot-folder ROOT
        # (not next to the chosen raw take): `shot{NN}_{zh|en|zhen}.mp4`. Any of
        # the shot's imported takes can be burned; the output name is stable, so
        # re-burning overwrites the same language master. Episode concat then
        # picks these by language.
        out_path = shot_folder / f"{shot_folder.name}_{_LANG_SUFFIX[lang]}.mp4"
        with tempfile.TemporaryDirectory() as tmp:
            ass_path = Path(tmp) / "sub.ass"
            ass_path.write_text(cues_to_ass(cues, lang), encoding="utf-8")
            cmd = [
                ffmpeg,
                "-y",
                "-i", str(src),
                "-vf", "subtitles=sub.ass",  # bare name; cwd=tmp avoids Win path escaping
                "-c:a", "copy",
                "-c:v", "libx264",
                "-preset", "veryfast",
                "-crf", "18",
                "-loglevel", "error",
                str(out_path),
            ]
            try:
                completed = subprocess.run(
                    cmd,
                    cwd=tmp,
                    capture_output=True,
                    timeout=_FFMPEG_TIMEOUT_S,
                    check=False,
                )
            except subprocess.TimeoutExpired as exc:
                raise BurnFailedError("ffmpeg_timeout") from exc
        if completed.returncode != 0 or not out_path.is_file():
            err = completed.stderr.decode("utf-8", errors="replace").strip()[:300]
            raise BurnFailedError(err or "ffmpeg_failed")
        return BurnResult(
            src_rel=self._rel(src),
            out_rel=self._rel(out_path),
            cue_count=len(cues),
            lang=lang,
        )

    def scaffold(self, rel: str) -> ScaffoldResult:
        src = self._validate_video_source(rel)
        return self.scaffold_folder(self._shot_folder(src))

    def scaffold_folder(self, shot_folder: Path) -> ScaffoldResult:
        """(Re)write `subtitles.md` for a shot folder from its `shot{NN}.md`.

        Always overwrites — a second call regenerates rather than failing. Used
        directly by per-shot scaffolding and by batch episode scaffolding (no
        render mp4 needed; the timeline is derived from `shot{NN}.md`)."""
        sub_md = shot_folder / SUBTITLE_FILE_NAME
        existed = sub_md.is_file() and bool(sub_md.read_text(encoding="utf-8").strip())
        duration, lines = self._read_shot_dialogue(shot_folder)
        phrases: list[str] = []
        for line in lines:
            phrases.extend(_split_phrases(line))
        body = self._build_scaffold(shot_folder.name, duration, phrases)
        sub_md.write_text(body, encoding="utf-8")
        return ScaffoldResult(
            md_rel=self._rel(sub_md),
            cue_count=len(phrases) or 1,
            created=not existed,
        )

    def spoken_lines(self, shot_folder: Path) -> list[str]:
        """The clean spoken `台词:` lines for a shot (empty if the shot is
        silent). Batch scaffolding uses this to skip dialogue-free shots."""
        _, lines = self._read_shot_dialogue(shot_folder)
        return lines

    def _shot_folder(self, src: Path) -> Path:
        """The shot ROOT folder (`…/shotNN`). Burned language masters land here,
        NEVER under `renders/` (which holds the untouched originals). Resolve to
        the nearest `shotNN` ancestor so a render nested anywhere under
        `renders/` still maps to the shot root."""
        for anc in (src.parent, *src.parent.parents):
            if _SHOT_DIR_RE.match(anc.name):
                return anc
        if src.parent.name == RENDERS_DIR_NAME:
            return src.parent.parent
        return src.parent

    def _read_shot_dialogue(self, shot_folder: Path) -> tuple[float, list[str]]:
        shot_md = shot_folder / f"{shot_folder.name}.md"
        if not shot_md.is_file():
            candidates = sorted(shot_folder.glob("shot*.md"))
            shot_md = candidates[0] if candidates else shot_md
        duration = 5.0
        lines: list[str] = []
        if shot_md.is_file():
            text = shot_md.read_text(encoding="utf-8")
            for raw in text.splitlines():
                stripped = raw.strip()
                if "时长:" in raw and "时长目标" not in raw:
                    m = _DURATION_RE.search(raw.split("时长:", 1)[1])
                    if m:
                        duration = float(m.group(1))
                # Prefer the clean spoken lines from the `## 台词配音` blocks
                # (`台词: 正文`). Skip the video-prompt `台词: （…paren note…）`.
                if stripped.startswith("台词:"):
                    val = stripped[len("台词:"):].strip()
                    if val and not val.startswith("（") and not val.startswith("("):
                        if val not in lines:
                            lines.append(val)
                # Fallback: quoted dialogue elsewhere (legacy shot.md shape).
                elif "台词" in raw:
                    for q in _QUOTE_RE.findall(raw):
                        cleaned = q.strip().strip("：:")
                        if cleaned and cleaned not in lines:
                            lines.append(cleaned)
        return duration, lines

    def _build_scaffold(
        self, shot_name: str, duration: float, phrases: list[str]
    ) -> str:
        head = (
            f"# {shot_name} 双语台词时间轴\n\n"
            "> 每行一句: `起-止(秒) 中文 || English`。`||` 左为中文、右为英文;\n"
            ">   只写中文(省略 `||`)则为中文单语。内心独白(OS)写法相同, 不单独区分样式。\n"
            "> 台词已按标点拆成短句、时间窗按字数估算(≈匀速), 字幕随说话推进逐句切换;\n"
            f"> 总时长 {self._fmt(duration)}s, 请按真实语速逐句微调起止。\n"
            "> render 卡片上的「💬中文 / 💬英文 / 💬中英」可分别烧出对应语言版本视频。\n\n"
            "```text\n"
        )
        cue_lines: list[str] = []
        if phrases:
            total_chars = sum(len(p) for p in phrases) or 1
            cursor = 0.0
            for i, text in enumerate(phrases):
                start = round(cursor, 2)
                if i == len(phrases) - 1:
                    end = duration
                else:
                    end = round(cursor + duration * len(text) / total_chars, 2)
                    if end <= start:  # guard against zero-width windows
                        end = round(start + 0.1, 2)
                cue_lines.append(f"{self._fmt(start)}-{self._fmt(end)}  {text} || ")
                cursor = end
        else:
            cue_lines.append(f"0-{self._fmt(duration)}  （在此填写中文台词） || (English here)")
        return head + "\n".join(cue_lines) + "\n```\n"

    @staticmethod
    def _fmt(value: float) -> str:
        return str(int(value)) if float(value).is_integer() else str(value)

    def _validate_video_source(self, rel: str) -> Path:
        if not isinstance(rel, str) or rel == "":
            raise InvalidVideoPathError("path is empty")
        if not self._exposed.is_inside(rel):
            raise VideoNotFoundError("path outside sandbox")
        ext = Path(rel).suffix.lower()
        if ext not in VIDEO_EXTENSIONS:
            raise NotVideoError("extension is not a video type")
        resolved = self._resolver.resolve(rel)
        if resolved is None or not resolved.is_file():
            raise VideoNotFoundError("file does not exist")
        if resolved.is_symlink():
            raise VideoNotFoundError("symlink is not allowed")
        return resolved

    def _rel(self, p: Path) -> str:
        try:
            return p.resolve().relative_to(self._resolver.root).as_posix()
        except (OSError, ValueError):
            return p.as_posix()
