"""Novel downloader: scrape canonical novels from sudugu.org into novels/{slug}/.

Per follow-up 096. State machine per novel:
  1. GET /{source_id}/ — parse chapter index (<div id="list" class="dir clear">).
  2. For each chapter <li><a href="/{source_id}/{chapter_id}.html">第N章 标题</a></li>:
     a. Skip if `_meta.json[chapters][idx].done == True`.
     b. Fetch chapter; follow `下一页` pagination until no more pages.
     c. Extract <p> blocks from <div class="con">.
     d. Append `\n## 第N章 标题\n\n{body}\n` to novels/{slug}/{slug}.md.
     e. Atomic-write updated _meta.json (tmp → os.replace).
  3. `complete: true` IFF every chapter's `done` flag is True.

Resumable: re-running reads _meta.json, skips done chapters, resumes from next gap.
Rate limit: 0.8 s between requests; exponential backoff on 429 / 5xx (up to 3 retries).
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

import httpx

from libs.domain.value_objects.novel__valueobject import CANONICAL_NOVELS, NovelSpec, categories, find_novel
from libs.infrastructure.errors.novel__error import (
    ChapterIndexParseFailed,
    DownloadFailed,
    SourceUnreachable,
)

_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
_REQUEST_TIMEOUT = 20.0
_INTER_REQUEST_DELAY = 0.8
_MAX_RETRIES = 3
_BACKOFF_BASE = 1.5

_INDEX_LIST_RE = re.compile(
    r'<div\s+id="list"\s+class="dir\s+clear">(.*?)</div>',
    re.DOTALL,
)
_CHAPTER_LINK_RE = re.compile(
    r'<li><a\s+href="(/\d+/\d+\.html)">([^<]+)</a></li>',
)
_CONTENT_BLOCK_RE = re.compile(
    r'<div\s+class="con">(.*?)</div>',
    re.DOTALL,
)
_P_TAG_RE = re.compile(r'<p[^>]*>(.*?)</p>', re.DOTALL)
_HTML_TAG_RE = re.compile(r'<[^>]+>')
_NEXT_PAGE_RE = re.compile(
    r'<a\s+href="(/\d+/\d+-\d+\.html)">下一页</a>',
)
_INDEX_PAGE_OPTIONS_RE = re.compile(
    r'<select\s+id="pageSelect"[^>]*>(.*?)</select>',
    re.DOTALL,
)
_INDEX_PAGE_OPTION_RE = re.compile(r'<option\s+value="(\d+)"', re.IGNORECASE)


@dataclass
class ChapterRecord:
    idx: int
    title: str
    url: str
    done: bool = False
    hash: str | None = None
    error: str | None = None

    def to_json(self) -> dict[str, object]:
        return {
            "idx": self.idx,
            "title": self.title,
            "url": self.url,
            "done": self.done,
            "hash": self.hash,
            "error": self.error,
        }

    @classmethod
    def from_json(cls, data: dict[str, object]) -> "ChapterRecord":
        return cls(
            idx=int(data["idx"]),
            title=str(data["title"]),
            url=str(data["url"]),
            done=bool(data.get("done", False)),
            hash=data.get("hash") if data.get("hash") is not None else None,  # type: ignore[arg-type]
            error=data.get("error") if data.get("error") is not None else None,  # type: ignore[arg-type]
        )


@dataclass
class NovelMeta:
    slug: str
    title_zh: str
    author: str
    category: str
    category_zh: str
    source_host: str
    source_id: str
    chapters: list[ChapterRecord] = field(default_factory=list)
    complete: bool = False
    last_updated_at: str = ""

    def to_json(self) -> dict[str, object]:
        return {
            "slug": self.slug,
            "title_zh": self.title_zh,
            "author": self.author,
            "category": self.category,
            "category_zh": self.category_zh,
            "source_host": self.source_host,
            "source_id": self.source_id,
            "complete": self.complete,
            "last_updated_at": self.last_updated_at,
            "chapters": [c.to_json() for c in self.chapters],
        }

    @classmethod
    def from_json(cls, data: dict[str, object]) -> "NovelMeta":
        return cls(
            slug=str(data["slug"]),
            title_zh=str(data["title_zh"]),
            author=str(data.get("author", "")),
            category=str(data.get("category", "xianxia")),
            category_zh=str(data.get("category_zh", "仙侠")),
            source_host=str(data["source_host"]),
            source_id=str(data["source_id"]),
            chapters=[ChapterRecord.from_json(c) for c in data.get("chapters", [])],  # type: ignore[arg-type]
            complete=bool(data.get("complete", False)),
            last_updated_at=str(data.get("last_updated_at", "")),
        )


@dataclass
class NovelDownloadResult:
    slug: str
    title_zh: str
    category: str
    category_zh: str
    chapters_done: int
    chapters_total: int
    complete: bool
    errors: list[str] = field(default_factory=list)


@dataclass
class _NovelState:
    spec: NovelSpec
    meta: NovelMeta
    meta_path: Path
    body_path: Path


class NovelDownloader:
    def __init__(
        self,
        novels_root: Path,
        client: httpx.Client | None = None,
        delay_seconds: float = _INTER_REQUEST_DELAY,
        max_retries: int = _MAX_RETRIES,
    ) -> None:
        self._root = novels_root
        self._owns_client = client is None
        self._client = client or httpx.Client(
            timeout=_REQUEST_TIMEOUT,
            headers={"User-Agent": _USER_AGENT, "Accept-Language": "zh-CN,zh;q=0.9"},
            follow_redirects=True,
        )
        self._delay = delay_seconds
        self._max_retries = max_retries
        self._last_request_at = 0.0

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> "NovelDownloader":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def download_all(self, on_progress: object = None) -> list[NovelDownloadResult]:
        """Serial download: complete novel N (every chapter `done=True`)
        before starting novel N+1.

        Reverted from the round-robin design in follow-up 103 per follow-up
        104: the user explicitly only wants completed novels in the sidebar.
        Serial → one novel finishes → it pops into the (complete-only) tree
        filter → next novel starts.
        """
        results: list[NovelDownloadResult] = []
        for spec in CANONICAL_NOVELS:
            try:
                result = self.download(spec.slug, on_progress=on_progress)
            except Exception as exc:
                result = NovelDownloadResult(
                    slug=spec.slug,
                    title_zh=spec.title_zh,
                    category=spec.category,
                    category_zh=spec.category_zh,
                    chapters_done=0,
                    chapters_total=0,
                    complete=False,
                    errors=[f"top-level: {type(exc).__name__}: {exc}"],
                )
            results.append(result)
            self._write_index_md(results + self._stub_results_for_remaining(spec))
        return results

    def _stub_results_for_remaining(self, last_done: NovelSpec) -> list[NovelDownloadResult]:
        """Build placeholder rows for novels that haven't been touched yet
        so _index.md still lists every canonical novel (with 0/0 progress)
        between download_all iterations.
        """
        passed_last = False
        out: list[NovelDownloadResult] = []
        for spec in CANONICAL_NOVELS:
            if not passed_last:
                if spec.slug == last_done.slug:
                    passed_last = True
                continue
            out.append(
                NovelDownloadResult(
                    slug=spec.slug,
                    title_zh=spec.title_zh,
                    category=spec.category,
                    category_zh=spec.category_zh,
                    chapters_done=0,
                    chapters_total=0,
                    complete=False,
                )
            )
        return out

    def download(self, slug: str, on_progress: object = None) -> NovelDownloadResult:
        spec = find_novel(slug)
        state = self._ensure_index(spec)
        errors: list[str] = []
        while True:
            next_ch = next((c for c in state.meta.chapters if not c.done), None)
            if next_ch is None:
                break
            ok, err = self._download_one_chapter(state, next_ch, on_progress)
            if not ok and err is not None:
                errors.append(err)
        done = sum(1 for c in state.meta.chapters if c.done)
        state.meta.complete = done == len(state.meta.chapters) and len(state.meta.chapters) > 0
        self._write_meta(state.meta_path, state.meta)
        return NovelDownloadResult(
            slug=spec.slug,
            title_zh=spec.title_zh,
            category=spec.category,
            category_zh=spec.category_zh,
            chapters_done=done,
            chapters_total=len(state.meta.chapters),
            complete=state.meta.complete,
            errors=errors,
        )

    def _ensure_index(self, spec: NovelSpec) -> "_NovelState":
        novel_dir = self._root / spec.category / spec.slug
        novel_dir.mkdir(parents=True, exist_ok=True)
        meta_path = novel_dir / "_meta.json"
        body_path = novel_dir / f"{spec.slug}.md"
        meta = self._load_or_init_meta(meta_path, spec)
        fresh_index = self._fetch_chapter_index(spec)
        if not meta.chapters:
            meta.chapters = fresh_index
            self._write_meta(meta_path, meta)
            body_path.write_text(
                f"# {spec.title_zh}\n\n作者：{spec.author}\n\n来源：{spec.source_host}/{spec.source_id}/\n\n",
                encoding="utf-8",
            )
        elif len(fresh_index) > len(meta.chapters):
            for new_ch in fresh_index[len(meta.chapters):]:
                meta.chapters.append(new_ch)
            self._write_meta(meta_path, meta)
        meta.complete = (
            len(meta.chapters) > 0 and all(c.done for c in meta.chapters)
        )
        self._write_meta(meta_path, meta)
        return _NovelState(spec=spec, meta=meta, meta_path=meta_path, body_path=body_path)

    def _download_one_chapter(
        self,
        state: "_NovelState",
        chapter: ChapterRecord,
        on_progress: object,
    ) -> tuple[bool, str | None]:
        try:
            body_text = self._fetch_chapter_full(state.spec, chapter)
        except Exception as exc:
            chapter.error = f"{type(exc).__name__}: {exc}"
            self._write_meta(state.meta_path, state.meta)
            return False, f"{state.spec.slug} ch{chapter.idx}: {chapter.error}"
        block = f"\n## {chapter.title}\n\n{body_text}\n"
        with state.body_path.open("a", encoding="utf-8") as fh:
            fh.write(block)
        chapter.done = True
        chapter.error = None
        chapter.hash = hashlib.sha256(body_text.encode("utf-8")).hexdigest()[:16]
        state.meta.last_updated_at = time.strftime("%Y-%m-%dT%H:%M:%S")
        self._write_meta(state.meta_path, state.meta)
        if callable(on_progress):
            on_progress(state.spec.slug, chapter.idx, len(state.meta.chapters))  # type: ignore[misc]
        return True, None

    def _load_or_init_meta(self, meta_path: Path, spec: NovelSpec) -> NovelMeta:
        if meta_path.is_file():
            try:
                data = json.loads(meta_path.read_text(encoding="utf-8"))
                return NovelMeta.from_json(data)
            except (json.JSONDecodeError, KeyError):
                pass
        return NovelMeta(
            slug=spec.slug,
            title_zh=spec.title_zh,
            author=spec.author,
            category=spec.category,
            category_zh=spec.category_zh,
            source_host=spec.source_host,
            source_id=spec.source_id,
            chapters=[],
            complete=False,
        )

    def _write_meta(self, meta_path: Path, meta: NovelMeta) -> None:
        tmp = meta_path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(meta.to_json(), ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tmp, meta_path)

    def _fetch_chapter_index(self, spec: NovelSpec) -> list[ChapterRecord]:
        base = f"https://www.{spec.source_host}/{spec.source_id}/"
        first_html = self._http_get(base)
        pages_to_fetch = self._discover_index_pages(first_html, spec)
        all_links: list[tuple[str, str]] = []
        seen_urls: set[str] = set()
        all_links.extend(self._parse_index_links(first_html, base))
        for url in pages_to_fetch:
            html = self._http_get(url)
            for rel_url, title in self._parse_index_links(html, url):
                all_links.append((rel_url, title))
        if not all_links:
            raise ChapterIndexParseFailed(f"no chapter links found in index at {base}")
        records: list[ChapterRecord] = []
        for rel_url, title in all_links:
            if rel_url in seen_urls:
                continue
            seen_urls.add(rel_url)
            records.append(
                ChapterRecord(
                    idx=len(records) + 1,
                    title=title.strip(),
                    url=f"https://www.{spec.source_host}{rel_url}",
                )
            )
        return records

    def _parse_index_links(self, html: str, page_url: str) -> list[tuple[str, str]]:
        m = _INDEX_LIST_RE.search(html)
        if m is None:
            raise ChapterIndexParseFailed(f"index list block not found at {page_url}")
        return _CHAPTER_LINK_RE.findall(m.group(1))

    def _discover_index_pages(self, first_html: str, spec: NovelSpec) -> list[str]:
        opts_match = _INDEX_PAGE_OPTIONS_RE.search(first_html)
        if opts_match is None:
            return []
        page_numbers: list[int] = []
        for raw in _INDEX_PAGE_OPTION_RE.findall(opts_match.group(1)):
            try:
                n = int(raw)
            except ValueError:
                continue
            if n >= 2:
                page_numbers.append(n)
        page_numbers = sorted(set(page_numbers))
        return [
            f"https://www.{spec.source_host}/{spec.source_id}/p-{n}.html"
            for n in page_numbers
        ]

    def _fetch_chapter_full(self, spec: NovelSpec, chapter: ChapterRecord) -> str:
        parts: list[str] = []
        current_url = chapter.url
        visited: set[str] = set()
        while current_url:
            if current_url in visited:
                break
            visited.add(current_url)
            if len(visited) > 30:
                raise DownloadFailed(f"runaway pagination at {current_url}")
            html = self._http_get(current_url)
            cm = _CONTENT_BLOCK_RE.search(html)
            if cm is None:
                raise DownloadFailed(f"content block not found at {current_url}")
            body_html = cm.group(1)
            parts.append(self._extract_paragraphs(body_html))
            nm = _NEXT_PAGE_RE.search(html)
            if nm is None:
                break
            next_rel = nm.group(1)
            current_url = f"https://www.{spec.source_host}{next_rel}"
        return "\n\n".join(p for p in parts if p)

    def _extract_paragraphs(self, body_html: str) -> str:
        paragraphs: list[str] = []
        for raw in _P_TAG_RE.findall(body_html):
            text = _HTML_TAG_RE.sub("", raw).strip()
            text = (
                text.replace("&nbsp;", " ")
                .replace("&amp;", "&")
                .replace("&lt;", "<")
                .replace("&gt;", ">")
                .replace("&quot;", '"')
                .replace("&#39;", "'")
            )
            if text:
                paragraphs.append(text)
        return "\n\n".join(paragraphs)

    def _http_get(self, url: str) -> str:
        elapsed = time.monotonic() - self._last_request_at
        if elapsed < self._delay:
            time.sleep(self._delay - elapsed)
        last_exc: Exception | None = None
        for attempt in range(self._max_retries + 1):
            try:
                r = self._client.get(url)
            except httpx.HTTPError as exc:
                last_exc = exc
                self._sleep_backoff(attempt)
                continue
            finally:
                self._last_request_at = time.monotonic()
            if r.status_code == 200:
                return r.text
            if r.status_code in (429, 500, 502, 503, 504):
                last_exc = SourceUnreachable(f"http {r.status_code} at {url}")
                self._sleep_backoff(attempt)
                continue
            raise SourceUnreachable(f"http {r.status_code} at {url}")
        assert last_exc is not None
        raise SourceUnreachable(f"retries exhausted for {url}: {last_exc}")

    def _sleep_backoff(self, attempt: int) -> None:
        time.sleep(_BACKOFF_BASE ** attempt)

    def _write_index_md(self, results: Iterable[NovelDownloadResult]) -> None:
        by_cat: dict[str, list[NovelDownloadResult]] = {}
        cat_zh: dict[str, str] = {}
        for r in results:
            by_cat.setdefault(r.category, []).append(r)
            cat_zh[r.category] = r.category_zh
        lines = ["# 小说下载索引", ""]
        for cat_slug, cat_label in categories():
            entries = by_cat.get(cat_slug, [])
            if not entries:
                continue
            lines.append(f"## {cat_label}")
            lines.append("")
            lines.append("| 状态 | 标题 | 进度 |")
            lines.append("|---|---|---|")
            for r in entries:
                badge = "✅ 完结" if r.complete else f"⏳ 下载中 ({r.chapters_done}/{r.chapters_total})"
                lines.append(
                    f"| {badge} | [{r.title_zh}]({r.category}/{r.slug}/{r.slug}.md) | "
                    f"{r.chapters_done}/{r.chapters_total} |"
                )
            lines.append("")
        lines.append(f"_最后更新：{time.strftime('%Y-%m-%d %H:%M:%S')}_")
        (self._root / "_index.md").write_text("\n".join(lines), encoding="utf-8")


__all__ = [
    "ChapterRecord",
    "NovelDownloader",
    "NovelDownloadResult",
    "NovelMeta",
]
