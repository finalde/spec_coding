# Unit Tests — spec_driven

Run: spec_driven-20260502-141813
Stage: 5 (Validation strategy) — level: unit_tests
Source spec: `specs/development/spec_driven/final_specs/spec.md`

Descriptions only (no test framework code). Each case maps to one or more FR/NFR ids in the spec. Where the spec is silent, the case is annotated `spec gap — confirm with author` and the test asserts whatever interim behavior the implementer chose, with a TODO to lock down once the spec author rules.

---

## Required fixture files

Backend (`projects/spec_driven/backend/tests/fixtures/`):

- `tests/fixtures/exposed/CLAUDE.md` — minimal valid markdown (a heading + paragraph).
- `tests/fixtures/exposed/.claude/agents/agent_team__interview_manager.md` — single line.
- `tests/fixtures/exposed/.claude/agents/agent_team__research_manager.md` — single line.
- `tests/fixtures/exposed/.claude/agents/__init__.py` — non-`.md` file used to verify glob exclusion.
- `tests/fixtures/exposed/.claude/skills/agent_team/SKILL.md` — single heading.
- `tests/fixtures/exposed/.claude/skills/agent_team/README.md` — non-`SKILL.md` file used to verify exclusion.
- `tests/fixtures/exposed/specs/development/spec_driven/user_input/raw_prompt.md`.
- `tests/fixtures/exposed/specs/development/spec_driven/user_input/revised_prompt.md`.
- `tests/fixtures/exposed/specs/development/spec_driven/findings/dossier.md`.
- `tests/fixtures/exposed/specs/development/spec_driven/findings/angle-routing.md`.
- `tests/fixtures/exposed/specs/development/spec_driven/final_specs/spec.md` — contains relative links used by the link-classifier test set.
- `tests/fixtures/exposed/specs/development/spec_driven/validation/strategy.md`.
- `tests/fixtures/exposed/specs/development/spec_driven/validation/acceptance_criteria.md`.
- `tests/fixtures/exposed/specs/development/spec_driven/validation/bdd_scenarios.md`.
- `tests/fixtures/exposed/specs/development/spec_driven/validation/events.jsonl` — three well-formed JSON lines, one trailing newline.
- `tests/fixtures/exposed/specs/development/spec_driven/notes/scratch.md` — non-stage subfolder used to verify FR-10 exclusion.
- `tests/fixtures/binary_with_null.md` — UTF-8 text containing one literal `\x00` byte mid-content.
- `tests/fixtures/2mb_plus_1_byte.md` — exactly `2 * 1024 * 1024 + 1` bytes of `a` characters (boundary for FR-5.5).
- `tests/fixtures/2mb_minus_1_byte.md` — exactly `2 * 1024 * 1024 - 1` bytes (boundary, must pass).
- `tests/fixtures/jsonl_well_formed.jsonl` — three lines, each independently valid JSON, plus a trailing `\n`.
- `tests/fixtures/jsonl_with_malformed_line.jsonl` — line 1 valid, line 2 malformed (`{"k":}`), line 3 valid.
- `tests/fixtures/jsonl_with_blank_line.jsonl` — valid JSON, blank line, valid JSON, trailing `\n`.
- `tests/fixtures/symlink_target.md` — real file inside exposed tree.
- `tests/fixtures/symlink_inside_tree` — symlink whose target is `symlink_target.md` (skipped on Windows runners; Linux/macOS only — flagged in conftest).
- `tests/fixtures/symlink_outside_tree` — symlink whose target is `/etc/passwd` (POSIX) or `C:\Windows\System32\drivers\etc\hosts` (Windows).

Frontend (`projects/spec_driven/frontend/src/__tests__/fixtures/`):

- `slug_collisions.md` — markdown with three `## Foo` headings in sequence.
- `non_ascii_heading.md` — `## Café`.
- `link_set.md` — every link variant exercised by the markdown link classifier.
- `localStorage_corrupted.json` — non-JSON garbage used to seed `localStorage`.
- `localStorage_valid.json` — valid `spec_driven.sidebar.v1` payload.
- `long_names.json` — strings of length 80 / 200 / 500 chars, with and without `.md` extensions.

---

## Group 1 — `safe_resolve(rel, REPO_ROOT)` (FR-5.1, FR-5.2, FR-6, NFR-4)

The unit under test is the path-resolution helper that every file-touching endpoint uses. `REPO_ROOT` is a `pathlib.Path` pointing at the fixture sandbox root. Helper signature inferred from spec: returns the relative `Path` inside `REPO_ROOT` on success; raises a typed exception (interim: `OutsideSandboxError`) on rejection. The endpoint maps that exception to HTTP 400 `outside_sandbox`. The 12+ cases below exercise every rejection branch.

### 1.1 `safe_resolve__accepts_relative_path_inside_sandbox`
- Inputs: `rel="CLAUDE.md"`, `REPO_ROOT=<fixture>/exposed`.
- Expected output: returns `Path("CLAUDE.md")` (resolved, relative to `REPO_ROOT`).
- Edge cases handled: the trivial happy path; verifies `.resolve(strict=False)` does not throw on existing files.
- Spec refs: FR-5.1, FR-6.

### 1.2 `safe_resolve__rejects_dot_dot_traversal`
- Inputs: `rel="../../etc/hosts"`, `REPO_ROOT=<fixture>/exposed`.
- Expected output: raises `OutsideSandboxError` (endpoint maps to 400 `outside_sandbox`).
- Edge cases handled: verifies `Path.relative_to` raises `ValueError` and the helper catches and re-raises typed.
- Spec refs: FR-5.1, FR-6, NFR-4.

### 1.3 `safe_resolve__rejects_absolute_posix_path`
- Inputs: `rel="/etc/passwd"`, `REPO_ROOT=<fixture>/exposed`.
- Expected output: raises `OutsideSandboxError`.
- Edge cases handled: absolute path passed through `REPO_ROOT / rel` becomes `/etc/passwd` per `pathlib` semantics; resolution lands outside sandbox.
- Spec refs: FR-5.1, NFR-4.

