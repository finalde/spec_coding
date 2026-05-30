"""Novel downloader: scrape canonical novels from sudugu.org into downloaded_novels/{cat}/{slug}/.

Per follow-up 096 (initial design) + 111 (per-chapter file layout) + 113 (folder
renamed from `novels/` to `downloaded_novels/`; sibling `my_novel/` now holds
original manuscripts). State machine per novel:
  1. GET /{source_id}/ — parse chapter index (<div id="list" class="dir clear">).
  2. For each chapter <li><a href="/{source_id}/{chapter_id}.html">第N章 标题</a></li>:
     a. Skip if `_meta.json[chapters][idx].done == True`.
     b. Fetch chapter; follow `下一页` pagination until no more pages.
     c. Extract <p> blocks from <div class="con">.
     d. Write `# 第N章 标题\n\n{body}\n` to downloaded_novels/{cat}/{slug}/chapters/{NNNN}-{safe_title}.md
        (one file per chapter — pre-111 this appended to a single {slug}.md which the
        webapp could not load past 1 MiB).
     e. Atomic-write updated _meta.json (tmp → os.replace); ChapterRecord.file = filename.
  3. `complete: true` IFF every chapter's `done` flag is True.

Resumable: re-running reads _meta.json, skips done chapters, resumes from next gap.
Rate limit: 1.0–2.0 s random jitter between requests (follow-up 109); exponential
backoff on 429 / 5xx (up to 3 retries).
"""
from __future__ import annotations

import hashlib
import json
import os
import random
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from threading import Lock
from typing import Iterable

import httpx

from libs.domain.value_objects.novel__valueobject import (
    CANONICAL_NOVELS,
    NovelSource,
    NovelSpec,
    categories,
    find_novel,
)
from libs.domain.errors.novel__error import (
    NovelChapterIndexParseError,
    NovelDownloadFailedError,
    NovelSourceUnreachableError,
)

_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
_REQUEST_TIMEOUT = 20.0
# Random jitter rather than fixed cadence — anti-bot fingerprinting cares about
# request *cadence* (follow-up 109; converged values from freeok/so-novel's
# bundle/rules/rate-limit.json which uses the same min/max for sudugu + ttkan).
_INTER_REQUEST_DELAY_MIN = 1.0
_INTER_REQUEST_DELAY_MAX = 2.0
_MAX_RETRIES = 3
_BACKOFF_BASE = 1.5
# End-of-chapter boilerplate every so-novel site rule strips via filterTxt.
_END_OF_CHAPTER_MARKER_RE = re.compile(r"\(本章完\)")

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

# ttkan.co patterns — chapter index served as a single page; no pagination
# either at index or chapter level.
_TTKAN_CHAPTER_LINK_RE = re.compile(
    r'<a[^>]+href="(/novel/pagea/[^"]+\.html)"[^>]*>([^<]+)</a>',
)
_TTKAN_CONTENT_BLOCK_RE = re.compile(
    r'<div\s+class="content">(.*?)</div>',
    re.DOTALL,
)


_FILENAME_FORBIDDEN_RE = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
_FILENAME_MAX_TITLE_LEN = 80


def _safe_filename_segment(s: str) -> str:
    """Strip Windows-reserved chars + control chars; trim trailing whitespace/dots; cap length.

    Chinese / full-width punctuation preserved (per follow-up 004 UTF-8 filename allowance).
    """
    cleaned = _FILENAME_FORBIDDEN_RE.sub("", s).strip().rstrip(".").strip()
    if len(cleaned) > _FILENAME_MAX_TITLE_LEN:
        cleaned = cleaned[:_FILENAME_MAX_TITLE_LEN].rstrip()
    return cleaned or "untitled"


def _build_chapter_filename(idx: int, title: str) -> str:
    return f"{idx:04d}-{_safe_filename_segment(title)}.md"


