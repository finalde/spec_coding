"""Infrastructure-side exceptions raised by the character_video writer/reader.

Per follow-up 067 (Single Responsibility Principle): exception classes
do not belong in the writer/reader file. They live here, one file per
aggregate, mirroring the `libs/domain/errors/character_video__error.py` layout
on the domain side. Commands catch these infra exceptions and re-raise
as named domain errors.
"""
from __future__ import annotations


class InvalidPath(Exception):
    """Path failed sandbox / shape validation (both operations)."""

class NotFound(Exception):
    """File does not exist on disk (both operations)."""

class FfmpegMissing(Exception):
    """imageio_ffmpeg.get_ffmpeg_exe() failed (both operations)."""

class NotCharacterVideo(Exception):
    pass

class TruncateFailed(Exception):
    pass

class NotShotMd(Exception):
    pass

class NoCharacterTable(Exception):
    pass

class ConcatFailed(Exception):
    pass

class ViewExtractFailed(Exception):
    pass

class AudioExtractFailed(Exception):
    pass
