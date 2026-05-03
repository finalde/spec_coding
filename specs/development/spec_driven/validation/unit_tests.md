# Unit tests — spec_driven

Run: spec_driven-20260503-030434 (level: unit_tests)

Scope: every unit test case the build needs, grouped by module under `backend/libs/` and `frontend/src/`. **Descriptions only — no code.** Each case lists test name, inputs (1 line), expected output, and edge cases. Cross-platform skips are explicitly called out per case using `pytest.mark.skipif(sys.platform == "win32", reason="...")` (Vitest/Playwright equivalents on the frontend).

The cases marked **[regression-2026-05-02-clean]** are the cases that, had they existed, would have caught the bugs in run `spec_driven-20260502-clean` (consumer-walk for `/api/tree`, autonomous-mode QaView fixture, parse-on-render Error Boundary). They are non-negotiable.

---

## Backend — `backend/libs/`

### Group 1 — `safe_resolve` (path canonicalization + sandbox)

Module: `backend/libs/safe_resolve.py`. All cases below operate on the EXPOSED_TREE root and assert that `safe_resolve` returns either an absolute path INSIDE the tree or raises `OutsideTreeError` (mapped to HTTP 404 by the API layer per FR-3 / FR-4). 404 is the single error code; 403 is forbidden (no enumeration side-channel).

#### 1.1 `test_safe_resolve_happy_path_relative`
- Inputs: `rel = "specs/development/spec_driven/final_specs/spec.md"` against EXPOSED_TREE root.
- Expected: returns the absolute path; `os.path.exists` is true; the returned path is forward-slash normalized.
- Edge cases: trailing slash, `./`-prefixed input, mixed separators (`specs\\development/spec_driven/...`), unicode filename, deeply nested path (>10 segments).

#### 1.2 `test_safe_resolve_rejects_relative_traversal`
- Inputs: `rel = "specs/../../etc/passwd"` and `rel = "../etc/passwd"`.
- Expected: raises `OutsideTreeError` (→ 404). Never returns a path; never reads disk.
- Edge cases: `../` mid-path (`specs/development/../../../etc/passwd`); URL-encoded variants (`specs%2F..%2F..%2Fetc%2Fpasswd`) — must be rejected at decode time before reaching `safe_resolve`; double-encoded variants; mixed `..` with `.` (`specs/./.././../`); `..` after a symlink-like segment.

#### 1.3 `test_safe_resolve_rejects_absolute_paths`
- Inputs: `rel = "C:\\Windows\\System32\\drivers\\etc\\hosts"`, `rel = "/etc/passwd"`, `rel = "\\\\?\\C:\\Windows\\..."` (Win32 long-path prefix), `rel = "\\\\server\\share\\file"` (UNC).
- Expected: each raises `OutsideTreeError` (→ 404).
- Edge cases: drive-relative (`C:relative\\path`); `file://` URI; trailing whitespace and trailing dots that NTFS strips silently.

#### 1.4 `test_safe_resolve_rejects_alternate_data_streams`
- Inputs: `rel = "specs/development/spec_driven/final_specs/spec.md::$DATA"`, `rel = "...:stream"`, `rel = "...:hidden:$DATA"`.
- Expected: each raises `OutsideTreeError` (→ 404). The colon-stream segment is detected BEFORE filesystem lookup so the underlying file is never read.
- Edge cases: ADS embedded mid-path (`specs/foo::$DATA/bar`); empty stream name (`spec.md:`); reserved stream `:$INDEX_ALLOCATION`.

#### 1.5 `test_safe_resolve_rejects_windows_reserved_device_names`
- Inputs: each of `CON, PRN, AUX, NUL, COM1..COM9, LPT1..LPT9`, both bare and with extension (`CON.md`, `prn.txt`), at root and nested (`specs/.../CON.md`).
- Expected: each raises `OutsideTreeError` (→ 404).
- Edge cases: case variants (`con`, `Con`, `CON`); device name as a parent segment (`COM1/foo.md`); device name with trailing dots/spaces (NTFS strips them so `CON.` resolves to `CON`).

#### 1.6 `test_safe_resolve_rejects_8_3_short_names`
- Inputs: `rel = "PROGRA~1/foo.md"`, `rel = "specs/DEVELO~1/spec_driven/..."` (synthesized), `rel = "FINAL_~1/spec.md"`.
- Expected: each raises `OutsideTreeError` (→ 404). The `~N` short-name pattern is detected by regex on each segment before any disk lookup.
- Edge cases: short name nested mid-path; short name that does NOT actually correspond to a real long name (still rejected — pattern-based, not lookup-based); legitimate filenames containing `~` but not in 8.3 form (e.g., `notes~v2.md`) — these MUST be allowed; `~N` in extension only.

#### 1.7 `test_safe_resolve_rejects_junctions_and_reparse_points`
- Inputs: a real NTFS junction created inside `specs/` pointing outside EXPOSED_TREE (e.g., to `C:\Windows\Temp`), then `rel = "specs/<junction-name>/passwd"`.
- Expected: raises `OutsideTreeError` (→ 404). Detection uses `GetFileAttributesW` for `FILE_ATTRIBUTE_REPARSE_POINT` on every path segment ending at the resolved leaf, NOT just the leaf itself.
- Edge cases: junction at a parent segment (must still reject); symlink instead of junction (POSIX) — `pytest.mark.skipif(sys.platform == "win32", reason="POSIX symlink fixture requires Developer Mode on Windows; junction case covers the same logic on win32")`; broken/dangling reparse point (still rejected, no leak that the target is missing); nested junctions (junction inside a junction).

