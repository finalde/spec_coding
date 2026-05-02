# Unit Tests — spec_driven

Run: spec_driven-20260502-clean
Stage: 5 (Validation strategy — unit_tests level)
Source spec: `specs/development/spec_driven/final_specs/spec.md`
Inputs read: spec.md only (read-zero).
Descriptions only — no test framework code.

---

## Group 1 — `safe_resolve` (15 cases)

Exercises the single path-joining helper that every file-touching backend endpoint funnels through. The helper does `(REPO_ROOT / rel).resolve(strict=False).relative_to(REPO_ROOT.resolve())` and converts a `ValueError` into a structured 400 `outside_sandbox`. These cases lock in the exact threats called out in the spec: relative `..` traversal, absolute paths on both Windows and POSIX, single- and double-percent-encoding (the helper must NOT double-decode because FastAPI already decoded once), drive-letter mixed slashes, embedded NUL byte, symlinks (rejected even when target resolves inside the tree), `~` literal (treated as a literal segment, not a home expansion), empty strings, leading slash, and dotfiles. Coverage anchors on FR-5.1, FR-5.2, FR-6, NFR-4, NFR-5.

### 1.1
- Test name: `test_safe_resolve_clean_relative_path_returns_relative`
- Inputs: `rel = "specs/development/spec_driven/final_specs/spec.md"`, `REPO_ROOT = /tmp/repo`.
- Expected output: returns `Path("specs/development/spec_driven/final_specs/spec.md")`; no exception.
- Edge cases handled: standard happy path with mid-tree depth.
- Spec refs: FR-5.1, FR-6.

### 1.2
- Test name: `test_safe_resolve_dotdot_traversal_rejected`
- Inputs: `rel = "../../etc/hosts"`.
- Expected output: raises the helper's structured rejection mapped by the handler to HTTP 400 `outside_sandbox`.
- Edge cases handled: classic parent-traversal escape attempt.
- Spec refs: FR-5.1, AC-7, NFR-4.

### 1.3
- Test name: `test_safe_resolve_windows_absolute_path_rejected`
- Inputs: `rel = "C:\\Windows\\System32\\drivers\\etc\\hosts"`.
- Expected output: 400 `outside_sandbox`.
- Edge cases handled: drive-letter absolute path on Windows.
- Spec refs: FR-5.1, NFR-4.

### 1.4
- Test name: `test_safe_resolve_posix_absolute_path_rejected`
- Inputs: `rel = "/etc/passwd"`.
- Expected output: 400 `outside_sandbox`.
- Edge cases handled: POSIX absolute path that resolves outside `REPO_ROOT`.
- Spec refs: FR-5.1, AC-7.

### 1.5
- Test name: `test_safe_resolve_url_encoded_dotdot_after_layer_decode_rejected`
- Inputs: `rel = "%2e%2e/secret"` (already URL-decoded once by FastAPI to `"../secret"` before `safe_resolve` sees it).
- Expected output: 400 `outside_sandbox` (helper sees `../secret` and rejects).
- Edge cases handled: percent-encoded traversal, validated to fail after FastAPI's single decode.
- Spec refs: FR-5.1, FR-5 prelude.

### 1.6
- Test name: `test_safe_resolve_double_encoded_dotdot_does_not_bypass`
- Inputs: `rel = "%252e%252e/secret"` (FastAPI decodes once → `%2e%2e/secret`; `safe_resolve` MUST NOT decode again).
- Expected output: helper joins literally, `%2e%2e` becomes a regular segment name; the path lives under `REPO_ROOT` and is later filtered out by the `EXPOSED_TREE` membership check (404 `outside_exposed_tree`). Crucially: NOT silently decoded into `..` and NOT 400 `outside_sandbox` because the helper does not strip a second layer.
- Edge cases handled: double-encoding bypass attempt; explicit "MUST NOT double-decode" requirement.
- Spec refs: FR-5 prelude, FR-5.1, FR-5.3.

### 1.7
- Test name: `test_safe_resolve_drive_letter_with_mixed_slashes_rejected`
- Inputs: `rel = "C:/Windows\\System32/config"`.
- Expected output: 400 `outside_sandbox`.
- Edge cases handled: mixed forward / backward separators around a drive letter.
- Spec refs: FR-5.1.

### 1.8
- Test name: `test_safe_resolve_embedded_nul_byte_rejected`
- Inputs: `rel = "specs/development/spec_driven/final_specs/spec.md\x00.png"`.
- Expected output: rejected; backend handler returns 400 `outside_sandbox` (or the equivalent structured "invalid path" rejection raised before extension/membership checks).
- Edge cases handled: NUL-byte injection trying to fool extension whitelist.
- Spec refs: FR-5.1, FR-14a, NFR-13.

### 1.9
- Test name: `test_safe_resolve_symlink_rejected_even_inside_tree`
- Inputs: a symlink at `specs/development/proj/findings/dossier.md` whose target is `specs/development/proj/findings/real_dossier.md` inside `EXPOSED_TREE`.
- Expected output: 400 `outside_sandbox` (handler walks parent segments and the leaf via `is_symlink()`; symlink rejected regardless of where target points).
- Edge cases handled: symlink-points-inside case (still rejected per NFR-5).
- Spec refs: FR-4, FR-5.2, NFR-5.

### 1.10
- Test name: `test_safe_resolve_tilde_treated_as_literal_segment`
- Inputs: `rel = "~/secrets.md"`.
- Expected output: helper joins literally as `REPO_ROOT/~/secrets.md`; resolves inside `REPO_ROOT`; later 404 `outside_exposed_tree` from FR-5.3 OR 404 `file_removed` if the literal `~` directory truly does not exist.
- Edge cases handled: `~` is NOT expanded to home; treated as a literal directory name.
- Spec refs: FR-5.1, FR-5.3.

### 1.11
- Test name: `test_safe_resolve_empty_path_rejected`
- Inputs: `rel = ""`.
- Expected output: 400 `outside_sandbox` (or `is_directory` if the join returns `REPO_ROOT` itself; spec specifies the directory case as FR-5.7 → 400 `is_directory`).
- Edge cases handled: empty string.
- Spec refs: FR-5.1, FR-5.7.

