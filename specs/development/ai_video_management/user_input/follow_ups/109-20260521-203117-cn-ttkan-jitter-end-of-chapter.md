# Follow-up draft 109 — 2026-05-21

Three small wins extracted from reading `freeok/so-novel`'s declarative source-rule schema (their Java tool's `bundle/rules/*.json`). The architectural refactor (declarative `SourceRule` dataclass + bs4 CSS selectors) and adding 3rd/4th fallback hosts were both deferred — only the trivial quick wins are in scope this turn.

## Why now

Follow-up 107 added `ttkan.co` as a 2nd source but flagged content as **Traditional Chinese** (so-novel's `cn.ttkan.co` rule serves Simplified — same selectors, same paths, different subdomain). Follow-up 106 made the fixed `0.8 s` polite delay default global; so-novel's converged convention is min/max randomized jitter (typical 1.0–2.0 s) which is anti-bot smarter at the same average rate. End-of-chapter `(本章完)` markers leak into body files because the existing `_extract_paragraphs` only strips HTML, not Chinese boilerplate — every so-novel site rule lists this exact regex under `chapter.filterTxt`.

## Changes

### 1. `ttkan.co` → `cn.ttkan.co` (Simplified Chinese)

- `libs/domain/value_objects/novel__valueobject.py:65` — `_ttkan()` factory returns `NovelSource("cn.ttkan.co", source_slug)`.
- `libs/infrastructure/writers/novel__writer.py` — ttkan URL templates use `https://{src.host}/...` (no `www.` prefix; the `cn.` subdomain is already in `host`). Host comparison in `_fetch_chapter_full` becomes `cn.ttkan.co`.
- Sudugu paths unchanged — the change is ttkan-only to keep blast radius minimal.

**Migration on next run:** `_meta.json` files for the 5 ttkan-bearing novels (`fanren_xiuxian_zhuan`, `guangyin_zhiwai`, `wanmei_shijie`, `ze_tian_ji`, `lingjing_xingzhe`) carry `active_source_host="ttkan.co"`. New spec has `host="cn.ttkan.co"` → `source_changed=True` in `_ensure_index` → ttkan index re-fetched from `cn.` subdomain → chapter URLs rewritten by `idx`, preserving `done`/`hash`. Already-downloaded Traditional Chinese chapters stay in body files; new chapters appended as Simplified (mixed-script boundary acknowledged, opencc conversion deferred). Sudugu-only novels: `active_source_host="sudugu.org"` unchanged, no migration triggered.

### 2. `(本章完)` filter in `_extract_paragraphs`

Strip the literal end-of-chapter marker from each paragraph before appending; if the paragraph becomes empty, drop it. Matches so-novel's universal `filterTxt: "\\(本章完\\)"` (half-width parens only — the form sudugu/ttkan emit; full-width `（本章完）` not yet observed).

### 3. Jitter delay (replace fixed 0.8 s)

- `_INTER_REQUEST_DELAY = 0.8` replaced with `_INTER_REQUEST_DELAY_MIN = 1.0` + `_INTER_REQUEST_DELAY_MAX = 2.0` (so-novel's converged values for both sudugu and ttkan).
- `NovelDownloader.__init__` signature: `delay_seconds: float` → `delay_min_seconds: float, delay_max_seconds: float`. CLI doesn't pass either (uses defaults), so the rename is contained.
- `_http_get` computes `required = random.uniform(self._delay_min, self._delay_max)` per request instead of a fixed sleep.
- `_download_in_isolated_worker` plumbs both delays to the per-worker `NovelDownloader`.
- Average request rate goes from 1.25 req/s → ~0.67 req/s per worker (50% slower at the average, but **harder to fingerprint** than fixed cadence; matches so-novel's empirical anti-bot setting for sudugu).

## What was deliberately NOT done

- **Declarative `SourceRule` schema + bs4 port.** so-novel's rule-template.json5 is genuinely better than my regex-per-host approach, but moving sudugu+ttkan to a generic CSS-selector engine is a 2–3 hr refactor with replay-test scope. Deferred until a 3rd source is needed.
- **Adding `xbiqugu.la` / `22biqu.com` / `shuhaige.net` as 3rd/4th fallback hosts.** Each would need either (a) new `_fetch_index_via_*` / `_fetch_chapter_via_*` pairs (deepening the per-host pattern that's already painful) OR (b) the declarative refactor above. Deferred together with the refactor.
- **`@js:` rule support** — so-novel's `bundle/rules/main.json` embeds JavaScript snippets for ~3 sites (base64 decode, paragraph re-ordering). Out of scope; Python equivalent is mini-racer or pyjsdom, heavy for narrow use.
- **Cloudflare / proxy-required tier hosts** — would need `curl_cffi` for TLS fingerprint spoofing or actual proxies. Not pursued.
- **opencc 繁→简 conversion** for the existing body fragments downloaded from `www.ttkan.co` pre-migration. Still deferred per follow-up 107.

## Touch list

- **Modified Python files (2)**:
  - `libs/domain/value_objects/novel__valueobject.py` — `_ttkan()` factory host string.
  - `libs/infrastructure/writers/novel__writer.py` — delay constants + `__init__` signature + `_http_get` jitter + `_extract_paragraphs` filter + ttkan URL templates + ttkan host comparison + docstring lines mentioning `0.8 s` / `ttkan.co`.
- **Unchanged**: CLI, application layer, frontend, routes, container, `NovelMeta` schema, `NovelSource` schema. so-novel's `bundle/rules/*.json` was read for reference only — not vendored.
- **Audit**: revised_prompt.md header bump; changelog 109.