#### 1.8 `test_safe_resolve_canonicalizes_first_then_asserts_containment`
- Inputs: `rel` whose normalized form lands inside EXPOSED_TREE but whose unnormalized form spells out `..`-traversal that incidentally cancels (e.g., `specs/development/../development/spec_driven/final_specs/spec.md`).
- Expected: returns the canonical absolute path; succeeds (the input does NOT escape after normalization).
- Edge cases: same input but with one extra `..` to actually escape (must reject); canonicalization that requires NTFS case-folding (input `SPECS/DEVELOPMENT/...` against on-disk `specs/development/...`); long-path prefix `\\?\` strip during canonicalization.

#### 1.9 `test_safe_resolve_case_folding_on_ntfs`
- Inputs: `rel = "Specs/Development/Spec_Driven/Final_Specs/Spec.md"` against on-disk lowercase tree.
- Expected: returns the path (NTFS is case-insensitive; `safe_resolve` case-folds for containment check). Skipped on POSIX: `pytest.mark.skipif(sys.platform != "win32", reason="POSIX FS is case-sensitive; case-folding is Windows-specific behavior")`.
- Edge cases: mixed casing in middle segments only; ASCII case-fold versus full Unicode (`İ` / `ı` / `I` / `i`) — must follow Win32 semantics, not Python's `str.lower()`.

#### 1.10 `test_safe_resolve_rejects_null_bytes_and_control_chars`
- Inputs: `rel = "specs/development/spec_driven/\x00etc/passwd"`, `rel = "specs/\x01\x02foo"`.
- Expected: raises `OutsideTreeError` (→ 404) before any filesystem call.
- Edge cases: bare NUL anywhere; characters in `0x00..0x1F` range; trailing space and trailing dot (NTFS strips silently); `:` and `*` and `?` (NTFS-illegal) reaching `safe_resolve` (must reject, not 500).

---

### Group 2 — `file_reader` (GET /api/file backing module)

Module: `backend/libs/file_reader.py`. Implements FR-3 and FR-5.

#### 2.1 `test_file_reader_extension_whitelist_allows_listed_types`
- Inputs: a path each ending in `.md, .json, .yaml, .yml, .jsonl, .txt, .png, .jpg`, all inside EXPOSED_TREE.
- Expected: each returns `{path, content, mtime, bytes}`; status 200.
- Edge cases: uppercase extensions (`.MD`, `.JSON`); double extensions (`spec.md.bak` is rejected — `.bak` is the effective extension); no extension at all (rejected as 415); extension-only filename (`.gitignore` — rejected unless explicitly whitelisted, NOT served).

#### 2.2 `test_file_reader_extension_whitelist_rejects_executables_and_scripts`
- Inputs: paths ending in `.exe, .bat, .cmd, .ps1, .sh, .py, .js, .ts, .html, .svg`.
- Expected: each returns 415 (Unsupported Media Type) — the response body contains a generic `{detail: "unsupported_extension"}` (no echo of the rejected path, to avoid enumeration leakage in error text).
- Edge cases: `.svg` MUST be rejected (NFR-9 — code-execution vector); `.html` MUST be rejected even though markdown renders to HTML (only the renderer can emit HTML, never the file_reader); double-extension (`malware.md.exe`) returns 415, NOT 200 with the wrong content type.

#### 2.3 `test_file_reader_size_cap_returns_413_above_1mb`
- Inputs: a fixture file of exactly 1 MB (1,048,576 bytes) → expect 200; a fixture of 1 MB + 1 byte → expect 413.
- Expected: 413 body is `{detail: {kind: "too_large"}}`; the file is NOT read into memory before the size check (`os.stat()` first).
- Edge cases: zero-byte file → 200 with empty `content`; sparse file whose logical size is huge but allocated size is tiny — use logical size; symlink-style indirection (already rejected by `safe_resolve`, but verify the size cap fires before any read attempt).

#### 2.4 `test_file_reader_single_404_for_missing_and_outside_tree`
- Inputs: `path = "specs/.../does_not_exist.md"` (real folder, missing file); `path = "../etc/passwd"` (outside tree, real file); `path = "specs/.../CON.md"` (reserved name).
- Expected: ALL three return identical 404 status with identical body shape and identical `Content-Length`. No timing side-channel between "missing inside tree" and "outside tree" (both perform a `safe_resolve` + `os.stat` and return early on either failure mode).
- Edge cases **[regression]**: a directory listing attempt should NOT be possible — passing the path to a directory returns 404 (or 415 if dir is treated as no-extension), never an index. Verify by enumerating: a path one level above the EXPOSED_TREE root (`/`) and a path that lands on an existing-but-non-whitelisted file (`.gitignore`) both return 404 and CANNOT be distinguished from a missing path.

#### 2.5 `test_file_reader_emits_nosniff_and_attachment_headers`
- Inputs: any allowed file.
- Expected: response carries `X-Content-Type-Options: nosniff` AND `Content-Disposition: attachment` (per FR-5). The `Content-Disposition` filename is the leaf basename, properly quoted (RFC 6266) when it contains spaces.
- Edge cases: filename with spaces; filename with non-ASCII (UTF-8 with `filename*=UTF-8''...` per RFC 5987); files that some browsers would otherwise sniff as HTML (a `.txt` containing `<html>...`) — `nosniff` MUST still be set; verify both headers on 200 AND on the 200-with-zero-bytes case (empty file).

#### 2.6 `test_file_reader_returns_correct_mtime_and_bytes`
- Inputs: a file with known mtime and known length.
- Expected: `mtime` is ISO 8601 UTC; `bytes` matches `os.stat().st_size`.
- Edge cases: file modified during read (race) — returns the mtime captured BEFORE the read (consistency); files on FAT32 with 2-second mtime granularity (informational only); negative mtime (pre-1970) — return as-is, do not crash.

#### 2.7 `test_file_reader_image_returns_base64_or_passthrough_per_contract`
- Inputs: a `.png` and a `.jpg` fixture.
- Expected: `content` is base64-encoded with a `data_encoding: "base64"` field, OR the API delivers binary directly with `Content-Type: image/png`/`image/jpeg` — pick one and assert it consistently. Headers still include `nosniff` and `attachment`.
- Edge cases: corrupted PNG (still served, no parsing); zero-byte image (200, empty content); EXIF-laden JPG (no metadata stripping in v1 — assert raw bytes are preserved).

---

### Group 3 — `file_writer` (PUT /api/file backing module)

Module: `backend/libs/file_writer.py`. Implements FR-6 / FR-7 / FR-8.

#### 3.1 `test_file_writer_atomic_temp_then_rename`
- Inputs: a write to `specs/.../scratch.md` with content `"hello"`.
- Expected: the writer creates a temp file in the SAME directory (so `os.replace` is atomic on the same volume), writes content + fsync, then `os.replace` to the final path. After success the temp file does NOT exist.
- Edge cases: write to a path on a different volume than `tempfile.gettempdir()` — verify temp is created on the target volume, not the system temp; concurrent writes to the same path (last writer wins; neither sees a half-written state); writer is interrupted (KeyboardInterrupt) between temp-write and rename — temp file remains, target file is untouched (caller's earlier content is preserved).

#### 3.2 `test_file_writer_body_cap_at_1mb`
- Inputs: body of 1 MB → 200; body of 1 MB + 1 byte → 413 with `{detail: {kind: "too_large"}}`.
- Expected: 413 fires BEFORE the body is fully buffered into a python string (stream check on `Content-Length`, then a hard cap on actually-read bytes). No partial file is ever written.
- Edge cases: chunked-transfer body without `Content-Length` — must still cap by counting accumulated bytes and abort when limit exceeded; client claims `Content-Length: 100` but sends 2 MB — hard cap catches it; body cap is enforced at the FastAPI level AND the spec mandates it at any reverse proxy (FR-7) — backend test asserts the FastAPI-level limit; reverse-proxy enforcement is asserted separately in system_tests.md.

#### 3.3 `test_file_writer_extension_validation_matches_reader`
- Inputs: PUT to `.md` (allowed) → 200; PUT to `.svg` → 415; PUT to `.png` / `.jpg` → 415 (image extensions are NOT writable in v1, per FR-8); PUT to `.exe` → 415.
- Expected: rejection happens BEFORE temp file creation so no detritus on disk.
- Edge cases: writing to a path that doesn't yet exist (must succeed if extension is allowed and path is inside the tree — but only inside whitelisted stage subfolders; the API layer enforces whitelist of writable subfolders); double extension (`foo.md.exe` → 415); zero-byte body to a `.md` path → 200 (empty file is valid); extension case (`.MD` → 200).

#### 3.4 `test_file_writer_first_16_bytes_must_be_valid_utf8_no_nul`
- Inputs: body whose first 16 bytes are valid UTF-8 ASCII → 200; body starting with a NUL byte → 415; body whose first byte is 0xFF (invalid UTF-8 start) → 415; body that is valid UTF-8 BOM (`﻿`) followed by ASCII → 200 (BOM is allowed).
- Expected: rejection returns `{detail: {kind: "not_text"}}` (or similar deterministic shape); no temp file is created on rejection.
- Edge cases: body shorter than 16 bytes → check what's available (e.g., empty file passes the check trivially; 5-byte body is checked for those 5 bytes); valid multi-byte UTF-8 sequence that happens to span the 16-byte boundary (must not falsely reject — decode the head as a stream); bytes that are valid UTF-8 but include a ` ` codepoint — reject (treated as embedded NUL); CRLF line endings preserved verbatim (do not normalize during write).

#### 3.5 `test_file_writer_returns_path_bytes_mtime_on_success`
- Inputs: a successful write of `"hello\n"` to a fresh path.
- Expected: response shape is `{path, bytes, mtime}`; `bytes == 6`; `mtime` is ISO 8601 UTC.
- Edge cases: write that overwrites an existing file — `mtime` advances; write where target was read-only (Windows) → 500 with a structured error, NOT a stack trace; disk full (rare to test, simulate by mocking `os.replace`) → 500 with a structured error and the temp file is cleaned up.

---

### Group 4 — `regen_prompt` (POST /api/regen-prompt assembler)

Module: `backend/libs/regen_prompt.py`. Implements FR-10/11/12. The prompt assembly is deterministic — same inputs, same output bytes.

#### 4.1 `test_regen_prompt_first_line_autonomous_header`
- Inputs: `{stages: ["interview", "research"], modules: {...}, autonomous: true}`.
- Expected: the returned `prompt` string's first line is exactly `# EXECUTION MODE: AUTONOMOUS` with no leading whitespace, no trailing characters, terminated by `\n`.
- Edge cases: the next non-blank line is the verbatim imperative sentence (asserted in 4.2); leading BOM is forbidden; CRLF vs LF — assert LF only.

