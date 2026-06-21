"""Named domain errors for episode-level BGM cue management + burn.

A burn muxes a sparse multi-cue `episodes/ep{NN}/bgm/bgm.md` timeline onto the
subtitled episode master `ep{NN}_zh.mp4`, producing `ep{NN}_zh_bgm.mp4`. Each
error is a distinct named subclass mapped to an HTTP `detail.kind` by
app_factory's handlers.
"""
from __future__ import annotations


class EpisodeBgmDomainError(Exception):
    """Base for episode-BGM pipeline errors."""


class InvalidEpisodeBgmPathError(EpisodeBgmDomainError):
    """Path is empty, outside sandbox, or otherwise malformed."""


class NotEpisodeBgmPathError(EpisodeBgmDomainError):
    """Path is not under `ai_videos/{drama}/episodes/ep{NN}/`."""


class EpisodeBgmCueFileMissingError(EpisodeBgmDomainError):
    """The episode's `bgm/bgm.md` cue timeline does not exist."""


class BgmCueNotFoundError(EpisodeBgmDomainError):
    """No cue line matches the requested time window."""


class InvalidBgmCueError(EpisodeBgmDomainError):
    """A cue value (window / category / vol) is malformed."""


class NoAssignedBgmCuesError(EpisodeBgmDomainError):
    """No cue has a `bgm_NNNN` assigned — nothing to mux."""


class SubtitledEpisodeMissingError(EpisodeBgmDomainError):
    """The source `ep{NN}_zh.mp4` subtitled master does not exist yet."""


class BgmTrackAudioMissingError(EpisodeBgmDomainError):
    """An assigned `bgm_NNNN` has no rendered mp3 in the shared library."""


class EpisodeBgmFfmpegMissingError(EpisodeBgmDomainError):
    """ffmpeg binary unavailable on this host."""


class EpisodeBgmMuxFailedError(EpisodeBgmDomainError):
    """ffmpeg mux invocation failed; no output produced."""
