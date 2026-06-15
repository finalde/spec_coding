"""Named domain errors for subtitle burn-in / scaffolding.

Video-path validation reuses the frame aggregate's errors
(InvalidVideoPathError / NotVideoError / VideoNotFoundError /
FfmpegMissingError) — the validation shape is identical.
"""
from __future__ import annotations


class SubtitleDomainError(Exception):
    """Base for subtitle domain errors."""


class SubtitleFileMissingError(SubtitleDomainError):
    """No `subtitles.md` found in the shot folder for this render."""


class EmptySubtitlesError(SubtitleDomainError):
    """`subtitles.md` exists but contains no parseable cue lines."""


class SubtitleAlreadyExistsError(SubtitleDomainError):
    """Scaffold refused — a non-empty `subtitles.md` already exists."""


class BurnFailedError(SubtitleDomainError):
    """ffmpeg ran but failed to produce the subtitled mp4."""
