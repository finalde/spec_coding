# Unit tests — `spec_driven`

Run: `spec_driven-20260503-145859` (level-specialist-03-unit, parent-direct stage 5).

This file enumerates **descriptions** of unit tests, not source code. Each test follows the shape `**N.M** test_name — inputs, expected, edge cases`. Severity for any failure follows the matrix in `validation/strategy.md` and `agent_refs/validation/development.md`. Tests originating from a numbered "Required validation move" cite that move inline (e.g., `[move 2]`).

**Targets covered:**

- Backend libs: `safe_resolve`, `file_reader`, `file_writer`, `tree_walker`, `api_security`, `regen_prompt`, `promotions`, plus the `api` route surface (negative-status checks).
- Frontend libs/components: `qaParser`, `linkResolver`, `QaErrorBoundary`, `autonomousMode` + `localStorage` cross-tab.

**Targets NOT covered here (handled in other validation modules):**

- Whole-flow user journeys → `system_tests.md` / `bdd_scenarios.md`.
- Origin/Host real-Vite-proxy crossing → `system_tests.md` (e2e profile per `[move 1]`).
- Boot smoke → `system_tests.md` (`boot_smoke` work unit per `[move 4]`).
- WCAG color contrast / focus / motion → `accessibility.md` (manual walkthrough per `[move 7]`).
- Performance budgets (NFR-1..3) → `performance.md`.
- Security probe set (path traversal HTTP fuzz, XSS payloads) → `security.md`. (Group 1 below covers the **library-level** sandbox checks; the HTTP-level fuzz lives in `security.md`.)

**Cross-platform note:** Mark POSIX-only tests with `pytest.mark.skipif(sys.platform == "win32", reason="POSIX symlink semantics")` per `[move 5]`. Never silently skip; always supply a reason.

---

## Group 1 — `safe_resolve` / path sandbox

Module: `projects/spec_driven/backend/libs/safe_resolve.py`. Surface under test: the function (or class method) that takes a user-supplied relative path string and either returns an absolute `Path` inside `EXPOSED_TREE` or raises a sandbox-violation error that the API layer translates to a single 404. Spec anchors: FR-2, FR-4, NFR-5, NFR-10, NFR-11, NFR-12.

**Severity rule:** any test in this group failing is a `critical` (path traversal / sandbox escape per general.md severity table). No revision rounds without explicit user approval.

### 1.1 test_resolves_known_good_relative_path
- Inputs: `"CLAUDE.md"`, `"specs/development/spec_driven/final_specs/spec.md"`.
- Expected: returns an absolute `Path`; `path.is_file()` is true; the resolved path's `parents` chain contains `repo_root`.
- Edge cases: forward slashes only; mixed-case (NTFS preserves but resolves case-insensitively — we accept the resolved canonical form).

### 1.2 test_rejects_dotdot_traversal
- Inputs: `"../etc/passwd"`, `"specs/../../../etc/passwd"`, `"./../../something"`.
- Expected: raises sandbox error (the API translates to 404).
- Edge cases: trailing `/..`, embedded `/.././`, single-segment `..`.

### 1.3 test_rejects_percent_encoded_traversal
- Inputs: `"%2e%2e/etc/passwd"`, `"%2E%2E%2Fetc"`, `"specs%2F..%2F.."`.
- Expected: rejected. The resolver MUST treat percent-encoding as opaque (the API layer is responsible for URL decoding once; double-decoding is the bug we are guarding against).
- Edge cases: mixed-case percent (`%2E` vs `%2e`), already-decoded vs raw.

### 1.4 test_rejects_alternate_data_streams
- Inputs: `"CLAUDE.md:hidden"`, `"CLAUDE.md::$DATA"`, `"specs/foo.md:Zone.Identifier"`.
- Expected: rejected (literal `:` in the relative segment is forbidden per NFR-12 Vite CVE-2025-62522 mitigation).
- Edge cases: drive-letter colon at index 1 only acceptable for absolute paths the resolver constructs internally — never accepted from user input.

### 1.5 test_rejects_windows_reserved_names
- Inputs: `"CON"`, `"PRN.md"`, `"specs/COM1.txt"`, `"AUX"`, `"NUL"`, `"LPT3"`.
- Expected: rejected. Reserved names route to devices on Windows even with extensions.
- Edge cases: case variations (`con`, `Con`, `CON`); reserved name as a directory segment vs the leaf.

### 1.6 test_rejects_windows_8_3_short_names
- Inputs: `"PROGRA~1"`, `"DOCUME~1/foo"`, `"VERY~1.MD"`.
- Expected: rejected (8.3 short-name aliasing is a known sandbox-escape via case/length normalization).
- Edge cases: tilde + digit pattern; tilde without digit (allow — common in Linux usernames inside paths) — assert the rejection regex is anchored on `~\d`.

