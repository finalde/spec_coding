# Interview — spec_driven

Run: spec_driven-20260502-141813

## Categories probed

- **functional-scope** — what the readonly viewer surfaces, the v1 in/out boundary for each sidebar section, and how non-markdown files render.
- **discovery-data-model** — how the backend finds projects on disk, what root directories it scans, caching policy, and target scale.
- **ux-navigation** — sidebar grouping, landing page, code/markdown rendering, in-app link resolution, and large-file behavior.
- **deployment-runtime** — process topology (single binary vs. two processes), default port, startup commands, and how the backend locates the repo root.
- **success-criteria** — what counts as "v1 done", target browser, validation layers (BDD/e2e/unit), e2e framework, and whether a second project ships in v1.

## Round 1

### functional-scope

**Q:** Section 1 ("Claude Settings & Shared Context") — what exactly belongs here?
- A: Other — Free text: "claude.md, agents, skills, anything that is common and will impact spec driven results, could also include common things under specs folder if there is any (we don't need to include any project specific ones, those are reviewed in section 2, here is all the common things)". (Narrowed in round 2 — see SettListing below.)

**Q:** Per-project tree — which stage subfolders does the Projects section expose?
- A: All five (Recommended) — user_input/, interview/, findings/, final_specs/, validation/. No audit, no output folder, no extras.

**Q:** Non-markdown files (YAML execution plans, JSON event logs) — how should they render?
- A: Highlighted (Recommended) — client-side syntax highlighting (Shiki) plus line numbers.

**Q:** Implicit out-of-scope items from the prompt — confirm v1 excludes them?
- A: Confirm all out (Recommended) — v1 has NO authentication/multi-user, search, file-watch, auto-refresh, run controls, editing, deletes, or uploads.

### discovery-data-model

**Q:** How does the viewer discover projects?
- A: Scan per request (Recommended) — backend walks `specs/{task_type}/{task_name}/` on every API call. No persistent index, no manifest, no watcher.

**Q:** Which root directories are surfaced as projects?
- A: specs/ only (Recommended) — Projects tree is derived solely from `specs/{task_type}/{task_name}/`. Output folders (`projects/`, `ai_videos/`) are NOT surfaced as projects in v1.

**Q:** Caching strategy for filesystem reads?
- A: None (Recommended) — read filesystem on every request. No ETag, no TTL, no in-memory cache.

**Q:** Target scale for v1?
- A: Small (Recommended) — ≤50 projects, ≤200 files per project, individual files <500 KB. Optimize for clarity, not throughput.

### ux-navigation

**Q:** How should relative markdown links between artifacts behave?
- A: Internal clickable (Recommended) — relative links that resolve inside the exposed tree become in-app navigations. External links (http/mailto) open in a new tab. Broken links render as muted text with a tooltip.

**Q:** Sidebar grouping when multiple task_types exist?
- A: Collapsible by type (Recommended) — sidebar groups projects under one collapsible section per task_type (development, ai_video, …). The section containing the current project default-expands.

**Q:** Landing page on first open?
- A: spec_driven readme (Recommended) — auto-select Projects > development > spec_driven and render its final spec (or revised_prompt if the spec doesn't exist yet).

**Q:** Syntax highlighter for code/yaml/json/jsonl?
- A: Shiki (Recommended) — VS-Code-grade tokenization, dark-mode-friendly.

**Q:** Behavior for large files?
- A: Render in full (Recommended) — render any file in full regardless of size. No truncation, no streaming, no virtualization.

### deployment-runtime

**Q:** Process topology — single FastAPI or two processes?
- A: Single FastAPI (Recommended) — FastAPI serves the built React static assets at `/` and the JSON API at `/api`. One port, one process.

**Q:** Default port?
- A: Fixed 8765 (Recommended) — overridable via the `SPEC_DRIVEN_PORT` env var.

**Q:** Startup convention?
- A: make dev / make run (Recommended) — Makefile (or simple shell script) at `projects/spec_driven/` wraps uvicorn (and Vite in dev). README documents `make run` and `make dev`.

**Q:** How does the backend locate the repo root?
- A: Walk upward (Recommended) — backend walks parent directories from its own file until it finds a directory containing `CLAUDE.md` + `specs/` + `.claude/`. Caches the result.

### success-criteria

**Q:** What's the v1 dogfood demo scope?
- A: Specs + settings (Recommended) — user can browse all five stage subfolders of `Projects/development/spec_driven/` AND all three Claude Settings & Shared Context file kinds. Audit logs and project-output folders are NOT required in v1.

**Q:** Target browser?
- A: Latest Chrome (Recommended) — latest stable Chrome / Chromium-based browsers only. No IE, no mobile responsiveness guarantees.

**Q:** Validation layers?
- A: BDD + a few e2e (Recommended) — BDD scenarios drive the spec. Small Playwright/Cypress suite covers the dogfood happy path. Backend gets pytest unit + integration tests. (E2E framework narrowed in round 2 — see E2EFramework below.)

**Q:** Does v1 ship with a second project to validate multi-project navigation?
- A: No, just spec_driven (Recommended) — v1 ships with only `Projects/development/spec_driven/`. Multi-project rendering (sidebar grouping, navigation) is verified by unit/component tests using fixture data.

## Round 2

### functional-scope

**Q:** Section 1 listing — which exact files/folders feed the "Claude Settings & Shared Context" section? (Narrows the round-1 SettScope "Other" free text.)
- A: Fixed three globs (Recommended) — backend hardcodes exactly three sources: `CLAUDE.md` at repo root, `.claude/agents/*.md`, `.claude/skills/**/SKILL.md`. Nothing else. The round-1 free-text mention of "common things under specs folder" is explicitly NOT included in v1.

**Q:** Section 1 sidebar grouping — how should the three sources be visually arranged?
- A: Three subgroups (Recommended) — Section 1 sidebar shows three subgroups: 'CLAUDE.md' (single leaf), 'Agents' (one entry per `.claude/agents/*.md`, named after the file), 'Skills' (one entry per skill folder, named after the folder).

### success-criteria

**Q:** Which e2e framework for the v1 dogfood happy path? (Resolves the round-1 "Playwright/Cypress" ambiguity.)
- A: Playwright (Recommended) — v1 uses Playwright as the e2e framework.

**Q:** Concrete dogfood click-path the e2e suite must cover?
- A: Browse + render (Recommended) — open app, see spec_driven landing page, click each of the five stage subfolders, click one file in each, verify it renders. Plus open all three settings file kinds. No link-navigation assertions, no sidebar collapse-expand assertions in v1.

## Team consensus

- Round 1 marked **discovery-data-model**, **ux-navigation**, and **deployment-runtime** as clear. No further rounds needed for those.
- Round 2 follow-ups closed the open threads in **functional-scope** (SettScope free-text → fixed three globs) and **success-criteria** (e2e framework + dogfood click-path).
- Round 3 cleanliness check (sub-interviewers re-evaluating only the two round-2 categories) returned `{"clear": true}` for both.

All five categories marked clear by the interviewer team after **2 rounds of user-facing questions** plus a round-3 internal consensus check on the two revisited categories. The spec author has closed-form answers for every load-bearing decision.
