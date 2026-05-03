# Validation — Security probes

Run: `spec_driven-20260503-145859` · Worker: `level-specialist-05-security`

Source angle: `findings/angle-localhost-fs-sandbox-risks.md`. Severity policy: `.claude/agent_refs/validation/general.md` § Standard severity policy + `.claude/agent_refs/validation/development.md` § Severity escalations specific to development.

Convention: every probe is a row of **Class** / **CWE/CVE** / **Vector** / **Expected behavior** / **Pass criterion** / **Severity**. All security failures (any SEC-* miss) halt immediately per the standard policy — no revision rounds without explicit user approval.

The probe corpus is table-driven where possible (`tests/unit/test_path_sandbox.py` parametrize) so a new variant is one fixture row, not one new test function. Backend probes target `127.0.0.1:8765`; proxy probes target `127.0.0.1:5173` with the Vite proxy active.

---

## SEC-1 — Path traversal: literal `..` segments

- **Class:** Path traversal sandbox escape.
- **CWE:** CWE-22 (Improper Limitation of a Pathname to a Restricted Directory).
- **Vector:** `GET /api/file?path=../../etc/passwd`, `GET /api/file?path=specs/../../etc/passwd`, `GET /api/file?path=..\..\windows\system.ini`. Same payloads against `PUT /api/file`.
- **Expected behavior:** `resolve_safe()` rejects the literal `..` segment before any FS call. No `realpath` resolution happens. No file-existence side channel.
- **Pass criterion:** every probe returns `404` with the same generic body as a missing-file probe; response headers identical to a clean 404; no `errno`/`strerror` text in the body; latency within 5 % of a clean 404 (no timing oracle).
- **Severity:** `critical`.

## SEC-2 — Path traversal: percent-encoded variants

- **Class:** Path traversal sandbox escape via encoding.
- **CWE:** CWE-22 (decoded variants), CWE-172 (Encoding Error).
- **Vector:** `%2e%2e%2f`, `%2e%2e%5c`, double-encoded `%252e%252e%252f`, mixed case `%2E%2e%2F`, overlong UTF-8 `%c0%ae%c0%ae`, NUL byte `%00`. Probe against both GET and PUT.
- **Expected behavior:** server URL-decodes once, then runs `..` rejection. Double-encoded variants are NOT decoded twice (no recursive decode). Overlong UTF-8 is rejected at the codec layer.
- **Pass criterion:** all probes → single `404`. Property-based test (`hypothesis`) generates 200 random encoding combinations and asserts the same single-404 response.
- **Severity:** `critical`.

## SEC-3 — Path traversal: mixed slashes + absolute paths

