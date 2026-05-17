"""Named domain errors for character-video truncation and shot-character concat.

Both features share the same ffmpeg lifecycle, so they share an errors module.
Each error class is a distinct named subclass of the base, used by routes.py
to map to an HTTP `detail.kind` string.
"""
from __future__ import annotations


class CharacterVideoDomainError(Exception):
    """Base for character-video pipeline errors (truncate + concat)."""


# --- Truncate (Feature 1) ---------------------------------------------------


class InvalidCharacterVideoPathError(CharacterVideoDomainError):
    """Path is empty, outside sandbox, or otherwise malformed."""


class NotCharacterVideoError(CharacterVideoDomainError):
    """Extension is not a video type, or path is not under
    `ai_videos/{drama}/characters/{cN_xxx}/`."""


class CharacterVideoNotFoundError(CharacterVideoDomainError):
    """Source mp4 file does not exist."""


class FfmpegMissingForCharacterVideoError(CharacterVideoDomainError):
    """ffmpeg binary unavailable on this host."""


class TruncateFailedError(CharacterVideoDomainError):
    """ffmpeg ran but the 2-second cut could not be produced."""


# --- Concat (Feature 2) -----------------------------------------------------


class InvalidShotMdPathError(CharacterVideoDomainError):
    """Path is empty, outside sandbox, or otherwise malformed."""


class NotShotMdError(CharacterVideoDomainError):
    """Path does not end in .md, or is not under a `prompts/shot{NN}/` folder."""


class ShotMdNotFoundError(CharacterVideoDomainError):
    """Shot md file does not exist."""


class NoCharacterTableError(CharacterVideoDomainError):
    """Shot md has no recognisable 出场角色 / Characters in this shot table."""


class ConcatFailedError(CharacterVideoDomainError):
    """ffmpeg concat invocation failed; no output produced."""
