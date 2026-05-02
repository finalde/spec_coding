# Validation — Security

Run: spec_driven-20260502-clean
Stage: 5
Source spec: `specs/development/spec_driven/final_specs/spec.md`
Inputs read: spec.md only (read-zero)

## Threat model

The deployment posture is **single-user, localhost-bound, no authentication** (NFR-7, NFR-8). The spec explicitly takes auth, sessions, and access control out of scope. Threats decompose into:

### In-scope (must be defended against in code)

1. **Malicious file content from upstream Claude.** Claude Code or other tooling writes files into the exposed tree. Markdown and JSON content is therefore semi-trusted: it can contain `javascript:` URIs, traversal-shaped link hrefs, oversized payloads, NUL bytes, and links pointing outside the tree. Defense lives in the link classifier (FR-33), the file-read pipeline (FR-5), and the markdown sanitization layer.
2. **Cross-origin local browser tab.** Another tab on the same machine could try to issue requests to `http://127.0.0.1:8765/`. Defense: no permissive CORS (NFR-8), GET-only verbs are read-only, and the mutation endpoints reuse the same `safe_resolve` + `EXPOSED_TREE` membership checks as reads (FR-14a).
3. **Confused-deputy traversal.** A path query parameter (`/api/file?path=...`, `/api/regen-prompt` body) is the user-controlled surface. Anything that joins user input to `REPO_ROOT` outside the single `safe_resolve` helper is a vulnerability (FR-6, NFR-4).
4. **Filesystem races during write.** `PUT /api/file` must not produce a torn file under concurrent writers (FR-14a atomic-replace via `os.replace`).
5. **DoS via tree shape.** A pathological repo (10K files, deep nesting) must not 500 the `/api/tree` endpoint.

### Out-of-scope (explicitly accepted as residual risk)

- **Remote network attacker.** Mitigated entirely by NFR-7 (loopback bind). If the deployer overrides `--host` to `0.0.0.0`, that is operator error, not a code defect — but SEC-11 verifies the default.
- **Trusted local user privilege escalation.** The single user can already write any file in the repo without the app; the app does not expand their authority.
- **TOCTOU between `safe_resolve` and `open()`.** Symlinks created in the microsecond gap are treated as the OS treats them; we do not lock the tree. NFR-12 explicitly accepts torn-read UX.

## Probes

### SEC-01 — Dot-dot path traversal (multiple forms)

- **Attack vector.** `path` query param crafted to escape `REPO_ROOT`.
- **Method.** Run each curl sequentially:
  ```
  curl -i "http://127.0.0.1:8765/api/file?path=../../../etc/hosts"
  curl -i "http://127.0.0.1:8765/api/file?path=..%2F..%2F..%2Fetc%2Fhosts"
  curl -i "http://127.0.0.1:8765/api/file?path=specs/../../../etc/hosts"
  curl -i "http://127.0.0.1:8765/api/file?path=specs%2F..%2F..%2F..%2Fetc%2Fhosts"
  curl -i "http://127.0.0.1:8765/api/file?path=./.././../etc/hosts"
  ```
- **Expected behavior.** Each call returns HTTP 400 with JSON body `{"detail": {"kind": "outside_sandbox", ...}}`. No filesystem read of `/etc/hosts` occurs.
- **Pass criterion.** Status == 400 for every variant; response body's `kind` is `outside_sandbox`; no `/etc/hosts` content appears in the response.
- **Spec refs.** FR-5.1, FR-6, AC-7.

### SEC-02 — Absolute paths including UNC

- **Attack vector.** `path` is an absolute path or Windows UNC share.
- **Method.**
  ```
  curl -i "http://127.0.0.1:8765/api/file?path=/etc/passwd"
  curl -i "http://127.0.0.1:8765/api/file?path=C:%5CWindows%5Cwin.ini"
  curl -i "http://127.0.0.1:8765/api/file?path=%5C%5Cattacker%5Cshare%5Cfile.md"
  curl -i "http://127.0.0.1:8765/api/file?path=//attacker/share/file.md"
  ```