- **Class:** Path traversal via separator confusion.
- **CWE:** CWE-22.
- **Vector:** `/etc/passwd`, `C:\Windows\System32\drivers\etc\hosts`, `\\?\C:\Windows\win.ini` (UNC form), `/specs/development/spec_driven/../../etc/shadow`, leading `/` or `\` on the path query. Mixed `..\\..\/..\\` separators.
- **Expected behavior:** absolute-path detection (`Path.is_absolute()`) AND leading `/`/`\` rejection happen before resolution. Mixed separators are normalized once and the result is re-validated.
- **Pass criterion:** all probes → `404`. Backend never reads outside `EXPOSED_TREE`; assert via a process-level `os.open` audit hook in the test fixture that no path outside the configured root is opened.
- **Severity:** `critical`.

## SEC-4 — Vite CVE-2025-62522 trailing-backslash bypass

- **Class:** Sandbox bypass via path-suffix trick.
- **CVE:** **CVE-2025-62522** (CWE-22). Affects Vite 2.9.18→<3, 3.2.9→<4, 4.5.3→<5, 5.2.6→<5.4.21, 6.0.0→<6.4.1, 7.0.0→<7.0.8, 7.1.0→<7.1.11. Patched 5.4.21 / 6.4.1 / 7.0.8 / 7.1.11.
- **Vector:** `GET /api/file?path=specs/development/spec_driven/final_specs/spec.md\` (trailing `\`); `GET /api/file?path=foo.png\` (resolves to `foo.png` on Windows under unpatched Vite); `GET /api/file?path=.env\`; `GET /api/file?path=CLAUDE.md/`; same trailing-`\` payload against `PUT /api/file`.
- **Expected behavior:** the Python backend independently rejects any path containing a literal `\` byte, ending in `\` or `/`, or containing `:` (drive letters / ADS) — BEFORE `realpath` resolution. The defense does NOT rely on Vite's filtering even when running under the dev proxy.
- **Pass criterion:** probe returns `404`. Backend `package.json` / `vite` lockfile pinned to a patched range (`>=7.1.11` for the v7 line). Test fixture asserts the installed Vite version is in the patched set OR the unit test for trailing-backslash path rejection passes (defense-in-depth — both must hold).
- **Severity:** `critical`.

## SEC-5 — Windows reserved device names

- **Class:** Windows reserved-name handling.
- **CWE:** CWE-66 (Improper Handling of File Names that Identify Virtual Resources).
- **Vector:** `GET /api/file?path=CON`, `?path=CON.md`, `?path=PRN.txt`, `?path=AUX`, `?path=NUL`, `?path=NUL.tar.gz`, `?path=COM1`, `?path=COM9.md`, `?path=COM1.json` (case variants `con`, `Con`, `CON`), `?path=LPT1`…`LPT9`, superscript-digit variants `COM¹`, `LPT²`. Same set against `PUT /api/file` (write probes).
- **Expected behavior:** path-component check matches `^(CON|PRN|AUX|NUL|COM[0-9¹²³]|LPT[0-9¹²³])(\.|$)` case-insensitively, rejects before any FS open. Real-world precedent: `claude-code` issue #16604 (literal `nul` file broke OneDrive sync).
- **Pass criterion:** every probe returns `404` (read) / `404` (write — sandbox-reject before extension check). No `nul` / `con` / etc. file is ever created on disk during the test; assert by globbing `EXPOSED_TREE` for matching basenames after the test run and asserting an empty result.
- **Severity:** `critical`.

## SEC-6 — NTFS Alternate Data Streams + 8.3 short names

- **Class:** Windows-specific filename-format bypass.
- **CWE:** CWE-66 (filename-format confusion); related to CWE-178 (Improper Handling of Case Sensitivity).
- **Vector:** ADS: `?path=spec.md::$DATA`, `?path=CLAUDE.md::$DATA`, `?path=specs/foo:hidden`, `?path=foo.md:stream:$DATA`. 8.3 short names: `?path=FILE~1.MD`, `?path=PROGRA~1`, `?path=SPEC_D~1/final_specs/SPEC~1.MD`. Mixed-case variants of each.
- **Expected behavior:** any path component containing `:` is rejected outright on all platforms (not just Windows). Any path component matching `~\d` regex is rejected. Both checks happen pre-resolve.
- **Pass criterion:** all probes → `404`. Documented carve-out: a legitimate file literally named `foo~1.md` would be rejected — `EXPOSED_TREE` contains no such files (asserted by a sweep test that fails if any tracked file matches the `~\d` pattern).
- **Severity:** `critical`.

## SEC-7 — POSIX symlink refusal (read path)

- **Class:** Link-following sandbox escape.
- **CWE:** CWE-59 (Improper Link Resolution Before File Access — "Link Following").
- **Vector:** create a symlink `specs/development/spec_driven/findings/leak.md` → `/etc/passwd` (POSIX) or to `..\..\..\Windows\win.ini` (Windows under Developer Mode). `GET /api/file?path=specs/development/spec_driven/findings/leak.md`. Also probe a directory whose ancestor was replaced by a symlink mid-walk (TOCTOU).
- **Expected behavior:** per-component `Path.is_symlink()` check during resolution refuses the path outright if any ancestor or the leaf itself is a symlink. NO `realpath`-and-re-verify fallback (refused outright per spec OQ-4 resolution).
- **Pass criterion:** probe returns `404`. Test marker `pytest.mark.skipif(sys.platform == "win32", reason="POSIX symlinks require Developer Mode on Windows; covered by SEC-8 junction probe")` per `agent_refs/validation/development.md` § 5.
- **Severity:** `critical`.

## SEC-8 — Windows junction refusal

- **Class:** Link-following sandbox escape (Windows variant).
- **CWE:** CWE-59. Microsoft RedirectionGuard (Windows 11, June 2025) acknowledges junctions as the largest residual junction-traversal gap.
- **Vector:** `mklink /J specs\junction_leak C:\Windows\System32` then `GET /api/file?path=specs/junction_leak/drivers/etc/hosts`. Also probe `mklink /D` directory symlinks and registry-symlink-style indirection where applicable.
- **Expected behavior:** junctions are detected via `Path.is_symlink()` (which returns True for NTFS junctions in Python 3.10+) AND via a defensive `os.lstat` reparse-point check on Windows. Refused outright; no realpath fallback.
- **Pass criterion:** probe returns `404`. Assert no read happens on the junction target (file-system audit hook in the fixture). Marked `pytest.mark.skipif(sys.platform != "win32", reason="Windows-only junction test")`.
- **Severity:** `critical`.

## SEC-9 — Extension allowlist enforcement

- **Class:** Unrestricted file type / executable-content vector.
- **CWE:** CWE-434 (Unrestricted Upload of File with Dangerous Type).
- **Vector:** `GET /api/file?path=spec.exe`, `?path=spec.bat`, `?path=spec.svg`, `?path=spec.html`, `?path=spec.php`, `?path=spec.tar.gz`, `?path=spec.md.exe` (double extension). Same probes against `PUT /api/file`. Image-write probes (`PUT /api/file?path=foo.png`) — must be blocked by FR-8.
- **Expected behavior:** allowlist is exact-match on the final extension after canonicalization: `.md`, `.json`, `.yaml`, `.yml`, `.jsonl`, `.txt`, `.png`, `.jpg`. Anything else → `415`. SVG explicitly NOT in allowlist (code-execution vector). PUT to `.png` / `.jpg` → `415` (FR-8: image extensions not writable).
- **Pass criterion:** every disallowed-extension probe → `415` with `{detail: {kind: "extension_not_allowed"}}`. Allowed extensions → `200`. Double-extension `.md.exe` resolves to `.exe` final → `415`. Test the full extension allowlist as a parametrized truth table.
- **Severity:** `critical`.

## SEC-10 — Size cap enforcement (1 MB read + write)

- **Class:** Resource exhaustion / DoS via oversized payload.
- **CWE:** CWE-770 (Allocation of Resources Without Limits or Throttling).
- **Vector:** `GET /api/file?path=oversized.md` where the on-disk file is 1.5 MB; `PUT /api/file` with a 1.5 MB body; `POST /api/regen-prompt` whose assembled output would be ≥1 MB; `Content-Length: 0` with a chunked-encoded 2 MB body (length-claim mismatch).
- **Expected behavior:** read-side checks file size via `Path.stat().st_size` before opening; write-side checks `Content-Length` header AND streams with a hard 1 MB ceiling (no buffering past the cap). Chunked encoding still hits the streaming cap. Regen-prompt assembly checks final byte length post-assembly.
- **Pass criterion:** oversized read → `413 {detail: {kind: "too_large"}}`; oversized write → `413 {detail: {kind: "too_large"}}`; oversized regen → `413 {detail: {kind: "too_large"}}` per FR-12. Memory profile during the chunked-encoding probe stays below 8 MB peak (no buffer-the-whole-body anti-pattern).
- **Severity:** `critical`.

## SEC-11 — Origin / Host validation: foreign origins

- **Class:** Cross-Site Request Forgery.
- **CWE:** CWE-352 (Cross-Site Request Forgery).
- **Vector:** `PUT /api/file` with `Origin: https://evil.com`; `Origin: http://127.0.0.1:9999` (wrong port); `Origin: http://127.0.0.1` (no port — same site, wrong allowlist match); missing `Origin` header entirely; `Origin: null`; `Origin: file://`; `Origin: http://[::1]:8765` (IPv6 — explicitly out of scope per OQ-8). Same payloads against `POST /api/regen-prompt`, `POST /api/promote`, `DELETE /api/promote`.
- **Expected behavior:** the four state-changing endpoints share one middleware that allow-lists `Origin ∈ {http://127.0.0.1:8765, http://localhost:8765}` and `Host ∈ {127.0.0.1:8765, localhost:8765}`. Anything else → `403`. Loopback aliases admit (same socket).
- **Pass criterion:** all foreign-origin probes → `403` with `{detail: {kind: "origin_blocked"}}`. Loopback aliases → `200`. Verb whitelist holds (PATCH/DELETE on `/api/file` → `405` per SEC-19). Per `agent_refs/validation/development.md` § 7, BOTH pre- and post-rewrite shapes are tested (see SEC-21).
- **Severity:** `critical`.