### 1.12
- Test name: `test_safe_resolve_leading_slash_treated_as_root_relative_then_rejected`
- Inputs: `rel = "/specs/development/spec_driven/final_specs/spec.md"`.
- Expected output: 400 `outside_sandbox` (a leading slash makes `REPO_ROOT / rel` resolve to absolute `/specs/...`, escaping the sandbox; OR helper normalizes by stripping the slash — spec mandates the strict behavior, so 400 is the contract).
- Edge cases handled: accidental leading slash from a copy-paste.
- Spec refs: FR-5.1.

### 1.13
- Test name: `test_safe_resolve_dotfile_inside_exposed_tree_allowed`
- Inputs: `rel = ".claude/agents/agent_team__interview_manager.md"`.
- Expected output: returns `Path(".claude/agents/agent_team__interview_manager.md")`; passes membership check via FR-1's `.claude/agents/*.md` glob.
- Edge cases handled: hidden / dot-prefixed directory that IS in `EXPOSED_TREE`.
- Spec refs: FR-1, FR-5.

### 1.14
- Test name: `test_safe_resolve_dotfile_outside_exposed_tree_rejected_at_membership`
- Inputs: `rel = ".env"`.
- Expected output: helper returns the relative path successfully, but FR-5.3 then maps it to 404 `outside_exposed_tree` because `.env` is not under any of the four `EXPOSED_TREE` globs.
- Edge cases handled: dotfile NOT in `EXPOSED_TREE` (defense layered between resolver and membership filter).
- Spec refs: FR-1, FR-5.3.

### 1.15
- Test name: `test_safe_resolve_parent_dir_is_symlink_walked_and_rejected`
- Inputs: a regular file `specs/development/proj/findings/x.md` whose **parent ancestor** `specs/development/proj/` is a symlink.
- Expected output: 400 `outside_sandbox`. The handler walks parent segments, detects the ancestor symlink, and rejects.
- Edge cases handled: ancestor-symlink (not just leaf).
- Spec refs: FR-5.2, NFR-5.

---

## Group 2 — `EXPOSED_TREE` glob membership (32 cases — 8 per source)

Exercises the predicate that decides whether a resolved relative path falls inside one of the four sources defined in FR-1: (a) `CLAUDE.md` at repo root, (b) `.claude/agents/*.md`, (c) `.claude/skills/**/SKILL.md`, (d) per-project five-stage subfolders with the `.{md,yaml,yml,json,jsonl}` extension whitelist. The same predicate gates `GET /api/file`, `PUT /api/file`, the sidebar tree, and the link resolver — so each source needs both a positive case (canonical hit) and negative cases (extension wrong / location wrong / depth wrong / file vs folder).

### 2a — Source: `CLAUDE.md`

#### 2a.1
- Test name: `test_membership_claude_md_at_root_positive`
- Inputs: `rel = "CLAUDE.md"`.
- Expected output: `True`.
- Edge cases handled: canonical Settings-section root file.
- Spec refs: FR-1, FR-7.1.

#### 2a.2
- Test name: `test_membership_claude_md_in_subdir_negative`
- Inputs: `rel = "projects/spec_driven/CLAUDE.md"`.
- Expected output: `False`.
- Edge cases handled: name match in wrong location.
- Spec refs: FR-1.

#### 2a.3
- Test name: `test_membership_claude_md_lowercase_negative`
- Inputs: `rel = "claude.md"`.
- Expected output: `False`.
- Edge cases handled: case-mismatched filename on case-sensitive POSIX filesystems.
- Spec refs: FR-1.

#### 2a.4
- Test name: `test_membership_claude_yaml_negative`
- Inputs: `rel = "CLAUDE.yaml"`.
- Expected output: `False` (only the literal `CLAUDE.md` filename is in the source).
- Edge cases handled: extension swap.
- Spec refs: FR-1, FR-5.4.

### 2b — Source: `.claude/agents/*.md`

#### 2b.1
- Test name: `test_membership_agents_canonical_md_positive`
- Inputs: `rel = ".claude/agents/agent_team__research_manager.md"`.
- Expected output: `True`.
- Edge cases handled: canonical permanent agent file.
- Spec refs: FR-1, FR-7.1.

#### 2b.2
- Test name: `test_membership_agents_nested_subfolder_negative`
- Inputs: `rel = ".claude/agents/sub/foo.md"`.
- Expected output: `False` (glob is single-segment `*.md`, not `**/*.md`).
- Edge cases handled: depth>1 under `.claude/agents/`.
- Spec refs: FR-1.

#### 2b.3
- Test name: `test_membership_agents_yaml_negative`
- Inputs: `rel = ".claude/agents/foo.yaml"`.
- Expected output: `False` (extension is `.md` only for the agents glob).
- Edge cases handled: extension whitelist for this source is `.md` only.
- Spec refs: FR-1.

#### 2b.4
- Test name: `test_membership_agents_directory_path_negative`
- Inputs: `rel = ".claude/agents"`.
- Expected output: `False` (directory itself is not a leaf in `EXPOSED_TREE`).
- Edge cases handled: directory vs file.
- Spec refs: FR-1, FR-5.7.

### 2c — Source: `.claude/skills/**/SKILL.md`

#### 2c.1
- Test name: `test_membership_skills_canonical_positive`
- Inputs: `rel = ".claude/skills/agent_team/SKILL.md"`.
- Expected output: `True`.
- Edge cases handled: canonical SKILL.md, exactly one folder deep.
- Spec refs: FR-1, FR-7.1.

#### 2c.2
- Test name: `test_membership_skills_deep_subfolder_positive`
- Inputs: `rel = ".claude/skills/cat/sub/SKILL.md"`.
- Expected output: `True` (glob is `**/SKILL.md`).
- Edge cases handled: nested skill folder.
- Spec refs: FR-1.

#### 2c.3
- Test name: `test_membership_skills_skill_md_lowercase_negative`
- Inputs: `rel = ".claude/skills/foo/skill.md"`.
- Expected output: `False` (filename must be exactly `SKILL.md` upper-case).
- Edge cases handled: case-sensitive filename rule.
- Spec refs: FR-1.

#### 2c.4
- Test name: `test_membership_skills_other_md_in_skill_folder_negative`
- Inputs: `rel = ".claude/skills/foo/README.md"`.
- Expected output: `False`.
- Edge cases handled: only `SKILL.md` is exposed inside skill folders.
- Spec refs: FR-1.

