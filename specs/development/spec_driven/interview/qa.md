# Interview — spec_driven

Run: spec_driven-20260503-030434 (autonomous full-pipeline clean regen)

## Categories probed

- **functional-scope** — what the editor surfaces, what it edits, what's still in/out after follow-up 001 + 002.
- **ux-interaction** — file-pane affordances, structured Q/A view, regenerate panel layout, autonomous-mode toggle, soft-wrap UX.
- **data-model** — the canonical project tree the backend walks; how follow-ups + promoted.md feed regen.
- **edge-cases** — empty / oversized / corrupt artifacts, broken links, OS-specific traps (Windows + Git Bash).

## Round 1 (autonomous, judgment-call answers)

Interview manager runs parent-direct shape A (direct generation, no per-category workers). Each answer is annotated `*(judgment call — chose X because Y)*` with the FR slice it informs.

### functional-scope

**Q:** Section 2 ("Projects") — which projects appear in the tree?
- A: All discovered (Recommended) — backend walks `specs/{type}/{name}/` for every type+name pair on disk; show all. `spec_driven` is just the first; `ai_video` etc. appear automatically when present.

*(pin-001 preserved verbatim from interview/promoted.md — answer ratified during interactive Round 1 in run `spec_driven-20260502-clean`. Binds FR-12 / FR-13.)*

**Q:** Which file types under the exposed tree are openable in the main pane?
- A *(judgment call — chose "markdown + YAML/JSON + JSONL + plain text" because Y)*: `.md`, `.json`, `.yaml`, `.yml`, `.jsonl`, `.txt`. Binary files (images under findings/) render as a placeholder. **Why:** the spec-driven workflow's artifacts are exclusively text; binary support beyond placeholders is YAGNI. Binds FR-9, FR-10, NFR-4.

**Q:** Is the `agent_team` orchestrator a permanent agent file under `.claude/agents/`?
- A *(judgment call — chose "no, it's a skill" because Y)*: `agent_team` lives under `.claude/skills/agent_team/` as a top-level SKILL with `playbooks/{interview,research,validation}.md`. **Why:** the parent IS the manager (per CLAUDE.md "Tool scoping" section); the playbooks are runbooks the parent reads inline at each stage. No separate manager subagent. Binds FR-3, FR-4, FR-5.

**Q:** Are deletes / uploads exposed by the editor?
- A *(judgment call — chose "no" because Y)*: only `PUT /api/file` (modify existing) and `POST /api/regen-prompt` (assemble) — no DELETE, no upload, no create-new-file. **Why:** every artifact in the workflow is created by the pipeline, not by hand; manual creation invites parallel state surfaces (the anti-pattern CLAUDE.md explicitly forbids). Binds NFR-6.

### ux-interaction

**Q:** Markdown link resolution under the editor — relative vs absolute?
- A *(judgment call — chose "relative-only, broken links muted" because Y)*: relative links resolve against the current file's directory; absolute http(s) links open in a new tab; broken links render as muted spans (not anchors) with a `title` tooltip describing the cause. **Why:** the muted-span pattern surfaces issues without breaking flow; making them real anchors invites accidental external nav. Binds FR-33, FR-34, FR-35.

**Q:** Structured Q/A view for `interview/qa.md` — flat markdown or color-block?
- A *(judgment call — chose "color-block with per-Q/A pencil edit" because Y)*: rounds → categories → Q/A pairs render as discrete blocks; Q tinted blue, A tinted green; category badge in header. Each Q and each A has a ✎ inline edit pencil. Whole-file edit remains via the toolbar toggle. **Why:** spec-driven Q/A maps to a strict tree; rendering it flat costs the tree affordance. Binds FR-41a..d.

**Q:** Regenerate panel layout — single panel per stage, or master at project page?
- A *(judgment call — chose "both" because Y)*: a per-stage collapsible `<details>` panel above any file under a stage subfolder, AND a master panel at `/project/{type}/{name}` that selects across stages. Same `localStorage` value drives the autonomous toggle on both. **Why:** users alternate between "rerun this one stage" and "rerun the world"; a single surface forces them to navigate either way. Binds FR-42, FR-43, FR-44.

**Q:** Assembled regen prompt — visible inline, or behind a `<details>` expander?
- A *(judgment call — chose "inline visible block with header bar Copy + Wrap toggle" because Y)*: after `Build prompt` succeeds, the prompt renders directly inside a bordered block. Header bar carries title, "Wrap" toggle (default ON), and a prominent **Copy** button (label flips to "Copied!" for ~1.5s). **Why:** follow-up 002 explicitly removed the inner `<details>` — a one-click visible Copy is friendlier than a two-click expand-then-copy. Binds FR-42(f).

**Q:** Autonomous-mode toggle persistence?
- A *(judgment call — chose "localStorage, per-tab synced via storage events, default off" because Y)*: persisted under `spec_driven.autonomous_mode.v1`. Default is **interactive**. Same value across per-stage and project-page panels. **Why:** accidental autonomous runs should not be the path of least resistance; the user makes an explicit choice each session. Binds FR-44.

