"""Infrastructure-side exceptions raised by the media writer/reader.

Per follow-up 067 (Single Responsibility Principle): exception classes
do not belong in the writer/reader file. They live here, one file per
aggregate, mirroring the `libs/domain/errors/media__error.py` layout
on the domain side. Commands catch these infra exceptions and re-raise
as named domain errors.
"""
from __future__ import annotations


class InvalidPath(Exception):
    pass

class NotFound(Exception):
    pass

class NotMedia(Exception):
    pass

class AlreadyArchived(Exception):
    pass

class NotInArchive(Exception):
    pass

class AlreadyDeleted(Exception):
    pass

class NotInAiVideos(Exception):
    pass

class NotInDeleted(Exception):
    pass

class TargetExists(Exception):
    pass

class MoveFailed(Exception):
    pass

class InvalidDramaPath(Exception):
    pass

class DramaNotFound(Exception):
    pass
