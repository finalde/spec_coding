"""Named domain errors for text-file read / write operations.

The actual encoding rules (allowed extensions, MAX_FILE_BYTES, image-vs-text
extension allowlists) currently live in libs.common.exposed_tree and the
infrastructure FileReader / FileWriter classes — those are the policy
boundary. This module names the failure modes those classes raise so the
application layer can catch them with domain vocabulary rather than
catching infrastructure exception classes directly.
"""
from __future__ import annotations


class FileResourceDomainError(Exception):
    """Base for all file-resource domain errors."""


class UnsupportedFileExtensionError(FileResourceDomainError):
    """Extension not in the allowlist (for read or write per the boundary)."""


class FileTooLargeError(FileResourceDomainError):
    """File body exceeds MAX_FILE_BYTES."""


class FileNotInSandboxError(FileResourceDomainError):
    """Path resolves outside the EXPOSED_TREE sandbox."""


class StaleWriteError(FileResourceDomainError):
    """If-Unmodified-Since precondition failed — file was modified externally."""

    def __init__(self, current_mtime: float) -> None:
        super().__init__(f"stale_write: current_mtime={current_mtime}")
        self.current_mtime: float = current_mtime


class MissingIfUnmodifiedSinceError(FileResourceDomainError):
    """PUT to an existing file is required to carry an If-Unmodified-Since header."""


class InvalidBodyEncodingError(FileResourceDomainError):
    """Body bytes are not valid UTF-8 / contain a NUL in the first 16 bytes."""