## SEC-12 — DNS rebinding via Host header

- **Class:** DNS rebinding to localhost.
- **CWE:** CWE-350 (Reliance on Reverse DNS Resolution for a Security-Critical Action) + CWE-352.
- **Vector:** `PUT /api/file` with `Host: 127.0.0.1.evil.com:8765`; `Host: localhost.attacker.test:8765`; `Host: 127.0.0.1:8765.evil.com`; `Host: 127.0.0.1` (no port, ambiguous); `Host: 127.0.0.2:8765` (different loopback IP).
- **Expected behavior:** Host allowlist exact-matches `{127.0.0.1:8765, localhost:8765}`; substring/suffix matches are rejected. The Host-rebind variant (`127.0.0.1.evil.com`) does NOT match `127.0.0.1:8765`. Stanford DNS-rebinding paper / MCP Python SDK "421 Invalid Host Header" pattern.
- **Pass criterion:** all rebind variants → `403`. Test parametrizes the full string-match boundary cases. Probe the same against the GET path's optional Host check (defense-in-depth — even though GET is non-state-changing, leaking arbitrary file content to a rebound origin is a confidentiality issue).
- **Severity:** `critical`.

## SEC-13 — Source-grep: no `0.0.0.0` LAN bind anywhere in `projects/spec_driven/`