### 2d — Source: `specs/{type}/{name}/{stages}/**/*.{md,yaml,yml,json,jsonl}`

#### 2d.1
- Test name: `test_membership_specs_final_specs_md_positive`
- Inputs: `rel = "specs/development/spec_driven/final_specs/spec.md"`.
- Expected output: `True`.
- Edge cases handled: canonical spec file.
- Spec refs: FR-1.

#### 2d.2
- Test name: `test_membership_specs_validation_jsonl_positive`
- Inputs: `rel = "specs/development/spec_driven/validation/events.jsonl"`.
- Expected output: `True`.
- Edge cases handled: `.jsonl` allowed under stage subfolders.
- Spec refs: FR-1, FR-32.

#### 2d.3
- Test name: `test_membership_specs_user_input_followups_nested_positive`
- Inputs: `rel = "specs/development/spec_driven/user_input/follow_ups/001-foo.md"`.
- Expected output: `True` (recursive `**/*.md` under each stage).
- Edge cases handled: nested follow-ups directory.
- Spec refs: FR-1, FR-7.

#### 2d.4
- Test name: `test_membership_specs_outside_five_stages_negative`
- Inputs: `rel = "specs/development/spec_driven/notes/scratch.md"` (`notes/` is NOT one of the five stage folders).
- Expected output: `False`.
- Edge cases handled: per FR-10, only the five canonical stage subfolders are exposed.
- Spec refs: FR-1, FR-10.

#### 2d.5
- Test name: `test_membership_specs_unsupported_extension_negative`
- Inputs: `rel = "specs/development/spec_driven/findings/diagram.png"`.
- Expected output: `False`.
- Edge cases handled: extension outside the `{md,yaml,yml,json,jsonl}` whitelist.
- Spec refs: FR-1, FR-5.4.

#### 2d.6
- Test name: `test_membership_specs_root_no_project_negative`
- Inputs: `rel = "specs/README.md"`.
- Expected output: `False` (no `task_type/task_name/stage` chain).
- Edge cases handled: shallow path under `specs/`.
- Spec refs: FR-1, FR-7.2.

#### 2d.7
- Test name: `test_membership_specs_taskname_only_no_stage_negative`
- Inputs: `rel = "specs/development/spec_driven/foo.md"`.
- Expected output: `False` (missing stage segment).
- Edge cases handled: `task_name`-level file without stage.
- Spec refs: FR-1, FR-10.

#### 2d.8
- Test name: `test_membership_specs_audit_path_negative`
- Inputs: `rel = ".audit/adhoc_agents/2026-05-02/spec_driven-foo/events.jsonl"`.
- Expected output: `False` (audit log explicitly out of scope per spec "Out of scope" list).
- Edge cases handled: audit-log path absolutely not in `EXPOSED_TREE`.
- Spec refs: FR-1, "Out of scope (v1)".

---

## Group 3 — Tree ordering (8 cases)

Exercises the deterministic ordering rules from FR-7 (top-level sections, three settings subgroups, projects sorted by `task_type` then `task_name`, the fixed five-stage enum) and FR-8 (alphabetical case-insensitive within stage with stable tie-break, plus the `validation/` priority head: `strategy.md`, `acceptance_criteria.md`, `bdd_scenarios.md`, then alphabetical). These are pure data-shape tests fed handcrafted lists of filenames; no filesystem touched.

### 3.1
- Test name: `test_tree_top_level_sections_order`
- Inputs: tree response built from a fixture with both settings + projects populated.
- Expected output: `keys[0] == "settings"`, `keys[1] == "projects"`; exactly two top-level keys.
- Edge cases handled: top-level section order is fixed regardless of insertion.
- Spec refs: FR-7.

### 3.2
- Test name: `test_tree_settings_three_subgroups_order`
- Inputs: settings node from the fixture.
- Expected output: subgroup keys in order `["claude_md", "agents", "skills"]`.
- Edge cases handled: settings subgroup order is fixed.
- Spec refs: FR-7.1.

### 3.3
- Test name: `test_tree_stages_fixed_order_enum`
- Inputs: a project with all five stage folders present, supplied in shuffled order.
- Expected output: stage list in order `["user_input", "interview", "findings", "final_specs", "validation"]`.
- Edge cases handled: stage order is the fixed enum, never alphabetical.
- Spec refs: FR-7.2.

### 3.4
- Test name: `test_tree_validation_priority_first_three`
- Inputs: validation/ contains `["acceptance_criteria.md", "bdd_scenarios.md", "strategy.md", "system_tests.md", "unit_tests.md", "security.md"]` in random order.
- Expected output: ordered as `["strategy.md", "acceptance_criteria.md", "bdd_scenarios.md", "security.md", "system_tests.md", "unit_tests.md"]` (priority three first; remainder alphabetical).
- Edge cases handled: validation-folder priority head with alphabetical tail.
- Spec refs: FR-8.

### 3.5
- Test name: `test_tree_alpha_within_stage_case_insensitive`
- Inputs: findings/ contains `["Zebra.md", "alpha.md", "beta.md", "Alpha-2.md"]`.
- Expected output: ordered as `["alpha.md", "Alpha-2.md", "beta.md", "Zebra.md"]` (case-insensitive primary).
- Edge cases handled: case-insensitive ASCII compare.
- Spec refs: FR-8.

### 3.6
- Test name: `test_tree_alpha_stable_tiebreak_by_raw_name`
- Inputs: findings/ contains `["Foo.md", "foo.md"]` (both lowercase to identical key).
- Expected output: ordered as `["Foo.md", "foo.md"]` because raw-byte stable tie-break preserves "F" < "f" ordinal.
- Edge cases handled: collision in case-insensitive key resolved by stable raw-name compare.
- Spec refs: FR-8.

### 3.7
- Test name: `test_tree_projects_alpha_by_task_type_then_task_name`
- Inputs: `specs/` contains `[("development","zen"), ("ai_video","alpha"), ("development","spec_driven")]`.
- Expected output: `[("ai_video","alpha"), ("development","spec_driven"), ("development","zen")]`.
- Edge cases handled: dual-key alphabetical sort.
- Spec refs: FR-7.2.

