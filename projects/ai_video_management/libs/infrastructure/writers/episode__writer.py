"""Episode-aggregate writer: stitch each shot's newest render into one
`ep{NN}.mp4` placed directly in the episode folder.

Given a path anywhere under `ai_videos/{drama}/episodes/ep{NN}/`, the builder
locates the episode dir, walks `shots/shot*/` in lexicographic order, and for
each shot takes the **newest** mp4 found under that shot's `renders/` subfolder
(`archive/` excluded). Shots whose `renders/` is missing/empty are skipped. The
selected full-length clips are ffmpeg-concatenated — uniform 9:16, with audio —
into `{ep dir name}.mp4` next to the episode's markdown, overwriting any prior
build. Output lives in the episode folder (not under `shots/`), so a re-run
never re-ingests its own previous output.

Implementation mirrors ShotConcatBuilder's concat *filter* approach
(`trim`-free here, so each shot plays at full length): every input is
normalised through `setpts → scale → pad → setsar → fps` for video and
`asetpts → aresample → aformat` for audio, so heterogeneous Kling / Seedance
renders stitch without A/V drift. Inputs lacking an audio stream contribute a
silent `anullsrc` track of matching length.

Seam de-stutter (跨镜首帧承接, ai_video.md 2026-06-21): a 承接 shot is generated
from the previous shot's last frame, so its first frame is a held duplicate that
reads as a ~0.2s freeze at the join. For every 承接 shot (per its `衔接:` line)
the builder (1) `trim`s the leading freeze off the incoming clip — `freezedetect`
measures the hold, with a guaranteed minimum so the structural duplicate frame is
dropped even when the hold is too short to detect — and (2) cross-fades the seam
~0.12s (the two seam frames are near identical, so the blend is invisible but it
absorbs the residual velocity hitch). 硬切 seams are intended cuts: butt-joined,
untouched.

ffmpeg binary supplied by `imageio-ffmpeg` — no system install required.
"""
from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

import imageio_ffmpeg

from libs.common.exposed_tree import ExposedTree
from libs.common.render_select import newest_render
from libs.common.safe_resolve import SafeResolver
from libs.domain.errors.episode__error import (
    EpisodeConcatFailedError,
    EpisodeFfmpegMissingError,
    EpisodeNotFoundError,
    InvalidEpisodePathError,
    NoShotsError,
    NoShotVideosError,
    NotEpisodePathError,
)

_EP_DIR_RE = re.compile(r"^ep\d+$", re.IGNORECASE)
_SHOT_DIR_RE = re.compile(r"^shot\d+$", re.IGNORECASE)
_MP4_EXT = ".mp4"

# Episode build variants. "original" = each shot's newest raw render under
# renders/. The subtitle variants pick each shot's burned language master
# `shot{NN}_{suffix}.mp4` (produced by SubtitleBurner) from the shot-folder root.
VALID_EPISODE_LANGS: tuple[str, ...] = ("original", "zh", "en", "both")
_LANG_SUFFIX: dict[str, str] = {"zh": "zh", "en": "en", "both": "zhen"}

_EPISODE_FFMPEG_TIMEOUT_S: int = 600
_CONCAT_TARGET_W: int = 720      # 9:16 reel — 720x1280 is fast to encode + plenty for review
_CONCAT_TARGET_H: int = 1280
# Output framerate is matched to the SOURCE cadence, not hardcoded. The shot
# renders are ~24fps (VFR); forcing them to 30 duplicates ~1 in 5 frames (4:5
# pulldown) → a global judder that reads as 不顺 throughout, not just at seams.
# So _ffmpeg_concat probes the clips' fps and snaps to the nearest standard rate,
# falling back to 30 only if detection fails (e.g. synthetic test clips).
_CONCAT_FALLBACK_FPS: int = 30
_STANDARD_FPS: tuple[int, ...] = (24, 25, 30, 50, 60)
_FPS_SNAP_TOL: float = 1.5       # snap a probed rate to a standard one within this many fps

