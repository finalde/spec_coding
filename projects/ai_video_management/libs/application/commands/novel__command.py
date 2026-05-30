"""Novel-aggregate commands: download a single novel or every canonical novel.

Per follow-up 096: scrape canonical novels from sudugu.org.
"""
from __future__ import annotations

from libs.application.dtos.novel__dto import NovelDownloadResultCdto
from libs.application.mappers.novel__mapper import NovelMapper
from libs.infrastructure.writers.novel__writer import NovelDownloader


class NovelCommand:
    def __init__(self, downloader: NovelDownloader) -> None:
        self._downloader = downloader

    def download(self, slug: str) -> NovelDownloadResultCdto:
        return NovelMapper.download_to_cdto(self._downloader.download(slug))

    def download_all(self) -> list[NovelDownloadResultCdto]:
        return [NovelMapper.download_to_cdto(r) for r in self._downloader.download_all()]