### 3.8
- Test name: `test_tree_validation_priority_when_one_priority_file_missing`
- Inputs: validation/ contains `["bdd_scenarios.md", "strategy.md", "system_tests.md"]` (no `acceptance_criteria.md`).
- Expected output: `["strategy.md", "bdd_scenarios.md", "system_tests.md"]` (priority order honored over only the present priority files; tail alphabetical).
- Edge cases handled: priority head is robust to missing intermediate files.
- Spec refs: FR-8.

---

## Group 4 — Stage presence flag (3 states)

Exercises FR-9: every project tree entry MUST include all five canonical stage entries; missing folders surface as `present: false` with empty file list; the sidebar then renders these as muted-italic per FR-24. Three tri-state cases.

### 4.1
- Test name: `test_stage_present_with_files`
- Inputs: project where `validation/` exists and contains `strategy.md`.
- Expected output: stage entry `{name: "validation", present: true, files: ["strategy.md"]}`.
- Edge cases handled: standard "present" state.
- Spec refs: FR-9.

### 4.2
- Test name: `test_stage_missing_folder`
- Inputs: project where `validation/` directory does not exist on disk.
- Expected output: stage entry `{name: "validation", present: false, files: []}`. Tree response still includes the entry.
- Edge cases handled: stage entry survives missing directory; consumers can render muted leaf.
- Spec refs: FR-9, FR-24.

### 4.3
- Test name: `test_stage_present_but_empty_directory`
- Inputs: project where `validation/` directory exists but is empty.
- Expected output: stage entry `{name: "validation", present: true, files: []}`. Distinct from 4.2 (`present: true` vs `false`).
- Edge cases handled: present-but-empty distinguished from absent — the sidebar can render this as expandable yet childless.
- Spec refs: FR-9.

---

## Group 5 — GFM kebab-case slug generator (12 cases)

Exercises the slug generator from FR-30: lowercase ASCII, drop non-ASCII characters and punctuation except hyphens, replace whitespace with hyphens, collapse multiple hyphens, trim leading/trailing hyphens, append `-1`, `-2`, … on collisions within the file. If the slug is empty, use `section` as the base before applying collision suffixes. Used by anchor-link resolution (FR-33 case 2 and FR-35).

### 5.1
- Test name: `test_slug_simple_heading`
- Inputs: heading text `"Functional requirements"`.
- Expected output: `"functional-requirements"`.
- Edge cases handled: standard two-word heading.
- Spec refs: FR-30.

### 5.2
- Test name: `test_slug_collision_appends_dash_one_then_dash_two`
- Inputs: three headings in the same file, all `"Notes"`.
- Expected output: `["notes", "notes-1", "notes-2"]`.
- Edge cases handled: collision suffixing.
- Spec refs: FR-30.

### 5.3
- Test name: `test_slug_non_ascii_dropped`
- Inputs: heading `"Café señor"`.
- Expected output: `"caf-seor"`.
- Edge cases handled: non-ASCII characters are dropped entirely (per spec "drop non-ASCII characters").
- Spec refs: FR-30.

### 5.4
- Test name: `test_slug_punctuation_only_falls_back_to_section`
- Inputs: heading `"!!!"`.
- Expected output: `"section"`.
- Edge cases handled: empty-after-strip → fallback base.
- Spec refs: FR-30.

### 5.5
- Test name: `test_slug_punctuation_only_collisions_use_section_base`
- Inputs: three headings, all `"!!!"`.
- Expected output: `["section", "section-1", "section-2"]`.
- Edge cases handled: fallback base participates in collision counter.
- Spec refs: FR-30.

### 5.6
- Test name: `test_slug_leading_digits_preserved`
- Inputs: heading `"123 ways"`.
- Expected output: `"123-ways"` (digits are ASCII and not punctuation).
- Edge cases handled: numeric-prefix headings don't get an alpha-prefix added.
- Spec refs: FR-30.

### 5.7
- Test name: `test_slug_mixed_case_lowercased`
- Inputs: heading `"Functional Requirements"`.
- Expected output: `"functional-requirements"`.
- Edge cases handled: case-folding via ASCII lowercase.
- Spec refs: FR-30.

### 5.8
- Test name: `test_slug_multiple_spaces_collapsed`
- Inputs: heading `"hello   world"` (three spaces).
- Expected output: `"hello-world"` (collapse multiple hyphens after whitespace conversion).
- Edge cases handled: hyphen collapse after whitespace replacement.
- Spec refs: FR-30.

### 5.9
- Test name: `test_slug_leading_trailing_spaces_trimmed`
- Inputs: heading `"  hello  "`.
- Expected output: `"hello"`.
- Edge cases handled: leading/trailing whitespace → leading/trailing hyphens → trimmed.
- Spec refs: FR-30.

### 5.10
- Test name: `test_slug_all_punctuation_with_hyphens_preserved_then_trimmed`
- Inputs: heading `"---"`.
- Expected output: `"section"` (hyphens-only collapses then trims to empty → fallback).
- Edge cases handled: pure-hyphen heading.
- Spec refs: FR-30.

### 5.11
- Test name: `test_slug_punctuation_in_middle_replaced_with_nothing_then_collapsed`
- Inputs: heading `"foo:bar / baz!"`.
- Expected output: `"foobar-baz"` (`:`, `/`, `!` dropped; whitespace → hyphen).
- Edge cases handled: mixed punctuation with whitespace.
- Spec refs: FR-30.

### 5.12
- Test name: `test_slug_unicode_emoji_dropped`
- Inputs: heading `"hello 👋 world"`.
- Expected output: `"hello--world"` collapsed to `"hello-world"` after multi-hyphen collapse.
- Edge cases handled: multi-byte emoji dropped, surrounding whitespace becomes hyphens, hyphen collapse normalizes.
- Spec refs: FR-30.

---

## Group 6 — Markdown link classifier (FR-33) (16 cases)

Exercises the four-branch classifier in FR-33 in its required order: external scheme / protocol-relative / fragment-only / relative-path-resolved-against-EXPOSED_TREE-with-existence-check. Each branch is exercised positively and at least once near the boundary. The relative-path branch is the most complex — needs decode-once-then-normalize, parent-traversal escape detection, file-exists detection, and the Windows case-mismatch tooltip. Source-file parent directory in all relative cases is `specs/development/spec_driven/final_specs/`.

### 6.1
- Test name: `test_link_https_scheme_external`
- Inputs: `href = "https://example.com/foo"`.
- Expected output: classification `external`; rendered with `target="_blank" rel="noopener noreferrer"` + sr-only.
- Edge cases handled: standard https link.
- Spec refs: FR-33.1, AC-6.

