# Filesystem read-only viewer risks (and the editing path)

spec_driven is a localhost FastAPI app that walks `specs/{task_type}/{task_name}/` per request, reads files via `GET /api/file?path=...`, and writes them back via `PUT /api/file`. Even bound to `127.0.0.1`, every request that takes a path from the client and resolves it against the filesystem is a path-traversal API. This dossier covers the seven failure modes the design has to survive: race conditions, path traversal, symlinks, encoding/binary detection, permissions, atomic-write semantics, and stale-tree UX. It closes with concrete recommendations for the `safe_resolve` helper, symlink policy, write path, error mapping, and size ceiling.

## 1. Path traversal — the case study is in our own dependency tree

FastAPI sits on Starlette, and Starlette's own `StaticFiles` shipped CVE-2023-29159 — a path-traversal bug that affected versions `>=0.13.5,<0.27.0`. The advisory is direct about the cause: `StaticFiles` validated the requested path against the configured directory using `os.path.commonprefix()`, which "works a character at a time, it does not treat the arguments as paths" ([Kludex/starlette GHSA-v5gw-mw7f-84px](https://github.com/Kludex/starlette/security/advisories/GHSA-v5gw-mw7f-84px), [NVD CVE-2023-29159](https://nvd.nist.gov/vuln/detail/CVE-2023-29159)). A request like `GET /static/../static1.txt` resolved to `./static1.txt`; `commonprefix(["./static1.txt", "./static"])` returns `./static`, which the check happily accepted as "inside the static dir." The fix was to switch to `os.path.commonpath()`, which compares path components rather than characters.