### 1.7 test_rejects_vite_cve_2025_62522_trailing_backslash [NFR-12]
- Inputs: `"CLAUDE.md\\"`, `"specs\\..\\.."`, `"foo\\bar.md"`, `"\x00CLAUDE.md"` (NUL byte), `"foo:bar.md"`.
- Expected: rejected before any `realpath` call.
- Edge cases: literal `\` anywhere (we never accept backslashes from user input — frontend always sends forward slashes); NUL byte at any position; literal `:` in any non-drive position.

### 1.8 test_rejects_symlink_paths [move 5, NFR-10]
- Inputs: a fixture symlink under `specs/` pointing outside `EXPOSED_TREE` (test setup creates one on Linux, skipped on Windows without Developer Mode).
- Expected: rejected outright (refuse, no realpath leak).
- Skip marker: `pytest.mark.skipif(sys.platform == "win32" and not has_developer_mode(), reason="POSIX symlinks require Developer Mode on NTFS")`.

### 1.9 test_rejects_windows_junctions
- Inputs: a fixture NTFS junction created with `mklink /J`.
- Expected: rejected (treated like a symlink — refuse outright per NFR-10).
- Skip marker: `pytest.mark.skipif(sys.platform != "win32", reason="NTFS junction syntax")`.

### 1.10 test_collapses_outside_tree_to_single_404_signal
- Inputs: `"/etc/passwd"`, `"C:\\Windows\\System32\\drivers\\etc\\hosts"`, `"~/secret"`, `"node_modules/foo"`.
- Expected: rejected with the SAME error class regardless of *why* (no "exists but outside" vs "doesn't exist" distinction). Existence oracle is a side-channel the API gate explicitly closes per NFR-11.
- Edge cases: a path that is both outside-tree AND missing — still single signal.

### 1.11 test_accepts_uppercase_extension
- Inputs: `"specs/foo.MD"`, `"specs/foo.JSON"`.
- Expected: resolved successfully (extension allowlist is case-insensitive). The extension allowlist gate sits in `file_reader` / `file_writer`, but `safe_resolve` itself MUST not strip extensions.

### 1.12 test_rejects_mixed_slashes_in_user_input
- Inputs: `"specs\\foo/bar.md"`, `"specs/foo\\bar.md"`.
- Expected: rejected (mixed slashes are a normalization-confusion vector). User input MUST be pure forward-slash.

### 1.13 test_uniform_error_class_no_path_leak
- Inputs: a missing-but-inside-tree path AND a valid-but-outside-tree path.
- Expected: same exception class, same string format. The error message MUST NOT echo the resolved absolute path (no realpath leak per NFR-10).

---

## Group 2 — `file_reader` (extension allowlist, size cap, security headers)

Module: `projects/spec_driven/backend/libs/file_reader.py`. Surface under test: the reader function/class consumed by `GET /api/file`. Spec anchors: FR-4, FR-5, NFR-9.

### 2.1 test_reads_allowed_text_extensions
- Inputs: fixture files of every allowed text extension: `.md`, `.json`, `.yaml`, `.yml`, `.jsonl`, `.txt`.
- Expected: returns `{path, content, mtime, bytes}`; `content` is the text bytes decoded as UTF-8; `bytes` matches `len(raw_bytes)`; `mtime` is RFC 7232 / `datetime`-comparable.

### 2.2 test_reads_allowed_image_extensions_returns_metadata_only_or_base64
- Inputs: a tiny `.png` fixture and `.jpg` fixture.
- Expected: returns the same shape; `content` is whatever the API layer expects (binary base64 OR a marker that triggers the ImagePlaceholder render path). Test asserts the contract the route handler consumes; do NOT bake a specific encoding in the lib test if the lib returns raw bytes.
- Edge cases: 0-byte image; image with bogus header (still served — it's the renderer's job to deal with malformed pixels).

### 2.3 test_rejects_disallowed_extension_415 [FR-4]
- Inputs: `.svg` (NFR-9 carve-out — code-execution vector), `.html`, `.exe`, `.zip`, `.bin`, no extension at all.
- Expected: raises a domain-specific `UnsupportedExtension` error the API layer translates to **415**.
- Edge cases: double extension (`foo.md.exe` — leaf extension wins → 415); leading-dot files (`.gitignore` → 415).

### 2.4 test_rejects_oversize_file_413 [FR-4]
- Inputs: a fixture file of exactly 1_048_576 bytes (1 MB) and one of 1_048_577 bytes.
- Expected: 1_048_576 reads OK; 1_048_577 raises a domain-specific `FileTooLarge` error → **413**. Boundary case is `>1 MB`, not `>=1 MB`. Adjust if the spec is exclusive — re-derive from FR-4 verbatim.
- Edge cases: 0-byte file (allowed); exactly 1 byte (allowed).

### 2.5 test_response_headers_include_nosniff_and_attachment [FR-5]
- Inputs: any successful read.
- Expected: the route layer attaches `X-Content-Type-Options: nosniff` AND `Content-Disposition: attachment`. (This test sits at the API integration layer; if `file_reader` returns a `Headers` object alongside content, assert on it here. Otherwise sit under Group 8.)
- Edge cases: image responses also carry both headers; error responses (415/413) MAY omit `Content-Disposition` but MUST keep `X-Content-Type-Options: nosniff`.

### 2.6 test_path_outside_tree_returns_404_not_existence_oracle [FR-4, NFR-11]
- Inputs: `"../../etc/passwd"`, a path under `EXPOSED_TREE` that doesn't exist (`"specs/development/nope/missing.md"`), and a path outside `EXPOSED_TREE` that doesn't exist.
- Expected: SAME 404 status, SAME error body shape for all three. No "found but outside" distinction.

### 2.7 test_reads_under_dotclaude_subtrees [FR-2]
- Inputs: `".claude/skills/agent_team/SKILL.md"`, `".claude/skills/agent_team/playbooks/research.md"`, `".claude/agent_refs/validation/general.md"`, `".claude/agent_refs/project/development.md"` (recursive subfolder discovery).
- Expected: all read successfully. Verifies `EXPOSED_TREE` recursive discovery picks up future subfolders without code changes.

---

## Group 3 — `file_writer` (atomic write, body validation, stale-write 409)

Module: `projects/spec_driven/backend/libs/file_writer.py`. Surface: `PUT /api/file` consumer. Spec anchors: FR-7, FR-7b, FR-8, NFR-6.

### 3.1 test_writes_atomic_via_temp_then_replace [FR-7]
- Inputs: a path inside `EXPOSED_TREE`, a body of UTF-8 text.
- Expected: target file's bytes match; the implementation creates a temp file in the SAME directory and calls `os.replace` (assert via mock or by monkey-patching `os.replace` to verify it was called with the expected `(src, dst)`).
- Edge cases: write to a path that doesn't yet exist — allowed only for paths under existing directories inside `EXPOSED_TREE` (the API surface does not create new files in v1 per NFR-6, but if the lib supports it, exercise it; otherwise assert the lib refuses).

### 3.2 test_writes_round_trip_returns_new_mtime
- Inputs: round-trip — write content, read it back via `file_reader`.
- Expected: the returned `mtime` matches the post-write `os.stat().st_mtime`; `bytes` matches `len(content.encode("utf-8"))`.

### 3.3 test_rejects_disallowed_extension_415 [FR-8]
- Inputs: `PUT` with `path="foo.svg"`, `path="foo.exe"`, `path="foo.png"`, `path="foo.jpg"`.
- Expected: raises `UnsupportedExtension` → 415. Image extensions explicitly NOT writable per FR-8 (PNG/JPG are read-only in v1).
- Edge cases: SVG MUST be 415 even though it's text — code-execution vector per NFR-9.

### 3.4 test_rejects_oversize_body_413 [FR-7]
- Inputs: a body of 1_048_577 bytes (>1 MB).
- Expected: raises `FileTooLarge` → 413.

### 3.5 test_validates_first_16_bytes_for_text_extensions [FR-8]
- Inputs:
  - body starting with `\x00` (NUL byte) → reject
  - body of valid UTF-8 starting with BOM `\xef\xbb\xbf` → accept (BOM is valid UTF-8)
  - body that is invalid UTF-8 in the first 16 bytes (`b"\xff\xfe...invalid"`) → reject
  - empty body → accept (0 bytes is a valid empty file)
- Expected: rejects raise a domain-specific `InvalidBodyEncoding` → 415 (or 400, whichever the spec resolves; assert the chosen status from the spec).
- Edge cases: NUL byte at index 17 (beyond the first-16-byte check) MAY be allowed if the lib only inspects the prefix — assert the documented behavior.

### 3.6 test_stale_write_returns_409 [FR-7b, AC-13..15]
- Inputs:
  - load mtime M1 from disk;
  - externally update the file (or `os.utime` to a newer mtime M2);
  - `PUT` with `If-Unmodified-Since: M1`.
- Expected: raises a domain-specific `StaleWrite` error carrying `current_mtime=M2` → API layer maps to **409** with body `{detail: {kind: "stale_write", current_mtime}}`.
- Edge cases:
  - `If-Unmodified-Since` exactly equals current mtime → write succeeds.
  - `If-Unmodified-Since` newer than current mtime (impossible in practice) → write succeeds.
  - `If-Unmodified-Since` missing → write proceeds (header is optional; concurrency check skipped).
  - `If-Unmodified-Since` malformed (not RFC 7232) → write proceeds (lenient parse) OR 400 — assert the documented behavior.

### 3.7 test_concurrent_write_does_not_corrupt
- Inputs: two writes interleaved (best-effort with threading/asyncio); the os.replace contract guarantees readers see one or the other but never a partial.
- Expected: post-write file is exactly one of the two bodies, never a mix.
- Skip marker on Windows? `os.replace` is atomic on NTFS for files in the same directory; no skip needed for v1. Mark `xfail` only if a flake is observed.

### 3.8 test_write_outside_tree_404 [NFR-5]
- Inputs: `"../etc/hosts"`, `"/tmp/foo.md"`.
- Expected: same 404 collapse as the reader. No write side-channel.

---

## Group 4 — `tree_walker` (uniform `children` field — consumer-walk regression) [move 2]

Module: `projects/spec_driven/backend/libs/tree_walker.py`. Surface: `GET /api/tree`. Spec anchors: FR-3, FR-15.

This group exists primarily to enforce the **consumer-walk contract** from `agent_refs/validation/development.md` move 2 — the field name `children` MUST appear on every non-leaf, NEVER `task_type.projects` / `project.stages`.

### 4.1 test_root_shape_has_two_top_level_sections [FR-3]
- Inputs: walk the live `EXPOSED_TREE`.
- Expected: top-level returns a `children` array with exactly two entries whose `name` values are `"Claude Settings & Shared Context"` and `"Projects"` (in that order).
- Edge cases: empty repo (no `projects/`) — both top-level sections still present; "Projects" has `children: []`.

### 4.2 test_every_non_leaf_has_children_field [move 2, FR-3]
- Inputs: walk the tree recursively.
- Expected: every node where `type != "file"` carries a `children` field that is a (possibly empty) list. NO node uses `projects`, `stages`, `files`, `items`, or any other custom descent field.
- Implementation: a recursive consumer walk that descends only via `node["children"]` and asserts it terminates at the expected leaf count.

### 4.3 test_every_leaf_has_no_children_field [FR-3]
- Inputs: leaves under `specs/`, `projects/`, `.claude/`.
- Expected: leaves have `type == "file"`, `name`, `path`, but NO `children` key (not even `children: []`). Leaves with an empty array would be "directory with no contents," a different shape.

### 4.4 test_consumer_walk_recursive_descent [move 2, FR-3]
- Inputs: the response from `GET /api/tree`.
- Expected: a recursive function that descends ONLY via `node.children` reaches every file under `EXPOSED_TREE`. Concretely: `count_leaves_via_children == count_files_in_exposed_tree_on_disk`.
- This is the **regression test** for run `spec_driven-20260502-clean`. If the backend reverts to `task_type.projects` / `project.stages`, this test fails loudly.

### 4.5 test_projects_subtree_includes_per_stage_subfolders [FR-15]
- Inputs: a project under `projects/spec_driven/` with `user_input/`, `interview/`, `findings/`, `final_specs/`, `validation/` populated.
- Expected: walking from `Projects → development → spec_driven` descends through `children` into each stage subfolder; each stage subfolder has the expected leaf files.

### 4.6 test_dotclaude_subtree_picks_up_recursive_agent_refs [FR-2]
- Inputs: `.claude/agent_refs/interview/general.md`, `.claude/agent_refs/research/general.md`, `.claude/agent_refs/validation/general.md`, `.claude/agent_refs/project/development.md`.
- Expected: every file appears as a leaf under the `Claude Settings & Shared Context → .claude → agent_refs → ...` chain via `children`.

### 4.7 test_tree_excludes_paths_outside_exposed_tree [FR-2, NFR-5]
- Inputs: a file under `node_modules/`, a file under `.audit/`, a file under `.git/`.
- Expected: NONE appear in the tree response.

### 4.8 test_tree_response_under_250ms_at_canonical_scale [NFR-1]
- Inputs: 50-project × 200-file synthetic fixture (or assert via the actual repo if it exceeds the floor).
- Expected: serializes `<= 250 ms`.
- Note: this is a perf assertion that may live in `performance.md` instead. Cross-listed here because the implementation choice (single tree-walk vs N-call recursion) drives both shape and perf.

---

## Group 5 — `api_security` (Origin/Host allow-list, pre-rewrite vs post-rewrite shape) [move 11]

Module: `projects/spec_driven/backend/libs/api_security.py`. Surface: the middleware/dependency that gates every state-changing route. Spec anchors: FR-9, NFR-7, AC-11.

**This is the regression-test group for run `spec_driven-006`.** Per `[move 11]`, the unit-test set MUST cover BOTH the pre-mutation shape (browser-Origin = dev-server origin) AND the post-mutation shape (Origin = backend bound origin). Missing the pre-rewrite case = `blocker`.

### 5.1 test_accepts_origin_127_loopback [FR-9, AC-11]
- Inputs: `Origin: http://127.0.0.1:8765`, `Host: 127.0.0.1:8765`, on `PUT /api/file`.
- Expected: passes the gate (request proceeds to the handler).

