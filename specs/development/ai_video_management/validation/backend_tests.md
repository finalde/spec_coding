# Backend tests — validation strategy (level 03)

Run: `ai_video_management-20260505-002710`
Stage: 5 (validation strategy)
Specialist: `level-specialist-03-backend_tests`

Spec anchors covered: FR-1..FR-39, FR-82..FR-83, NFR-1, NFR-7.
Refs consulted: `.claude/agent_refs/validation/general.md`, `.claude/agent_refs/validation/development.md` (moves #2, #3, #4, #5, #6, #10), `.claude/agent_refs/project/development.md`, `.claude/agent_refs/project/general.md`.
Port source: `projects/spec_driven/backend/tests/` (existing pytest suite — port verbatim where the contract is unchanged).

---

## 总览

This level produces the pytest unit + system + boot-smoke suite under `projects/ai_video_management/backend/tests/`. Layout mirrors `spec_driven/backend/tests/`:

```
backend/tests/
├── __init__.py
├── conftest.py                 # fixtures: repo_root, resolver, bound (port=8766), app, client, good_headers, localhost_headers, scratch_dir
└── unit/
    ├── test_repo_root.py
    ├── test_safe_resolve.py
    ├── test_exposed_tree.py
    ├── test_tree_walker.py     # +consumer-walk + project_meta tests (move #2)
    ├── test_file_reader.py
    ├── test_file_writer.py
    ├── test_promotions.py
    ├── test_regen_prompt.py    # +ai_video scope variants
    ├── test_sub_type_lookup.py # NEW — regex against real wukong_juexing/qa.md (move #10)
    ├── test_stages.py
    ├── test_api_security.py    # pre-rewrite + post-rewrite shapes (move #11)
    ├── test_api.py             # endpoint surface
    └── test_boot_smoke.py      # NEW — uvicorn boot + GET / + GET /api/tree (move #4)
```

Key fixture overrides vs spec_driven (in `conftest.py`):
- `BoundOrigin(host="127.0.0.1", port=8766)` — bound to **8766**, not 8765 (FR-4).
- `good_headers = {"Origin": "http://127.0.0.1:8766", "Host": "127.0.0.1:8766"}`.
- `localhost_headers = {"Origin": "http://localhost:8766", "Host": "localhost:8766"}`.
- `scratch_dir` rooted at `specs/ai_video/wukong_juexing/__scratch__/` (real EXPOSED_TREE folder; the spec_driven location `specs/development/spec_driven/__scratch__/` is OUTSIDE this app's EXPOSED_TREE per FR-7/FR-8).

Severity defaults follow `agent_refs/validation/development.md` "Severity escalations specific to development". A failure that lands in the *Critical* table (boot exception, sandbox escape, API shape drift, latent deep-link blank page) halts immediately with no revision rounds; *Blocker* gets the standard 3-round cap; *Warning* logs only.

---

## 模块测试矩阵 (per-module test inventory)

### 1. `repo_root.py` — `test_repo_root.py` *(port verbatim)*

| Test | Inputs | Expected | Edge cases | Severity if fails |
|---|---|---|---|---|
| `test_find_locates_repo_root` | cwd anywhere under repo | returns `RepoRoot` whose `.path` contains `CLAUDE.md` + `.claude/` | called from deeply nested cwd, called from repo root | `critical` (every other test depends on this) |
| `test_find_raises_when_outside_repo` | cwd = `tmp_path` (no markers above) | raises `RepoRootNotFound` | symlinked tmp dir | `blocker` |
| `test_path_is_absolute_and_resolved` | default | `repo_root.path.is_absolute() and ".." not in str(repo_root.path)` | UNC path on Windows (skipif win32 only if it actually breaks) | `blocker` |

### 2. `safe_resolve.py` — `test_safe_resolve.py` *(port the 13 groups verbatim from spec_driven; only the test fixture path changes)*

Port 1.1 → 1.13 verbatim. Substitute `specs/development/spec_driven/__scratch__/...` → `specs/ai_video/wukong_juexing/__scratch__/...` and `specs/development/spec_driven/final_specs/spec.md` → `specs/ai_video/wukong_juexing/__scratch__/dummy.md` (or any real EXPOSED_TREE path; resolver is content-agnostic).

Reserved-name probe at any segment: substitute the in-tree path (`specs/ai_video/wukong_juexing/CON.md`).

| Group | Severity if fails |
|---|---|
| 1.1 happy paths | `blocker` |
| 1.2 `..` traversal | `critical` (sandbox escape) |
| 1.3 percent-encoded traversal | `critical` |
| 1.4 ADS / colons | `critical` |
| 1.5 Windows reserved names | `critical` (Windows host canonical) |
| 1.6 8.3 short names | `critical` |
| 1.7 Vite CVE-2025-62522 + NUL byte + colon | `critical` |
| 1.8 POSIX symlink | `blocker` (skipped on Windows — see § Cross-platform skip) |
| 1.9 Windows junction | `blocker` (skipped on POSIX) |
| 1.10 outside-tree single-None | `critical` (existence-oracle gap) |
| 1.11 mixed slashes | `critical` |
| 1.12 empty/control input | `blocker` |
| 1.13 absolute paths | `critical` |

### 3. `exposed_tree.py` — `test_exposed_tree.py` *(port shape, change roots per FR-7/FR-8)*

| Test | Target | Inputs | Expected | Severity |
|---|---|---|---|---|
| `test_is_inside_accepts_ai_videos` | `is_inside` | `ai_videos/wukong_juexing/script.md` | `True` | `critical` |
| `test_is_inside_accepts_specs_ai_video` | `is_inside` | `specs/ai_video/wukong_juexing/interview/qa.md` | `True` | `critical` |
| `test_is_inside_accepts_claude_md` | `is_inside` | `CLAUDE.md` | `True` | `critical` |
| `test_is_inside_accepts_dotclaude_skill` | `is_inside` | `.claude/skills/agent_team/SKILL.md` | `True` | `critical` |
| `test_is_inside_accepts_dotclaude_playbooks` | `is_inside` | `.claude/skills/agent_team/playbooks/research.md` | `True` | `critical` |
| `test_is_inside_accepts_dotclaude_agent_refs` | `is_inside` | `.claude/agent_refs/project/ai_video.md` | `True` | `critical` |
| `test_is_inside_rejects_projects` | `is_inside` | `projects/spec_driven/backend/main.py` | `False` (FR-8 explicitly drops `projects/` from this app's tree) | `critical` |
| `test_is_inside_rejects_specs_development` | `is_inside` | `specs/development/spec_driven/final_specs/spec.md` | `False` (FR-8 tightens to `specs/ai_video/**`) | `critical` |
| `test_is_inside_rejects_dotgit_audit_node_modules` | `is_inside` | `.git/HEAD`, `.audit/foo`, `node_modules/x` | `False` × 3 | `critical` |
| `test_is_inside_extension_allowlist_for_ai_videos` | `is_inside` | `.svg`, `.exe`, `.html` under `ai_videos/` | `False` (FR-13 — SVG NOT allowed) | `critical` |
| `test_is_inside_accepts_image_extensions_under_ai_videos` | `is_inside` | `.png`, `.jpg` under `ai_videos/wukong_juexing/characters/ref_images/` | `True` (FR-7 includes images) | `blocker` |
| `test_is_inside_rejects_images_under_specs` | `is_inside` | `.png` under `specs/ai_video/wukong_juexing/` | `False` (FR-7 — image extensions only on `ai_videos/**`) | `blocker` |
| `test_is_inside_rejects_root_md_other_than_claude` | `is_inside` | `README.md` (repo root) | `False` | `blocker` |

### 4. `tree_walker.py` — `test_tree_walker.py` *(port + add `project_meta` + image type)*

Port the 8 existing groups (uniform `children`, no legacy keys, no backslash, excludes `.audit/.git/node_modules`, sort order). Add the following:

| Test | Inputs | Expected | Severity |
|---|---|---|---|
| `test_root_has_three_top_level_sections` | `GET /api/tree` | top-level children include exactly `AI Videos`, `Specs (ai_video)`, `Context` in **fixed order** (FR-18, FR-43) | `critical` (frontend Sidebar walks ordinal index) |
| `test_tree_consumer_walk` | recursive descent via `node.children` only | every non-leaf has `children: list`; every leaf has `name` + `path`; at least one leaf under each top-level section | `critical` (move #2) |
| `test_tree_consumer_walk_uses_children_not_legacy_keys` | walk | NO node carries any of `projects`, `stages`, `task_type`, `files`, `items`, `videos`, `episodes` as a recursive descent field — always `children` | `critical` (move #2 + spec_driven-20260502-clean regression) |
| `test_image_leaves_have_type_image` | walk | every leaf with extension `.png`/`.jpg` has `type == "image"` (FR-19) | `blocker` |
| `test_text_leaves_have_type_file` | walk | every leaf with extension `.md`/`.json`/`.jsonl`/`.yaml`/`.yml`/`.txt` has `type == "file"` | `blocker` |
| `test_dir_nodes_have_type_dir` | walk | every non-leaf has `type == "dir"` or `type == "section"` (top-level only) | `blocker` |
| `test_ai_videos_project_dirs_have_project_meta` | locate every direct child of the `AI Videos` section (e.g. `ai_videos/wukong_juexing/`) | each carries `project_meta` field; for `wukong_juexing` `project_meta.sub_type == "short"` (matches real `qa.md`); `shot_count` is `int | None`; `episode_count` is `None` for shorts | `critical` (FR-19, FR-44 — sidebar badge depends on this) |
| `test_non_ai_video_project_dirs_have_no_project_meta` | walk | `Context` section nodes (`CLAUDE.md`, `.claude/...`) and `Specs` section nodes have `project_meta is None` | `blocker` (FR-19 carve-out) |
| `test_specs_subtree_only_ai_video` | walk | every `path` under the `Specs (ai_video)` section starts with `specs/ai_video/`; NEVER `specs/development/` | `critical` (FR-7/FR-8) |
| `test_no_projects_subtree_in_tree` | walk | NO `path` starts with `projects/` (FR-8) | `critical` |
| `test_sort_order_alphabetical_dirs_first` | walk every non-leaf | `children` are sorted: dirs first (alpha within), then files (alpha within) | `blocker` (FR-20) |
| `test_no_path_uses_backslash` | walk | every `path` is forward-slash only | `blocker` |
| `test_excludes_audit_git_node_modules` | walk | no path segment in `{".audit", ".git", "node_modules"}` | `critical` |
| `test_dotclaude_agent_refs_recursive` | walk | at least one `.claude/agent_refs/project/ai_video.md` leaf appears (FR-7 recursive glob) | `blocker` |

The consumer-walk skeleton (move #2):

```python
def _walk(node):
    yield node
    for c in node.get("children", []) or []:
        yield from _walk(c)

def test_tree_consumer_walk(client):
    """Descend ONLY via `node.children` and assert no missing descent field.

    Mirrors the frontend Sidebar's recursion. Per agent_refs/validation/development.md
    move #2 — pure-shape unit tests are insufficient; the test must walk the data
    the way the consumer walks it.
    """
    r = client.get("/api/tree")
    assert r.status_code == 200
    tree = r.json()
    for node in _walk(tree):
        if node.get("type") in {"file", "image"}:
            assert "children" not in node or node["children"] == [], (
                f"leaf carries non-empty children: {node.get('path')!r}"
            )
        else:
            assert "children" in node, f"non-leaf missing 'children' key: {node.get('name')!r}"
            assert isinstance(node["children"], list)
        for forbidden in ("projects", "stages", "task_type", "files", "items", "videos", "episodes"):
            assert forbidden not in node, (
                f"forbidden legacy descent field {forbidden!r} on {node.get('name')!r}"
            )

def test_ai_videos_project_meta_present(client):
    r = client.get("/api/tree")
    tree = r.json()
    ai_videos = next(c for c in tree["children"] if c["name"] == "AI Videos")
    project_dirs = [c for c in ai_videos["children"] if c.get("type") == "dir"]
    assert project_dirs, "AI Videos section has no project dirs"
    for pd in project_dirs:
        assert "project_meta" in pd, f"{pd['name']} missing project_meta"
        meta = pd["project_meta"]
        assert meta is None or isinstance(meta, dict)
        if pd["name"] == "wukong_juexing":
            assert meta is not None
            assert meta["sub_type"] == "short"  # real qa.md says short
            assert meta["episode_count"] is None  # shorts have no episodes
```

### 5. `file_reader.py` — `test_file_reader.py` *(port + add image route)*

| Test | Inputs | Expected | Severity |
|---|---|---|---|
| `test_read_text_file_returns_content_and_mtime` | `CLAUDE.md` | `{content: str, mtime: float, bytes: int}`, content non-empty | `critical` |
| `test_read_image_file_returns_binary_with_correct_content_type` | `ai_videos/wukong_juexing/characters/ref_images/<stem>.png` (write fixture if absent) | response is raw bytes; `Content-Type: image/png`; `Last-Modified` set; `Cache-Control: private, max-age=0, must-revalidate` (FR-25, FR-26) | `blocker` |
| `test_read_image_jpg_returns_image_jpeg` | `.jpg` fixture | `Content-Type: image/jpeg` | `blocker` |
| `test_read_image_accepts_mtime_query_string` | `?mtime=12345.0` | response is fresh; mtime value is informational only — never consulted; cache headers identical (FR-26) | `blocker` |
| `test_read_size_cap_413` | `> 1 MiB` body | 413 (FR-14) | `blocker` |
| `test_read_extension_disallowed_415` | `.exe` fixture under EXPOSED_TREE | 415 (FR-13) | `critical` |
| `test_read_svg_disallowed_415` | `.svg` fixture | 415 (FR-13 SVG NOT allowed — code-execution vector) | `critical` |
| `test_read_outside_tree_404` | `projects/foo/bar.md` | 404 single signal (FR-8) | `critical` |
| `test_read_unicode_chinese_filename_works` | path with Chinese chars (e.g. `ai_videos/wukong_juexing/__scratch__/测试.md`) — write then read | round-trips byte-identically (NFR-7) | `blocker` |

### 6. `file_writer.py` — `test_file_writer.py` *(port + add image-rejection)*

| Test | Inputs | Expected | Severity |
|---|---|---|---|
| `test_put_atomic_write_via_temp_file` | new path under `__scratch__/` | content lands at the canonical path; no leftover temp file in same dir; mtime returned | `blocker` (FR-29) |
| `test_put_extension_writeable_allowlist` | parametrize `.md, .json, .yaml, .yml, .jsonl, .txt` | all 200 | `blocker` (FR-27/FR-28) |
| `test_put_image_extensions_rejected_400` | parametrize `.png, .jpg` | 400 (FR-13/FR-28 image extensions excluded from writeable list) | `critical` |
| `test_put_disallowed_extension_400` | `.exe`, `.html`, `.svg` | 400 | `critical` |
| `test_put_size_cap_413` | body > 1 MiB | 413 (FR-14) | `blocker` |
| `test_put_size_soft_warning_logged_at_50KiB` | body 51 KiB; capture log | log line written at WARN level; status 200 (FR-14) | `warning` |
| `test_put_if_unmodified_since_required_400_or_428` | PUT without `If-Unmodified-Since` header | 400 or 428 (FR-15) | `blocker` |
| `test_put_stale_mtime_returns_409` | mtime older than disk mtime by ≥1 sec | 409 (FR-15) | `critical` (concurrency contract) |
| `test_put_outside_tree_404` | path outside EXPOSED_TREE | 404 (FR-28) | `critical` |
| `test_put_returns_new_mtime` | success | `{mtime: float}` matches new disk mtime | `blocker` (FR-29) |
| `test_put_atomic_temp_in_same_directory_not_tmp_dir` | success | temp file (during write) never appears under `%TEMP%` — must be sibling of target (FR-29 atomic via same-dir rename) | `blocker` (`os.replace` cross-volume safety on Windows, NFR-7) |

### 7. `promotions.py` — `test_promotions.py` *(port byte-identical contract per FR-33)*

| Test | Severity |
|---|---|
| `test_parse_promoted_text_round_trip` (per spec_driven) | `blocker` |
| `test_serialize_promoted_block_byte_identical_to_spec_driven` — read a known fixture from `projects/spec_driven/.../validation/promoted.md`, round-trip through this app's `_serialize_promoted_block`, assert byte-identical output | `critical` (FR-33 byte-identical contract) |
| `test_promote_post_then_delete_round_trip` (HTTP) | `blocker` |
| `test_promote_rejects_stage_execution_400` — POST `/api/promote` with `stage="execution"` | 400 (FR-32) | `critical` |
| `test_promote_rejects_path_under_ai_videos_400` — POST `/api/promote` with `source_path="ai_videos/wukong_juexing/script.md"` | 400 (FR-32 — only `specs/ai_video/{name}/...` is promotable) | `critical` |
| `test_promote_accepts_path_under_specs_ai_video` | 200 | `blocker` |
| `test_promote_stage_folder_allowlist` | 422 for `user_input` | `blocker` |
| `test_promoted_md_header_uses_ai_video_management_app_name` — sanity check the header line in `<stage>/promoted.md` (mirrors the spec_driven header but with this app's name) | `warning` |

### 8. `regen_prompt.py` — `test_regen_prompt.py` *(port + add ai_video scope variants)*

Port from spec_driven the `_READ_ZERO_CONTRACT` and `_AUTONOMOUS_IMPERATIVE` byte-checks (FR-37). Then add:

| Test | Inputs | Expected | Severity |
|---|---|---|---|
| `test_read_zero_contract_byte_identical_to_spec_driven` | read `_READ_ZERO_CONTRACT` constant from this app + from `projects/spec_driven/.../regen_prompt.py` | bytes equal (FR-37 contract) | `critical` |
| `test_autonomous_imperative_byte_identical_to_spec_driven` | same | bytes equal (FR-37) | `critical` |
| `test_assembled_prompt_starts_with_execution_mode_header` | mode=INTERACTIVE | starts with `# EXECUTION MODE: INTERACTIVE` | `blocker` |
| `test_assembled_prompt_autonomous_header` | mode=AUTONOMOUS | starts with `# EXECUTION MODE: AUTONOMOUS` | `blocker` |
| `test_assembled_prompt_inlines_revised_prompt` | known project | `revised_prompt.md` content present verbatim (FR-39) | `critical` |
| `test_assembled_prompt_inlines_follow_ups` | project with follow-ups | every `user_input/follow_ups/*.md` content present (FR-39) | `critical` |
| `test_assembled_prompt_inlines_promoted_md_when_nonempty` | stage with `promoted.md` | content present verbatim (FR-39, pinned-items contract) | `critical` |
| `test_assembled_prompt_includes_audit_event_tags` | any | substrings `regen.delete.planned`, `regen.delete.completed`, `regen.write.completed` (FR-39) | `blocker` |
| `test_project_type_must_be_ai_video_400` | `project_type="development"` in body | 400 (FR-34 hard-locked) | `critical` |
| `test_scope_project_default_for_short` | `wukong_juexing` (sub_type=short), no scope passed | scope defaults to `project`; prompt body uses `short × project` template (FR-38) | `blocker` |
| `test_scope_episode_on_short_400` | `wukong_juexing`, `scope="episode", scope_episode=5` | 400 (FR-36) | `critical` |
| `test_scope_episodes_on_short_400` | `wukong_juexing`, `scope="episodes"` | 400 (FR-36) | `critical` |
| `test_scope_episode_on_novel_assembles_correctly` | a novel project (fixture), `scope="episode", scope_episode=3` | response 200; `scope_resolved` mentions `ep03`; prompt body delete contract scoped to `ai_videos/{name}/episodes/ep03/` only; explicitly preserves `characters/`, `world.md`, `style_guide.md`, `arc_outline.md` (FR-38 novel × episode N) | `critical` |
| `test_scope_episodes_range_expanded_inline` | novel, `scope="episodes", scope_episode_range={start: 5, end: 7}` | prompt body lists `ep05`, `ep06`, `ep07` literally — no `M..N` shorthand (FR-38 novel × episodes M..N) | `critical` |
| `test_scope_episodes_range_inverted_400` | `start=7, end=5` | 400 (FR-34 `start ≤ end`) | `blocker` |
| `test_scope_episodes_range_zero_400` | `start=0, end=3` | 400 (FR-73 `≥1`) | `blocker` |
| `test_scope_episode_missing_episode_number_400` | `scope="episode"` no `scope_episode` | 400 (FR-36) | `blocker` |
| `test_scope_episodes_missing_range_400` | `scope="episodes"` no `scope_episode_range` | 400 (FR-36) | `blocker` |
| `test_scope_unknown_subtype_409_when_not_project` | project whose `qa.md` is missing/unparseable, `scope="episode"` | 409 (FR-36) | `critical` |
| `test_scope_unknown_subtype_succeeds_when_project` | same, `scope="project"` | 200 (FR-73 — `None` falls back to project) | `blocker` |
| `test_assembled_prompt_under_50_KiB_no_warning` | small project | no warning in response `warning` field | `warning` |
| `test_assembled_prompt_50_KiB_to_1_MiB_warning_logged` | mid-size | response carries soft warning (FR-36) | `warning` |
| `test_assembled_prompt_over_1_MiB_413` | over-large | 413 (FR-36) | `blocker` |
| `test_short_project_template_matches_ai_video_md_layout` | `wukong_juexing` | prompt body reflects the short-layout delete contract (`script.md`, `style_guide.md`, `shotlist.md`, `prompts/`, `characters/`, `publish.md`) per `agent_refs/project/ai_video.md` rule 10 | `blocker` |
| `test_novel_project_template_matches_ai_video_md_layout` | novel fixture | prompt body reflects novel layout (`world.md`, `arc_outline.md`, `episodes/epNN/...`) | `blocker` |
| `test_stage_1_to_5_prompt_body_byte_identical_to_spec_driven_modulo_project_type_line` | for each stage `intake|interview|research|spec|validation_strategy` generate prompt and compare to spec_driven equivalent; only diff is `project_type=ai_video` line + optional `sub_type` line (FR-37) | `critical` |

### 9. `stages.py` — `test_stages.py` *(port verbatim shape; reassert each of 6 stage IDs + module slugs)*

| Test | Severity |
|---|---|
| `test_stages_count_is_six` | `blocker` |
| `test_stage_ids_match_canonical_six` (`intake, interview, research, spec, validation_strategy, execution`) | `blocker` |
| `test_each_stage_has_id_label_folder_invocation_modules` | `blocker` |
| `test_stages_for_ai_video_specific_modules` — execution stage modules include ai_video-specific slugs (e.g., `characters`, `script`, `shotlist`, `prompts`, `publish`) per `agent_refs/project/ai_video.md` | `warning` |

### 10. `api_security.py` — `test_api_security.py` *(port + adjust port to 8766; cover BOTH shapes per move #11)*

Port the spec_driven security tests with port 8765 → 8766. Move #11 explicitly: BOTH pre-rewrite and post-rewrite Origin shapes covered.

| Test | Inputs | Expected | Severity |
|---|---|---|---|
| `test_bound_origin_8766_only` | various Origin/Host combos | only `127.0.0.1:8766` and `localhost:8766` admit; everything else 403 (FR-11) | `critical` |
| `test_8765_origin_rejected_403` | `Origin: http://127.0.0.1:8765` (sister webapp `spec_driven`) | 403 — `8765` is foreign to this app (FR-11) | `critical` (cross-port admission would let spec_driven mutate this app's state) |
| `test_8765_host_rejected_403` | `Host: 127.0.0.1:8765` | 403 (FR-11) | `critical` |
| `test_localhost_alias_admitted` | `Origin: http://localhost:8766, Host: localhost:8766` | 200 (FR-11) | `blocker` |
| `test_cross_product_127_origin_localhost_host_admitted` | `Origin: http://127.0.0.1:8766, Host: localhost:8766` | 200 (FR-11 alias rules) | `blocker` |
| `test_ipv6_loopback_rejected_403` | `Origin: http://[::1]:8766, Host: [::1]:8766` | 403 (FR-3 IPv4-only bind) | `critical` |
| `test_zero_origin_rejected_403` | `Origin: http://0.0.0.0:8766` | 403 (FR-3) | `critical` |
| `test_missing_origin_403` | no Origin header | 403 (FR-11) | `critical` |
| `test_foreign_origin_403` | `evil.example.com` | 403 | `critical` |
| `test_pre_rewrite_dev_server_origin_rejected_403` (move #11) | `Origin: http://localhost:5174, Host: 127.0.0.1:8766` (raw browser shape direct-to-backend; the Vite proxy is supposed to rewrite this) | 403 (FR-11; per move #11 — proves the Vite proxy rewrite is load-bearing; missing this case = `blocker` per `agent_refs/validation/development.md`) | `blocker` |
| `test_post_rewrite_origin_admitted` (move #11) | `Origin: http://127.0.0.1:8766, Host: 127.0.0.1:8766` (post-rewrite shape — what `make run-prod` produces) | 200 (FR-11) | `blocker` |
| `test_get_endpoints_skip_origin_check` | `GET /api/tree` and `GET /api/file` with `Origin: http://evil.com` | 200 — read endpoints are NOT origin-validated (FR-9 only state-changing routes are gated) | `blocker` |
| `test_csp_header_on_responses` | any GET | `Content-Security-Policy` header present and matches FR-17 string verbatim | `critical` |
| `test_csp_includes_object_src_none_and_base_uri_self` | any GET | substrings `object-src 'none'` and `base-uri 'self'` (FR-17 hardening against plugin / `<base>` injection) | `critical` |
| `test_x_content_type_options_nosniff` | `GET /api/file?path=CLAUDE.md` | `X-Content-Type-Options: nosniff` | `blocker` |
| `test_content_disposition_attachment_on_text_file_get` | same | `Content-Disposition` contains `attachment` (port from spec_driven) | `blocker` |

### 11. `api.py` — `test_api.py` *(endpoint surface; port + add ai_video)*

Verb whitelist (NFR-6 / FR-9 — only 4 state-changing endpoints):

| Test | Severity |
|---|---|
| `test_patch_on_file_returns_405` | `blocker` |
| `test_delete_on_file_returns_405` | `blocker` |
| `test_post_on_file_returns_405` | `blocker` |
| `test_post_on_tree_returns_405` | `blocker` |
| `test_no_create_endpoint` — POST/PUT to any `/api/file/create*`, `/api/upload`, `/api/dir/*` | 404 (FR-9 explicit "no file create / delete / upload endpoints") | `critical` |

Tree:

| Test | Severity |
|---|---|
| `test_get_tree_returns_recursive_shape_with_three_sections` | `critical` |
| `test_get_tree_top_level_order_ai_videos_specs_context` | `critical` (FR-18 fixed order) |

File reader:

| Test | Severity |
|---|---|
| `test_get_file_text_happy_path` | `blocker` |
| `test_get_file_image_happy_path` | `blocker` |
| `test_traversal_returns_single_404` (parametrize ADS, reserved name, `..`, percent-encoded, mixed slash) | `critical` |
| `test_extension_disallowed_415` | `critical` |
| `test_size_cap_413` | `blocker` |

File writer:

| Test | Severity |
|---|---|
| `test_put_with_legitimate_origin_succeeds_returns_new_mtime` | `blocker` |
| `test_put_with_localhost_origin_succeeds` | `blocker` |
| `test_put_image_extension_400` | `critical` (FR-13/FR-28) |
| `test_put_stale_mtime_409` | `critical` (FR-15) |
| `test_put_size_cap_413` | `blocker` |
| `test_put_disallowed_extension_400` | `critical` |
| `test_put_outside_tree_404` | `critical` |

Regen-prompt route surface:

| Test | Severity |
|---|---|
| `test_post_regen_prompt_returns_documented_shape` (`{prompt, scope, scope_resolved, byte_size}` per FR-35) | `critical` (API shape drift = `critical` per dev refs) |
| `test_post_regen_prompt_validates_body_shape_422` | `blocker` |
| `test_post_regen_prompt_foreign_origin_403` | `critical` |
| `test_post_regen_prompt_dev_server_origin_pre_rewrite_403` (5174, not 5173 — this app's dev port per FR-6) | `blocker` (move #11) |
| `test_post_regen_prompt_project_type_development_400` (FR-34 hard-lock) | `critical` |

Promotions route surface (port 8 tests verbatim with origin port adjusted):

| Test | Severity |
|---|---|
| `test_promote_post_then_delete` | `blocker` |
| `test_promote_stage_folder_allowlist` | `blocker` |
| `test_promote_post_foreign_origin_403` | `critical` |
| `test_promote_delete_foreign_origin_403` | `critical` |
| `test_promote_stage_execution_400` | `critical` (FR-32) |
| `test_promote_path_under_ai_videos_400` | `critical` (FR-32) |

Unknown route:

| Test | Severity |
|---|---|
| `test_unknown_route_returns_404` | `warning` |

### 12. `sub_type_lookup.py` — `test_sub_type_lookup.py` *(NEW — move #10 critical: parser regex tested against real upstream output)*

See § Parser-regex-against-real-artifact below for the canonical move-#10 test. Module surface:

| Test | Inputs | Expected | Edge cases | Severity |
|---|---|---|---|---|
| `test_lookup_against_real_wukong_juexing_qa_md` | real on-disk `specs/ai_video/wukong_juexing/interview/qa.md` | `"short"` (matches the settled-fact row in the real file) | none — load-bearing real-artifact test | `critical` (move #10 — regex untested against real upstream output = `blocker` per dev refs; this test eliminates that risk) |
| `test_lookup_returns_none_when_qa_md_missing` | project name with no `qa.md` | `None` (FR-23 — never crash) | `blocker` |
| `test_lookup_returns_none_when_row_missing` | qa.md without the `sub_type` row (write fixture) | `None` (FR-23) | `blocker` |
| `test_lookup_returns_none_on_value_typo` | qa.md with `\| sub_type \| novell \|` (typo) | `None` — never invent a third value (FR-23) | `critical` (FR-23 explicit prohibition on inventing values) |
| `test_lookup_returns_none_on_multiple_rows` | qa.md with two `sub_type` rows (one `short`, one `novel`) | `None` (FR-23 — ambiguity refused) | `blocker` |
| `test_lookup_handles_backtick_wrapping` | row written `\| `sub_type` \| `novel` \|` | `"novel"` (regex tolerates backticks per FR-22) | `blocker` |
| `test_lookup_handles_no_backticks` | row written `\| sub_type \| novel \|` | `"novel"` (regex tolerates absence per FR-22) | `blocker` |
| `test_lookup_handles_extra_whitespace` | various spacing inside cells | matches both `short` and `novel` | `blocker` |
| `test_lookup_case_sensitive_on_value` | row with `\| sub_type \| Short \|` | `None` (regex literal `(novel\|short)` lowercase) | `warning` (lock the contract — uppercase variants come from spec drift) |
| `test_lookup_does_not_match_inside_backtick_code_block` | qa.md with the line inside a fenced code block | currently MAY match (regex is multiline; documents intent) | `warning` (document and accept; pin to `qa.md` table convention) |
| `test_lookup_handles_crlf_line_endings` | qa.md saved with CRLF (Windows) | matches identically (NFR-7) | `blocker` |
| `test_lookup_handles_unicode_chinese_qa_md` | qa.md whose other content includes CJK characters | matches without crash (FR-23 robustness) | `blocker` |
| `test_lookup_idempotent` | call twice on same file | identical result | `warning` |
| `test_lookup_consumes_same_value_as_sidebar_badge_and_regen_gating` (FR-24 single-source-of-truth) — call `sub_type_lookup.lookup("wukong_juexing")` directly AND via the route that drives the sidebar badge AND via the regen-prompt scope-validation path; assert the three values are identical | `critical` (FR-24 single source of truth) |

### 13. `main.py` — `test_main.py` *(small surface — covered by boot-smoke; one micro-test here)*

| Test | Inputs | Expected | Severity |
|---|---|---|---|
| `test_main_module_under_15_lines` | line count of `main.py` | `≤ 15` (FR-2) | `warning` |
| `test_main_imports_create_app_and_uvicorn` | source-import check | `from libs.api import create_app` + `import uvicorn` present | `blocker` |
| `test_main_binds_127_0_0_1_and_8766` | source-grep | the literal strings `"127.0.0.1"` and `8766` (NOT `0.0.0.0`, NOT `[::1]`) appear in the `uvicorn.run(...)` call | `critical` (FR-3, FR-4) |

---

## Boot-smoke (move #4)

`test_boot_smoke.py` is the canonical answer to move #4: every backend service must start cleanly and at least one structurally meaningful endpoint must return the expected shape under real workload before the unit is declared done.

**File:** `backend/tests/unit/test_boot_smoke.py`
**Make target:** `make boot-smoke` (must use `pip install` + `.venv`, NEVER `uv run` per move #6).

Skeleton:

```python
"""
Boot-smoke — process starts; root + /api/tree return 200 + expected shape.

Per agent_refs/validation/development.md move #4 — every backend service: process
starts cleanly, first health-style endpoint returns 200, at least one
structurally-meaningful endpoint returns the expected shape under real workload.
Severity: failure is `critical`, halts immediately, no revision rounds.

Bound port: 8766 (FR-4). IPv4 loopback only (FR-3).
"""

from __future__ import annotations

import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError

import pytest

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
PORT = 8766
HOST = "127.0.0.1"
BOOT_TIMEOUT_S = 15


def _is_port_listening(host: str, port: int, timeout: float = 0.5) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        try:
            s.connect((host, port))
            return True
        except OSError:
            return False


def _wait_for_listen(host: str, port: int, timeout: float) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if _is_port_listening(host, port):
            return True
        time.sleep(0.25)
    return False


def _http_get(path: str, headers: dict[str, str] | None = None) -> tuple[int, bytes, dict[str, str]]:
    req = Request(f"http://{HOST}:{PORT}{path}", headers=headers or {})
    try:
        with urlopen(req, timeout=5) as resp:
            return resp.status, resp.read(), dict(resp.headers)
    except URLError as e:
        # propagate the HTTPError code where available
        if hasattr(e, "code"):
            return e.code, b"", {}
        raise


@pytest.fixture(scope="module")
def server():
    if _is_port_listening(HOST, PORT):
        pytest.skip(f"{HOST}:{PORT} already in use — run boot-smoke against a clean host")

    proc = subprocess.Popen(
        [sys.executable, str(BACKEND_DIR / "main.py")],
        cwd=str(BACKEND_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    try:
        if not _wait_for_listen(HOST, PORT, BOOT_TIMEOUT_S):
            # critical: process never started serving
            try:
                stdout, _ = proc.communicate(timeout=2)
            except subprocess.TimeoutExpired:
                proc.kill()
                stdout = b"<no stdout captured>"
            pytest.fail(
                f"backend never bound {HOST}:{PORT} within {BOOT_TIMEOUT_S}s. "
                f"stdout:\n{stdout.decode('utf-8', errors='replace')}"
            )
        yield proc
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


def test_root_returns_200(server):
    """SPA root serves (FR-5 single-process production OR FR-6 dev backend)."""
    status, body, _headers = _http_get("/")
    assert status == 200, f"root returned {status}; body: {body[:200]!r}"


def test_api_tree_returns_200_and_three_section_shape(server):
    """Move #4 — structurally meaningful endpoint returns expected shape."""
    status, body, headers = _http_get("/api/tree")
    assert status == 200
    import json
    tree = json.loads(body.decode("utf-8"))
    assert isinstance(tree, dict)
    children = tree.get("children")
    assert isinstance(children, list) and len(children) >= 3, (
        f"tree should have ≥3 top-level sections (AI Videos, Specs (ai_video), Context); got {[c.get('name') for c in (children or [])]}"
    )
    names = [c["name"] for c in children]
    assert "AI Videos" in names
    assert "Specs (ai_video)" in names
    assert "Context" in names


def test_api_file_returns_200_for_claude_md(server):
    """End-to-end read smoke — CLAUDE.md is in EXPOSED_TREE per FR-7."""
    status, body, _headers = _http_get("/api/file?path=CLAUDE.md")
    assert status == 200
    import json
    payload = json.loads(body.decode("utf-8"))
    assert "content" in payload
    assert "# CLAUDE.md" in payload["content"]


def test_does_not_bind_ipv6_loopback(server):
    """FR-3 — IPv4 only. `[::1]:8766` MUST refuse the connection."""
    with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        with pytest.raises(OSError):
            s.connect(("::1", PORT))


def test_does_not_bind_zero(server):
    """FR-3 — `0.0.0.0` MUST refuse (we bound only the loopback interface)."""
    # If 0.0.0.0 were bound, an external-facing interface would also accept.
    # Best-effort: assert at least the loopback works (positive control); the
    # negative — "no other interface listens" — is impossible to assert
    # portably from inside the same host. Document the constraint here and
    # rely on `test_main_binds_127_0_0_1_and_8766` (source-grep) for the
    # negative half.
    assert _is_port_listening(HOST, PORT)
```

Severity: every assertion in this file is `critical` per move #4. Failure halts immediately with no revision rounds.

Audit events emitted by the parent for this work-unit kind:
- `validation.started` with `unit_kind="boot_smoke"`.
- On pass: `validation.pass`.
- On fail: `validation.issue.raised` followed immediately by `pipeline.halted` (`critical`, no retry per move #4).

---

## Cross-platform skip (move #5)

Tests requiring POSIX-only OS behavior are marked `@pytest.mark.skipif(sys.platform == "win32", reason=...)` so they SKIP rather than fail on the canonical Windows host. Tests requiring Windows-only behavior carry the inverse marker. **Skipping with a clear reason is healthy; silent passing is a hidden bug** (general.md principle #3).

| Test | Marker | Reason string |
|---|---|---|
| `test_safe_resolve.test_rejects_symlink_outside_tree` | `skipif(sys.platform == "win32")` | "POSIX symlink test; Windows junctions tested separately (Developer Mode optional)" |
| `test_safe_resolve.test_rejects_windows_junction` | `skipif(sys.platform != "win32")` | "NTFS junction syntax (`mklink /J`); Windows-only" |
| `test_file_writer.test_put_atomic_temp_in_same_directory_not_tmp_dir` | (none — runs on both) | n/a — `os.replace` is portable; cross-volume failure mode is the same on POSIX and NTFS |
| `test_safe_resolve.test_rejects_windows_reserved_names` | (none — Windows reserved names rejected on every platform; the resolver normalizes the rule) | n/a — universal rejection (the resolver's contract is platform-independent) |
| `test_safe_resolve.test_rejects_windows_8_3_short_names` | (none) | n/a — universal rejection |
| `test_main.test_main_binds_127_0_0_1_and_8766` | (none — source grep is OS-independent) | n/a |
| `test_boot_smoke.test_does_not_bind_ipv6_loopback` | `skipif(not socket.has_ipv6)` | "host without IPv6 stack — refusal to bind `::1` is implicit" |
| Any test using `os.fork` | `skipif(sys.platform == "win32")` | "fork-based test; Windows lacks `os.fork`" — not currently any in the suite, but flagged here as the rule |
| Any test using POSIX-only signals (`SIGUSR1`, `SIGHUP`) | `skipif(sys.platform == "win32")` | "POSIX-only signal" — not currently any |
| Case-sensitivity tests (probing NTFS's case-insensitive behavior) | `skipif(sys.platform != "win32")` | "NTFS case-insensitivity probe" — only relevant if added |

Forbidden anti-patterns (will be flagged `blocker` in stage-6 review per dev refs "Test depends on POSIX behavior with no skip marker"):
- A POSIX-only test that just `pass`es silently when a POSIX-only call raises.
- A Windows-only test that's gated by a try/except that swallows the exception.
- A test that sets `pytest.mark.skip` (unconditional) instead of `skipif` — unconditional skip = hidden bug.

---

## Consumer-walk (move #2)

The full skeleton lives in § 模块测试矩阵 row 4 (`test_tree_walker.py`). The contract:

1. `test_tree_consumer_walk` recursively descends `node.children` (the literal field name the frontend Sidebar walks); fails loudly if any non-leaf is missing the descent field.
2. `test_tree_consumer_walk_uses_children_not_legacy_keys` asserts no node carries any of the legacy / lookalike fields (`projects`, `stages`, `task_type`, `files`, `items`, `videos`, `episodes`) — those are exactly the fields a parallel-spawned backend agent might emit when "thinking in domain terms" instead of mirroring the frontend's flat-recursive consumption pattern. This is the *exact* bug class that broke the spec_driven Projects sidebar in run `spec_driven-20260502-clean`.
3. `test_ai_videos_project_dirs_have_project_meta` asserts every direct child of the `AI Videos` section carries the `project_meta` field (FR-19), and that `wukong_juexing` specifically resolves to `sub_type="short"` — chained against the real on-disk `qa.md`, this doubles as an integration check that `tree_walker` actually consults `sub_type_lookup`.

Severity: missing `children`, presence of any forbidden legacy descent field, or missing `project_meta` on an AI-video project dir = `critical` (API shape drift between front and back is `critical` per dev refs severity table).

---

## Parser-regex-against-real-artifact (move #10)

The `sub_type_lookup` regex (FR-22):

```
^\|\s*`?sub_type`?\s*\|\s*`?(novel|short)`?\s*\|
```

is parser-for-stage-N+1 against text generated by stage-N (the interview stage). Per move #10 — *"the parser's regex MUST be tested against real output from stage N, not a hand-written fixture"* — the canonical test:

```python
"""
test_lookup_against_real_wukong_juexing_qa_md — move #10 critical test.

Per agent_refs/validation/development.md move #10 — when stage N produces text
consumed by stage N+1's parser, the parser's regex MUST be tested against real
output from stage N, not a hand-written fixture. The autonomous-mode interview
output that wrote `qa.md` may evolve; the regex must keep matching.

This test consults the REAL on-disk
`specs/ai_video/wukong_juexing/interview/qa.md` (created by run
wukong_juexing-20260503-201831). If that file changes shape — different table
header, different settled-facts encoding, different sub_type spelling — this
test fails LOUDLY rather than silently drifting. Severity: critical.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from libs.repo_root import RepoRoot
from libs.sub_type_lookup import lookup


REAL_QA_MD_REL = "specs/ai_video/wukong_juexing/interview/qa.md"


def test_lookup_against_real_wukong_juexing_qa_md():
    repo = RepoRoot.find()
    qa_md = repo.path / REAL_QA_MD_REL
    if not qa_md.exists():
        pytest.fail(
            f"real upstream artifact missing: {qa_md}. Move #10 requires the "
            "parser regex to be tested against an actual on-disk artifact "
            "from a representative recent run; create wukong_juexing first or "
            "update REAL_QA_MD_REL to point at a newer real run."
        )
    result = lookup("wukong_juexing")
    assert result == "short", (
        f"sub_type_lookup returned {result!r} for wukong_juexing; the real "
        f"qa.md at {REAL_QA_MD_REL} has the row "
        f"`| `sub_type` | `short` | User: \"short one like youtube shorts not a series\" |`"
        f" — the regex `^\\|\\s*`?sub_type`?\\s*\\|\\s*`?(novel|short)`?\\s*\\|` "
        "should match it. If the upstream interview format has drifted, update "
        "the regex AND this assertion in lockstep — never one without the other."
    )
```

Why this is non-negotiable:

- The real `qa.md` row uses **backtick-wrapped** field name AND value: `` | `sub_type` | `short` | … | ``. A regex written off the bare-spec example `| sub_type | short |` would silently miss this and return `None`.
- The real interview was AUTONOMOUS-mode (judgment-call format `*(judgment call — chose A because: ...)*`). A regex that accidentally anchored on Round-1 / "User:" prefix shape would break on autonomous-mode output. *(This is the exact lesson from `spec_driven-20260502-clean`'s QaView regex.)*
- The real qa.md is **CRLF on Windows** in the canonical dev environment. Multiline regex must still match.

Hand-written fixtures cover the negative space (typo, missing row, multiple rows, value typo); the **real artifact** is the single load-bearing positive case. Severity: **critical** — without it, future interview-format drift slips past validation, the sidebar badge stops showing, and the regen-scope toggle silently re-enables `episode N` on a `short` project (which 4xx's at `/api/regen-prompt` and looks like a backend bug).

---

## Move #6 enforcement — no `uv` in Make targets

Per move #6 — *"`uv run` has crashed with `EXCEPTION_ACCESS_VIOLATION` on this Windows host; validation Makefile targets MUST be implementable in plain `pip` + the repo's existing `.venv`. Flag any `uv` invocation without a pip fallback as `blocker`."*

**Stage-5 validation rule for the Makefile produced in stage 6:**

| Make target | MUST be | MUST NOT be | Severity if violated |
|---|---|---|---|
| `install` | `cd backend && python -m pip install -r requirements.txt` (+ frontend equivalent via `npm`) | `uv sync`, `uv pip install`, any `uv run` | `blocker` |
| `install-backend` | `cd backend && python -m pip install -r requirements.txt` | `uv pip install` | `blocker` |
| `run-backend` | `cd backend && python main.py` | `uv run python main.py` | `blocker` |
| `run-prod` | `make build-frontend && cd backend && python main.py` | any `uv` invocation | `blocker` |
| `test-backend` | `cd backend && python -m pytest tests/ -v` | `uv run pytest`, `uv run python -m pytest` | `blocker` |
| `boot-smoke` | `cd backend && python -m pytest tests/unit/test_boot_smoke.py -v` | `uv run pytest …` | `blocker` |
| `e2e` | `cd frontend && npm run test:e2e` | n/a (no `uv` interaction) | `blocker` |

A static check (CI lint, or a one-off `test_makefile_no_uv` test under `tests/unit/`):

```python
def test_makefile_no_uv_invocation():
    repo = RepoRoot.find()
    mk = (repo.path / "projects" / "ai_video_management" / "Makefile").read_text(encoding="utf-8")
    # Allow the literal word "uv" inside a comment that explains WHY uv is
    # forbidden (e.g., "# pip-only — no `uv` invocation"); flag every
    # non-comment occurrence.
    for lineno, line in enumerate(mk.splitlines(), start=1):
        stripped = line.split("#", 1)[0]
        assert "uv " not in stripped and "uv\t" not in stripped, (
            f"Makefile line {lineno} invokes `uv`: {line!r}. "
            "Move #6 forbids it on this Windows host (EXCEPTION_ACCESS_VIOLATION). "
            "Use `python -m pip install -r requirements.txt` against the repo .venv instead."
        )
```

Severity: `blocker` (per dev refs severity table — `uv run` invocation in Makefile with no pip fallback = `blocker`).

---

## 覆盖 FR 矩阵

| FR | Module(s) | Test(s) | Severity |
|---|---|---|---|
| FR-1 (backend libs layout) | all | every `test_<module>.py` exists | `blocker` |
| FR-2 (`main.py` ≤15 lines) | `main.py` | `test_main_module_under_15_lines` | `warning` |
| FR-3 (IPv4 loopback only) | `main.py`, `boot_smoke` | `test_main_binds_127_0_0_1_and_8766`, `test_does_not_bind_ipv6_loopback` | `critical` |
| FR-4 (port 8766) | `boot_smoke`, `api_security`, `main.py` | `test_main_binds_127_0_0_1_and_8766`, `test_bound_origin_8766_only`, `test_8765_origin_rejected_403` | `critical` |
| FR-5 (`run-prod` single-process) | boot-smoke + e2e (level-05) | `test_root_returns_200` (run-prod profile) | `blocker` |
| FR-6 (dev mode 8766/5174) | `api_security` | `test_pre_rewrite_dev_server_origin_rejected_403` (5174) | `blocker` |
| FR-7 (EXPOSED_TREE roots) | `exposed_tree`, `tree_walker` | `test_is_inside_accepts_*` (5 roots), `test_specs_subtree_only_ai_video`, `test_no_projects_subtree_in_tree` | `critical` |
| FR-8 (`is_inside` predicate) | `exposed_tree` | full `test_exposed_tree.py` suite | `critical` |
| FR-9 (4 mutation endpoints) | `api` | `test_no_create_endpoint`, `test_patch/delete/post_on_file_returns_405` | `critical` |
| FR-10 (read endpoints) | `api` | `test_get_tree_*`, `test_get_file_*` | `blocker` |
| FR-11 (Origin/Host gate) | `api_security` | full suite (8766 only, alias rules, IPv6 reject, foreign reject) | `critical` |
| FR-12 (path traversal → 404) | `safe_resolve`, `api` | groups 1.2-1.7, 1.10-1.13; `test_traversal_returns_single_404` | `critical` |
| FR-13 (extension allowlist) | `file_reader`, `file_writer`, `exposed_tree` | `test_read_extension_disallowed_415`, `test_read_svg_disallowed_415`, `test_put_image_extensions_rejected_400`, `test_is_inside_extension_allowlist_for_ai_videos` | `critical` |
| FR-14 (1 MiB body cap + 50 KiB warn) | `file_reader`, `file_writer` | `test_size_cap_413`, `test_put_size_soft_warning_logged_at_50KiB` | `blocker` |
| FR-15 (If-Unmodified-Since) | `file_writer`, `api` | `test_put_if_unmodified_since_required`, `test_put_stale_mtime_409` | `critical` |
| FR-16 (markdown sanitization) | covered by frontend Vitest + e2e (level 05); backend has no surface | n/a here | n/a |
| FR-17 (CSP header) | `api_security` | `test_csp_header_on_responses`, `test_csp_includes_object_src_none_and_base_uri_self` | `critical` |
| FR-18 (`/api/tree` 3 sections) | `tree_walker`, `api` | `test_root_has_three_top_level_sections`, `test_get_tree_top_level_order_ai_videos_specs_context` | `critical` |
| FR-19 (TreeNode + ProjectMeta) | `tree_walker` | `test_image_leaves_have_type_image`, `test_ai_videos_project_dirs_have_project_meta`, `test_non_ai_video_project_dirs_have_no_project_meta` | `critical` |
| FR-20 (sort order) | `tree_walker` | `test_sort_order_alphabetical_dirs_first` | `blocker` |
| FR-21 (refresh semantics) | covered by frontend (level 05) | n/a here | n/a |
| FR-22 (sub_type regex) | `sub_type_lookup` | `test_lookup_against_real_wukong_juexing_qa_md` + 8 fixture variants | `critical` |
| FR-23 (sub_type edge cases) | `sub_type_lookup` | `test_lookup_returns_none_when_*` × 4 | `critical` |
| FR-24 (single source of truth) | `sub_type_lookup` | `test_lookup_consumes_same_value_as_sidebar_badge_and_regen_gating` | `critical` |
| FR-25/FR-26 (`GET /api/file`) | `file_reader`, `api` | `test_read_text_file_*`, `test_read_image_file_*`, `test_read_image_accepts_mtime_query_string` | `blocker` |
| FR-27/FR-28 (`PUT /api/file`) | `file_writer`, `api` | full `test_file_writer.py` + 7 PUT tests in `test_api.py` | `critical` |
| FR-29 (atomic write + new mtime) | `file_writer` | `test_put_atomic_write_via_temp_file`, `test_put_returns_new_mtime`, `test_put_atomic_temp_in_same_directory_not_tmp_dir` | `blocker` |
| FR-30/FR-31/FR-32/FR-33 (promotions) | `promotions`, `api` | full `test_promotions.py`; `test_promote_stage_execution_400`, `test_promote_path_under_ai_videos_400`, `test_serialize_promoted_block_byte_identical_to_spec_driven` | `critical` |
| FR-34 (regen-prompt body schema) | `regen_prompt`, `api` | `test_project_type_must_be_ai_video_400`, `test_scope_episodes_range_inverted_400` | `critical` |
| FR-35 (regen-prompt response) | `api` | `test_post_regen_prompt_returns_documented_shape` | `critical` |
| FR-36 (regen-prompt 4xx surface) | `regen_prompt`, `api` | `test_scope_episode_on_short_400`, `test_scope_episodes_on_short_400`, `test_scope_unknown_subtype_409_when_not_project`, `test_assembled_prompt_over_1_MiB_413` | `critical` |
| FR-37 (stages 1-5 byte-identical) | `regen_prompt` | `test_read_zero_contract_byte_identical_to_spec_driven`, `test_autonomous_imperative_byte_identical_to_spec_driven`, `test_stage_1_to_5_prompt_body_byte_identical_to_spec_driven_modulo_project_type_line` | `critical` |
| FR-38 (stage 6 four templates) | `regen_prompt` | `test_short_project_template_*`, `test_novel_project_template_*`, `test_scope_episode_on_novel_assembles_correctly`, `test_scope_episodes_range_expanded_inline` | `critical` |
| FR-39 (regen-prompt inlines) | `regen_prompt` | `test_assembled_prompt_inlines_revised_prompt`, `test_assembled_prompt_inlines_follow_ups`, `test_assembled_prompt_inlines_promoted_md_when_nonempty`, `test_assembled_prompt_includes_audit_event_tags`, `test_assembled_prompt_starts_with_execution_mode_header` | `critical` |
| FR-82 (backend pytest scope) | all | every module under `backend/libs/` has a `test_<module>.py` with at least one positive + one negative test | `blocker` |
| FR-83 (boot-smoke) | `boot_smoke` | full `test_boot_smoke.py` | `critical` |
| NFR-1 (pip-only, no `uv`) | Makefile | `test_makefile_no_uv_invocation` | `blocker` |
| NFR-7 (cross-platform) | every test | skip markers per § Cross-platform skip; CRLF/CJK-filename tests | `blocker` |

---

## Audit-event contract for stage 6

Each test module in this strategy maps to one stage-6 work-unit kind. Per general.md principle #5 — *"a level without audit events is treated as if it didn't run"* — the parent emits, for every backend-tests work unit:

- `validation.started` with `unit_kind="backend_tests:<module>"` and `pre_reading_consulted` array including this file's absolute path.
- For each pytest test that fails: `validation.issue.raised` with `severity` per the matrix above.
- `validation.pass` once all tests in that module pass; OR `pipeline.halted` (with summary) if a `critical`-severity test fails (no revision rounds for `critical`); OR after 3 revision rounds for `blocker` failures.
- `validation.requires_manual_walkthrough` is NOT emitted from this level (this is a pure-automated gate; manual walkthrough is owned by level-specialist-06).

The boot-smoke unit uses `unit_kind="boot_smoke"` and `severity="critical"` per move #4 — pipeline halts on any failure with no retry.

---

## Out of scope for this level

- Frontend Vitest (`shotPairing.ts`, `shotlistParser.ts`, `linkResolver.ts` — owned by level-05 e2e + frontend specialists).
- Playwright e2e suites (level-05).
- Acceptance-criteria document (level-01).
- BDD scenarios (level-02).
- Security review beyond the gate-tests above (level-04).
- Accessibility / manual walkthrough (level-06).
