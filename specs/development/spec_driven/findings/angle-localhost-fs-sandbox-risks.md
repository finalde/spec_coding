# Angle — localhost-fs-sandbox-risks

Run: `spec_driven-20260503-145859` · Worker: `researcher-03-localhost-fs-sandbox-risks`

## 1. What this angle covers

`spec_driven` exposes a FastAPI backend at `127.0.0.1:8765` with `GET /api/file` and `PUT /api/file` over a path-sandboxed `EXPOSED_TREE`. Even bound to loopback, the surface is reachable by *any* origin a browser can be coerced into — so the sandbox must withstand (a) path-traversal classes (`..`, absolute paths, percent-encoded variants, **Vite CVE-2025-62522** trailing-backslash bypass), (b) Windows reserved device names (`CON`, `PRN`, `NUL`, `COM1`, `LPT1`…), (c) NTFS Alternate Data Streams (`file::$DATA`), (d) NTFS 8.3 short names, (e) POSIX symlinks / Windows junctions, (f) DNS rebinding to localhost, (g) `Origin` / `Host` validation under a Vite reverse proxy, (h) `0.0.0.0` vs `127.0.0.1` exposure, (i) MIME sniffing / `Content-Disposition` defenses, (j) extension allowlist + size cap as defense-in-depth. This angle inventories the established defenses converged on by OWASP / CWE / NIST / vendor guidance and maps them to concrete spec hooks.

## 2. Key findings