This bug is not unique. Seth Larson catalogues `os.path.commonprefix()` as a 35-year footgun and points at three more incarnations: pip's wheel-unpack path-traversal (CVE-2026-1703), dbt-common's `safe_extract` ([GitLab CVE-2026-29790](https://advisories.gitlab.com/pkg/pypi/dbt-common/CVE-2026-29790/)), and a Trellix-led mitigation campaign for the tarfile CVE-2007-4559 that propagated the same broken `is_within_directory()` to over 61,000 downstream pull requests ([Larson, "Deprecate confusing APIs like os.path.commonprefix()"](https://sethmlarson.dev/deprecate-confusing-apis-like-os-path-commonprefix)). The wrong-vs-right pattern is worth pinning to the wall:

```python
# WRONG — character-level, allows /tmp/packages/ vs /tmp/packagesevil/
prefix = os.path.commonprefix([abs_directory, abs_target])
return prefix == abs_directory

# RIGHT — component-level
return os.path.commonpath([abs_directory, abs_target]) == abs_directory
```

OWASP's own guidance does not name `commonpath` directly but lands at the same place: "validate the user's input by only accepting known good — do not sanitize the data," "surround the user-supplied path component with application-controlled path code," and "normalize the input before using in file IO APIs," with explicit pointers to `realpath()` (PHP), `Path.normalize()` (Java), and `Path.GetFullPath()` (.NET) as the canonicalization primitives ([OWASP Path Traversal](https://owasp.org/www-community/attacks/Path_Traversal)).

For Python the canonical primitive is `pathlib.Path.resolve()`, which the standard library docs describe as "Make the path absolute, resolving any symlinks. … `..` components are also eliminated (this is the only method to do so)" ([Python pathlib docs](https://docs.python.org/3/library/pathlib.html)). The companion check is `Path.is_relative_to(base)` or, when you need the suffix back, `Path.relative_to(base)`. Critically, **`is_relative_to` is string-based** — "this method is string-based; it neither accesses the filesystem nor treats `..` segments specially" — so it is only safe **after** `resolve()` has done the canonicalization. Salvatore Security's preventing-directory-traversal-in-Python writeup arrives at the same shape (`DOCUMENT_ROOT.resolve() not in requested_path.resolve().parents`) and flags the obvious caveat: `resolve()` follows symlinks, so the check is only as strong as your symlink policy ([Salvatore Security](https://salvatoresecurity.com/preventing-directory-traversal-vulnerabilities-in-python/)).

### Double-decode is the other classic miss

The OWASP double-encoding page is explicit that "by using double encoding it's possible to bypass security filters that only decode user input once" ([OWASP Double Encoding](https://owasp.org/www-community/Double_Encoding)), and CVE-2026-21726 in Grafana Loki is a current example: the original sanitiser decoded once and validated, the file-access layer decoded again, and `%252e%252e%252f` slipped through ([SentinelOne CVE-2026-21726](https://www.sentinelone.com/vulnerability-database/cve-2026-21726/)). FastAPI/Starlette already URL-decodes path and query arguments once before they reach the handler. As long as spec_driven's `safe_resolve` operates on the already-decoded string and **does not decode again**, the double-decode class is closed. Equally important: do not write your own ad-hoc decoder before validation. Take the string as Starlette hands it to you, feed it to `Path()`, then `resolve()`.

### `pathlib.Path.resolve(strict=False)` semantics — the read vs write asymmetry

The docs say "If a path doesn't exist or a symlink loop is encountered, and strict is True, OSError is raised. If strict is False, the path is resolved as far as possible and any remainder is appended without checking whether it exists" ([Python pathlib docs](https://docs.python.org/3/library/pathlib.html)). This matters for the editing path: `PUT /api/file` may target a file that does not exist yet (creating a new draft section). Using `resolve(strict=True)` would `FileNotFoundError` on every legitimate create; `resolve(strict=False)` resolves the parent that does exist and appends the trailing leaf — exactly what a "create-or-overwrite" handler needs. For the read path, `strict=True` is fine and gives you a clean 404 mapping for free.

## 2. Symlinks — the policy decision spec_driven cannot dodge

`resolve()` follows symlinks. If `specs/development/foo/findings/dossier.md` is a symlink to `/etc/passwd`, an authenticated `safe_resolve` based purely on `resolve() + is_relative_to(base)` returns `/etc/passwd` and `is_relative_to(specs/)` is False, so traversal is denied — but only because the link target falls outside. A symlink to `/Users/dalu/secrets/api_key.txt` placed inside the project tree by an attacker who already has write access to one subdirectory escapes the canonical base check the same way: the resolved target is outside, the check fails, the read is denied — only if and when `resolve()` actually walks the link. If we resolve **the parent** rather than the full path (a common mistake when you want `resolve(strict=False)` for the create case), a symlink at the leaf can let the underlying `open()` follow the link past the base.

The web-server world has settled on three knobs:

- **nginx `disable_symlinks`** has four modes: `off` (default — links allowed), `on` (deny if any path component is a link), `if_not_owner` (deny only when link and target have different owners — the SymLinksIfOwnerMatch behaviour), and `from=$prefix` (skip checking some leading prefix). It is implemented on top of `openat()` / `fstatat()` and is therefore "only available on systems that have the `openat()` and `fstatat()` interfaces … modern versions of FreeBSD, Linux, and Solaris" ([nginx docs](https://nginx.org/en/docs/http/ngx_http_core_module.html#disable_symlinks)). Notably it does not work on Windows.
- **Plesk** ships a "Restrict the ability to follow symbolic links" checkbox per subscription, layered on Apache's `SymLinksIfOwnerMatch` and nginx's `disable_symlinks`. Plesk's own docs flag that `SymLinksIfOwnerMatch` "leaves a time-of-check to time-of-use race condition vulnerability" and that deeper protection requires kernel-level mechanisms like CloudLinux SecureLinks or grsecurity ([Plesk symlinks vulnerability mitigation](https://docs.plesk.com/en-US/obsidian/administrator-guide/plesk-administration/securing-plesk/mitigating-the-symlinks-vulnerability.79045/)).
- **Dufs** (sigoden/dufs) defaults to **denying** symlink targets outside the served root and exposes `--allow-symlink` / `DUFS_ALLOW_SYMLINK=true` to opt in ([Dufs README](https://github.com/sigoden/dufs)).

For a localhost dev tool serving the user's own `specs/` tree, the simplest correct policy is **deny any path whose `resolve()` differs from its lexical normalisation** — i.e., reject if the resolved real path is not byte-identical to a non-following lexical normalisation that uses `os.path.normpath()` followed by `os.path.realpath()` and an equality check, **or** simpler, after `resolve()` re-check `is_relative_to(base.resolve())` *and* walk each parent and assert none of them is a symlink (`Path.is_symlink()`) when iterating from base downward. This matches Dufs's default and avoids the `if_not_owner` race that Plesk warns about.

## 3. Encoding and binary detection — do not MIME-sniff

The viewer needs to decide: is this file something we render in the editor (text + monospace), or an opaque binary we offer for download? The intuitive move is to MIME-sniff. The intuitive move is wrong.

The WHATWG MIME Sniffing Standard exists precisely because browsers historically disagreed on how to guess content types from bytes ([WHATWG MIME Sniffing](https://mimesniff.spec.whatwg.org/)), and MDN's media-types primer is blunt: "file extensions are not used to determine the supplied MIME type … because they are unreliable and easily spoofed" ([MDN MIME types](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/MIME_types)). Worse, charset sniffing has been used to **bypass** browser security (the canonical example: CSS / JSONP files reinterpreted as scripts via UTF-7 BOM injection — see Wikipedia's [Content sniffing](https://en.wikipedia.org/wiki/Content_sniffing) write-up).

`chardet` is more honest but still probabilistic. The FAQ says it "achieves 99.3% accuracy on its test suite," but also that "very short strings (under a few hundred bytes) may require additional data for reliable results" and that callers should "try `detect_all()` if the top result is wrong" ([chardet FAQ](https://chardet.readthedocs.io/en/latest/faq.html)). It returns `None` when "the data appears to be binary rather than text … contains null bytes or a high proportion of control characters." That last sentence is the actual signal we need.

The concrete, unambiguous binary check (no probabilistic step) the WHATWG spec uses is: **a byte is a "binary data byte" if it is in `0x00..0x08`, `0x0B`, `0x0E..0x1A`, or `0x1C..0x1F`** ([WHATWG MIME Sniffing §3](https://mimesniff.spec.whatwg.org/)). Read the first 4 KB; if any byte is in those ranges, treat it as binary, refuse to render in the editor, return a small JSON envelope `{is_binary: true, size: N}` plus a download link. For files that pass that check, default to UTF-8 decode and only fall back to chardet on `UnicodeDecodeError`. Do **not** use a Python `mimetypes.guess_type()` answer to drive editor vs download — that goes by extension and lies.

## 4. Permissions, EAFP, and the structured error envelope

Localhost-only does not mean "no errors." The user may rename a file in another tab, `chmod 000` it, or delete the parent. The CERT secure-coding rule for filesystem access is "FIO45-C: avoid TOCTOU race conditions" — checks (`os.path.exists`, `os.access`) before use are racy because the world can change between check and open ([CERT FIO45-C](https://wiki.sei.cmu.edu/confluence/display/c/FIO45-C.+Avoid+TOCTOU+race+conditions+while+accessing+files)). Apple's secure-coding guide makes the same point: the only reliable path is EAFP — "easier to ask forgiveness than permission" — try the operation and translate the OSError to the right HTTP code.

The mapping spec_driven should commit to:

| `OSError.errno` | HTTP | meaning |
| --- | --- | --- |
| `ENOENT` (2) | 404 | file or parent gone |
| `ENOTDIR` (20) | 404 | a path component is a regular file |
| `EISDIR` (21) | 400 | client asked for a file, target is a directory |
| `EACCES` (13), `EPERM` (1) | 403 | filesystem-level permission |
| `ELOOP` (40) | 400 | symlink loop (or our policy denied the link) |
| `ENAMETOOLONG` (36) | 414 | URI/path too long |
| `EXDEV` (18) | 500 | cross-device on the rename — internal bug |
| `ENOSPC` (28), `EDQUOT` (122) | 507 | disk full / quota |
| anything else | 500 | unexpected; log full traceback server-side |

Combined with a base-resolution failure (`safe_resolve` raising), which is its own 400 ("path escapes base"), this gives the frontend a small, finite vocabulary to render reasonably.

## 5. Atomic write — `tempfile.mkstemp` + `os.replace`

The standard idiom for crash-safe in-place file replacement in Python is:

1. `mkstemp(dir=target.parent)` — same directory so the rename stays on one filesystem.
2. Write payload to the temp fd, `os.fsync(fd)`, close.
3. `os.replace(temp_path, target)`.
4. On any exception, `os.unlink(temp_path)` to avoid temp-file litter.

[ActiveState recipe 579097](https://code.activestate.com/recipes/579097-safely-and-atomically-write-to-a-file/) and the [python-atomicwrites library](https://github.com/untitaker/python-atomicwrites) both codify this; the discuss.python.org thread "Adding atomicwrite in stdlib" ([discuss.python.org/t/adding-atomicwrite-in-stdlib/11899](https://discuss.python.org/t/adding-atomicwrite-in-stdlib/11899)) catalogues the same shape with the `fsync` step explicit. The `fsync` is the part most "atomic write" tutorials drop and the part that matters when the box loses power between the rename and the write hitting platters.

### POSIX vs Windows asymmetry

The big footgun: `os.replace`/`os.rename` is **not** uniformly atomic across platforms.

- **POSIX** `rename(2)` is atomic, including overwrite of an existing destination on the same filesystem ([POSIX rename](https://pubs.opengroup.org/onlinepubs/9699919799/functions/rename.html)).
- **Windows**: `os.replace` lowers to `MoveFileEx(MOVEFILE_REPLACE_EXISTING)`, which Microsoft's docs do **not** guarantee atomic. The golang-nuts thread "windows: ReplaceFile vs MoveFileEx" ([Google Groups](https://groups.google.com/g/golang-nuts/c/JFvnLx246uM)) and the LWN article "Atomic rename in Windows" ([lwn.net/Articles/682988](https://lwn.net/Articles/682988/)) both land on the same conclusion: `ReplaceFile()` is the closer match because its requirement that "the backup file, replaced file, and replacement file must all reside on the same volume" is what makes the operation atomic, and `SetFileInformationByHandle(..., FileRenameInfoEx, ..., FILE_RENAME_FLAG_POSIX_SEMANTICS)` is the modern way to get true POSIX-style replace on Windows 10+.
- The Python issue tracker has been aware of this since [bpo-8828 "Atomic function to rename a file"](https://bugs.python.org/issue8828); the `os.replace` docstring promises overwrite, not atomicity, on Windows.
- Cross-filesystem `rename` on POSIX returns `EXDEV` and `os.replace` does **not** fall back to copy+delete ([zetcode os.replace](https://zetcode.com/python/os-replace/)). Putting the temp file in the same directory as the target makes this irrelevant.

**Practical implication for spec_driven:** on Linux/macOS the `mkstemp + fsync + os.replace` pattern gives a strong "old file or new file, never half-written" guarantee. On Windows, the same code yields "almost always one or the other," and a hard power-loss in the middle of the rename can corrupt. For a localhost dev tool that's an acceptable failure mode — the user can `git diff` and re-save — but it should be documented, not silently assumed.

## 6. Stale-tree UX — what the sidebar should show

The sidebar lists the spec tree, the user clicks a file, the editor loads it. Between the listing and the click, the file may have been renamed, deleted, or had its permissions changed by another process (a `git checkout`, an editor save in IDE, the agent_team pipeline writing a new artifact). LWN's "Filesystem notification, part 2" ([LWN Articles/605128](https://lwn.net/Articles/605128/)) walks through the inotify race: "if you scan a directory adding watches for subdirectories first, then add a watch for the parent directory, and a new subdirectory is created between these two steps, no watch will be created for that directory." A web tool that pre-builds a tree snapshot and serves stale paths from it inherits the same race plus a network round-trip.

The cleanest design, and what the current spec calls for ("scans `specs/` per request"), avoids inotify entirely: every `GET /api/tree` call walks the filesystem fresh, and every `GET /api/file` resolves the path against the live filesystem. There is no cache to invalidate. The cost is one stat-walk per refresh; for a `specs/` tree of a few hundred files on local disk this is sub-10 ms and irrelevant. **Do not introduce a watcher.** It would add a layer of bugs (dropped events on macOS FSEvents under heavy churn, kqueue limits on BSD, polling fallback semantics on Windows) for a problem that does not exist.

For the per-file UX, the right shape is: editor open does a fresh GET; if the file has been modified since the version the client holds (compare `mtime_ns` returned in the GET response), refuse the next PUT with a 409 Conflict and surface "the file changed on disk — reload?" This is the `If-Unmodified-Since` pattern minus the HTTP-date precision loss.

## 7. The 2 MB ceiling

Even with all of the above right, an unbounded read is a memory-exhaustion vector. Symlink-protected, traversal-safe, atomic-write-correct — none of that helps if a curious user clicks `package-lock.json` (8 MB) and the response object stalls the browser. A hard ceiling at **2 MB** for both read and write: above that, return `413 Payload Too Large` on PUT and a `{is_binary: false, too_large: true, size: N}` envelope on GET so the frontend can show "file is too large to edit in the browser" with a download link. 2 MB covers every spec/markdown/yaml/json/python file the pipeline produces; anything bigger is by definition not a hand-edited artifact.

---

## Recommendations for spec_driven

1. **`safe_resolve(path: str, base: Path) -> Path`**: build with `Path((base / path).resolve(strict=False))`, then assert `resolved.is_relative_to(base.resolve())`. Use `resolve(strict=False)` so create-new-file works on the write path and let the subsequent `open()` raise `FileNotFoundError` (mapped to 404) when reading a non-existent path. Never use `os.path.commonprefix` and never mix in `os.path.commonpath` either — `pathlib.is_relative_to` is the component-aware check. Do not URL-decode the path again inside the helper; trust Starlette's single decode.

2. **Symlink policy: deny.** After `safe_resolve` produces the resolved path, walk parents from `base` to leaf and reject if any segment satisfies `Path.is_symlink()`. This matches Dufs's default and avoids the `SymLinksIfOwnerMatch` TOCTOU race Plesk warns about. Document this in the spec; if a user genuinely needs symlinks inside `specs/`, they must opt in via a config flag and accept the localhost-only risk.

3. **Atomic write via `tempfile.mkstemp` + `os.fsync` + `os.replace`**, with the temp file in the **same directory** as the target so the rename stays single-filesystem. Wrap in `try/except` that `os.unlink`s the temp on failure. Document that on Windows the atomicity is "best-effort" because `os.replace` lowers to `MoveFileEx`, not `ReplaceFile`/`FileRenameInfoEx`.

4. **EAFP read with structured 4xx mapping.** No `os.path.exists` or `os.access` pre-checks. `try: open(...)` and translate `OSError.errno` per the table in §4. Return `{error: {code: "ENOENT", http: 404, message: "..."}}`; never leak full server paths in the message — only the user-supplied relative path.

5. **Binary detection by null-byte scan**, not MIME sniffing and not chardet. Read first 4096 bytes; if any byte is in WHATWG's binary-byte set (`0x00..0x08`, `0x0B`, `0x0E..0x1A`, `0x1C..0x1F`), treat as binary, return `{is_binary: true}` with no body. For text files, attempt UTF-8 decode first; on `UnicodeDecodeError` retry with `latin-1` and flag `{encoding: "latin-1", lossy: true}` so the frontend can warn before the user accidentally normalises a non-UTF-8 file to UTF-8 on save.

6. **2 MB hard ceiling** on both GET and PUT. On GET, `os.path.getsize` first (cheap, one syscall) and return `{too_large: true, size: N}` rather than streaming. On PUT, check `Content-Length` and reject with 413 before reading the body.

7. **No filesystem watcher.** Every API call re-walks the relevant subtree. Return `mtime_ns` on every GET; require it back on PUT and 409 on mismatch — closes the lost-update window without a watcher's bugs.

8. **Single canonical resolver in `libs/safe_path.py`.** All four routes (`/api/tree`, `/api/file` GET, `/api/file` PUT, `/api/regen-prompt`) call it; no per-route ad-hoc string manipulation. Unit-test it against the OWASP/PortSwigger payload list (`../`, `..%2f`, `%252e%252e%252f`, `....//`, absolute paths, NUL bytes, Windows backslashes, symlink targets) and the Starlette CVE-2023-29159 reproducer specifically — `/static1.txt` against base `/static/` must be denied.

---

## Open questions / not researched

- Whether Windows-host users of spec_driven will hit the `ReplaceFile` vs `MoveFileEx` distinction in practice (we suspect not for hand-edits, but did not measure).
- Whether `aiofiles` adds atomicity guarantees on top of `os.replace` (the FastAPI ecosystem's default async file lib); we assumed not.
- Macro performance of "re-walk every request" for users with huge `projects/` trees alongside `specs/`. A polling cache (5-second TTL) might be needed at scale; not characterised.
- How `pathlib.Path.is_relative_to` behaves on Windows when one path is `C:\specs` and the other has been symlinked through a junction point — Windows reparse points are a separate animal from POSIX symlinks.
- Whether `chardet`'s `None`-on-binary signal is reliable enough to replace the explicit byte-range check, or whether the byte-range check is strictly superior (we recommended the latter conservatively).

## Sources

- [GHSA-v5gw-mw7f-84px — Starlette path-traversal in StaticFiles](https://github.com/Kludex/starlette/security/advisories/GHSA-v5gw-mw7f-84px)
- [NVD CVE-2023-29159](https://nvd.nist.gov/vuln/detail/CVE-2023-29159)
- [Snyk SNYK-PYTHON-STARLETTE-5538332](https://security.snyk.io/vuln/SNYK-PYTHON-STARLETTE-5538332)
- [Seth Larson, "Deprecate confusing APIs like os.path.commonprefix()"](https://sethmlarson.dev/deprecate-confusing-apis-like-os-path-commonprefix)
- [GitLab CVE-2026-29790 — dbt-common safe_extract](https://advisories.gitlab.com/pkg/pypi/dbt-common/CVE-2026-29790/)
- [OWASP Path Traversal](https://owasp.org/www-community/attacks/Path_Traversal)
- [OWASP Double Encoding](https://owasp.org/www-community/Double_Encoding)
- [PortSwigger Web Security Academy — file path traversal](https://portswigger.net/web-security/file-path-traversal)
- [SentinelOne CVE-2026-21726 (Grafana Loki double-decode)](https://www.sentinelone.com/vulnerability-database/cve-2026-21726/)
- [Python pathlib documentation](https://docs.python.org/3/library/pathlib.html)
- [Salvatore Security — Preventing Directory Traversal in Python](https://salvatoresecurity.com/preventing-directory-traversal-vulnerabilities-in-python/)
- [nginx disable_symlinks directive](https://nginx.org/en/docs/http/ngx_http_core_module.html#disable_symlinks)
- [Plesk — Mitigating the symlinks vulnerability](https://docs.plesk.com/en-US/obsidian/administrator-guide/plesk-administration/securing-plesk/mitigating-the-symlinks-vulnerability.79045/)
- [Dufs README — sigoden/dufs](https://github.com/sigoden/dufs)
- [WHATWG MIME Sniffing Standard](https://mimesniff.spec.whatwg.org/)
- [MDN — MIME types (HTTP)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/MIME_types)
- [Wikipedia — Content sniffing](https://en.wikipedia.org/wiki/Content_sniffing)
- [chardet FAQ](https://chardet.readthedocs.io/en/latest/faq.html)
- [CERT FIO45-C — Avoid TOCTOU races](https://wiki.sei.cmu.edu/confluence/display/c/FIO45-C.+Avoid+TOCTOU+race+conditions+while+accessing+files)
- [Apple Secure Coding Guide — Race Conditions and Secure File Operations](https://developer.apple.com/library/archive/documentation/Security/Conceptual/SecureCodingGuide/Articles/RaceConditions.html)
- [LWN — Filesystem notification, part 2 (inotify)](https://lwn.net/Articles/605128/)
- [LWN — Atomic rename in Windows](https://lwn.net/Articles/682988/)
- [golang-nuts — windows: ReplaceFile vs MoveFileEx](https://groups.google.com/g/golang-nuts/c/JFvnLx246uM)
- [bpo-8828 — Atomic function to rename a file](https://bugs.python.org/issue8828)
- [ActiveState recipe 579097 — Safely and atomically write to a file](https://code.activestate.com/recipes/579097-safely-and-atomically-write-to-a-file/)
- [python-atomicwrites](https://github.com/untitaker/python-atomicwrites)
- [discuss.python.org — Adding atomicwrite in stdlib](https://discuss.python.org/t/adding-atomicwrite-in-stdlib/11899)
- [zetcode — Python os.replace](https://zetcode.com/python/os-replace/)
- [POSIX rename(2)](https://pubs.opengroup.org/onlinepubs/9699919799/functions/rename.html)
