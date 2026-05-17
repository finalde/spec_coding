"""Named domain errors for downloads-import."""
from __future__ import annotations


class DownloadsDomainError(Exception):
    """Base for downloads-import domain errors."""


class DownloadsDirMissingError(DownloadsDomainError):
    """The OS Downloads folder cannot be read."""
