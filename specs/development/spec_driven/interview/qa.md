# Interview — spec_driven

Run: spec_driven-20260503-145859 (autonomous full-pipeline regen; intake + interview only — see § Halt note in the run's `events.jsonl`)

## Categories probed

- **functional-scope** — what the editor surfaces, what it edits, what's still in / out after follow-ups 001–006.
- **ux-interaction** — file-pane affordances, structured Q/A view, regenerate panel layout, autonomous-mode toggle, soft-wrap UX.
- **data-model** — the canonical project tree the backend walks, how follow-ups + promoted.md feed regen, how the new `agent_refs/project/` sibling is exposed.
- **edge-cases** — empty / oversized / corrupt artifacts, broken links, OS-specific traps (Windows + Git Bash), dev-server proxy mode under `make run-frontend`.

## Round 1 (autonomous, judgment-call answers)

Interview manager runs parent-direct shape A (direct generation, no per-category workers). Each answer is annotated `*(judgment call — chose X because Y)*` with the FR slice it informs.

### functional-scope

**Q:** Section 2 ("Projects") — which projects appear in the tree?
- A: All discovered (Recommended) — backend walks `specs/{type}/{name}/` for every type+name pair on disk; show all. `spec_driven` is just the first; `ai_video` etc. appear automatically when present.

*(pin-001 preserved verbatim from `interview/promoted.md` — answer ratified during interactive Round 1 in run `spec_driven-20260502-clean`. Binds FR-12 / FR-13.)*

**Q:** Which file types under the exposed tree are openable in the main pane?
- A *(judgment call — chose "markdown + YAML/JSON + JSONL + plain text" because the workflow's artifacts are exclusively text)*: `.md`, `.json`, `.yaml`, `.yml`, `.jsonl`, `.txt`. Image extensions (`.png` / `.jpg`) render as a placeholder. Disallowed extensions return 415. Binds FR-3, FR-9, NFR-9.

**Q:** Is the `agent_team` orchestrator a permanent agent file under `.claude/agents/`?
- A *(judgment call — chose "no, it's a skill" because the parent IS the manager per CLAUDE.md § Tool scoping)*: `agent_team` lives under `.claude/skills/agent_team/` as a top-level SKILL with `playbooks/{interview,research,validation}.md`. No separate manager subagent. `.claude/agents/` is reserved for future permanent subagents and is currently empty. Binds the parent-direct contract.

**Q:** Are deletes / uploads / create-new-file exposed by the editor?
- A *(judgment call — chose "no" because every artifact is created by the pipeline, not by hand)*: only `PUT /api/file` (modify existing), `POST /api/regen-prompt` (assemble), `POST /api/promote` / `DELETE /api/promote` (pinning). No DELETE on `/api/file`, no upload, no create-new-file — those would invite parallel state surfaces, the anti-pattern CLAUDE.md explicitly forbids. PATCH/DELETE on file → 405. Binds NFR-6, AC-12.

**Q:** Does the webapp show `.claude/agent_refs/project/` files (introduced by follow-up 005)?
- A *(judgment call — chose "yes, automatically via the existing recursive glob" because the EXPOSED_TREE already covers `.claude/agent_refs/**/*.md`)*: no webapp / tree-walker code change is needed; the new subfolder appears in the sidebar under `Claude Settings & Shared Context → .claude/agent_refs/project/`. Binds FR-2 (EXPOSED_TREE definition) and the contract in CLAUDE.md § Stage playbooks and reference docs.

### ux-interaction

**Q:** Markdown link resolution under the editor — relative vs absolute?
- A *(judgment call — chose "relative-only, broken links muted" because the muted-span pattern surfaces issues without breaking flow)*: relative links resolve against the current file's directory; absolute http(s) links open in a new tab; broken links render as muted spans (not anchors) with a `title` tooltip describing the cause. Making them real anchors invites accidental external nav. Binds FR-33, FR-34, FR-35.

**Q:** Structured Q/A view for `interview/qa.md` — flat markdown or color-block?
- A *(judgment call — chose "color-block with per-Q/A pencil edit" because spec-driven Q/A maps to a strict tree)*: rounds → categories → Q/A pairs render as discrete blocks; Q tinted blue, A tinted green; category badge in header. Each Q and each A has a ✎ inline edit pencil. Whole-file edit remains via the toolbar toggle. Binds FR-41a..d.

**Q:** Regenerate panel layout — single panel per stage, or master at project page?
- A *(judgment call — chose "both" because users alternate between "rerun this one stage" and "rerun the world")*: a per-stage collapsible `<details>` panel above any file under a stage subfolder, AND a master panel at `/project/{type}/{name}` that selects across stages. Same `localStorage` value drives the autonomous toggle on both. Binds FR-42, FR-43, FR-44.

**Q:** Assembled regen prompt — visible inline, or behind a `<details>` expander?
- A *(judgment call — chose "inline visible block with header bar Copy + Wrap toggle" per follow-up 002)*: after `Build prompt` succeeds, the prompt renders directly inside a bordered `regen-prompt-block`. Header bar carries title, "Wrap" toggle (default ON), and a prominent **Copy** button (label flips to "Copied!" for ~1.5s). One-click visible Copy is friendlier than a two-click expand-then-copy. Binds FR-42(f).

**Q:** Autonomous-mode toggle persistence?
- A *(judgment call — chose "localStorage, per-tab synced via storage events, default off" because accidental autonomous runs should not be the path of least resistance)*: persisted under `spec_driven.autonomous_mode.v1`. Default is **interactive**. Same value across per-stage and project-page panels. Binds FR-44.

**Q:** App chrome theme?
- A *(judgment call — chose "light only" per `agent_refs/project/development.md`)*: body / sidebar / toolbar / panels / buttons stay light regardless of OS `prefers-color-scheme`. `<pre>` blocks inside `.regen-prompt-block`, `.markdown-view pre`, `.code-view pre` keep their fixed dark palette as intentional carve-outs (validated for WCAG AA). No `@media (prefers-color-scheme: dark)` on chrome. Binds the cross-cutting development project rule.

### data-model

**Q:** Sidebar tree shape returned by `GET /api/tree` — flat list or recursive?
- A *(judgment call — chose "recursive with `children`" because run `spec_driven-20260502-clean` had a contract drift where the backend emitted `task_type.projects` / `project.stages` while the frontend walked `node.children`)*: top-level sections "Claude Settings & Shared Context" and "Projects". Each tree node has `{name, path, type, children: []}`. Frontend descends `node.children` uniformly. Per `agent_refs/validation/development.md` move 2 (consumer-walk). Binds FR-7, FR-8, AC-3.

**Q:** What does the regen-prompt assembler include?
- A *(judgment call — chose "intent + follow-up list + selected stages + every selected stage's promoted.md inline" because a regen prompt must be self-contained)*: `revised_prompt.md` (or raw if no revised), every `user_input/follow_ups/*.md` filename, the selected stages with their invocation hints + module list, and any non-empty `<stage>/promoted.md` inlined verbatim under "Pinned items (MUST survive regeneration)". A fresh Claude session can act on it without browsing other files. Binds FR-14c.

**Q:** Where do follow-ups land?
- A *(judgment call — chose "specs/{type}/{name}/user_input/follow_ups/NNN-{YYYYMMDD-HHmmss}-{slug}.md" per CLAUDE.md § Follow-up prompt handling)*: NNN is the zero-padded sequence; the timestamp + slug make the filename self-describing. `revised_prompt.md` is auto-regenerated = `raw_prompt.md` + every follow-up in numerical order. Binds the auto-regen rule + changelog protocol.

**Q:** How does `make run-frontend` (Vite at 5173) talk to the backend (8765)?
- A *(judgment call — chose "Vite proxy rewrites Origin to the bound backend origin" per follow-up 006 Option A)*: the proxy block in `vite.config.ts` for `/api`, `/file`, `/project` ships `target: http://127.0.0.1:8765`, `changeOrigin: true` (rewrites Host), AND a `configure(proxy => proxy.on('proxyReq', proxyReq => proxyReq.setHeader('origin', target)))` hook (rewrites Origin). The backend allow-list stays bound-port-only; the rewrite happens at the proxy boundary, not by widening backend trust. Binds FR-9 dev-server proxy contract.

### edge-cases

**Q:** Behavior on a file >1 MB read attempt?
- A *(judgment call — chose "413 with `kind: too_large`" per OWASP File Upload Cheat Sheet guidance)*: applies to both `GET /api/file` and `PUT /api/file`. Binds FR-3, FR-7, AC-10.

**Q:** Path traversal probes (`../etc/passwd`, `specs/development/spec_driven/CON.md`, ADS `…::$DATA`, 8.3 short names)?
- A *(judgment call — chose "single 404, no enumeration side-channel")*: every traversal / Windows-reserved-device / NTFS-ADS / POSIX-junction / case-mismatch probe collapses to a single `404` so a path-existence oracle isn't leaked. Binds FR-3, AC-1, SEC-* battery.

**Q:** What happens to a deep-link to `interview/qa.md` when the autonomous-mode answer regex fails to parse?
- A *(judgment call — chose "QaErrorBoundary as a real React class component, falls back to plain markdown render" per `agent_refs/validation/development.md` move 9)*: `try { return <QaView /> } catch` does NOT catch render-phase throws — that's why an Error Boundary class with `componentDidCatch` / `getDerivedStateFromError` is mandatory. Fallback shows markdown verbatim with a banner explaining parse failure. Binds FR-41 fallback + AC-25.

**Q:** Build-prompt under `make run-frontend` returns 403 — how is this caught next time?
- A *(judgment call — chose "test the proxied request shape directly + add a second e2e profile per `agent_refs/validation/development.md` moves 1, 11" per follow-up 006)*: SYS-16b boots both backend and Vite, asserts (i) raw `Origin: http://localhost:5173` direct-to-backend → 403 (proves rewrite is load-bearing), (ii) proxied flow → 200. Wiring the second Playwright `webServer` is a follow-on implementation task; the SYS-test text is the contract a future stage-5 strategy MUST honor. Binds AC-11 dev-server branch + the new severity rows in `agent_refs/validation/development.md`.

## Team consensus

All four categories marked clear after one autonomous round. No follow-up round needed; inputs (revised_prompt + 6 follow-ups + agent_refs) are tight. Binding map: every Q is annotated with the FR / NFR / AC / SEC slice it informs so a future interactive run can revise without re-deriving the rationale.
