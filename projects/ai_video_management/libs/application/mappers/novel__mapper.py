"""NovelMapper — translates infrastructure NovelDownloadResult / NovelMeta
into application-layer Cdtos / Qdtos.
"""
from __future__ import annotations

from libs.application.dtos.novel__dto import NovelDownloadResultCdto, NovelStatusQdto
from libs.infrastructure.writers.novel__writer import NovelDownloadResult, NovelMeta


class NovelMapper:
    @staticmethod
    def download_to_cdto(r: NovelDownloadResult) -> NovelDownloadResultCdto:
        return NovelDownloadResultCdto(
            slug=r.slug,
            title_zh=r.title_zh,
            category=r.category,
            category_zh=r.category_zh,
            chapters_done=r.chapters_done,
            chapters_total=r.chapters_total,
            complete=r.complete,
            errors=list(r.errors),
        )

    @staticmethod
    def meta_to_qdto(meta: NovelMeta) -> NovelStatusQdto:
        done = sum(1 for c in meta.chapters if c.done)
        return NovelStatusQdto(
            slug=meta.slug,
            title_zh=meta.title_zh,
            author=meta.author,
            category=meta.category,
            category_zh=meta.category_zh,
            source_host=meta.source_host,
            source_id=meta.source_id,
            chapters_total=len(meta.chapters),
            chapters_done=done,
            complete=meta.complete,
            last_updated_at=meta.last_updated_at,
        )