# Cross-shot first-frame handoff (跨镜首帧承接, ai_video.md 2026-06-21): a 承接
# shot is generated FROM the previous shot's last frame, so its first frame is a
# duplicate of that frame. The perceived ~0.2s 卡顿 at the seam is NOT just that
# duplicate frame — it's a VELOCITY RAMP on BOTH sides: the outgoing clip
# DECELERATES into its final frame (i2v settles toward the still it was told to
# end on) and the incoming clip ACCELERATES from rest (it starts from that same
# still). Those frames keep changing, just slowly, so a tight freeze threshold
# misses them. So at each 承接 seam we trim BOTH sides: the incoming head via
# freezedetect-at-a-loose-threshold (catches the duplicate frame + accel ramp),
# and the outgoing tail via a fixed bite (the decel settle reads as near-frozen
# over a long fragmented span that detection over-estimates — so only the final
# dead sliver is removed, deterministically). Result: a clean motion-to-motion
# cut. 硬切 shots are intended cuts — untouched. 承接/硬切 status is the `衔接:`
# line in shotNN.md.
_SEAM_FREEZE_NOISE: str = "-45dB"   # loose enough that the slow accel ramp registers as near-frozen
_SEAM_FREEZE_MIN_D: float = 0.04    # min freeze duration freezedetect reports (~1 frame)
_SEAM_PROBE_WINDOW_S: float = 1.5   # only decode the clip head when probing
_SEAM_PROBE_TIMEOUT_S: int = 30
_SEAM_EDGE_EPS_S: float = 0.12      # leading freeze must touch the head to count as a seam ramp
_SEAM_MAX_TRIM_S: float = 1.0       # safety cap so a mostly-static clip isn't gutted
# Per-side bite at every 承接 seam regardless of detection: the incoming first
# frame is a structural duplicate by construction and the outgoing clip settles
# into it, so a minimum bite on each side reliably removes the dwell. Used as the
# floor for the (detected) incoming head and as the fixed outgoing-tail trim.
_SEAM_MIN_EDGE_TRIM_S: float = 0.15  # ≈4–5 frames @30fps, each side of the seam
# Trimming the velocity ramp off both sides leaves a butt-join concat that reads
# as a clean continuous cut. Cross-fades were tried twice and rejected: dissolving
# the two (post-trim, near-identical) 承接 seam frames read as a flash (follow-up
# 135/136), and a whole-episode cross-dissolve between different shots did not read
# as softer than a clean cut — it looked worse (follow-up 142/143). Plain concat.
_FREEZE_START_RE = re.compile(r"freeze_start:\s*([0-9.]+)")
_FREEZE_END_RE = re.compile(r"freeze_end:\s*([0-9.]+)")
_CLIP_DURATION_RE = re.compile(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)")
_PROGRESS_TIME_RE = re.compile(r"time=\s*(\d+):(\d+):(\d+(?:\.\d+)?)")
_FPS_RE = re.compile(r"(\d+(?:\.\d+)?)\s*fps")
# A de-freeze pass (mpdecimate, follow-up 139/140) once lived here to collapse the
# i2v renders' long mid-shot stalls, but it was REVERTED (follow-up 141): the
# stalls overlap speech, so removing them either sped the dialogue (atempo) or
# dropped words — and shortened the cut below the source total. The stalls are
# generation defects, fixed by regenerating the shot, not in concat.


@dataclass(frozen=True)
class ShotClip:
    shot: str
    video_rel: str
    trimmed_s: float = 0.0   # seam head-freeze trimmed off this clip (承接 shots only)

    def to_payload(self) -> dict[str, object]:
        return {"shot": self.shot, "video": self.video_rel, "trimmed_s": self.trimmed_s}


@dataclass(frozen=True)
class ShotSkip:
    shot: str
    reason: str

    def to_payload(self) -> dict[str, object]:
        return {"shot": self.shot, "reason": self.reason}


@dataclass(frozen=True)
class EpisodeConcatResult:
    episode_rel: str
    out_rel: str | None
    used: tuple[ShotClip, ...]
    skipped: tuple[ShotSkip, ...]
    lang: str

    def to_payload(self) -> dict[str, object]:
        return {
            "episode": self.episode_rel,
            "out": self.out_rel,
            "used": [u.to_payload() for u in self.used],
            "skipped": [s.to_payload() for s in self.skipped],
            "lang": self.lang,
        }