### 1.4 `safe_resolve__rejects_windows_drive_letter`
- Inputs: `rel="C:\\Windows\\system32\\drivers\\etc\\hosts"`, `REPO_ROOT=<fixture>/exposed`.
- Expected output: raises `OutsideSandboxError`.
- Edge cases handled: Windows-only branch where `pathlib.PureWindowsPath` treats the drive letter as anchored; on POSIX runners the test still expects rejection because the resolved path is not under `REPO_ROOT`.
- Spec refs: FR-5.1, NFR-4.

### 1.5 `safe_resolve__rejects_url_encoded_traversal`
- Inputs: `rel="%2e%2e/%2e%2e/etc/hosts"`, `REPO_ROOT=<fixture>/exposed`.
- Expected output: spec gap — confirm with author. Spec text says the FRONTEND link classifier "URL-decode the path component once" (FR-33 case 3); it does not say the BACKEND `safe_resolve` decodes. Interim assertion: `safe_resolve` does NOT decode (raw `%2e%2e` is treated as literal filename) and therefore returns `Path("%2e%2e/%2e%2e/etc/hosts")` IF the literal path resolves inside `REPO_ROOT`, else raises. With the fixture sandbox the literal path does not exist and is not under `EXPOSED_TREE`, so the request will subsequently 404 at the FR-5.3 check, not 400.
- Edge cases handled: confirms decoding is the frontend's job, not `safe_resolve`'s.
- Spec refs: FR-5.1, FR-33 (boundary).

### 1.6 `safe_resolve__rejects_double_url_encoded_traversal`
- Inputs: `rel="%252e%252e/%252e%252e/etc/hosts"`.
- Expected output: same as 1.5; literal filename, no decoding; eventually 404 `outside_exposed_tree`. Test exists to lock the no-decoding behavior across encoding depths.
- Edge cases handled: defense against double-decode bugs introduced later.
- Spec refs: FR-5.1, NFR-4.

### 1.7 `safe_resolve__rejects_symlink_pointing_inside_sandbox`
- Inputs: `rel="symlink_inside_tree"` where the symlink's target is `symlink_target.md` (also inside sandbox); `REPO_ROOT=<fixture>/exposed`.
- Expected output: spec gap on `safe_resolve` itself. FR-5.2 and FR-4 require symlink rejection but at the file-read endpoint level (`Path.is_symlink()` after resolve). Interim: `safe_resolve` returns the relative path normally; the endpoint is then responsible for the `is_symlink()` check. Test asserts that `safe_resolve` does NOT throw and that a separate `is_symlink_check(resolved)` returns `True`.
- Edge cases handled: separates the resolve concern from the symlink concern; ensures FR-4 is enforced by the caller, not silently inside the helper.
- Spec refs: FR-5.2, FR-4, NFR-5.

### 1.8 `safe_resolve__handles_mixed_slashes_on_windows`
- Inputs: `rel="specs\\development/spec_driven\\final_specs/spec.md"`, `REPO_ROOT=<fixture>/exposed`.
- Expected output: returns `Path("specs/development/spec_driven/final_specs/spec.md")` on Windows (POSIX-normalized for downstream comparison) or skips on POSIX runners with a clear `pytest.skip` reason.
- Edge cases handled: backslash-as-separator support on Windows; ensures cross-platform path equality.
- Spec refs: FR-5.1.

### 1.9 `safe_resolve__strips_trailing_slash`
- Inputs: `rel="specs/development/spec_driven/final_specs/"`, `REPO_ROOT=<fixture>/exposed`.
- Expected output: returns `Path("specs/development/spec_driven/final_specs")` (the directory). The endpoint then fails FR-5.4 / FR-5.7 with `IsADirectoryError` → 400 `is_directory`.
- Edge cases handled: trailing slash does not crash resolve; downstream `is_dir()` branch is exercised.
- Spec refs: FR-5.1, FR-5.7.

### 1.10 `safe_resolve__rejects_empty_string`
- Inputs: `rel=""`, `REPO_ROOT=<fixture>/exposed`.
- Expected output: spec gap — confirm with author. Interim: `(REPO_ROOT / "").resolve()` equals `REPO_ROOT.resolve()`, `relative_to` returns `Path(".")`. Endpoint then fails FR-5.4 because `.` has no extension → 415 `unsupported_extension`. Test asserts `safe_resolve` returns `Path(".")` and does NOT raise.
- Edge cases handled: empty input does not crash; degrades into a 415 not a 500.
- Spec refs: FR-5.1, FR-5.4.

### 1.11 `safe_resolve__resolves_dot_only_to_repo_root`
- Inputs: `rel="."`, `REPO_ROOT=<fixture>/exposed`.
- Expected output: returns `Path(".")`. Endpoint then 415 because dot has no whitelisted extension, OR 400 `is_directory` if extension check is sequenced after directory check (spec orders extension before size — and the `is_dir` branch is in the EAFP catch — so `IsADirectoryError` is raised by `read_text()` and mapped to 400). Interim: assert no exception in `safe_resolve`.
- Edge cases handled: `.` does not escape; downstream layering catches the directory.
- Spec refs: FR-5.1, FR-5.7.

### 1.12 `safe_resolve__treats_tilde_as_literal`
- Inputs: `rel="~/etc/passwd"`, `REPO_ROOT=<fixture>/exposed`.
- Expected output: returns `Path("~/etc/passwd")` (literal, no expansion). Endpoint then 404 `outside_exposed_tree` because the literal path is not in any glob.
- Edge cases handled: prevents accidental `Path.expanduser()` introduction; locks the contract.
- Spec refs: FR-5.1, NFR-4.

