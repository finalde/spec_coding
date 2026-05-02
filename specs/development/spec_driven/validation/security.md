# Validation — Security Checks (Level 06)

Run: spec_driven-20260502-141813
Stage: 5 (Validation strategy)
Level: security
Spec refs: FR-4, FR-5, FR-6, FR-33, FR-37, NFR-4, NFR-5, NFR-6, NFR-7, NFR-8, NFR-13, NFR-15, plus `## Out of scope (v1)`.

---

## Threat model summary

**Assumed attacker.** The threat model assumes a *local* attacker only, in two flavors:

1. **Malicious file content authored by upstream Claude** (or another local process that writes into `EXPOSED_TREE`). Claude Code is non-deterministic and could, accidentally or under prompt injection, drop a file containing a `javascript:` link, a path-traversal markdown link, a binary blob inside a `.md`, a 2 GB JSON, or a symlink. The viewer must not be a vector that turns those file-system-level surprises into something worse (XSS, SSRF, sandbox escape, OOM, 500-with-stack-trace).
2. **Another local-user process** that crafts URLs and POSTs them at `127.0.0.1:8765` (e.g., a browser tab loading a malicious page that fires `fetch('http://127.0.0.1:8765/api/file?path=../../../etc/passwd')`).

**Out of scope (per NFR-7).** A *remote network* attacker is explicitly out of scope. The mitigation is the bind address (`127.0.0.1`, never `0.0.0.0`) and the documented "localhost-only is the security model" line in the README — not authentication, not TLS, not CSRF tokens. Probes that require a remote attacker are intentionally absent below.

**In-scope threat surface:**
- Path escape via `..`, absolute paths, UNC paths, null-bytes, alternate data streams, short names, symlinks, case-folding tricks.
- Resource exhaustion via oversized files or dense directories.
- Information disclosure via error messages (stack traces, internal paths, Python class names).
- Markdown content as an XSS / SSRF vector against the local browser.
- Verb confusion (write methods accidentally exposed).
- CORS misconfiguration that would let any local web page read repo content.

