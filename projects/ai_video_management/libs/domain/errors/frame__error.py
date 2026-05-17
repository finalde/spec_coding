"""Named domain errors for frame extraction."""
from __future__ import annotations


class FrameDomainError(Exception):
    """Base for frame-extraction domain errors."""


class InvalidVideoPathError(FrameDomainError):
    """Path is empty, not under sandbox, or is a symlink."""


class NotVideoError(FrameDomainError):
    """Extension is not in the video allowlist."""


class VideoNotFoundError(FrameDomainError):
    """File does not exist."""


class FfmpegMissingError(FrameDomainError):
    """ffmpeg binary unavailable on this host."""


class FrameExtractFailedError(FrameDomainError):
    """ffmpeg ran but every frame timestamp failed to produce a PNG."""
