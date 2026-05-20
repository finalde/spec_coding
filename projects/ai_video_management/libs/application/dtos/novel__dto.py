"""Novel-aggregate DTOs (follow-up 096): Q-side status payloads and C-side
download-result payloads.

Qdto = NovelStatusQdto (one per novel surfaced on GET /api/novels).
Cdto = NovelDownloadResultCdto (one per slug returned by NovelCommand.download*).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class NovelStatusQdto:
    slug: str
    title_zh: str
    author: str
    category: str
    category_zh: str
    source_host: str
    source_id: str
    chapters_total: int
    chapters_done: int
    complete: bool
    last_updated_at: str

    def to_payload(self) -> dict[str, Any]:
        return {
            "slug": self.slug,
            "title_zh": self.title_zh,
            "author": self.author,
            "category": self.category,
            "category_zh": self.category_zh,
            "source_host": self.source_host,
            "source_id": self.source_id,
            "chapters_total": self.chapters_total,
            "chapters_done": self.chapters_done,
            "complete": self.complete,
            "last_updated_at": self.last_updated_at,
        }


@dataclass(frozen=True)
class NovelDownloadResultCdto:
    slug: str
    title_zh: str
    category: str
    category_zh: str
    chapters_done: int
    chapters_total: int
    complete: bool
    errors: list[str]

    def to_payload(self) -> dict[str, Any]:
        return {
            "slug": self.slug,
            "title_zh": self.title_zh,
            "category": self.category,
            "category_zh": self.category_zh,
            "chapters_done": self.chapters_done,
            "chapters_total": self.chapters_total,
            "complete": self.complete,
            "errors": list(self.errors),
        }