class EpisodeConcatBuilder:
    def __init__(self, exposed: ExposedTree, resolver: SafeResolver) -> None:
        self._exposed = exposed
        self._resolver = resolver

    def build(self, rel: str, lang: str = "original") -> EpisodeConcatResult:
        if lang not in VALID_EPISODE_LANGS:
            raise InvalidEpisodePathError(f"unknown episode lang: {lang!r}")
        episode_dir, episode_slug = self._validate_episode(rel)
        shots_dir = episode_dir / "shots"
        if not shots_dir.is_dir():
            raise NoShotsError("episode has no shots/ folder")
        shot_dirs = self._shot_dirs(shots_dir)
        if not shot_dirs:
            raise NoShotsError("shots/ folder contains no shot{NN} subfolders")

        used: list[ShotClip] = []
        used_dirs: list[Path] = []
        skipped: list[ShotSkip] = []
        for shot_dir in shot_dirs:
            clip = self._select_clip(shot_dir, lang)
            if clip is None:
                reason = (
                    "no_render_mp4" if lang == "original"
                    else f"no_{_LANG_SUFFIX[lang]}_subtitle_mp4"
                )
                skipped.append(ShotSkip(shot_dir.name, reason))
                continue
            used.append(ShotClip(shot_dir.name, self._rel(clip)))
            used_dirs.append(shot_dir)

        if not used:
            raise NoShotVideosError("no shot has a matching mp4 to concatenate")

        ffmpeg = self._ffmpeg_exe()
        inputs = [self._resolver.resolve(u.video_rel) for u in used]
        # Seam de-stutter at every 承接 seam: trim the velocity ramp off BOTH sides
        # — the incoming clip's head (accelerate-from-still + duplicate frame) and
        # the outgoing clip's tail (decelerate-into-final-frame). Never trim across
        # a 硬切 (intended cut); the first clip has no predecessor.
        head_trims: list[float] = [0.0] * len(used_dirs)
        tail_trims: list[float] = [0.0] * len(used_dirs)
        for i, shot_dir in enumerate(used_dirs):
            is_cont = (
                i > 0 and self._is_continuity_shot(shot_dir) and inputs[i] is not None
            )
            if not is_cont:
                continue
            # Incoming head: freezedetect (catches the duplicate frame + the
            # accelerate-from-still ramp), floored so the dwell goes even when the
            # ramp is too slow to register. Outgoing tail: a fixed bite — the
            # decelerate-into-final-frame settle reads as near-frozen over a long,
            # fragmented span that detection over-estimates, so trim only the final
            # dead sliver deterministically.
            head_trims[i] = max(
                self._detect_head_freeze(ffmpeg, inputs[i]), _SEAM_MIN_EDGE_TRIM_S
            )
            if inputs[i - 1] is not None:
                tail_trims[i - 1] = _SEAM_MIN_EDGE_TRIM_S
        used = [
            ShotClip(c.shot, c.video_rel, head_trims[i] + tail_trims[i])
            for i, c in enumerate(used)
        ]

        suffix = "" if lang == "original" else f"_{_LANG_SUFFIX[lang]}"
        out_path = episode_dir / f"{episode_slug}{suffix}{_MP4_EXT}"
        self._ffmpeg_concat(
            ffmpeg=ffmpeg,
            inputs=inputs,  # type: ignore[arg-type]
            out_path=out_path,
            head_trims=head_trims,
            tail_trims=tail_trims,
        )
        return EpisodeConcatResult(
            episode_rel=self._rel(episode_dir),
            out_rel=self._rel(out_path),
            used=tuple(used),
            skipped=tuple(skipped),
            lang=lang,
        )

    @staticmethod
    def _ffmpeg_exe() -> str:
        try:
            return imageio_ffmpeg.get_ffmpeg_exe()
        except Exception as exc:  # imageio_ffmpeg raises various on failure
            raise EpisodeFfmpegMissingError(str(exc)) from exc

    def _is_continuity_shot(self, shot_dir: Path) -> bool:
        """True iff the shot's `衔接:` line marks it 承接 (cross-shot first-frame
        handoff). 硬切 / missing → False (default hard cut)."""
        md = shot_dir / f"{shot_dir.name}.md"
        try:
            text = md.read_text(encoding="utf-8")
        except OSError:
            return False
        for line in text.splitlines():
            if "衔接" in line:
                # check 硬切 first — the hard-cut text「硬切（独立首帧·无承接帧）」
                # itself contains the substring 承接, so order matters.
                if "硬切" in line:
                    return False
                if "承接" in line:
                    return True
        return False

    def _detect_head_freeze(self, ffmpeg: str, src: Path) -> float:
        """Seconds of held/slow frames at the clip's head, capped, or 0.0.

        Runs `freezedetect` over only the clip's first ~1.5s and returns the end
        of the leading freeze when the clip starts (near-)frozen — i.e. the
        duplicate first frame + the accelerate-from-still ramp. 0.0 when the clip
        starts moving or detection fails (fail-open = no trim)."""
        try:
            result = subprocess.run(
                [ffmpeg, "-t", f"{_SEAM_PROBE_WINDOW_S}", "-i", str(src),
                 "-vf", f"freezedetect=n={_SEAM_FREEZE_NOISE}:d={_SEAM_FREEZE_MIN_D}",
                 "-map", "0:v", "-an", "-f", "null", "-"],
                capture_output=True, timeout=_SEAM_PROBE_TIMEOUT_S, check=False,
            )
        except subprocess.TimeoutExpired:
            return 0.0
        return self._parse_head_freeze(result.stderr.decode("utf-8", errors="replace"))

    @staticmethod
    def _parse_head_freeze(out: str) -> float:
        """Head-freeze seconds from freezedetect stderr: the end of the leading
        freeze IFF the clip starts (near-)frozen, capped; else 0.0."""
        starts = _FREEZE_START_RE.findall(out)
        ends = _FREEZE_END_RE.findall(out)
        if not starts or not ends:
            return 0.0
        try:
            first_start = float(starts[0])
            first_end = float(ends[0])
        except ValueError:
            return 0.0
        if first_start > _SEAM_EDGE_EPS_S:
            return 0.0  # leading freeze is not at the head → not a seam dup
        return min(max(0.0, first_end), _SEAM_MAX_TRIM_S)

    def _validate_episode(self, rel: str) -> tuple[Path, str]:
        if not isinstance(rel, str) or rel == "":
            raise InvalidEpisodePathError("path is empty")
        if not self._exposed.is_inside(rel):
            raise InvalidEpisodePathError("path outside sandbox")
        parts = rel.split("/")
        if len(parts) < 4 or parts[0] != "ai_videos" or parts[1].startswith("_"):
            raise NotEpisodePathError("path is not under ai_videos/{drama}/")
        try:
            ep_idx = next(
                i for i in range(1, len(parts) - 1)
                if parts[i] == "episodes" and _EP_DIR_RE.match(parts[i + 1])
            )
        except StopIteration as exc:
            raise NotEpisodePathError("path is not under episodes/ep{NN}/") from exc
        episode_rel = "/".join(parts[: ep_idx + 2])
        resolved = self._resolver.resolve(episode_rel)
        if resolved is None:
            raise InvalidEpisodePathError("episode path failed sandbox resolution")
        if resolved.is_symlink():
            raise InvalidEpisodePathError("symlink is not allowed")
        if not resolved.is_dir():
            raise EpisodeNotFoundError("episode folder does not exist")
        return resolved, parts[ep_idx + 1].lower()

    @staticmethod
    def _shot_dirs(shots_dir: Path) -> list[Path]:
        try:
            entries = sorted(shots_dir.iterdir(), key=lambda p: p.name)
        except OSError:
            return []
        return [
            e for e in entries
            if e.is_dir() and not e.is_symlink() and _SHOT_DIR_RE.match(e.name)
        ]

    def _select_clip(self, shot_dir: Path, lang: str) -> Path | None:
        """Pick the clip representing this shot for the requested variant.

        - "original": newest raw take under `renders/`.
        - zh / en / both: the burned language master `shot{NN}_{suffix}.mp4` in
          the shot-folder root (skip the shot if that master hasn't been burned).
        """
        if lang == "original":
            return newest_render(shot_dir)
        master = shot_dir / f"{shot_dir.name}_{_LANG_SUFFIX[lang]}{_MP4_EXT}"
        if master.is_file() and not master.is_symlink():
            return master
        return None

    def _ffmpeg_concat(
        self,
        ffmpeg: str,
        inputs: list[Path],
        out_path: Path,
        head_trims: list[float],
        tail_trims: list[float],
    ) -> None:
        n = len(inputs)
        durations = [self._probe_duration(ffmpeg, src) for src in inputs]
        has_audio = [self._probe_has_audio(ffmpeg, src) for src in inputs]
        target_fps = self._target_fps(ffmpeg, inputs)
        h = [head_trims[i] if i < len(head_trims) else 0.0 for i in range(n)]
        tl = [tail_trims[i] if i < len(tail_trims) else 0.0 for i in range(n)]
        # kept window of each clip [head_trim, duration - tail_trim).
        end = [max(h[i] + 0.1, durations[i] - tl[i]) for i in range(n)]
        eff = [end[i] - h[i] for i in range(n)]

        # FAITHFUL concat: each clip plays at its NATURAL speed and length (audio
        # included), so the total ≈ the sum of the source clips and speech is never
        # sped up. The only edits are the 承接 seam trims (head + predecessor tail,
        # follow-up 137) for a clean motion-to-motion cut, and matching every clip
        # to the source framerate (follow-up 138) to avoid pulldown judder. Audio-
        # less clips get their own silent anullsrc of matching length so concat
        # never double-consumes a source. Two transition experiments were tried and
        # REVERTED: a de-freeze pass (mpdecimate, follow-up 139/140 → 141) sped or
        # dropped speech, and a whole-episode cross-dissolve (xfade+acrossfade,
        # follow-up 142 → 143) did NOT read as softer — the dissolve between two
        # different shots looked worse than a clean butt-cut. NO cross-fade. The
        # tail-settle jolt and mid-shot stalls are generation defects, fixed by
        # regenerating the shot, not in concat.
        segs: list[str] = []
        for i in range(n):
            t = h[i]
            vtrim = f"trim=start={t:.3f}:end={end[i]:.3f}," if (t > 0 or tl[i] > 0) else ""
            segs.append(
                f"[{i}:v]{vtrim}setpts=PTS-STARTPTS,"
                f"scale={_CONCAT_TARGET_W}:{_CONCAT_TARGET_H}:force_original_aspect_ratio=decrease,"
                f"pad={_CONCAT_TARGET_W}:{_CONCAT_TARGET_H}:(ow-iw)/2:(oh-ih)/2:black,"
                f"setsar=1,fps={target_fps}[v{i}]"
            )
            if has_audio[i]:
                atrim = (
                    f"atrim=start={t:.3f}:end={end[i]:.3f},"
                    if (t > 0 or tl[i] > 0) else ""
                )
                segs.append(
                    f"[{i}:a]{atrim}asetpts=PTS-STARTPTS,aresample=44100,"
                    f"aformat=sample_fmts=fltp:channel_layouts=stereo[a{i}]"
                )
            else:
                segs.append(
                    f"anullsrc=channel_layout=stereo:sample_rate=44100,"
                    f"atrim=0:{eff[i]:.3f},asetpts=PTS-STARTPTS,"
                    f"aformat=sample_fmts=fltp:channel_layouts=stereo[a{i}]"
                )
        concat_pads = "".join(f"[v{i}][a{i}]" for i in range(n))
        filter_complex = ";".join(
            [*segs, f"{concat_pads}concat=n={n}:v=1:a=1[outv][outa]"]
        )

        cmd: list[str] = [ffmpeg, "-y"]
        for src in inputs:
            cmd.extend(["-i", str(src)])
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
            "-shortest",
            "-movflags", "+faststart",
            "-loglevel", "error",
            str(out_path),
        ])

        try:
            completed = subprocess.run(
                cmd,
                capture_output=True,
                timeout=_EPISODE_FFMPEG_TIMEOUT_S,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise EpisodeConcatFailedError("ffmpeg_timeout") from exc
        if completed.returncode != 0 or not out_path.is_file():
            err = completed.stderr.decode("utf-8", errors="replace").strip()[:400]
            raise EpisodeConcatFailedError(err or "ffmpeg_failed")

    @staticmethod
    def _probe_duration(ffmpeg: str, src: Path) -> float:
        """The VIDEO-STREAM duration in seconds — NOT the container Duration,
        which can be the longer audio track. xfade operates on the video
        timeline, so an over-long container value pushes the xfade offset past
        the real end of the accumulated video and drops everything after the
        seam. `-map 0:v:0 -c copy -f null -` demuxes (no decode → fast) and the
        final progress `time=` is the video stream's true length. 5.0 on failure.
        """
        try:
            result = subprocess.run(
                [ffmpeg, "-i", str(src), "-map", "0:v:0", "-c", "copy",
                 "-f", "null", "-"],
                capture_output=True, timeout=30, check=False,
            )
        except subprocess.TimeoutExpired:
            return 5.0
        err = result.stderr.decode("utf-8", errors="replace")
        times = _PROGRESS_TIME_RE.findall(err)
        if times:
            h, m, s = times[-1]
            return max(0.1, int(h) * 3600 + int(m) * 60 + float(s))
        m2 = _CLIP_DURATION_RE.search(err)  # fallback: container Duration
        if m2:
            return max(
                0.1, int(m2.group(1)) * 3600 + int(m2.group(2)) * 60 + float(m2.group(3))
            )
        return 5.0

    def _target_fps(self, ffmpeg: str, inputs: list[Path]) -> int:
        """The output framerate, matched to the source cadence: the median of the
        clips' probed fps, snapped to the nearest standard rate. Matching the
        source avoids the frame-duplication judder of up-converting (e.g. 24→30).
        Falls back to `_CONCAT_FALLBACK_FPS` when no clip's fps can be read."""
        probed = [f for f in (self._probe_fps(ffmpeg, s) for s in inputs) if f]
        if not probed:
            return _CONCAT_FALLBACK_FPS
        probed.sort()
        median = probed[len(probed) // 2]
        return self._snap_fps(median)

    @staticmethod
    def _probe_fps(ffmpeg: str, src: Path) -> float | None:
        """The clip's nominal frame rate from `ffmpeg -i` stderr, or None."""
        try:
            result = subprocess.run(
                [ffmpeg, "-i", str(src), "-hide_banner"],
                capture_output=True, timeout=15, check=False,
            )
        except subprocess.TimeoutExpired:
            return None
        m = _FPS_RE.search(result.stderr.decode("utf-8", errors="replace"))
        if not m:
            return None
        try:
            return float(m.group(1))
        except ValueError:
            return None

    @staticmethod
    def _snap_fps(fps: float) -> int:
        """Snap a probed rate to the NEAREST standard rate when within tolerance
        (24 and 25 are only 1 apart, so closest — not first-match — wins); else
        round to the nearest integer (never below 1)."""
        nearest = min(_STANDARD_FPS, key=lambda std: abs(fps - std))
        if abs(fps - nearest) <= _FPS_SNAP_TOL:
            return nearest
        return max(1, round(fps))

    @staticmethod
    def _probe_has_audio(ffmpeg: str, src: Path) -> bool:
        """True iff `src` carries at least one Audio stream (probed via `ffmpeg -i`
        stderr — imageio_ffmpeg bundles no ffprobe)."""
        try:
            result = subprocess.run(
                [ffmpeg, "-i", str(src), "-hide_banner"],
                capture_output=True, timeout=15, check=False,
            )
        except subprocess.TimeoutExpired:
            return False
        for line in result.stderr.decode("utf-8", errors="replace").splitlines():
            stripped = line.strip()
            if stripped.startswith("Stream #") and "Audio:" in stripped:
                return True
        return False

    def _rel(self, p: Path) -> str:
        try:
            return p.resolve().relative_to(self._resolver.root).as_posix()
        except (OSError, ValueError):
            return p.as_posix()
