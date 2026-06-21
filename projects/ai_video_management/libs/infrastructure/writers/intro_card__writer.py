"""Burn character intro cards into a shot render (ai_video.md rule 11d).

Each card is a complete per-character nameplate PNG (透明底, designed in Kling)
from the global library `ai_videos/_intro_cards/`. The burn composites that PNG
onto the shot's top corner (right/left) with a fade in/out over the MOVING
footage — the video is not frozen, nothing is drawn programmatically. Output is
the shot's finished video `shot{NN}.mp4` in the shot-folder ROOT (never under
`renders/`, which keeps the originals); a re-burn overwrites it.

Layout: a shot lives at `…/episodes/ep{NN}/shots/shot{NN}/`; the card spec is
the episode-level `…/episodes/ep{NN}/intro_cards.md`. ffmpeg comes from the
`imageio-ffmpeg` wheel — no system install.
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
    IntroCardImageMissingError,
    IntroCardsFileMissingError,
    NoCardForShotError,
)
from libs.domain.value_objects.intro_card__valueobject import (
    IntroCard,
    cards_for_shot,
    parse_intro_cards,
)

VIDEO_EXTENSIONS: frozenset[str] = frozenset(
    {".mp4", ".mov", ".webm", ".mkv", ".avi", ".m4v"}
)
RENDERS_DIR_NAME: str = "renders"
INTRO_CARDS_FILE_NAME: str = "intro_cards.md"
_IMAGE_EXTS: tuple[str, ...] = (".png", ".webp", ".jpg", ".jpeg")
_EP_DIR_RE = re.compile(r"^ep\d+$", re.IGNORECASE)
_SHOT_DIR_RE = re.compile(r"^shot\d+$", re.IGNORECASE)
_FFMPEG_TIMEOUT_S: int = 300
_FADE_S: float = 0.35
_MARGIN_FRAC: float = 0.035       # corner gap as a fraction of video width
# Many user cards are generated on a black background (the prompt allows it for
# easy keying) and/or sit in a wide empty frame. Auto-crop to the content bbox
# then key near-black to transparent, so the card composites as a clean
# transparent nameplate rather than a black box.
_BLACK_KEY: str = "colorkey=0x000000:0.18:0.12"
_STREAM_RE = re.compile(r"Stream #.*Video:.* (\d{2,5})x(\d{2,5})")
_DURATION_RE = re.compile(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)")
_CROP_RE = re.compile(r"crop=(\d+:\d+:\d+:\d+)")


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
        drama_root = self._drama_root(shot_folder)
        images = [self._resolve_card_image(c, drama_root) for c in cards]
        try:
            ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        except Exception as exc:
            raise FfmpegMissingError(str(exc)) from exc
        width, duration = self._probe_dims(ffmpeg, src)
        crops = [self._detect_crop(ffmpeg, img) for img in images]
        out_path = shot_folder / f"{shot_folder.name}.mp4"
        with tempfile.TemporaryDirectory() as tmp:
            cmd = [ffmpeg, "-y", "-i", str(src)]
            for img in images:
                # `-t` bounds the looped image to the clip so ffmpeg terminates.
                cmd += ["-loop", "1", "-t", f"{duration:.3f}", "-i", str(img)]
            cmd += ["-filter_complex", self._build_filter(cards, width, crops),
                    "-map", "[v]", "-map", "0:a?", "-c:a", "copy",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                    "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                    # looped image inputs are infinite — bound output to the video.
                    "-shortest", "-loglevel", "error", "out.mp4"]
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
            names=tuple(c.label or c.image_ref for c in cards),
        )

    def _build_filter(
        self, cards: tuple[IntroCard, ...], width: int, crops: list[str | None]
    ) -> str:
        """Per card: auto-crop to the nameplate bbox (drops black border / empty
        frame), key near-black to transparent, scale to `width_frac * video
        width`, fade in/out (alpha fade hides it outside its window), and overlay
        at the top-left / top-right corner. Cards chain onto each other."""
        margin = max(8, round(width * _MARGIN_FRAC))
        chains: list[str] = []
        for i, c in enumerate(cards):
            ow = max(40, round(width * c.width_frac))
            out_start = round(c.at + c.duration - _FADE_S, 2)
            pre = f"crop={crops[i]}," if crops[i] else ""
            chains.append(
                f"[{i + 1}:v]{pre}format=rgba,{_BLACK_KEY},scale={ow}:-1,"
                f"fade=t=in:st={c.at}:d={_FADE_S}:alpha=1,"
                f"fade=t=out:st={out_start}:d={_FADE_S}:alpha=1[c{i}]"
            )
        base = "[0:v]"
        for i, c in enumerate(cards):
            x = f"{margin}" if c.corner == "tl" else f"main_w-overlay_w-{margin}"
            out = "[v]" if i == len(cards) - 1 else f"[b{i}]"
            chains.append(f"{base}[c{i}]overlay=x={x}:y={margin}{out}")
            base = f"[b{i}]"
        return ";".join(chains)

    def _resolve_card_image(self, card: IntroCard, drama_root: Path) -> Path:
        """Resolve the card's raw `卡图` ref against THIS drama:
        - full sandbox path (`ai_videos/…`) → used as-is;
        - any other path → relative to the drama root;
        - a bare id (`裴知秋`) → found under the drama's `intro_cards/` folder."""
        ref = card.image_ref
        if "/" not in ref:
            found = self._find_card_in_drama(drama_root, ref)
            if found is not None:
                return found
            raise IntroCardImageMissingError(ref)
        rel = ref if ref.startswith("ai_videos/") else f"{self._rel(drama_root)}/{ref}"
        if not rel.lower().endswith(_IMAGE_EXTS):
            rel = f"{rel}.png"
        if not self._exposed.is_inside(rel):
            raise IntroCardImageMissingError(ref)
        resolved = self._resolver.resolve(rel)
        if resolved is None or not resolved.is_file() or resolved.is_symlink():
            raise IntroCardImageMissingError(ref)
        return resolved

    @staticmethod
    def _find_card_in_drama(drama_root: Path, card_id: str) -> Path | None:
        """Find a character's intro card. Convention: the card lives INSIDE the
        character folder as `characters/{…角色名…}/intro_card.{ext}` (so no extra
        folder). `card_id` is the 角色 name (e.g. `裴知秋`) → its character
        folder (`c1_裴知秋`). Fallback: a literal `{card_id}.{ext}` anywhere."""
        try:
            for d in drama_root.rglob(f"*{card_id}*"):
                if (d.is_dir() and not d.is_symlink()
                        and d.parent.name == "characters"):
                    for e in _IMAGE_EXTS:
                        cand = d / f"intro_card{e}"
                        if cand.is_file() and not cand.is_symlink():
                            return cand
        except OSError:
            pass
        names = (
            [card_id] if card_id.lower().endswith(_IMAGE_EXTS)
            else [f"{card_id}{e}" for e in _IMAGE_EXTS]
        )
        for name in names:
            try:
                for cand in drama_root.rglob(name):
                    if cand.is_file() and not cand.is_symlink():
                        return cand
            except OSError:
                continue
        return None

    def _drama_root(self, shot_folder: Path) -> Path:
        for anc in shot_folder.parents:
            if anc.parent.name == "ai_videos":
                return anc
        return shot_folder

    @staticmethod
    def _detect_crop(ffmpeg: str, img: Path) -> str | None:
        """`crop=W:H:X:Y` of the card's non-black content bbox (so a black-bg or
        wide-framed card crops down to just the nameplate), or None."""
        try:
            result = subprocess.run(
                [ffmpeg, "-loop", "1", "-t", "0.3", "-i", str(img),
                 "-vf", "cropdetect=24:2:0", "-f", "null", "-"],
                capture_output=True, timeout=20, check=False,
            )
        except subprocess.TimeoutExpired:
            return None
        matches = _CROP_RE.findall(result.stderr.decode("utf-8", errors="replace"))
        return matches[-1] if matches else None

    @staticmethod
    def _probe_dims(ffmpeg: str, src: Path) -> tuple[int, float]:
        """(video width px, duration seconds) — defaults 1080 / 10s on failure."""
        try:
            result = subprocess.run(
                [ffmpeg, "-i", str(src), "-hide_banner"],
                capture_output=True, timeout=15, check=False,
            )
        except subprocess.TimeoutExpired:
            return 1080, 10.0
        out = result.stderr.decode("utf-8", errors="replace")
        wm = _STREAM_RE.search(out)
        width = int(wm.group(1)) if wm else 1080
        dm = _DURATION_RE.search(out)
        if dm:
            dur = int(dm.group(1)) * 3600 + int(dm.group(2)) * 60 + float(dm.group(3))
        else:
            dur = 10.0
        return width, max(0.1, dur)

    def _shot_folder(self, src: Path) -> Path:
        """The shot ROOT folder (`…/shotNN`). Output lands here, NEVER under
        `renders/`. Resolve to the nearest `shotNN` ancestor."""
        for anc in (src.parent, *src.parent.parents):
            if _SHOT_DIR_RE.match(anc.name):
                return anc
        if src.parent.name == RENDERS_DIR_NAME:
            return src.parent.parent
        return src.parent

    def _episode_dir(self, shot_folder: Path) -> Path:
        for anc in shot_folder.parents:
            if _EP_DIR_RE.match(anc.name):
                return anc
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