- **Class:** Configuration / supply-chain leak via accidental wide bind.
- **CWE:** CWE-668 (Exposure of Resource to Wrong Sphere).
- **Vector:** static analysis. `rg -F '0.0.0.0' projects/spec_driven/` (all files), `rg -F 'host="0.0.0.0"' projects/spec_driven/`, `rg -F "host='0.0.0.0'" projects/spec_driven/`, `rg --pcre2 'uvicorn\.run\([^)]*0\.0\.0\.0' projects/spec_driven/`, plus a Makefile grep `rg -F '0.0.0.0' projects/spec_driven/Makefile`.
- **Expected behavior:** zero literal `0.0.0.0` matches anywhere under `projects/spec_driven/` (source, Makefile, Vite config, env templates, tests, fixtures). Per spec OQ-9: cross-port LAN bind is explicitly out of scope; SEC-13 is the audit that prevents accidental introduction.
- **Pass criterion:** the grep command emits an empty result. Test runs as a pytest unit test (`test_no_lan_bind`) and an additional CI lint step. A non-empty result fails the test with the file path so the regression is immediately diagnosable.
- **Severity:** `critical`.

## SEC-14 — Markdown XSS via raw `<script>`

- **Class:** Stored / reflected XSS via markdown.
- **CWE:** CWE-79 (Cross-site Scripting).
- **Vector:** craft a markdown file under `EXPOSED_TREE` with `<script>alert('xss')</script>`, `<script src="//evil.com/x.js"></script>`, raw `<iframe srcdoc="...">`, raw `<object data="...">`, raw `<embed>`, `<svg onload="alert(1)">`. Probe via the SPA at `/file/<encoded-path>` and assert the rendered DOM.
- **Expected behavior:** `react-markdown` + `rehype-sanitize` (default schema) drops the raw HTML before render. Default schema disallows `<script>`, `<iframe>`, `<object>`, `<embed>`, raw `<svg>`. No execution occurs.
- **Pass criterion:** Playwright loads the file, asserts `page.evaluate(() => window.__xss_executed)` is undefined, asserts `await page.locator('script[src*="evil.com"]').count() === 0`, asserts `consoleErrors` is empty. Unit test (`test_markdown_view_strips_script`) renders via JSDOM and asserts the same.
- **Severity:** `critical`.

## SEC-15 — Markdown XSS via event handlers + `javascript:` URIs