### 5.2 test_accepts_origin_localhost_alias [FR-9, AC-11]
- Inputs: `Origin: http://localhost:8765`, `Host: localhost:8765`.
- Expected: passes — `localhost` ↔ `127.0.0.1` are admitted because they resolve to the same loopback socket.

### 5.3 test_accepts_127_origin_with_localhost_host [FR-9]
- Inputs: `Origin: http://127.0.0.1:8765`, `Host: localhost:8765` (and the swap).
- Expected: passes — the allow-list admits the cross-product `{127.0.0.1, localhost} × {bound_port}`.

### 5.4 test_rejects_pre_rewrite_dev_server_origin_403 [move 11, AC-11] **regression test**
- Inputs: `Origin: http://localhost:5173` (the Vite dev port), `Host: 127.0.0.1:8765`, on `PUT /api/file`.
- Expected: **403** with `{detail: ...}`. This is the EXACT shape a browser sends BEFORE the Vite proxy `configure` hook rewrites it. If this test passes when the middleware naively accepts `localhost:*`, the proxy rewrite hook is bypassable and the bug from run `spec_driven-006` re-introduces silently.
- This test MUST exist; missing it is a `blocker` per the development.md severity table.

### 5.5 test_accepts_post_rewrite_shape_200 [move 11, AC-11]
- Inputs: `Origin: http://127.0.0.1:8765`, `Host: 127.0.0.1:8765` (the Vite proxy hook rewrites both before the request hits the backend).
- Expected: passes the gate. Same shape `make run-prod` produces.

### 5.6 test_rejects_foreign_origin_403 [FR-9]
- Inputs: `Origin: https://evil.example.com`, `Host: 127.0.0.1:8765`.
- Expected: **403**.
- Edge cases: `Origin` with an IP literal of a public host; `Origin` with `null` (some browsers send for cross-origin redirects); `Origin` with `file://`.

### 5.7 test_rejects_missing_origin_403 [FR-9]
- Inputs: no `Origin` header at all.
- Expected: **403**. Missing `Origin` is treated as foreign per the spec ("missing → 403").
- Edge cases: empty-string `Origin: ` — also 403.

