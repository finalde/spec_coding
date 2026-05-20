"""Infrastructure-side exceptions raised by the novel writer/reader.

Per follow-up 067 (SRP): infrastructure errors live in their own file,
mirroring the domain side. Commands catch these and re-raise as named
domain errors.
"""
from __future__ import annotations


class SourceUnreachable(Exception):
    pass


class ChapterIndexParseFailed(Exception):
    pass


class DownloadFailed(Exception):
    pass


class NovelMetaCorrupt(Exception):
    pass
