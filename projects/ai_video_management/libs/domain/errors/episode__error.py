"""Named domain errors for episode-level shot concatenation.

One episode-concat operation stitches each shot's newest `renders/` mp4 into
a single `ep{NN}.mp4`. Each error class is a distinct named subclass of the
base, mapped to an HTTP `detail.kind` string by app_factory's handlers.
"""
from __future__ import annotations


class EpisodeDomainError(Exception):
    """Base for episode-concat pipeline errors."""


class InvalidEpisodePathError(EpisodeDomainError):
    """Path is empty, outside sandbox, or otherwise malformed."""


class NotEpisodePathError(EpisodeDomainError):
    """Path is not under `ai_videos/{drama}/episodes/ep{NN}/`."""


class EpisodeNotFoundError(EpisodeDomainError):
    """Resolved episode directory does not exist."""


class NoShotsError(EpisodeDomainError):
    """Episode has no `shots/` folder, or it contains no shot{NN} subfolders."""


class NoShotVideosError(EpisodeDomainError):
    """No shot contributed a renders/ mp4 — nothing to concatenate."""


class EpisodeFfmpegMissingError(EpisodeDomainError):
    """ffmpeg binary unavailable on this host."""


class EpisodeConcatFailedError(EpisodeDomainError):
    """ffmpeg concat invocation failed; no output produced."""