#### 4.2 `test_regen_prompt_autonomous_imperative_line_verbatim`
- Inputs: same as 4.1.
- Expected: the second non-blank line equals exactly `Do not call AskUserQuestion. For anything unclear, use your best judgment, record the choice inline in the artifact, and keep going. Produce every requested artifact below in this single turn before stopping.` (FR-11(b)). Byte-for-byte; no rephrasing.
- Edge cases: this test pins the sentence as a string constant in the test file with a comment pointing at FR-11(b) — refactoring drift is the canonical failure mode; ensure the surrounding context (blank line above and below) does NOT break the assertion (use a regex with `\s*\n` separators).

#### 4.3 `test_regen_prompt_interactive_header_no_imperative`
- Inputs: `{autonomous: false}`.
- Expected: first line is `# EXECUTION MODE: INTERACTIVE`. The autonomous imperative sentence does NOT appear anywhere in the prompt body (assert by substring search).
- Edge cases: autonomous flag missing from request body → defaults to false → INTERACTIVE; autonomous flag is the string `"false"` instead of bool → 422 (Pydantic strict).

#### 4.4 `test_regen_prompt_inlines_revised_prompt_or_falls_back_to_raw`
- Inputs: a project with a non-empty `revised_prompt.md`; a project with NO `revised_prompt.md` but a `raw_prompt.md`.
- Expected: in the first case the prompt body inlines `revised_prompt.md` content verbatim; in the second case it inlines `raw_prompt.md` and labels the section accordingly.
- Edge cases: both files missing → 404 with a clear error (project does not exist); `revised_prompt.md` exists but is empty (zero bytes) → fall back to `raw_prompt.md`; `revised_prompt.md` exists and is large (use real revised file from this project — ~XX KB).

#### 4.5 `test_regen_prompt_lists_followups_in_numerical_order`
- Inputs: `user_input/follow_ups/` containing `001-...md, 002-...md, 010-...md, 003-...md` (out-of-order on disk, gaps allowed).
- Expected: the prompt's "Follow-ups" section lists `001, 002, 003, 010` in ascending numeric order (NOT lexicographic, NOT mtime).
- Edge cases: zero follow-ups → section header still present, body empty (or section omitted with the count = 0 in the breakdown); non-numeric prefix (`README.md` accidentally in the folder) → ignored, never included; duplicate sequence numbers (`001-foo.md`, `001-bar.md`) — both included, ordered by full filename as tiebreaker.

#### 4.6 `test_regen_prompt_inlines_promoted_md_when_nonempty`
- Inputs: stage `interview` selected; `interview/promoted.md` non-empty.
- Expected: the prompt includes a `### Pinned items (MUST survive regeneration)` section containing the verbatim content of `interview/promoted.md`. The header text is exact (per FR-11(f)).
- Edge cases: empty `promoted.md` → section is OMITTED entirely (not present with empty body); stage selected but `promoted.md` does not exist → section omitted; multiple stages with promoted.md → one section per stage in stage order.

