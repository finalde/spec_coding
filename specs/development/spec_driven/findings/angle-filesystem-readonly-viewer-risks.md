# Angle — filesystem viewer/editor risks

Stage 3 / Research — angle file.
Run: spec_driven-20260503-fullregen
Author: parent-spawned researcher-filesystem-risks (autonomous mode)
Inputs read: `user_input/revised_prompt.md`, `interview/qa.md`. Prior findings explicitly NOT read.

This angle covers the security and correctness considerations for a localhost-only FastAPI + React app that **reads and writes** plain files under a fixed sandbox root (the `spec_coding` repo). It treats the viewer/editor scope of `spec_driven` as the unit of analysis: an `exposed tree` of allow-listed paths, a body cap, a write whitelist of extensions, and a last-write-wins write contract.

Two design choices are locked by the interview and must be honored verbatim:

1. **Last-write-wins** on `PUT /api/file` — no `If-Match`/`If-Unmodified-Since`, no mtime guard, no 409 conflict path. The editor's buffer overwrites whatever is on disk.
2. **10 MB body cap** on both `GET /api/file` and `PUT /api/file` — the AC tests 10 MB exactly (200) and 10 MB + 1 byte (413).

The rest of this document examines what actually goes wrong with file-serving sandboxes, lines up the relevant comparators, then lands on 6 concrete recommendations.

---

## 1. Path traversal — the first thing every reviewer will look at

Path traversal (CWE-22, "dot-dot-slash", "directory climbing") is the single most common file-server bug. OWASP's community page describes it as a class of attacks where the attacker reads or writes files outside the intended directory by injecting `..`, absolute paths, encoded variants, or other path operators into a request that reaches a filesystem API. The OWASP-recommended primary defense is **avoid passing user-supplied input to filesystem APIs altogether** — and when that is impossible, validate the *resolved absolute path* against an allow-listed root rather than scanning the input string for `..`.

For `spec_driven` the user-supplied input is the path component of `GET/PUT /api/file?path=…`. The path *must* go to the filesystem, so OWASP's "avoid" rule cannot apply — the validation strategy has to be airtight.

### 1a. The Starlette comparator (CVE-2023-29159)

CVE-2023-29159 is the canonical recent example of a sandbox that *thought* it was safe and was not. Starlette's `StaticFiles` validated that a requested path was inside the configured root using `os.path.commonprefix([full_path, directory])`. With a directory `./static` and a request like `/static/../static1.txt`:

- `full_path` resolved to `./static1.txt` (sibling of `static`).
- `os.path.commonprefix(["./static1.txt", "./static"])` returned `"./static"` — a string-prefix match.
- Starlette concluded "in the directory" and served `./static1.txt`.

Affected: `>= 0.13.5, < 0.27.0`. Fix in 0.27.0: replace `commonprefix` with `os.path.commonpath`, which compares **path segments** rather than characters. This is a one-line change with very large blast radius — every Starlette/FastAPI-derivative app served unauthenticated file disclosure for two years.

### 1b. The `os.path.commonprefix` anti-pattern more broadly

Seth Larson's writeup ("Deprecate confusing APIs like `os.path.commonprefix()`") and the GitLab Advisory DB enumerate a non-trivial list of CVEs caused by the same mistake:

- **CVE-2026-1703 (pip)** — wheel-unpacking path traversal via an `is_within_directory()` helper built on `commonprefix`.
- **CVE-2026-29790 (dbt-common)** — same pattern, same outcome.
- **CVE-2026-35592 (pyload-ng)** — `_safe_extractall` checked tar entries with `commonprefix`; a sibling directory like `/tmp/packagesevil/` slips through when the target is `/tmp/packages`.
- **SecureDrop (2013)** — early example, traced to the same misuse.
- **The Trellix-campaign 2022 fixes** for CVE-2007-4559 — over 61,000 PRs across the ecosystem proposed an `is_within_directory()` helper using `commonprefix`, *propagating the bug*.

The takeaway is unambiguous: **never use `os.path.commonprefix` for security decisions.** Use `os.path.commonpath`, or — better for our stack — `pathlib.Path.is_relative_to(root)` after `Path.resolve()`. The viewer's path validator must avoid both `commonprefix` and naive substring/`startswith` checks, both of which fail for `./root` vs `./rootevil`.