### 6.2
- Test name: `test_link_mailto_scheme_external`
- Inputs: `href = "mailto:foo@example.com"`.
- Expected output: classification `external`.
- Edge cases handled: non-http scheme matched by `^[a-z][a-z0-9+.-]*:`.
- Spec refs: FR-33.1.

### 6.3
- Test name: `test_link_ftp_scheme_external`
- Inputs: `href = "ftp://files.example.com/x"`.
- Expected output: classification `external`.
- Edge cases handled: another non-http scheme.
- Spec refs: FR-33.1.

### 6.4
- Test name: `test_link_protocol_relative_external`
- Inputs: `href = "//cdn.example.com/lib.js"`.
- Expected output: classification `external`.
- Edge cases handled: `//`-prefixed protocol-relative URL.
- Spec refs: FR-33.1.

### 6.5
- Test name: `test_link_anchor_only_same_file`
- Inputs: `href = "#functional-requirements"`.
- Expected output: classification `same_file_anchor`; in-app `scrollIntoView` for the matching id; click is a no-op if no match (silent).
- Edge cases handled: `#`-prefix triggers branch 2.
- Spec refs: FR-33.2.

### 6.6
- Test name: `test_link_relative_internal_resolves_inside_tree_and_exists`
- Inputs: source parent `specs/development/spec_driven/final_specs/`, `href = "../findings/dossier.md"`, file exists.
- Expected output: classification `internal`; renders `<Link>` with push-history target `/file/specs/development/spec_driven/findings/dossier.md`.
- Edge cases handled: typical sibling-stage cross-link (this is AC-4).
- Spec refs: FR-33.3, AC-4.

### 6.7
- Test name: `test_link_relative_dotdot_escapes_tree`
- Inputs: `href = "../../../etc/hosts"`.
- Expected output: classification `broken_outside`; rendered via FR-34 with cause `"outside exposed tree"`.
- Edge cases handled: parent-traversal escape from inside `EXPOSED_TREE`.
- Spec refs: FR-33.3, FR-34.

### 6.8
- Test name: `test_link_relative_inside_tree_but_missing`
- Inputs: `href = "../validation/missing.md"`, the file does not exist.
- Expected output: classification `broken_missing`; rendered via FR-34 with cause `"file not found"`.
- Edge cases handled: target inside `EXPOSED_TREE` glob but file does not exist.
- Spec refs: FR-33.3, FR-34, AC-5.

### 6.9
- Test name: `test_link_relative_dot_slash_resolves`
- Inputs: source parent `specs/development/spec_driven/final_specs/`, `href = "./spec.md"`, exists.
- Expected output: classification `internal` to `/file/specs/development/spec_driven/final_specs/spec.md`.
- Edge cases handled: explicit `./` prefix.
- Spec refs: FR-33.3.

### 6.10
- Test name: `test_link_percent_encoded_path_decoded_once`
- Inputs: `href = "../findings/dossier%20notes.md"`, target file is named `dossier notes.md` and exists.
- Expected output: classification `internal`; URL decoded once to `dossier notes.md`, file resolves and renders.
- Edge cases handled: standard percent-encoding of a space.
- Spec refs: FR-33.3.

### 6.11
- Test name: `test_link_double_encoded_path_does_not_decode_twice`
- Inputs: `href = "../findings/dossier%2520notes.md"` (URL `%25` = `%`).
- Expected output: classification `broken_missing` (decoded once → `dossier%20notes.md`; no such file exists).
- Edge cases handled: explicit "decode once" rule, mirroring backend FR-5.
- Spec refs: FR-33.3.

### 6.12
- Test name: `test_link_windows_case_mismatch_tooltip`
- Inputs: source parent `specs/development/spec_driven/final_specs/`, `href = "../FINDINGS/dossier.md"`, true filename is `findings/dossier.md`, running on Linux.
- Expected output: classification `broken_missing` with Windows-aware tooltip `"case mismatch — fix the link"`.
- Edge cases handled: case-sensitive POSIX behavior with case-mismatch hint.
- Spec refs: FR-33.3 (case-sensitive note).

### 6.13
- Test name: `test_link_internal_image_placeholder_branch`
- Inputs: image link `![diagram](../findings/diagram.svg)` — extension not in supported text set.
- Expected output: rendered as `<span class="image-placeholder">diagram</span>` with `title="v1: images not rendered"`.
- Edge cases handled: image link is a special render mode separate from the four FR-33 branches but FR-36 is part of the same render pipeline.
- Spec refs: FR-36.

### 6.14
- Test name: `test_link_path_with_anchor_classified_internal_and_anchor_handled_after`
- Inputs: `href = "../findings/dossier.md#angle-1"` (file exists, anchor unknown to this test).
- Expected output: classification `internal` for the file resolution; FR-35 governs post-navigation scroll attempt; click navigates regardless of anchor existence.
- Edge cases handled: `path#anchor` cross-file link is clickable per FR-35.
- Spec refs: FR-33.3, FR-35.

### 6.15
- Test name: `test_link_uppercase_scheme_still_external`
- Inputs: `href = "HTTPS://example.com"`.
- Expected output: classification `external` (regex is case-insensitive).
- Edge cases handled: case insensitivity of the scheme regex.
- Spec refs: FR-33.1.

### 6.16
- Test name: `test_link_anchor_with_no_matching_heading_silent_fallthrough`
- Inputs: `href = "#nonexistent-section"`, no heading slugs match.
- Expected output: classification `same_file_anchor`; click resolves to no-op (no scroll, no error UI).
- Edge cases handled: silent fallthrough on missing anchor.
- Spec refs: FR-33.2, FR-35.

---

## Group 7 — JSONL per-line renderer (8 cases)

Exercises FR-32's `.jsonl` renderer: each line is independently parsed and Shiki-highlighted as JSON; malformed lines render as plain text; blank lines are skipped. Tests are pure (renderer-input → list of rendered blocks) — no Shiki real-renderer invocation needed; output is the structural decision per line: `{kind: "json"|"plain"|"skipped", text}`.