- **Expected behavior.** `safe_resolve` rejects (the `relative_to(REPO_ROOT)` step raises `ValueError`).
- **Pass criterion.** Each returns 400 `outside_sandbox`. No outbound SMB connection observed in OS-level network trace.
- **Spec refs.** FR-5.1, FR-6.

### SEC-03 — Null-byte injection in path

- **Attack vector.** Embed `%00` to truncate path interpretation in legacy stacks.
- **Method.**
  ```
  curl -i "http://127.0.0.1:8765/api/file?path=specs/development/spec_driven/final_specs/spec.md%00.png"
  curl -i "http://127.0.0.1:8765/api/file?path=CLAUDE.md%00"
  ```
- **Expected behavior.** Either Python's `Path` constructor raises (caught and mapped to 400) or `safe_resolve` rejects on extension whitelist; never reads the truncated form.
- **Pass criterion.** Status is 4xx (400 or 415). Response body contains no file contents. No 500.
- **Spec refs.** FR-5.1, FR-5.4.

### SEC-04 — OS-specific path tricks (Windows)

- **Attack vector.** Alternate Data Streams, 8.3 short names, case-insensitive matching that bypasses an exact-suffix check.
- **Method.** On Windows host:
  ```
  curl -i "http://127.0.0.1:8765/api/file?path=CLAUDE.md::%24DATA"
  curl -i "http://127.0.0.1:8765/api/file?path=CLAUDE.MD"
  curl -i "http://127.0.0.1:8765/api/file?path=PROGRA~1/foo.md"
  ```
  Plus DOM check: requesting `/api/file?path=claude.md` (lowercase) on a case-insensitive volume should still produce a deterministic outcome — either resolves to the canonical path OR returns 404, never returns content under a path that disagrees with the on-disk casing.
- **Expected behavior.** ADS form returns 415 (`::$DATA` is not in the extension whitelist) or 404 (resolved path not under EXPOSED_TREE source globs). 8.3 short-name form returns 400/404. Case mismatch matches the OS reality but is documented in FR-33's "Windows-aware case-mismatch tooltip".
- **Pass criterion.** No `::DATA` content served. 8.3 form does not bypass the whitelist. No 500.
- **Spec refs.** FR-5.4, FR-33.

### SEC-05 — Symlinks (file, parent, target inside vs outside)

- **Attack vector.** Symlink under `EXPOSED_TREE` pointing inside or outside the tree.
- **Method.** Set up four fixtures inside a sandbox repo:
  1. `specs/dev/x/user_input/inside_link.md` → `specs/dev/x/user_input/raw_prompt.md` (target inside tree).
  2. `specs/dev/x/user_input/outside_link.md` → `/etc/hosts` (target outside tree).
  3. `specs/dev/x/user_input/link_dir/raw_prompt.md` where `link_dir` is a symlink to a directory inside the tree.
  4. `specs/dev/x/user_input/link_dir2/raw_prompt.md` where `link_dir2` symlinks outside the tree.
  Then:
  ```
  curl -i "http://127.0.0.1:8765/api/file?path=specs/dev/x/user_input/inside_link.md"
  curl -i "http://127.0.0.1:8765/api/file?path=specs/dev/x/user_input/outside_link.md"
  curl -i "http://127.0.0.1:8765/api/file?path=specs/dev/x/user_input/link_dir/raw_prompt.md"
  curl -i "http://127.0.0.1:8765/api/file?path=specs/dev/x/user_input/link_dir2/raw_prompt.md"
  curl -s "http://127.0.0.1:8765/api/tree" | jq '.. | .name? // empty' | grep -E "(inside_link|outside_link)"
  ```
