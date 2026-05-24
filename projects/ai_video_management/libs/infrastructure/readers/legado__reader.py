"""Legado-rule-driven HTML extractor for novel mirrors.

Lets us add a new novel source by dropping a Legado 3.0 book-source JSON
into `sources/` instead of writing per-host scraping Python. Public Legado
rule libraries (e.g. XIU2/Yuedu) cover hundreds of Chinese novel sites;
this reader can ingest the typical subset directly.

Rule grammar supported:
  - XPath: rule starting with `//` or `./`, or `@xpath:` prefix.
  - CSS: `@css:` prefix.
  - Default tag/class/id path: `class.X`, `tag.X`, `id.X`, optional `.N`
    index, chained with `@`. Final accessor `@text` / `@href` / `@src` /
    `@textNodes` / `@children[N]`. A bare `text`/`href`/`src` applied to
    a single element returns the corresponding accessor.
  - Multi-rule concat: `ruleA&&ruleB` — each evaluated, results joined.
  - Regex replace post: trailing `##pat##rep##` (or `##pat##rep`).

Out of scope (raises `LegadoUnsupportedSyntaxError`):
  - `@js:` rules, `<js>…</js>` blocks, full `{{js}}` templating.
  - JSONPath rules (`$.foo`, `@json:…`).
  - AllInOne single-colon regex.

The reader is opt-in scaffolding: nothing in the production download path
imports it yet. Wire it from `novel__writer.py` once a host needs it.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import httpx
from lxml import html as lxml_html
from lxml.etree import _Element

from libs.infrastructure.daos.legado_source__dao import LegadoSourceDao
from libs.infrastructure.errors.legado_source__error import (
    LegadoFetchError,
    LegadoRuleError,
    LegadoUnsupportedSyntaxError,
)

_REQUEST_TIMEOUT = 20.0
_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

_SELECTOR_RE = re.compile(r"^(class|tag|id)\.([\w\-]+)(?:\.(\d+))?$")
_CHILDREN_RE = re.compile(r"^children\[(\d+)\]$")
_TRAILING_REPLACE_RE = re.compile(r"##([^#]*)##([^#]*?)##?\s*$")


@dataclass(frozen=True)
class LegadoTocEntry:
    title: str
    url: str


class _LegadoEngine:
    """Stateless evaluator for the supported Legado rule subset."""

    def extract(self, ctx: _Element | str, rule: str) -> list[Any]:
        rule = (rule or "").strip()
        if not rule:
            return []
        self._reject_unsupported(rule)
        rule, post = self._split_off_replace(rule)
        if "&&" in rule:
            out: list[Any] = []
            for sub in rule.split("&&"):
                out.extend(self.extract(ctx, sub))
            return [self._apply_replace(r, post) for r in out]
        root = lxml_html.fromstring(ctx) if isinstance(ctx, str) else ctx
        results = self._dispatch(root, rule)
        return [self._apply_replace(r, post) for r in results]

    def _dispatch(self, root: _Element, rule: str) -> list[Any]:
        if rule.startswith("@css:"):
            return self._eval_css(root, rule[len("@css:") :])
        if rule.startswith("@xpath:"):
            return self._eval_xpath(root, rule[len("@xpath:") :])
        if rule.startswith("//") or rule.startswith("./") or rule.startswith("("):
            return self._eval_xpath(root, rule)
        return self._eval_default(root, rule)

    def _eval_css(self, root: _Element, sel: str) -> list[Any]:
        try:
            return list(root.cssselect(sel))
        except Exception as exc:
            raise LegadoRuleError(f"CSS eval failed: {sel!r}: {exc}") from exc

    def _eval_xpath(self, root: _Element, expr: str) -> list[Any]:
        try:
            return [self._coerce_xpath(x) for x in root.xpath(expr)]
        except Exception as exc:
            raise LegadoRuleError(f"XPath eval failed: {expr!r}: {exc}") from exc

    @staticmethod
    def _coerce_xpath(value: Any) -> Any:
        if isinstance(value, _Element):
            return value
        return str(value)

    def _eval_default(self, root: _Element, rule: str) -> list[Any]:
        nodes: list[Any] = [root]
        for raw in rule.split("@"):
            seg = raw.strip()
            if not seg:
                continue
            nodes = self._step(nodes, seg)
            if not nodes:
                return nodes
            if not isinstance(nodes[0], _Element):
                return nodes
        return nodes

    def _step(self, nodes: list[Any], seg: str) -> list[Any]:
        if seg in ("text", "@text"):
            return [self._node_text(n) for n in nodes if isinstance(n, _Element)]
        if seg == "textNodes":
            out: list[str] = []
            for n in nodes:
                if not isinstance(n, _Element):
                    continue
                out.append(
                    "\n".join(s.strip() for s in n.xpath(".//text()") if s.strip())
                )
            return [s for s in out if s]
        if seg in ("href", "src"):
            return [
                n.get(seg, "") for n in nodes if isinstance(n, _Element)
            ]
        m = _CHILDREN_RE.match(seg)
        if m:
            idx = int(m.group(1))
            out_nodes: list[Any] = []
            for n in nodes:
                if not isinstance(n, _Element):
                    continue
                kids = list(n)
                if 0 <= idx < len(kids):
                    out_nodes.append(kids[idx])
            return out_nodes
        if re.fullmatch(r"\d+", seg):
            i = int(seg)
            return [nodes[i]] if 0 <= i < len(nodes) else []
        return self._select(nodes, seg)

    def _select(self, nodes: list[Any], seg: str) -> list[Any]:
        m = _SELECTOR_RE.match(seg)
        if not m:
            raise LegadoUnsupportedSyntaxError(
                f"unrecognized default-syntax segment: {seg!r}"
            )
        kind, name, idx_raw = m.group(1), m.group(2), m.group(3)
        if kind == "class":
            xp = (
                ".//*[contains(concat(' ', normalize-space(@class), ' '), "
                f"' {name} ')]"
            )
        elif kind == "tag":
            xp = f".//{name}"
        else:
            xp = f".//*[@id={self._xpath_lit(name)}]"
        matched: list[_Element] = []
        for n in nodes:
            if isinstance(n, _Element):
                matched.extend(n.xpath(xp))
        if idx_raw is None:
            return list(matched)
        i = int(idx_raw)
        return [matched[i]] if 0 <= i < len(matched) else []

    @staticmethod
    def _xpath_lit(s: str) -> str:
        if "'" not in s:
            return f"'{s}'"
        return "concat('" + s.replace("'", "',\"'\",'") + "')"

    @staticmethod
    def _node_text(n: _Element) -> str:
        return "".join(n.itertext()).strip()

    @staticmethod
    def _reject_unsupported(rule: str) -> None:
        if rule.startswith("@js:") or "<js>" in rule:
            raise LegadoUnsupportedSyntaxError(
                f"JS rules not supported: {rule[:60]}"
            )
        if rule.startswith("@json:") or rule.startswith("$."):
            raise LegadoUnsupportedSyntaxError(
                f"JSONPath rules not supported: {rule[:60]}"
            )

    @staticmethod
    def _split_off_replace(rule: str) -> tuple[str, tuple[str, str] | None]:
        m = _TRAILING_REPLACE_RE.search(rule)
        if not m:
            return rule, None
        head = rule[: m.start()].rstrip()
        return head, (m.group(1), m.group(2))

    @staticmethod
    def _apply_replace(value: Any, post: tuple[str, str] | None) -> Any:
        if post is None or not isinstance(value, str):
            return value
        pat, rep = post
        try:
            return re.sub(pat, rep, value)
        except re.error as exc:
            raise LegadoRuleError(f"regex replace failed: /{pat}/: {exc}") from exc


class LegadoReader:
    """Drive a Legado book source against a live host."""

    def __init__(
        self,
        source: LegadoSourceDao,
        http: httpx.Client | None = None,
    ) -> None:
        self._source = source
        self._engine = _LegadoEngine()
        self._owns_http = http is None
        headers: dict[str, str] = {
            "User-Agent": _USER_AGENT,
            "Accept-Language": "zh-CN,zh;q=0.9",
        }
        headers.update(source.header)
        self._http = http or httpx.Client(
            timeout=_REQUEST_TIMEOUT,
            headers=headers,
            follow_redirects=True,
        )

    def close(self) -> None:
        if self._owns_http:
            self._http.close()

    def __enter__(self) -> "LegadoReader":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    @property
    def source(self) -> LegadoSourceDao:
        return self._source

    @classmethod
    def from_json_file(
        cls,
        path: Path,
        http: httpx.Client | None = None,
    ) -> "LegadoReader":
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(LegadoSourceDao.from_legado_json(raw), http=http)

    def fetch_toc(self, book_url: str) -> list[LegadoTocEntry]:
        rule = self._source.rule_toc
        if not rule.chapter_list:
            raise LegadoRuleError("book source has empty ruleToc.chapterList")
        root = lxml_html.fromstring(self._get(book_url))
        rows = self._engine.extract(root, rule.chapter_list)
        entries: list[LegadoTocEntry] = []
        for row in rows:
            if not isinstance(row, _Element):
                continue
            title = self._first_str(self._engine.extract(row, rule.chapter_name))
            href = self._first_str(self._engine.extract(row, rule.chapter_url))
            if not href:
                continue
            entries.append(LegadoTocEntry(title=title.strip(), url=urljoin(book_url, href)))
        return entries

    def fetch_chapter(self, chapter_url: str) -> str:
        rule = self._source.rule_content
        if not rule.content:
            raise LegadoRuleError("book source has empty ruleContent.content")
        root = lxml_html.fromstring(self._get(chapter_url))
        parts = self._engine.extract(root, rule.content)
        body = "\n\n".join(p for p in (str(x).strip() for x in parts) if p)
        if rule.replace_regex:
            for line in rule.replace_regex.splitlines():
                if "##" in line:
                    pat, rep = line.split("##", 1)
                    body = re.sub(pat, rep, body)
        return body

    def fetch_book_info(self, book_url: str) -> dict[str, str]:
        rule = self._source.rule_book_info
        root = lxml_html.fromstring(self._get(book_url))
        out: dict[str, str] = {}
        for key, expr in (
            ("name", rule.name),
            ("author", rule.author),
            ("intro", rule.intro),
            ("kind", rule.kind),
            ("cover_url", rule.cover_url),
            ("last_chapter", rule.last_chapter),
        ):
            if not expr:
                continue
            try:
                out[key] = self._first_str(self._engine.extract(root, expr))
            except LegadoRuleError:
                out[key] = ""
        return out

    def _get(self, url: str) -> str:
        try:
            r = self._http.get(url)
        except httpx.HTTPError as exc:
            raise LegadoFetchError(f"http error for {url}: {exc}") from exc
        if r.status_code != 200:
            raise LegadoFetchError(f"http {r.status_code} at {url}")
        return r.text

    @staticmethod
    def _first_str(results: list[Any]) -> str:
        for r in results:
            if isinstance(r, str):
                return r
            if isinstance(r, _Element):
                return "".join(r.itertext()).strip()
        return ""


__all__ = [
    "LegadoReader",
    "LegadoTocEntry",
]