### 7.1
- Test name: `test_jsonl_well_formed_lines_each_render_as_json_block`
- Inputs: file contents `'{"a":1}\n{"b":2}\n{"c":3}\n'`.
- Expected output: three blocks, each `{kind: "json", text: "..."}`.
- Edge cases handled: standard happy path, trailing newline.
- Spec refs: FR-32.

### 7.2
- Test name: `test_jsonl_malformed_line_renders_as_plain`
- Inputs: file contents `'{"a":1}\nNOT JSON\n{"c":3}\n'`.
- Expected output: blocks `[{kind:"json", ...}, {kind:"plain", text:"NOT JSON"}, {kind:"json", ...}]`.
- Edge cases handled: malformed line falls back to plain text per FR-32.
- Spec refs: FR-32.

### 7.3
- Test name: `test_jsonl_empty_file_renders_zero_blocks`
- Inputs: file contents `""`.
- Expected output: empty list of blocks; no error; pane shows the standard "empty" state.
- Edge cases handled: zero-byte JSONL.
- Spec refs: FR-32.

### 7.4
- Test name: `test_jsonl_blank_line_in_middle_skipped`
- Inputs: file contents `'{"a":1}\n\n{"c":3}\n'`.
- Expected output: two `json` blocks; blank line produces no block (skipped per FR-32 "Blank lines in `.jsonl` are skipped").
- Edge cases handled: blank-line policy.
- Spec refs: FR-32.

### 7.5
- Test name: `test_jsonl_no_trailing_newline_last_line_still_rendered`
- Inputs: file contents `'{"a":1}\n{"b":2}'` (no final `\n`).
- Expected output: two `json` blocks.
- Edge cases handled: missing trailing newline.
- Spec refs: FR-32.

### 7.6
- Test name: `test_jsonl_single_line`
- Inputs: file contents `'{"a":1}\n'`.
- Expected output: one `json` block.
- Edge cases handled: degenerate single-line file.
- Spec refs: FR-32.

### 7.7
- Test name: `test_jsonl_very_long_line_still_one_block`
- Inputs: file contents = a single 100KB JSON line + `\n`.
- Expected output: one `json` block; renderer does not truncate at the line level (FR-5 size cap is the only ceiling).
- Edge cases handled: long-line tolerance below the 2 MB cap.
- Spec refs: FR-32, FR-5.5.

### 7.8
- Test name: `test_jsonl_whitespace_only_line_skipped`
- Inputs: file contents `'{"a":1}\n   \n{"c":3}\n'` (middle line is spaces).
- Expected output: two `json` blocks; whitespace-only line treated as blank-skipped.
- Edge cases handled: extends "blank line" semantics to whitespace-only.
- Spec refs: FR-32.

---

## Group 8 — File-read error mapping (FR-5) (8 cases)

Exercises the full HTTP status code table in FR-5 for `GET /api/file`. Each test feeds a controlled filesystem fixture and asserts both the status code and the structured `kind` discriminator. Coverage is one case per status branch.

### 8.1
- Test name: `test_file_read_outside_sandbox_returns_400`
- Inputs: `path = "../../etc/hosts"`.
- Expected output: HTTP 400, body `{"kind": "outside_sandbox"}`.
- Edge cases handled: `safe_resolve` raised `ValueError`.
- Spec refs: FR-5.1, AC-7.

### 8.2
- Test name: `test_file_read_is_directory_returns_400`
- Inputs: `path = "specs/development/spec_driven/findings/"` (resolves to a directory).
- Expected output: HTTP 400, body `{"kind": "is_directory"}`.
- Edge cases handled: `IsADirectoryError` mapped per FR-5.7.
- Spec refs: FR-5.7.

### 8.3
- Test name: `test_file_read_permission_denied_returns_403`
- Inputs: `path` resolves to a file inside `EXPOSED_TREE` whose mode is `000`.
- Expected output: HTTP 403, body `{"kind": "permission_denied"}`.
- Edge cases handled: `PermissionError` mapped per FR-5.7.
- Spec refs: FR-5.7.

### 8.4
- Test name: `test_file_read_file_removed_returns_404`
- Inputs: `path` resolves to a path that the tree-walker saw a moment ago, but it has since been deleted.
- Expected output: HTTP 404, body `{"kind": "file_removed"}`.
- Edge cases handled: `FileNotFoundError` mapped per FR-5.7; concurrent-write tolerance NFR-12.
- Spec refs: FR-5.7, NFR-12, AC-15.

### 8.5
- Test name: `test_file_read_outside_exposed_tree_returns_404`
- Inputs: `path = "pyproject.toml"` (resolves under `REPO_ROOT` but not under any of the four `EXPOSED_TREE` globs).
- Expected output: HTTP 404, body `{"kind": "outside_exposed_tree"}`.
- Edge cases handled: distinct kind from `file_removed`; both share status 404 but discriminate by `kind`.
- Spec refs: FR-5.3.

### 8.6
- Test name: `test_file_read_too_large_returns_413`
- Inputs: a `.md` file 2 097 153 bytes (1 byte over 2 MB).
- Expected output: HTTP 413, body `{"kind": "too_large"}`.
- Edge cases handled: 2 MB cap.
- Spec refs: FR-5.5, AC-10, NFR-15.

### 8.7
- Test name: `test_file_read_unsupported_extension_returns_415`
- Inputs: `path = "specs/development/spec_driven/findings/diagram.png"`.
- Expected output: HTTP 415, body `{"kind": "unsupported_extension"}`.
- Edge cases handled: extension whitelist.
- Spec refs: FR-5.4, AC-8.

### 8.8
- Test name: `test_file_read_binary_content_returns_415`
- Inputs: a `.md` file containing a `\x00` byte after UTF-8 decoding with `errors="replace"`.
- Expected output: HTTP 415, body `{"kind": "binary_content"}`.
- Edge cases handled: NUL-byte is the binary discriminator (no `chardet`).
- Spec refs: FR-5.6, NFR-13, AC-9.

---

## Group 9 — Sidebar localStorage state (6 cases)

Exercises FR-23 (sidebar collapse state + last-selected file persisted under key `spec_driven.sidebar.v1`, restored on page load, URL takes precedence over saved last-selected, corrupted JSON falls back with no console error). Tests target the pure state-load / state-save module — no DOM.

### 9.1
- Test name: `test_sidebar_load_default_when_no_localstorage_key`
- Inputs: empty `localStorage`.
- Expected output: state object equal to `{expandedPaths: {}, lastSelectedPath: null}`.
- Edge cases handled: first-visit defaults.
- Spec refs: FR-23.