### 2a. Path traversal — the primary attack class
- **CWE-22** ("Improper Limitation of a Pathname to a Restricted Directory") is the canonical classification; defenses are: validate against an allowlist of known-good values, never sanitize; minimize user input into FS calls; surround user input with an enforced base path; chrooted-style jail / canonicalize then re-check the prefix; use indexes instead of filenames where possible. (https://cwe.mitre.org/data/definitions/22.html, https://owasp.org/www-community/attacks/Path_Traversal)
- **Variants** to handle even after collapsing `..`: percent-encoded (`%2e%2e%2f`), double-encoded, mixed slashes, null-byte injection, double extensions (`x.jpg.php`). Validate **after** decoding. (https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html)
- **Python canonicalization gotcha:** `pathlib.Path.resolve()` calls `os.path.realpath()` under the hood, but resolve-alone is **not safe against symlink poisoning** — you must resolve and then re-verify the result is a descendant of the base, with `strict=True` if the file must exist. (https://docs.python.org/3/library/pathlib.html, https://github.com/python/cpython/issues/99390)

### 2b. Vite CVE-2025-62522 — the trailing-backslash bypass (load-bearing for this project)
- **CVE-2025-62522** (CWE-22) bypasses Vite's `server.fs.deny` on Windows when the URL ends with a backslash: `fs.readFile('/foo.png/')` resolves to `/foo.png` and `/.env\` reads `.env`. Affects Vite 2.9.18→<3, 3.2.9→<4, 4.5.3→<5, 5.2.6→<5.4.21, 6.0.0→<6.4.1, 7.0.0→<7.0.8, 7.1.0→<7.1.11. Patched 5.4.21 / 6.4.1 / 7.0.8 / 7.1.11. Only triggers when dev server is *exposed to the network on Windows*. (https://advisories.gitlab.com/pkg/npm/vite/CVE-2025-62522/, https://www.cvedetails.com/cve/CVE-2025-62522/, https://security.snyk.io/vuln/SNYK-JS-VITE-13644406)
- **Implication:** the `spec_driven` Python backend must independently reject paths that contain `\`, end in `\` or `/`, contain `..`, contain `%`-encoded variants of those, contain `:` (drive letters / ADS), or fail an `os.path.commonpath`-based base-prefix re-check after `realpath`. The sandbox cannot rely on Vite's filtering.

### 2c. Windows reserved device names
- Reserved (case-insensitive, with **or without** an extension): `CON`, `PRN`, `AUX`, `NUL`, `COM1..COM9`, `COM¹/²/³`, `LPT1..LPT9`, `LPT¹/²/³`. `NUL.txt`, `NUL.tar.gz`, and `NUL` all resolve to the NUL device. (https://learn.microsoft.com/en-us/windows/win32/fileio/naming-a-file, https://www.meziantou.net/reserved-filenames-on-windows-con-prn-aux-nul.htm)
- **Real-world fallout:** `claude-code` issue #16604 documents an agent creating a literal `nul` file on Windows that broke OneDrive/SharePoint sync — proof that even modern tooling regularly forgets to filter these. (https://github.com/anthropics/claude-code/issues/16604)

### 2d. NTFS Alternate Data Streams (ADS)
- A file on NTFS has multiple `$DATA` streams. The OWASP community page documents IIS classic-ASP source disclosure via `filename.asp::$DATA` because extension-parsing didn't strip the stream suffix. As pentesters note, ADS suffixes routinely bypass input validation that "wasn't expecting a filename using the NTFS stream format." (https://owasp.org/www-community/attacks/Windows_alternate_data_stream, https://labs.portcullis.co.uk/blog/ntfs-alternate-data-streams-for-pentesters-part-1/, https://netwrix.com/en/resources/blog/alternate_data_stream/)
- **Defense:** reject any path component containing `:` outright on Windows; do not treat the stream syntax as "just a colon."

### 2e. NTFS 8.3 short names
- Windows generates DOS-compatible 8.3 aliases (`file.shtml` → `FILE~1.SHT`) by default. CoreLabs documented multiple web-server bypasses where the short name evaded filename-extension filters and served unprocessed source. Mitigation is `NtfsDisable8dot3NameCreation = 1`, but the application can't rely on that being set. (https://www.coresecurity.com/core-labs/advisories/filename-pseudonyms-vulnerabilities, https://en.wikipedia.org/wiki/8.3_filename)
- **Defense:** reject any path component matching `~\d` patterns at the validation layer; also reject any extension that doesn't match the allowlist exactly *after* canonicalization.

### 2f. Symlinks / Junctions (CWE-59 "Link Following")
- POSIX symlinks and Windows NTFS junctions (and object-manager / registry symlinks) are the prototypical TOCTOU and sandbox-escape vectors. CWE-59 prescribes resolving the symlink to its actual target and re-checking against the allowed base, plus refusing to operate on dirs an attacker can rename. Microsoft shipped **RedirectionGuard** in Windows 11 (June 2025) specifically because junctions are creatable by standard users and remained the largest junction-traversal gap. (https://cwe.mitre.org/data/definitions/59.html, https://www.microsoft.com/en-us/msrc/blog/2025/06/redirectionguard-mitigating-unsafe-junction-traversal-in-windows)
- **Defense:** stat with `lstat`/`Path.is_symlink()` per component, refuse if any ancestor is a symlink/junction; or `realpath` and re-verify base prefix.

### 2g. DNS rebinding to localhost
- Even a service bound to `127.0.0.1` is reachable from the browser via DNS rebinding: an attacker-controlled domain initially resolves to a public IP (so the page loads under that origin in the browser's eyes), then re-resolves to `127.0.0.1` so subsequent fetches hit the local service. Stanford's foundational paper and Wikipedia describe the mechanism; the converged-on defense is server-side **`Host` header allowlist** containing only `127.0.0.1[:port]` and `localhost[:port]`. The MCP Python SDK's "421 Invalid Host Header" guide is exactly this pattern. (https://en.wikipedia.org/wiki/DNS_rebinding, https://crypto.stanford.edu/dns/dns-rebinding.pdf, https://github.com/modelcontextprotocol/python-sdk/issues/1798)

### 2h. CSRF + Origin/Host validation under Vite proxy (CWE-352)
- For state-changing requests (i.e. `PUT /api/file`, `POST /api/regen-prompt`, `POST/DELETE /api/promote`), OWASP's CSRF cheat sheet endorses validating `Origin` (preferred) with `Host` as a fallback, in addition to (or in lieu of) tokens. The browser sets `Origin` on every non-GET; tokens may not be available in a localhost-only no-auth context. (https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html, https://cwe.mitre.org/data/definitions/352.html)
- **Vite proxy nuance** (already captured in follow-up 006): browsers treat `localhost` and `127.0.0.1` as **distinct origins** for CORS/CSRF purposes — a known FastAPI quirk. The dev-server proxy must rewrite `Origin` to the bound backend origin so the backend's allow-list stays bound-port-only. (https://github.com/fastapi/fastapi/discussions/8744)

### 2i. `0.0.0.0` vs `127.0.0.1` LAN exposure
- Binding to `0.0.0.0` exposes the service on **every** interface (loopback, LAN, public if reachable); `127.0.0.1` is loopback-only and unreachable from any other device, even on the same Wi-Fi. Recommendation across all sources: dev/admin/local-only services bind `127.0.0.1` and only widen explicitly. (https://stenzr.medium.com/understanding-0-0-0-0-vs-127-0-0-1-c6257ae35c62, https://thelinuxcode.com/127001-vs-0000-what-they-mean-when-to-use-each-and-how-to-debug-binding-bugs/, https://discuss.kubernetes.io/t/security-implications-of-binding-server-to-127-0-0-1-vs-0-0-0-0-vs-pod-ip/13880)

### 2j. MIME sniffing / Content-Disposition / nosniff (defense-in-depth on read)
- OWASP File Upload Cheat Sheet: "When files are downloaded, use `X-Content-Type-Options: nosniff` and `Content-Disposition` headers to force safe handling." MDN concurs: `nosniff` makes browsers trust the declared `Content-Type`; without it, browsers may sniff a `text/plain` payload and execute it as JS/HTML. (https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html, https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Disposition)
- **Caveat:** `Content-Disposition: attachment` is bypassable on its own under specific browser quirks (markitzeroday's "defeating Content-Disposition"), so it must be paired with `nosniff` and an extension allowlist. (https://markitzeroday.com/xss/bypass/2018/04/17/defeating-content-disposition.html)

### 2k. Extension allowlist + size cap (defense-in-depth on write)
- OWASP File Upload Cheat Sheet converged-on practice: allowlist the *small* set of business-critical extensions; reject everything else; cap file size to protect storage and prevent DoS; never trust the client `Content-Type`; account for decompressed size on archives. The current QA already binds `.md/.json/.yaml/.yml/.jsonl/.txt` and a 1 MB cap for both GET and PUT — that matches OWASP. (https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html, https://owasp.org/www-community/vulnerabilities/Unrestricted_File_Upload)

## 3. Implications for the spec (concrete)

These should appear (or remain) as named requirements / security checks in stage 4's `final_specs/spec.md` and stage 5's `validation/security.md`:

- **FR-3 / SEC-PathSandbox** — a single `resolve_safe(path)` helper used by every read & write endpoint that: (i) URL-decodes once, (ii) rejects literal `\`, `:`, NUL byte, leading `/` or `\`, percent-encoded variants, `..` segments, trailing `/` or `\` (Vite CVE-2025-62522 class); (iii) rejects path components matching the Windows reserved-device regex `^(CON|PRN|AUX|NUL|COM[0-9¹²³]|LPT[0-9¹²³])(\.|$)` case-insensitively; (iv) rejects 8.3-short-name `~\d` segments; (v) `realpath`s and verifies `os.path.commonpath([resolved, EXPOSED_ROOT]) == EXPOSED_ROOT`; (vi) refuses if any ancestor is a symlink/junction (`Path.is_symlink()` per component). Every probe collapses to a single 404 — no enumeration side-channel (already in QA round 1).
- **NFR-9 / SEC-ExtensionAllowlist** — exact-match allowlist `.md/.json/.yaml/.yml/.jsonl/.txt`; `.png/.jpg` get a placeholder render and a 200 with image MIME but **never** an executable MIME; everything else 415.
- **NFR-Size / SEC-SizeCap** — 1 MB cap on both `GET /api/file` and `PUT /api/file`; oversized → `413 {"kind": "too_large"}`.
- **SEC-CSRF-Origin** — bound port allowlist for `Origin` and `Host`: `{http://127.0.0.1:8765, http://localhost:8765}`; mismatch → 403. Same gate covers DNS-rebinding (`Host`) and CSRF (`Origin`). Under `make run-frontend`, the Vite proxy rewrites both headers to the bound origin (per FR-9 dev-server proxy contract); the backend allow-list is **not** widened to 5173.
- **SEC-Bind127** — uvicorn binds `127.0.0.1`, never `0.0.0.0`, in every Makefile target; covered by a startup assertion + e2e probe that an external interface refuses connection.
- **SEC-DownloadHeaders** — every `GET /api/file` response carries `X-Content-Type-Options: nosniff`. For non-rendered file types (binary placeholder), also `Content-Disposition: attachment; filename="..."` with an ASCII-safe filename.
- **SEC-NoSymlinkFollow** — write path additionally refuses to *create* a file whose parent is a symlink/junction.
- **AC-1 / AC-11 / SYS-16b** — already binding the sandbox + dev-server proxy contract; unit tests should table-drive the probe corpus (`../`, `..\`, `%2e%2e%2f`, `\..\\`, `CON.md`, `nul`, `file.md::$DATA`, `FILE~1.MD`, `/etc/passwd`, `C:\Windows\System32\drivers\etc\hosts`, trailing `\`, trailing `/`) and assert all collapse to a single 404.

## 4. Open questions surfaced

- **Symlink-handling policy on read.** Refuse outright (reject any sandbox member that *is* or *contains* a symlink ancestor), or `realpath` + re-verify base prefix? The latter is more permissive (lets a curated symlink stay inside the tree); the former is simpler. **Tentative recommendation: refuse outright** — `EXPOSED_TREE` is curated, no legitimate use case for symlinks.
- **8.3 short-name detection robustness.** Pure-regex `~\d` rejection is a heuristic — a legitimate file literally named `foo~1.md` would be rejected. Acceptable for `EXPOSED_TREE` (no such files exist) but should be documented.
- **Image placeholder MIME.** Spec says `.png/.jpg` render as a placeholder — does the backend serve them as `image/png` (with `nosniff` blocking script-sniffing) or as `application/octet-stream`? Established practice favors `application/octet-stream` + `Content-Disposition: attachment` for any non-rendered surface, but this contradicts "render as placeholder." Likely resolved by the frontend rendering a placeholder UI without ever fetching the bytes.
- **Should the sandbox refuse paths longer than `MAX_PATH` (260) on Windows even when long-path support is enabled?** Long paths can confuse legacy tools downstream (e.g. OneDrive sync, the same class of failure as `nul`). Defensive cap at ~240 chars seems prudent.
- **`Referer` fallback when `Origin` is absent.** Some old Chrome/Firefox builds omit `Origin` on same-origin same-method requests in unusual configurations; OWASP's CSRF cheat sheet allows `Referer` as a documented fallback. Worth deciding for the spec rather than discovering at runtime.
