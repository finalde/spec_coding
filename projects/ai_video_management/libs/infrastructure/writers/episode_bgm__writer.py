"""Episode-BGM manager: read / assign / burn a sparse BGM cue timeline.

The arrangement lives at `episodes/ep{NN}/bgm/bgm.md` (authored by the AI-video
pipeline — sparse: only the dramatic beats that want music). The user assigns a
shared-library `bgm_NNNN` to each cue slot (mirrors casting), then burns: each
assigned cue's mp3 is placed at its window on the episode timeline, optionally
ducked under the episode's own dialogue audio, and mixed over the SUBTITLED
master `ep{NN}_zh.mp4` (preserved, never touched) → `ep{NN}_zh_bgm.mp4`
(re-burn overwrites).

Assignment is a surgical line replace in `bgm.md` (line-oriented timeline, not a
markdown table — safe). The burn is one ffmpeg invocation with a filter graph
built from the assigned cues; the video stream is stream-copied (`-c:v copy`).

ffmpeg binary supplied by `imageio-ffmpeg` — no system install.
"""
from __future__ import annotations

import os
import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

import imageio_ffmpeg

from libs.common.exposed_tree import ExposedTree
from libs.common.safe_resolve import SafeResolver
from libs.domain.errors.episode_bgm__error import (
    BgmCueNotFoundError,
    BgmTrackAudioMissingError,
    EpisodeBgmCueFileMissingError,
    EpisodeBgmFfmpegMissingError,
    EpisodeBgmMuxFailedError,
    InvalidEpisodeBgmPathError,
    NoAssignedBgmCuesError,
    NotEpisodeBgmPathError,
    SubtitledEpisodeMissingError,
)
from libs.domain.value_objects.bgm__valueobject import validate_bgm_id
from libs.domain.value_objects.episode_bgm__valueobject import (
    BgmCue,
    parse_bgm_cues,
    parse_cue_line,
    serialize_cue,
)
from libs.infrastructure.writers.bgm__writer import BgmPool

_EP_DIR_RE = re.compile(r"^ep\d+$", re.IGNORECASE)
BGM_CUE_DIR_NAME: str = "bgm"
BGM_CUE_FILE_NAME: str = "bgm.md"
_SUBTITLED_SUFFIX: str = "_zh"
_OUTPUT_SUFFIX: str = "_zh_bgm"
_MP4_EXT: str = ".mp4"
_MUX_TIMEOUT_S: int = 900
_AUDIO_BITRATE: str = "192k"
_FADE_SECONDS: float = 1.0
# sidechaincompress duck params — mirror tools/mux_av.py defaults.
_DUCK = {"threshold": 0.03, "ratio": 8.0, "attack": 40.0, "release": 400.0}


@dataclass(frozen=True)
class EpisodeBgmReadResult:
    episode_rel: str
    cue_file_rel: str
    cue_file_exists: bool
    source_rel: str
    source_exists: bool
    output_rel: str
    output_exists: bool
    cues: tuple[BgmCue, ...]

    def to_payload(self) -> dict[str, object]:
        return {
            "episode": self.episode_rel,
            "cue_file": self.cue_file_rel,
            "cue_file_exists": self.cue_file_exists,
            "source": self.source_rel,
            "source_exists": self.source_exists,
            "output": self.output_rel,
            "output_exists": self.output_exists,
            "cues": [c.to_payload() for c in self.cues],
        }


@dataclass(frozen=True)
class BurnEpisodeBgmResult:
    episode_rel: str
    out_rel: str
    used: tuple[dict[str, object], ...]
    skipped: tuple[dict[str, object], ...]

    def to_payload(self) -> dict[str, object]:
        return {
            "episode": self.episode_rel,
            "out": self.out_rel,
            "used": list(self.used),
            "skipped": list(self.skipped),
        }


