"""Burn character intro cards into a shot render (ai_video.md rule 11d).

For each card the shot has in its episode's `intro_cards.md`, a framed corner
nameplate (主名 + 副身份, mounted in a gold frame, top-left/right) fades in over
the MOVING footage at the card's appear-time and fades out — the video is NOT
frozen, it keeps playing smoothly. Output is the shot's finished video
`shot{NN}.mp4` in the shot-folder ROOT — never under `renders/` (which keeps the
original takes untouched); a re-burn overwrites it.

Layout: a shot lives at `…/episodes/ep{NN}/shots/shot{NN}/`; the card spec is
the episode-level `…/episodes/ep{NN}/intro_cards.md`. ffmpeg binary comes from
the `imageio-ffmpeg` wheel — no system install.
"""
from __future__ import annotations

import re
import shutil
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
from libs.domain.errors.intro_card__error import (
    IntroCardBurnFailedError,
    IntroCardsFileMissingError,
    NoCardForShotError,
)
from libs.domain.value_objects.intro_card__valueobject import (
    cards_for_shot,
    cards_to_ass,
    parse_intro_cards,
)

VIDEO_EXTENSIONS: frozenset[str] = frozenset(
    {".mp4", ".mov", ".webm", ".mkv", ".avi", ".m4v"}
)
RENDERS_DIR_NAME: str = "renders"
INTRO_CARDS_FILE_NAME: str = "intro_cards.md"
_EP_DIR_RE = re.compile(r"^ep\d+$", re.IGNORECASE)
_SHOT_DIR_RE = re.compile(r"^shot\d+$", re.IGNORECASE)
_FFMPEG_TIMEOUT_S: int = 300


@dataclass(frozen=True)
class IntroCardBurnResult:
    src_rel: str
    out_rel: str
    card_count: int
    names: tuple[str, ...]


class IntroCardBurner:
    def __init__(self, exposed: ExposedTree, resolver: SafeResolver) -> None:
        self._exposed = exposed
        self._resolver = resolver

    def burn(self, rel: str) -> IntroCardBurnResult:
        src = self._validate_video_source(rel)
        shot_folder = self._shot_folder(src)
        episode_dir = self._episode_dir(shot_folder)
        cards_md = episode_dir / INTRO_CARDS_FILE_NAME
        if not cards_md.is_file():
            raise IntroCardsFileMissingError(self._rel(cards_md))
        cards = cards_for_shot(
            parse_intro_cards(cards_md.read_text(encoding="utf-8")), shot_folder.name
        )
        if not cards:
            raise NoCardForShotError(shot_folder.name)
        try:
            ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        except Exception as exc:
            raise FfmpegMissingError(str(exc)) from exc
        # Output is the shot's finished video in the shot ROOT — just
        # `shot{NN}.mp4` (never under renders/, which keeps the original takes).
        out_path = shot_folder / f"{shot_folder.name}.mp4"
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "cards.ass").write_text(cards_to_ass(cards), encoding="utf-8")
            # Smooth overlay — the video is NOT frozen; the framed nameplate just
            # fades in over the moving footage. Video re-encoded, audio copied,
            # timeline unchanged. Render to tmp then move (a re-burn that reads
            # `shot{NN}.mp4` never reads+writes the same path).
            cmd = [
                ffmpeg, "-y", "-i", str(src),
                "-vf", "ass=cards.ass",  # bare name; cwd=tmp avoids Win path escaping
                "-c:a", "copy",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                "-loglevel", "error", "out.mp4",
            ]
            try:
                completed = subprocess.run(
                    cmd, cwd=tmp, capture_output=True,
                    timeout=_FFMPEG_TIMEOUT_S, check=False,
                )
            except subprocess.TimeoutExpired as exc:
                raise IntroCardBurnFailedError("ffmpeg_timeout") from exc
            tmp_out = Path(tmp) / "out.mp4"
            if completed.returncode != 0 or not tmp_out.is_file():
                err = completed.stderr.decode("utf-8", errors="replace").strip()[:300]
                raise IntroCardBurnFailedError(err or "ffmpeg_failed")
            shutil.move(str(tmp_out), str(out_path))
        return IntroCardBurnResult(
            src_rel=self._rel(src),
            out_rel=self._rel(out_path),
            card_count=len(cards),
            names=tuple(c.main or c.sub for c in cards),
        )

    def _shot_folder(self, src: Path) -> Path:
        """The shot ROOT folder (`…/shotNN`). Output masters land here, NEVER
        under `renders/` (which holds the untouched originals). Resolve to the
        nearest `shotNN` ancestor so a render nested anywhere under `renders/`
        still maps to the shot root."""
        for anc in (src.parent, *src.parent.parents):
            if _SHOT_DIR_RE.match(anc.name):
                return anc
        if src.parent.name == RENDERS_DIR_NAME:
            return src.parent.parent
        return src.parent

    def _episode_dir(self, shot_folder: Path) -> Path:
        # shot_folder = …/episodes/ep{NN}/shots/shot{NN}; episode dir is 2 up.
        for anc in shot_folder.parents:
            if _EP_DIR_RE.match(anc.name):
                return anc
        # fallback: shots/ parent
        return shot_folder.parent.parent

    def _validate_video_source(self, rel: str) -> Path:
        if not isinstance(rel, str) or rel == "":
            raise InvalidVideoPathError("path is empty")
        if not self._exposed.is_inside(rel):
            raise VideoNotFoundError("path outside sandbox")
        if Path(rel).suffix.lower() not in VIDEO_EXTENSIONS:
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