### 1c. Other anti-patterns to avoid

- **Double-decoding.** A request handler that URL-decodes once at the framework boundary and then again inside the file route can let `%252e%252e%252f` through. FastAPI/Starlette decode once; the viewer code must not decode again. Reject paths that contain `%` after framework decoding — they have no legitimate use here.
- **Whitelisting "safe characters" instead of resolving.** Banning `..` is brittle: encoded variants (`%2e%2e`, `%c0%ae`, NULL injection `..%00`), Windows alternate separators (`\..\`), and Unicode normalization tricks all bypass character-class filters. The only robust check is "resolve to an absolute path, then verify it's inside the root." This is the OWASP-blessed form for languages that have a `realpath` equivalent.
- **MIME sniffing for routing decisions.** Content-sniffing (browsers' fallback when `Content-Type` is missing or wrong) is a known XSS vector, mitigated by `X-Content-Type-Options: nosniff`. The viewer should set that header on every response. More importantly, the viewer **must not** decide what to render based on sniffing the file's bytes — extension-based dispatch (`.md` → markdown, `.json` → highlighted, `.yaml` → highlighted) is both safer and matches the user's expectations. Sniffing was historically the source of a long tail of "renders a `.txt` as HTML and runs script" bugs.

---

## 2. Symlinks — the second thing every reviewer will look at

Symlinks are how path validation that "looked correct" gets bypassed. The classic move: an attacker (or a careless developer) creates a symlink inside the root that points outside it; a naive validator sees the link is under the root and serves whatever it points to. This is the reason production file servers ship dedicated symlink controls.

### 2a. nginx `disable_symlinks`

nginx's `disable_symlinks` directive is the comparator most relevant to `spec_driven`'s threat model. Three values:

- `off` (default) — follow symlinks freely.
- `on` — return 403 if **any component** of the requested URI is a symlink.
- `if_not_owner` — 403 only if the link and its target have different owners (shared-hosting model).

It also takes a `from=` parameter to skip the check for a leading prefix. nginx documents that this directive is only available on systems with `openat()` and `fstatat()` (modern Linux/FreeBSD/Solaris) — Windows lacks this support and the directive is a no-op there per ticket #637. The lesson: symlink checks need atomic openat-style primitives to be race-free, and Windows simply doesn't offer the same surface.

### 2b. Dufs `--allow-symlink` and Plesk

Dufs (sigoden/dufs), a popular small file server, takes the opposite default: symlinks outside the root are **disallowed unless** `--allow-symlink` (or `DUFS_ALLOW_SYMLINK=true`) is set. Same reasoning, opposite knob orientation — and it's defaulted safe.

Plesk's "Restricting the Ability to Follow Symbolic Links" KB documents the equivalent for both Apache (`SymlinksIfOwnerMatch`) and nginx (`disable_symlinks if_not_owner`), framed as a hardening step on shared hosting where multiple users share a filesystem. The `if_not_owner` mode is the explicit answer to symlink-as-privilege-escalation between tenants.

### 2c. Why `pathlib.Path.resolve()` + `is_relative_to` is enough for our threat model

`spec_driven` runs as a **single user, on localhost**, against the user's own checkout. The threat model is not "malicious tenant tries to escape jail"; it's "developer's tooling accidentally writes outside the repo, or follows a stray symlink and serves something the user did not realize was exposed." That maps cleanly to a Python-side check:

```python
def safe_resolve(repo_root: Path, request_path: str) -> Path:
    candidate = (repo_root / request_path).resolve(strict=False)
    if not candidate.is_relative_to(repo_root.resolve(strict=True)):
        raise HTTPException(status_code=403, detail="path outside repo")
    return candidate
```

`Path.resolve()` follows symlinks and canonicalizes `..`. `is_relative_to` (Python 3.9+) does the segment-aware containment check that `commonprefix` does not. This combination is the OWASP-recommended approach in Python form, and it's what the FastAPI ecosystem moved to after Starlette CVE-2023-29159.

Caveats worth recording in the spec:

- **Symlink loops.** CPython issue #109187 documents that `resolve()` historically mishandles symlink loops. Modern Python raises `OSError`; we should let that propagate as 500 rather than catch-and-retry.
- **`strict=False` quirk.** When the path doesn't exist, `resolve(strict=False)` resolves what it can and tacks the rest on without symlink-checking the missing components. For `PUT /api/file` against a nonexistent path that's fine — we already reject creation per the interview ("edit existing only"). For paranoid hardening, resolve the parent with `strict=True` and append the basename.
- **Windows case sensitivity.** NTFS is case-insensitive by default. `Path.resolve()` returns the canonical case for paths that exist; for comparison, casefold both sides on Windows or rely on `Path.is_relative_to` which uses the platform-native comparator.
- **Non-availability of `openat` on Windows.** We accept the Python-level race window (TOCTOU) — see §3 — because the threat model does not include a hostile process on the same box. nginx ticket #637 is the documented prior art that says Windows simply cannot offer the same race-free guarantee.

### 2d. Symlink policy for the viewer

Match nginx's `disable_symlinks on` posture: **if any component of the resolved path is a symlink, refuse with 403.** Implementation: walk parts after `resolve()` and check `Path.is_symlink()` on each ancestor up to the repo root, OR reject if `path.resolve() != path.absolute()` (a coarser but simpler check). The repo `spec_coding` is unlikely to contain intentional symlinks; the cost of the strict policy is near zero and the value is bypass resistance.

---

## 3. Race conditions — TOCTOU on read, on write, and on the tree walker

TOCTOU (Time-of-Check / Time-of-Use, CWE-367) is the bug pattern where a program checks a property of a filesystem object at time T and acts on it at time T+ε, and the property changes in between. Classic web example: a download endpoint validates that the requested filename resolves into the allowed directory, then opens the file by name; an attacker swaps a symlink between the check and the open. Wikipedia and the CERT "FIO45-C" page enumerate this class; PortSwigger's race-conditions academy adapts it to web settings.

For `spec_driven` the relevant TOCTOUs are:

1. **Path validation race.** `safe_resolve` returns a `Path`, but we then open by name in a separate syscall. A concurrent symlink swap could mean the validated path and the opened file diverge. **Mitigation in our threat model: accept the race window**, document it, and rely on the symlink-rejection policy to make the exploitable variant trivially small. The user is the only writer to the repo; nginx would tell us to use `openat` here, and Python doesn't expose that conveniently. (CPython has `os.open` with `O_NOFOLLOW`, which could be added if a stronger guarantee is wanted.)
2. **Editor vs CLI race on writes.** Two writers overlapping: the user's browser editor `PUT /api/file` and the user's terminal `vim`. The interview locks the resolution: **last-write-wins, no 409, no mtime guard.** That moves the conflict-detection burden to the user (it's their hand on both keyboards) and removes a whole class of false-positive 409s that would have shown up because the page sat open for an hour.
3. **Stale tree UX.** Sidebar fetches `/api/tree` once at load. The user creates a file in another shell. The sidebar still shows the old tree. This is a freshness issue, not a race; the spec's interview answer ("Empty state + regen panel mounted" for missing files) implicitly handles part of it. We should add: a manual refresh control on the sidebar, and re-fetch on focus / on every navigation.
4. **Stale buffer on open.** A user opens a file, walks away, comes back, the file changed on disk. They Save and overwrite. By design (interview answer): **this is fine.** That's what last-write-wins means. The dot/asterisk dirty indicator and the "warn on nav while dirty" pattern (interview answer) cover the user-error case where they forgot they were dirty; they do not cover external concurrent edits, and **by design we are not covering external concurrent edits.**

The general defense pattern from CERT FIO45-C is **EAFP not LBYL** — "easier to ask forgiveness than permission." Don't `os.path.exists()` then `open()`; just `open()` and catch `FileNotFoundError` / `PermissionError` / `IsADirectoryError`, mapping each to a structured 4xx. This is the Python-idiomatic form anyway and removes the inner race.

---

## 4. Atomic-write semantics for the editor

The write path needs to be **atomic** in the sense that another reader (the user's editor in another tab, or a CLI process, or the sidebar walker) never sees a half-written file. The standard pattern, well-documented in `tempfile` docs, the Python `os.replace` ZetCode guide, the python-atomicwrites library, and Alex Chan's "Atomic, cross-filesystem moves in Python":

```python
fd, tmp = tempfile.mkstemp(dir=target.parent, prefix=f".{target.name}.", suffix=".tmp")
try:
    with os.fdopen(fd, "wb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, target)
except Exception:
    Path(tmp).unlink(missing_ok=True)
    raise
```

Three points that often go wrong:

1. **Same directory for the tempfile.** `os.replace` is only atomic on the same filesystem. `tempfile.mkstemp(dir=target.parent, …)` guarantees that.
2. **Close the fd before `os.replace` on Windows.** A common mistake is leaving the temp file open and then renaming — fails with `PermissionError` on Windows because of share-mode locking. Using `os.fdopen` inside a `with` block closes it deterministically.
3. **`os.fsync` before `os.replace`.** On crash, you want either the old contents or the new contents — never partial. `fsync` on the temp + atomic rename gives that on POSIX.

### 4a. POSIX rename vs Windows MoveFileEx

`os.replace` is `rename(2)` on POSIX and `MoveFileEx` (with `MOVEFILE_REPLACE_EXISTING`) on Windows. POSIX `rename(2)` is atomic across the metadata layer; the destination either points at the old inode or the new one, never at a partially-written file. Windows is messier:

- LWN's "Atomic rename in Windows" (2016) and the Go issue #8914 ("os: make Rename atomic on Windows") both note that `MoveFileEx` is **not strictly atomic**: NTFS may have to free the destination's allocation, and very large files can exceed a single transaction, leading to a window where both source and target exist with the target partially truncated on crash.
- Windows 10 build 1601+ added `FileRenameInfoEx` with `FILE_RENAME_FLAG_POSIX_SEMANTICS`, which gives proper atomic semantics. Rust's stdlib (`std::fs::rename`, PR #131072) uses this when available and falls back to `FileRenameInfo`/`MoveFileEx` otherwise.
- Python's `os.replace` does NOT use `FileRenameInfoEx` as of CPython 3.13 — it uses `MoveFileEx` with replace-existing.

For `spec_driven` the practical impact is bounded: max body 10 MB, single-disk write, modern NTFS. Crash-during-rename leaving a half-truncated target is theoretically possible on Windows but vanishingly rare for files at this size. We accept the residual risk and document that `os.replace` is "atomic enough" for this single-user localhost editor; if a future user reports a crash with half-truncated files, switching to `python-atomicwrites` (which handles fsync, permissions, and the Windows nuances) is a one-line dependency add.

### 4b. Permissions on the new file

`tempfile.mkstemp` creates files with mode `0600` by default, which is **stricter than the user's umask** for the original file. On `os.replace`, the new file inherits that mode and the original mode is lost. Two options:

- Capture `target.stat().st_mode` before write, `os.chmod(tmp, mode)` before `os.replace`. Preserves Unix permissions correctly.
- On Windows it doesn't matter — ACLs are inherited from the parent, not the source file.

For markdown/JSON/YAML files in a developer's repo this is usually a no-op, but the spec should call it out so reviewers don't ask.

---

## 5. Encoding and binary detection

The exposed-tree extension whitelist (`.md, .yaml, .yml, .json, .jsonl, .txt`) is the strongest gate here. All six are textual; binary detection is a defense-in-depth concern, not a primary control.

### 5a. UTF-8 default, with BOM tolerance

Modern Python (3.x) opens text files with `open(path, encoding='utf-8')` cleanly. The wrinkles:

- **UTF-8 BOM (EF BB BF).** A non-trivial number of Windows tools (Notepad, older PowerShell, older VS) write UTF-8 with BOM. `encoding='utf-8'` will pass the BOM through as a literal `﻿` character at file start, which round-trips into the editor and back. Use `encoding='utf-8-sig'` for reads (strips the BOM if present) and `encoding='utf-8'` for writes (does not add one). Per chardet's docs and the BOM Wikipedia entry, BOM detection is the very first stage in any encoding-detection pipeline because it's deterministic.
- **UTF-16.** PowerShell 5.1's default `Out-File` is UTF-16 LE with BOM (per the project's `CLAUDE.md` note). If the user has any tool in the chain that emits UTF-16, opening with `utf-8` raises `UnicodeDecodeError`. We should: try `utf-8-sig` first, fall back to detecting `\xff\xfe` / `\xfe\xff` and reading `utf-16`, otherwise reject with 415.
- **Non-text bytes.** If a `.md` file somehow contains nulls or invalid UTF-8 sequences, treat it as binary and refuse to render. The chardet-recommended heuristic is "presence of null bytes ⇒ binary" plus "high proportion of control chars ⇒ binary." `binaryornot` packages this in pure Python.

We do *not* need `chardet` as a dependency — the whitelist plus `utf-8-sig` plus an explicit rejection on `UnicodeDecodeError` handles every realistic case.

### 5b. CRLF vs LF round-trip

Markdown and YAML round-trips through a textarea on a browser running on Windows can introduce `\r\n` where the original file had `\n`, causing every save to look like a giant whitespace diff to git. Two stable resolutions:

- Server-side: normalize EOL to the file's existing convention on write (sniff from the original; default LF if empty).
- Client-side: have the editor normalize on submit.

Recommending server-side normalization because it's the more durable layer and there's only one server.

---

## 6. The 10 MB body cap (locked)

The cap applies to both `GET /api/file` (response body) and `PUT /api/file` (request body). Locked at 10 MB. Implementation notes:

- FastAPI/Starlette doesn't enforce request size by default. Apply `Content-Length` check on `PUT` *before* reading the body; reject 413 if missing or > 10 MB. For chunked uploads, count bytes as they stream and abort early.
- For `GET` the cap is `target.stat().st_size > 10*1024*1024` ⇒ 413.
- The interview AC tests **10 MB exactly = 200, 10 MB + 1 byte = 413**. That's `<=` semantics, not `<`. The spec must encode this exactly.

The cap is generous for our use case (markdown is rarely > 1 MB; JSON dossiers might reach low single MB) and exists primarily to prevent OOM if a user accidentally points the editor at a 4 GB log file via a follow-up that leaks a path.

---

## 7. Last-write-wins write contract — the load-bearing decision

The user's pin: `PUT /api/file` always overwrites, no `If-Match`, no mtime guard, no 409. This is the unusual choice and worth justifying explicitly because reviewers will challenge it.

**Why it's correct here:**

1. **Single user, localhost.** No simultaneous remote actors. The "concurrent writer" is the same human at the same desk.
2. **Cost of the conflict UX is high.** mtime/ETag-guarded PUTs require a 409 path, a "reload?" modal, a merge UX, or a force-overwrite affordance. All of those add code and decision points to a tool whose virtue is being a thin window onto plain files.
3. **The detection benefit is small.** mtime guards catch the case where the file changed under the editor — but the user is the one who changed it. They will either remember (and accept the overwrite) or not (and the dirty-indicator/warn-on-nav UX from the interview already nags them when the *editor* has unsaved changes).
4. **Git is the durable conflict layer.** Every file under `specs/` is committed. If the editor stomps on a CLI edit, `git diff` and `git reflog` are one command away. The viewer/editor doesn't need to reinvent CAS on top.
5. **Validation is testable.** The interview's AC explicitly says: concurrent CLI writes during an editor session do NOT trigger 409; the final-write-wins outcome is the editor's buffer. That's a one-line `assert response.status_code == 200`.

The justification belongs in the final spec under the FR for `PUT /api/file` and again in `validation/security.md` so it doesn't get re-litigated by future readers.

---

## 8. Recommendations (action items for stages 4 + 5 + 6)

1. **`safe_resolve(repo_root, request_path)` helper.** `Path.resolve(strict=False)` then `is_relative_to(root.resolve(strict=True))`. Reject with 403 on miss. Rejects null bytes (`\0`), drive letters mid-path, and absolute inputs (`Path("/etc/passwd")` makes `(root / "/etc/passwd")` collapse to `/etc/passwd`, which `is_relative_to` correctly fails). Unit-tested with: `..` / `%2e%2e` / `/etc/passwd` / `c:\windows\system32` / `root_evil` / `..%00something` / a symlink that points outside.
2. **Symlink policy: refuse if any path component is a symlink.** Match nginx `disable_symlinks on`. Implementation: walk `path.parents` from the candidate up to `repo_root`, `is_symlink()` on each; or check `path.resolve() == path.absolute().resolve(strict=False)` after canonicalization. Document in `security.md` that this is a stricter posture than nginx's default-off and a strict-er one than Dufs's default (which allows internal symlinks).
3. **Atomic write via `tempfile.mkstemp(dir=target.parent) + os.fsync + os.replace`.** Preserve the original file's mode via `os.chmod(tmp, original_stat.st_mode)` before `os.replace`. Document the Windows non-strict-atomicity caveat (`MoveFileEx` semantics; LWN/Go-issue-8914) and the optional `python-atomicwrites` upgrade path.
4. **EAFP read with structured 4xx.** `try: open(...)` catching `FileNotFoundError → 404`, `PermissionError → 403`, `IsADirectoryError → 400`, `UnicodeDecodeError → 415`. No pre-check `os.path.exists()` — eliminates an inner TOCTOU per CERT FIO45-C and matches the Pythonic idiom.
5. **10 MB cap, enforced both directions, AC at the boundary.** `Content-Length` precheck on `PUT` (reject before reading body); `st_size` check on `GET`. AC tests: 10 MB body → 200; 10 MB + 1 byte → 413.
6. **Last-write-wins, justified explicitly.** No `If-Match`, no mtime header on response, no 409 path. Spec FR notes the rationale (single user / localhost / git is the conflict layer). Validation security doc includes the explicit test: concurrent CLI write during editor session, editor Save returns 200 and the editor buffer wins.
7. **`X-Content-Type-Options: nosniff` + extension-based dispatch on the frontend.** Never sniff bytes to decide rendering; always switch on extension. Reject any extension outside the whitelist (`.md`, `.yaml`, `.yml`, `.json`, `.jsonl`, `.txt`) with 415. This is the cheap defense against the "render markdown as HTML and run `<script>`" class of bug if the markdown renderer ever sanitizes incompletely.
8. **UTF-8-sig on read, UTF-8 (no BOM) on write, EOL preservation server-side.** Tolerates BOM-prefixed files from Windows tooling without round-tripping the BOM into a noisy diff. Detect file's existing line-ending convention and preserve on write so editor saves don't add CRLF noise on Windows.

---

## Sources

- [Starlette has Path Traversal vulnerability in StaticFiles · CVE-2023-29159 · GitHub Advisory Database](https://github.com/advisories/GHSA-v5gw-mw7f-84px)
- [CVE-2023-29159 Detail — NVD](https://nvd.nist.gov/vuln/detail/CVE-2023-29159)
- [Path Traversal · OWASP Foundation](https://owasp.org/www-community/attacks/Path_Traversal)
- [What is path traversal, and how to prevent it? · PortSwigger Web Security Academy](https://portswigger.net/web-security/file-path-traversal)
- [Deprecate confusing APIs like "os.path.commonprefix()" — Seth M. Larson](https://sethmlarson.dev/deprecate-confusing-apis-like-os-path-commonprefix)
- [dbt-common's commonprefix() doesn't protect against path traversal — GitLab Advisory Database (CVE-2026-29790)](https://advisories.gitlab.com/pkg/pypi/dbt-common/CVE-2026-29790/)
- [pyload-ng UnTar._safe_extractall commonprefix bypass — GitLab Advisory Database (CVE-2026-35592)](https://advisories.gitlab.com/pkg/pypi/pyload-ng/CVE-2026-35592/)
- [pathlib — Object-oriented filesystem paths · Python docs](https://docs.python.org/3/library/pathlib.html)
- [pathlib.Path.resolve() mishandles symlink loops · CPython issue #109187](https://github.com/python/cpython/issues/109187)
- [nginx `disable_symlinks` — O'Reilly excerpt, Nginx HTTP Server, Fourth Edition](https://www.oreilly.com/library/view/nginx-http-server/9781788623551/e1c22cbb-8229-4025-bff9-426c0086f41c.xhtml)
- [nginx ticket #637 — `disable_symlinks` doesn't work on Windows](https://trac.nginx.org/nginx/ticket/637)
- [Apache and Nginx Settings — Restricting the Ability to Follow Symbolic Links · Plesk KB](https://www.plesk.com/kb/docs/apache-and-nginx-settings-restricting-the-ability-to-follow-symbolic-links-2/)
- [sigoden/dufs — README & flags (`--allow-symlink`)](https://github.com/sigoden/dufs)
- [Time-of-check to time-of-use — Wikipedia](https://en.wikipedia.org/wiki/Time-of-check_to_time-of-use)
- [CWE-367: Time-of-check Time-of-use (TOCTOU) Race Condition](https://cwe.mitre.org/data/definitions/367.html)
- [FIO45-C. Avoid TOCTOU race conditions while accessing files · CERT Secure Coding](https://wiki.sei.cmu.edu/confluence/display/c/FIO45-C.+Avoid+TOCTOU+race+conditions+while+accessing+files)
- [Race conditions · PortSwigger Web Security Academy](https://portswigger.net/web-security/race-conditions)
- [tempfile — Generate temporary files and directories · Python docs](https://docs.python.org/3/library/tempfile.html)
- [Python `os.replace` Function — ZetCode](https://zetcode.com/python/os-replace/)
- [Atomic, cross-filesystem moves in Python — Alex Chan](https://alexwlchan.net/2019/atomic-cross-filesystem-moves-in-python/)
- [python-atomicwrites](https://github.com/untitaker/python-atomicwrites)
- [os: make Rename atomic on Windows · Go issue #8914](https://github.com/golang/go/issues/8914)
- [Atomic rename in Windows · LWN.net](https://lwn.net/Articles/682988/)
- [Win: Use POSIX rename semantics for `std::fs::rename` if available · Rust PR #131072](https://github.com/rust-lang/rust/pull/131072)
- [MIME type verification · MDN Web Docs — Practical implementation guides](https://developer.mozilla.org/en-US/docs/Web/Security/Practical_implementation_guides/MIME_types)
- [Exploiting MIME Sniffing · Beyond XSS](https://aszx87410.github.io/beyond-xss/en/ch5/mime-sniffing/)
- [chardet — How It Works (BOM detection, UTF-8 validation, binary detection)](https://chardet.readthedocs.io/en/latest/how-it-works.html)
- [Byte order mark — Wikipedia](https://en.wikipedia.org/wiki/Byte_order_mark)
- [binaryornot — pure Python binary-vs-text detection](https://github.com/audreyfeldroy/binaryornot/blob/master/binaryornot/helpers.py)

---

## Open questions / not researched

- **Windows `FileRenameInfoEx` adoption in CPython.** Whether a future CPython release will switch `os.replace` to use `FILE_RENAME_FLAG_POSIX_SEMANTICS` (matching what Rust did in PR #131072) was not researched. If/when it does, the Windows non-strict-atomicity caveat in §4a can be dropped.
- **`O_NOFOLLOW` / `openat` ergonomics in Python.** A stricter symlink-race posture than `Path.resolve()` exists via `os.open(O_NOFOLLOW)` plus a directory-fd-anchored open, but the ergonomic and cross-platform cost wasn't surveyed. Acceptable for our threat model; revisit if a multi-user or remote scenario emerges.
- **Browser-side guard on file size before upload.** The 10 MB cap is server-enforced; whether the editor should also pre-check via `Blob.size` and refuse early was not researched (UX call, not a security one).
- **Diff/merge UI for last-write-wins escape hatch.** Whether a future "the file changed under you, here's a diff before you save" non-blocking notice would add value (without becoming a 409) is out of scope for this angle; it would be a UX research angle, not a security one.
- **CSRF / same-origin posture.** The localhost-only model implies same-origin, but whether the API needs explicit CSRF tokens or `SameSite=Strict` cookies for the editor was not researched here — covered in a separate angle (browser-attack-surface) if one is run.