class EpisodeBgmManager:
    def __init__(
        self, exposed: ExposedTree, resolver: SafeResolver, bgm_pool: BgmPool
    ) -> None:
        self._exposed = exposed
        self._resolver = resolver
        self._bgm_pool = bgm_pool

    # ------------------------------------------------------------------ read
    def read(self, rel: str) -> EpisodeBgmReadResult:
        episode_dir, slug = self._validate_episode(rel)
        cue_file = episode_dir / BGM_CUE_DIR_NAME / BGM_CUE_FILE_NAME
        source = episode_dir / f"{slug}{_SUBTITLED_SUFFIX}{_MP4_EXT}"
        output = episode_dir / f"{slug}{_OUTPUT_SUFFIX}{_MP4_EXT}"
        cues: tuple[BgmCue, ...] = ()
        if cue_file.is_file():
            cues = tuple(parse_bgm_cues(cue_file.read_text(encoding="utf-8")))
        return EpisodeBgmReadResult(
            episode_rel=self._rel(episode_dir),
            cue_file_rel=self._rel(cue_file),
            cue_file_exists=cue_file.is_file(),
            source_rel=self._rel(source),
            source_exists=source.is_file(),
            output_rel=self._rel(output),
            output_exists=output.is_file(),
            cues=cues,
        )

    # ------------------------------------------------------------------ assign
    def assign(self, rel: str, start: float, end: float, bgm_id: str) -> EpisodeBgmReadResult:
        validate_bgm_id(bgm_id)
        if not self._bgm_pool.bgm_exists(bgm_id):
            raise BgmTrackAudioMissingError(f"{bgm_id} has no rendered mp3 in the library")
        self._rewrite_slot(rel, start, end, bgm_id)
        return self.read(rel)

    def unassign(self, rel: str, start: float, end: float) -> EpisodeBgmReadResult:
        self._rewrite_slot(rel, start, end, None)
        return self.read(rel)

    def _rewrite_slot(
        self, rel: str, start: float, end: float, bgm_id: str | None
    ) -> None:
        episode_dir, _slug = self._validate_episode(rel)
        cue_file = episode_dir / BGM_CUE_DIR_NAME / BGM_CUE_FILE_NAME
        if not cue_file.is_file():
            raise EpisodeBgmCueFileMissingError(self._rel(cue_file))
        lines = cue_file.read_text(encoding="utf-8").splitlines()
        out: list[str] = []
        matched = False
        for raw in lines:
            cue = parse_cue_line(raw)
            if (
                cue is not None
                and not matched
                and _same_window(cue.start, start)
                and _same_window(cue.end, end)
            ):
                indent = raw[: len(raw) - len(raw.lstrip())]
                updated = BgmCue(
                    start=cue.start,
                    end=cue.end,
                    category=cue.category,
                    bgm_id=bgm_id,
                    vol=cue.vol,
                    duck=cue.duck,
                    fade_in=cue.fade_in,
                    fade_out=cue.fade_out,
                    comment=cue.comment,
                )
                out.append(indent + serialize_cue(updated))
                matched = True
            else:
                out.append(raw)
        if not matched:
            raise BgmCueNotFoundError(f"no cue at window {start}-{end}")
        self._atomic_write(cue_file, "\n".join(out) + "\n")

    # ------------------------------------------------------------------ burn
    def burn(self, rel: str) -> BurnEpisodeBgmResult:
        episode_dir, slug = self._validate_episode(rel)
        cue_file = episode_dir / BGM_CUE_DIR_NAME / BGM_CUE_FILE_NAME
        if not cue_file.is_file():
            raise EpisodeBgmCueFileMissingError(self._rel(cue_file))
        source = episode_dir / f"{slug}{_SUBTITLED_SUFFIX}{_MP4_EXT}"
        if not source.is_file():
            raise SubtitledEpisodeMissingError(self._rel(source))
        cues = parse_bgm_cues(cue_file.read_text(encoding="utf-8"))

        resolved: list[tuple[BgmCue, Path]] = []
        skipped: list[dict[str, object]] = []
        for cue in cues:
            if cue.bgm_id is None:
                skipped.append({"window": f"{cue.start}-{cue.end}", "reason": "unassigned"})
                continue
            mp3 = self._bgm_pool.audio_path_for(cue.bgm_id)
            if mp3 is None:
                raise BgmTrackAudioMissingError(f"{cue.bgm_id} has no rendered mp3")
            resolved.append((cue, mp3))
        if not resolved:
            raise NoAssignedBgmCuesError("no assigned cue to mux")

        out_path = episode_dir / f"{slug}{_OUTPUT_SUFFIX}{_MP4_EXT}"
        self._mux(source, resolved, out_path)
        return BurnEpisodeBgmResult(
            episode_rel=self._rel(episode_dir),
            out_rel=self._rel(out_path),
            used=tuple(
                {"window": f"{c.start}-{c.end}", "bgm_id": c.bgm_id, "duck": c.duck}
                for c, _ in resolved
            ),
            skipped=tuple(skipped),
        )

    def _mux(
        self, source: Path, cues: list[tuple[BgmCue, Path]], out_path: Path
    ) -> None:
        try:
            ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        except Exception as exc:  # imageio_ffmpeg raises various on failure
            raise EpisodeBgmFfmpegMissingError(str(exc)) from exc

        filtergraph, mix_pads = self._build_filtergraph(cues)
        cmd: list[str] = [ffmpeg, "-y", "-i", str(source)]
        for _cue, mp3 in cues:
            cmd.extend(["-i", str(mp3)])
        cmd.extend([
            "-filter_complex", filtergraph,
            "-map", "0:v", "-map", mix_pads,
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", _AUDIO_BITRATE,
            "-shortest", "-movflags", "+faststart",
            "-loglevel", "error",
            str(out_path),
        ])
        try:
            completed = subprocess.run(
                cmd, capture_output=True, timeout=_MUX_TIMEOUT_S, check=False
            )
        except subprocess.TimeoutExpired as exc:
            raise EpisodeBgmMuxFailedError("ffmpeg_timeout") from exc
        if completed.returncode != 0 or not out_path.is_file():
            err = completed.stderr.decode("utf-8", errors="replace").strip()[-400:]
            raise EpisodeBgmMuxFailedError(err or "ffmpeg_failed")

    @staticmethod
    def _build_filtergraph(cues: list[tuple[BgmCue, Path]]) -> tuple[str, str]:
        """One BGM input per cue (input index i+1; 0 is the source video).

        Each cue's bgm is looped→trimmed to its window, gain/fade applied, then
        delayed to its start. Ducked cues are sidechain-compressed by a copy of
        the source's own audio. Everything mixes with the source audio at
        normalize=0 so the dialogue is never silently halved.
        """
        steps: list[str] = []
        duck_count = sum(1 for c, _ in cues if c.duck)

        base_label = "[0:a]"
        if duck_count:
            keys = "".join(f"[k{i}]" for i in range(duck_count))
            steps.append(f"[0:a]asplit={duck_count + 1}[base]{keys}")
            base_label = "[base]"

        mix_inputs: list[str] = [base_label]
        key_idx = 0
        for i, (cue, _mp3) in enumerate(cues):
            idx = i + 1
            win = cue.window if cue.window > 0 else 0.1
            start_ms = int(round(cue.start * 1000))
            chain = [
                f"[{idx}:a]aloop=loop=-1:size=2147483647",
                f"atrim=0:{win:.3f}",
                "asetpts=PTS-STARTPTS",
                f"volume={cue.vol:g}",
            ]
            if cue.fade_in:
                chain.append(f"afade=t=in:st=0:d={_FADE_SECONDS:.3f}")
            if cue.fade_out:
                fo = max(win - _FADE_SECONDS, 0.0)
                chain.append(f"afade=t=out:st={fo:.3f}:d={_FADE_SECONDS:.3f}")
            chain.append(f"adelay={start_ms}:all=1")
            steps.append(",".join(chain) + f"[bgm{i}]")
            if cue.duck:
                steps.append(
                    f"[bgm{i}][k{key_idx}]sidechaincompress="
                    f"threshold={_DUCK['threshold']}:ratio={_DUCK['ratio']}:"
                    f"attack={_DUCK['attack']}:release={_DUCK['release']}[bgm{i}d]"
                )
                mix_inputs.append(f"[bgm{i}d]")
                key_idx += 1
            else:
                mix_inputs.append(f"[bgm{i}]")
        steps.append(
            "".join(mix_inputs)
            + f"amix=inputs={len(mix_inputs)}:normalize=0:duration=longest[aout]"
        )
        return ";".join(steps), "[aout]"

    # ------------------------------------------------------------------ helpers
    def _validate_episode(self, rel: str) -> tuple[Path, str]:
        if not isinstance(rel, str) or rel == "":
            raise InvalidEpisodeBgmPathError("path is empty")
        if not self._exposed.is_inside(rel):
            raise InvalidEpisodeBgmPathError("path outside sandbox")
        parts = rel.split("/")
        if len(parts) < 4 or parts[0] != "ai_videos" or parts[1].startswith("_"):
            raise NotEpisodeBgmPathError("path is not under ai_videos/{drama}/")
        try:
            ep_idx = next(
                i for i in range(1, len(parts) - 1)
                if parts[i] == "episodes" and _EP_DIR_RE.match(parts[i + 1])
            )
        except StopIteration as exc:
            raise NotEpisodeBgmPathError("path is not under episodes/ep{NN}/") from exc
        episode_rel = "/".join(parts[: ep_idx + 2])
        resolved = self._resolver.resolve(episode_rel)
        if resolved is None:
            raise InvalidEpisodeBgmPathError("episode path failed sandbox resolution")
        if resolved.is_symlink() or not resolved.is_dir():
            raise NotEpisodeBgmPathError("episode folder does not exist")
        return resolved, parts[ep_idx + 1].lower()

    def _atomic_write(self, path: Path, body: str) -> None:
        parent = path.parent
        parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_str = tempfile.mkstemp(prefix=".bgmcue_", suffix=".md.tmp", dir=str(parent))
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

    def _rel(self, p: Path) -> str:
        try:
            return p.resolve().relative_to(self._resolver.root).as_posix()
        except (OSError, ValueError):
            return p.as_posix()


def _same_window(a: float, b: float) -> bool:
    return abs(a - b) < 0.001