- **Expected behavior.** All four file requests return 400 `outside_sandbox` (FR-5.2 rejects symlinks AND walks parent segments). Tree response omits all symlinked entries (FR-4).
- **Pass criterion.** Zero file bytes served from any symlink case, including the inside-tree target. Tree grep returns empty.
- **Spec refs.** FR-4, FR-5.2, NFR-5.

### SEC-06 — Extension whitelist enforcement

- **Attack vector.** Request a non-whitelisted extension hoping to trigger the file-read path.
- **Method.**
  ```
  curl -i "http://127.0.0.1:8765/api/file?path=specs/development/spec_driven/final_specs/spec.png"
  curl -i "http://127.0.0.1:8765/api/file?path=CLAUDE.MD.bak"
  curl -i "http://127.0.0.1:8765/api/file?path=specs/development/spec_driven/note.txt"
  curl -i "http://127.0.0.1:8765/api/file?path=specs/development/spec_driven/script.py"
  curl -i "http://127.0.0.1:8765/api/file?path=specs/development/spec_driven/.env"
  ```
- **Expected behavior.** Each returns 415 with `unsupported_extension`. Whitelist is `{.md, .yaml, .yml, .json, .jsonl}` only.
- **Pass criterion.** Status 415 every time; body contains the structured error key; no file bytes leaked.
- **Spec refs.** FR-5.4, AC-8.

### SEC-07 — Binary content (`\x00`) rejection

- **Attack vector.** A `.md` extension hides binary payload that could trip downstream renderers.
- **Method.** Create fixture `specs/development/spec_driven/user_input/binary.md` whose content is `b"# Header\x00\x01evil"`. Then:
  ```
  curl -i "http://127.0.0.1:8765/api/file?path=specs/development/spec_driven/user_input/binary.md"
  ```
- **Expected behavior.** 415 `binary_content`. Read uses `errors="replace"` so the NUL byte survives the decode and the post-decode check fires.
- **Pass criterion.** Status 415; body's `kind` is `binary_content`; no part of the binary data appears in the response.
- **Spec refs.** FR-5.6, NFR-13, AC-9.

### SEC-08 — Size limit (>2 MB)

- **Attack vector.** Oversize file used as DoS or to exhaust client memory.
- **Method.** Create `specs/development/spec_driven/user_input/huge.md` of `2_500_000` bytes (`python -c "open('huge.md','wb').write(b'a' * 2_500_000)"`). Then:
  ```
  curl -i "http://127.0.0.1:8765/api/file?path=specs/development/spec_driven/user_input/huge.md"
  ```
- **Expected behavior.** 413 `too_large` BEFORE the file body is read into memory (the size check uses `Path.stat().st_size`).
- **Pass criterion.** Status 413; the response body length is < 1 KB (no file leakage); server RSS does not jump by 2.5 MB during the call.
- **Spec refs.** FR-5.5, AC-10, NFR-15.

### SEC-09 — Tree-walk DoS at 10K files

- **Attack vector.** Pathological-but-legitimate repo shape causes uncaught exception → 500.
- **Method.** Generate fixture `tests/fixtures/big_repo/` with 50 projects × 200 files of size 1 KB across the five stage subfolders. Point `REPO_ROOT` discovery at it. Then:
  ```
  for i in $(seq 1 5); do curl -s -o /dev/null -w "%{http_code} %{time_total}\n" "http://127.0.0.1:8765/api/tree"; done
  ```
- **Expected behavior.** Every response is 200, JSON well-formed, p95 within performance budget (cross-ref PERF-01). No 500. Memory peak < 200 MB during the walk.
- **Pass criterion.** Five consecutive 200s with non-empty `projects` array; zero 500s.
- **Spec refs.** FR-3, NFR-1, NFR-15.

### SEC-10 — GET-only verb confusion

