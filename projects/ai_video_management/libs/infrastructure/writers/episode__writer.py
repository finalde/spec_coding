"""Episode-aggregate writer: stitch each shot's newest render into one
`ep{NN}.mp4` placed directly in the episode folder.

Given a path anywhere under `ai_videos/{drama}/episodes/ep{NN}/`, the builder
locates the episode dir, walks `shots/shot*/` in lexicographic order, and for
each shot takes the **newest** mp4 found under that shot's `renders/` subfolder
(`archive/` excluded). Shots whose `renders/` is missing/empty are skipped. The
selected full-length clips are ffmpeg-concatenated — uniform 9:16, with audio —
into `{ep dir name}.mp4` next to the episode's markdown. Output lives in the
episode folder (not under `shots/`), so a re-run never re-ingests its own previous
output. The prior `ep{NN}.mp4` (and its `.segments.json` sidecar) is DELETED first
— right after shot validation, before the slow seam-probe + stitch — so its absence
signals "generating…" and a stale reel is never mistaken for a freshly-built one;
a validation failure (no shots) raises before that delete, preserving the old reel.

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

import base64
import importlib.util
import json
import os
import re
import subprocess
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from types import ModuleType

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

# Concat is subtitle-FREE (follow-up 147): it always stitches each shot's clean
# selected take into `ep{NN}.mp4`. Subtitles are no longer burned per-shot then
# concatenated (that re-encoded the burned subs + the seam trims shifted their
# timeline). The whole-episode subtitle pass (EpisodeSubtitleBurner) burns ONCE
# onto this clean reel, aligned to the real final timeline via segments.json.
# The `lang` param survives only for route/back-compat; only "original" is valid.
VALID_EPISODE_LANGS: tuple[str, ...] = ("original",)
# Sidecar manifest written next to ep{NN}.mp4: each shot's [start,end) in the
# FINAL stitched timeline (post seam-trim). The whole-episode subtitle burn reads
# it so each shot's cues land at their true offset — never guessed from nominal
# shot 时长 (the old per-shot-then-concat misalignment root).
_SEGMENTS_SUFFIX: str = ".segments.json"

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
# RIFE seam bridging (opt-in, button checkbox). Instead of butt-joining the two
# trimmed 承接 frames, an external RIFE interpolator synthesises the deleted
# motion so the velocity hitch is filled rather than cut. The bridge logic is the
# repo tool `tools/seam_concat.py` — reused as the single source of truth (loaded
# by path off the sandbox root) rather than duplicated here. 硬切 seams stay
# untouched. Only runs when the exe resolves; the path comes from
# RIFE_NCNN_VULKAN_EXE or the default install location.
_RIFE_ENV_VAR: str = "RIFE_NCNN_VULKAN_EXE"
_RIFE_DEFAULT_EXE: str = (
    r"C:\tools\rife\rife-ncnn-vulkan-20221029-windows\rife-ncnn-vulkan.exe"
)
_RIFE_SEAM_TRIM_S: float = 0.10   # per-side bite seam_concat trims at each bridge seam
# Seam planner (UI per-seam method/trim/density). The chosen plan persists next to
# the episode so a re-generate reproduces the exact stitch.
_SEAM_PLAN_FILE: str = "seam_plan.json"
_SEAM_THUMB_W: int = 200          # px width of the per-seam preview frames (base64 JPEG)
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
    rife_used: bool = False     # RIFE motion-bridge stitch applied at 承接 seams
    rife_bridges: int = 0       # number of seams actually bridged
    segments_rel: str | None = None   # sidecar ep{NN}.segments.json (final timeline)

    def to_payload(self) -> dict[str, object]:
        return {
            "episode": self.episode_rel,
            "out": self.out_rel,
            "used": [u.to_payload() for u in self.used],
            "skipped": [s.to_payload() for s in self.skipped],
            "lang": self.lang,
            "rife_used": self.rife_used,
            "rife_bridges": self.rife_bridges,
            "segments": self.segments_rel,
        }


@dataclass(frozen=True)
class SeamInfo:
    index: int
    from_shot: str
    to_shot: str
    link: str            # "handoff" (承接, RIFE-eligible) | "hardcut" (硬切, butt only)
    diff: float | None   # mean-abs frame diff (handoff only; suggestion guide)
    suggest: str         # "trim" | "rife" | "butt" — auto recommendation
    method: str          # "trim" | "rife" | "butt" — current choice (saved plan/suggest)
    trim: float
    depth: int | None    # 补帧密度 override (None = auto)
    thumb_a: str         # data-URI base64 JPEG of predecessor tail frame
    thumb_b: str         # data-URI base64 JPEG of successor head frame

    def to_payload(self) -> dict[str, object]:
        return {
            "index": self.index, "from": self.from_shot, "to": self.to_shot,
            "link": self.link, "diff": self.diff, "suggest": self.suggest,
            "method": self.method, "trim": self.trim, "depth": self.depth,
            "thumb_a": self.thumb_a, "thumb_b": self.thumb_b,
        }


@dataclass(frozen=True)
class SeamAnalysis:
    episode_rel: str
    lang: str
    seams: tuple[SeamInfo, ...]
    has_saved_plan: bool

    def to_payload(self) -> dict[str, object]:
        return {
            "episode": self.episode_rel, "lang": self.lang,
            "seams": [s.to_payload() for s in self.seams],
            "has_saved_plan": self.has_saved_plan,
        }


class EpisodeConcatBuilder:
    def __init__(self, exposed: ExposedTree, resolver: SafeResolver) -> None:
        self._exposed = exposed
        self._resolver = resolver

    def build(
        self, rel: str, lang: str = "original", rife: bool = False,
        plan: list[dict] | None = None,
    ) -> EpisodeConcatResult:
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
            clip = self._select_clip(shot_dir)
            if clip is None:
                skipped.append(ShotSkip(shot_dir.name, "no_render_mp4"))
                continue
            used.append(ShotClip(shot_dir.name, self._rel(clip)))
            used_dirs.append(shot_dir)

        if not used:
            raise NoShotVideosError("no shot has a matching mp4 to concatenate")

        # Clear the prior build FIRST — before the (slow) seam-probe + stitch — so the
        # absence of ep{NN}.mp4 signals "generating…" and the user never mistakes a
        # stale reel for a freshly-built one. Done only after the validation above
        # confirmed there ARE shots to stitch (so a no-shots failure preserves the old
        # reel). seam_plan.json is the user's saved input, not output — never removed.
        out_path = episode_dir / f"{episode_slug}{_MP4_EXT}"
        self._remove_stale_output(out_path)

        ffmpeg = self._ffmpeg_exe()
        inputs = [self._resolver.resolve(u.video_rel) for u in used]
        # Seam de-stutter at every 承接 seam: trim the velocity ramp off BOTH sides
        # — the incoming clip's head (accelerate-from-still + duplicate frame) and
        # the outgoing clip's tail (decelerate-into-final-frame). Never trim across
        # a 硬切 (intended cut); the first clip has no predecessor.
        head_trims: list[float] = [0.0] * len(used_dirs)
        tail_trims: list[float] = [0.0] * len(used_dirs)
        cont_flags: list[bool] = [False] * len(used_dirs)
        for i, shot_dir in enumerate(used_dirs):
            is_cont = (
                i > 0 and self._is_continuity_shot(shot_dir) and inputs[i] is not None
            )
            cont_flags[i] = is_cont
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

        rife_used = False
        rife_bridges = 0
        approx_eff = True
        eff: list[float] = []
        all_resolved = all(p is not None for p in inputs)
        if plan is not None and all_resolved:
            # Explicit per-seam plan from the UI planner: honor each choice (RIFE
            # gate off). Persist the plan FIRST — it is the user's intent and must
            # survive even if the (long) render is interrupted, so reopening the
            # planner always reloads their last choices.
            self._save_plan(episode_dir, plan)
            tool_plan = self._plan_for_used(plan, used)
            rife_bridges = self._stitch_with_plan(inputs, out_path, tool_plan)  # type: ignore[arg-type]
            rife_used = any(e.get("rife") and e["bridge"] for e in tool_plan)
            eff = self._approx_eff(ffmpeg, inputs, head_trims, tail_trims)  # type: ignore[arg-type]
        elif rife and all_resolved and any(
            cont_flags[j + 1] for j in range(len(inputs) - 1)
        ):
            # seam j (between clip j and j+1) is a 承接 bridge iff clip j+1 is a
            # continuity shot. Auto motion gate applies (no explicit plan).
            seams = [cont_flags[j + 1] for j in range(len(inputs) - 1)]
            rife_bridges = self._rife_stitch(inputs, out_path, seams, None)  # type: ignore[arg-type]
            rife_used = True
            eff = self._approx_eff(ffmpeg, inputs, head_trims, tail_trims)  # type: ignore[arg-type]
        else:
            ret = self._ffmpeg_concat(
                ffmpeg=ffmpeg,
                inputs=inputs,  # type: ignore[arg-type]
                out_path=out_path,
                head_trims=head_trims,
                tail_trims=tail_trims,
            )
            # Butt concat returns the EXACT per-clip kept-window durations it cut;
            # the stubbed-ffmpeg unit tests return a placeholder list of matching
            # length. Either way `eff[i]` is shot i's length in the final reel.
            if ret:
                eff = list(ret)
                approx_eff = False
        segments_rel = self._write_segments(out_path, used, eff, approx_eff)
        # Persist the seam scorecard for THIS build so the dashboard shows the last
        # generation's score with no recompute when the page opens (best-effort).
        self._write_seam_scores(episode_dir, lang)
        return EpisodeConcatResult(
            episode_rel=self._rel(episode_dir),
            out_rel=self._rel(out_path),
            used=tuple(used),
            skipped=tuple(skipped),
            lang="original",
            rife_used=rife_used,
            rife_bridges=rife_bridges,
            segments_rel=segments_rel,
        )

    def _rife_stitch(
        self, inputs: list[Path], out_path: Path,
        seams: list[bool] | None, plan: list[dict] | None = None,
    ) -> int:
        """Stitch via the repo tool `tools/seam_concat.py` with RIFE bridges. With
        `seams` (b/c) the tool's auto motion gate decides; with `plan` (explicit
        per-seam) the user's choices win. Returns the bridge count. Raises
        EpisodeConcatFailedError when the RIFE exe is absent (explicit — never a
        silent butt-join fallback) or the stitch fails."""
        rife_exe = self._resolve_rife_exe()
        if rife_exe is None:
            raise EpisodeConcatFailedError(
                f"rife_exe_not_found — install rife-ncnn-vulkan or set ${_RIFE_ENV_VAR}"
            )
        seam_mod = self._load_seam_concat(self._resolver.root)
        try:
            return int(
                seam_mod.seam_concat(
                    list(inputs), out_path, _RIFE_SEAM_TRIM_S, rife_exe, 0, seams, plan
                )
            )
        except Exception as exc:  # tool raises RuntimeError on any ffmpeg/RIFE failure
            raise EpisodeConcatFailedError(f"rife_concat_failed: {exc}") from exc

    def _stitch_with_plan(
        self, inputs: list[Path], out_path: Path, tool_plan: list[dict]
    ) -> int:
        """Stitch via `tools/seam_concat.py` with an explicit per-seam plan that may
        mix RIFE bridges, trim-butt 承接 joins and hard cuts. The RIFE exe is required
        ONLY when some seam actually requests a bridge — a pure trim-butt / hard-cut
        plan stitches with no GPU. Returns the bridge count; raises on any failure
        (explicit — never a silent fallback)."""
        needs_rife = any(e.get("rife") and e["bridge"] for e in tool_plan)
        rife_exe = self._resolve_rife_exe() if needs_rife else None
        if needs_rife and rife_exe is None:
            raise EpisodeConcatFailedError(
                f"rife_exe_not_found — install rife-ncnn-vulkan or set ${_RIFE_ENV_VAR}"
            )
        seam_mod = self._load_seam_concat(self._resolver.root)
        try:
            return int(
                seam_mod.seam_concat(
                    list(inputs), out_path, _RIFE_SEAM_TRIM_S, rife_exe, 0, None, tool_plan
                )
            )
        except Exception as exc:  # tool raises RuntimeError on any ffmpeg/RIFE failure
            raise EpisodeConcatFailedError(f"plan_concat_failed: {exc}") from exc

    def _plan_for_used(
        self, plan: list[dict], used: list[ShotClip]
    ) -> list[dict]:
        """Map the UI plan (entries keyed by from/to shot) onto the n-1 consecutive
        used-clip seams the tool expects: {bridge, rife, trim, depth}. Three 承接
        join types: "rife" → trim both sides + RIFE motion-bridge (bridge+rife);
        "trim" → trim the ease/duplicate-frame off both sides + butt-join, NO RIFE
        (bridge, rife False) — the smoothest choice for an already-continuous seam;
        "butt"/hardcut → plain hard cut (no trim). A seam with no matching entry
        defaults to a clean butt-join."""
        by_pair = {(e.get("from"), e.get("to")): e for e in plan}
        tool_plan: list[dict] = []
        for i in range(len(used) - 1):
            e = by_pair.get((used[i].shot, used[i + 1].shot))
            if e is None:
                tool_plan.append({"bridge": False, "rife": False,
                                  "trim": _RIFE_SEAM_TRIM_S, "depth": None})
                continue
            method = e.get("method")
            trim = e.get("trim")
            depth = e.get("depth")
            tool_plan.append({
                "bridge": method in ("rife", "trim"),
                "rife": method == "rife",
                "trim": float(trim) if trim is not None else _RIFE_SEAM_TRIM_S,
                "depth": int(depth) if depth is not None and method == "rife" else None,
            })
        return tool_plan

    @staticmethod
    def _remove_stale_output(out_path: Path) -> None:
        """Delete a prior `ep{NN}.mp4` + its derived `.segments.json` sidecar before a
        re-stitch, so the file's absence marks 'generating…' and a stale reel is never
        mistaken for a fresh one. Missing files are fine; a locked file is left for the
        final ffmpeg `-y` (which will surface its own error). `seam_plan.json` is the
        user's saved input — never removed here."""
        for p in (out_path, out_path.with_suffix(_SEGMENTS_SUFFIX)):
            try:
                p.unlink()
            except OSError:
                pass

    def _save_plan(self, episode_dir: Path, plan: list[dict]) -> None:
        """Persist the per-seam plan next to the episode for reproducible regen."""
        path = episode_dir / _SEAM_PLAN_FILE
        payload = {"version": 1, "seams": plan}
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def _load_plan(self, episode_dir: Path) -> dict | None:
        """The saved plan as {(from,to): entry}, or None when absent/unreadable."""
        path = episode_dir / _SEAM_PLAN_FILE
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None
        out: dict = {}
        for e in data.get("seams", []):
            out[(e.get("from"), e.get("to"))] = e
        return out or None

    def analyze_seams(self, rel: str, lang: str = "original") -> SeamAnalysis:
        """Inspect every shot→shot junction for the seam-planner UI: 承接/硬切, the
        boundary-frame thumbnails, a frame-diff suggestion, and any saved choice."""
        if lang not in VALID_EPISODE_LANGS:
            raise InvalidEpisodePathError(f"unknown episode lang: {lang!r}")
        episode_dir, _ = self._validate_episode(rel)
        shot_dirs = self._shot_dirs(episode_dir / "shots")
        used: list[tuple[str, Path, Path]] = []
        for sd in shot_dirs:
            clip = self._select_clip(sd)
            if clip is not None:
                used.append((sd.name, clip, sd))
        if len(used) < 2:
            raise NoShotVideosError("need at least 2 shot clips to plan seams")
        ffmpeg = self._ffmpeg_exe()
        seam_mod = self._load_seam_concat(self._resolver.root)
        saved = self._load_plan(episode_dir)
        seams: list[SeamInfo] = []
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            for i in range(len(used) - 1):
                (fn, fclip, _), (tn, _tclip, tsd) = used[i], used[i + 1]
                a = tdp / f"{i}_a.jpg"
                b = tdp / f"{i}_b.jpg"
                self._seam_thumb(ffmpeg, fclip, ["-sseof", "-0.12"], a)
                self._seam_thumb(ffmpeg, used[i + 1][1], ["-ss", "0.10"], b)
                link = "handoff" if self._is_continuity_shot(tsd) else "hardcut"
                diff: float | None = None
                suggest = "butt"
                if link == "handoff" and a.is_file() and b.is_file():
                    diff = seam_mod._frame_diff(ffmpeg, a, b)
                    if diff is not None and (
                        seam_mod._BRIDGE_MIN_DIFF <= diff <= seam_mod._BRIDGE_MAX_DIFF
                    ):
                        # In-band 承接 seam: a trim-butt join (trim the ease/dup-frame,
                        # no RIFE) is the smoothest default — RIFE only adds blips on an
                        # already-continuous seam (empirically; tune with seam_tune.py).
                        suggest = "trim"
                sv = saved.get((fn, tn)) if saved else None
                method = sv.get("method") if sv else suggest
                if link == "hardcut":
                    method = "butt"  # 硬切 is never RIFE
                trim = float(sv["trim"]) if sv and sv.get("trim") is not None else _RIFE_SEAM_TRIM_S
                depth = sv.get("depth") if sv else None
                seams.append(SeamInfo(
                    index=i, from_shot=fn, to_shot=tn, link=link, diff=diff,
                    suggest=suggest, method=method or suggest, trim=trim, depth=depth,
                    thumb_a=self._b64_jpeg(a), thumb_b=self._b64_jpeg(b),
                ))
        return SeamAnalysis(self._rel(episode_dir), lang, tuple(seams), saved is not None)

    def _seam_thumb(self, ffmpeg: str, src: Path, when: list[str], dst: Path) -> None:
        """Extract one frame at `when` scaled to `_SEAM_THUMB_W` wide as JPEG."""
        subprocess.run(
            [ffmpeg, "-y", *when, "-i", str(src), "-frames:v", "1",
             "-vf", f"scale={_SEAM_THUMB_W}:-1", "-q:v", "5", "-update", "1", str(dst)],
            capture_output=True, timeout=_SEAM_PROBE_TIMEOUT_S, check=False,
        )

    @staticmethod
    def _b64_jpeg(path: Path) -> str:
        """A JPEG file as a data-URI, or '' when missing."""
        try:
            return "data:image/jpeg;base64," + base64.b64encode(path.read_bytes()).decode("ascii")
        except OSError:
            return ""

    @staticmethod
    def _resolve_rife_exe() -> str | None:
        """The rife-ncnn-vulkan exe path from ${_RIFE_ENV_VAR} or the default
        install location, or None when neither exists."""
        cand = os.environ.get(_RIFE_ENV_VAR, "").strip() or _RIFE_DEFAULT_EXE
        return cand if Path(cand).is_file() else None

    @staticmethod
    def _load_seam_concat(root: Path) -> ModuleType:
        """Load `tools/seam_concat.py` (the tested CLI) as a module off the
        sandbox root, so the button reuses the exact stitch logic the CLI runs."""
        path = root / "tools" / "seam_concat.py"
        spec = importlib.util.spec_from_file_location("seam_concat_tool", path)
        if spec is None or spec.loader is None:
            raise EpisodeConcatFailedError(f"seam_concat tool not found at {path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    @staticmethod
    def _load_seam_metrics(root: Path) -> ModuleType:
        """Load `tools/seam_metrics.py` (the objective seam scorer) off the sandbox
        root, so the dashboard reuses the exact metric the CLI computes."""
        path = root / "tools" / "seam_metrics.py"
        spec = importlib.util.spec_from_file_location("seam_metrics_tool", path)
        if spec is None or spec.loader is None:
            raise EpisodeConcatFailedError(f"seam_metrics tool not found at {path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def score_seams(
        self, rel: str, lang: str = "original", compare: bool = True
    ) -> dict:
        """Score every 首尾帧承接 seam of the episode (optical-flow + SSIM metrics) and,
        when `compare`, rank a standard method panel — returning the structured
        scorecard the dashboard renders. RIFE-needing panel rows are skipped when no
        RIFE exe is present (the chosen/trim/hardcut rows still score)."""
        if lang not in VALID_EPISODE_LANGS:
            raise InvalidEpisodePathError(f"unknown episode lang: {lang!r}")
        episode_dir, _ = self._validate_episode(rel)
        if not (episode_dir / _SEAM_PLAN_FILE).is_file():
            raise NoShotsError("episode has no seam_plan.json to score")
        metrics = self._load_seam_metrics(self._resolver.root)
        return metrics.compute_scorecard(
            episode_dir, lang, compare, self._resolve_rife_exe()
        )

    def read_seam_scores(self, rel: str) -> dict | None:
        """The persisted scorecard sidecar (last generation's score), or None when the
        episode has not been scored yet. Instant — no recompute — so the dashboard shows
        the last build's result the moment the page opens."""
        episode_dir, _ = self._validate_episode(rel)
        metrics = self._load_seam_metrics(self._resolver.root)
        path = metrics.scorecard_path(episode_dir)
        if not path.is_file():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None

    def _write_seam_scores(self, episode_dir: Path, lang: str) -> None:
        """Score the just-built episode's 首尾帧承接 seams and persist the sidecar so the
        dashboard renders the last generation instantly — but do it on a BACKGROUND
        thread so it never adds to the concat's response time. Scoring rebuilds isolated
        seam pairs + runs optical flow (~tens of seconds); running it inline would make
        每次「拼接成片」感觉卡住/超时. The reel (ep{NN}.mp4) is already written by the time
        this is spawned; the score sidecar simply appears a little later."""
        if not (episode_dir / _SEAM_PLAN_FILE).is_file():
            return
        import threading

        root = self._resolver.root
        rife_exe = self._resolve_rife_exe()

        def _job() -> None:
            try:
                metrics = self._load_seam_metrics(root)
                card = metrics.compute_scorecard(episode_dir, lang, False, rife_exe)
                if card.get("seams"):
                    metrics.save_scorecard(
                        episode_dir, card,
                        datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    )
            except Exception:  # scoring is a nicety; never let it surface anywhere
                return

        threading.Thread(target=_job, name="seam-score", daemon=True).start()

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

    def _select_clip(self, shot_dir: Path) -> Path | None:
        """The clean clip representing this shot: the user-locked selected take
        `shot{NN}.mp4` in the shot-folder root (written by `select-takes`) if
        present, else the newest raw take under `renders/`. Never a burned
        subtitle master — concat is subtitle-free (follow-up 147)."""
        locked = shot_dir / f"{shot_dir.name}{_MP4_EXT}"
        if locked.is_file() and not locked.is_symlink():
            return locked
        return newest_render(shot_dir)

    def _approx_eff(
        self, ffmpeg: str, inputs: list[Path],
        head_trims: list[float], tail_trims: list[float],
    ) -> list[float]:
        """Per-clip kept duration for the segments manifest on the RIFE/plan
        paths (the stitch is done by the external tool, so durations are
        re-probed here): `probe(dur) - head - tail`, floored. Marked approximate
        in the manifest — dialogue never sits at a seam, so sub-frame error at
        the joins is irrelevant to cue alignment."""
        out: list[float] = []
        for i, src in enumerate(inputs):
            dur = self._probe_duration(ffmpeg, src)
            h = head_trims[i] if i < len(head_trims) else 0.0
            tl = tail_trims[i] if i < len(tail_trims) else 0.0
            out.append(max(0.1, dur - h - tl))
        return out

    def _write_segments(
        self, out_path: Path, used: list[ShotClip], eff: list[float], approx: bool,
    ) -> str | None:
        """Write `ep{NN}.segments.json` — each shot's [start,end) in the final
        stitched timeline, cumulative over `eff`. Returns its rel path, or None
        when durations are unknown (e.g. an unresolved input)."""
        if not eff or len(eff) != len(used):
            return None
        segments: list[dict[str, object]] = []
        cursor = 0.0
        for clip, e in zip(used, eff):
            start = round(cursor, 3)
            cursor += e
            segments.append({
                "shot": clip.shot,
                "start_s": start,
                "end_s": round(cursor, 3),
                "dur_s": round(e, 3),
            })
        seg_path = out_path.with_suffix(_SEGMENTS_SUFFIX)
        seg_path.write_text(
            json.dumps(
                {"version": 1, "approx": approx, "total_s": round(cursor, 3),
                 "segments": segments},
                ensure_ascii=False, indent=2,
            ),
            encoding="utf-8",
        )
        return self._rel(seg_path)

    def _ffmpeg_concat(
        self,
        ffmpeg: str,
        inputs: list[Path],
        out_path: Path,
        head_trims: list[float],
        tail_trims: list[float],
    ) -> list[float]:
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
        return eff

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
