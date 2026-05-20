"""Novel-aggregate commands: download a single novel or every canonical novel.

Per follow-up 096: scrape canonical novels from sudugu.org. Re-raises
infrastructure exceptions as named domain errors.
"""
from __future__ import annotations

from libs.application.dtos.novel__dto import NovelDownloadResultCdto
from libs.application.mappers.novel__mapper import NovelMapper
from libs.domain.errors.novel__error import (
    NovelChapterIndexParseError,
    NovelDownloadFailedError,
    NovelNotFoundError,
    NovelSourceUnreachableError,
)
from libs.infrastructure.errors.novel__error import (
    ChapterIndexParseFailed,
    DownloadFailed,
    SourceUnreachable,
)
from libs.infrastructure.writers.novel__writer import NovelDownloader


class NovelCommand:
    def __init__(self, downloader: NovelDownloader) -> None:
        self._downloader = downloader

    def download(self, slug: str) -> NovelDownloadResultCdto:
        try:
            result = self._downloader.download(slug)
        except SourceUnreachable as exc:
            raise NovelSourceUnreachableError(str(exc)) from exc
        except ChapterIndexParseFailed as exc:
            raise NovelChapterIndexParseError(str(exc)) from exc
        except DownloadFailed as exc:
            raise NovelDownloadFailedError(str(exc)) from exc
        except NovelNotFoundError:
            raise
        return NovelMapper.download_to_cdto(result)

    def download_all(self) -> list[NovelDownloadResultCdto]:
        results = self._downloader.download_all()
        return [NovelMapper.download_to_cdto(r) for r in results]