- **Attack vector.** Attempt to use unsanctioned HTTP methods on the file endpoint.
- **Method.**
  ```
  curl -i -X PATCH "http://127.0.0.1:8765/api/file?path=CLAUDE.md"
  curl -i -X DELETE "http://127.0.0.1:8765/api/file?path=CLAUDE.md"
  curl -i -X POST "http://127.0.0.1:8765/api/file" -H "Content-Type: application/json" -d '{"path":"CLAUDE.md","text":"x"}'
  curl -i -X OPTIONS "http://127.0.0.1:8765/api/file"
  ```
- **Expected behavior.** PATCH and DELETE return 405. POST returns 405 (sanctioned mutator is PUT). OPTIONS may return 405 or 200 with empty Allow as long as no CORS wildcard appears.
- **Pass criterion.** PATCH=405, DELETE=405, POST=405. No file mutation occurred (verify CLAUDE.md mtime is unchanged).
- **Spec refs.** NFR-6, AC-23.

### SEC-11 — Bind address verification

- **Attack vector.** Process listens on `0.0.0.0` exposing the API to LAN.
- **Method.** With the server running, run:
  ```
  netstat -an | grep 8765
  python -c "import socket; s=socket.socket(); s.settimeout(1); s.connect(('127.0.0.1',8765)); print('lo ok')"
  python -c "import socket,subprocess; ip=subprocess.check_output('hostname -I',shell=True).decode().split()[0]; s=socket.socket(); s.settimeout(1); s.connect((ip,8765))"
  ```
- **Expected behavior.** `netstat` shows listen on `127.0.0.1:8765`, NOT `0.0.0.0:8765`. The third connect raises `ConnectionRefusedError` or times out.
- **Pass criterion.** Bind line contains `127.0.0.1`; LAN-IP connect fails.
- **Spec refs.** FR-12, NFR-7, AC-24.

### SEC-12 — No `Access-Control-Allow-Origin: *`

- **Attack vector.** Wildcard CORS lets any local origin make authenticated requests.
- **Method.**
  ```
  curl -is "http://127.0.0.1:8765/api/tree" | grep -i "^access-control"
  curl -is -H "Origin: http://evil.example" "http://127.0.0.1:8765/api/tree" | grep -i "^access-control"
  ```
- **Expected behavior.** Neither call emits any `Access-Control-Allow-Origin` header (the spec is single-origin). If headers are present, none equal `*` and none reflect arbitrary origins.
- **Pass criterion.** First grep is empty. Second grep is empty (no reflected origin).
- **Spec refs.** NFR-8, AC-25.

### SEC-13 — No auth code paths greppable

- **Attack vector.** Half-built auth scaffolding gives a false sense of security and may be partially bypassable.
- **Method.** Static check at repo root:
  ```
  rg -ni "(authenticate|authorization|bearer|jwt|session|login|password|api[_-]?key)" projects/spec_driven/backend/
  ```
- **Expected behavior.** Zero matches in production code (test fixtures verifying absence are OK).
- **Pass criterion.** `rg` exits with status 1 (no matches) when run against the backend `libs/` and `main.py`.
- **Spec refs.** NFR-7.

### SEC-14 — Markdown XSS / `javascript:` URL sanitization

- **Attack vector.** A markdown link `[click](javascript:alert(1))` turns into a working JS-execution sink.
- **Method.** Create fixture `specs/development/spec_driven/user_input/xss.md` containing:
  ```
  [click](javascript:alert(1))
  [data](data:text/html,<script>alert(1)</script>)
  [vbs](vbscript:msgbox(1))
  [legit](https://example.com)
  ```
  Open `http://127.0.0.1:8765/file/specs/development/spec_driven/user_input/xss.md` in DevTools. For each link:
  - Inspect the rendered DOM via `document.querySelectorAll('a').forEach(a => console.log(a.href, a.textContent))`.
  - Click each `javascript:` / `data:` / `vbscript:` link.
