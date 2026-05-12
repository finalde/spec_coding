# Validation strategy — Level 04: Security

Project: `ai_video_management` (development webapp)
Run: `ai_video_management-20260505-002710`
Spec anchors: FR-3, FR-7, FR-8, FR-11..FR-17, FR-28, FR-32
Reference moves: `agent_refs/validation/general.md` § 1, 2, 3, 7; `agent_refs/validation/development.md` move #11.

## Scope

Backend security gate for `projects/ai_video_management/backend/`. Every check is an HTTP-shape regression test runnable from `pytest` inside `backend/tests/unit/` against the in-process FastAPI test client (port 8766 conceptually; the test client doesn't bind a socket but the gate reads the `Host`/`Origin` headers as if it had).

All checks are **per-FR**, not per-endpoint. The same FR may apply to multiple endpoints; each row enumerates every endpoint it gates.

## Severity policy (recap)

Per `agent_refs/validation/general.md` standard table: every SEC-* finding is `critical` (security failure ⇒ critical, halts immediately, no revision rounds without explicit user approval). Per move #11, the *missing-test* class is `blocker` when a header-mutating proxy exists in the dev workflow — Vite at `127.0.0.1:5174` rewrites `Origin` per FR-6, so the full pre/post-rewrite shape coverage is mandatory.

The "severity" column below records the severity of a *failing* check at runtime; the strategy itself is a `blocker` if any check is missing from the test set.

---

## SEC-ORIGIN-HOST — Origin / Host gate (FR-11, FR-3)

Target endpoints: `PUT /api/file`, `POST /api/regen-prompt`, `POST /api/promote`, `DELETE /api/promote` (every state-changing endpoint per FR-9). GET endpoints are NOT gated by Origin (port the spec_driven posture verbatim).

Bound port: **8766**. Loopback aliases admitted: `localhost` ↔ `127.0.0.1` at port 8766. **Port 8765 (spec_driven) is foreign** even when bound on the same host — the two webapps coexist (NFR-3) but DO NOT share an Origin allow-list.

Per development.md move #11, BOTH the pre-Vite-rewrite shape AND the post-rewrite shape are unit-tested. The Vite proxy at `127.0.0.1:5174` rewrites `Origin: http://127.0.0.1:5174` → `Origin: http://127.0.0.1:8766` per FR-6 (parallels spec_driven follow-up 006); a request with the un-rewritten Origin landing on the backend must 403, otherwise dropping the proxy hook re-introduces the cross-port admit.

| Id | Endpoint(s) | Attack scenario | Pass condition | Severity |
|---|---|---|---|---|
| SEC-ORIGIN-HOST-01 | PUT, POST regen, POST/DELETE promote | No `Origin` header at all | 403 on every endpoint | critical |
| SEC-ORIGIN-HOST-02 | PUT, POST regen, POST/DELETE promote | `Origin: http://evil.example.com` + `Host: 127.0.0.1:8766` | 403 | critical |
| SEC-ORIGIN-HOST-03 | PUT, POST regen, POST/DELETE promote | `Origin: http://127.0.0.1:8766` + `Host: evil.com` | 403 | critical |
| SEC-ORIGIN-HOST-04 | PUT, POST regen, POST/DELETE promote | `Origin: http://127.0.0.1:9999` (wrong port) + `Host: 127.0.0.1:8766` | 403 | critical |
| SEC-ORIGIN-HOST-05 | PUT, POST regen, POST/DELETE promote | `Origin: http://127.0.0.1:8765` + `Host: 127.0.0.1:8765` (spec_driven port — foreign for this app) | 403 | critical |
| SEC-ORIGIN-HOST-06 | PUT, POST regen, POST/DELETE promote | `Origin: http://[::1]:8766` + `Host: [::1]:8766` (IPv6 loopback — backend bound IPv4 only per FR-3) | 403 | critical |
| SEC-ORIGIN-HOST-07 | PUT, POST regen, POST/DELETE promote | **[regression-spec_driven-006 / move #11 pre-rewrite]** `Origin: http://127.0.0.1:5174` + `Host: 127.0.0.1:8766` (raw browser-shape direct-to-backend; what hits the backend if the Vite proxy `configure` rewrite hook is missing) | 403 | critical |
| SEC-ORIGIN-HOST-08 | PUT, POST regen, POST/DELETE promote | **[regression-spec_driven-006 / move #11 pre-rewrite]** `Origin: http://localhost:5174` + `Host: 127.0.0.1:8766` (alias variant of -07) | 403 | critical |
| SEC-ORIGIN-HOST-09 | PUT, POST regen, POST/DELETE promote | **[move #11 post-rewrite happy path]** `Origin: http://127.0.0.1:8766` + `Host: 127.0.0.1:8766` (the shape `make run-prod` produces and the shape Vite produces after rewrite) | 200 (with otherwise-valid body) | critical (pass = green; failure means the gate is too strict and breaks `run-prod`) |
| SEC-ORIGIN-HOST-10 | PUT, POST regen, POST/DELETE promote | **[loopback alias admit]** `Origin: http://localhost:8766` + `Host: localhost:8766` | 200 | critical |
| SEC-ORIGIN-HOST-11 | PUT, POST regen, POST/DELETE promote | **[loopback cross-product]** `Origin: http://127.0.0.1:8766` + `Host: localhost:8766` | 200 | critical |
| SEC-ORIGIN-HOST-12 | PUT, POST regen, POST/DELETE promote | **[loopback cross-product]** `Origin: http://localhost:8766` + `Host: 127.0.0.1:8766` | 200 | critical |
| SEC-ORIGIN-HOST-13 | GET `/api/file`, GET `/api/tree` | `Origin: http://evil.example.com` + foreign Host | 200 (GET endpoints intentionally NOT gated per FR-9 read-vs-write split) | critical (pass = green; failure means GETs got over-gated and break public-token-style use cases the spec leaves open) |
| SEC-ORIGIN-HOST-14 | E2E (Playwright, dev-mode profile) | Real browser → Vite at `127.0.0.1:5174` → backend at 8766 → PUT succeeds | 200 round-trip; the proxy `configure` hook is wired up | critical |

**Pass-condition note for -09 / -10 / -11 / -12:** these are positive-path tests; failure here is what move #11 calls "the dev-server profile broke after the gate was tightened." They MUST stay green to prove the gate is correctly scoped.

**Coverage proof obligation:** `test_api.py` (or a dedicated `test_api_security.py`) MUST contain one named test per row above. A reviewer can grep the file for `SEC-ORIGIN-HOST-` markers (in test docstrings or names) and find all 14.

---

## SEC-PATH-TRAVERSAL — Path traversal hardening (FR-12, FR-8)

Target endpoints: `GET /api/file`, `PUT /api/file` (path is also user-controlled in the JSON body), `POST /api/promote` / `DELETE /api/promote` (their `source_path` / project-path inputs).

**Single-404 contract:** every probe returns `404` with NO distinction between "outside tree", "doesn't exist", "wrong extension", "reserved name", etc. No oracle leaks "this path exists but you can't access it" vs "this path doesn't exist."

| Id | Endpoint(s) | Attack scenario (path string) | Pass condition | Severity |
|---|---|---|---|---|
| SEC-PATH-TRAVERSAL-01 | GET, PUT | `../etc/passwd` | 404 | critical |
| SEC-PATH-TRAVERSAL-02 | GET, PUT | `ai_videos/../../etc/passwd` | 404 | critical |
| SEC-PATH-TRAVERSAL-03 | GET, PUT | `/etc/passwd` (absolute POSIX) | 404 | critical |
| SEC-PATH-TRAVERSAL-04 | GET, PUT | `C:\Windows\System32\drivers\etc\hosts` (absolute Windows) | 404 | critical |
| SEC-PATH-TRAVERSAL-05 | GET, PUT | `%2e%2e%2fetc%2fpasswd` (percent-encoded `../etc/passwd`) | 404 | critical |
| SEC-PATH-TRAVERSAL-06 | GET, PUT | `%252e%252e%252fetc%252fpasswd` (double-encoded) | 404 | critical |
| SEC-PATH-TRAVERSAL-07 | GET, PUT | `..%c0%af..%c0%afetc/passwd` (UTF-8 overlong-encoding bypass) | 404 | critical |
| SEC-PATH-TRAVERSAL-08 | GET, PUT | `ai_videos/wukong_juexing/README.md::$DATA` (Windows ADS / NTFS alternate data stream) | 404 | critical |
| SEC-PATH-TRAVERSAL-09 | GET, PUT | `ai_videos/wukong_juexing/README.md:zone.identifier` (named ADS) | 404 | critical |
| SEC-PATH-TRAVERSAL-10 | GET, PUT | `ai_videos/CON.md` (Windows reserved name CON) | 404 | critical |
| SEC-PATH-TRAVERSAL-11 | GET, PUT | `ai_videos/PRN.md`, `AUX.md`, `NUL.md`, `COM1.md`, `LPT1.md` (parametrized over reserved names) | 404 | critical |
| SEC-PATH-TRAVERSAL-12 | GET, PUT | `ai_videos/wukong~1/README.md` (Windows 8.3 short name) | 404 | critical |
| SEC-PATH-TRAVERSAL-13 | GET, PUT | `ai_videos\\wukong_juexing\\README.md` (mixed/back-slashes on POSIX) | 404 OR resolved-to-allowed-path (pick one and document; default 404 — port spec_driven posture) | critical |
| SEC-PATH-TRAVERSAL-14 | GET, PUT | `ai_videos/wukong_juexing/README.md\` (CVE-2025-62522 trailing-backslash Vite bypass — backend MUST reject regardless of frontend) | 404 | critical |
| SEC-PATH-TRAVERSAL-15 | GET, PUT | Path resolving to a symlink that points outside EXPOSED_TREE (POSIX; Windows skipped via `pytest.mark.skipif`) | 404; symlink refused outright (per FR-12) | critical |
| SEC-PATH-TRAVERSAL-16 | GET, PUT | Path resolving to a Windows directory junction pointing outside EXPOSED_TREE (Windows; POSIX skipped) | 404 | critical |
| SEC-PATH-TRAVERSAL-17 | GET, PUT | `projects/spec_driven/README.md` (sibling project dir — FR-8 dropped `projects/` from EXPOSED_TREE allowed top-levels) | 404 (no read across to spec_driven) | critical |
| SEC-PATH-TRAVERSAL-18 | GET, PUT | `specs/development/ai_video_management/final_specs/spec.md` (FR-8 tightened `specs/**` to `specs/ai_video/**` only) | 404 | critical |
| SEC-PATH-TRAVERSAL-19 | GET, PUT | `` (empty path) | 404 OR 422 (FastAPI default for missing query/body field) — pick and document | critical |
| SEC-PATH-TRAVERSAL-20 | GET, PUT | `.` and `./` (current-dir refs) | 404 | critical |
| SEC-PATH-TRAVERSAL-21 | GET | NUL byte injection: `ai_videos/wukong_juexing/README.md\x00.png` | 404 (path normalization rejects NUL) | critical |

**Single-oracle assertion:** for any pair of probes from the list above where one names an existing file and one names a non-existent sibling under the same parent, the response body MUST be byte-identical (or at minimum, return the same 404 status with no `detail` that reveals the fork). Add `test_traversal_no_existence_oracle` that issues two probes and asserts equal status + (if `detail` exists) equal `detail.kind`.

**Skip protocol (per development.md move #5):** symlink/junction tests use `pytest.mark.skipif(sys.platform == "win32", reason="POSIX symlinks require Developer Mode")` and the inverse for junctions. Skipping is healthy; silent passing is not.

---

## SEC-EXTENSION-ALLOWLIST — Read + write extension allowlist (FR-13, FR-28)

Target endpoints: `GET /api/file` (read allowlist), `PUT /api/file` (write allowlist — strictly narrower).

Read allowlist: `.md`, `.json`, `.yaml`, `.yml`, `.jsonl`, `.txt`, `.png`, `.jpg`. Write allowlist excludes images (`.png`, `.jpg`, `.svg` rejected) — image extensions are read-only via `/api/file` per FR-64.

| Id | Endpoint | Attack scenario | Pass condition | Severity |
|---|---|---|---|---|
| SEC-EXT-01 | GET | `.exe`, `.bat`, `.sh`, `.dll`, `.html`, `.php`, `.svg` (parametrized over each) | 415 (port spec_driven status; ai_video spec FR-28 says 400 for *write* — read uses 415 unless overridden by stage-6 review) | critical |
| SEC-EXT-02 | GET | `.png` accepted (returns binary with `Content-Type: image/png` per FR-25) | 200 | critical (pass = green) |
| SEC-EXT-03 | GET | `.jpg` accepted | 200 | critical (pass = green) |
| SEC-EXT-04 | GET | `.svg` rejected (code-execution vector — explicit FR-13 carve-out) | 415 | critical |
| SEC-EXT-05 | GET | `.md`, `.json`, `.jsonl`, `.yaml`, `.yml`, `.txt` (parametrized) accepted | 200 | critical (pass = green) |
| SEC-EXT-06 | PUT | `.png` write attempt | 400 (per FR-28) | critical |
| SEC-EXT-07 | PUT | `.jpg` write attempt | 400 | critical |
| SEC-EXT-08 | PUT | `.svg` write attempt | 400 | critical |
| SEC-EXT-09 | PUT | `.exe`, `.bat`, `.sh`, `.dll`, `.html`, `.php` (parametrized) | 400 (or 415 if porting verbatim from spec_driven; ai_video spec FR-28 chose 400 — emit 400) | critical |
| SEC-EXT-10 | PUT | `.md`, `.json`, `.jsonl`, `.yaml`, `.yml`, `.txt` (parametrized) accepted | 200 | critical (pass = green) |
| SEC-EXT-11 | GET | Extension-by-trick: `evil.exe.md` (allowed) — assert 200 (compound suffix is not an attack; only the FINAL extension is checked, by spec) | 200 | critical (pass = green; documents the allowlist semantics) |
| SEC-EXT-12 | GET | No extension at all: `ai_videos/wukong_juexing/README` (file may not exist, but the gate decision is what matters) | 415 OR 404; document which | critical |

**FR-28 status-code drift note:** spec_driven returns 415 for disallowed extensions on PUT; FR-28 in the ai_video_management spec says 400. The strategy emits **400** per FR-28 (newer spec wins). Stage-6 implementer MUST honor FR-28; if a port-verbatim block returns 415, that's a `blocker` finding.

---

## SEC-BODY-CAP — 1 MiB body cap with 50 KiB soft warning (FR-14)

Target endpoint: `PUT /api/file`.

| Id | Attack scenario | Pass condition | Severity |
|---|---|---|---|
| SEC-BODY-CAP-01 | Body = `"a" * (1024 * 1024 + 1)` (just over 1 MiB) | 413 | critical |
| SEC-BODY-CAP-02 | Body = `"a" * (10 * 1024 * 1024)` (10 MiB) | 413 (NOT 500 — reject before buffering full body if FastAPI middleware allows; see implementer note) | critical |
| SEC-BODY-CAP-03 | Body = `"a" * (1024 * 1024)` (exactly 1 MiB) | 200 | critical (pass = green; documents the boundary is `>1 MiB`, not `≥`) |
| SEC-BODY-CAP-04 | Body = `"a" * (50 * 1024 + 1)` (just over 50 KiB soft threshold) | 200 + warning logged to stdout (per NFR-5 "no structured logging beyond stdout") with substring `soft_warning` and the path | critical (pass = green + log assertion via `caplog` or stdout capture) |
| SEC-BODY-CAP-05 | Body = `"a" * (50 * 1024)` (exactly at threshold) | 200 + NO warning logged | critical (pass = green) |
| SEC-BODY-CAP-06 | Multipart / `Content-Length: 0` PUT with empty `content` field | 200 (empty body is allowed per port-verbatim from spec_driven `test_put_empty_body_is_allowed`) | critical (pass = green) |

**Implementer note:** the cap MUST be enforced at the request-parsing boundary so that a 100 MiB upload doesn't OOM the process before hitting the JSON parser. FastAPI's default does NOT cap; the strategy assumes a Starlette `BaseHTTPMiddleware` or uvicorn `--limit-request-line` / explicit body-size middleware. Stage-6 review must verify the cap fires BEFORE the JSON body is loaded into memory.

---

## SEC-MTIME-CONCURRENCY — `If-Unmodified-Since` mtime concurrency (FR-15)

Target endpoint: `PUT /api/file`.

**Strict reading of FR-15:** "If-Unmodified-Since (RFC 7232 mtime) **required** on PUT /api/file. Stale mtime → 409." The level prompt explicitly says missing-header = 400. This DIVERGES from spec_driven's behavior (where the header is optional — see `test_put_without_iums_proceeds`); the ai_video_management webapp tightens the contract.

| Id | Attack scenario | Pass condition | Severity |
|---|---|---|---|
| SEC-MTIME-01 | `If-Unmodified-Since` header absent | 400 (per FR-15 + level prompt; DIVERGES from spec_driven's optional behavior) | critical |
| SEC-MTIME-02 | `If-Unmodified-Since` present but parses to a timestamp strictly older than current on-disk mtime → stale | 409 | critical |
| SEC-MTIME-03 | `If-Unmodified-Since` present and parses to a timestamp ≥ current on-disk mtime → fresh | 200 | critical (pass = green) |
| SEC-MTIME-04 | `If-Unmodified-Since` present but malformed (e.g., `not-a-date`) | 400 (NOT 409 — malformed ≠ stale) | critical |
| SEC-MTIME-05 | `If-Unmodified-Since` for a file that does not yet exist (creation case) | 200 (no prior mtime to be stale against; document this as the create-path semantics) OR 409 (if the implementer chose strict-create semantics) — the strategy picks **200** per FR-29 atomic-write path; stage-6 must document this | critical |
| SEC-MTIME-06 | 409 response body shape: `{detail: {kind: "stale_write", current_mtime: float}}` so the SPA can offer the "file changed externally — Reload?" UX per FR-15 | shape match | critical |
| SEC-MTIME-07 | Race condition: two concurrent PUTs to the same path with the same valid IUMS, second-arriving must 409 | second PUT returns 409 | critical |
| SEC-MTIME-08 | `If-Unmodified-Since: *` (RFC-defined wildcard) | 400 (wildcard is NOT meaningful for IUMS in this contract) | critical |

**Divergence record:** the FR-15-required IUMS rule is a deliberate tightening from spec_driven's optional posture. The stage-5 strategy surfaces this per general.md principle 6 ("question every v1 carve-out at stage 5"); the user can downgrade to optional via a follow-up if the strict rule turns out to break a workflow.

---

## SEC-CSP — Content-Security-Policy header (FR-17)

Target endpoints: every backend response (both static SPA bundle and JSON API responses).

Required policy: `default-src 'self'; img-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'self'`.

| Id | Endpoint(s) | Attack scenario | Pass condition | Severity |
|---|---|---|---|---|
| SEC-CSP-01 | `GET /` (SPA root) | Request returns SPA HTML | response includes `Content-Security-Policy` header with the exact policy string above | critical |
| SEC-CSP-02 | `GET /api/tree`, `GET /api/file`, `PUT /api/file`, `POST /api/regen-prompt`, `POST/DELETE /api/promote` | Standard request | every response carries the CSP header | critical |
| SEC-CSP-03 | `GET /static/...` (Vite-bundled assets in `make run-prod` mode) | Standard request | CSP header present | critical |
| SEC-CSP-04 | CSP directive completeness: `default-src`, `img-src`, `style-src`, `script-src`, `connect-src`, `object-src`, `base-uri` all present in the header value | parametrized assert per directive | critical |
| SEC-CSP-05 | `script-src` MUST NOT include `'unsafe-inline'` or `'unsafe-eval'` (only styles get the inline carve-out for Vite-bundled CSS) | substring assertion: `'unsafe-inline'` appears in `style-src` segment but NOT in `script-src` segment | critical |
| SEC-CSP-06 | `object-src 'none'` (blocks Flash / ActiveX / `<embed>` legacy vectors) | substring assertion | critical |
| SEC-CSP-07 | E2E: render an `_seedream.md` page in a real browser; assert `console.warn` / `console.error` from CSP violation report is empty (rules out a CSP that silently breaks the SPA) | Playwright `page.on('console', ...)` capture is empty | critical |

**Test-shape note:** the CSP header value is a single string per response. A `parametrize` over `(endpoint, expected_substring)` keeps the test concise; one negative test (SEC-CSP-05) for the `script-src` carve-out asymmetry catches the most common mis-config.

---

## SEC-SANITIZE — Markdown sanitization (FR-16)

Target: frontend `MarkdownView` component (and every renderer that wraps it: `QaView`, `ShotPairView`, `ShotlistTableView`, `ImageRefView` left pane).

Rendered through `react-markdown ^9` + `rehype-sanitize ^6` with the default schema. The default schema strips raw HTML, event handlers, and `javascript:` URIs.

These are **frontend tests** (Vitest + jsdom); they live under `frontend/src/markdown/__tests__/` (or wherever the unit tests land per FR-84). Inclusion in the security strategy is intentional — sanitization is a security gate even though its implementation is client-side.

| Id | Component | Attack scenario (markdown source) | Pass condition (rendered DOM) | Severity |
|---|---|---|---|---|
| SEC-SANITIZE-01 | MarkdownView | `<script>alert(1)</script>` in a markdown body | rendered DOM contains NO `<script>` element (text node OK; live element NOT) | critical |
| SEC-SANITIZE-02 | MarkdownView | `<img src=x onerror="alert(1)">` raw HTML | `<img>` either removed entirely or the `onerror` attribute stripped | critical |
| SEC-SANITIZE-03 | MarkdownView | `[click](javascript:alert(1))` markdown link | rendered `<a>` either removed OR `href` attribute absent / set to `about:blank` (rehype-sanitize default behavior) | critical |
| SEC-SANITIZE-04 | MarkdownView | `<iframe src="https://evil.com">` raw HTML | `<iframe>` element NOT in DOM | critical |
| SEC-SANITIZE-05 | MarkdownView | `<a href="data:text/html,<script>alert(1)</script>">x</a>` | `<a>` present but `href` absent / sanitized | critical |
| SEC-SANITIZE-06 | MarkdownView | Raw HTML inside a fenced code block: ` ```html\n<script>alert(1)</script>\n``` ` | `<script>` rendered as escaped TEXT inside `<code>`, NOT as live element (code blocks survive sanitization with content escaped) | critical |
| SEC-SANITIZE-07 | ShotPairView | Each pane independently sanitized (regression: a sanitization layer that wrapped only the outer container leaks if the splitter-internal MarkdownView is rendered separately) | both panes' DOM clean for SEC-SANITIZE-01..05 inputs | critical |
| SEC-SANITIZE-08 | ShotlistTableView | Markdown table cell with `<script>` tag in cell content | `<script>` not in DOM; `<td>` text-only | critical |
| SEC-SANITIZE-09 | QaView | Q/A body with `<img onerror>` payload | sanitized | critical |
| SEC-SANITIZE-10 | E2E | Real PUT uploads `<script>alert("xss")</script>` to a `.md` file under `ai_videos/`; user opens the file in browser; Playwright asserts `page.on('dialog', ...)` was never called AND `page.evaluate(() => document.querySelector('script[data-test-payload]'))` returns null | no dialog, no live `<script>` | critical |

**Locked-block pill note:** FR-65 wraps `【...锁定描述符 vN】...禁用 ...。` blocks in `<span class="locked-block">` BEFORE handing source to react-markdown. This wrapping is a TEXT-LEVEL operation (regex on string) — assert that an attacker who places HTML inside a locked-block delimiter does NOT smuggle live HTML through the wrapper. Add SEC-SANITIZE-11: input `【XSS · v1 · 锁定描述符 v1】<script>alert(1)</script>禁用 X。` → wrapper applied; sanitization still strips the inner `<script>`.

---

## SEC-PROMOTE-STAGE6 — Promotion endpoint stage-6 rejection (FR-32)

Target endpoints: `POST /api/promote`, `DELETE /api/promote`.

Per FR-32, stage 6 (project code under `ai_videos/{name}/`) does NOT support promotion in v1. The endpoints reject `stage="execution"` AND any `source_path` under `ai_videos/{name}/` (paths under `specs/ai_video/{name}/` remain valid).

This is a security check because promotion writes to `<stage>/promoted.md` — accepting a stage-6 promotion would either silently no-op (UX bug) or, worse, write a `promoted.md` under `ai_videos/{name}/` which the regen contract preserves indefinitely (data-integrity bug).

| Id | Endpoint | Attack scenario | Pass condition | Severity |
|---|---|---|---|---|
| SEC-PROMOTE-S6-01 | POST /api/promote | Body `{stage: "execution", source_path: "ai_videos/wukong_juexing/episodes/ep01/prompts/shot01_kling.md", item_id: "x", item_text: "y"}` | 400 with `detail` mentioning the stage-6 rule | critical |
| SEC-PROMOTE-S6-02 | DELETE /api/promote | Body `{stage: "execution", item_id: "x"}` | 400 | critical |
| SEC-PROMOTE-S6-03 | POST /api/promote | Body `{stage: "interview", source_path: "ai_videos/wukong_juexing/README.md", ...}` (valid stage but ai_videos/ source path — must reject because the file is not under specs/) | 400 | critical |
| SEC-PROMOTE-S6-04 | POST /api/promote | Body `{stage: "interview", source_path: "specs/ai_video/wukong_juexing/interview/qa.md", ...}` (correct path under specs/ — happy path) | 200 | critical (pass = green) |
| SEC-PROMOTE-S6-05 | POST /api/promote | Body `{stage: "validation", source_path: "specs/ai_video/wukong_juexing/validation/security.md", ...}` happy path | 200 | critical (pass = green) |
| SEC-PROMOTE-S6-06 | POST /api/promote | Stage value not in allowlist `{"interview", "findings", "final_specs", "validation"}`: e.g., `stage="user_input"` or `stage="render"` | 400 (or 422 for FastAPI Enum default) | critical |

**Why the symmetric check (-03):** an attacker who knows `stage="interview"` is allowed but supplies an `ai_videos/` source_path could otherwise plant a `promoted.md` outside `specs/`. The check enforces that the source-path root MUST be `specs/ai_video/{name}/` regardless of which stage the body claims.

---

## SEC-LOOPBACK-ONLY — Backend bind on `0.0.0.0` or `[::1]` is forbidden (FR-3)

Target: process startup config in `backend/libs/main.py`.

| Id | Attack scenario | Pass condition | Severity |
|---|---|---|---|
| SEC-LOOPBACK-01 | Static-source check: grep `main.py` for `host="127.0.0.1"` (substring match); fail if `host="0.0.0.0"`, `host=""`, `host="::"`, or `host="[::1]"` appear | grep matches `127.0.0.1` and matches no forbidden form | critical |
| SEC-LOOPBACK-02 | Boot-smoke check: launch `make run-backend` in a subprocess; `socket.connect(("127.0.0.1", 8766))` succeeds; `socket.connect(("::1", 8766))` fails with `ConnectionRefusedError` | both behave as expected | critical |
| SEC-LOOPBACK-03 | argparse / CLI surface: `python -m main --host 0.0.0.0` MUST be rejected (or the flag MUST not exist). Per FR-2 main.py is ≤15 lines and `host` is hard-coded; a `--host` CLI flag is itself a finding | no CLI override of host accepted | critical |
| SEC-LOOPBACK-04 | Boot-smoke check on a multi-NIC machine (skipped in unit; documented in stage-6 manual walkthrough): `socket.connect((<external-NIC-IP>, 8766))` MUST fail | manual walkthrough item | critical (manual) |

**Test placement:** SEC-LOOPBACK-01 is a static unit test (`backend/tests/unit/test_main_bind.py` — read the file, assert substrings). SEC-LOOPBACK-02 belongs in the boot-smoke suite per development.md move #4. SEC-LOOPBACK-03 is satisfied by spec inspection if `main.py` truly is ≤15 lines and hard-codes the host (FR-2 + FR-3); flag a finding if a CLI flag was added.

---

## Cross-cutting / coverage proof obligations

1. **Single test file `test_api_security.py` per the spec_driven precedent** OR distribute across `test_api.py` + `test_file_writer.py` + a new `test_csp.py` + a frontend `MarkdownView.spec.tsx`. Either layout is acceptable as long as a reviewer can grep the test tree for every `SEC-*` marker above and find at least one test per id.
2. **Audit-event emission:** every level run emits `validation.started` + (`validation.pass` | `validation.issue.raised`) per general.md principle 5. The security level emits to `events.jsonl` like every other level.
3. **No silent skips:** any test marked `pytest.mark.skipif` MUST include a `reason=` string. Per general.md principle 3, skipping is healthy; silent passing is not.
4. **Pre-rewrite shape coverage proof:** SEC-ORIGIN-HOST-07 + SEC-ORIGIN-HOST-08 (the two move-#11 pre-rewrite tests) MUST be present. Stage-5 sign-off is `blocker` if either is missing.
5. **Header-mutating-layer e2e profile:** SEC-ORIGIN-HOST-14 requires a Playwright profile that boots Vite at `127.0.0.1:5174` AND the backend at `127.0.0.1:8766` AND drives a real browser through the proxy. Per development.md move #1, "mode count = e2e profile count" — `make run-prod` and `make run-frontend` are both advertised, so two profiles, both exercising the gate.
6. **Status-code drift docket:** the strategy makes two intentional status-code choices that diverge from spec_driven; both are recorded above (FR-28 chose 400 over 415 for write-extension reject; FR-15 made IUMS strictly required → 400 missing). Stage-6 must honor FR-* over port-verbatim.

## Coverage matrix vs FRs

| FR | SEC-* check group | Status |
|---|---|---|
| FR-3 (loopback only) | SEC-LOOPBACK | covered |
| FR-7 / FR-8 (EXPOSED_TREE shape) | SEC-PATH-TRAVERSAL-17, -18 | covered |
| FR-11 (Origin/Host) | SEC-ORIGIN-HOST | covered |
| FR-12 (path traversal) | SEC-PATH-TRAVERSAL | covered |
| FR-13 (extension allowlist read) | SEC-EXT-01..05, -11, -12 | covered |
| FR-14 (1 MiB cap + 50 KiB warning) | SEC-BODY-CAP | covered |
| FR-15 (IUMS required) | SEC-MTIME | covered |
| FR-16 (sanitization) | SEC-SANITIZE | covered |
| FR-17 (CSP) | SEC-CSP | covered |
| FR-28 (PUT rejection set, includes image extensions) | SEC-EXT-06..10 + SEC-MTIME-02 + SEC-BODY-CAP-01 + SEC-PATH-TRAVERSAL (PUT rows) | covered |
| FR-32 (stage-6 promotion rejection) | SEC-PROMOTE-S6 | covered |
| FR-9b (rename-media drama-scope) | SEC-RENAME-SCOPE (follow-up 007) | covered |
| FR-9c / FR-9d (archive / unarchive single file) | SEC-ARCHIVE-PATH (follow-up 008) | covered |
| FR-9e (import-from-downloads — first read outside EXPOSED_TREE) | SEC-IMPORT-DOWNLOADS (see carve-out #6) | partial |
| FR-9f (actors/generate — first outbound HTTP) | SEC-OUTBOUND-POLLINATIONS (see carve-out #7) | partial |
| FR-9g / FR-9h (casting assign/unassign) | SEC-CASTING-WRITE (see carve-out #7) | partial |
| FR-86 (closed attribute schema) | SEC-OUTBOUND-POLLINATIONS (input validation prevents prompt injection beyond known options) | covered |

## Open carve-outs (per general.md principle 6)

The spec lists these as out-of-scope for v1; the security strategy surfaces them so the user can confirm:

1. **No auth / multi-user.** EXPOSED_TREE + Origin/Host gate + loopback-only are the entire trust boundary. Anyone with shell access to the box can `curl http://127.0.0.1:8766/api/file?path=ai_videos/...`. This is by design (localhost productivity tool) but must be re-confirmed.
2. **No file create / delete / upload.** PUT only edits existing-or-new files at allowed paths; there is no DELETE-file endpoint. A compromised SPA can still overwrite any allowed file with garbage. Confirm this risk is acceptable.
3. **No CSRF token beyond Origin/Host.** Origin checks suffice for state-changing endpoints because all mutations require an `Origin` header; browsers send `Origin` on cross-origin POST/PUT/DELETE per the Fetch spec. No additional CSRF token. Confirm.
4. **`<pre>` dark carve-out is fixed-palette, NOT OS-toggled (FR-80).** The user may want a system-following dark mode in v2; not a security issue but a UX surface that intersects with sanitization (CSS injection through markdown is blocked by SEC-SANITIZE).
5. **No rate limit on PUT / regen.** A buggy SPA loop or local script can saturate the 1-MiB cap repeatedly. Out of scope per spec; confirm.
6. **`/api/import-from-downloads` reads outside EXPOSED_TREE** (follow-up 009). This is the FIRST endpoint to do so. Hardening (per FR-9e): (a) source dir is fixed to `Path.home() / "Downloads"` (env override available for testing only); (b) only immediate children — no recursive scan; (c) extension whitelist (MEDIA_EXTENSIONS); (d) mtime window ≤ 7 days; (e) symlinks refused; (f) basename validation via `_BASENAME_INVALID` regex + length ≤ 255 before any `shutil.move`. Destinations stay inside EXPOSED_TREE (drama folder). Residual risks: (i) a maliciously-named recent download could occupy a destination filename that collides with existing drama assets (mitigated by `target_exists` 409); (ii) Downloads dir is shared with the OS and may contain unrelated user files — if any happens to substring-match a folder name, it will be moved; the user must reconcile via `not_matched/` review. Confirm this residual surface is acceptable; if not, a future follow-up could add per-file user confirmation before move.

7. **`/api/actors/generate` makes outbound HTTP to pollinations.ai** (follow-up 014). This is the FIRST endpoint where the backend issues requests to an external host (no API key, no auth, no signup; MIT-licensed open-source endpoint per `image.pollinations.ai`). Hardening (per FR-9f): (a) base URL hardcoded as `https://image.pollinations.ai/prompt/` — user input cannot replace or extend it; (b) prompt is **assembled server-side** from the closed enum schema (FR-86) — user cannot inject arbitrary characters except through the `notes` field, and `notes` is URL-encoded as part of the path segment; (c) per-image timeout 30s; (d) per-image response read cap 5 MiB; (e) batch size cap 20 — bounds total wall-clock to ~10 minutes worst case; (f) HTTP redirects are NOT followed (httpx `follow_redirects=False`) — prevents redirect-based SSRF to internal addresses; (g) writes land only inside `ai_videos/_actors/actor_NNNN/` (EXPOSED_TREE-inside; ID monotonically allocated, no overwrite). Residual risks: (i) pollinations.ai availability is a hard dependency — endpoint failure manifests as `errors[]` per image, no fallback (acceptable: user retries or shifts strategy); (ii) generated images are NOT filtered for content — a degenerate seed could produce an undesirable face, no human-in-the-loop check (user must delete via filesystem; v1 has no delete endpoint); (iii) backend now has internet egress as part of normal operation — anyone with localhost shell access can trigger external requests at our IP (low risk on a personal laptop; would be material if exposed to multi-user). The CSP `connect-src 'self'` is unchanged: the frontend never directly contacts pollinations.ai, all generation flows through `POST /api/actors/generate` which the backend proxies. **`/api/casting/assign` writes** only touch `ai_videos/{drama}/casting.md` inside EXPOSED_TREE; the same Origin/Host gap exists as for rename/archive/import (not in `GUARDED_ROUTES`) — confirm whether widening the gate is in or out of scope before merge.

If any of these is upgraded to in-scope by user follow-up, this strategy MUST be re-run.
