# Validation — Security level

Stage: 5 (Validation strategy) — clean-state regeneration
Run: spec_driven-20260503-030434
Specialist: level-specialist-05-security
Inputs read: `final_specs/spec.md` (FR-3..9, NFR-4..9, AC-3..12, AC-29), `findings/angle-localhost-fs-sandbox-risks.md`, `CLAUDE.md`, `.claude/skills/agent_team/playbooks/validation.md`, `.claude/agent_refs/validation/general.md`, `.claude/agent_refs/validation/development.md`.

This catalogue defines the security probes that exercise the spec's hardening claims. Each entry is a single test the validator runs against a live `127.0.0.1:8765` instance (or against the underlying `safe_resolve` / sanitizer for unit-shape probes that do not require HTTP). All HTTP probes default to a benign `Origin: http://127.0.0.1:8765` and `Host: 127.0.0.1:8765` unless the probe explicitly tests CSRF / DNS rebinding.

Severity contract (per `.claude/agent_refs/validation/general.md` and prompt rules):
- `critical` — any path-traversal / sandbox-escape success, ADS bypass, reparse-point bypass, sanitizer XSS that reaches the DOM.
- `blocker` — missing security header on the success path, or `0.0.0.0` bind in any default config.
- `high` — verb / extension / size-cap / Origin-Host enforcement gap that does NOT escape the sandbox but trivially bypasses the documented rule.
- `medium` — enumeration side-channel (403/404 split, error-message leakage).

---

## SEC-01 — Path traversal via `..` (POSIX form)
- **Attack vector:** `GET /api/file?path=../etc/passwd`, `GET /api/file?path=specs/../../etc/passwd`, `GET /api/file?path=specs/development/../../../CLAUDE.md` (last form deliberately resolves *back inside* the tree to confirm the rule is "containment after canonicalization", not "any `..` is rejected outright").
- **Expected behavior:** Every request returns **404** with no body that names whether the file exists. `safe_resolve` rejects on `..` after normalization for the first two; the third resolves back into the EXPOSED_TREE and MAY return 200 (containment-based rule per FR-4) — flag as informational, not a failure.
- **Pass criterion:** Status `404` for the first two probes; no `Content-Disposition` containing the absolute attacker path; response identical (modulo timing) to the "outside EXPOSED_TREE" probe in SEC-18.
- **Severity:** `critical` if any of the first two returns 200 or leaks bytes from outside the tree.
- **CWE:** CWE-22 (Path Traversal).
- **Components exercised:** FR-3, FR-4, AC-3, NFR-4.

## SEC-02 — Path traversal via URL-encoded `..` (`..%2f`, `%2e%2e/`, `%2e%2e%2f`)
- **Attack vector:** `GET /api/file?path=..%2fetc%2fpasswd`, `GET /api/file?path=%2e%2e%2fetc%2fpasswd`, `GET /api/file?path=specs%2f..%2f..%2fetc%2fpasswd`.
- **Expected behavior:** FastAPI / Starlette decodes the query string before the handler sees it, so `safe_resolve` receives literal `..` and rejects per SEC-01.
- **Pass criterion:** All return **404**. No 200 / 500.
- **Severity:** `critical` on any 200.
- **CWE:** CWE-22.
- **Components exercised:** FR-3, FR-4, AC-3.