### 9.2
- Test name: `test_sidebar_load_valid_json_restores_state`
- Inputs: `localStorage[key] = '{"expandedPaths": {"specs/development": true}, "lastSelectedPath": "specs/development/spec_driven/final_specs/spec.md"}'`.
- Expected output: state object matches the parsed value exactly.
- Edge cases handled: round-trip from saved state.
- Spec refs: FR-23.

### 9.3
- Test name: `test_sidebar_corrupted_json_falls_back_silently`
- Inputs: `localStorage[key] = 'not-json-at-all'`; spy on `console.error`.
- Expected output: state object equals defaults; `console.error` is NOT called (silent fallback per FR-23).
- Edge cases handled: malformed JSON, no console noise.
- Spec refs: FR-23.

### 9.4
- Test name: `test_sidebar_save_round_trip_preserves_shape`
- Inputs: save state `{expandedPaths: {"a/b": true, "a/c": false}, lastSelectedPath: "a/b/x.md"}`.
- Expected output: subsequent load returns the same object structurally.
- Edge cases handled: persistence write+read symmetry.
- Spec refs: FR-23.

### 9.5
- Test name: `test_sidebar_url_overrides_saved_last_selected`
- Inputs: saved `lastSelectedPath = "X.md"`; current URL `/file/Y.md`.
- Expected output: effective selected path is `Y.md`. The URL precedence rule (FR-23) wins.
- Edge cases handled: dual sources of truth, URL wins.
- Spec refs: FR-23, FR-15.

### 9.6
- Test name: `test_sidebar_expanded_paths_record_semantics_value_true_is_expanded_missing_key_is_collapsed`
- Inputs: state `{expandedPaths: {"a/b": true, "a/c": false}}`. Caller checks `isExpanded("a/b")`, `isExpanded("a/c")`, `isExpanded("a/d")`.
- Expected output: `[true, false, false]` — missing key treated as collapsed.
- Edge cases handled: collapse-by-default semantics; FR-23 + FR-22 ("fully collapsed on first visit").
- Spec refs: FR-22, FR-23.

---

## Group 10 — Long-name truncation classifier (5 cases)

Exercises FR-25: every tree row is single-line, ellipsis-on-overflow, with full text in `title`. Files use **middle-ellipsis** (preserves the extension via a two-element `direction: rtl` flex split). Folders use **end-ellipsis**. Tests target the pure classifier that, given (kind, name), returns the structural rendering decision: which split-mode to apply and what the two segments are.

### 10.1
- Test name: `test_truncation_folder_uses_end_ellipsis`
- Inputs: `(kind="folder", name="very_long_folder_name_that_overflows_the_320px_sidebar")`.
- Expected output: `{mode: "end_ellipsis", text: name}` — single span, CSS `text-overflow: ellipsis`.
- Edge cases handled: folders never split.
- Spec refs: FR-25.

### 10.2
- Test name: `test_truncation_file_with_extension_uses_middle_ellipsis_split`
- Inputs: `(kind="file", name="acceptance_criteria_for_some_extremely_long_topic.md")`.
- Expected output: `{mode: "middle_ellipsis", left: "acceptance_criteria_for_some_extremely_long_topic", right: ".md"}` — left rendered as overflow-ellipsis, right rendered RTL-pinned.
- Edge cases handled: extension preserved on the right.
- Spec refs: FR-25.

### 10.3
- Test name: `test_truncation_short_file_no_op`
- Inputs: `(kind="file", name="x.md")`.
- Expected output: same `middle_ellipsis` mode but no overflow occurs at runtime; classifier still emits split (renderer applies CSS regardless; no overflow → no visible ellipsis).
- Edge cases handled: short names don't bypass classifier; CSS handles the no-op.
- Spec refs: FR-25.

### 10.4
- Test name: `test_truncation_file_with_long_extension`
- Inputs: `(kind="file", name="huge_data_dump_with_explanation.jsonl")`.
- Expected output: `{mode: "middle_ellipsis", left: "huge_data_dump_with_explanation", right: ".jsonl"}` — `.jsonl` is among the supported extensions and is preserved.
- Edge cases handled: multi-char extension still pinned right.
- Spec refs: FR-25, FR-1.

### 10.5
- Test name: `test_truncation_file_with_no_extension_falls_back_to_end_ellipsis`
- Inputs: `(kind="file", name="LICENSE")` (theoretically — extensionless file in `EXPOSED_TREE` is rare, but classifier must still decide).
- Expected output: `{mode: "end_ellipsis", text: "LICENSE"}` (no `.ext` to pin → behave like a folder, end-ellipsis).
- Edge cases handled: extensionless file robustness.
- Spec refs: FR-25.

---

## Group 11 — Regen-prompt size policy + breakdown formatter (10 cases)

Exercises FR-14c size policy and the FR-42(d) breakdown line. The size policy is "warn-don't-truncate above 50 KB; 413 above 1 MB; emit prompt in full below". The breakdown formatter renders a single line beside the Copy button. The line includes count of stages, count of follow-ups, autonomous flag literal, and bytes formatted with locale-aware separator. Pluralization: "stage" vs "stages", "follow-up" vs "follow-ups". Two cases verify the verbatim imperative line under autonomous.

### 11.1
- Test name: `test_regen_under_50kb_returns_null_warning`
- Inputs: assembled prompt body 30 000 bytes.
- Expected output: `{warning: null, bytes: 30000}`; HTTP 200; prompt emitted verbatim.
- Edge cases handled: standard-sized prompt below threshold.
- Spec refs: FR-14c.

