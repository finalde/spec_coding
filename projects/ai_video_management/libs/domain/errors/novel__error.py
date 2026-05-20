"""Named domain errors for novel downloads (follow-up 096)."""
from __future__ import annotations


class NovelDomainError(Exception):
    """Base for novel-download domain errors."""


class NovelNotFoundError(NovelDomainError):
    """The slug does not match any entry in CANONICAL_NOVELS."""


class NovelSourceUnreachableError(NovelDomainError):
    """The source host could not be reached after retries."""


class NovelChapterIndexParseError(NovelDomainError):
    """The chapter-index page could not be parsed into a chapter list."""


class NovelDownloadFailedError(NovelDomainError):
    """At least one chapter failed to download after retries; novel is incomplete."""