### 5.8 test_rejects_wrong_port_origin_403 [FR-9]
- Inputs: `Origin: http://127.0.0.1:9999`, `Host: 127.0.0.1:8765`.
- Expected: **403**. Port mismatch.

### 5.9 test_rejects_ipv6_loopback_origin_403 [OQ-8]
- Inputs: `Origin: http://[::1]:8765`, `Host: [::1]:8765`.
- Expected: **403**. v1 is IPv4-only per OQ-8; the allow-list does NOT include `[::1]`.

### 5.10 test_gate_applies_to_every_state_changing_route [FR-9, NFR-7]
- Inputs: parameterized over `PUT /api/file`, `POST /api/regen-prompt`, `POST /api/promote`, `DELETE /api/promote`. Each with a foreign Origin.
- Expected: all four return **403**.

### 5.11 test_gate_does_not_apply_to_get_routes [FR-9]
- Inputs: `GET /api/file`, `GET /api/tree`, `GET /api/stages` with foreign `Origin`.
- Expected: pass through (200). The gate is for state-changing routes only — Origin/Host CSRF defense is irrelevant on safe methods because they have no side effects.

### 5.12 test_host_header_validated_independently [FR-9]
- Inputs: `Origin: http://127.0.0.1:8765`, `Host: evil.example.com`.
- Expected: **403**. Both headers validated; either failing → 403.

### 5.13 test_request_body_not_consumed_on_gate_failure
- Inputs: a 100 KB body sent with foreign Origin.
- Expected: 403 returned without consuming the body (the gate runs before the body parser). Asserted via the response timing or by mocking the body reader.

### 5.14 test_audit_log_entry_on_gate_failure
- Inputs: a foreign-Origin request.
- Expected: a structured log line with `kind="origin_host_403"`, the offending `Origin`/`Host` values (PII-safe — they're URL components), and the route path. (If the spec deferred audit on 403s, drop this test; otherwise it's the canary.)

---

## Group 6 — `regen_prompt` (header verbatim, contract verbatim, size policy)

Module: `projects/spec_driven/backend/libs/regen_prompt.py`. Surface: `POST /api/regen-prompt`. Spec anchors: FR-10, FR-11, FR-12, FR-37, AC-16..19.

### 6.1 test_interactive_header_first_line_verbatim [FR-11a, AC-16]
- Inputs: `autonomous=False`, any stages.
- Expected: the FIRST line of `prompt` is exactly `"# EXECUTION MODE: INTERACTIVE"` (byte-for-byte; trailing newline is the line terminator). Asserted via `prompt.split("\n", 1)[0] == "# EXECUTION MODE: INTERACTIVE"`.

### 6.2 test_autonomous_header_first_line_verbatim [FR-11a, AC-16]
- Inputs: `autonomous=True`.
- Expected: first line is exactly `"# EXECUTION MODE: AUTONOMOUS"`.

### 6.3 test_no_header_for_explicitly_unset_mode_treated_as_interactive_in_caller
- Inputs: at the API surface, `autonomous` is always a bool (Pydantic default `False`). The lib MUST always emit one of the two headers. Test that there is NO code path producing a prompt without an `# EXECUTION MODE: ...` first line.

### 6.4 test_autonomous_imperative_block_present_when_autonomous [FR-11a]
- Inputs: `autonomous=True`.
- Expected: the prompt contains the literal imperative block from `CLAUDE.md` § Regeneration prompts & autonomous mode (no `AskUserQuestion`; record judgment calls inline; produce all artifacts in same turn; honor every other rule). Verbatim sub-string match against the canonical text in `CLAUDE.md`.
- Edge cases: when `autonomous=False`, the imperative block MUST be absent (no leakage).

### 6.5 test_revised_prompt_inlined_verbatim [FR-11b, AC-16]
- Inputs: a project whose `user_input/revised_prompt.md` has a known body.
- Expected: that exact body appears in the prompt string under a clearly delimited section header (e.g., `## Revised prompt` or `## User intent`), with NO truncation, NO reflow, NO trailing-whitespace munging.

### 6.6 test_falls_back_to_raw_prompt_when_no_revised [FR-11b]
- Inputs: a project where `user_input/revised_prompt.md` does NOT exist; only `user_input/raw_prompt.md`.
- Expected: the prompt inlines `raw_prompt.md` instead, with a header that reflects the fallback (e.g., `## Raw prompt (no revised yet)`).

### 6.7 test_follow_ups_inlined_in_numerical_order [FR-11c, AC-16]
- Inputs: a project with `follow_ups/001-...md`, `follow_ups/002-...md`, `follow_ups/003-...md`.
- Expected:
  - all three filenames AND bodies appear in the prompt;
  - they appear in numeric order 001 → 002 → 003 (NOT lexicographic if that diverges; NOT mtime order);
  - each is preceded by a per-follow-up header citing the filename verbatim.
- Edge cases: zero follow-ups → no follow-ups section emitted (or a "No follow-ups" stub — assert the documented behavior); follow-up with non-three-digit prefix (`010-...md`) sorts numerically (10) AFTER `009`, BEFORE `011`.

### 6.8 test_promoted_md_inlined_verbatim_under_pinned_header [FR-11d, AC-18]
- Inputs: a stage's `<stage>/promoted.md` with two pinned items.
- Expected: under the per-stage section, a sub-header `### Pinned items (MUST survive regeneration)` (or the canonical header from `CLAUDE.md`) followed by the verbatim `promoted.md` body. NO whitespace reflow.

### 6.9 test_promoted_md_section_omitted_when_empty [FR-11d]
- Inputs: a stage whose `promoted.md` is missing OR empty (only the boilerplate comment).
- Expected: the pinned-items section is OMITTED (not a stub with "no pins"). Empty pinned-items section is noise — assert clean omission.

### 6.10 test_read_zero_contract_section_verbatim [FR-11e, FR-37, AC-18]
- Inputs: any stages, any modes.
- Expected: a `### Constraints` section appears at the END of the prompt with the read-zero contract paragraph from `CLAUDE.md` § Regeneration prompts & autonomous mode (the per-stage delete-list table or the prose summary). Verbatim sub-string match.
- Edge cases: when only one stage is selected, the constraint table MAY be filtered to that stage's row OR include the full table — assert the documented choice.

### 6.11 test_audit_event_protocol_section_present [FR-38]
- Inputs: any prompt.
- Expected: the prompt mentions the three event names: `regen.delete.planned`, `regen.delete.completed`, `regen.write.completed`. Verbatim string match for all three (no paraphrase).

### 6.12 test_size_policy_under_50kb_warning_null [FR-12, AC-19]
- Inputs: a small project (revised prompt 1 KB, no follow-ups, one stage).
- Expected: response includes `bytes < 50 * 1024` and `warning is None`.

### 6.13 test_size_policy_50kb_to_1mb_warning_approaching [FR-12, AC-19]
- Inputs: a synthesized project where the assembled prompt is between 50 KB and 1 MB (e.g., a long revised prompt or many follow-ups).
- Expected: response `warning == {"kind": "approaching_ceiling", "bytes": <actual>, "soft_limit": 51200}`.

