"""DownloadsMapper — DAO↔Cdto translation for the downloads importer."""
from __future__ import annotations

from libs.application.dtos.downloads__dto import ImportFromDownloadsResultCdto
from libs.infrastructure.writers.downloads__writer import ImportResult


class DownloadsMapper:
    @staticmethod
    def to_cdto(r: ImportResult) -> ImportFromDownloadsResultCdto:
        rename = r.rename if r.rename is not None else {"renamed": [], "skipped": [], "errors": []}
        return ImportFromDownloadsResultCdto(
            moved=list(r.moved),
            unmatched=list(r.unmatched),
            errors=list(r.errors),
            rename=rename,
        )