### data-model

**Q:** Sidebar tree shape returned by `GET /api/tree` — flat list or recursive?
- A *(judgment call — chose "recursive with `children`" because Y)*: top-level sections "Claude Settings & Shared Context" and "Projects". Each tree node has `{name, path, type, children: []}`. Frontend descends `node.children` uniformly. **Why:** prior run `spec_driven-20260502-clean` had a contract drift where backend emitted `task_type.projects` and `project.stages` while frontend walked `node.children` — that produced an empty Projects sidebar (per `agent_refs/validation/development.md` move #2). The unified `children` field eliminates that class of bug. Binds FR-7, FR-8, AC-3.

**Q:** What does the regen-prompt assembler include?
- A *(judgment call — chose "intent + follow-up list + selected stages + every selected stage's promoted.md inline" because Y)*: `revised_prompt.md` (or raw if no revised), every `user_input/follow_ups/*.md` filename, the selected stages with their invocation hints + module list, and any non-empty `<stage>/promoted.md` inlined verbatim under "Pinned items (MUST survive regeneration)". **Why:** a regen prompt is self-contained; a fresh Claude session can act on it without browsing other files. Binds FR-14c.

**Q:** Where do follow-ups land?
- A *(judgment call — chose "specs/{type}/{name}/user_input/follow_ups/NNN-{YYYYMMDD-HHmmss}-{slug}.md" because Y)*: NNN is the zero-padded sequence; the timestamp + slug make the filename self-describing. revised_prompt.md is auto-regenerated = raw + every follow-up in numerical order. **Why:** the convention is documented in CLAUDE.md → "Follow-up prompt handling"; consistent naming makes the audit trail readable. Binds the auto-regen rule + changelog protocol.

### edge-cases

**Q:** Path safety — symlinks, parent traversal, hidden files?
- A *(judgment call — chose "deny symlinks, deny `..` traversal, deny dotfiles outside the exposed tree" because Y)*: `safe_resolve` refuses any path that, after resolution, falls outside the EXPOSED_TREE; refuses any symlink (including upstream symlinks); refuses dotfiles unless explicitly listed (`.claude/...` is in the tree, individual dotfiles are not). **Why:** localhost is not a security boundary on a multi-user dev box; defense in depth. Binds NFR-4, NFR-5, NFR-6, security tests.

**Q:** Oversized files in the editor — what's the cap?
- A *(judgment call — chose "1 MB hard cap; reads above cap return 413" because Y)*: the editor refuses to load files > 1 MB. Same cap on writes. **Why:** the workflow's largest realistic artifacts are dossiers + spec.md (~50 KB each); 1 MB is generous headroom while bounding worst-case memory. Binds NFR-2, AC-19.

**Q:** Regenerate-prompt size — assembled prompt > 50 KB?
- A *(judgment call — chose "warn-don't-truncate at 50 KB; 413 above 1 MB; emit prompt in full below" because Y)*: response body returns `{warning: "..."}` when > 50 KB so the UI can render a banner; the prompt itself is always full-length unless the request would exceed 1 MB (then 413 with `kind: "too_large"`). **Why:** silent truncation is a footgun; the user must see the size before pasting. Binds FR-14c, FR-42(d/e), AC-19.

**Q:** Windows + Git Bash quirks — what's skipped?
- A *(judgment call — chose "POSIX symlinks, os.replace atomicity, case-sensitivity, fork/signals" because Y)*: any test that depends on those uses `pytest.mark.skipif(sys.platform == "win32", reason="...")` — never a silent pass. **Why:** the canonical dev host is Windows + Git Bash (`agent_refs/validation/development.md` move #5). Skipping is fine; silent passing is not. Binds NFR-7, validation/system_tests, validation/unit_tests.

**Q:** Frontend render-mode dispatch — what gets its own component?
- A *(judgment call — chose "MarkdownView (default), QaView (interview/qa.md), JsonlView (.jsonl), CodeView (.json/.yaml/.yml), ImagePlaceholder (.png/.jpg/.svg fallback)" because Y)*: file-extension or path-pattern dispatch; each component has its own e2e scenario opening a real file (per `agent_refs/validation/development.md` move #8). **Why:** in run `spec_driven-20260502-clean`, qa.md deep-links produced a blank page because QaView's answer regex didn't match autonomous-mode `- A *(judgment call — ...)*: text` and `try { return <QaView/> } catch` did not catch React render errors. Latent-render-error class is `critical`. Binds FR-30, FR-41, validation moves #8 and #9.

## Team consensus

All 4 categories marked clear after Round 1 (autonomous mode). Each judgment-call annotation cites the FR slice it binds into, so a future interactive run can revise individual answers without re-deriving the rationale. pin-001 is preserved verbatim under functional-scope.
