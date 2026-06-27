"""Whole-episode subtitle burn (follow-up 147, step 3 of 3).

Burns ONE subtitle track onto the clean stitched `ep{NN}.mp4` — never per shot
then concatenated (that re-encoded the burned subs and the seam trims shifted
their timeline → misalignment). Each shot's cues are placed at their TRUE offset
in the final reel, read from `ep{NN}.segments.json` (written by concat): a
segment's cues are generated on a 0..dur_s axis (SubtitleBurner.segment_cues,
re-timed to the segment's real post-trim length) then shifted by its start_s.

Output `ep{NN}_{zh|en|zhen}.mp4` next to the episode markdown. ffmpeg binary
from imageio-ffmpeg.
"""
from __future__ import annotations

import json
import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

import imageio_ffmpeg

from libs.common.exposed_tree import ExposedTree
from libs.common.safe_resolve import SafeResolver
from libs.domain.errors.frame__error import FfmpegMissingError
from libs.domain.errors.subtitle__error import (
    BurnFailedError,
    EmptySubtitlesError,
    EpisodeNotConcatenatedError,
    InvalidBatchScopeError,
    InvalidSubtitleLangError,
    NoEpisodeVideoError,
)
from libs.domain.value_objects.subtitle__valueobject import (
    VALID_LANGS,
    SubtitleCue,
    cues_to_ass,
    has_text_for,
)
from libs.infrastructure.writers.subtitle__writer import SubtitleBurner

_EP_DIR_RE = re.compile(r"^ep\d+$", re.IGNORECASE)
_LANG_SUFFIX: dict[str, str] = {"zh": "zh", "en": "en", "both": "zhen"}
_FFMPEG_TIMEOUT_S: int = 600


@dataclass(frozen=True)
class EpisodeWholeBurnResult:
    episode_rel: str
    out_rel: str
    lang: str
    cue_count: int
    shot_count: int

    def to_payload(self) -> dict[str, object]:
        return {
            "episode": self.episode_rel,
            "out": self.out_rel,
            "lang": self.lang,
            "cues": self.cue_count,
            "shots": self.shot_count,
        }


class EpisodeSubtitleBurner:
    def __init__(
        self, exposed: ExposedTree, resolver: SafeResolver, burner: SubtitleBurner
    ) -> None:
        self._exposed = exposed
        self._resolver = resolver
        self._burner = burner

    def burn_whole(self, rel: str, lang: str = "zh") -> EpisodeWholeBurnResult:
        if lang not in VALID_LANGS:
            raise InvalidSubtitleLangError(lang)
        episode_dir, slug = self._episode_dir(rel)
        ep_mp4 = episode_dir / f"{slug}.mp4"
        if not ep_mp4.is_file():
            raise NoEpisodeVideoError(self._rel(ep_mp4))
        seg_json = episode_dir / f"{slug}.segments.json"
        if not seg_json.is_file():
            raise EpisodeNotConcatenatedError(self._rel(seg_json))
        segments = self._read_segments(seg_json)
        cue_tuple, shots_with_cues = self.assemble_cues(episode_dir / "shots", segments)
        if not cue_tuple or not has_text_for(cue_tuple, lang):
            raise EmptySubtitlesError(self._rel(seg_json))
        out_path = episode_dir / f"{slug}_{_LANG_SUFFIX[lang]}.mp4"
        self._burn(ep_mp4, cue_tuple, lang, out_path)
        return EpisodeWholeBurnResult(
            episode_rel=self._rel(episode_dir),
            out_rel=self._rel(out_path),
            lang=lang,
            cue_count=len(cue_tuple),
            shot_count=shots_with_cues,
        )

    def assemble_cues(
        self, shots_dir: Path, segments: list[dict]
    ) -> tuple[tuple[SubtitleCue, ...], int]:
        """The whole-episode cue track: each shot's local cues (re-timed to its
        real segment duration) SHIFTED by that segment's start_s in the final
        reel. This is the offset that fixes the old misalignment. Returns
        (cues, number_of_shots_that_contributed_cues)."""
        cues: list[SubtitleCue] = []
        shots_with_cues = 0
        for seg in segments:
            seg_cues = self._burner.segment_cues(
                shots_dir / str(seg["shot"]), float(seg["dur_s"])
            )
            if not seg_cues:
                continue
            shots_with_cues += 1
            off = float(seg["start_s"])
            cues.extend(
                SubtitleCue(start=c.start + off, end=c.end + off, zh=c.zh, en=c.en)
                for c in seg_cues
            )
        return tuple(cues), shots_with_cues

    def _burn(
        self, src: Path, cues: tuple[SubtitleCue, ...], lang: str, out_path: Path
    ) -> None:
        try:
            ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        except Exception as exc:  # imageio_ffmpeg raises various on failure
            raise FfmpegMissingError(str(exc)) from exc
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "sub.ass").write_text(cues_to_ass(cues, lang), encoding="utf-8")
            cmd = [
                ffmpeg, "-y", "-i", str(src),
                "-vf", "subtitles=sub.ass",  # bare name; cwd=tmp avoids Win path escaping
                "-c:a", "copy", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                "-loglevel", "error", str(out_path),
            ]
            try:
                completed = subprocess.run(
                    cmd, cwd=tmp, capture_output=True,
                    timeout=_FFMPEG_TIMEOUT_S, check=False,
                )
            except subprocess.TimeoutExpired as exc:
                raise BurnFailedError("ffmpeg_timeout") from exc
        if completed.returncode != 0 or not out_path.is_file():
            err = completed.stderr.decode("utf-8", errors="replace").strip()[:300]
            raise BurnFailedError(err or "ffmpeg_failed")

    @staticmethod
    def _read_segments(seg_json: Path) -> list[dict]:
        try:
            data = json.loads(seg_json.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise EpisodeNotConcatenatedError(f"unreadable segments.json: {exc}") from exc
        segs = data.get("segments", [])
        if not isinstance(segs, list) or not segs:
            raise EpisodeNotConcatenatedError("segments.json has no segments")
        return segs

    def _episode_dir(self, rel: str) -> tuple[Path, str]:
        if not isinstance(rel, str) or rel == "":
            raise InvalidBatchScopeError("path is empty")
        if not self._exposed.is_inside(rel):
            raise InvalidBatchScopeError("path outside sandbox")
        parts = rel.split("/")
        if len(parts) < 4 or parts[0] != "ai_videos" or parts[1].startswith("_"):
            raise InvalidBatchScopeError("path is not under ai_videos/{drama}/")
        try:
            ep_idx = next(
                i for i in range(1, len(parts) - 1)
                if parts[i] == "episodes" and _EP_DIR_RE.match(parts[i + 1])
            )
        except StopIteration as exc:
            raise InvalidBatchScopeError("path is not under episodes/ep{NN}/") from exc
        resolved = self._resolver.resolve("/".join(parts[: ep_idx + 2]))
        if resolved is None or resolved.is_symlink() or not resolved.is_dir():
            raise InvalidBatchScopeError("episode path failed sandbox resolution")
        return resolved, parts[ep_idx + 1].lower()

    def _rel(self, p: Path) -> str:
        try:
            return p.resolve().relative_to(self._resolver.root).as_posix()
        except (OSError, ValueError):
            return p.as_posix()