- **Class:** XSS via attribute injection.
- **CWE:** CWE-79.
- **Vector:** markdown with `[click me](javascript:alert(1))`, `[click me](JaVaScRiPt:alert(1))`, `[click me](data:text/html,<script>alert(1)</script>)`, `<a href="javascript:alert(1)">x</a>` (raw), `<img src=x onerror=alert(1)>` (raw), `[x](#" onclick="alert(1))` (attribute-break injection).
- **Expected behavior:** rehype-sanitize default schema strips `on*` attributes and rejects `javascript:` / `data:` URI schemes on `<a>` href + `<img>` src. The link is rendered as plain text or as a muted span (broken link convention from FR-19), never as a clickable navigation.
- **Pass criterion:** Playwright clicks every link in the rendered file and asserts no navigation to `javascript:` or unexpected origins; asserts no `alert` dialog fired (`page.on('dialog', ...)` raises if it does); asserts `consoleErrors` is empty. Unit test parametrizes 20 attribute-injection variants and asserts the sanitized output contains none of them.
- **Severity:** `critical`.

## SEC-16 — `rehype-sanitize` default schema enforcement

- **Class:** XSS via misconfigured sanitizer.
- **CWE:** CWE-79 + CWE-1188 (Insecure Default Initialization of Resource).
- **Vector:** static + runtime checks. Static: grep `projects/spec_driven/frontend/src/` for `rehype-sanitize` usage and assert the import is `import rehypeSanitize from 'rehype-sanitize'` with NO custom `schema` argument (or with an explicit `defaultSchema` import — both signal default-schema enforcement). Runtime: render a corpus of 30 known-bad payloads and assert every one is sanitized.
- **Expected behavior:** the sanitizer is invoked with the **default schema**. No `allowedTags` / `allowedAttributes` widening anywhere in the codebase. Custom schemas would be a `critical` finding.
- **Pass criterion:** static grep returns either zero custom-schema usages OR every custom-schema usage is the documented `defaultSchema` reference; runtime corpus passes. Plus a regression test that fails if anyone widens the schema in a future PR.
- **Severity:** `critical`.

## SEC-17 — Single-404 enumeration policy

- **Class:** Information disclosure via response side-channel.
- **CWE:** CWE-204 (Observable Response Discrepancy).
- **Vector:** probe a series of paths that fail for *different* reasons and compare responses byte-by-byte: (a) outside `EXPOSED_TREE` (`/etc/passwd`), (b) inside tree but file absent, (c) inside tree but extension disallowed, (d) inside tree but path contains `..`, (e) inside tree but symlink-rejected. ALL must collapse to the SAME 404 unless the spec specifically defines a different status (extension → 415 per FR-4 + SEC-9; size → 413 per FR-12 + SEC-10).
- **Expected behavior:** "path outside `EXPOSED_TREE`" and "file does not exist inside `EXPOSED_TREE`" return identical `404` responses (same body, same headers, no `errno`/`strerror` leak, no realpath leak per NFR-10). Latency within 5 % across the variants (no timing oracle).
- **Pass criterion:** test diffs response body + headers across all 404-class probes; asserts byte-equality of body and identity-equality of header set (modulo `Date`). Latency oracle test: 1000 probes per variant, t-test fails to reject `H0: same mean` at p>0.01.
- **Severity:** `blocker` (information disclosure, not a sandbox escape).

## SEC-18 — Security headers on every `GET /api/file`

- **Class:** Defense-in-depth header gating.
- **CWE:** CWE-693 (Protection Mechanism Failure).
- **Vector:** `GET /api/file?path=CLAUDE.md`, `?path=specs/development/spec_driven/final_specs/spec.md`, `?path=foo.png` (image), `?path=foo.json` (json), `?path=foo.jsonl` (jsonl), `?path=foo.txt` (txt). Inspect response headers.
- **Expected behavior:** every successful `GET /api/file` carries BOTH `X-Content-Type-Options: nosniff` AND `Content-Disposition: attachment; filename="<ascii-safe>"`. Per FR-5 + the OWASP File Upload Cheat Sheet — the pair is load-bearing because `Content-Disposition` alone is bypassable (markitzeroday "defeating Content-Disposition"); `nosniff` alone leaves `text/plain` payloads sniffable; the pair closes both.
- **Pass criterion:** parametrized header-presence test across the full extension allowlist asserts both headers present on every successful 200. Filename in `Content-Disposition` is ASCII-safe (no high-bit bytes, no CRLF). Test fails loudly if either header is missing or if the filename contains a CR/LF (header-injection regression).
- **Severity:** `blocker`.