**Out-of-scope threats (call out so reviewers don't waste time):**
- Remote-network attackers: relies on bind-address (NFR-7).
- Auth bypass: there is no auth surface (NFR-7).
- TLS downgrade: HTTP-only by design.
- Multi-tenant isolation: single-user.

---

## Format

Each check below is structured:

- **ID** — stable identifier `SEC-NN`.
- **Threat** — concrete attacker goal in one sentence.
- **Vector** — request shape, file shape, or environment manipulation.
- **Probe inputs** — exact strings/payloads.
- **Expected behavior** — exact response (HTTP status, JSON error key, log line shape).
- **Pass criterion** — what must be true for the check to pass.
- **Spec refs** — FR/NFR identifiers.
- **Fixture** — inline description of any required fixture file.
- **Platform** — `all`, `windows-only`, `unix-only`.

All probes assume the backend is running on `http://127.0.0.1:8765` (the FR-12 default port).

---

## SEC-01 — Path traversal via `..`

- **Threat.** Caller reads any file outside `EXPOSED_TREE` by walking up the directory tree with `..` segments.
- **Vector.** `GET /api/file?path=<traversal>`. Includes raw, single-encoded, double-encoded, mixed-slash variants.
- **Probe inputs.**
  - `path=../../../etc/passwd`
  - `path=..%2F..%2F..%2Fetc%2Fpasswd`
  - `path=..%252F..%252F..%252Fetc%252Fpasswd` (double-encoded `%2F`)
  - `path=..\..\..\Windows\system32\drivers\etc\hosts` (Windows backslashes)
  - `path=..%5C..%5C..%5CWindows%5Csystem32%5Cdrivers%5Cetc%5Chosts` (encoded `\`)
  - `path=specs/../../../etc/passwd` (dot-segments after a legitimate prefix)
  - `path=specs/development/spec_driven/final_specs/../../../../../etc/passwd`
- **Curl form.**

  ```
  curl -i 'http://127.0.0.1:8765/api/file?path=../../../etc/passwd'
  curl -i --data-urlencode 'path=../../../etc/passwd' -G 'http://127.0.0.1:8765/api/file'
  ```

- **Expected behavior.** Each call returns `400 Bad Request` with JSON body `{"error":"outside_sandbox", ...}`. No file content. No stack trace. No Python class name. Server log records the rejection at INFO or WARN, not ERROR-with-traceback.
- **Pass criterion.** All 7 probes return 400 with `error == "outside_sandbox"`. No probe returns 200 or any partial file content. Server log contains no `Traceback (most recent call last)` line for any of the 7.
- **Spec refs.** FR-5.1, FR-6, NFR-4, AC-7.
- **Fixture.** None required.
- **Platform.** all (Windows-flavored backslash probes also run on Unix; they should still 400, not 404).

---

## SEC-02 — Path traversal via absolute paths

- **Threat.** Caller bypasses sandbox by passing an already-absolute path. `Path("/foo") / "abs"` resolves to `"abs"` on POSIX or anchors to the drive on Windows; either way, `safe_resolve`'s `relative_to(REPO_ROOT)` must reject.
- **Vector.** Absolute POSIX, absolute Windows, UNC.
- **Probe inputs.**
  - `path=/etc/passwd`
  - `path=/etc/shadow`
  - `path=C:\Windows\system32\drivers\etc\hosts`
  - `path=C:/Windows/system32/drivers/etc/hosts`
  - `path=\\server\share\file.txt` (UNC; literal)
  - `path=//server/share/file.txt` (UNC with forward slashes)
  - `path=%5C%5Cserver%5Cshare%5Cfile.txt` (URL-encoded UNC)
  - `path=file:///etc/passwd` (file URI; should fall through extension check or sandbox check)
- **Curl form.**

  ```
  curl -i --data-urlencode 'path=/etc/passwd' -G 'http://127.0.0.1:8765/api/file'
  curl -i --data-urlencode 'path=C:\Windows\system32\drivers\etc\hosts' -G 'http://127.0.0.1:8765/api/file'
  curl -i --data-urlencode 'path=\\server\share\file.txt' -G 'http://127.0.0.1:8765/api/file'
  ```

- **Expected behavior.** Each returns `400 Bad Request`, `error == "outside_sandbox"`. Never 200. Never any 5xx. Never an SMB connection attempt to `\\server\share` (verify with `tcpdump`/Wireshark or by pointing UNC at a non-routable host and confirming no DNS/SMB packets leave the box).
- **Pass criterion.** All 8 probes 400 with `outside_sandbox`. On Windows, no SMB connection initiated for the UNC variants (a stray `Path.resolve()` on UNC must not trigger network IO before sandbox rejection). On Unix, `\\server\share\file.txt` is interpreted as a relative path with literal backslashes; still 400 (either `outside_sandbox` after resolve, or `unsupported_extension` — both acceptable, but never 200, never 5xx).
- **Spec refs.** FR-5.1, FR-6, NFR-4.
- **Fixture.** None.
- **Platform.** all (UNC probes are Windows-significant; on Unix the call must still be safe).

---

## SEC-03 — Path traversal via null injection

- **Threat.** Caller smuggles a traversal past an extension check by terminating the visible portion with a null byte; some C-level filesystem APIs treat `\x00` as string terminator while Python sees the rest.
- **Vector.** `path` query containing literal or URL-encoded `\x00`.
- **Probe inputs.**
  - `path=spec.md` followed by literal `\x00` then `../../../etc/passwd` (test client must allow raw NUL — use `curl --data-urlencode` with a Python-built payload, or `requests.get(params={...})` after the param value is mutated to embed NUL).
  - `path=spec.md%00../../../etc/passwd`
  - `path=specs/development/spec_driven/final_specs/spec.md%00../../../etc/passwd`
  - `path=foo.md%00.exe` (extension confusion)
- **Curl form.**

  ```
  python - <<'PY'
  import urllib.parse, urllib.request
  p = "spec.md\x00../../../etc/passwd"
  qs = urllib.parse.urlencode({"path": p})
  print(urllib.request.urlopen(f"http://127.0.0.1:8765/api/file?{qs}").read())
  PY
  ```

- **Expected behavior.** FastAPI / Starlette parses the query string and passes the value to the handler. The handler MUST reject any `path` containing `\x00` (either explicit check or because `Path.resolve()` raises `ValueError` on NUL on most platforms). Acceptable responses: `400 outside_sandbox`, `400 invalid_path`, or `404 not_found` after `safe_resolve` raises. Never 200. Never 500. Never partial content from `etc/passwd`.
- **Pass criterion.** All 4 probes return 4xx (preferably 400). No probe returns content from outside `EXPOSED_TREE`. No probe yields a 500 with a `ValueError: embedded null byte` traceback in the response body.
- **Spec refs.** FR-5.1, FR-5.7, FR-6, NFR-4.
- **Fixture.** None.
- **Platform.** all.

---

## SEC-04 — `safe_resolve` bypass via OS-specific path quirks

- **Threat.** Path looks inside `EXPOSED_TREE` to a string-comparison check, but resolves outside thanks to OS-specific path interpretation: Windows case-insensitive matching, NTFS Alternate Data Streams (`file.md::$DATA`), 8.3 short names (`PROGRA~1`), trailing dots/spaces (`spec.md.` on Windows is `spec.md`).
- **Vector.** Windows-significant edge cases routed through `Path.resolve()` then back to the four `EXPOSED_TREE` source globs.
- **Probe inputs.** (Windows host)
  - `path=specs/development/spec_driven/final_specs/spec.md::$DATA` — NTFS ADS pointer to the same file's default stream.
  - `path=specs/development/spec_driven/final_specs/spec.md:hidden` — named ADS that may or may not exist; if exists, must be rejected (extension is now `.md:hidden`).
  - `path=SPECS/DEVELOPMENT/SPEC_DRIVEN/FINAL_SPECS/SPEC.MD` — case-folded path; on case-insensitive Windows NTFS this resolves to the real file. The spec is silent on case sensitivity. Accept either behavior but it MUST be deterministic and MUST NOT escape the sandbox.
  - `path=PROGRA~1\file.md` — 8.3 short name. Should never resolve inside `EXPOSED_TREE`; should 400 or 404.
  - `path=specs/development/spec_driven/final_specs/spec.md.` (trailing dot) — Windows strips it, file resolves; non-Windows treats literally and 404s.
  - `path=specs/development/spec_driven/final_specs/spec.md ` (trailing space) — same as above.
- **Curl form.**

  ```
  curl -i --data-urlencode 'path=specs/development/spec_driven/final_specs/spec.md::$DATA' -G 'http://127.0.0.1:8765/api/file'
  curl -i --data-urlencode 'path=PROGRA~1\file.md' -G 'http://127.0.0.1:8765/api/file'
  ```

- **Expected behavior.** Probes that introduce stream syntax or short names return 400 (`outside_sandbox` if `safe_resolve` rejects the resolved-but-aliased path, or `unsupported_extension` if the extension check trips). Probes that exploit case-folding either consistently 200 (treating Windows as case-insensitive) or consistently 404 — but they never escape the sandbox or resolve to a *different* file than the lower-case exact match.
- **Pass criterion.** No probe returns content from a file outside the four `EXPOSED_TREE` source globs. No probe returns 500. ADS and short-name probes return 4xx. Case-folding behavior is documented in the README or test output (e.g., "Windows: case-insensitive lookup is accepted"); it does not vary between consecutive identical requests.
- **Spec refs.** FR-5, FR-6, NFR-4.
- **Fixture.** None (assumes the spec file exists).
- **Platform.** windows-significant; `::$DATA` and short-name probes also run on Unix and must 4xx there too.

---

## SEC-05 — Symlink follow attempts

- **Threat.** Caller plants a symlink inside `EXPOSED_TREE` whose target is outside (e.g., `/etc/passwd`), then requests the symlink path; if the backend follows symlinks, it leaks arbitrary file content. Even if the target is *inside* `EXPOSED_TREE`, the policy is hard-no per FR-4 / NFR-5.
- **Vector.** Three sub-cases: out-of-tree symlink, in-tree symlink, directory symlink.
- **Probe inputs.**
  - SEC-05a (file symlink, target outside).
    - Fixture (Unix): `ln -s /etc/passwd specs/development/spec_driven/final_specs/spec_link.md`
    - Fixture (Windows admin/dev-mode): `mklink specs\development\spec_driven\final_specs\spec_link.md C:\Windows\system32\drivers\etc\hosts`
    - Probe: `curl -i 'http://127.0.0.1:8765/api/file?path=specs/development/spec_driven/final_specs/spec_link.md'`
  - SEC-05b (file symlink, target inside).
    - Fixture: `ln -s spec.md specs/development/spec_driven/final_specs/spec_alias.md`
    - Probe: `curl -i 'http://127.0.0.1:8765/api/file?path=specs/development/spec_driven/final_specs/spec_alias.md'`
  - SEC-05c (directory symlink).
    - Fixture: `ln -s /tmp specs/development/spec_driven/final_specs/tmp_link`
    - Probe: `curl -i 'http://127.0.0.1:8765/api/tree'` (verify the symlink dir is silently absent)
    - Secondary probe: `curl -i 'http://127.0.0.1:8765/api/file?path=specs/development/spec_driven/final_specs/tmp_link/anyfile.md'`
- **Expected behavior.**
  - 05a: 400 `outside_sandbox` (the resolved real path escapes `REPO_ROOT`). Acceptable alternative: 400 with a dedicated `is_symlink` error key, since the FR-5.2 check fires first. Never 200.
  - 05b: 400 from the FR-5.2 `is_symlink()` check. Even though the target is legitimate, the symlink itself is not a normal file. Never 200.
  - 05c: `/api/tree` does NOT include the symlink directory among its entries (FR-4). The secondary probe returns 400 (the parent on the path is a symlink and `safe_resolve`'s `is_symlink()` check on the resolved path or any ancestor fires) or 404. Never 200.
- **Pass criterion.** All three sub-cases reject. Tree-walk silently skips symlink entries (no `present:true` leaf for them). Server logs do not contain a stack trace for any sub-case.
- **Spec refs.** FR-4, FR-5.2, NFR-5, OQ-4.
- **Fixture.** Three symlinks created before the test; tear down after.
- **Platform.** unix-primary; windows-only with developer mode enabled or admin shell for `mklink`.

---

## SEC-06 — Extension whitelist bypass

- **Threat.** Caller reads a file with a non-allowed extension (e.g., `.env`, `.exe`, `.py`).
- **Vector.** `path` query whose suffix is outside `{.md, .yaml, .yml, .json, .jsonl}`.
- **Probe inputs.**
  - `path=secrets.env` (env files are common in repo roots; here `secrets.env` does not exist but the extension check fires first → 415).
  - `path=foo.md.exe` (effective suffix is `.exe`; expect 415).
  - `path=foo.MD` (uppercase variant; spec is silent — flag).
  - `path=foo.json5` (JSON5 is not in the whitelist; expect 415).
  - `path=foo.yml.bak` (suffix `.bak`; expect 415).
  - `path=specs/development/spec_driven/final_specs/spec` (no extension; expect 415).
  - `path=specs/development/spec_driven/final_specs/spec.md/` (trailing slash; expect 400 or 404 depending on resolve, never 200).
- **Curl form.**

  ```
  curl -i --data-urlencode 'path=secrets.env' -G 'http://127.0.0.1:8765/api/file'
  curl -i --data-urlencode 'path=foo.md.exe' -G 'http://127.0.0.1:8765/api/file'
  curl -i --data-urlencode 'path=foo.MD' -G 'http://127.0.0.1:8765/api/file'
  ```

- **Expected behavior.** All probes except `foo.MD` return 415 `unsupported_extension`. The `foo.MD` case: the spec at FR-5.4 enumerates lowercase suffixes; record the implementation's choice (case-sensitive 415 *or* case-insensitive 200/404). Both are acceptable for v1 but must be deterministic; emit a documentation entry if the implementation accepts uppercase.
- **Pass criterion.** 6 of the 7 probes return 415. The 7th (`foo.MD`) is consistent across two consecutive runs and the README or `validation/notes.md` has a one-line note recording the chosen behavior.
- **Spec refs.** FR-5.4, AC-8.
- **Fixture.** None (none of the probe paths need to exist; extension check fires before existence).
- **Platform.** all.

---

## SEC-07 — Binary content masquerading as text

- **Threat.** A `.md` or `.json` file with embedded `\x00` bytes is served as text, leaking binary content or mis-rendering arbitrary blobs in the markdown pane.
- **Vector.** Allowed extension + binary payload.
- **Probe inputs.**
  - SEC-07a: a file at `specs/development/spec_driven/final_specs/binary_test.md` whose first 100 bytes contain `\x00` somewhere.
  - SEC-07b: a file at `specs/development/spec_driven/final_specs/binary_test.json` containing `{"k": "\x00"}` raw (literal NUL inside the string).
  - SEC-07c: a `.md` file whose bytes are valid UTF-8 except for one stray `\xC0\x80` (overlong NUL); after `errors="replace"` the result must still contain `\x00` if the implementation pre-replaces, or the replacement char `�` if it post-decodes. Verify FR-5.6's behavior is "after decode, scan for `\x00`".
- **Curl form.**

  ```
  printf 'Hello\x00World\n' > specs/development/spec_driven/final_specs/binary_test.md
  curl -i 'http://127.0.0.1:8765/api/file?path=specs/development/spec_driven/final_specs/binary_test.md'
  ```

- **Expected behavior.** SEC-07a and SEC-07b return 415 `binary_content`. SEC-07c: per FR-5.6 the read uses `errors="replace"`; an overlong-NUL is decoded as `�` (not `\x00`), so it does NOT trip `binary_content`. The 415 trigger must check the decoded string, not raw bytes — verify by reading the implementation.
- **Pass criterion.** SEC-07a and 07b: 415 with `error == "binary_content"`. SEC-07c: 200 OK with the file body, where any non-decodable bytes appear as `�`. No probe returns 200 with raw NUL bytes in the response body. No probe returns 500.
- **Spec refs.** FR-5.6, NFR-13, AC-9.
- **Fixture.** Three small files written into `final_specs/` before tests; remove after.
- **Platform.** all.

---

## SEC-08 — Size DoS

- **Threat.** Caller exhausts memory by requesting a multi-gigabyte file the backend reads into memory before checking the size.
- **Vector.** A large file at an allowed extension under `EXPOSED_TREE`.
- **Probe inputs.**
  - SEC-08a: file of exactly 2 MB (2 * 1024 * 1024 bytes) of valid UTF-8 ASCII.
  - SEC-08b: file of 2 MB + 1 byte.
  - SEC-08c: file of 2 GB created sparse (`truncate -s 2G specs/development/spec_driven/final_specs/big.md` on Unix, `fsutil file createnew big.md 2147483649` on Windows).
- **Curl form.**

  ```
  truncate -s 2097152 specs/development/spec_driven/final_specs/exact.md
  curl -i 'http://127.0.0.1:8765/api/file?path=specs/development/spec_driven/final_specs/exact.md'

  truncate -s 2097153 specs/development/spec_driven/final_specs/over.md
  curl -i 'http://127.0.0.1:8765/api/file?path=specs/development/spec_driven/final_specs/over.md'

  truncate -s 2147483649 specs/development/spec_driven/final_specs/huge.md
  /usr/bin/time -v curl -s 'http://127.0.0.1:8765/api/file?path=specs/development/spec_driven/final_specs/huge.md' >/dev/null
  ```

- **Expected behavior.**
  - 08a: 200 OK (boundary is *strictly greater than 2 MB* per FR-5.5). If the spec interprets "exceeds" as `>=`, 413 is also acceptable; document the chosen interpretation.
  - 08b: 413 `too_large`.
  - 08c: 413 `too_large`. **Critical:** the backend must `os.stat()` the file before reading content. Verify by checking server RSS during the request — must stay flat (not jump by 2 GB). Verify by reading source: `Path.stat().st_size > 2_097_152` check appears before any `read_text()` call.
- **Pass criterion.** 08a returns 200 with full body; 08b returns 413; 08c returns 413 within ≤200 ms with backend RSS delta < 50 MB. No probe yields a 5xx or an OOM kill of the process.
- **Spec refs.** FR-5.5, NFR-15, AC-10.
- **Fixture.** Three files; tear down (especially the 2 GB sparse file) after.
- **Platform.** all.

---

## SEC-09 — Tree-walk DoS

- **Threat.** Caller pre-stages a directory under `specs/{type}/{name}/{stage}/` containing tens of thousands of files; `/api/tree` walks all of them per request (FR-3) and either times out or starves the event loop.
- **Vector.** Densely populated stage subfolder.
- **Probe inputs.**
  - Fixture: 10000 empty files at `specs/development/dos_test/findings/file_00000.md` … `file_09999.md`.
  - Probe: `/usr/bin/time -v curl -s 'http://127.0.0.1:8765/api/tree' > /tmp/tree.json`
  - Repeat 5x to capture variance.
- **Expected behavior.** The endpoint completes (does not hang the server) within a documented bound. Per NFR-15 the locked scale is ≤200 files per project; 10000 is *beyond* spec. Acceptable outcomes per spec:
  - The walk completes (slowly is OK, e.g., 5–30 s) and the response is well-formed JSON. The README or this doc records "tree-walk performance is undefined beyond NFR-15 ceilings".
  - OR the walk returns a graceful 503 `tree_too_large` if a guard rail was implemented (not required by spec).
  - The walk does NOT 500. The walk does NOT hang the server such that subsequent unrelated requests stall.
- **Pass criterion.** During and after the probe, a parallel `curl http://127.0.0.1:8765/api/tree?` against an in-spec project still returns within 1 second (i.e., the dense walk does not block the FastAPI worker indefinitely; if it does, document explicitly as accepted-undefined-behavior). No 500. Memory delta < 200 MB during the walk.
- **Spec refs.** FR-3, NFR-15.
- **Fixture.** A `dos_test` task name with 10000 files in `findings/`; clean up after.
- **Platform.** all.

---

## SEC-10 — GET-only API surface

- **Threat.** Caller mutates filesystem state via a write verb (POST/PUT/PATCH/DELETE) that the backend exposes by accident.
- **Vector.** Probe each non-GET verb on the two real endpoints and one wildcard path.
- **Probe inputs.**
  - `POST /api/file?path=spec.md` body `{"content":"x"}`
  - `POST /api/tree`
  - `PUT /api/file?path=spec.md`
  - `PATCH /api/file?path=spec.md`
  - `DELETE /api/file?path=spec.md`
  - `OPTIONS /api/file` (acceptable: 200/204 with `Allow: GET` header; or 405)
  - `HEAD /api/file?path=spec.md` (FastAPI's default may add HEAD for GET routes; acceptable: 200 with empty body, or 405)
  - `GET /api/upload` (sanity: confirm no upload-shaped endpoint exists → 404)
  - `POST /api/anything` (404)
- **Curl form.**

  ```
  for V in POST PUT PATCH DELETE; do
    curl -i -X "$V" 'http://127.0.0.1:8765/api/file?path=specs/development/spec_driven/final_specs/spec.md'
  done
  curl -i -X OPTIONS 'http://127.0.0.1:8765/api/file'
  curl -i -X HEAD 'http://127.0.0.1:8765/api/file?path=specs/development/spec_driven/final_specs/spec.md'
  ```

- **Expected behavior (revised by follow-up 001).**
  - `PUT /api/file` is now a sanctioned mutation endpoint and accepts `{path, text}` JSON bodies. With a valid sandboxed path it returns 200 and writes (atomic temp+rename). The probe should validate the file is restored after the test or use a scratch file.
  - `POST /api/regen-prompt` is a sanctioned read-only endpoint and returns 200 with the assembled prompt body.
  - `POST /api/file`, `PATCH /api/file`, `DELETE /api/file`, `POST /api/tree`, `POST /api/upload`: 405 `Method Not Allowed` (no upload, no delete, no patch in v1).
  - OPTIONS: 200/204 with an `Allow` header listing only the methods registered for the path.
  - HEAD: either 200 with empty body and same headers as GET, or 405. Both acceptable.
  - Phantom endpoints: 404.
- **Pass criterion.** Only `GET`, `PUT`, and `POST` verbs return success codes, and only on the three known routes (`/api/tree`, `/api/file`, `/api/regen-prompt`). `DELETE`, `PATCH`, and uploads must 405. After the probe set, the repo's pre-probe `git status` matches the post-probe `git status` (the PUT probe operates on a scratch fixture file or restores the original).
- **Spec refs.** NFR-6, FR-14a, FR-14c.
- **Fixture.** None.
- **Platform.** all.

---

## SEC-11 — Bind address (loopback only)

- **Threat.** Backend bound to `0.0.0.0` exposes the file-read API to anything that can route to the host (LAN, VPN peers, container network).
- **Vector.** Verify the listening socket is bound to loopback. Verify a connection from a non-loopback interface is refused.
- **Probe inputs.**
  - On Unix: `ss -tlnp | grep 8765` should show `127.0.0.1:8765`, NOT `0.0.0.0:8765` and NOT `*:8765`.
  - On Windows: `netstat -an | findstr 8765` should show `127.0.0.1:8765`, NOT `0.0.0.0:8765`.
  - Connection probe from a non-loopback: from the same host, find a non-127 IP (`hostname -I` first non-127 entry, or `ipconfig` LAN address) and run `curl -i --connect-timeout 2 http://<lan-ip>:8765/api/tree`. Must `Connection refused` or time out.
  - Read the source: `grep -rn "host=" projects/spec_driven/backend/main.py` (and `libs/`) — must show `"127.0.0.1"`, never `"0.0.0.0"`, never absent (Uvicorn's default is `127.0.0.1` so omission is OK, but explicit is preferred).
- **Curl form.**

  ```
  ss -tlnp | grep 8765
  curl -i --connect-timeout 2 'http://192.168.1.50:8765/api/tree' || echo 'refused (expected)'
  grep -rn 'host\s*=' projects/spec_driven/backend
  ```

- **Expected behavior.** Listening socket is `127.0.0.1:8765` only. Connection from any non-loopback IP refused or times out. Source either explicitly sets `host="127.0.0.1"` or relies on the Uvicorn default (also `127.0.0.1`).
- **Pass criterion.** `ss`/`netstat` output shows only loopback. Cross-interface curl returns "Connection refused" or times out; never 200 or 4xx (a 4xx response would mean the listener accepted the connection from a non-loopback peer — fail). No grep hit for `0.0.0.0` in backend source.
- **Spec refs.** NFR-7, FR-12.
- **Fixture.** None.
- **Platform.** all.

---

## SEC-12 — No CORS wildcard

- **Threat.** A misconfigured `allow_origins=["*"]` would let any web page in any local browser tab read the entire `EXPOSED_TREE` via cross-origin `fetch`.
- **Vector.** Inspect response headers on every API path; inspect source for `CORSMiddleware` registration.
- **Probe inputs.**
  - `curl -i 'http://127.0.0.1:8765/api/tree'`
  - `curl -i -H 'Origin: http://evil.example' 'http://127.0.0.1:8765/api/tree'`
  - `curl -i -H 'Origin: http://evil.example' 'http://127.0.0.1:8765/api/file?path=specs/development/spec_driven/final_specs/spec.md'`
  - `curl -i -X OPTIONS -H 'Origin: http://evil.example' -H 'Access-Control-Request-Method: GET' 'http://127.0.0.1:8765/api/tree'`
  - Source grep: `grep -rn 'CORSMiddleware\|allow_origins\|allow_origin_regex' projects/spec_driven/backend`
- **Expected behavior.** Response headers contain NO `Access-Control-Allow-Origin` header at all (preferred). If present (because some middleware or a reverse proxy injects one), it is a literal allow-list of `http://localhost:8765` / `http://127.0.0.1:8765` only — never `*`, never the request's `Origin` echoed back. Source grep: no `CORSMiddleware` registration with `allow_origins=["*"]`.
- **Pass criterion.** Zero responses contain `Access-Control-Allow-Origin: *`. Source contains no `allow_origins=["*"]` literal. The OPTIONS preflight returns 405 (no CORS) or returns headers without `Access-Control-Allow-Origin: *`.
- **Spec refs.** NFR-8.
- **Fixture.** None.
- **Platform.** all.

---

## SEC-13 — No auth bypass risks (because no auth exists)

- **Threat.** Reviewer reading the code might assume there is auth and look for bypass; the *correct* answer is "no auth, by design, documented".
- **Vector.** Code inspection + README inspection.
- **Probe inputs.**
  - `grep -rni 'auth\|login\|session\|cookie\|token\|jwt\|bearer\|csrf\|password' projects/spec_driven/backend` → expect zero meaningful hits (matches in vendored libs are out of scope).
  - `grep -ni 'localhost-only\|localhost only\|127.0.0.1' projects/spec_driven/README.md` → expect a sentence stating "localhost-only is the security model" or equivalent (NFR-7's exact wording).
- **Curl form.**

  ```
  grep -rni 'authenticate\|login\|session\|jwt\|bearer\|csrf\|api[_-]key' projects/spec_driven/backend
  grep -ni 'localhost' projects/spec_driven/README.md
  ```

- **Expected behavior.** Backend source contains no auth code paths. README contains a sentence documenting the localhost-only security model.
- **Pass criterion.** Zero auth-related code identifiers in backend source. README contains an explicit "localhost-only" or "no authentication; localhost-only deployment" line.
- **Spec refs.** NFR-7, FR-14.
- **Fixture.** None.
- **Platform.** all.

---

## SEC-14 — Frontend XSS via markdown link with `javascript:` scheme

- **Threat.** A markdown file authored by upstream Claude contains `[click me](javascript:alert(document.cookie))`; if the renderer emits this as `<a href="javascript:alert(...)">`, clicking it executes script in the app's origin and reads any same-origin state.
- **Vector.** Markdown content rendered through the parser pipeline (FR-30, FR-31, FR-33).
- **Probe inputs.**
  - Fixture: a file at `specs/development/spec_driven/final_specs/xss_test.md` containing literal:

    ```
    # XSS test

    [xss-1](javascript:alert(1))
    [xss-2](JaVaScRiPt:alert(2))
    [xss-3](data:text/html,<script>alert(3)</script>)
    [xss-4](vbscript:msgbox(4))
    [xss-5](file:///etc/passwd)
    [normal](https://example.com)
    [internal](../findings/dossier.md)
    ```

  - Render this file and inspect the produced DOM for the `<a>` tags emitted.
- **Curl form.** Browser-driven; use Playwright or DevTools.

  ```js
  // In DevTools after navigating to /projects/development/spec_driven/final_specs/xss_test.md:
  Array.from(document.querySelectorAll('a, span.link-broken')).map(el => ({
    tag: el.tagName, href: el.getAttribute('href'), text: el.textContent
  }))
  ```

- **Expected behavior.**
  - Per FR-33 case 1, any `href` matching `^[a-z][a-z0-9+.-]*:` is classified **external**. Rendered as `<a href target="_blank" rel="noopener noreferrer">`.
  - However, a CommonMark+GFM-compliant parser (e.g., `markdown-it`) by default sanitizes `javascript:`, `vbscript:`, and `data:` URLs out of the `href` (replaces with `#` or strips the link). Verify the chosen parser does this.
  - If the parser does NOT strip dangerous schemes by default, the implementation MUST add an explicit allow-list (`http`, `https`, `mailto` only) before classifying as external — otherwise SEC-14 fails.
- **Pass criterion.** None of `xss-1` through `xss-4` produces an `<a>` element whose `href` attribute starts with `javascript:`, `vbscript:`, or `data:`. They render as plain text, broken-outside, or with `href="#"`. `xss-5` (`file://`) similarly produces no clickable `<a>` (or is treated as broken-outside). `normal` renders as `<a target="_blank" rel="noopener noreferrer">`. `internal` renders as a React-Router `<Link>`.
- **Spec refs.** FR-30, FR-31, FR-33.
- **Fixture.** One markdown file; remove after.
- **Platform.** all.

---

## SEC-15 — External-image SSRF — confirm no SSRF surface exists

- **Threat.** A markdown image with a `src` pointing at an internal localhost URL (`http://127.0.0.1:8765/api/file?path=...`) or an internal-network address could trigger an SSRF if the *backend* fetched URLs. Per FR-36 the backend never proxies images.
- **Vector.** Markdown image embedded in a file.
- **Probe inputs.**
  - Fixture: `specs/development/spec_driven/final_specs/img_test.md` containing:

    ```
    ![SSRF](http://127.0.0.1:8765/api/file?path=specs/development/spec_driven/final_specs/spec.md)
    ![internal-net](http://169.254.169.254/latest/meta-data/)
    ![local-img](dossier.png)
    ```

- **Curl form.** Browser-driven; observe network panel.
- **Expected behavior.**
  - External images render as `<img src=...>` straight (FR-36); the *browser* may attempt the fetch but the *backend* never does.
  - The internal-image case (`dossier.png`) resolves inside `EXPOSED_TREE` but the extension `.png` is not in `{.md,.yaml,.yml,.json,.jsonl}`; per FR-36 it renders as a `<span class="image-placeholder">` with title `v1: images not rendered`. The backend serves NO image bytes via `/api/file` (it would 415 anyway).
- **Pass criterion.** Server logs contain ZERO requests to `169.254.169.254`, ZERO outbound `requests.get`/`urllib.request` calls during the test. The two external image URLs render as raw `<img>` tags; the browser may load or fail to load them but no traffic is initiated by the backend. The internal `dossier.png` renders as a placeholder span, not an `<img>`. Source grep: `grep -rn 'requests.get\|urllib.request\|httpx.get\|aiohttp' projects/spec_driven/backend` returns zero hits in production code paths.
- **Spec refs.** FR-36, NFR-7.
- **Fixture.** One markdown file; remove after.
- **Platform.** all.

---

## SEC-16 — Error leakage — no stack traces, no internal paths

- **Threat.** A 5xx with a Python traceback in the response body discloses the absolute path of `REPO_ROOT`, the Python class hierarchy, library versions, and code structure to a local attacker.
- **Vector.** Trigger each FR-5.7 enumerated exception class and inspect the response body.
- **Probe inputs.**
  - Trigger `PermissionError`:
    - Unix: `chmod 000 specs/development/spec_driven/final_specs/spec.md`; then `curl -i 'http://127.0.0.1:8765/api/file?path=specs/development/spec_driven/final_specs/spec.md'`. Restore permissions after.
    - Windows: deny-read ACL via `icacls spec.md /deny "%USERNAME%:R"`; same curl; restore after.
  - Trigger `IsADirectoryError`: `curl -i 'http://127.0.0.1:8765/api/file?path=specs/development/spec_driven/final_specs'` (the path is the directory itself). Note: extension check probably 415s first; explicitly probe with `path=specs/development/spec_driven/final_specs/.`. If extension still trips, accept 415 and skip the IsADirectory branch.
  - Trigger `FileNotFoundError`: `curl -i 'http://127.0.0.1:8765/api/file?path=specs/development/spec_driven/final_specs/does_not_exist.md'`. Expect 404 `kind: "file_removed"` or `kind: "outside_exposed_tree"`.
- **Curl form.**

  ```
  chmod 000 specs/development/spec_driven/final_specs/spec.md
  curl -i 'http://127.0.0.1:8765/api/file?path=specs/development/spec_driven/final_specs/spec.md'
  chmod 644 specs/development/spec_driven/final_specs/spec.md
  ```

- **Expected behavior.** Each exception is caught (FR-5.7) and mapped to a structured response with a small JSON body: `{"error":"permission_denied"}`, `{"error":"is_directory"}`, `{"error":"not_found","kind":"file_removed"}`. The body NEVER contains:
  - The substring `Traceback (most recent call last)` — fail if present.
  - An absolute filesystem path containing the user's home directory or `REPO_ROOT` value — fail if present.
  - A Python class FQN like `builtins.PermissionError` or `pathlib.PosixPath` — fail if present.
  - A stack-frame line number reference (e.g., `File "/.../libs/files.py", line 42`) — fail if present.
- **Pass criterion.** All probes return the documented status (403, 400, 404 respectively). Body bytes match a tight schema with no traceback markers. Server log can include a traceback (operationally useful), but the HTTP body cannot.
- **Spec refs.** FR-5.7.
- **Fixture.** Permission flip on spec.md (revert after).
- **Platform.** all.

---

## SEC-17 — `EXPOSED_TREE` escape via FR-37 link resolution

- **Threat.** A link in `CLAUDE.md` (or an agent file, or a skill file) points to a real, existing file in the repo that is *outside* `EXPOSED_TREE` (e.g., `pyproject.toml`, `tools/scripts/foo.py`). The frontend link resolver must mark these broken-outside, NOT internal.
- **Vector.** Markdown link from a Section-1 file to a non-`EXPOSED_TREE` repo file.
- **Probe inputs.**
  - Fixture: temporarily inject a test sentence into `CLAUDE.md` (or use a fixture-fork in tests):

    ```
    See [pyproject](pyproject.toml).
    See [readme](README.md).  # ALSO outside EXPOSED_TREE per FR-1
    See [skills overview](.claude/skills/agent_team/SKILL.md).  # inside EXPOSED_TREE; should be internal
    ```

  - Render `CLAUDE.md` and inspect the DOM.
- **Curl form.** Browser-driven; same DevTools snippet as SEC-14.
- **Expected behavior.**
  - `pyproject.toml` link: classified broken-outside per FR-37. Renders as `<span class="link-broken" title="outside exposed tree">`. Not clickable.
  - `README.md` (repo-root README) link: same — outside `EXPOSED_TREE` (only `CLAUDE.md` is exposed at root). Broken-outside.
  - `.claude/skills/agent_team/SKILL.md` link: inside `EXPOSED_TREE`. Renders as a working in-app `<Link>`.
- **Pass criterion.** First two links produce a `<span class="link-broken">` with title `outside exposed tree`; never a working `<a href>`; never a 200 from `/api/file?path=pyproject.toml`. The third link is a working `<Link>`. Independent verification via `curl -i 'http://127.0.0.1:8765/api/file?path=pyproject.toml'` returns 404 with `kind:"outside_exposed_tree"` (the backend independently rejects per FR-6).
- **Spec refs.** FR-33, FR-37, FR-6.
- **Fixture.** Either edit a working copy of `CLAUDE.md` for the test (revert after) or use a synthetic fixture file in a test harness; do not commit the test sentences.
- **Platform.** all.

---

## SEC-18 — Tree response does not leak metadata for skipped or out-of-tree entries

- **Threat.** Even though symlinks and out-of-tree files are not served via `/api/file`, the tree response could still leak their existence or `stat()` info (size, mtime, target path) to a caller who wouldn't otherwise know they exist.
- **Vector.** Inspect `/api/tree` JSON for any reference to symlinks (per SEC-05c) or to files outside the four `EXPOSED_TREE` source globs.
- **Probe inputs.**
  - Pre-stage: SEC-05c's `tmp_link` directory symlink is in place.
  - Pre-stage: a file at `specs/development/spec_driven/final_specs/extra.txt` (extension not whitelisted, but it physically exists in a stage subfolder).
  - Pre-stage: a file at `specs/development/spec_driven/random_dir/foo.md` (outside the five fixed stage subfolders, per FR-10).
  - Probe: `curl -s 'http://127.0.0.1:8765/api/tree' | python -m json.tool`.
- **Curl form.**

  ```
  curl -s 'http://127.0.0.1:8765/api/tree' > /tmp/tree.json
  python -c "import json,sys; t=json.load(open('/tmp/tree.json')); print(json.dumps(t,indent=2))"
  ```

- **Expected behavior.**
  - Symlink dir: NOT present in any list (FR-4).
  - `extra.txt`: per FR-1 only files with whitelisted extensions are in `EXPOSED_TREE`; the tree-walk should skip it. (If the implementation lists all files in the stage subfolder regardless of extension and lets the file-read endpoint reject by extension, that's a spec deviation — flag.)
  - `random_dir/foo.md`: NOT present (FR-10 — only the five fixed stage subfolders are exposed; siblings are ignored).
  - Each leaf in the response contains *only* the keys needed by the sidebar: `name`, `path` (relative to repo root), `present` (FR-9), perhaps `kind`. NO `size`, NO `mtime`, NO `target`, NO `realpath`, NO `inode`.
- **Pass criterion.** Response JSON does not contain the substrings `tmp_link`, `extra.txt`, `random_dir`. Response JSON schema for each leaf has no `size`, `mtime`, `target`, `realpath`, `inode`, or any other `stat`-derived key.
- **Spec refs.** FR-1, FR-3, FR-4, FR-10.
- **Fixture.** Three fixture entries staged; remove after.
- **Platform.** all (symlink portion unix-primary).

---

## Summary

| ID     | Theme                              | Status when implemented |
|--------|------------------------------------|-------------------------|
| SEC-01 | `..` traversal                     | required                |
| SEC-02 | absolute / UNC                     | required                |
| SEC-03 | NUL byte injection                 | required                |
| SEC-04 | OS-specific resolve quirks         | required                |
| SEC-05 | symlinks (3 sub-cases)             | required                |
| SEC-06 | extension whitelist                | required                |
| SEC-07 | binary-content rejection           | required                |
| SEC-08 | size limit (3 boundaries)          | required                |
| SEC-09 | tree-walk DoS                      | accepted-undefined-behavior beyond NFR-15; verify no 500 |
| SEC-10 | GET-only verbs                     | required                |
| SEC-11 | bind to 127.0.0.1                  | required                |
| SEC-12 | no CORS wildcard                   | required                |
| SEC-13 | no auth + README states model      | required                |
| SEC-14 | markdown XSS via `javascript:`     | required                |
| SEC-15 | no backend-side URL fetching       | required                |
| SEC-16 | no stack traces in error bodies    | required                |
| SEC-17 | FR-37 outside-tree link rejection  | required                |
| SEC-18 | tree response leaks no metadata    | required                |

End of security checks document.