### 6.14 test_size_policy_at_or_above_1mb_returns_413 [FR-12, AC-19]
- Inputs: a synthesized project where the prompt is `>= 1 MB` (1_048_576 bytes).
- Expected: raises a domain-specific `PromptTooLarge` → API returns **413** with `{detail: {kind: "too_large"}}`. Prompt body NOT included in the response.

### 6.15 test_module_filtering_excludes_unselected [FR-32]
- Inputs: a stage with three modules; `modules: {stage_id: ["module_a"]}` (only one selected).
- Expected: the prompt's per-stage section includes ONLY `module_a`'s deletion entry / module reference; modules `module_b` and `module_c` are NOT mentioned.

### 6.16 test_default_modules_when_unspecified [FR-31]
- Inputs: a stage selected without an explicit `modules` entry (the UI default = all modules).
- Expected: assert the documented behavior — either the lib infers "all" from a missing key, or the API surface defaults the request before the lib sees it. Pin down which.

### 6.17 test_stage_invocation_hint_included_per_stage [FR-11d]
- Inputs: stages 2 and 5 selected.
- Expected: each stage's section includes the canonical invocation hint from `stages.py` (e.g., "Re-run interview stage" / "Re-run validation strategy stage"), the folder path, and the module list with `description` fields.

### 6.18 test_returns_response_shape [FR-10]
- Inputs: any successful build.
- Expected: response dict has exactly the keys `{prompt, warning, selected_stages_count, follow_ups_count, autonomous, bytes}`. No extra keys. Types: `prompt: str`, `warning: dict|None`, counts: `int`, `autonomous: bool`, `bytes: int`.

### 6.19 test_unicode_safe_assembly
- Inputs: a `revised_prompt.md` containing emoji, CJK characters, and combining diacritics.
- Expected: the assembled prompt is valid UTF-8; `bytes` reflects the encoded byte count (not the codepoint count). NO `\uXXXX` escape leakage.

---

## Group 7 — `promotions` (parse_promoted_text, idempotent post/delete, stage_folder allowlist)

Module: `projects/spec_driven/backend/libs/promotions.py`. Surface: `POST /api/promote`, `DELETE /api/promote`. Spec anchors: FR-13, FR-14, AC-24, plus `agent_refs/validation/general.md` § Pinned items survive regeneration.

### 7.1 test_parse_promoted_text_round_trip [pinned-items contract]
- Inputs: a synthesized `promoted.md` containing two pinned items, each with `source_file`, `item_id`, `item_text` metadata blocks.
- Expected: `parse_promoted_text(text)` returns a list of two `PromotedItem` (or equivalent) objects with the right fields. Re-serializing them produces a text that round-trips through `parse_promoted_text` to the same list (modulo whitespace per general.md § 8).
- Edge cases:
  - empty file → empty list;
  - file with only the boilerplate header `_INPUT to regeneration..._` → empty list;
  - duplicate `item_id` entries → both parsed (lib does not de-dupe; idempotence happens at write).

### 7.2 test_parse_handles_real_promoted_text_from_run [move 10]
- Inputs: a fixture `promoted.md` copied from a real prior run (e.g., `spec_driven-006` interview stage, if available).
- Expected: parses without raising; returned items have non-empty `item_text`.
- Per `[move 10]`: parser regex tested against actual upstream output, not a hand-written fixture. The fixture is rotated whenever a new pin shape appears.

### 7.3 test_post_promote_appends_to_promoted_md [FR-13]
- Inputs: an empty (or missing) `promoted.md`, a `POST /api/promote` body with `{stage_folder: "interview", source_file: "qa.md", item_id: "Q-3", item_text: "..."}`.
- Expected:
  - file is created (or appended) at `specs/{type}/{name}/interview/promoted.md`;
  - the new content is parseable by `parse_promoted_text`;
  - response is `{status: "ok", item_id: "Q-3"}`.

### 7.4 test_post_promote_is_idempotent [FR-13]
- Inputs: `POST /api/promote` with the same `{stage_folder, source_file, item_id}` twice.
- Expected: second call does NOT duplicate the entry. Either it returns 200 with the existing item OR it overwrites in-place. Assert the documented behavior; either way, `parse_promoted_text` returns ONE entry, not two.

### 7.5 test_delete_promote_removes_entry [FR-14]
- Inputs: `promoted.md` containing two items; `DELETE /api/promote` with one of the `item_id`s.
- Expected: the named item is gone; the other survives; response is `{status: "ok", item_id: ...}`.

### 7.6 test_delete_promote_idempotent_when_missing [FR-14]
- Inputs: `DELETE /api/promote` for an `item_id` that does NOT exist in `promoted.md`.
- Expected: returns 200 (`{status: "ok"}`); file unchanged. NOT 404 — the spec calls for idempotent 200.

### 7.7 test_stage_folder_allowlist [FR-13]
- Inputs: `POST /api/promote` with `stage_folder` in `{"interview", "findings", "final_specs", "validation"}` (allowed) and `stage_folder` in `{"user_input", "..", "../etc", "projects", "stage_6", ""}` (rejected).
- Expected: allowed values write to the right path; rejected values return **400** (or 403 — assert spec).
- Edge cases: case sensitivity (`Interview` should be rejected — strict allowlist).

### 7.8 test_promote_to_stage_6_rejected [FR-13, NFR-15-adjacent]
- Inputs: `POST /api/promote` with `stage_folder="execution"` or anything implying stage 6.
- Expected: 400 (out-of-scope per FR-13: stage 6 does NOT support promotion in v1).

### 7.9 test_promote_path_uses_safe_resolve [NFR-5]
- Inputs: a `POST /api/promote` whose `stage_folder` is a valid allowlist value, but whose `project_name` contains `..` or other traversal markers.
- Expected: rejected (the resolver runs over the constructed path before the appender opens it).

### 7.10 test_promoted_md_preserves_through_simulated_regen
- Inputs: a `promoted.md` written via `POST`, then a simulated regen-delete pass that walks the per-stage delete list.
- Expected: `promoted.md` is in the Preserve column and remains on disk after the deletion pass. (Cross-listed in `system_tests.md` for the e2e form.)

---

## Group 8 — API routes (negative-status surface)

Module: `projects/spec_driven/backend/libs/api.py`. Surface: the FastAPI route layer. Spec anchors: FR-4, FR-7..9, NFR-6.

These tests assert the HTTP-status surface, not handler internals (which Groups 2/3/5/6/7 cover). They use `httpx.AsyncClient` against the FastAPI app.

### 8.1 test_patch_on_api_file_returns_405 [NFR-6, AC-12]
- Inputs: `PATCH /api/file?path=CLAUDE.md`.
- Expected: **405**. (The route handler MUST be explicit about allowed methods.)

### 8.2 test_delete_on_api_file_returns_405 [NFR-6, AC-12]
- Inputs: `DELETE /api/file?path=CLAUDE.md`.
- Expected: **405**.

