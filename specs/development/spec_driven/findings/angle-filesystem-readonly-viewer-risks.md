# Angle: filesystem-readonly-viewer-risks

## 1. What this angle covers

A scan-on-every-request, readonly FastAPI viewer over a *live* tree (`specs/`, `.claude/`, `CLAUDE.md`) that Claude Code is concurrently editing. We map the realistic failure modes — race conditions, path traversal, symlinks, encoding, permissions, stale UI — then triage which need v1 code and which can defer.

The locked decisions framing this risk surface:
- backend re-walks the tree on every API call (no cache, no watcher);
- repo root found by walking upward for `CLAUDE.md` + `specs/` + `.claude/`;
- readonly only;
- single user, single port, localhost;
- the same git tree is mutated by Claude Code while the viewer runs.

Single-user localhost shrinks the threat model significantly — but does not eliminate the operational footguns (a half-written file, a `..` link in markdown, a transient `FileNotFoundError`).

## 2. Key findings

### 2.1 Path traversal is the only "real" security risk in v1

- Starlette's `StaticFiles` had a real CVE here (CVE-2023-29159, fixed in 0.27.0). The bug was using `os.path.commonprefix` instead of comparing resolved absolute paths — `/static/../static1.txt` matched the prefix `./static`. ([starlette advisory](https://github.com/Kludex/starlette/security/advisories/GHSA-v5gw-mw7f-84px), [PR #985](https://github.com/encode/starlette/pull/985/files), [CVE-2023-29159](https://github.com/advisories/GHSA-v5gw-mw7f-84px))
- The robust pattern is well-established: `Path(base).resolve()`, `Path(base / user_input).resolve()`, then `resolved.relative_to(base_resolved)` — catch `ValueError` ⇒ reject. `commonpath`/`commonprefix` on raw strings is the wrong primitive. ([OpenStack guideline](https://security.openstack.org/guidelines/dg_using-file-paths.html), [pathlib docs](https://docs.python.org/3/library/pathlib.html))
- Even on a single-user localhost server, traversal is exploitable through user-authored content: a markdown link `[oops](../../../.ssh/id_rsa)` clicked in the viewer, an `iframe` in rendered HTML, or any cross-link the spec mentions. The "attacker" is not a hostian — it's the user's own pasted content. This warrants v1 code.

### 2.2 Symlinks: refuse, don't follow

- `Path.resolve()` follows symlinks by default and that is a foot-gun: a symlink inside `specs/` to `/etc/passwd` resolves to the target, then sandbox check (correctly) rejects — fine. But a symlink chain or loop can hang or `OSError`. ([CPython issue 109187 — symlink loops](https://github.com/python/cpython/issues/109187))
- Mature file servers all expose a "no symlinks" knob: nginx ships `disable_symlinks on` / `if_not_owner` ([nginx docs reference](https://www.oreilly.com/library/view/nginx-http-server/9781788623551/e1c22cbb-8229-4025-bff9-426c0086f41c.xhtml), [Plesk symlink hardening](https://docs.plesk.com/en-US/obsidian/administrator-guide/plesk-administration/securing-plesk/mitigating-the-symlinks-vulnerability.79045/)); Dufs has `--allow-symlink` (off by default) ([Dufs README](https://github.com/sigoden/dufs)).
- For our case the spec_coding repo never legitimately uses symlinks under `specs/` or `.claude/`. Cheapest correct policy: refuse to traverse into `Path.is_symlink()` entries during directory listing AND verify the resolved path is still under the sandboxed root.

### 2.3 Race conditions exist but are mild — handle with EAFP

- Two windows: (a) listing returns a file, then a follow-up read returns `FileNotFoundError`; (b) reading mid-write returns a truncated/partial markdown blob.
- The Pythonic fix is EAFP — `try: open(...) except FileNotFoundError`, return 404 with a `{"reason": "removed_during_request"}` body. Pre-checking with `os.path.exists` is the textbook race-condition antipattern. ([yapf #731 race condition](https://github.com/google/yapf/issues/731), [Python tracker — pyc race](https://bugs.python.org/issue210610))
- Torn writes are a real concern only against tools that do truncate-then-write (the historic VS Code default — `vscode#98063`). Atomic writers (`tempfile.NamedTemporaryFile` + `os.replace`, the pattern python-atomicwrites canonized) make the pre-rename file invisible to readers. ([VS Code #98063 atomic save](https://github.com/microsoft/vscode/issues/98063), [python-atomicwrites](https://python-atomicwrites.readthedocs.io/), [ActiveState recipe](https://code.activestate.com/recipes/579097-safely-and-atomically-write-to-a-file/))
- Claude Code's own `Write` tool truncates-and-rewrites in place (NOT atomic) — so a race where the viewer reads while Claude's write is in flight CAN return a partial/empty markdown body. For a single-user dogfood the user just refreshes; the viewer should not crash, but does not need an atomic-read shim.
- Git checkout itself avoids the same races for parallel checkout by sequencing creation/removal. We do not need to mimic that — we only read. ([Git parallel-checkout doc](https://git-scm.com/docs/parallel-checkout))

### 2.4 Encoding / binary safety

- Markdown renderers expect Unicode; passing raw bytes to python-markdown breaks. ([python-markdown reference](https://python-markdown.github.io/reference/))
- Spec artifacts are author-controlled markdown. Realistic risks are limited to: (a) BOM-prefixed UTF-8 from a Windows editor; (b) a stray binary file (image, PDF) accidentally placed under `specs/`. `chardet` solves (a) overkill — `open(..., encoding="utf-8")` handles BOM via `utf-8-sig` if needed, and `errors="replace"` is enough for misencoded bytes. For (b), `chardet` returns encoding `None` and a binary MIME type via magic numbers — a fine quick reject signal. ([chardet docs](https://chardet.readthedocs.io/en/latest/usage.html), [chardet how-it-works](https://chardet.readthedocs.io/en/latest/how-it-works.html))
- A pragmatic v1 rule: read at most `MAX_BYTES` (e.g. 2 MB given the ≤500 KB target), decode with `utf-8` + `errors="replace"`, and if the result contains NUL bytes (`\x00`) classify as binary and refuse to render. No `chardet` dependency needed.

### 2.5 Permissions

- A file existing-but-unreadable (Windows ACL deny, Unix `chmod 000`) raises `PermissionError`. Treat the same as 404 from the user's POV with a distinct `reason: "permission_denied"` for logs. No special code beyond the `try/except`.

### 2.6 Stale tree UX

- `mkdocs serve` and Docusaurus dev servers solve this with file-watching + WebSocket push reload. We've explicitly opted OUT of watcher/auto-refresh (qa.md), so we accept the staleness window.
- Established UX: when a click on the cached sidebar tree resolves to a now-missing file, return 404 with a body like `{"removed": true, "path": "..."}`; the frontend shows a small inline "this file no longer exists — refresh sidebar" affordance. This is the same pattern VS Code uses when an external delete races a tab open.

### 2.7 Not worth code in v1

- Symlink-cycle detection beyond `is_symlink()` refusal: dead code given our policy.
- Atomic-read shims (read-then-checksum-then-reread): solves a problem that costs the user a refresh.
- `chardet` / `cchardet`: dependency weight not justified for author-controlled markdown.
- Per-file MIME sniffing: only `.md`, `.yaml`, `.json`, `.jsonl` are surfaced — extension-based dispatch is sufficient. ([SecureFlag — file download patterns](https://knowledge-base.secureflag.com/vulnerabilities/unrestricted_file_download/unrestricted_file_download_python.html))

## 3. Implications for the spec (concrete)

### v1-required

1. **Sandboxed path resolver.** Single helper used by every API endpoint:
   ```
   def safe_resolve(user_rel: str, root: Path) -> Path
   ```
   that does: `candidate = (root / user_rel).resolve(strict=False)`, then `candidate.relative_to(root.resolve())` — `ValueError` ⇒ HTTP 400. Reject any `Path` whose lstat is a symlink before resolving.
2. **Whitelisted file extensions.** Read endpoint serves only `.md`, `.yaml`, `.yml`, `.json`, `.jsonl`. Anything else → 415.
3. **EAFP file reads.** Don't `os.path.exists`. `try: open()` with a single `except (FileNotFoundError, PermissionError, IsADirectoryError)` returning structured 404/403 JSON. No 500s on benign races.
4. **Binary-content reject.** After `read_text(encoding="utf-8", errors="replace")`, scan for `\x00`; if present, return 415 with `reason: "binary_content"`.
5. **No symlink follow.** During directory listing, if `entry.is_symlink()`, skip it (or surface as a leaf marked "symlink — not followed"). Do not call `resolve()` on it.
6. **Sidebar 404 contract.** API returns `{"error": "not_found", "kind": "file_removed" | "permission_denied" | "outside_sandbox"}`. Frontend shows a non-modal inline message and offers a "refresh sidebar" button.
7. **Size cap.** Refuse to read files >2 MB (well above the ≤500 KB scale target). Returns 413.

### Defer (out of scope for v1)

- File-watching / auto-refresh / WebSocket reload (qa.md confirmed out).
- ETag / If-Modified-Since: zero benefit at single-user scale.
- Encoding auto-detection via `chardet`: read as `utf-8` with `errors="replace"`; document the assumption.
- Symlink-cycle detection: refusal renders it moot.
- Atomic-read shim for torn writes: the user just refreshes.
- AC checks for race-window 404 specifically: covered transitively by the EAFP rule plus the not_found contract; no dedicated test.

## 4. Open questions

1. **Symlink policy — refuse silently or surface as a marked leaf?** Surfacing has discoverability value (the user sees something is there); silent refusal is simpler. Recommend marked leaf, but the spec must pick one.
2. **What does the API return for a directory whose name resolves outside the sandbox?** 400 `outside_sandbox` is clear, but should the frontend distinguish that from a generic 404 for UX clarity?
3. **JSONL files can grow boundlessly during a pipeline run** (the `events.jsonl` audit log). Even though we're surfacing only `specs/` (not `.audit/`) in v1, future expansion to audit views needs a streaming-read story. Note this as a known follow-up, not a v1 blocker.
4. **Should the path resolver call `.resolve()` once and cache the resolved sandbox root at startup, or per-request?** Per-request is safer if the cwd or the discovered root could change; once-at-startup is faster. Given walk-upward already caches the root, once-at-startup is consistent.
5. **Windows long-path (>260 chars) handling.** `pathlib` on modern Python + Windows 10+ generally works, but a deeply nested `findings/angle-*.md` on a long-named project could cross the limit. Probably fine at v1 scale; flag if the e2e suite hits it.

---

Sources:
- [Starlette CVE-2023-29159 advisory](https://github.com/Kludex/starlette/security/advisories/GHSA-v5gw-mw7f-84px)
- [Starlette PR #985 — robust path traversal check](https://github.com/encode/starlette/pull/985/files)
- [GitHub Advisory CVE-2023-29159](https://github.com/advisories/GHSA-v5gw-mw7f-84px)
- [OWASP Path Traversal](https://owasp.org/www-community/attacks/Path_Traversal)
- [Python pathlib docs](https://docs.python.org/3/library/pathlib.html)
- [OpenStack — Restrict path access to prevent path traversal](https://security.openstack.org/guidelines/dg_using-file-paths.html)
- [CPython #109187 — Path.resolve() symlink loops](https://github.com/python/cpython/issues/109187)
- [nginx disable_symlinks (O'Reilly excerpt)](https://www.oreilly.com/library/view/nginx-http-server/9781788623551/e1c22cbb-8229-4025-bff9-426c0086f41c.xhtml)
- [Plesk — Mitigating the symlinks vulnerability](https://docs.plesk.com/en-US/obsidian/administrator-guide/plesk-administration/securing-plesk/mitigating-the-symlinks-vulnerability.79045/)
- [Dufs README — symlink + readonly config](https://github.com/sigoden/dufs)
- [VS Code #98063 — atomic file save](https://github.com/microsoft/vscode/issues/98063)
- [VS Code #15111 — atomic save vs file watchers](https://github.com/Microsoft/vscode/issues/15111)
- [python-atomicwrites docs](https://python-atomicwrites.readthedocs.io/)
- [ActiveState recipe — atomic write](https://code.activestate.com/recipes/579097-safely-and-atomically-write-to-a-file/)
- [yapf #731 — race condition on file existence check](https://github.com/google/yapf/issues/731)
- [Python tracker — race when reading/writing pyc](https://bugs.python.org/issue210610)
- [chardet documentation — usage](https://chardet.readthedocs.io/en/latest/usage.html)
- [chardet — How it works](https://chardet.readthedocs.io/en/latest/how-it-works.html)
- [python-markdown library reference](https://python-markdown.github.io/reference/)
- [Git parallel-checkout documentation](https://git-scm.com/docs/parallel-checkout)
- [SecureFlag — Unrestricted file download (Python)](https://knowledge-base.secureflag.com/vulnerabilities/unrestricted_file_download/unrestricted_file_download_python.html)
- [FastAPI Static Files tutorial](https://fastapi.tiangolo.com/tutorial/static-files/)
- [Starlette StaticFiles docs](https://www.starlette.io/staticfiles/)