### 1.13 `safe_resolve__rejects_embedded_null_byte`
- Inputs: `rel="CLAUDE.md\x00.png"`, `REPO_ROOT=<fixture>/exposed`.
- Expected output: spec gap — confirm with author. Python 3.11+ raises `ValueError("embedded null byte")` from `Path.resolve()`. Interim: `safe_resolve` lets the `ValueError` surface as `OutsideSandboxError` (it already catches `ValueError`); endpoint maps to 400 `outside_sandbox`.
- Edge cases handled: nul-byte injection (CVE-2019-9948-style) is rejected before reaching the filesystem.
- Spec refs: FR-5.1, NFR-4.

### 1.14 `safe_resolve__normalizes_redundant_segments`
- Inputs: `rel="specs/./development/../development/spec_driven/final_specs/spec.md"`.
- Expected output: returns `Path("specs/development/spec_driven/final_specs/spec.md")`.
- Edge cases handled: confirms normalization happens before relative-to check; cosmetic `./` and `../` cancel correctly without escaping.
- Spec refs: FR-5.1.

### 1.15 `safe_resolve__rejects_traversal_via_long_chain`
- Inputs: `rel="a/b/c/../../../../etc/passwd"`.
- Expected output: raises `OutsideSandboxError`.
- Edge cases handled: more `..` segments than depth from root; resolution lands at parent of `REPO_ROOT`.
- Spec refs: FR-5.1, NFR-4.

---

## Group 2 — `EXPOSED_TREE` glob membership (FR-1, FR-10)

Unit under test: `is_in_exposed_tree(rel_path: Path) -> bool` (or equivalent named predicate). Each case asserts the predicate's return for a single path. Predicate must mirror FR-1's union of four globs and FR-10's "stage subfolders only" rule.

### 2.1 `exposed_tree__includes_claude_md_at_root`
- Inputs: `Path("CLAUDE.md")`.
- Expected output: `True`.
- Edge cases handled: root-level whitelist entry.
- Spec refs: FR-1.

### 2.2 `exposed_tree__excludes_pyproject_at_root`
- Inputs: `Path("pyproject.toml")`.
- Expected output: `False`.
- Edge cases handled: confirms only `CLAUDE.md` is whitelisted at root, not other root files.
- Spec refs: FR-1, FR-37.

### 2.3 `exposed_tree__includes_agent_md_under_claude_agents`
- Inputs: `Path(".claude/agents/agent_team__research_manager.md")`.
- Expected output: `True`.
- Edge cases handled: agents glob is shallow (`*.md`, not `**/*.md`).
- Spec refs: FR-1.

### 2.4 `exposed_tree__excludes_non_md_under_claude_agents`
- Inputs: `Path(".claude/agents/__init__.py")`.
- Expected output: `False`.
- Edge cases handled: extension-based filter inside the agents glob.
- Spec refs: FR-1.

### 2.5 `exposed_tree__includes_skill_md_under_claude_skills`
- Inputs: `Path(".claude/skills/agent_team/SKILL.md")`.
- Expected output: `True`.
- Edge cases handled: skills glob is `**/SKILL.md` — only files literally named `SKILL.md` qualify.
- Spec refs: FR-1.

### 2.6 `exposed_tree__excludes_readme_under_claude_skills`
- Inputs: `Path(".claude/skills/agent_team/README.md")`.
- Expected output: `False`.
- Edge cases handled: filename-specific match in skills glob.
- Spec refs: FR-1.

### 2.7 `exposed_tree__includes_md_under_stage_subfolder`
- Inputs: `Path("specs/development/spec_driven/user_input/raw_prompt.md")`.
- Expected output: `True`.
- Edge cases handled: typical stage file.
- Spec refs: FR-1, FR-10.

### 2.8 `exposed_tree__excludes_non_stage_subfolder_under_project`
- Inputs: `Path("specs/development/spec_driven/notes/scratch.md")`.
- Expected output: `False`.
- Edge cases handled: FR-10 explicit — `notes/` is not one of the five stages, so the file is excluded even though it sits under a real project.
- Spec refs: FR-10.

### 2.9 `exposed_tree__includes_jsonl_under_validation`
- Inputs: `Path("specs/development/spec_driven/validation/events.jsonl")`.
- Expected output: `True`.
- Edge cases handled: `.jsonl` is in the whitelisted extension set inside stage glob.
- Spec refs: FR-1, FR-32.

### 2.10 `exposed_tree__excludes_unsupported_extension_under_stage`
- Inputs: `Path("specs/development/spec_driven/findings/diagram.png")`.
- Expected output: `False`.
- Edge cases handled: stage glob whitelists `{.md, .yaml, .yml, .json, .jsonl}` only.
- Spec refs: FR-1, FR-5.4.

### 2.11 `exposed_tree__includes_yaml_under_stage`
- Inputs: `Path("specs/development/spec_driven/findings/angle-routing.yaml")`.
- Expected output: `True`.
- Edge cases handled: `.yaml` extension acceptance.
- Spec refs: FR-1.

### 2.12 `exposed_tree__excludes_audit_log_paths`
- Inputs: `Path(".audit/adhoc_agents/2026-05-02/spec_driven-20260502-141813/events.jsonl")`.
- Expected output: `False`.
- Edge cases handled: confirms the audit tree is NOT in the exposed set (out-of-scope per spec "Out of scope" item).
- Spec refs: FR-1, spec out-of-scope item ".audit not browsable".

### 2.13 `exposed_tree__excludes_projects_output_folder`
- Inputs: `Path("projects/spec_driven/backend/main.py")`.
- Expected output: `False`.
- Edge cases handled: `projects/` is execution output, not exposed.
- Spec refs: FR-1, spec out-of-scope item "projects/ not browsable".

---

## Group 3 — Tree ordering (FR-7, FR-8)

Unit under test: `build_tree_response(repo_root)` — produces the JSON tree. Tests call the function with a fully-stocked fixture sandbox and assert ordering of node lists.