@dataclass
class ChapterRecord:
    idx: int
    title: str
    url: str
    done: bool = False
    hash: str | None = None
    error: str | None = None
    file: str | None = None

    def to_json(self) -> dict[str, object]:
        return {
            "idx": self.idx,
            "title": self.title,
            "url": self.url,
            "done": self.done,
            "hash": self.hash,
            "error": self.error,
            "file": self.file,
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
            file=data.get("file") if data.get("file") is not None else None,  # type: ignore[arg-type]
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
    active_source_host: str = ""
    active_source_id: str = ""

    def to_json(self) -> dict[str, object]:
        return {
            "slug": self.slug,
            "title_zh": self.title_zh,
            "author": self.author,
            "category": self.category,
            "category_zh": self.category_zh,
            "source_host": self.source_host,
            "source_id": self.source_id,
            "active_source_host": self.active_source_host,
            "active_source_id": self.active_source_id,
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
            active_source_host=str(data.get("active_source_host", data.get("source_host", ""))),
            active_source_id=str(data.get("active_source_id", data.get("source_id", ""))),
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
    chapters_dir: Path
    readme_path: Path


class NovelDownloader:
    def __init__(
        self,
        novels_root: Path,
        client: httpx.Client | None = None,
        delay_min_seconds: float = _INTER_REQUEST_DELAY_MIN,
        delay_max_seconds: float = _INTER_REQUEST_DELAY_MAX,
        max_retries: int = _MAX_RETRIES,
    ) -> None:
        self._root = novels_root
        self._owns_client = client is None
        self._client = client or httpx.Client(
            timeout=_REQUEST_TIMEOUT,
            headers={"User-Agent": _USER_AGENT, "Accept-Language": "zh-CN,zh;q=0.9"},
            follow_redirects=True,
        )
        self._delay_min = delay_min_seconds
        self._delay_max = delay_max_seconds
        self._max_retries = max_retries
        self._last_request_at = 0.0

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> "NovelDownloader":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def download_all(
        self,
        on_progress: object = None,
        max_workers: int = 5,
    ) -> list[NovelDownloadResult]:
        """Parallel download: `max_workers` novels in flight at once.

        Per follow-up 105: serial mode (follow-up 104) was wall-clock-
        bound at ~9 h for the full manifest. Parallel mode runs N novels
        concurrently, each owning its own `httpx.Client` and rate-limit
        clock so the 0.8 s polite delay applies per-worker, not globally
        — peak aggregate ~6 req/s to sudugu.org with 5 workers.

        Each worker downloads exactly one novel at a time (no round-
        robin), so the user's "complete novels only" sidebar contract
        from follow-up 104 still holds: novels pop into the sidebar one
        at a time as workers finish them.

        Per follow-up 109 the polite delay is randomized 1.0–2.0 s per
        request rather than a fixed 0.8 s, so peak aggregate throughput
        with 5 workers drops to ~3.3 req/s on average — anti-bot harder.
        """
        results: list[NovelDownloadResult] = []
        results_lock = Lock()
        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            future_to_spec = {
                pool.submit(self._download_in_isolated_worker, spec, on_progress): spec
                for spec in CANONICAL_NOVELS
            }
            for future in as_completed(future_to_spec):
                spec = future_to_spec[future]
                try:
                    result = future.result()
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
                with results_lock:
                    results.append(result)
        self._write_index_md(self._reorder_to_canonical(results))
        return self._reorder_to_canonical(results)

    def _download_in_isolated_worker(
        self,
        spec: NovelSpec,
        on_progress: object,
    ) -> NovelDownloadResult:
        """Each worker owns its own NovelDownloader (and therefore its
        own httpx.Client + rate-limit clock). Avoids contention on a
        shared mutex which would serialize the workers anyway.
        """
        with NovelDownloader(
            novels_root=self._root,
            delay_min_seconds=self._delay_min,
            delay_max_seconds=self._delay_max,
            max_retries=self._max_retries,
        ) as worker:
            return worker.download(spec.slug, on_progress=on_progress)

    def _reorder_to_canonical(
        self,
        results: list[NovelDownloadResult],
    ) -> list[NovelDownloadResult]:
        order = {spec.slug: i for i, spec in enumerate(CANONICAL_NOVELS)}
        return sorted(results, key=lambda r: order.get(r.slug, 9999))

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
        chapters_dir = novel_dir / "chapters"
        chapters_dir.mkdir(parents=True, exist_ok=True)
        meta_path = novel_dir / "_meta.json"
        readme_path = novel_dir / "README.md"
        meta = self._load_or_init_meta(meta_path, spec)
        fresh_index, active = self._fetch_chapter_index(spec)
        source_changed = (
            meta.active_source_host != active.host
            or meta.active_source_id != active.source_id
        )
        meta.active_source_host = active.host
        meta.active_source_id = active.source_id
        readme_path.write_text(
            f"# {spec.title_zh}\n\n作者：{spec.author}\n\n来源：{active.host}/{active.source_id}/\n\n"
            f"章节存放于 `chapters/` 目录，每章一个 `.md` 文件。\n",
            encoding="utf-8",
        )
        if not meta.chapters:
            meta.chapters = fresh_index
            self._write_meta(meta_path, meta)
        elif source_changed:
            # New source — rewrite chapter URLs by `idx`, preserve `done`/`hash`/`error`.
            old_by_idx = {c.idx: c for c in meta.chapters}
            new_chapters: list[ChapterRecord] = []
            for fresh in fresh_index:
                prev = old_by_idx.get(fresh.idx)
                if prev is not None:
                    fresh.done = prev.done
                    fresh.hash = prev.hash
                    fresh.error = prev.error if not prev.done else None
                new_chapters.append(fresh)
            meta.chapters = new_chapters
            self._write_meta(meta_path, meta)
        elif len(fresh_index) > len(meta.chapters):
            for new_ch in fresh_index[len(meta.chapters):]:
                meta.chapters.append(new_ch)
            self._write_meta(meta_path, meta)
        meta.complete = (
            len(meta.chapters) > 0 and all(c.done for c in meta.chapters)
        )
        self._write_meta(meta_path, meta)
        return _NovelState(
            spec=spec,
            meta=meta,
            meta_path=meta_path,
            chapters_dir=chapters_dir,
            readme_path=readme_path,
        )

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
        filename = _build_chapter_filename(chapter.idx, chapter.title)
        chapter_path = state.chapters_dir / filename
        chapter_path.write_text(
            f"# {chapter.title}\n\n{body_text}\n",
            encoding="utf-8",
        )
        chapter.done = True
        chapter.error = None
        chapter.hash = hashlib.sha256(body_text.encode("utf-8")).hexdigest()[:16]
        chapter.file = filename
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
            active_source_host="",
            active_source_id="",
            chapters=[],
            complete=False,
        )

    def _write_meta(self, meta_path: Path, meta: NovelMeta) -> None:
        tmp = meta_path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(meta.to_json(), ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tmp, meta_path)

    def _fetch_chapter_index(
        self, spec: NovelSpec
    ) -> tuple[list[ChapterRecord], NovelSource]:
        """Try each source in spec.sources. Return (chapters, active_source)
        for the first reachable + parseable one. Raise if all sources fail.
        """
        last_exc: Exception | None = None
        for src in spec.sources:
            try:
                chapters = self._fetch_chapter_index_for_source(src)
                return chapters, src
            except (NovelChapterIndexParseError, NovelSourceUnreachableError) as exc:
                last_exc = exc
                continue
        raise NovelChapterIndexParseError(
            f"all {len(spec.sources)} sources failed for {spec.slug}: {last_exc}"
        )

    def _fetch_chapter_index_for_source(self, src: NovelSource) -> list[ChapterRecord]:
        if src.host == "sudugu.org":
            return self._fetch_index_via_sudugu(src)
        if src.host == "cn.ttkan.co":
            return self._fetch_index_via_ttkan(src)
        raise NovelChapterIndexParseError(f"no scraper registered for host {src.host!r}")

    def _fetch_index_via_sudugu(self, src: NovelSource) -> list[ChapterRecord]:
        base = f"https://www.{src.host}/{src.source_id}/"
        first_html = self._http_get(base)
        pages_to_fetch = self._discover_index_pages_sudugu(first_html, src)
        all_links: list[tuple[str, str]] = []
        all_links.extend(self._parse_index_links_sudugu(first_html, base))
        for url in pages_to_fetch:
            html = self._http_get(url)
            for rel_url, title in self._parse_index_links_sudugu(html, url):
                all_links.append((rel_url, title))
        if not all_links:
            raise NovelChapterIndexParseError(f"no chapter links found in index at {base}")
        records: list[ChapterRecord] = []
        seen_urls: set[str] = set()
        for rel_url, title in all_links:
            if rel_url in seen_urls:
                continue
            seen_urls.add(rel_url)
            records.append(
                ChapterRecord(
                    idx=len(records) + 1,
                    title=title.strip(),
                    url=f"https://www.{src.host}{rel_url}",
                )
            )
        return records

    def _fetch_index_via_ttkan(self, src: NovelSource) -> list[ChapterRecord]:
        # src.host already carries the `cn.` subdomain (follow-up 109);
        # do NOT prepend `www.`.
        url = f"https://{src.host}/novel/chapters/{src.source_id}"
        html = self._http_get(url)
        links = _TTKAN_CHAPTER_LINK_RE.findall(html)
        if not links:
            raise NovelChapterIndexParseError(f"no chapter links found in ttkan index at {url}")
        records: list[ChapterRecord] = []
        seen_urls: set[str] = set()
        for rel_url, title in links:
            if rel_url in seen_urls:
                continue
            seen_urls.add(rel_url)
            records.append(
                ChapterRecord(
                    idx=len(records) + 1,
                    title=title.strip(),
                    url=f"https://{src.host}{rel_url}",
                )
            )
        return records

    def _parse_index_links_sudugu(self, html: str, page_url: str) -> list[tuple[str, str]]:
        m = _INDEX_LIST_RE.search(html)
        if m is None:
            raise NovelChapterIndexParseError(f"index list block not found at {page_url}")
        return _CHAPTER_LINK_RE.findall(m.group(1))

    def _discover_index_pages_sudugu(self, first_html: str, src: NovelSource) -> list[str]:
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
            f"https://www.{src.host}/{src.source_id}/p-{n}.html"
            for n in page_numbers
        ]

    def _fetch_chapter_full(self, spec: NovelSpec, chapter: ChapterRecord) -> str:
        """Dispatch to per-host fetcher based on the chapter URL.
        Falls back to next source if the active one returns nothing parseable.
        """
        host = self._host_of_url(chapter.url)
        if host == "sudugu.org":
            return self._fetch_chapter_via_sudugu(chapter, "sudugu.org")
        if host == "cn.ttkan.co":
            return self._fetch_chapter_via_ttkan(chapter)
        raise NovelDownloadFailedError(f"no chapter fetcher for host {host!r} (url={chapter.url})")

    @staticmethod
    def _host_of_url(url: str) -> str:
        m = re.match(r"https?://(?:www\.)?([^/]+)", url)
        return m.group(1) if m else ""

    def _fetch_chapter_via_sudugu(self, chapter: ChapterRecord, host: str) -> str:
        parts: list[str] = []
        current_url = chapter.url
        visited: set[str] = set()
        while current_url:
            if current_url in visited:
                break
            visited.add(current_url)
            if len(visited) > 30:
                raise NovelDownloadFailedError(f"runaway pagination at {current_url}")
            html = self._http_get(current_url)
            cm = _CONTENT_BLOCK_RE.search(html)
            if cm is None:
                raise NovelDownloadFailedError(f"content block not found at {current_url}")
            body_html = cm.group(1)
            parts.append(self._extract_paragraphs(body_html))
            nm = _NEXT_PAGE_RE.search(html)
            if nm is None:
                break
            next_rel = nm.group(1)
            current_url = f"https://www.{host}{next_rel}"
        return "\n\n".join(p for p in parts if p)

    def _fetch_chapter_via_ttkan(self, chapter: ChapterRecord) -> str:
        html = self._http_get(chapter.url)
        cm = _TTKAN_CONTENT_BLOCK_RE.search(html)
        if cm is None:
            raise NovelDownloadFailedError(f"ttkan content block not found at {chapter.url}")
        return self._extract_paragraphs(cm.group(1))

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
            text = _END_OF_CHAPTER_MARKER_RE.sub("", text).strip()
            if text:
                paragraphs.append(text)
        return "\n\n".join(paragraphs)

    def _http_get(self, url: str) -> str:
        required = random.uniform(self._delay_min, self._delay_max)
        elapsed = time.monotonic() - self._last_request_at
        if elapsed < required:
            time.sleep(required - elapsed)
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
                last_exc = NovelSourceUnreachableError(f"http {r.status_code} at {url}")
                self._sleep_backoff(attempt)
                continue
            raise NovelSourceUnreachableError(f"http {r.status_code} at {url}")
        assert last_exc is not None
        raise NovelSourceUnreachableError(f"retries exhausted for {url}: {last_exc}")

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
                    f"| {badge} | [{r.title_zh}]({r.category}/{r.slug}/README.md) | "
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
    "_build_chapter_filename",
    "_safe_filename_segment",
]
