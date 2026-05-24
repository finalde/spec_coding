"""DAO mirroring the on-disk Legado 3.0 book-source JSON shape.

Only the fields the reader actually consumes are modelled; unknown fields
are dropped on `from_legado_json`. Snake-case attributes map to Legado's
camelCase keys.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class LegadoTocRulesDao:
    chapter_list: str = ""
    chapter_name: str = ""
    chapter_url: str = ""
    next_toc_url: str = ""


@dataclass(frozen=True)
class LegadoContentRulesDao:
    content: str = ""
    next_content_url: str = ""
    replace_regex: str = ""


@dataclass(frozen=True)
class LegadoBookInfoRulesDao:
    name: str = ""
    author: str = ""
    intro: str = ""
    kind: str = ""
    cover_url: str = ""
    toc_url: str = ""
    last_chapter: str = ""


@dataclass(frozen=True)
class LegadoSearchRulesDao:
    book_list: str = ""
    name: str = ""
    author: str = ""
    book_url: str = ""
    cover_url: str = ""
    intro: str = ""
    kind: str = ""
    last_chapter: str = ""


@dataclass(frozen=True)
class LegadoSourceDao:
    book_source_url: str
    book_source_name: str
    header: dict[str, str] = field(default_factory=dict)
    search_url: str = ""
    rule_toc: LegadoTocRulesDao = field(default_factory=LegadoTocRulesDao)
    rule_content: LegadoContentRulesDao = field(default_factory=LegadoContentRulesDao)
    rule_book_info: LegadoBookInfoRulesDao = field(default_factory=LegadoBookInfoRulesDao)
    rule_search: LegadoSearchRulesDao = field(default_factory=LegadoSearchRulesDao)

    @classmethod
    def from_legado_json(cls, raw: dict[str, Any]) -> "LegadoSourceDao":
        toc = raw.get("ruleToc") or {}
        content = raw.get("ruleContent") or {}
        info = raw.get("ruleBookInfo") or {}
        search = raw.get("ruleSearch") or {}
        header_raw = raw.get("header") or ""
        header: dict[str, str]
        if isinstance(header_raw, dict):
            header = {str(k): str(v) for k, v in header_raw.items()}
        else:
            header = {}
        return cls(
            book_source_url=str(raw.get("bookSourceUrl", "")),
            book_source_name=str(raw.get("bookSourceName", "")),
            header=header,
            search_url=str(raw.get("searchUrl", "")),
            rule_toc=LegadoTocRulesDao(
                chapter_list=str(toc.get("chapterList", "")),
                chapter_name=str(toc.get("chapterName", "")),
                chapter_url=str(toc.get("chapterUrl", "")),
                next_toc_url=str(toc.get("nextTocUrl", "")),
            ),
            rule_content=LegadoContentRulesDao(
                content=str(content.get("content", "")),
                next_content_url=str(content.get("nextContentUrl", "")),
                replace_regex=str(content.get("replaceRegex", "")),
            ),
            rule_book_info=LegadoBookInfoRulesDao(
                name=str(info.get("name", "")),
                author=str(info.get("author", "")),
                intro=str(info.get("intro", "")),
                kind=str(info.get("kind", "")),
                cover_url=str(info.get("coverUrl", "")),
                toc_url=str(info.get("tocUrl", "")),
                last_chapter=str(info.get("lastChapter", "")),
            ),
            rule_search=LegadoSearchRulesDao(
                book_list=str(search.get("bookList", "")),
                name=str(search.get("name", "")),
                author=str(search.get("author", "")),
                book_url=str(search.get("bookUrl", "")),
                cover_url=str(search.get("coverUrl", "")),
                intro=str(search.get("intro", "")),
                kind=str(search.get("kind", "")),
                last_chapter=str(search.get("lastChapter", "")),
            ),
        )


__all__ = [
    "LegadoBookInfoRulesDao",
    "LegadoContentRulesDao",
    "LegadoSearchRulesDao",
    "LegadoSourceDao",
    "LegadoTocRulesDao",
]