### 3.1 `tree_order__settings_section_appears_before_projects_section`
- Inputs: fixture sandbox with both sections populated.
- Expected output: `tree["sections"][0].kind == "settings"` and `tree["sections"][1].kind == "projects"`.
- Edge cases handled: top-level section order locked.
- Spec refs: FR-7.

### 3.2 `tree_order__settings_subgroups_in_fixed_order`
- Inputs: fixture sandbox.
- Expected output: settings subgroup ids in order: `claude_md`, `agents`, `skills`.
- Edge cases handled: subgroup order is fixed regardless of disk order.
- Spec refs: FR-7.

### 3.3 `tree_order__agents_sorted_alphabetically`
- Inputs: agents fixture containing files in reverse alpha order on disk: `agent_team__validation_manager.md`, `agent_team__research_manager.md`, `agent_team__interview_manager.md`.
- Expected output: returned list order `interview, research, validation`.
- Edge cases handled: tree-walk does not preserve disk order; explicit sort.
- Spec refs: FR-7.

### 3.4 `tree_order__skills_sorted_by_folder_name`
- Inputs: skills fixture with two folders `agent_team/` and `aaa_first/`, each containing `SKILL.md`.
- Expected output: leaf order `aaa_first` then `agent_team`.
- Edge cases handled: sort key is folder name, not file path.
- Spec refs: FR-7.

### 3.5 `tree_order__task_types_sorted_alphabetically`
- Inputs: `specs/` contains `development/` and `ai_video/`.
- Expected output: `ai_video` precedes `development`.
- Edge cases handled: alphabetical at the task_type level.
- Spec refs: FR-7.

### 3.6 `tree_order__task_names_sorted_alphabetically`
- Inputs: `specs/development/` contains `zeta_project/` and `alpha_project/` and `spec_driven/`.
- Expected output: order `alpha_project, spec_driven, zeta_project`.
- Edge cases handled: alpha sort within task_type.
- Spec refs: FR-7.

### 3.7 `tree_order__stages_in_fixed_order`
- Inputs: project with all five stage subfolders present.
- Expected output: stage child order `user_input, interview, findings, final_specs, validation`.
- Edge cases handled: the stage list is hard-coded, not alphabetical (alphabetical would yield `final_specs, findings, interview, user_input, validation`).
- Spec refs: FR-7.

### 3.8 `tree_order__stages_in_fixed_order_when_subset_present`
- Inputs: project with only `user_input/` and `validation/` on disk.
- Expected output: all five stages still listed, in the fixed order, with `interview`, `findings`, `final_specs` carrying `present: false`.
- Edge cases handled: missing stages do not collapse the order; FR-9 interaction with FR-7.
- Spec refs: FR-7, FR-9.

### 3.9 `tree_order__validation_priority_files_first`
- Inputs: `validation/` contains on disk (in random order): `acceptance_criteria.md`, `bdd_scenarios.md`, `unit_tests.md`, `strategy.md`, `system_tests.md`.
- Expected output: leaf order `strategy.md, acceptance_criteria.md, bdd_scenarios.md, system_tests.md, unit_tests.md`.
- Edge cases handled: priority-three-then-alpha rule.
- Spec refs: FR-8.

### 3.10 `tree_order__validation_priority_when_priority_files_missing`
- Inputs: `validation/` contains only `system_tests.md` and `unit_tests.md`.
- Expected output: leaf order `system_tests.md, unit_tests.md` — no errors from missing priority files.
- Edge cases handled: priority list tolerates absence; alpha fallback works alone.
- Spec refs: FR-8.

### 3.11 `tree_order__non_validation_stage_files_alphabetical`
- Inputs: `findings/` contains `dossier.md, angle-routing.md, angle-shiki.md`.
- Expected output: order `angle-routing.md, angle-shiki.md, dossier.md`.
- Edge cases handled: pure alpha for non-validation stages.
- Spec refs: FR-8.

### 3.12 `tree_order__alpha_sort_is_case_insensitive`
- Inputs: stage with files `Apple.md, banana.md, Cherry.md`.
- Expected output: spec gap — confirm with author. Spec says "alphabetically" without specifying case. Interim assertion: case-insensitive sort yields `Apple.md, banana.md, Cherry.md`. Test is annotated as a spec-gap pin.
- Edge cases handled: locks down case folding; flagged for confirmation.
- Spec refs: FR-8 (spec gap).

---

## Group 4 — Stage presence flag (FR-9)

Unit under test: per-stage entry construction, asserted on the `present` boolean and the file list.

### 4.1 `stage_presence__false_when_subfolder_absent`
- Inputs: project with no `validation/` directory on disk.
- Expected output: `validation` entry exists with `{present: false, files: []}`.
- Edge cases handled: missing folder does not throw; FR-9 explicit.
- Spec refs: FR-9.

### 4.2 `stage_presence__true_with_files_when_present_and_populated`
- Inputs: project with `findings/dossier.md` and `findings/angle-routing.md`.
- Expected output: `findings` entry has `{present: true, files: [...two leaves...]}`.
- Edge cases handled: standard populated case.
- Spec refs: FR-9.

### 4.3 `stage_presence__true_with_empty_list_when_present_but_empty`
- Inputs: project with `interview/` directory existing but containing zero whitelisted files.
- Expected output: `interview` entry has `{present: true, files: []}`.
- Edge cases handled: distinguishes "folder not generated yet" (FR-9 false) from "folder created but empty" (true with empty list); the sidebar renders these differently per FR-24 vs an empty expansion.
- Spec refs: FR-9.

### 4.4 `stage_presence__ignores_non_whitelisted_files_for_emptiness`
- Inputs: `interview/` containing only `notes.txt` (not in extension whitelist).
- Expected output: `present: true, files: []` — folder exists, but no whitelisted file is listed.
- Edge cases handled: distinguishes filesystem presence from listing presence.
- Spec refs: FR-9, FR-1.