- **Expected behavior.** FR-33 case 1 classifies any `^[a-z][a-z0-9+.-]*:` href as external. Then the link classifier or sanitizer must drop dangerous schemes — they should render either as a broken-link span (FR-34) or as an `<a>` whose `href` has been stripped to `#` / `about:blank`. Clicking executes nothing.
- **Pass criterion.** No alert dialog appears. Rendered DOM contains no anchor with `href` starting `javascript:`, `data:`, or `vbscript:`. The legitimate `https://example.com` link DOES render as an `<a target="_blank" rel="noopener noreferrer">`.
- **Spec refs.** FR-33, FR-34.

### SEC-15 — SSRF surface absence

- **Attack vector.** A backend endpoint that fetches arbitrary URLs would let a local attacker pivot via the loopback service.
- **Method.** Static check:
  ```
  rg -ni "(httpx|aiohttp|urllib\.request|requests\.(get|post)|fetch\()" projects/spec_driven/backend/libs/
  rg -ni "(httpx|aiohttp|urllib\.request|requests\.(get|post))" projects/spec_driven/backend/main.py
  ```
- **Expected behavior.** Zero matches. The backend never makes outbound HTTP.
- **Pass criterion.** Both greps exit 1.
- **Spec refs.** Out-of-scope list (no model invocation, no external fetches), NFR-7.

### SEC-16 — Error leakage (no stack traces, no Python class names, no local paths)

- **Attack vector.** 4xx/5xx response bodies leak filesystem paths or internal class names.
- **Method.** Provoke each error class and inspect bodies:
  ```
  curl -s "http://127.0.0.1:8765/api/file?path=../../../etc/hosts" | jq .
  curl -s "http://127.0.0.1:8765/api/file?path=specs/development/spec_driven/missing.md" | jq .
  curl -s "http://127.0.0.1:8765/api/file?path=specs/development/spec_driven/final_specs/spec.png" | jq .
  curl -s -X PUT "http://127.0.0.1:8765/api/file" -H "Content-Type: application/json" -d '{}' | jq .
  ```
  Grep responses for forbidden tokens:
  ```
  ... | grep -E "(Traceback|File \"|line [0-9]+|FastAPI|ValueError|FileNotFoundError|/home/|C:\\\\Users|REPO_ROOT)"
  ```
- **Expected behavior.** Each body is `{"detail": {"kind": "<error_key>", "message": "<short, no path>"}}`. No stack frames, no exception class names, no absolute filesystem paths.
- **Pass criterion.** Forbidden-token grep returns empty. Each response is valid JSON with a `kind` field from the documented set.
- **Spec refs.** FR-5.7 ("Never let these bubble into a 500"), FR-14a error mapping.

### SEC-17 — Outside-tree link rejection (FR-37)

- **Attack vector.** A link from `CLAUDE.md` or an agent file points outside `EXPOSED_TREE` (e.g., `../../etc/hosts` or `projects/spec_driven/backend/main.py`) — clicking should not navigate.
- **Method.** Add to a sandbox `CLAUDE.md`:
  ```
  [outside1](../../../etc/hosts)
  [outside2](projects/spec_driven/backend/main.py)
  [outside3](.audit/adhoc_agents/2026-05-02/x/events.jsonl)
  [inside](specs/development/spec_driven/final_specs/spec.md)
  ```
  Render `/file/CLAUDE.md`. For each link, check via DOM:
  ```
  document.querySelectorAll('.link-broken[aria-disabled="true"]').forEach(s => console.log(s.title, s.textContent))
  document.querySelectorAll('a[href^="/file/"]').forEach(a => console.log(a.href))
  ```
- **Expected behavior.** `outside1`, `outside2`, `outside3` all render as `<span class="link-broken" aria-disabled="true">` with title "outside exposed tree" or "file not found" depending on existence. `inside` renders as a navigable `<a href="/file/...">`.
- **Pass criterion.** Three broken spans, one navigable link. No anchor whose href escapes EXPOSED_TREE.
- **Spec refs.** FR-33 case 3, FR-34, FR-37.

### SEC-18 — PUT atomic-write race

