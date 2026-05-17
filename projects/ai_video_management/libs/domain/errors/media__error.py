"""Named domain errors for media-file operations (archive / delete / rename / hard-delete)."""
from __future__ import annotations


class MediaDomainError(Exception):
    """Base for all Media-aggregate domain errors."""


class InvalidMediaPathError(MediaDomainError):
    """The path string is empty or otherwise malformed."""


class NotMediaError(MediaDomainError):
    """The extension is not in the media allowlist."""


class MediaNotFoundError(MediaDomainError):
    """The file does not exist on disk or is a symlink."""


class AlreadyArchivedError(MediaDomainError):
    """File is already inside an archive/ folder."""


class NotInArchiveError(MediaDomainError):
    """unarchive requires the file to be inside an archive/ folder."""


class AlreadyDeletedError(MediaDomainError):
    """File is already under _deleted/."""


class NotUnderAiVideosError(MediaDomainError):
    """delete only operates on paths under ai_videos/."""


class NotUnderDeletedError(MediaDomainError):
    """hard_delete only operates on paths under ai_videos/_deleted/."""