### 11.2
- Test name: `test_regen_at_50kb_threshold_returns_warning`
- Inputs: assembled prompt body 51 200 bytes (50 KB).
- Expected output: `warning` is a non-empty string mentioning size; `bytes: 51200`; HTTP 200; prompt emitted verbatim (warn-don't-truncate).
- Edge cases handled: at-threshold behavior; warn-don't-truncate.
- Spec refs: FR-14c.

### 11.3
- Test name: `test_regen_at_900kb_still_warns_no_413`
- Inputs: assembled prompt body 921 600 bytes (900 KB).
- Expected output: `warning` non-null; HTTP 200; full prompt returned.
- Edge cases handled: between 50 KB and 1 MB the warn-don't-truncate continues to apply.
- Spec refs: FR-14c.

### 11.4
- Test name: `test_regen_above_1mb_returns_413`
- Inputs: assembled prompt body 1 100 000 bytes (>1 MB).
- Expected output: HTTP 413, body `{"kind": "too_large"}`. No prompt body.
- Edge cases handled: hard ceiling.
- Spec refs: FR-14c, AC-19.

### 11.5
- Test name: `test_breakdown_line_singular_stage_singular_followup`
- Inputs: `{selected_stages_count: 1, follow_ups_count: 1, autonomous: false, bytes: 10240}`.
- Expected output: line `"1 stage selected, 1 follow-up inlined, autonomous=false, 10.0 KB"` (locale-formatted KB to one decimal, singular nouns).
- Edge cases handled: singular pluralization for both nouns.
- Spec refs: FR-42d.

### 11.6
- Test name: `test_breakdown_line_plural_stages_plural_followups`
- Inputs: `{selected_stages_count: 6, follow_ups_count: 3, autonomous: true, bytes: 102400}`.
- Expected output: line `"6 stages selected, 3 follow-ups inlined, autonomous=true, 100.0 KB"`.
- Edge cases handled: plural forms.
- Spec refs: FR-42d.

### 11.7
- Test name: `test_breakdown_line_zero_followups`
- Inputs: `{selected_stages_count: 2, follow_ups_count: 0, autonomous: false, bytes: 4096}`.
- Expected output: `"2 stages selected, 0 follow-ups inlined, autonomous=false, 4.0 KB"` (zero is plural per English convention).
- Edge cases handled: zero count uses plural noun.
- Spec refs: FR-42d.

### 11.8
- Test name: `test_breakdown_line_locale_formatted_bytes`
- Inputs: `{selected_stages_count: 1, follow_ups_count: 1, autonomous: false, bytes: 1500000}`.
- Expected output: `"1 stage selected, 1 follow-up inlined, autonomous=false, 1,464.8 KB"` (locale comma separator for thousands; en-US default).
- Edge cases handled: thousands separator on KB display.
- Spec refs: FR-42d.

### 11.9
- Test name: `test_regen_prompt_autonomous_includes_imperative_line_verbatim`
- Inputs: `{stages: ["spec_compilation"], modules: {...}, autonomous: true}`.
- Expected output: prompt's first line is `# EXECUTION MODE: AUTONOMOUS`; the next non-blank line equals verbatim `"Do not call AskUserQuestion. For anything unclear, use your best judgment, record the choice inline in the artifact, and keep going. Produce every requested artifact below in this single turn before stopping."`.
- Edge cases handled: verbatim imperative under autonomous mode.
- Spec refs: FR-14c-b, AC-20.

### 11.10
- Test name: `test_regen_prompt_interactive_does_not_include_imperative_line`
- Inputs: same body, `autonomous: false`.
- Expected output: prompt's first line is `# EXECUTION MODE: INTERACTIVE`; the imperative sentence does NOT appear anywhere in the prompt body.
- Edge cases handled: imperative is autonomous-only.
- Spec refs: FR-14c-a, FR-14c-b.

---

## Group 12 — Editor dirty-state + save (6 cases)

Exercises FR-40: dirty state computed via deep-equality of `currentText` vs `lastSavedText` (no "user typed" flag); Save success updates `lastSavedText` and clears dirty; Save failure leaves dirty lit and shows a persistent banner that does NOT auto-dismiss on subsequent keystrokes. Tests target the editor's pure reducer + side-effect mock for `PUT /api/file`.

### 12.1
- Test name: `test_editor_initial_state_is_clean`
- Inputs: open editor with file content `"hello"`; `currentText = "hello"`, `lastSavedText = "hello"`.
- Expected output: `isDirty == false`; Save button disabled; no dirty dot; no badge.
- Edge cases handled: load is clean.
- Spec refs: FR-40b, FR-40c.

### 12.2
- Test name: `test_editor_type_then_revert_returns_to_clean_via_deep_equality`
- Inputs: start clean with `"hello"`; type → `"hello!"` (dirty); delete `!` → `"hello"`.
- Expected output: `isDirty == false` after revert; Save button disabled. The deep-equality check (NOT a "user typed" flag) makes this work — sidesteps the GitHub web editor CRLF anti-pattern.
- Edge cases handled: textual round-trip should clear dirty even though `onChange` fired.
- Spec refs: FR-40c.

### 12.3
- Test name: `test_editor_save_success_updates_last_saved_and_clears_dirty`
- Inputs: state `currentText = "world"`, `lastSavedText = "hello"` (dirty); `PUT /api/file` mocked to 200 OK.
- Expected output: post-save state `currentText = "world"`, `lastSavedText = "world"`, `isDirty == false`, dirty dot cleared, "Saved." announced via aria-live, editor stays open.
- Edge cases handled: success path clears dirty and stays in editor.
- Spec refs: FR-40e final paragraph, AC-16.

### 12.4
- Test name: `test_editor_save_failure_leaves_dirty_lit_and_shows_persistent_banner`
- Inputs: dirty state; `PUT /api/file` mocked to 415 `unsupported_extension`.
- Expected output: `isDirty == true` (still); banner present above textarea reading the structured error key + kind; banner does NOT auto-dismiss; dirty dot still lit.
- Edge cases handled: failure path; banner persistence.
- Spec refs: FR-40e, AC-17.

### 12.5
- Test name: `test_editor_save_failure_banner_does_not_clear_on_next_keystroke`
- Inputs: state from 12.4 (banner showing); user types one more character.
- Expected output: banner STILL present; dirty dot still lit. Banner only clears when a save actually succeeds.
- Edge cases handled: banner is sticky across edit events.
- Spec refs: FR-40e.

### 12.6
- Test name: `test_editor_ctrl_s_triggers_save_and_prevents_default`
- Inputs: editor focused, dirty; user fires `keydown` event `Ctrl+S` (and on macOS, `Cmd+S`).
- Expected output: `PUT /api/file` invoked once with `{path, text}`; browser default Save dialog suppressed (`event.preventDefault()` called).
- Edge cases handled: keyboard shortcut wiring on both Ctrl and Cmd.
- Spec refs: FR-40d.

End of unit_tests.md.