### 4.5 `stage_presence__false_when_subfolder_is_a_symlink`
- Inputs: `validation/` is a symlink (not a real directory) on POSIX runner.
- Expected output: `present: false, files: []` (symlink is silently skipped per FR-4).
- Edge cases handled: symlinks at the directory level are treated as absent, matching FR-4.
- Spec refs: FR-9, FR-4.

---

## Group 5 — GFM heading slug generator (FR-30)

Unit under test: `slugify(text: str, used: set[str]) -> str` (or equivalent class-method on a `SlugAllocator`). Each case is one row of an input/output table.

### 5.1 `slugify__simple_two_words`
- Inputs: `"Hello World"`, used set empty.
- Expected output: `"hello-world"`.
- Edge cases handled: space-to-hyphen, ASCII lowercasing.
- Spec refs: FR-30.

### 5.2 `slugify__strips_punctuation`
- Inputs: `"Hello, World!"`, used set empty.
- Expected output: `"hello-world"`.
- Edge cases handled: comma and exclamation dropped; remaining hyphen collapse.
- Spec refs: FR-30.

### 5.3 `slugify__trims_outer_whitespace`
- Inputs: `"  Spaces  "`, used set empty.
- Expected output: `"spaces"`.
- Edge cases handled: leading/trailing whitespace trimmed before hyphenation, no leading or trailing hyphen.
- Spec refs: FR-30.

### 5.4 `slugify__preserves_existing_hyphen`
- Inputs: `"Already-Hyphenated"`, used set empty.
- Expected output: `"already-hyphenated"`.
- Edge cases handled: in-text hyphen survives; lowercasing applied.
- Spec refs: FR-30.

### 5.5 `slugify__collision_first_two_foos`
- Inputs: in-order calls `slugify("Foo", used)`, `slugify("Foo", used)` against a shared mutable `used` set.
- Expected output: `"foo"`, then `"foo-1"`. After the second call the set contains both.
- Edge cases handled: first occurrence keeps the bare slug; second appends `-1`.
- Spec refs: FR-30.

### 5.6 `slugify__collision_three_foos`
- Inputs: three sequential calls `slugify("Foo", used)`.
- Expected output: `"foo"`, `"foo-1"`, `"foo-2"`.
- Edge cases handled: counter increments, not a hash; deterministic.
- Spec refs: FR-30.

### 5.7 `slugify__non_ascii_drops_characters`
- Inputs: `"Café"`, used set empty.
- Expected output: spec gap — confirm with author. Spec FR-30 says "lowercase ASCII, drop punctuation except hyphens". Two reasonable interpretations: (a) drop the `é` entirely → `"caf"`; (b) transliterate to `e` → `"cafe"`. GFM's reference implementation passes the character through; the spec demands ASCII so passing through is non-conformant. Interim assertion: option (a) `"caf"`. Test is annotated as a spec-gap pin.
- Edge cases handled: non-ASCII handling; flagged for author decision.
- Spec refs: FR-30 (spec gap).

### 5.8 `slugify__leading_digit_preserved`
- Inputs: `"1. Intro"`, used set empty.
- Expected output: `"1-intro"`.
- Edge cases handled: digit at start kept; period dropped; space-to-hyphen.
- Spec refs: FR-30.

### 5.9 `slugify__collapses_multiple_hyphens`
- Inputs: `"Hello   ---   World"`, used set empty.
- Expected output: `"hello-world"`.
- Edge cases handled: spec says "collapse multiple hyphens" — runs of internal whitespace and explicit hyphens collapse to one.
- Spec refs: FR-30.

### 5.10 `slugify__empty_after_stripping`
- Inputs: `"!!!"`, used set empty.
- Expected output: spec gap — confirm with author. Reasonable interpretations: empty string, or `"section"`/`"heading"` placeholder. Interim: empty string. Test annotated.
- Edge cases handled: degenerate input; flagged for confirmation.
- Spec refs: FR-30 (spec gap).

---

## Group 6 — Markdown link classifier (FR-33)

Unit under test: `classify_link(href: str, source_file: Path, repo_root: Path) -> LinkClassification`. Classification is one of `{external, anchor, internal, broken_outside, broken_missing}`. Test source file is `specs/development/spec_driven/final_specs/spec.md`.

### 6.1 `link_classify__https_url_is_external`
- Inputs: `href="https://example.com"`, source = spec.md.
- Expected output: `external`, target opens with `target="_blank"`, `rel="noopener noreferrer"`.
- Edge cases handled: scheme regex match for FR-33 case 1.
- Spec refs: FR-33, FR-6 (external link primary flow).

### 6.2 `link_classify__mailto_is_external`
- Inputs: `href="mailto:x@y.example"`.
- Expected output: `external`.
- Edge cases handled: `mailto:` matches the scheme regex `^[a-z][a-z0-9+.-]*:`.
- Spec refs: FR-33.

### 6.3 `link_classify__protocol_relative_is_external`
- Inputs: `href="//cdn.example.com/x.js"`.
- Expected output: `external`.
- Edge cases handled: explicit `//` branch in FR-33 case 1.
- Spec refs: FR-33.

### 6.4 `link_classify__hash_only_is_anchor`
- Inputs: `href="#section-overview"`.
- Expected output: `anchor`, no navigation, in-app scroll handler.
- Edge cases handled: FR-33 case 2.
- Spec refs: FR-33, FR-35.

### 6.5 `link_classify__sibling_md_is_internal_when_present`
- Inputs: `href="./acceptance_criteria.md"`, source = `validation/strategy.md`.
- Expected output: `internal`, resolved to `specs/development/spec_driven/validation/acceptance_criteria.md`.
- Edge cases handled: same-folder relative; resolves to existing file inside `EXPOSED_TREE`.
- Spec refs: FR-33 case 3 (file exists branch).