## SEC-19 — Verb whitelist (`PATCH` / `DELETE` on `/api/file` → `405`)

- **Class:** Mutation surface containment.
- **CWE:** CWE-749 (Exposed Dangerous Method or Function).
- **Vector:** `PATCH /api/file?path=foo.md`, `DELETE /api/file?path=foo.md`, `OPTIONS /api/file`, `TRACE /api/file`, `HEAD /api/file?path=foo.md`. Same verbs against `/api/tree`, `/api/stages`, `/api/regen-prompt`, `/api/promote`.
- **Expected behavior:** per NFR-6, mutation surface is exactly four endpoints (`PUT /api/file`, `POST /api/regen-prompt`, `POST /api/promote`, `DELETE /api/promote`). PATCH and DELETE on `/api/file` → `405 Method Not Allowed` per AC-12. `HEAD` may be allowed on read endpoints (FastAPI default) but must NOT short-circuit the Origin/Host gate when used in a state-changing-adjacent context.
- **Pass criterion:** the verb truth table is asserted across every endpoint. Unexpected-200 on a non-allowlisted verb fails the gate.
- **Severity:** `blocker`.

## SEC-20 — Read-zero contract preserved verbatim across the autonomous + interactive matrix

- **Class:** Regeneration semantics regression.
- **CWE:** CWE-754 (Improper Check for Unusual or Exceptional Conditions) — analog: silent omission of a load-bearing constraint sentence.
- **Vector:** call `POST /api/regen-prompt` with the full 2×N matrix: `{autonomous: false} × N` and `{autonomous: true} × N`, where N covers the six stages individually + project-level (selecting all six). For each assembled prompt, search for the exact read-zero contract sentences from `CLAUDE.md` § Regeneration semantics: read-zero from prior outputs.
- **Expected behavior:** every assembled prompt's `### Constraints` section contains the read-zero contract sentences VERBATIM (modulo line wrapping). The per-stage delete-then-regenerate table is included verbatim. The Files-to-preserve column (`<stage>/promoted.md`) is preserved verbatim. The audit-event protocol (`regen.delete.planned` → `regen.delete.completed` → `regen.write.completed`) is included verbatim. Per FR-37 and follow-up 005's contract-preservation rule: the webapp's `regen_prompt.py` MUST inline the contract from a single source of truth (no copy-paste drift between `CLAUDE.md` and the assembled prompt).
- **Pass criterion:** test fixture loads `CLAUDE.md`, extracts the canonical contract sentences (via marker comments or section anchors), and asserts byte-equality of those sentences in every assembled prompt across the 14-prompt matrix. Drift between `CLAUDE.md` and assembled prompt → `critical` regression. Test runs in CI on every change to either `CLAUDE.md` or `regen_prompt.py`.
- **Severity:** `critical`.

## SEC-21 — Pre-proxy-rewrite shape: `Origin: http://localhost:5173` direct-to-backend → `403`