- **Attack vector.** Two concurrent `PUT /api/file` calls on the same path interleave their writes, producing a torn file.
- **Method.** With a 500 KB target file `specs/development/spec_driven/user_input/race.md`, run:
  ```
  python -c "
  import concurrent.futures, requests, hashlib
  A = 'A' * 500_000
  B = 'B' * 500_000
  url = 'http://127.0.0.1:8765/api/file'
  def put(text): return requests.put(url, json={'path':'specs/development/spec_driven/user_input/race.md','text':text}).status_code
  for _ in range(50):
      with concurrent.futures.ThreadPoolExecutor(2) as ex:
          fA, fB = ex.submit(put, A), ex.submit(put, B)
          print(fA.result(), fB.result())
      with open('specs/development/spec_driven/user_input/race.md') as f: c = f.read()
      assert c == A or c == B, f'TORN: len={len(c)} prefix={c[:5]} suffix={c[-5:]}'
      assert hashlib.md5(c.encode()).hexdigest() in (hashlib.md5(A.encode()).hexdigest(), hashlib.md5(B.encode()).hexdigest())
  print('OK')
  "
  ```
- **Expected behavior.** Across 50 rounds, the file content always equals exactly one of the two payloads — never a hybrid. Both PUTs return 200. `os.replace` provides POSIX/NTFS atomicity.
- **Pass criterion.** Script prints `OK` (no `TORN` AssertionError); 100 of 100 PUTs returned 200.
- **Spec refs.** FR-14a (atomic-replace via `tempfile.mkstemp` + `os.fsync` + `os.replace`).

### SEC-19 — Regen-prompt size hard ceiling

- **Attack vector.** A bloated revised_prompt + many follow-ups yields a >1 MB assembled prompt; the endpoint must 413 rather than silently truncate (warn-don't-truncate threshold is 50 KB; hard ceiling is 1 MB).
- **Method.** Plant fixture project `specs/development/_oversize/` with:
  - `user_input/revised_prompt.md` of 1.2 MB.
  - One follow-up of 100 KB.
  Then:
  ```
  curl -is -X POST "http://127.0.0.1:8765/api/regen-prompt" \
    -H "Content-Type: application/json" \
    -d '{"project_type":"development","project_name":"_oversize","stages":["spec"],"modules":{"spec":["spec.md"]},"autonomous":false}'
  ```
- **Expected behavior.** Status 413 with `kind: "too_large"`. Response body length is small (no truncated prompt body included).
- **Pass criterion.** Status == 413; body's `kind` is `too_large`; response body < 1 KB.
- **Spec refs.** FR-14c size policy, AC-19.

### SEC-20 — Read-zero contract surfaced in regen prompt

- **Attack vector.** The webapp silently drops the read-zero constraint, causing downstream Claude to read prior outputs and reintroduce stale assumptions — a correctness failure with security flavor (the constraint is what guarantees regeneration is genuinely from-scratch).
- **Method.**
  ```
  curl -s -X POST "http://127.0.0.1:8765/api/regen-prompt" \
    -H "Content-Type: application/json" \
    -d '{"project_type":"development","project_name":"spec_driven","stages":["spec"],"modules":{"spec":["spec.md"]},"autonomous":true}' \
    | jq -r .prompt | grep -i "read-zero\|delete prior outputs first\|reads only the inputs"
  ```
- **Expected behavior.** The grep returns at least one match — the assembled prompt's `### Constraints` section spells out "regeneration deletes prior outputs first; new generation reads only the inputs."
- **Pass criterion.** Non-empty grep output. The autonomous header `# EXECUTION MODE: AUTONOMOUS` is on line 1 of the prompt; the read-zero string appears in the constraints section.
- **Spec refs.** FR-14c (f), AC-20, AC-21.

## Reporting

A failure on **any** of SEC-01..SEC-20 is a release blocker. Re-run the full suite manually before each release. No CI infrastructure required (per the locked scope — single-user dogfood).