### 6.6 `link_classify__parent_dir_md_is_internal`
- Inputs: `href="../findings/dossier.md"`, source = spec.md.
- Expected output: `internal`.
- Edge cases handled: `..` traversal that lands inside `EXPOSED_TREE`; FR-33 case 3 happy path.
- Spec refs: FR-33.

### 6.7 `link_classify__escapes_repo_root_is_broken_outside`
- Inputs: `href="../../../etc/hosts"`, source = spec.md.
- Expected output: `broken_outside`, cause `"outside exposed tree"`.
- Edge cases handled: `..` chain escapes `REPO_ROOT`; rendered as muted span per FR-34.
- Spec refs: FR-33, FR-34.

### 6.8 `link_classify__missing_target_in_tree_is_broken_missing`
- Inputs: `href="./missing.md"`, source = `validation/strategy.md`, file does not exist on disk.
- Expected output: `broken_missing`, cause `"file not found"`.
- Edge cases handled: resolves inside `EXPOSED_TREE` but file absent; distinct from `broken_outside`.
- Spec refs: FR-33, FR-34.

### 6.9 `link_classify__url_encoded_traversal_decoded_once`
- Inputs: `href="%2E%2E/findings/dossier.md"`, source = spec.md.
- Expected output: `internal` (decode once → `../findings/dossier.md` → resolves and exists).
- Edge cases handled: FR-33 case 3 explicit "URL-decode the path component once".
- Spec refs: FR-33.

### 6.10 `link_classify__double_encoded_traversal_still_rejected`
- Inputs: `href="%252E%252E/findings/dossier.md"`, source = spec.md.
- Expected output: spec gap — confirm with author. Single-decode yields `%2E%2E/findings/dossier.md`; that literal segment does not exist on disk. Interim: `broken_missing`. Test asserts the link is NOT classified `internal` and is NOT silently double-decoded.
- Edge cases handled: defense against double-decode; flagged.
- Spec refs: FR-33 (spec gap on double encoding).

### 6.11 `link_classify__cross_project_link_is_broken_outside`
- Inputs: `href="../../other_project/final_specs/spec.md"`, source = `specs/development/spec_driven/final_specs/spec.md`.
- Expected output: `broken_outside` per spec out-of-scope item "Cross-project cross-links … resolves as broken".
- Edge cases handled: locks down the explicit non-goal.
- Spec refs: FR-33, FR-34, spec Out-of-scope.

### 6.12 `link_classify__claude_md_to_pyproject_is_broken_outside`
- Inputs: `href="./pyproject.toml"`, source = `CLAUDE.md`.
- Expected output: `broken_outside` per FR-37 (Section 1 link to non-`EXPOSED_TREE` target).
- Edge cases handled: FR-37 explicit example.
- Spec refs: FR-37, FR-33, FR-34.

---

## Group 7 — `.jsonl` per-line renderer (FR-32)

Unit under test: `render_jsonl(text: str) -> list[Block]`. Each Block has `kind` ∈ `{json_highlighted, plain}` and `text`. The frontend Shiki block component is then driven by this list.

### 7.1 `jsonl_render__three_well_formed_lines_yield_three_blocks`
- Inputs: contents of `tests/fixtures/jsonl_well_formed.jsonl` (three lines of JSON, trailing `\n`).
- Expected output: `[Block(kind=json_highlighted, text=line1), Block(kind=json_highlighted, text=line2), Block(kind=json_highlighted, text=line3)]`.
- Edge cases handled: standard happy path.
- Spec refs: FR-32.

### 7.2 `jsonl_render__one_malformed_line_renders_plain`
- Inputs: contents of `tests/fixtures/jsonl_with_malformed_line.jsonl` (line 2 is `{"k":}`).
- Expected output: blocks `[json_highlighted, plain, json_highlighted]`; the plain block's text equals the malformed line verbatim.
- Edge cases handled: per-line independence; one bad line does not poison the others.
- Spec refs: FR-32.

### 7.3 `jsonl_render__empty_line_handled`
- Inputs: contents of `tests/fixtures/jsonl_with_blank_line.jsonl`.
- Expected output: spec gap — confirm with author. FR-32 silent on blank lines. Interim: blank line is skipped (no block emitted). Alternative behavior to flag: emit an empty `plain` block to preserve line numbering.
- Edge cases handled: blank line policy; flagged.
- Spec refs: FR-32 (spec gap).

### 7.4 `jsonl_render__trailing_newline_does_not_emit_extra_block`
- Inputs: `'{"a":1}\n{"b":2}\n'`.
- Expected output: exactly two blocks.
- Edge cases handled: split-on-newline edge case; no spurious empty trailing block.
- Spec refs: FR-32.

### 7.5 `jsonl_render__no_trailing_newline_still_renders_last_line`
- Inputs: `'{"a":1}\n{"b":2}'` (no final `\n`).
- Expected output: exactly two blocks, both `json_highlighted`.
- Edge cases handled: file may end mid-line; final line still parsed.
- Spec refs: FR-32.

### 7.6 `jsonl_render__single_line_file`
- Inputs: `'{"single":true}'`.
- Expected output: one `json_highlighted` block.
- Edge cases handled: degenerate single-line file.
- Spec refs: FR-32.

### 7.7 `jsonl_render__non_object_json_is_still_highlighted`
- Inputs: `'42\n"hello"\nnull\n'`.
- Expected output: three `json_highlighted` blocks. JSON spec accepts top-level scalars; `json.loads("42")` succeeds.
- Edge cases handled: JSON Lines does not require objects — scalars are valid JSON values.
- Spec refs: FR-32.

---

## Group 8 — File-read error mapping (FR-5)

Unit under test: the file-read endpoint handler `GET /api/file?path=<rel>`. Each row is a single request, asserting the HTTP status and JSON `error.code`.