## SEC-03 — Path traversal via Windows backslash (`..\`, `..%5c`)
- **Attack vector:** `GET /api/file?path=..\etc\passwd`, `GET /api/file?path=..%5cetc%5cpasswd`, `GET /api/file?path=specs%5c..%5c..%5cCLAUDE.md` — the canonical Vite CVE-2025-62522 regression. Run on both Windows and POSIX (POSIX should still treat `\` as a valid path char and refuse, because `safe_resolve` normalizes BEFORE checking traversal per FR-4 / findings 2b).
- **Expected behavior:** `safe_resolve` normalizes `\` → `/` first, then applies `..` rejection. Both forms return 404.
- **Pass criterion:** Status `404`; no platform divergence.
- **Severity:** `critical` on any 200; `high` on a platform-divergent result (POSIX rejects, Windows accepts) — that is the exact Vite regression class.
- **CWE:** CWE-22.
- **Components exercised:** FR-4, NFR-13.

## SEC-04 — Absolute path outside EXPOSED_TREE
- **Attack vector:** `GET /api/file?path=/etc/passwd` (POSIX), `GET /api/file?path=C:\Windows\System32\drivers\etc\hosts` (Windows), `GET /api/file?path=/proc/self/environ`.
- **Expected behavior:** `safe_resolve` rejects absolute paths (FR-4 explicit clause).
- **Pass criterion:** Status `404`. Body MUST NOT differ from the SEC-08 (extension-disallowed inside tree) body in a way that lets an attacker enumerate which case they hit — see SEC-18.
- **Severity:** `critical` on any 200.
- **CWE:** CWE-22.
- **Components exercised:** FR-4, AC-3, NFR-4.

## SEC-05 — Windows reserved device names
- **Attack vector:** `GET /api/file?path=specs/development/spec_driven/CON.md`, `…/PRN.md`, `…/AUX.md`, `…/NUL.md`, `…/COM1.md`, `…/LPT1.md`. Also case-mixed (`Con.MD`, `nUl.md`) and bare (`specs/CON`).
- **Expected behavior:** `safe_resolve` rejects on the basename allow-list per FR-4 regardless of extension or case.
- **Pass criterion:** Status `404` for every variant. AC-4 is the spec's anchor for this probe.
- **Severity:** `critical` on any 200 or 500 (a 500 means the OS device alias was actually opened).
- **CWE:** CWE-22 (alias resolution into a non-file device).
- **Components exercised:** FR-4, AC-4.

## SEC-06 — Alternate Data Streams (ADS)
- **Attack vector:** `GET /api/file?path=specs/development/spec_driven/final_specs/spec.md::$DATA`, `…/spec.md:hidden`, `…/spec.md:hidden.txt`, URL-encoded `…/spec.md%3a%3a%24DATA`.
- **Expected behavior:** `safe_resolve` rejects any path segment with `:` other than the drive-letter colon at index 1, AND rejects `::$DATA` literally (FR-4).
- **Pass criterion:** Status `404` for every form. AC-5 is the spec's anchor.
- **Severity:** `critical` on any 200 — ADS exposes alternate metadata streams that the user did not consent to expose.
- **CWE:** CWE-22 / CWE-538 (file/directory information exposure).
- **Components exercised:** FR-4, AC-5.

## SEC-07 — 8.3 short-name aliases (`PROGRA~1`)
- **Attack vector:** `GET /api/file?path=PROGRA~1/something.md`, `GET /api/file?path=specs/DEVELO~1/spec_driven/final_specs/spec.md` (where `DEVELO~1` is the 8.3 alias for `development`). On filesystems where 8.3 generation is disabled, this probe MAY natively 404 — the test runner injects a synthetic alias via a fixture directory or skips with a recorded reason.
- **Expected behavior:** `safe_resolve` rejects any segment containing `~<digit>` smell BEFORE resolution, OR resolves and re-checks containment after canonicalization (the spec's preferred form per findings 2b).
- **Pass criterion:** Status `404`. If the alias would otherwise resolve into the tree, the test fails — short-name canonicalization MUST not be a back-door.
- **Severity:** `critical` on a successful read; `high` on a successful read of a file that would also be reachable by its long name (still a rule violation even if the bytes are the same).
- **CWE:** CWE-22.
- **Components exercised:** FR-4.

## SEC-08 — Reparse points / NTFS junctions
- **Attack vector:** Set up a junction `specs/development/spec_driven/_junc -> C:\Windows` (test fixture, Windows-only). Then `GET /api/file?path=specs/development/spec_driven/_junc/win.ini`.
- **Expected behavior:** `safe_resolve` lstats every segment of the resolved path and refuses if `FILE_ATTRIBUTE_REPARSE_POINT` is set on any segment (FR-4, NFR-5).
- **Pass criterion:** Status `404`. AC-6 is the spec's anchor.
- **Severity:** `critical` on any 200 — junctions are the canonical Windows sandbox-escape vector.
- **CWE:** CWE-59 (Link Following).
- **Components exercised:** FR-4, NFR-5, AC-6.
- **Platform note:** Windows-only setup; on POSIX the test is skipped with `pytest.mark.skipif(sys.platform != "win32", reason="junction setup is Windows-specific")` per NFR-12. Skipping is fine; silent passing is not.

## SEC-09 — POSIX symlink crossing the sandbox
- **Attack vector:** `ln -s /etc/passwd specs/development/spec_driven/_link.md` then `GET /api/file?path=specs/development/spec_driven/_link.md`. POSIX-only; on Windows substitute SEC-08 junction.
- **Expected behavior:** `safe_resolve` is_symlink check rejects the resolved path before reading bytes (FR-4, NFR-5).
- **Pass criterion:** Status `404`.
- **Severity:** `critical` on any 200.
- **CWE:** CWE-59.
- **Components exercised:** FR-4, NFR-5.
- **Platform note:** `pytest.mark.skipif(sys.platform == "win32", reason="POSIX symlink setup")`. Use SEC-08 instead on Windows.

## SEC-10 — Disallowed extension on read
- **Attack vector:** `GET /api/file?path=evil.exe`, `…/scratch.bat`, `…/payload.ps1`, `…/x.svg` (SVG explicitly NOT in the allowlist per NFR-9 / FR-3), `…/x.dll`, `…/x.com` (also doubles as SEC-05 device-name check via the `.com` suffix). Run with the file actually present inside the tree (fixture write) to ensure the rejection is on extension, not on existence.
- **Expected behavior:** Status `415` (FR-3 disallowed-extension contract). Body matches the documented error shape (no leakage of which directory was probed).
- **Pass criterion:** Status `415` exactly; not `404`, not `403`, not `200`. AC-8 is the spec's anchor.
- **Severity:** `high` on `200` (extension allowlist failed); `medium` on `404` (consistent with SEC-18 enumeration policy but inconsistent with FR-3, which mandates `415`).
- **CWE:** CWE-434 (Unrestricted Upload — applied here in the read direction as "served what we should not serve").
- **Components exercised:** FR-3, NFR-9, AC-8.

## SEC-11 — File >1 MB on read
- **Attack vector:** Fixture-write a 1.5 MB `.md` file inside the tree, then `GET /api/file?path=<that path>`.
- **Expected behavior:** Status `413` (FR-3 size-cap contract). AC-7 anchor.
- **Pass criterion:** Status `413` and `Content-Length` of response is small (no streaming of the file's prefix before the cap fires).
- **Severity:** `high` on `200` (size cap failed); `medium` on `413` that arrives only after the full file was read into memory (DoS risk).
- **CWE:** CWE-770 (Allocation of Resources Without Limits).
- **Components exercised:** FR-3, AC-7.

## SEC-12 — PUT body >1 MB
- **Attack vector:** `PUT /api/file` with a 1.5 MB body (`{path: "…/scratch.md", content: "<1.5 MB of 'a'>"}`).
- **Expected behavior:** Status `413` with body `{detail: {kind: "too_large"}}` (FR-7, AC-10). The cap is enforced at FastAPI level (and at any reverse-proxy layer per FR-7) BEFORE the full body lands in memory, per OWASP File Upload Cheat Sheet (findings 2c).
- **Pass criterion:** Status `413` AND `response.json()["detail"]["kind"] == "too_large"`. The verbatim `kind` key is the contract — string comparison, not regex.
- **Severity:** `high` on `200` (write succeeded); `high` on `413` without the `kind: "too_large"` discriminator (rule violated even if status is right).
- **CWE:** CWE-770.
- **Components exercised:** FR-7, NFR-11, AC-10.

## SEC-13 — PUT with binary content (NUL bytes) to a `.md` path
- **Attack vector:** `PUT /api/file {path: "…/scratch.md", content: " <arbitrary bytes>"}` — the first 16 bytes contain NUL.
- **Expected behavior:** Status `415` (FR-8 first-16-bytes plain-text check rejects NUL).
- **Pass criterion:** Status `415`; on-disk file is unchanged (`mtime` unchanged from a baseline `GET` taken before the probe). The probe is a write-attempt; assert no partial write.
- **Severity:** `critical` on `200` AND on-disk content actually now contains NUL bytes (corruption + content-type smuggling); `high` on `200` with the NUL stripped (silent rewriting); `high` on `400` (wrong status — spec mandates `415` to keep the discriminator consistent with FR-3).
- **CWE:** CWE-434, CWE-138 (Improper Neutralization of Special Elements).
- **Components exercised:** FR-8.

## SEC-14 — PUT to a `.png` / `.jpg` path
- **Attack vector:** `PUT /api/file {path: "…/scratch.png", content: "<base64 png bytes>"}` and `…/scratch.jpg` likewise. Run with both a real PNG payload and a text payload to confirm the rule rejects on extension, not on magic-bytes.
- **Expected behavior:** Status `415` (FR-8 — image extensions are NOT writable in v1).
- **Pass criterion:** Status `415` for every payload; on-disk file (if it pre-existed) unchanged.
- **Severity:** `high` on `200`; `medium` on `400` (rejection is right, status is wrong — discriminator drift).
- **CWE:** CWE-434.
- **Components exercised:** FR-8, NFR-9.

## SEC-15 — PATCH and DELETE on `/api/file` return 405
- **Attack vector:** `PATCH /api/file?path=…/spec.md` with a JSON-merge-patch body, `DELETE /api/file?path=…/spec.md`. Also `OPTIONS` and `TRACE` for completeness — `OPTIONS` MAY return 200 with `Allow: GET, PUT`; `TRACE` MUST be `405` or disabled.
- **Expected behavior:** `405 Method Not Allowed` for `PATCH`, `DELETE`, `TRACE`. `Allow` response header lists the accepted methods (`GET, PUT`) so clients can self-correct (NFR-6, AC-12).
- **Pass criterion:** Status `405` AND `Allow: GET, PUT` (case-insensitive header value comparison; both methods must be present).
- **Severity:** `high` on any non-405 (especially `200` on `DELETE` — that would be a sandbox-escape via verb).
- **CWE:** CWE-749 (Exposed Dangerous Method).
- **Components exercised:** FR-6, NFR-6, AC-12.

## SEC-16 — POST without `Origin` from bound localhost
- **Attack vector:** `POST /api/regen-prompt` (and equivalently `PUT /api/file`, `POST /api/promote`, `DELETE /api/promote`) with the `Origin` header omitted entirely; also with `Origin: null` (browsers send this for `file://` and sandboxed iframes); also with `Origin: http://attacker.example.com`.
- **Expected behavior:** Status `403` for every form per FR-9 / NFR-7 (defense against DNS-rebinding / browser-driven CSRF). Tooling-style requests (curl, server-to-server) that legitimately have no `Origin` are NOT supported by v1 — the webapp's only client is a browser bound to `http://127.0.0.1:8765`.
- **Pass criterion:** Status `403` AND no side-effect (write not applied; promoted.md unchanged; no audit event of type `regen.delete.planned`).
- **Severity:** `high` on `200` (rule violation); `high` on `403` with side-effect (audit log shows the action ran before the rejection).
- **CWE:** CWE-352 (CSRF), CWE-918 (SSRF — partial, since DNS rebinding is the SSRF-cousin attack).
- **Components exercised:** FR-9, NFR-7, AC-11.

## SEC-17 — POST with `Host: 127.0.0.1.evil.com` (DNS-rebinding pattern)
- **Attack vector:** `POST /api/regen-prompt` with `Origin: http://127.0.0.1:8765` (looks legitimate) AND `Host: 127.0.0.1.evil.com` (the rebinding pattern — attacker domain that previously resolved to `127.0.0.1`). Also `Host: 127.0.0.1:8765.evil.com`, `Host: localhost.attacker.com`.
- **Expected behavior:** Status `403` per FR-9 — the `Host` allowlist is exactly `127.0.0.1:<bound-port>` (string equality, NOT suffix match). This is the load-bearing OWASP DNS-rebinding mitigation (findings 2a, 2c).
- **Pass criterion:** Status `403` and no side-effect, identical to SEC-16 contract.
- **Severity:** `critical` on `200` — DNS rebinding succeeded, attacker's tab now drives the user's local repo. This is the highest-severity browser-driven attack the spec explicitly defends against.
- **CWE:** CWE-918, CWE-350 (Reliance on Reverse DNS Resolution).
- **Components exercised:** FR-9, NFR-7.

## SEC-18 — Single 404 for "outside tree" vs "exists but disallowed"
- **Attack vector:** Run three probes back-to-back: (a) `GET /api/file?path=../etc/passwd` (outside tree, doesn't exist there), (b) `GET /api/file?path=specs/development/no-such-project/spec.md` (inside tree, file doesn't exist), (c) `GET /api/file?path=specs/development/spec_driven/final_specs/_secret_payload.md` (inside tree, file exists on disk via fixture but with a disallowed extension via a separate fixture for the disallowed-case). Diff the response bodies and status lines.
- **Expected behavior:** (a) and (b) both return **404** with byte-identical bodies (or differing only in dynamic fields the spec does not promise — empty body is preferred). (c) returns `415` per FR-3 — that distinction is intentional and is the only one the API discloses.
- **Pass criterion:** `status[a] == status[b] == 404`; `body[a] == body[b]`; no `WWW-Authenticate` / `X-Sandbox-Reason` / response-time delta > 5 ms median across N=20 trials.
- **Severity:** `medium` on a 403/404 split (enumeration side-channel — findings 2c bullet 7); `medium` on body-text divergence ("file not found" vs "outside sandbox") even with matching status.
- **CWE:** CWE-204 (Observable Response Discrepancy), CWE-203 (Observable Discrepancy).
- **Components exercised:** FR-3, FR-4, AC-3.

## SEC-19 — Response-header check on every successful `GET /api/file`
- **Attack vector:** `GET /api/file?path=specs/development/spec_driven/final_specs/spec.md` (200 path). Also exercise `.json`, `.yaml`, `.jsonl`, `.txt`, `.png` to confirm the rule is universal across content types.
- **Expected behavior:** Response carries BOTH `X-Content-Type-Options: nosniff` AND `Content-Disposition: attachment` per FR-5 / NFR-8. Image responses (`.png`, `.jpg`) MUST also carry `attachment` — the spec does not exempt them.
- **Pass criterion:** Both headers present (case-insensitive name match, exact value match) on every 200 response. AC-2 is the spec's anchor.
- **Severity:** `blocker` on missing-header (per prompt rule; this is the load-bearing browser-MIME-sniffing defense).
- **CWE:** CWE-693 (Protection Mechanism Failure), CWE-79 (XSS — the downstream attack the headers prevent).
- **Components exercised:** FR-5, NFR-8, AC-2.

## SEC-20 — `0.0.0.0` bind audit
- **Attack vector:** Static-grep the project source for the literal string `0.0.0.0` in every default-config code path: `projects/spec_driven/main.py`, `projects/spec_driven/Makefile`, `projects/spec_driven/backend/**/*.py`, any `uvicorn.run(...)` call site, any `.env*` template. Also runtime-grep: launch `python main.py` and `make run` / `make run-prod`, capture the Uvicorn startup line, assert it contains `127.0.0.1:8765` and NOT `0.0.0.0`.
- **Expected behavior:** No occurrence in source; runtime startup line names `127.0.0.1` (FR-38, AC-29).
- **Pass criterion:** Static grep returns zero hits; runtime startup line matches `Uvicorn running on http://127.0.0.1:8765`.
- **Severity:** `blocker` on any hit (per prompt rule + AC-29) — a `0.0.0.0` bind exposes the editor to the LAN, breaking the entire localhost-only threat model.
- **CWE:** CWE-1327 (Binding to an Unrestricted IP Address).
- **Components exercised:** FR-38, NFR-7, AC-29.

## SEC-21 — Markdown XSS: raw `<script>` in source
- **Attack vector:** Fixture-write `specs/development/spec_driven/_xss_script.md` containing literal `<script>window.__pwned=1;alert(1)</script>` inline and inside fenced code blocks (the latter must be preserved as text, not rendered as HTML). Open the file via the SPA at `/file/specs/development/spec_driven/_xss_script.md`.
- **Expected behavior:** `react-markdown` + `rehype-sanitize` (default schema, no raw-HTML escape hatch — per NFR-8 / FR-22) drops the `<script>` tag entirely. Inline form: tag stripped, no `<script>` element in the rendered DOM, `window.__pwned` is `undefined` after render, console has no errors. Fenced form: rendered as `<code>` text inside `<pre>`, never as a live element.
- **Pass criterion:** Playwright assertion: `await page.evaluate(() => window.__pwned) === undefined` AND `await page.locator('script:not([src])').count() === 0` (excluding the SPA's own scripts in the head). Console errors empty.
- **Severity:** `critical` on a successful XSS execution; `blocker` on a sanitizer failure that DOES NOT execute but DOES leave the tag in the DOM (rule violated regardless of exploitability).
- **CWE:** CWE-79.
- **Components exercised:** FR-22, NFR-8.

## SEC-22 — Markdown XSS: `<img onerror>` and `<a javascript:>`
- **Attack vector:** Fixture-write `_xss_event.md` containing `<img src=x onerror="window.__pwned=1">`, `<a href="javascript:window.__pwned=1">click</a>`, `<svg onload="window.__pwned=1">` (SVG inline as a sanity-check that `rehype-sanitize` strips the SVG element, not just the file extension), and the markdown form `[click](javascript:window.__pwned=1)`. Open via SPA.
- **Expected behavior:** Sanitizer drops `onerror` / `onload` attributes and rejects `javascript:` URIs. The markdown `[click](javascript:...)` form is rewritten to a broken-link span per FR-24 (`<span class="link-broken" aria-disabled="true" title="...">`), NOT an `<a>` element.
- **Pass criterion:** `window.__pwned === undefined`; no element matches `[onerror], [onload]`; no `<a>` whose `href` starts with `javascript:`; the markdown-`javascript:`-link renders as the broken-link span.
- **Severity:** `critical` on execution; `blocker` on attribute survival without execution.
- **CWE:** CWE-79, CWE-83 (Improper Neutralization of Script in Attributes).
- **Components exercised:** FR-22, FR-24, NFR-8.

## SEC-23 — Read-zero contract surfacing in regen prompts
- **Attack vector:** `POST /api/regen-prompt` with each of: `{stages: ["interview"], autonomous: false}`, `{stages: ["research"], autonomous: true}`, `{stages: ["interview","research","spec","validation"], autonomous: true}` (the full interactive + autonomous matrix across stages). Parse the returned `prompt` body.
- **Expected behavior:** Every returned `prompt` contains a `### Constraints` section, and that section contains the verbatim sentence `regeneration deletes prior outputs first; new generation reads only the inputs.` (FR-11(g), AC-16). Substring match (whitespace-normalized) is acceptable; case-sensitive on the sentence body, lenient on surrounding markdown.
- **Pass criterion:** All N matrix cells contain the sentence verbatim. None drops it under autonomous mode (regression surface).
- **Severity:** `high` on a missing sentence (the read-zero contract is the load-bearing rule that makes regen runs idempotent — silently dropping it makes the assembled prompt drift from intent, which is the failure mode the workflow exists to prevent).
- **CWE:** N/A (workflow-integrity probe, not a classical web vuln).
- **Components exercised:** FR-11(g), AC-16.

---

## Cross-cutting test moves

These are not numbered SEC entries but apply to the whole suite:

- **Run every probe twice — once on Windows, once on POSIX (Git Bash on Windows runs both via WSL or native, per NFR-12). Skip-with-reason is acceptable for SEC-08 (POSIX) and SEC-09 (Windows); silent passing is not.**
- **Every probe asserts no audit-event leakage on rejection paths.** A `403`/`404`/`405`/`413`/`415` response MUST NOT have caused a `regen.delete.planned` / `fs.write.accepted` event in `events.jsonl`. The probe diffs the audit log before and after.
- **Replay every state-changing probe with the documented benign Origin/Host once it has been rejected by SEC-16/SEC-17 — confirm the SAME inputs succeed when the headers are correct.** This is the negative-control that catches an over-broad rejection rule.
- **Snapshot the response-body bytes for every 4xx response and diff across the suite** to detect enumeration side-channels beyond the explicit SEC-18 probe.

## Severity rollup

| Severity | SEC entries that can hit this severity at peak |
|---|---|
| `critical` | SEC-01, SEC-02, SEC-03, SEC-04, SEC-05, SEC-06, SEC-07, SEC-08, SEC-09, SEC-13, SEC-17, SEC-21, SEC-22 |
| `blocker`  | SEC-19, SEC-20, SEC-21 (sanitizer leak without execution), SEC-22 (sanitizer leak without execution) |
| `high`     | SEC-10, SEC-11, SEC-12, SEC-14, SEC-15, SEC-16, SEC-23 |
| `medium`   | SEC-18 (enumeration side-channel) |

A `critical` or `blocker` finding halts the pipeline and emits `pipeline.halted` per `CLAUDE.md` § Iteration bounds.

## Background

Sources cited from `findings/angle-localhost-fs-sandbox-risks.md`:

- Vite path-traversal CVEs (Windows backslash bypass): `https://www.miggo.io/vulnerability-database/cve/CVE-2025-62522` (motivates SEC-03).
- Vite `server.fs.deny` bypass via `/.` prefix: `https://security.snyk.io/vuln/SNYK-JS-VITE-9919777` (motivates SEC-01, SEC-02).
- Vite `/@fs/...?import&raw??` traversal: `https://www.offsec.com/blog/cve-2025-30208/` (motivates SEC-01).
- MkDocs serve directory traversal: `https://github.com/mkdocs/mkdocs/issues/2601` (general traversal-on-localhost prior art).
- DNS-rebinding against MCP localhost servers: `https://rafter.so/blog/mcp-dns-rebinding-localhost` and `https://crypto.stanford.edu/dns/dns-rebinding.pdf` (motivate SEC-16, SEC-17).
- OWASP Path Traversal canonical guidance: `https://owasp.org/www-community/attacks/Path_Traversal` (motivates SEC-01..SEC-09).
- OWASP Windows Alternate Data Stream: `https://owasp.org/www-community/attacks/Windows_alternate_data_stream` (motivates SEC-06).
- Microsoft Win32 reserved-name docs: `https://learn.microsoft.com/en-us/windows/win32/fileio/naming-a-file` (motivates SEC-05).
- OWASP File Upload Cheat Sheet (size caps, headers, content-type spoofing): `https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html` (motivates SEC-10..SEC-14, SEC-19).
- OWASP CSRF Prevention Cheat Sheet: `https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html` (motivates SEC-16, SEC-17).
- FastAPI body-size cap discussion: `https://github.com/fastapi/fastapi/discussions/8167` (motivates SEC-11, SEC-12).
- VS Code extension localhost CVEs: `https://blog.trailofbits.com/2023/02/21/vscode-extension-escape-vulnerability/` (general "localhost is not a boundary" prior art motivating the whole SEC-16/SEC-17/SEC-20 trio).