- **Class:** Proxy-rewrite contract regression.
- **CWE:** CWE-352 (CSRF — variant: missing reverse-proxy hardening).
- **Vector:** `PUT /api/file` sent DIRECTLY to `127.0.0.1:8765` (bypassing Vite) with `Origin: http://localhost:5173` and `Host: localhost:5173`. This is the EXACT shape the browser produces when the dev-server proxy is misconfigured / missing its `configure(proxy => proxy.on('proxyReq', ...))` hook.
- **Expected behavior:** the backend `Origin`/`Host` middleware refuses the raw browser-shape request → `403`. Dropping the Vite `Origin` rewrite hook silently re-introduces the bug (`spec_driven-006` regression). Per `agent_refs/validation/development.md` § 11 (Header-mutating-layer middleware tests cover both shapes), this **pre-rewrite** test is load-bearing — it proves the proxy rewrite is *required*, not optional.
- **Pass criterion:** unit test (`test_origin_middleware_rejects_pre_rewrite_shape`) sends the raw browser-shape `PUT` direct to the backend and asserts `403`. Companion test (`test_origin_middleware_accepts_post_rewrite_shape`) sends `Origin: http://127.0.0.1:8765` and asserts `200` (or whatever the endpoint's normal success status is). BOTH tests must exist; missing the pre-rewrite case → `blocker` per the dev refs severity table.
- **Severity:** `blocker`.

## SEC-22 — Dev-server proxy rewrite hook present in `vite.config.ts`

- **Class:** Static-config regression — the Vite proxy actually wires the rewrite up.
- **CWE:** CWE-1188 (Insecure Default Initialization of Resource).
- **Vector:** static analysis of `projects/spec_driven/frontend/vite.config.ts`. Grep for `server.proxy['/api'].configure` AND for `proxyReq.setHeader('Origin'` AND for `proxyReq.setHeader('Host'` (or equivalent). Plus a runtime e2e probe through `make run-frontend` that sends a `PUT /api/file` and asserts the backend gate sees `Origin: http://127.0.0.1:8765` (verified via a backend-side audit hook that records the `Origin` value of the request that arrived).
- **Expected behavior:** `vite.config.ts` defines a `server.proxy['/api']` entry with `changeOrigin: true` AND a `configure(proxy => { proxy.on('proxyReq', (proxyReq, req) => { proxyReq.setHeader('Origin', 'http://127.0.0.1:8765'); }) })` hook. The hook is active at dev-server startup. Per FR-9 dev-server proxy contract.
- **Pass criterion:** static grep finds all three markers. Runtime e2e: backend audit-hook log shows `Origin: http://127.0.0.1:8765` (post-rewrite) for every `/api/*` request that arrived through `127.0.0.1:5173`. Hook missing or grep mismatch → `blocker` per `agent_refs/validation/development.md` § 11.
- **Severity:** `blocker`.

---

## Probe execution layout

- Unit-test surface: `projects/spec_driven/backend/tests/unit/test_path_sandbox.py`, `test_origin_host_middleware.py`, `test_extension_allowlist.py`, `test_size_cap.py`, `test_security_headers.py`, `test_verb_whitelist.py`, `test_no_lan_bind.py`, `test_regen_contract_preservation.py`.
- Frontend unit-test surface: `projects/spec_driven/frontend/src/__tests__/MarkdownView.security.test.tsx` (XSS corpus + sanitizer config).
- E2E surface: `projects/spec_driven/e2e/security.spec.ts` — DNS-rebind, dev-proxy header rewrite verification, end-to-end XSS payload render checks.
- Static analysis: `make security-audit` runs the source greps (SEC-13, SEC-22) and the regen-contract-preservation regression (SEC-20) as a single CI gate.

## Severity rollup

| Severity | Probes | Halt? |
|---|---|---|
| `critical` | SEC-1, SEC-2, SEC-3, SEC-4, SEC-5, SEC-6, SEC-7, SEC-8, SEC-9, SEC-10, SEC-11, SEC-12, SEC-13, SEC-14, SEC-15, SEC-16, SEC-20 | Yes — immediate halt; no revision rounds without explicit user approval. |
| `blocker` | SEC-17, SEC-18, SEC-19, SEC-21, SEC-22 | Standard 3-revision-round cap. |

Per `agent_refs/validation/general.md` § Standard severity policy, every `critical` probe failure halts immediately. The 17 `critical` probes form the security gate; the 5 `blocker` probes are still load-bearing but follow the standard revision-round cadence.

## Pre-reading consulted

- `C:/workspace/spec_coding/CLAUDE.md`
- `C:/workspace/spec_coding/.claude/skills/agent_team/SKILL.md`
- `C:/workspace/spec_coding/.claude/skills/agent_team/playbooks/validation.md`
- `C:/workspace/spec_coding/.claude/agent_refs/validation/general.md`
- `C:/workspace/spec_coding/.claude/agent_refs/validation/development.md`
- `C:/workspace/spec_coding/specs/development/spec_driven/final_specs/spec.md`
- `C:/workspace/spec_coding/specs/development/spec_driven/findings/angle-localhost-fs-sandbox-risks.md`
- `C:/workspace/spec_coding/specs/development/spec_driven/validation/promoted.md`