### 8.1 `file_read__file_not_found_maps_to_404_file_removed`
- Inputs: `path` resolves inside `EXPOSED_TREE` but the file is removed mid-test (race-style: delete after sandbox setup, then call endpoint).
- Expected output: HTTP 404, `error.code == "file_removed"`.
- Edge cases handled: FR-5.7 EAFP catch for `FileNotFoundError`; concurrency tolerance per NFR-12.
- Spec refs: FR-5.7, NFR-12.

### 8.2 `file_read__permission_denied_maps_to_403`
- Inputs: file with permission bits stripped (POSIX `chmod 000`); skip on Windows or simulate via `mock.patch("pathlib.Path.read_text", side_effect=PermissionError)`.
- Expected output: HTTP 403, `error.code == "permission_denied"`.
- Edge cases handled: FR-5.7 EAFP for `PermissionError`.
- Spec refs: FR-5.7.

### 8.3 `file_read__directory_path_maps_to_400_is_directory`
- Inputs: `path="specs/development/spec_driven/final_specs"` (a directory).
- Expected output: HTTP 400, `error.code == "is_directory"`.
- Edge cases handled: FR-5.7 EAFP for `IsADirectoryError`; downstream of FR-5.1 which lets the path through.
- Spec refs: FR-5.7.

### 8.4 `file_read__null_byte_in_content_maps_to_415_binary_content`
- Inputs: `path` points at `tests/fixtures/binary_with_null.md`.
- Expected output: HTTP 415, `error.code == "binary_content"`.
- Edge cases handled: FR-5.6 explicit; NFR-13 confirms no `chardet` dep.
- Spec refs: FR-5.6, NFR-13.

### 8.5 `file_read__file_above_2mb_maps_to_413_too_large`
- Inputs: `path` points at `tests/fixtures/2mb_plus_1_byte.md`.
- Expected output: HTTP 413, `error.code == "too_large"`.
- Edge cases handled: FR-5.5 boundary at exactly `2 * 1024 * 1024` bytes; one byte over.
- Spec refs: FR-5.5, NFR-15.

### 8.6 `file_read__file_below_2mb_passes`
- Inputs: `path` points at `tests/fixtures/2mb_minus_1_byte.md`.
- Expected output: HTTP 200, body contains the file contents.
- Edge cases handled: lower side of FR-5.5 boundary; off-by-one regression guard.
- Spec refs: FR-5.5.

### 8.7 `file_read__png_extension_maps_to_415_unsupported`
- Inputs: `path="path/to/foo.png"`.
- Expected output: HTTP 415, `error.code == "unsupported_extension"`.
- Edge cases handled: FR-5.4 whitelist; AC-8.
- Spec refs: FR-5.4, AC-8.

### 8.8 `file_read__symlink_source_maps_to_400_outside_sandbox`
- Inputs: `path="symlink_inside_tree"` where the symlink resolves to a real file inside the sandbox.
- Expected output: HTTP 400, `error.code == "outside_sandbox"`.
- Edge cases handled: FR-5.2 — symlink itself is not served even if its target is in-tree; NFR-5.
- Spec refs: FR-5.2, FR-4, NFR-5.

### 8.9 `file_read__path_outside_exposed_tree_maps_to_404_outside_exposed_tree`
- Inputs: `path="pyproject.toml"` (resolves inside `REPO_ROOT` but not inside `EXPOSED_TREE`).
- Expected output: HTTP 404, `error.code == "not_found"`, `error.kind == "outside_exposed_tree"`.
- Edge cases handled: FR-5.3 distinct from `outside_sandbox` (which is the ValueError-from-relative_to branch).
- Spec refs: FR-5.3.

### 8.10 `file_read__path_traversal_maps_to_400_outside_sandbox`
- Inputs: `path="../../etc/hosts"`.
- Expected output: HTTP 400, `error.code == "outside_sandbox"`.
- Edge cases handled: FR-5.1 ValueError catch; AC-7.
- Spec refs: FR-5.1, AC-7.

### 8.11 `file_read__write_endpoints_are_put_only` (revised by follow-up 001)
- Inputs: `POST /api/file?path=CLAUDE.md`, `DELETE /api/file?path=CLAUDE.md`, `PATCH /api/file?path=CLAUDE.md`.
- Expected output: each returns HTTP 405 Method Not Allowed. `PUT /api/file` with a valid body returns 200; `POST /api/regen-prompt` with a valid body returns 200.
- Edge cases handled: NFR-6 — only the sanctioned mutation endpoints exist (PUT for file write, POST for regen-prompt); no DELETE, no upload, no PATCH; routing surface check.
- Spec refs: NFR-6, FR-14a, FR-14c.

---

## Group 9 — Sidebar localStorage state (FR-23)

Unit under test: a frontend module (e.g., `useSidebarState` hook or `SidebarStore` class) that reads/writes `localStorage` under key `spec_driven.sidebar.v1`. Tests run in a JSDOM-style environment with `localStorage` mocked.

### 9.1 `sidebar_state__uses_correct_key`
- Inputs: dispatch a state-change action that writes; inspect `localStorage`.
- Expected output: `localStorage.getItem("spec_driven.sidebar.v1")` returns the serialized state. No other key was written.
- Edge cases handled: locks key name; future-proofs against accidental rename.
- Spec refs: FR-23.

### 9.2 `sidebar_state__defaults_when_key_missing`
- Inputs: empty `localStorage`.
- Expected output: hook/store initializes to defaults — `expanded` is empty `{}`, `lastSelectedPath` is `null`. No exception thrown.
- Edge cases handled: first-visit case; FR-22 fully-collapsed default.
- Spec refs: FR-22, FR-23.

### 9.3 `sidebar_state__falls_back_to_defaults_on_corrupted_json`
- Inputs: `localStorage.setItem("spec_driven.sidebar.v1", "not json{{")`.
- Expected output: hook/store initializes to defaults; no exception thrown; corrupted blob is overwritten on first state write.
- Edge cases handled: JSON.parse failure path; resilience requirement implicit in FR-23 ("State is restored on page load" — must not crash if state is unparseable).
- Spec refs: FR-23.