### 8.3 test_post_on_api_file_returns_405 [NFR-6, AC-12]
- Inputs: `POST /api/file` (with any body).
- Expected: **405**. Only `GET` and `PUT` are allowed.

### 8.4 test_put_disallowed_extension_returns_415 [FR-8]
- Inputs: `PUT /api/file` with `path="foo.svg"` (or `.exe`, `.html`).
- Expected: **415**.

### 8.5 test_put_oversize_body_returns_413 [FR-7, AC-10]
- Inputs: `PUT /api/file` with a 1.5 MB body.
- Expected: **413** with `{detail: {kind: "too_large"}}`.

### 8.6 test_get_path_outside_tree_returns_404_single_status [FR-4, NFR-11]
- Inputs: `GET /api/file?path=../etc/passwd`, `GET /api/file?path=specs/development/missing/foo.md` (inside-tree but missing).
- Expected: BOTH return **404** with the SAME body shape. No existence oracle.

### 8.7 test_get_disallowed_extension_returns_415 [FR-4]
- Inputs: `GET /api/file?path=foo.svg`, `?path=foo.exe`.
- Expected: **415**.

### 8.8 test_get_oversize_file_returns_413 [FR-4]
- Inputs: a fixture file >1 MB inside `EXPOSED_TREE`.
- Expected: **413**.

### 8.9 test_state_changing_routes_carry_security_headers [FR-5]
- Inputs: successful `GET /api/file` of a small `.md` fixture.
- Expected: response headers include `X-Content-Type-Options: nosniff` AND `Content-Disposition: attachment`.

### 8.10 test_options_preflight_disabled_or_locked [NFR-7]
- Inputs: `OPTIONS /api/file` with a foreign `Origin`.
- Expected: either **405** (if CORS preflight is disabled, which is the v1 default — same-origin only) OR a 200 with no `Access-Control-Allow-Origin` for foreign origins. Assert the documented behavior.

### 8.11 test_unknown_route_returns_404 [NFR-7]
- Inputs: `GET /api/nonexistent`, `POST /api/foo`.
- Expected: **404** (FastAPI default). Same shape as path-outside-tree 404 if the spec unifies them; otherwise distinct.

### 8.12 test_post_promote_validates_body_shape [FR-13]
- Inputs: `POST /api/promote` with missing `item_id`, missing `stage_folder`, and a foreign-Origin (with valid body — gate runs before body parse).
- Expected: invalid-body returns **422** (FastAPI/Pydantic default); foreign-Origin returns **403** (gate runs first).

### 8.13 test_post_regen_prompt_validates_body_shape [FR-10]
- Inputs: `POST /api/regen-prompt` with missing `project_type`, `stages` not a list, etc.
- Expected: **422** for malformed body; **403** for foreign-Origin (gate first).

### 8.14 test_get_stages_returns_six_stage_definition [FR-6]
- Inputs: `GET /api/stages?project_type=development&project_name=spec_driven`.
- Expected: 200 with a list of 6 stages, each having `{id, label, folder, invocation, modules: [...]}`. Hard-coded server-side per FR-6.

---

## Group 9 — Frontend `qaParser` (interactive + autonomous-mode forms) [move 10]

Module: `projects/spec_driven/frontend/src/lib/qaParser.ts`. Surface: the parser consumed by `QaView` to render `interview/qa.md`. Spec anchors: FR-20, AC-25.

**Per `[move 10]`, the parser regex MUST be tested against real upstream output, not hand-written fixtures.** The fixture inventory rotates whenever the upstream interview stage emits a new variant. v1 must include at minimum:

1. **Interactive form:** `- Q: ...` / `- A: ...` (the original spec-example format).
2. **Autonomous form:** `- A *(judgment call: chose X because Y)*: ...` (the form that broke the parser in run `spec_driven-20260502-clean`).

### 9.1 test_parses_interactive_form [FR-20]
- Inputs: a fixture string in the interactive form:
  ```
  ## Round 1
  ### Category: Foo
  - Q: What is X?
  - A: It is Y.
  ```
- Expected: returns one round with one category containing one Q/A pair: `{round: 1, category: "Foo", q: "What is X?", a: "It is Y."}`.

### 9.2 test_parses_autonomous_form_with_judgment_call_annotation [move 10, AC-25]
- Inputs: a fixture string in the autonomous form:
  ```
  ## Round 1
  ### Category: Foo
  - Q: What is X?
  - A *(judgment call: chose Y because of Z)*: It is Y.
  ```
- Expected: returns one Q/A pair where:
  - `q == "What is X?"`,
  - `a == "It is Y."`,
  - `judgmentCall == "chose Y because of Z"` (parsed out of the parenthetical),
  - the parenthetical does NOT bleed into the answer text.

### 9.3 test_parses_real_run_qa_md_fixture [move 10]
- Inputs: the actual `qa.md` from a recent run on disk (rotating fixture). Test imports the file at build time or via a fixture loader.
- Expected: parses without throwing; returns at least one round with at least one Q/A pair; `judgmentCall` is set on every A that has the annotation.
- Per `[move 10]`: this fixture MUST be sourced from a real run, not hand-edited. When the upstream interview stage adds a new annotation variant, this test updates first.

### 9.4 test_handles_multi_round_qa_md
- Inputs: a fixture with three rounds, multiple categories per round.
- Expected: returns three rounds in order; each round's categories are in source order; each category's Q/A pairs are in source order.

### 9.5 test_handles_multi_paragraph_answer
- Inputs: an answer that spans multiple bullets / multiple paragraphs.
- Expected: the parser captures the full answer text (the regex must not stop at the first newline). Edge case: an answer containing a `- ` literal (e.g., a Markdown list inside the answer) — the parser MUST distinguish nested list items from new Q/A bullets.

### 9.6 test_throws_or_returns_partial_on_malformed_input [AC-25]
- Inputs: a malformed `qa.md` (missing `## Round`, missing categories, mixed indentation).
- Expected: throws a typed `QaParseError` (so the `QaErrorBoundary` can render the parse-fallback). The error MUST be thrown DURING render — i.e., the parser is invoked as part of the render-tree, NOT pre-parsed in the parent (per `[move 9]`, the boundary protects render-phase throws).
- Edge cases: empty file → returns `{rounds: []}` (NOT an error); whitespace-only file → same.

### 9.7 test_q_and_a_color_metadata_passed_through [FR-20]
- Inputs: any well-formed Q/A pair.
- Expected: the returned shape carries the `kind` discriminant `"q" | "a" | "category"` so the renderer can pick blue / green / badge tints from a single source of truth.

### 9.8 test_pinnable_atomic_id_per_qa_pair [FR-35]
- Inputs: any well-formed Q/A pair.
- Expected: the returned shape carries an `itemId` (e.g., `"Q-1.2.3"` → round 1, category 2, pair 3) suitable for `POST /api/promote`. Stable across re-renders of the same source text.