#### 4.7 `test_regen_prompt_size_policy_warn_below_1mb`
- Inputs: a synthesized request whose assembled prompt would be (a) 30 KB, (b) 100 KB, (c) 600 KB, (d) 1.0 MB exactly, (e) 1 MB + 1 byte.
- Expected: (a) `warning: null`, status 200; (b)/(c)/(d) `warning: "<text>"` (warn-don't-truncate, status 200); (e) status 413 with `{detail: {kind: "too_large", bytes: <count>}}` and NO prompt body.
- Edge cases: the warning text is a stable constant — pin it in the test as a string; the prompt body is NEVER truncated when status is 200 (assert `bytes` equals `len(prompt.encode("utf-8"))`); the threshold is computed on the encoded byte length, NOT the python string length.

#### 4.8 `test_regen_prompt_constraints_section_includes_read_zero`
- Inputs: any valid request.
- Expected: the prompt closes with a `### Constraints` section. That section contains:
  - "regeneration deletes prior outputs first; new generation reads only the inputs" (read-zero contract — verbatim substring per FR-11(g) / AC-16).
  - References to `regen.delete.planned`, `regen.delete.completed`, `regen.write.completed` event types.
  - The four state surfaces (`CLAUDE.md`, `.claude/settings*`, `specs/{type}/{name}/`, `.audit/...`).
  - The parent-direct manager-spawn contract.
  - "Do not call AskUserQuestion in autonomous mode" (already enforced at top under AUTONOMOUS, but the constraints section restates it).
- Edge cases: the section header is `### Constraints` (three hashes, leading capital, exact spelling); ordering of bullets is stable across runs (sort keys); the read-zero sentence appears in INTERACTIVE prompts too (it's a regen contract, not an autonomous-only constraint).

#### 4.9 `test_regen_prompt_walks_each_selected_stage_with_invocation_and_modules`
- Inputs: `stages: ["interview", "validation"]`, `modules: {interview: ["all"], validation: ["security", "performance"]}`.
- Expected: the prompt contains one section per selected stage, each with the stage's invocation hint and the selected module list (and ONLY the selected modules).
- Edge cases: empty `modules` for a stage → defaults to "all modules of that stage" with a marker line; `stages = []` → 422 (at least one stage required); stage id not in the canonical six → 422.

#### 4.10 `test_regen_prompt_response_shape_and_counts`
- Inputs: any valid request.
- Expected: response is `{prompt, warning, selected_stages_count, follow_ups_count, autonomous, bytes}`; counts match what was actually inlined; `bytes == len(prompt.encode("utf-8"))`; `autonomous` echoes the request flag.
- Edge cases: zero stages → 422 (caught earlier); zero follow-ups → `follow_ups_count == 0` and the section is empty/omitted; flags coerced from non-bool → 422.

---

### Group 5 — `promotions` (pin/unpin)

Module: `backend/libs/promotions.py`. Implements FR-13 / FR-14 plus the `parse_promoted_text` helper consumed by validation strategy (general.md §6).

#### 5.1 `test_promote_post_appends_block_to_promoted_md`
- Inputs: POST `{project_type, project_name, stage_folder: "interview", source_file: "qa.md", item_id: "qa-r1-c2-q3", item_text: "...verbatim block..."}`.
- Expected: appends the block to `specs/{type}/{name}/interview/promoted.md`. The block is delimited with a header containing `item_id` so it can be parsed back. File is created if it didn't exist; existing pins are not disturbed.
- Edge cases: `promoted.md` does not exist yet → created with a leading title; `promoted.md` exists with no trailing newline → append still produces a clean separator; empty `item_text` → 422 (rejected at the API layer).

#### 5.2 `test_promote_post_idempotent_on_duplicate_item_id`
- Inputs: two consecutive POSTs with the same `item_id` and same `item_text`.
- Expected: `promoted.md` contains exactly ONE block for that `item_id` (second POST is a no-op or replaces in place); response on the second POST is 200 (not 409) and indicates idempotent behavior (e.g., `{status: "already_pinned"}` or 200 with the existing block returned).
- Edge cases: same `item_id` with DIFFERENT `item_text` (text drifted) → second POST replaces the body and updates the block (the user's most recent pin wins) — log this as a normal update; concurrent POSTs to the same `item_id` (race) → file lock or `os.replace`-based atomic rewrite ensures only one wins, no duplicate blocks.

#### 5.3 `test_promote_delete_removes_only_matching_block`
- Inputs: `promoted.md` with three pins (`item_id=A, B, C`); DELETE `{item_id: "B"}`.
- Expected: A and C remain verbatim; B's block (header + body) is removed; trailing whitespace between blocks is normalized but no other block's content is altered.
- Edge cases: DELETE for an `item_id` that doesn't exist → 404 (or 200 idempotent — pick one and assert); DELETE when `promoted.md` doesn't exist → 404; DELETE the last pin → file is left with just the title (or removed entirely — define and assert behavior).

#### 5.4 `test_promote_post_delete_roundtrip`
- Inputs: POST a pin, then DELETE the same pin, then GET `promoted.md`.
- Expected: the file ends up byte-identical to its pre-POST state (modulo a trailing newline).
- Edge cases: roundtrip across server restart (state is on disk, not in memory); roundtrip with multiple pins where the deleted one is in the middle.

#### 5.5 `test_promote_item_id_parsing_round_trips`
- Inputs: `parse_promoted_text` against a hand-built `promoted.md` with three blocks of varying body length, including a body containing the literal delimiter sequence.
- Expected: parser returns three records with correct `item_id` and `body`; bodies are byte-identical to what was POSTed (verbatim contract — pinned items survive regeneration with no whitespace drift beyond explicitly-tolerated normalization).
- Edge cases: body containing the block-header pattern verbatim — parser must use a delimiter strong enough that a body cannot accidentally start a new block (e.g., a UUID-style fence or a header with the `item_id` baked in); body containing CRLF or NUL byte (NUL must have been rejected at write-time per Group 3.4); body that ends without a trailing newline; multiple consecutive empty blocks.

#### 5.6 `test_promote_stage_folder_whitelist`
- Inputs: POST with `stage_folder` in the allowed set (`interview, findings, final_specs, validation`) → 200; with `stage_folder = "user_input"` → 422; with `stage_folder = "projects"` (stage 6) → 422 (FR-37 — stage 6 is excluded from promotion).
- Expected: rejection is at the API layer before any disk write.
- Edge cases: stage_folder casing variants (must match exactly); arbitrary path injected as `stage_folder` (`../etc`) — rejected as not-in-whitelist BEFORE any path-construction.

---

### Group 6 — `tree_walker` (GET /api/tree backing module)

Module: `backend/libs/tree_walker.py`. Implements FR-1 / FR-2. The single most important contract here is the **uniform `children` field name** — the consumer-walk regression from `spec_driven-20260502-clean` is in this module.

#### 6.1 `test_tree_walker_emits_children_field_uniformly` **[regression-2026-05-02-clean]**
- Inputs: a synthesized EXPOSED_TREE root with at least one each of `section, project, type, stage, file` nodes.
- Expected: every non-leaf node has a `children` array (possibly empty); NO node has a `projects`, `stages`, or `task_type.projects` field. Recursive descent uses `node["children"]` and ONLY `node["children"]`.
- Edge cases: an empty section (no projects) — `children: []` (NOT missing the field); a project with no stage subfolders (legitimate during pipeline mid-run) — `children: []`; a stage folder with only `promoted.md` and no other files — `children: [{...promoted.md}]`.

#### 6.2 `test_tree_consumer_walk` **[regression-2026-05-02-clean]**
- Inputs: a real `/api/tree` response from a fully-populated project.
- Expected: the test recursively descends `node.children` (Python equivalent of the frontend Sidebar's recursion: `for c in node["children"]: walk(c)`), reaches every leaf, and the count of leaves matches an independently-counted expected number derived from the EXPOSED_TREE definition (FR-2). Failure mode: any non-leaf is missing a `children` field, OR walking via `children` does not reach a known leaf.
- Edge cases: the test MUST use `node["children"]` literally — NOT `node.get("children", [])` (the latter masks the bug). If a non-leaf is missing `children`, the walk MUST raise KeyError. The test asserts every expected leaf path is visited (set equality, not just count).

#### 6.3 `test_tree_walker_type_tags_are_correct`
- Inputs: the synthesized tree from 6.1.
- Expected: each node has `type ∈ {section, file, type, project, stage}`; the top-level node containing CLAUDE.md / .claude/* is `section`; per-task-type group is `type`; per-project node is `project`; per-stage subfolder (`interview/`, `findings/`, etc.) is `stage`; everything else under a stage is `file`.
- Edge cases: the special files `changelog.md` and `<stage>/promoted.md` ARE `file` type (not `stage`); tree nodes do NOT have any extra `kind`/`category` keys (single source of truth on `type`).

#### 6.4 `test_tree_walker_includes_every_required_path_per_fr2`
- Inputs: a real on-disk repo with the documented structure.
- Expected: tree includes `CLAUDE.md`, every `.claude/agents/*.md`, every `.claude/skills/**/SKILL.md`, every `.claude/skills/agent_team/playbooks/*.md`, every `.claude/agent_refs/**/*.md`, and every canonical `specs/{type}/{name}/<stage>/` subfolder including their `promoted.md` sidecars and the `changelog.md`.
- Edge cases: a `specs/{type}/{name}/` with extra non-canonical subfolders (e.g., `notes/`) — NOT included; a project with `promoted.md` but no other stage files — `promoted.md` still appears under its stage; symlinks/junctions inside `specs/` — never traversed (depth-first walk skips reparse points; verify via integration with `safe_resolve`'s reparse-point check).

#### 6.5 `test_tree_walker_paths_are_forward_slash`
- Inputs: tree generated on Windows.
- Expected: every `path` field is forward-slash separated (NFR-13). No backslashes.
- Edge cases: paths with spaces or unicode; the `.claude/skills/agent_team/playbooks/research.md` path on Windows must serialize as `.claude/skills/agent_team/playbooks/research.md`, never with `\\`.

#### 6.6 `test_tree_walker_is_deterministic_within_a_directory`
- Inputs: same on-disk state called twice.
- Expected: byte-identical responses; sibling order is alphabetical (case-insensitive on NTFS, case-sensitive on POSIX — pick one and assert; spec implies alphabetical case-insensitive for cross-platform consistency).
- Edge cases: timestamp-sensitive sorts must NOT be used (mtime-based sort would be non-deterministic across rebuilds).

---

### Group 7 — `api` (FastAPI surface — verb whitelist, Origin/Host, error mapping)

Module: `backend/main.py` + `backend/libs/api_security.py`. Implements FR-9 / NFR-6 / NFR-7 + 413/415/404 mapping.

#### 7.1 `test_api_verb_whitelist_returns_405_on_patch_and_delete_to_file`
- Inputs: `PATCH /api/file?path=...`, `DELETE /api/file?path=...`.
- Expected: 405 Method Not Allowed; the `Allow` header lists only the supported verbs (`GET, PUT`).
- Edge cases: `OPTIONS` returns 200 with the same Allow header (CORS preflight); `HEAD` may be allowed for the file endpoint (verify decision and assert it consistently); arbitrary verb (`FROBNICATE`) → 405.

#### 7.2 `test_api_origin_validation_rejects_cross_origin_state_changes`
- Inputs: PUT/POST/DELETE with `Origin: http://evil.example.com`; same with `Origin: http://localhost:8765` (loopback alias) — implementation choice; same with `Origin: http://127.0.0.1:8765` (the bound origin).
- Expected: only `Origin: http://127.0.0.1:8765` is accepted; everything else returns 403 with a generic body; the `localhost:8765` alias decision is asserted explicitly (spec says "bound localhost" — assert exactly what the bound value is).
- Edge cases: `Origin` header missing → 403 (do NOT permit "no origin" as a fallback for browser-driven CSRF protection); `Origin: null` (sandboxed iframe) → 403; an `Origin` matching with a trailing slash (`http://127.0.0.1:8765/`) → 403 (must be exact match); GET requests are NOT subject to Origin validation (only state-changing routes per FR-9).

#### 7.3 `test_api_host_validation_rejects_dns_rebinding`
- Inputs: PUT/POST/DELETE with `Host: spec-driven.attacker.com`; `Host: 127.0.0.1:8765`; `Host: localhost:8765`; `Host: 127.0.0.1` (no port).
- Expected: only `Host: 127.0.0.1:8765` is accepted; everything else returns 403.
- Edge cases: `Host` header missing — 400 (HTTP/1.1 requires it); `Host` with a different port (`127.0.0.1:8000`) — 403; `Host` with an IPv6 form (`[::1]:8765`) — 403 (server is bound to IPv4 loopback only per FR-38).

#### 7.4 `test_api_error_mapping_413_415_404`
- Inputs: a request that triggers each of "too_large", "unsupported_extension", and "not_found".
- Expected: 413 → `{detail: {kind: "too_large"}}`; 415 → `{detail: "unsupported_extension"}` (deterministic shape); 404 → `{detail: "not_found"}` (single shape — no enumeration distinction between "outside tree" and "missing file").
- Edge cases: 413 from `GET /api/file` and 413 from `PUT /api/file` and 413 from `POST /api/regen-prompt` all use the same shape; 415 is never returned for write attempts to image extensions in v1 (per FR-8) — confirm those return 415; 404 body never echoes the requested path (no enumeration leak).

#### 7.5 `test_api_state_changing_routes_enforce_origin_host_collectively`
- Inputs: PUT, POST, DELETE under each of the four sanctioned mutation endpoints (`/api/file`, `/api/regen-prompt`, `/api/promote`, `/api/promote`).
- Expected: every one rejects bad Origin AND bad Host; coverage matrix: 4 routes × 2 headers = 8 cases all returning 403.
- Edge cases: a route with both bad Origin and bad Host returns 403 (single rejection, not 403 + 403); a route with bad Origin but good Host returns 403; same for inverse.

#### 7.6 `test_api_no_uncovered_state_changing_routes_exist`
- Inputs: enumerate FastAPI route table.
- Expected: every route with method in `{POST, PUT, DELETE, PATCH}` is in the sanctioned list `{PUT /api/file, POST /api/regen-prompt, POST /api/promote, DELETE /api/promote}` AND has Origin+Host validation. Any other state-changing route fails the test.
- Edge cases: dev-only debug routes must also be on the list or the test fails (no "I'll add this temporarily and forget"); routes mounted under a sub-router are still enumerated.

#### 7.7 `test_api_uvicorn_bind_127_0_0_1_only`
- Inputs: parse the Uvicorn invocation in `main.py` and the Makefile.
- Expected: bind host is `127.0.0.1`, port `8765`, NOT `0.0.0.0`. The string `0.0.0.0` does not appear in default invocation paths.
- Edge cases: env var override (`HOST=0.0.0.0`) is rejected at startup with a clear log line, OR the spec is enforced by hard-coding (assert one way and document); IPv6 wildcard `::` is also rejected.

---

## Frontend — `frontend/src/`

Test runner: Vitest + React Testing Library. Module paths are conventional; adjust to actual repo layout.

### Group 8 — `Sidebar` recursive descent

Module: `frontend/src/components/Sidebar.tsx`.

#### 8.1 `test_sidebar_renders_via_node_children` **[regression-2026-05-02-clean]**
- Inputs: a fixture `/api/tree` response with one section, two projects, and three stages each (per FR-1 shape).
- Expected: the rendered DOM contains one `data-testid="sidebar"`, leaves rendered with `data-testid="tree-leaf"`, and `data-testid="project-link"` on each project's `↗` link. The Sidebar component MUST descend `node.children` recursively — the test asserts every expected leaf is in the DOM AND is reached via the `<TreeNode>` recursion (not by a separate flat fetch).
- Edge cases: the fixture deliberately includes only `children` (no `projects`/`stages`). If the component reads `node.projects` or `node.task_type.projects`, the test fails — this is the canonical regression assertion. Empty `children` arrays render no leaves but the parent still appears.

#### 8.2 `test_sidebar_handles_deep_recursion`
- Inputs: a tree 8 levels deep (artificial but plausible — section → type → project → stage → subfolder → … ).
- Expected: every leaf is rendered; no React "key" warnings in `consoleErrors`.
- Edge cases: keys are stable across re-renders (not array indices); collapsed branches do NOT render their children but the toggle is interactable.

#### 8.3 `test_sidebar_top_level_sections_present`
- Inputs: standard fixture.
- Expected: at least the two top-level sections are present: "Claude Settings & Shared Context" and "Projects" (per FR-2 / journey 1).
- Edge cases: empty Projects section still shows the heading; empty CLAUDE settings is impossible (CLAUDE.md is always there).

---

### Group 9 — `Editor` (file edit pane)

Module: `frontend/src/components/Editor.tsx`. Implements FR-25 through FR-28.

#### 9.1 `test_editor_dirty_dot_appears_on_first_keystroke`
- Inputs: mount Editor with a baseline content `"hello"`; simulate one keystroke in the textarea (now content is `"helloX"`).
- Expected: the dirty-dot indicator (filled circle next to the toolbar filename) is in the DOM with a stable test id (e.g., `data-testid="dirty-dot"`).
- Edge cases: typing then deleting back to baseline → dirty-dot disappears (deep-equal compare); pasting same-text content (no change) → dirty-dot does NOT appear; whitespace-only changes still flip dirty (no auto-trim).

#### 9.2 `test_editor_dirty_dot_persists_across_save_errors`
- Inputs: mount Editor with baseline; user types a change; user clicks Save; mock the API to return 500.
- Expected: dirty-dot REMAINS visible after the failed save (FR-27 — content preserved across save failures); save-error banner appears with text `Could not save: <message>`; the textarea content is unchanged from what the user typed.
- Edge cases: 413 response (`{detail: {kind: "too_large"}}`) → banner says "Could not save: file too large" (or similar deterministic mapping); 415 response → banner names the cause; network error (no response) → banner says network error; multiple consecutive errors do NOT stack banners (single banner, latest error).

#### 9.3 `test_editor_dirty_dot_clears_on_save_success`
- Inputs: type a change; click Save; mock API returns 200 with new mtime.
- Expected: dirty-dot disappears; baseline content is updated to the saved text; subsequent identical typing does not re-flip dirty until a true delta from the new baseline.
- Edge cases: rapid type → save → type again → save (race) — the second save's baseline is post-first-save; FR-28 — after success, editor STAYS open (not auto-closed); the dirty-dot does not flicker between save-start and save-complete.

#### 9.4 `test_editor_save_button_remains_focusable_during_in_flight_error`
- Inputs: trigger a save error; verify Save button state.
- Expected: button is NOT disabled; Tab-focus reaches it; Ctrl+S retriggers Save (FR-25 — Save is "never disabled during an in-flight save error").
- Edge cases: Save during another in-flight save (double-click) — second click is debounced or queues; Discard during error reverts to baseline AND clears the banner; Close-editor during error prompts confirmation if dirty.

#### 9.5 `test_editor_discard_reverts_to_baseline`
- Inputs: type a change; click Discard.
- Expected: textarea content == baseline; dirty-dot disappears; banner (if any) clears.
- Edge cases: Discard with no dirty state is a no-op; Discard while save is in flight cancels the save (or completes it before reverting — pick one and assert).

---

### Group 10 — `QaView` parser (interview/qa.md structured view)

Module: `frontend/src/components/QaView.tsx` and its parser `frontend/src/lib/qa-parser.ts`. Implements FR-21 / FR-29 / FR-30 plus the autonomous-mode regression from `spec_driven-20260502-clean`.

#### 10.1 `test_qa_parser_accepts_interactive_form` **[regression-2026-05-02-clean]**
- Inputs: a fixture `qa.md` with `- Q: text` / `- A: text` pairs (interactive form).
- Expected: parser returns N rounds → categories → Q/A pairs; every Q has a matching A; counts match the fixture.
- Edge cases: indented bullets (under a category); multi-line Q or A bodies (continuation lines); `## Round 1`, `### category` headers with extra whitespace.

#### 10.2 `test_qa_parser_accepts_autonomous_form` **[regression-2026-05-02-clean]**
- Inputs: a fixture `qa.md` with `- A *(judgment call — chose X because Y)*: text` (autonomous form per FR-21 + agent_refs/validation/development.md move #10).
- Expected: parser returns the answer body correctly; the `judgment_call` annotation is captured into a separate field (e.g., `answer.judgmentCall = "chose X because Y"`) so QaView can render it as a badge; the Q/A pairing is preserved.
- Edge cases: judgment-call text with em-dash vs hyphen-minus; multi-line judgment-call body; autonomous-form A immediately following an interactive-form A in the same file (mixed file is legal); judgment-call body containing `*` or `(` characters.

#### 10.3 `test_qa_parser_fixture_is_a_real_on_disk_qa_md` **[regression-2026-05-02-clean]**
- Inputs: the fixture file is the actual `specs/development/spec_driven/interview/qa.md` (or a copy of a real autonomous-mode interview qa.md from a prior run).
- Expected: parser succeeds against the real artifact; rendered tree matches an expected snapshot.
- Edge cases: per agent_refs/validation/development.md move #10 ("fixture rotation") — when a new generation pattern appears, the fixture inventory grows by one. The test loads ALL fixtures in `frontend/test/fixtures/qa/*.md` and parses each; fail if any fixture fails to parse.

#### 10.4 `test_qa_parser_throws_on_malformed_input_so_error_boundary_catches` **[regression-2026-05-02-clean]**
- Inputs: a deliberately malformed `qa.md` (e.g., `### category` outside any `## Round`; or zero `- Q:` / `- A:` markers in a non-empty file).
- Expected: parser THROWS a `ParseError` with a descriptive message. It does NOT return an empty array silently (silent-pass is forbidden — see general.md §3).
- Edge cases: empty file → parser returns `{rounds: []}` (NOT an error — empty is valid); file with rounds but no Q/A inside → `{rounds: [{categories: []}]}` (also valid empty); file with one Q without an A → ParseError (Q/A pairing is required).

#### 10.5 `test_qa_view_error_boundary_falls_back_to_markdown_view` **[regression-2026-05-02-clean]**
- Inputs: render `<QaView source={malformed_qa_md} />` wrapped in the production Error Boundary; rely on React's componentDidCatch path.
- Expected: the Error Boundary catches the ParseError thrown DURING render; the fallback DOM is `<MarkdownView>` of the raw source PLUS a banner `Could not parse structured Q/A view; rendering raw markdown. (cause: <message>)` (FR-20).
- Edge cases **[critical]**: the Error Boundary MUST be a real class component with `componentDidCatch`/`getDerivedStateFromError`. A `try { return <QaView .../> } catch (e) { return <Fallback /> }` wrapper does NOT catch render-phase errors — this is the exact bug from `spec_driven-20260502-clean`. The test fails if the wrapper is the latter pattern (use `React.Component` instance check, or assert the boundary's class name).

#### 10.6 `test_qa_view_renders_blue_q_green_a_with_category_badge`
- Inputs: parsed QaView with a 3-round / 2-categories-per-round / 2-pairs-per-category structure.
- Expected: each Q block has the blue-tint className (or a stable test id `q-block`); each A block has the green-tint className; each category renders a colored badge in the header; ✎ pencils are present on each Q and A.
- Edge cases: category with zero Q/A is rendered with the badge but an empty body; long Q/A bodies do not overflow the container (CSS test); pencil stays in a stable position regardless of body length.

#### 10.7 `test_qa_view_per_block_editor_disables_file_level_edit`
- Inputs: open a per-Q editor via the ✎ pencil.
- Expected: the file-level ✎ Edit toolbar button is `disabled` (per FR-31) but still visible (NOT hidden).
- Edge cases: closing the per-Q editor re-enables the file-level ✎; opening multiple per-Q editors in sequence (cancel one, open another) keeps the file-level ✎ disabled while any per-block editor is open.

---

### Group 11 — `RegeneratePanel`

Module: `frontend/src/components/RegeneratePanel.tsx`. Implements FR-33 / FR-34 / AC-23 / AC-24 / AC-25.

#### 11.1 `test_regen_panel_section_breakdown_line_shape`
- Inputs: API response `{selected_stages_count: 2, follow_ups_count: 3, autonomous: true, bytes: 7860}` after Build prompt.
- Expected: the breakdown line beside Build prompt reads exactly `2 stages selected, 3 follow-ups inlined, autonomous=true, 7.86 KB` (or locale equivalent — pin the exact format).
- Edge cases: `autonomous: false` → `autonomous=false`; bytes < 1024 → "0.78 KB" or "780 B" (pick and assert the rounding rule); locale formatting (en-US is the test default; assert against `Intl.NumberFormat`); zero follow-ups → `0 follow-ups inlined`; one stage → `1 stage selected` (singular vs plural — pick one and assert; spec uses plural always for simplicity).

#### 11.2 `test_regen_panel_soft_wrap_toggle_default_on`
- Inputs: Build prompt → assembled prompt rendered.
- Expected: the "Wrap" checkbox is checked by default; the `<pre>` has CSS `white-space: pre-wrap; word-break: break-word` (soft-wrap on); unchecking switches to fixed-width with horizontal scroll.
- Edge cases: wrap state is NOT persisted (FR-33(f) — per-render only); reload the page → wrap is back ON; toggle does not affect Copy clipboard content (clipboard is the raw prompt either way).

#### 11.3 `test_regen_panel_copy_button_label_flip`
- Inputs: click Copy.
- Expected: clipboard receives the full prompt; button label changes to "Copied!" for ~1500 ms then reverts to "Copy"; the button has `aria-live="polite"` and a fixed minimum width so layout does not shift (assert min-width style is non-empty).
- Edge cases: clicking Copy again during the 1500ms window restarts the timer (does not double-flip); clipboard API permission denied → label flips to "Copy failed" or similar (define behavior); the button is always keyboard-focusable and Enter/Space activates it.

#### 11.4 `test_regen_panel_no_inline_render_on_413`
- Inputs: API response 413 with `{detail: {kind: "too_large", bytes: 1234567}}`.
- Expected: NO `regen-prompt-block` is rendered; an inline error message names the cause and the byte count; the panel itself stays expanded so the user can adjust modules and retry.
- Edge cases: a subsequent successful Build prompt clears the 413 error; the breakdown line is NOT shown for a 413 response (no successful assembly to describe); 413 during a previous build then a 200 in the new build replaces the error with the success block.

#### 11.5 `test_regen_panel_warning_banner_above_prompt_block`
- Inputs: API response 200 with `warning: "<some text>"`.
- Expected: a muted banner reading `warning: <text> — verify your selection before pasting` renders ABOVE the `regen-prompt-block`. The block itself still renders with the full prompt (warn-don't-truncate).
- Edge cases: `warning: null` → no banner; warning text containing markdown chars renders as plain text (no injection).

#### 11.6 `test_regen_panel_default_collapsed`
- Inputs: mount the panel for the first time.
- Expected: the surrounding `<details>` is closed (per AC-22); user must click the summary to expand.
- Edge cases: deep-link to a stage file does NOT auto-expand the panel; expanding then collapsing preserves any in-progress module selection (state lives in component, not in details).

---

### Group 12 — `autonomousMode` (localStorage hook)

Module: `frontend/src/hooks/useAutonomousMode.ts`. Implements FR-35 / AC-26.

#### 12.1 `test_autonomous_mode_localstorage_key_and_default_false`
- Inputs: fresh localStorage (key `spec_driven.autonomous_mode.v1` not present); mount the hook.
- Expected: hook returns `false`; localStorage is NOT written until the user toggles.
- Edge cases: localStorage value is `"true"` (string) → hook returns `true`; value is `"false"` → returns `false`; value is anything else (corrupt) → returns `false` (default) and logs a warning, does NOT throw.

#### 12.2 `test_autonomous_mode_persists_to_localstorage`
- Inputs: hook returns `[mode, setMode]`; call `setMode(true)`.
- Expected: localStorage[`spec_driven.autonomous_mode.v1`] === `"true"`; subsequent reads (new hook mount) return `true`.
- Edge cases: setMode(false) writes `"false"` (not removes the key); rapid toggle does not race localStorage writes.

#### 12.3 `test_autonomous_mode_subscribes_to_storage_event`
- Inputs: mount two hook instances (simulating two consumers — per-stage panel and project page); fire a `storage` event with `key: "spec_driven.autonomous_mode.v1", newValue: "true"`.
- Expected: both consumers re-render with the new value (FR-35 — cross-tab + same-tab propagation).
- Edge cases: `storage` event for a different key is ignored; `storage` event with `newValue: null` (key removed) → hook reverts to default `false`; same-tab updates propagate via an in-process subscription (storage events do NOT fire same-tab in the browser) — assert this branch separately.

#### 12.4 `test_autonomous_mode_unsubscribes_on_unmount`
- Inputs: mount + unmount the hook.
- Expected: the storage event listener is removed; firing storage events post-unmount does not invoke the hook's setter (no setState-on-unmounted-component warnings).
- Edge cases: multiple mount/unmount cycles do not leak listeners (assert via `window.addEventListener` mock counts).

---

## Cross-platform skip summary

The following cases use `pytest.mark.skipif(sys.platform == "win32", reason="...")` (or the inverse for Windows-only behavior), per agent_refs/validation/development.md move #5 / NFR-12:

- **1.7** — POSIX symlink fixture is skipped on Windows (Developer Mode required); the junction case exercises the equivalent reparse-point logic on win32. Mark: `@pytest.mark.skipif(sys.platform == "win32", reason="POSIX symlinks require Developer Mode on Windows; junction test case in same file covers reparse-point logic on win32")`.
- **1.9** — NTFS case-folding is win32-only. Mark: `@pytest.mark.skipif(sys.platform != "win32", reason="POSIX FS is case-sensitive; case-folding is Windows-specific behavior")`.
- **3.1 (concurrent-write race / atomic-replace cross-volume)** — `os.replace` atomicity across power-loss is best-effort on NTFS. Mark: `@pytest.mark.skipif(sys.platform == "win32", reason="os.replace power-loss atomicity is best-effort on NTFS")`.
- **6.5** — forward-slash paths are asserted on every OS, but the round-trip from `os.sep` is win32-only and uses `@pytest.mark.skipif(sys.platform != "win32", reason="backslash-to-forward-slash conversion is Windows-specific")`.

Skipping is fine; silent passing is not. Each skip MUST carry a reason string. A test that skips with no reason fails the lint check (general.md §3).

## Regression coverage summary (run `spec_driven-20260502-clean`)

The bugs from the prior clean-state run are covered by these cases — without all three, the regression is latent:

| Bug | Covered by |
|-----|-----------|
| Backend tree emitted `task_type.projects` / `project.stages` while frontend Sidebar walked `node.children` (Projects sidebar empty) | 6.1 `test_tree_walker_emits_children_field_uniformly`, 6.2 `test_tree_consumer_walk`, 8.1 `test_sidebar_renders_via_node_children` |
| QaView regex `/^-\s*A:\s*(.*)$/` missed autonomous-mode `- A *(judgment call …)*:` form (0 pairs parsed → ParseError → blank page) | 10.1, 10.2, 10.3 (real-on-disk fixture, autonomous form mandatory) |
| `try { return <QaView .../> } catch` didn't catch render-phase ParseError (no Error Boundary) → blank page on deep-link | 10.4 (parser throws), 10.5 (Error Boundary class component, fallback path reachable) |

Every other test in this file is contract-level coverage of the spec; the three listed are the ones that, had they existed, would have rejected the bad PR before merge.