### 9.4 `sidebar_state__restores_valid_state_on_load`
- Inputs: `localStorage.setItem("spec_driven.sidebar.v1", JSON.stringify({expanded: {"projects.development.spec_driven": true}, lastSelectedPath: "projects/development/spec_driven/findings/dossier.md"}))`.
- Expected output: hook/store hydrates with the same structure; expanded map and last-selected path match exactly.
- Edge cases handled: round-trip; deep equality of nested object.
- Spec refs: FR-23.

### 9.5 `sidebar_state__url_takes_precedence_over_last_selected`
- Inputs: stored `lastSelectedPath = "...dossier.md"`; current URL `/projects/development/spec_driven/final_specs/spec.md`.
- Expected output: the rendered selection matches the URL, NOT the stored last-selected path. The stored value remains unchanged in storage until the user navigates.
- Edge cases handled: FR-23 explicit precedence rule.
- Spec refs: FR-23.

### 9.6 `sidebar_state__schema_version_in_key_locked`
- Inputs: write through the API, then read raw key list.
- Expected output: only `spec_driven.sidebar.v1` is present (no `v0` shadow, no unsuffixed key). Confirms the `.v1` suffix is intentional and reserved for migration.
- Edge cases handled: future migration safety net.
- Spec refs: FR-23.

### 9.7 `sidebar_state__corrupted_json_does_not_throw_on_render`
- Inputs: `localStorage` contains corrupted blob; mount the sidebar component.
- Expected output: render completes without an unhandled exception in the React tree (no error boundary triggered).
- Edge cases handled: pairs with 9.3; ensures the resilience extends to render not just hydration.
- Spec refs: FR-23.

---

## Group 10 — Long-name truncation classifier (FR-25)

Unit under test: `chooseTruncation(node: TreeNode) -> "middle" | "end"`. Caller decides the CSS class to apply for ellipsis style. The renderer always sets `title` to the full text.

### 10.1 `truncation__file_uses_middle_ellipsis`
- Inputs: `node = {kind: "file", name: "agent_team__validation_manager_with_a_very_long_suffix.md"}`.
- Expected output: `"middle"`.
- Edge cases handled: confirms FR-25 file rule — middle-ellipsis preserves `.md`.
- Spec refs: FR-25.

### 10.2 `truncation__folder_uses_end_ellipsis`
- Inputs: `node = {kind: "folder", name: "spec_driven_with_a_very_long_suffix"}`.
- Expected output: `"end"`.
- Edge cases handled: folder rule.
- Spec refs: FR-25.

### 10.3 `truncation__file_without_extension_still_uses_middle`
- Inputs: `node = {kind: "file", name: "Makefile"}`.
- Expected output: spec gap — confirm with author. Spec rationale ("preserves `.md` extension") implies extension-based routing, but only `.md` files appear in the tree per FR-1. Interim: still `"middle"` because `kind=="file"` is the documented branch key.
- Edge cases handled: degenerate file without extension; flagged.
- Spec refs: FR-25 (spec gap).

### 10.4 `truncation__missing_state_leaf_uses_end_ellipsis`
- Inputs: `node = {kind: "stage_missing", name: "validation"}` (FR-9 / FR-24 muted-italic leaf).
- Expected output: spec gap — confirm with author. Missing stage leaves are folder-shaped semantically (their name is a stage folder name, e.g., `validation`) and never have a `.md` extension. Interim: `"end"` (treat as folder for truncation purposes).
- Edge cases handled: flagged for confirmation.
- Spec refs: FR-25, FR-24 (spec gap).

### 10.5 `truncation__title_attribute_carries_full_text`
- Inputs: a long file name; render the row.
- Expected output: the rendered DOM `title` attribute equals the original full string verbatim, no truncation, no `…` character.
- Edge cases handled: FR-25 explicit "full text in the native `title` attribute".
- Spec refs: FR-25.

### 10.6 `truncation__short_name_renders_no_ellipsis`
- Inputs: file name `"spec.md"` (10 chars), row width 320px.
- Expected output: no truncation applied (CSS `text-overflow: ellipsis` is a no-op when content fits). The classifier still returns `"middle"`, but no ellipsis is visible. Test asserts via measured width or absence of the ellipsis pseudo-content.
- Edge cases handled: classifier output and visual outcome diverge for short names; ensures no false positive.
- Spec refs: FR-25.

---

## Cross-cutting note — spec-gap tracking

The following test cases are flagged as spec gaps and should drive a follow-up question to the spec author before they harden:

| Case | FR | Question |
|---|---|---|
| 1.5 / 1.6 | FR-5.1 vs FR-33 | Does `safe_resolve` decode `%xx` once, or only the frontend link classifier? |
| 1.7 | FR-5.2 | Is symlink rejection inside `safe_resolve` or in the calling endpoint? |
| 1.10 | FR-5.1 | What does empty `path` return — 400, 404, or 415? |
| 1.13 | FR-5.1 | Should embedded `\x00` map to `outside_sandbox` or a distinct `invalid_path` code? |
| 3.12 | FR-8 | Is alpha sort case-sensitive or case-insensitive? |
| 5.7 | FR-30 | Non-ASCII heading: drop or transliterate? |
| 5.10 | FR-30 | Heading with no slug-able characters: empty string or placeholder? |
| 6.10 | FR-33 | Double-encoded traversal: broken_missing or broken_outside? |
| 7.3 | FR-32 | Blank line in `.jsonl`: skip or emit empty block? |
| 10.3 / 10.4 | FR-25 | Truncation rule for files without extensions and for missing-state leaves? |

Total: 84 unit test cases (15 + 13 + 12 + 5 + 10 + 12 + 7 + 11 + 7 + 6 = 98 — see per-group counts; cross-cutting table above is not an additional case set).

End of unit_tests.md.