### 9.9 test_parser_does_not_silently_swallow_unrecognized_lines [move 10]
- Inputs: a `qa.md` containing a recognized round + a stray unrecognized line ("Note: ...").
- Expected: either (a) the stray line surfaces in a typed `unrecognized` array, OR (b) the parser throws. NEVER silently drop. Silent drop would cause regressions like the autonomous-form bug to fail invisibly.

---

## Group 10 — Frontend `linkResolver` (relative resolution, broken-link detection)

Module: `projects/spec_driven/frontend/src/lib/linkResolver.ts`. Surface: the link transformer used by `MarkdownView` (react-markdown plugin or `<a>` interceptor). Spec anchors: FR-19, AC-27.

### 10.1 test_resolves_relative_link_against_current_file_dir [FR-19]
- Inputs: current file path `"specs/development/spec_driven/final_specs/spec.md"`, link href `"../validation/strategy.md"`.
- Expected: resolved to `"specs/development/spec_driven/validation/strategy.md"`.
- Edge cases: `"./sibling.md"`, `"foo/bar.md"` (no leading `./`), `"../../different_project/spec.md"`.

### 10.2 test_external_http_link_returns_unchanged [FR-19]
- Inputs: `"https://example.com/foo"`, `"http://example.com"`.
- Expected: returned as-is; the renderer opens it in a new tab (`target="_blank" rel="noreferrer noopener"`).

### 10.3 test_broken_link_renders_as_muted_span_not_a [FR-19, AC-27]
- Inputs: a relative link to a path that does NOT exist in the tree (asserted via the tree-data passed to the resolver).
- Expected: returns a `{kind: "broken", href, title}` discriminator that the renderer maps to `<span class="broken-link" title="...">` — NOT an `<a>`. AC-27 explicitly forbids `<a>` for broken links (avoids accidental navigation to a 404).

### 10.4 test_broken_link_title_explains_why
- Inputs: a relative link resolving to an outside-tree path (vs an inside-tree-but-missing path).
- Expected: the `title` tooltip distinguishes the cases ("link target not in exposed tree" vs "link target not found"). User-facing error message.
- Note: a path-outside-tree leak in the tooltip is acceptable here because the tree data is already client-side; the server's NFR-11 single-404 rule does NOT apply to the client renderer.

### 10.5 test_anchor_only_link_left_alone [FR-19]
- Inputs: `"#section-foo"`, `"foo.md#anchor"`.
- Expected: anchor-only links scroll inside the current page; cross-file anchors resolve the file part and pass the anchor through.

### 10.6 test_handles_percent_encoded_paths
- Inputs: a relative link `"../foo%20bar.md"` to a file actually named `foo bar.md`.
- Expected: decoded once, resolved correctly. NEVER double-decoded.

### 10.7 test_image_link_routed_to_image_path_resolver [FR-19, FR-23]
- Inputs: a relative `<img src="../diagram.png">`.
- Expected: resolved to the absolute path inside `EXPOSED_TREE` so the `ImagePlaceholder` (or img tag) can fetch via `GET /api/file`.

### 10.8 test_resolver_normalizes_mixed_slashes_in_user_authored_markdown
- Inputs: a link `"..\\validation\\strategy.md"` (Windows-authored in markdown).
- Expected: normalized to forward slashes and resolved. Asymmetry with the backend (which rejects backslashes from the API surface): the markdown CONTENT is allowed to contain Windows slashes; the API path argument is not.

### 10.9 test_resolver_does_not_throw_on_pathological_inputs
- Inputs: extremely long paths, paths with control characters, paths with ` `.
- Expected: returns `{kind: "broken", ...}` rather than throwing. Throwing would break the React render and the boundary (move 9) would catch it — but that's a worse user experience than a broken-link span.

---

## Group 11 — Frontend `QaErrorBoundary` (real React class) [move 9]

Module: `projects/spec_driven/frontend/src/components/QaErrorBoundary.tsx`. Surface: the boundary that wraps `<QaView />` and the generalized `<ParseFallback />` per FR-24. Spec anchors: FR-24, AC-25.

**Per `[move 9]`, the boundary MUST be a real class component with `componentDidCatch` / `getDerivedStateFromError`. A `try { return <QaView /> } catch` shape is a `blocker`.**

### 11.1 test_is_class_component_with_lifecycle [move 9, AC-25]
- Inputs: import the boundary module.
- Expected: the export is a class extending `React.Component` (or `React.PureComponent`). It defines:
  - `static getDerivedStateFromError(error)` returning `{hasError: true, error}`,
  - `componentDidCatch(error, info)` (logs / records error info),
  - a `render()` that returns the fallback when `hasError` is true.
- Asserted via reflection: `typeof Boundary.getDerivedStateFromError === 'function'`, `typeof Boundary.prototype.componentDidCatch === 'function'`.

### 11.2 test_catches_render_phase_throw_from_child [move 9, AC-25]
- Inputs: render `<QaErrorBoundary><Thrower /></QaErrorBoundary>` where `<Thrower />` throws inside its `render()` body (NOT in an effect, NOT in a click handler — exactly the render-phase shape that `try { return <Foo /> } catch` would miss).
- Expected: boundary captures the error; `componentDidCatch` is called with the thrown error; the rendered DOM contains the fallback markup (a `<pre>` with the raw text + a banner).
- This is the **regression test** for run `spec_driven-20260502-clean`.

### 11.3 test_does_not_catch_event_handler_errors
- Inputs: a child whose `onClick` throws. (React error boundaries do NOT catch event-handler errors by design.)
- Expected: the boundary does NOT mark `hasError: true`. The error propagates to the global `window.onerror` handler.
- Edge cases: this is documented React behavior, not a deviation. The test ensures the boundary is not over-reaching.

### 11.4 test_fallback_renders_raw_text_in_pre [FR-24]
- Inputs: a boundary whose child threw with the file's raw text passed via prop.
- Expected: fallback `<pre>` contains the raw text verbatim; banner above it has a clear parse-error message.
- Edge cases: very long raw text — `<pre>` MUST scroll, not truncate.

### 11.5 test_resets_on_new_file_load [FR-24]
- Inputs: load a malformed file → boundary fallback → user navigates to a different valid file.
- Expected: boundary resets `hasError` to false on the new prop / new key. Per the FR-24 generalization, the boundary uses a `key={filePath}` reset strategy OR a `getDerivedStateFromProps` reset.

### 11.6 test_logs_to_console_in_dev_only
- Inputs: a render-phase throw under `process.env.NODE_ENV === 'development'` vs `'production'`.
- Expected: dev mode logs to `console.error` with the captured info; prod mode does NOT log (to avoid leaking parse-error context to production users — though the v1 webapp is localhost-only, the convention sticks).

### 11.7 test_boundary_used_around_every_parse_then_render_component [FR-24, move 9]
- Inputs: the component tree under `Reader.tsx`.
- Expected: `<QaView />`, `<JsonlView />`, `<CodeView />`, `<MarkdownView />` (the four parse-then-render components per FR-19..22) are EACH wrapped by `<ParseFallback />` (the generalized boundary). Asserted by importing the Reader module and inspecting the JSX (or via a snapshot test of the component tree).

### 11.8 test_no_try_return_jsx_catch_pattern_in_codebase [move 9]
- Inputs: a static analysis pass over `frontend/src/**/*.tsx` looking for the regex `try\s*\{\s*return\s*<`.
- Expected: zero matches. Any match is the anti-pattern from `[move 9]` and a `blocker`.
- Note: this test sits at the lint level rather than runtime; integrate via `npm run lint` (custom ESLint rule) and assert the lint pass.

---

## Group 12 — Frontend `autonomousMode` + `localStorage` cross-tab `storage` event

Module: `projects/spec_driven/frontend/src/autonomousMode.ts` + `projects/spec_driven/frontend/src/localStorage.ts`. Surface: the hook/store that drives the autonomous toggle in `RegeneratePanel` and `ProjectPage`. Spec anchors: FR-34, AC-22..23.

### 12.1 test_default_off_when_no_localstorage_value [FR-34, AC-22]
- Inputs: `localStorage.getItem("spec_driven.autonomous_mode.v1")` returns `null`.
- Expected: hook initial value is `false` (interactive mode). Default off is the v1 contract.

### 12.2 test_persists_to_localstorage_on_toggle [FR-34, AC-22]
- Inputs: toggle from `false` → `true`.
- Expected: `localStorage.getItem("spec_driven.autonomous_mode.v1") === "true"` (or whatever serialization the lib uses — assert the documented format).
- Edge cases: toggle back to `false` → either `"false"` or removed-from-storage; assert documented choice.

### 12.3 test_reads_existing_localstorage_value_on_mount [FR-34]
- Inputs: pre-set `localStorage.setItem("spec_driven.autonomous_mode.v1", "true")` before mounting.
- Expected: hook initial value is `true`.

### 12.4 test_handles_corrupt_localstorage_value_gracefully [FR-34]
- Inputs: pre-set the key to `"banana"` or `"{"`.
- Expected: hook falls back to default `false`, optionally logs a `console.warn` in dev. Does NOT throw — corrupt storage MUST not break the panel.

### 12.5 test_cross_tab_storage_event_updates_value [FR-34, AC-23]
- Inputs: mount the hook in one "tab" (test); fire a synthetic `storage` event (`new StorageEvent("storage", {key, newValue, oldValue, storageArea: localStorage})`) with the autonomous key flipped.
- Expected: hook value updates without re-mount. Asserted via `act(() => window.dispatchEvent(...))` and then reading the value.
- Per FR-34: "same value drives per-stage and project-page panels via the native `storage` event."

### 12.6 test_storage_event_for_other_keys_ignored [FR-34]
- Inputs: a `storage` event with a different `key` (e.g., `"unrelated.key"`).
- Expected: hook value does NOT change.

### 12.7 test_storage_event_with_null_new_value_resets_to_default [FR-34]
- Inputs: a `storage` event with `newValue: null` (another tab cleared the key).
- Expected: hook value resets to `false` (the default).

### 12.8 test_unsubscribe_on_unmount [FR-34]
- Inputs: mount the hook, unmount, fire a `storage` event for the autonomous key.
- Expected: no React warnings about state updates on unmounted components. The hook MUST `removeEventListener("storage", ...)` on unmount.

### 12.9 test_no_server_side_persistence [FR-34]
- Inputs: any toggle action.
- Expected: NO network request fires. Autonomous mode is per-tab `localStorage` only; the API surface has no autonomous-mode endpoint.

### 12.10 test_localstorage_module_quota_exceeded_handled [FR-34]
- Inputs: mock `localStorage.setItem` to throw `QuotaExceededError`.
- Expected: the toggle still updates the in-memory value and renders correctly; the error is swallowed (with a dev `console.warn`). Persistence is best-effort — failing to write to storage MUST not break the UI.

### 12.11 test_localstorage_unavailable_falls_back_in_memory [FR-34]
- Inputs: simulate a runtime where `localStorage` access throws (Safari private mode, etc.).
- Expected: the hook works in-memory; values do NOT persist across reloads but the UI never breaks. `console.warn` in dev only.

### 12.12 test_storage_key_versioned [FR-34]
- Inputs: assert the literal key constant.
- Expected: the key is exactly `"spec_driven.autonomous_mode.v1"`. The `.v1` suffix is load-bearing — future schema changes bump the suffix to avoid colliding with old corrupt values.

---

## Cross-cutting test conventions

- **Naming:** `test_<unit>_<expected>` for Python; `<unit> <expected>` `it()` strings for the frontend (Vitest).
- **Layout:** Python unit tests under `projects/spec_driven/backend/tests/unit/test_<lib>.py`. Frontend unit tests under `projects/spec_driven/frontend/tests/unit/<lib>.test.ts(x)`. One test file per lib module; one `describe` block per group above.
- **Fixtures:**
  - Real `qa.md` rotating fixture lives at `projects/spec_driven/frontend/tests/fixtures/qa/<slug>.md`. Updated whenever the upstream interview stage produces a new annotation variant per `[move 10]`.
  - Real `promoted.md` rotating fixture lives at `projects/spec_driven/backend/tests/fixtures/promotions/<slug>-promoted.md`.
  - Synthetic large-file fixtures (1 MB, 1.5 MB) generated at test time via `tmp_path` to avoid bloating the repo.
- **Path constants:** every test reads `repo_root` from `libs/repo_root.py`; never hardcodes `C:\workspace\spec_coding`.
- **Skip markers:** every POSIX-only test carries `pytest.mark.skipif(sys.platform == "win32", reason="...")` per `[move 5]`. Same for the symlink/junction split (1.8 / 1.9).
- **Severity mapping:** failures in Group 1 (path sandbox) and Group 5 sub-cases marked `[move 11]` are `critical` / halt immediately. Failures in Groups 4 (consumer-walk), 9 (`autonomous` form parser), 11 (real boundary class) are `blocker`. Other failures follow the standard severity table.

## Outstanding questions for the parent

- **OQ-A.** Should test 2.5 (security headers on read responses) live in `unit_tests.md` (this file) or `system_tests.md`? The header attachment is a route-layer concern, not strictly a `file_reader` lib concern. **Recommendation:** keep in this file, Group 8, since the route layer is in scope here.
- **OQ-B.** `test_concurrent_write_does_not_corrupt` (3.7) is best-effort on NTFS per `[move 5]`. If a flake surfaces in CI, mark `xfail` rather than skipping silently.
- **OQ-C.** The exact response status for 5.4 / 5.6 / 5.7 (foreign / missing / wrong-port `Origin`) is **403** per spec; double-check no spec section has drifted to **401** during regen.
- **OQ-D.** The pinned-items contract's "modulo whitespace" assertion (general.md § 8) — pick a canonical normalizer (`re.sub(r"\s+", " ", x).strip()`) and use it consistently across this file's 7.1 and any system-test counterparts to avoid two definitions of "verbatim modulo whitespace."

## Audit trail

Spawn audit at `.audit/adhoc_agents/2026-05-03/spec_driven-20260503-145859/spawns/level-specialist-03-unit/` (`prompt.md` + `output.md`). Run id: `spec_driven-20260503-145859`.
