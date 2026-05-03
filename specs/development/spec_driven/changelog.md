# Changelog — spec_driven

## Follow-up 009 — 2026-05-03 16:48:40
Source: user_input/follow_ups/009-20260503-164840-specs-section-clickable-nodes-and-markdown-pins.md
Summary: Four coupled UX fixes. (a) Sidebar second top-level section renamed `Projects` → `Specs` (user mental model; matches FR-15 layout shipped in 008). (b) Project nodes (`specs/{type}/{name}`) now navigate to `/project/{type}/{name}` on row click, opening the FR-32 master Regenerate panel — disclosure caret split into its own button so expansion stays available. (c) Stage nodes (`specs/{type}/{name}/{stage}` for the 5 canonical stages) navigate to a new `/stage/{type}/{name}/{stage}` route rendered by a new `StagePage` component, which mounts the existing `RegeneratePanel` in stage-scoped mode (`stageId={stage}`). (d) Two coupled promotion bugs fixed: (d1) `Reader.tsx::extractPinnedIds` regex was looking for `pin:X` but `promotions.py::_serialize` writes `<!-- pin source=… id=… -->` — replaced the regex with one that mirrors `_PIN_HEADER` + `_ATTR` so QA pin state actually hydrates from `promoted.md`; (d2) markdown `Renderer` extended with an optional `PinContext` and component overrides on `<p>` / `<li>` that detect a leading `<strong>` matching `^(FR|NFR|AC|SYS|OQ)-(\d+\w?)\.?$` and inject a 📌 button — closing FR-35 coverage for spec / validation / findings markdown (Q/A pinning in `QaView` is unchanged). `Reader` builds `pinContext` for stages in the 4-stage promote allowlist (`interview` excluded since `QaView` already owns it; the loader still hydrates `pinnedIds` for QA via the now-correct regex).

Auto-updated:
- specs/development/spec_driven/final_specs/spec.md — FR-3: `"Projects"` → `"Specs"` in the top-level-sections sentence. FR-15: same literal in the section-name sentence AND `Projects/{type}/{name}/` → `Specs/{type}/{name}/` in the subtree-shape sentence. No new FR / NFR / AC.
- projects/spec_driven/backend/libs/tree_walker.py — `_projects_section` returns `name: "Specs"` (was `"Projects"`); leading comment updated.
- projects/spec_driven/backend/tests/unit/test_tree_walker.py — `test_root_has_two_top_level_sections` and `test_tree_consumer_walk` assert against `"Specs"` (was `"Projects"`).
- projects/spec_driven/frontend/src/components/Home.tsx — `discoverProjects` finds the section by name `"Specs"`.
- projects/spec_driven/frontend/src/App.tsx — added `<Route path="/stage/:projectType/:projectName/:stage" element={<StagePage />} />` and the corresponding import.
- projects/spec_driven/frontend/src/components/StagePage.tsx — new file. Reads `useParams`, renders `<RegeneratePanel … stageId={stage} initiallyOpen />`. Includes a `STAGE_LABELS` map for the human-readable subtitle.
- projects/spec_driven/frontend/src/components/Sidebar.tsx — new `classifySpecPath()` that returns `"project"` / `"stage"` / `null` for a tree node's path; row-click and `Enter`/`Space` keyboard handlers prefer navigation when the path matches; the disclosure indicator (▾/▸) is now a `<button>` with its own click handler so users can still expand/collapse without leaving the destination page.
- projects/spec_driven/frontend/src/components/Reader.tsx — `extractPinnedIds` now uses the canonical `<!-- pin source=… id=… -->` shape (mirror of `promotions.py::_PIN_HEADER` + `_ATTR`); pin loading runs for the 4 promotable stages (was: interview only); added `onPinMarkdown` / `onUnpinMarkdown` that look up the paragraph body for an FR-NN-style item via `extractMarkdownItemBody` and call `POST /api/promote` / `DELETE /api/promote`; `pinContext` (a new `PinContext` value imported from `markdown/Renderer`) is wired through to `<Renderer>` for non-QA pinnable stages (`findings`, `final_specs`, `validation`).
- projects/spec_driven/frontend/src/markdown/renderer.tsx — added `PinContext` interface + `PinButton` + `extractPinId(children)`. `Renderer` accepts a new optional `pinContext` prop. Component overrides on `<p>` / `<li>` inject a `PinButton` next to any leading `<strong>` matching `^(FR|NFR|AC|SYS|OQ)-(\d+[a-z]?)\.?$`. Existing link-resolution behavior is unchanged.
- projects/spec_driven/frontend/src/styles.css — `.tree-disclosure` extended with button-reset rules (background / border / padding / cursor) since it's now a `<button>` not a `<span>`. New `.pin-toggle-md` rules style the markdown pin button (low-opacity by default, full opacity when hovered or pinned). New `.markdown-view [data-pin-id]` rule reserves `position: relative` for future absolute-positioning if the pin button needs to float.
- specs/development/spec_driven/user_input/revised_prompt.md — `Last regenerated` header bumped to 2026-05-03 16:48:40 with follow-up 009 noted; body unchanged (intent unchanged; FR-15 / FR-32 / FR-35 already specified the desired states).

No conflicts found in: interview/qa.md, findings/dossier.md, validation/* (the rename is purely cosmetic at the section header; no FR text outside FR-3 / FR-15 references "Projects" as a section), projects/spec_driven/backend/libs/{api.py, promotions.py, file_reader.py, file_writer.py} (promotions backend already supports the 4-stage allowlist; `_PIN_HEADER` / `_ATTR` were already correct — the bug was only in the frontend mirror), projects/spec_driven/frontend/src/components/{ProjectPage,RegeneratePanel,QaView,Editor,Breadcrumb,BrokenLink,ParseFallback}.tsx (untouched — `RegeneratePanel`'s `stageId` prop already drives both project-wide and stage-scoped rendering, so `StagePage` is a thin wrapper; `QaView` continues to own Q/A pinning unchanged), projects/spec_driven/README.md (target list unchanged; no Run-section changes).

## Follow-up 008 — 2026-05-03 16:36:26
Source: user_input/follow_ups/008-20260503-163626-sidebar-mirrors-specs-and-home-project-link.md
Summary: Two coupled UI fixes. (a) Sidebar "Projects" section drifted from FR-15 — it wrapped the entire `specs/` tree behind a literal `specs/` folder name AND walked each `projects/{name}/` as a sibling. Restructured `tree_walker._projects_section` so its children are the direct children of `specs/` (task-type at level 1, task-name at level 2, per-stage subfolders at level 3 — matching the on-disk hierarchy). Project-code output `projects/{name}/` no longer appears in the sidebar; it's still reachable through the file API (`is_inside` admits `projects/...`) and via direct deep-link URLs. (b) `/project/:projectType/:projectName` (FR-32) had no UI affordance — only typed URLs. `Home.tsx` now derives `{type, name}` pairs from the tree's "Projects" section and renders a per-project "Build regen prompt" link to that route.

Auto-updated:
- projects/spec_driven/backend/libs/tree_walker.py — `_projects_section` rewritten: walks `specs/` directly, drops literal `specs/` wrapper and the `projects/{name}/` parallel loop. Path strings remain canonical filesystem-relative (deep-links unaffected).
- projects/spec_driven/frontend/src/components/Home.tsx — added `discoverProjects(tree)` that yields `(task_type, task_name)` from the "Projects" section's first two child levels; renders an `<ul>` of `<Link to={"/project/{type}/{name}"}>` entries when at least one project is discovered, falls back to the prior "{N} top-level sections loaded" message otherwise.
- projects/spec_driven/frontend/src/styles.css — added `.home-projects`, `.home-project-list`, `.home-project-item` rules under the existing "Home" section. No theme/token additions; only existing CSS vars (`--border`).
- specs/development/spec_driven/user_input/revised_prompt.md — header `Last regenerated` bumped to 2026-05-03 16:36:26 with follow-up 008 noted; body unchanged (intent does not move; FR-15 / FR-32 already describe the desired state).

No conflicts found in: final_specs/spec.md (FR-15 already specifies `Projects/{type}/{name}/` shape; FR-32 already specifies the project-page route — implementation drifted, spec did not), interview/qa.md, findings/dossier.md, validation/* (existing structural assertions in `test_tree_walker.py` survive the visible-name change since paths are unchanged; SYS-20 / SYS-21 selector-mismatch issues predate this follow-up and are explicitly deferred), projects/spec_driven/backend/libs/exposed_tree.py (untouched — `project_dirs()` left in place even though no longer called; trimming is out of scope), projects/spec_driven/frontend/src/App.tsx (route already wired), projects/spec_driven/frontend/src/components/{Sidebar,RegeneratePanel,ProjectPage}.tsx (no changes needed — Sidebar's uniform `node.children` walk handles the new shape; ProjectPage / RegeneratePanel already work standalone).

## Follow-up 007 — 2026-05-03 16:10:01
Source: user_input/follow_ups/007-20260503-161001-makefile-host-port-flag-mismatch.md
Summary: `make run-backend` and `make run-prod` crashed with `main.py: error: unrecognized arguments: --host 127.0.0.1 --port 8765`. The Makefile passed CLI flags that `backend/main.py` never declared (host/port are hardcoded module-level constants per SEC-13 / NFR-7). Aligned the Makefile to the spec by stripping the flags and the now-orphaned `HOST` / `PORT` vars; `main.py` left untouched to keep the loopback bind a hardcoded boundary, not a CLI surface.

Auto-updated:
- projects/spec_driven/Makefile — removed `HOST`, `PORT` vars and the `--host`/`--port` arguments from the `run-backend` and `run-prod` recipes.
- specs/development/spec_driven/user_input/revised_prompt.md — header `Last regenerated` bumped to 2026-05-03 16:10:01 with follow-up 007 noted; body unchanged (intent does not move).

No conflicts found in: final_specs/spec.md (FR-39 lists target names + asserts loopback bind, says nothing about CLI flags), interview/qa.md, findings/dossier.md, validation/* (boot-smoke + Origin/Host suites already assert behavior at `127.0.0.1:8765` against the un-flagged invocation), projects/spec_driven/README.md (Run section describes target names only), projects/spec_driven/backend/main.py (intentionally untouched — SEC-13 invariant).

## Autonomous regen — 2026-05-03 14:58:59 (run `spec_driven-20260503-145859`)

Source: user pasted a full-pipeline `# EXECUTION MODE: AUTONOMOUS` regen prompt selecting all six stages.
Outcome: **full pipeline regenerated and validated.** An initial premature `pipeline.halted` after stage 2 was reversed at 15:00:00 (operator pushback — self-imposed halt, not a real bound trip per CLAUDE.md § Iteration bounds); stages 3–6 then ran in the same autonomous turn. Final `pipeline.completed` event emitted at 15:55:08.

Stages completed (read-zero contract honored on each):

| Stage | Deletions | Workers | Outputs | Validation |
|---|---:|---:|---|---|
| 1 — Intake | 0 (in-place rewrite) | 0 | `revised_prompt.md` Last-regenerated bumped; body unchanged | n/a |
| 2 — Interview | 1 (`qa.md`; `promoted.md` preserved) | 0 (parent-direct) | 4 categories, 16 judgment-call answers; **pin-001 verbatim** | n/a |
| 3 — Research | 5 (`angle-*.md` + `dossier.md`) | 4 researchers in parallel (real `WebSearch` + `WebFetch`) | 4 angles + parent-synthesized `dossier.md` (10 KB, 6 cross-cutting insights, 8 spec recommendations) | n/a |
| 4 — Spec | 1 (`spec.md`) | 0 (parent-direct) | 41 FRs, 16 NFRs, 29 ACs, 9 OQs (~20 KB) | n/a |
| 5 — Validation strategy | 8 (every `validation/*.md` except `promoted.md`) | 7 level-specialists in parallel | 29 ACs, 15 BDD Features (~620 lines), 131 unit cases, 27 SYS scenarios incl. SYS-16b, 22 SEC probes (CWE/CVE-cited), 7 PERF budgets, 25 A11Y checks; parent-synthesized `strategy.md` | n/a |
| 6 — Execution + streaming validation | 65 (entire `projects/spec_driven/` source tree; `node_modules` preserved) | 6 implementation workers in parallel (backend-core, backend-tests, frontend-core, frontend-tests, e2e-config, project-meta) | 67 source files rebuilt; backend libs (12), backend tests (8), frontend src (~25 incl. 11 components), frontend tests (7), Playwright config + 27-scenario suite, Makefile, README, .gitignore | **211 passed / 1 skipped** (pytest), **56 passed** (vitest), `tsc -b` clean, `vite build` clean to `backend/static/`, boot smoke pass (8 routes wired, `/api/tree` recursive `children`, regen-prompt INTERACTIVE + AUTONOMOUS headers verbatim, loopback-alias 200, pre-rewrite-shape 403 — move-11 regression test passes, PATCH 405 with `Allow: GET, PUT`) |

Subagent total: **17** (4 research + 7 validation level-specialists + 6 implementation). Audit pairs at `.audit/adhoc_agents/2026-05-03/spec_driven-20260503-145859/spawns/`.

Read-zero contract preserved by:
- Every stage's prior outputs deleted before regenerate (real `rm`-equivalent, not logical "treat as missing"). 80 files total deleted.
- All `<stage>/promoted.md` files preserved (interview only had pin-001; findings/final_specs/validation promoted.md were empty/non-existent).
- Pin-001 verbatim re-inclusion verified in regenerated `qa.md` (Round 1 / functional-scope).

Pending manual verification (per `agent_refs/validation/general.md` principle 4 + accessibility A11Y-17):
- `make e2e` — Playwright drivers not invoked in this autonomous turn; the 27-scenario suite is wired (incl. SYS-16b dev-server-proxy parity contract per development.md move 11).
- A11Y manual walkthrough — visual hierarchy of QaView Q/A tints, focus-visibility under real keyboard, motion/animation perceptibility, NVDA screen-reader sanity, forced-colors mode, 200% zoom, prefers-reduced-motion.

Audit: `.audit/adhoc_agents/2026-05-03/spec_driven-20260503-145859/{events.jsonl (124 events), spawns/ (17 spawn audit pairs)}`.

## Follow-up 006 — 2026-05-03 14:27:03
Source: user_input/follow_ups/006-20260503-142703-vite-proxy-origin-rewrite-and-validation-gap-prevention.md
Summary: User reported that "Build prompt" still 403'd when the SPA was driven via `make run-frontend` (Vite at 5173 → backend at 8765). Two coupled fixes: (a) Option A — Vite proxy rewrites the `Origin` header to `http://127.0.0.1:8765` so the backend's strict-Origin gate (untouched) sees a same-shape request in both runtime modes; (b) capture the class of failure as institutional memory in `agent_refs/validation/{general.md, development.md}` so the next development task can't drift the same way.

Cross-cutting (NOT under this project's `specs/`):
- `.claude/agent_refs/validation/general.md` — added Principle 6.5 ("Question every 'v1 out of scope' carve-out at stage 5") and Principle 7 ("Validate the post-mutation shape when a request crosses a header-mutating layer"). Renumbered the prior pinned-items principle to 9. Both new principles cite run `spec_driven-006` as the lesson source.
- `.claude/agent_refs/validation/development.md` — added Required moves 11 (multi-mode runtime feature parity → one e2e profile per spec-advertised runtime mode) and 12 (cross-origin / cross-port middleware tests must cover both pre-rewrite and post-rewrite shapes). Severity table extended with three new rows: missing-e2e-profile-for-advertised-mode → `blocker`; Origin/Host middleware with no pre-proxy-rewrite unit test → `blocker`; spec carve-out conflicts with another spec section → `critical` at stage 5.

Auto-updated:
- `specs/development/spec_driven/user_input/revised_prompt.md` — Last-regenerated line bumped; "Cross-cutting constraints" loopback bullet extended with the dev-server proxy contract (Vite rewrites `Origin`/`Host`; backend allow-list is NOT widened to 5173).
- `specs/development/spec_driven/final_specs/spec.md` — FR-9 amended: appended one sentence describing the Vite proxy contract under `make run-frontend` (rewrite `Origin` to `http://127.0.0.1:8765`, `changeOrigin: true` rewrites `Host`, backend gate stays bound-port-only). Removed the implicit "out of scope for v1" carve-out for the cross-port case.
- `specs/development/spec_driven/validation/acceptance_criteria.md` — AC-11 extended with two new branches: (i) raw browser shape `Origin: http://localhost:5173` direct-to-backend → 403 (proves the proxy rewrite is load-bearing); (ii) the proxied flow under `make run-frontend` → 200.
- `specs/development/spec_driven/validation/system_tests.md` — new SYS-16b scenario: boots both `python backend/main.py` and `npm run dev`, drives Build-prompt + every state-changing route through the dev-server, asserts proxied 200 + raw-shape 403. Notes that the second Playwright `webServer`/project entry is a follow-on implementation task; the SYS text is the contract that future stage-5 strategies must respect.
- `specs/development/spec_driven/validation/strategy.md` — added SYS-16b under the system-tests bullet list with a forward reference to `agent_refs/validation/development.md` move 11 (`blocker`-severity stage-5 requirement).
- `projects/spec_driven/frontend/vite.config.ts` — proxy entries for `/api`, `/file`, `/project` upgraded from bare target strings to a shared `ProxyOptions` object with `changeOrigin: true` and a `configure(proxy => proxy.on('proxyReq', proxyReq => proxyReq.setHeader('origin', target)))` hook. Imported `ProxyOptions` from `vite` for type inference; `tsc -b` clean (exit 0).

No conflicts found in:
- `specs/development/spec_driven/interview/qa.md` (no Q/A about Origin / Vite proxy / dev-server contract).
- `specs/development/spec_driven/findings/` (no angle covers reverse-proxy header-rewrite patterns; conclusions about CSRF / sandbox unchanged).
- `specs/development/spec_driven/validation/{bdd_scenarios,unit_tests,security,performance,accessibility}.md` (the existing Origin/Host scenarios still hold; the new dev-server-proxy case is captured at the AC + SYS layer where it belongs; no a11y/performance/security shape changes).
- `projects/spec_driven/backend/libs/api_security.py` and `projects/spec_driven/backend/tests/unit/test_api.py` (the backend gate is unchanged by Option A — the rewrite happens at the Vite proxy, not at the backend allow-list. Existing tests still pass).
- `projects/spec_driven/frontend/playwright.config.ts` (the second `webServer`/project entry that boots `make run-frontend` is acknowledged as a follow-on implementation task; current playwright still boots single-process mode, but the SYS-16b contract is now in the spec for the next stage-5 run to enforce).

## Follow-up 005 — 2026-05-03 14:09:17
Source: user_input/follow_ups/005-20260503-140917-light-theme-rule-into-shared-refs.md
Summary: Relocate the light-theme rule (added to `CLAUDE.md → Project rules` by follow-up 004) into a new project-scoped refs hierarchy `.claude/agent_refs/project/{general.md, <task_type>.md}` that mirrors the existing per-stage `agent_refs/` layout. The rule's substance and carve-outs are unchanged; only its storage location moves. Future cross-cutting project-output rules accumulate in the new hierarchy instead of inflating `CLAUDE.md`.

Cross-cutting (NOT under this project's `specs/`):
- `.claude/agent_refs/project/general.md` — new file. Documents the project-scoped-refs contract (loaded at every coordinated stage and every stage-6 work unit alongside the existing stage-scoped refs), the precedence rules (per-task-type wins over `general.md`; project spec wins over project-scoped refs for that one project), and the surgical-update protocol. "Common principles" section intentionally empty in v1 — no rule yet spans `development` AND `ai_video`.
- `.claude/agent_refs/project/development.md` — new file. Hosts the light-theme rule verbatim (light app chrome, `color-scheme: light;` only, no `prefers-color-scheme: dark` on chrome, dark `<pre>` carve-outs allowed, `blocker`-severity at validation if violated). Cites follow-up 004 / 005 of `spec_driven` as the origin.
- `CLAUDE.md` — `## Stage playbooks and reference docs` section extended to describe the new `agent_refs/project/` sibling: required pre-reading at every coordinated stage and stage-6 work unit, recorded in the same `pre_reading_consulted` array, automatically exposed by the existing `EXPOSED_TREE` glob (`.claude/agent_refs/**/*.md`). The "UI theme: light only" bullet under `## Project rules (under projects/)` is removed and replaced by a one-line forward pointer to the new ref location.

Auto-updated:
- `specs/development/spec_driven/user_input/revised_prompt.md` — bumped Last-regenerated line; updated the "Light-theme app chrome" bullet under "Cross-cutting constraints" to reference `.claude/agent_refs/project/development.md` instead of `CLAUDE.md → Project rules`. Substance unchanged.

No conflicts found in:
- `specs/development/spec_driven/interview/qa.md` (no Q/A about theme storage location).
- `specs/development/spec_driven/findings/` (no angle covers ref-folder layout; no theme-source-of-truth mention).
- `specs/development/spec_driven/final_specs/spec.md` (no FR/NFR/AC pinned the rule's storage location — the spec only says "light app chrome"; that wording is location-agnostic).
- `specs/development/spec_driven/validation/{strategy,acceptance_criteria,bdd_scenarios,unit_tests,system_tests,security,performance,accessibility}.md` (the rule's substance is unchanged; A11Y-11 dark-`<pre>`-carve-out preserved; no validation language references `CLAUDE.md → Project rules → UI theme` directly).
- `projects/spec_driven/{backend,frontend}/` (the styles.css and api_security.py changes from follow-up 004 are unaffected by the relocation; no code path reads the rule's location).
- `specs/development/spec_driven/user_input/follow_ups/004-20260503-133625-light-theme-and-loopback-403-fix.md` (left as the historical record; its "source of truth is `CLAUDE.md`" prose was true at write time and is superseded by this follow-up 005, which the reader sees by reading both in order).

## Follow-up 004 — 2026-05-03 13:36:25
Source: user_input/follow_ups/004-20260503-133625-light-theme-and-loopback-403-fix.md
Summary: (a) Apply the new repo-wide `CLAUDE.md` "UI theme: light only" rule to spec_driven by removing every `@media (prefers-color-scheme: dark)` block on app chrome and switching `:root { color-scheme }` from `light dark` to `light`. (b) Fix the `403 forbidden` users hit on `POST /api/regen-prompt` (and the other guarded mutations) when the SPA is opened at `http://localhost:8765/` instead of `http://127.0.0.1:8765/` — the Origin/Host middleware now uses a loopback-equivalence allow-list (`{127.0.0.1, localhost}` at the bound port).

Cross-cutting (NOT under this project's `specs/`):
- `CLAUDE.md` — added a new "UI theme: light only" bullet under `## Project rules (under projects/)`. This is the source of truth for the light-theme rule; future webapp projects inherit it.

Auto-updated:
- `specs/development/spec_driven/user_input/revised_prompt.md` — bumped Last-regenerated line; added two bullets under "Cross-cutting constraints" referencing the loopback-alias fix and the light-theme application of the new CLAUDE.md rule.
- `specs/development/spec_driven/final_specs/spec.md` — FR-9 rewritten to spell out the loopback-equivalence allow-list (`{http://127.0.0.1:<port>, http://localhost:<port>}` for `Origin`; `{127.0.0.1:<port>, localhost:<port>}` for `Host`); foreign domains and IPv6 literals still 403.
- `specs/development/spec_driven/validation/acceptance_criteria.md` — AC-11 extended with two new branches: `Origin/Host = localhost:8765` → 200 (the previously-uncovered realistic case), and `example.com:8765` at the bound port → 403 (negative confirmation that the allow-list is bounded).
- `projects/spec_driven/backend/libs/api_security.py` — added `LOOPBACK_HOST_LITERALS`, `BoundOrigin.origin_allow_list()` / `host_allow_list()`, and switched the middleware to membership tests against the precomputed allow-sets.
- `projects/spec_driven/backend/tests/unit/test_api.py` — added `test_put_with_localhost_origin_succeeds` and `test_post_regen_prompt_with_localhost_origin_succeeds` (regression for the user-reported "Build prompt → forbidden" path).
- `projects/spec_driven/frontend/src/styles.css` — removed every `@media (prefers-color-scheme: dark)` block on `body`, `aside.sidebar`, `.toolbar`, `.markdown-view`, `.qa-view`, `.regen-panel`, `button`; flipped `:root { color-scheme }` to `light`. Dark `<pre>` palette inside `.regen-prompt-block` / `.markdown-view pre` / `.code-view pre` preserved per NFR-16 / A11Y-11.

No conflicts found in:
- `specs/development/spec_driven/interview/qa.md` (no Q/A about Origin handling or theme).
- `specs/development/spec_driven/findings/` (no angle covers Origin allow-list shape; angle-copypaste-prompt-ux's "theme" mention refers to syntax-highlighting themes, unaffected).
- `specs/development/spec_driven/validation/bdd_scenarios.md` ("Cross-origin save attempt is rejected" still holds; no scenario asserted exact-127.0.0.1 exclusivity, so no contradiction).
- `specs/development/spec_driven/validation/system_tests.md` (SYS-16 wording covers the hostile case; the new pass case is captured at the AC level).
- `specs/development/spec_driven/validation/security.md` (binary-byte issue noted on read; no surgical edit attempted — the AC-level allow-list extension covers the contract).
- `specs/development/spec_driven/validation/accessibility.md` (A11Y-11 on the dark code-block theme is unaffected; the light-theme rule explicitly preserves it).

## Follow-up 003 — 2026-05-03 13:36:25
Source: user_input/follow_ups/003-20260503-133625-make-run-backend-frontend.md
Summary: Split the dev-server story in the `Makefile` into `make run-backend` (FastAPI on 127.0.0.1:8765) and `make run-frontend` (Vite on 127.0.0.1:5173); preserve `make run` as a backend-only alias so AC-29 / SYS-17 stay literal.

Auto-updated:
- `specs/development/spec_driven/user_input/revised_prompt.md` — bumped Last-regenerated line and added a "Dev workflow" bullet under Stack noting the run-backend / run-frontend split.
- `specs/development/spec_driven/final_specs/spec.md` — FR-39 target list extended with `run-backend` and `run-frontend`; `run` re-described as a backend-only alias.
- `projects/spec_driven/Makefile` — added `run-backend` and `run-frontend` targets; `run` now depends on `run-backend`; `.PHONY` and the `help` echo updated.
- `projects/spec_driven/README.md` — Run section gains a "backend + frontend in two terminals" subsection naming both new targets.

No conflicts found in:
- `specs/development/spec_driven/interview/qa.md` (no Q/A about the Makefile dev-server shape).
- `specs/development/spec_driven/findings/` (no angle covers Makefile target layout).
- `specs/development/spec_driven/validation/acceptance_criteria.md` (AC-28 / AC-29 still spell `make run-prod` / `make run` literally; both keep working — `run` is now an alias for `run-backend` and `run-prod` is unchanged).
- `specs/development/spec_driven/validation/bdd_scenarios.md` (`make run-prod` and `make run` scenarios at lines 513 / 528 still hold).
- `specs/development/spec_driven/validation/system_tests.md` (SYS-1 boot smoke + SYS-17 localhost bind both invoke `make run-prod` / `make run` literally; both still resolve as before).
- `specs/development/spec_driven/validation/strategy.md` (no language touched — the new dev-only targets do not introduce a new validation gate).

## Follow-up 001 — 2026-05-02 09:58:22
Source: user_input/follow_ups/001-20260502-095822-editable-webapp.md
Summary: Drop readonly constraint. Editable in place for every file, structured colored Q/A view for `interview/qa.md`, per-stage and per-project regen-prompt panels with autonomous-mode toggle, autonomous-mode contract documented in `CLAUDE.md`.

Auto-updated:
- `specs/development/spec_driven/user_input/revised_prompt.md` — full regenerate (raw + 001) per the auto-regen rule.
- `specs/development/spec_driven/interview/qa.md` — round-1 functional-scope answer about "no editing/etc" rewritten to confirm editing is now in scope and call out 001 as the source.
- `specs/development/spec_driven/final_specs/spec.md` — Goal restated as viewer/editor; "Out of scope" rewritten (editing struck, deletes/uploads/diff still out, copy-paste regen explained); new FR-14a/14b/14c (backend write + stages + regen-prompt endpoints); new FR-40..FR-44 (frontend Edit toggle, structured Q/A view, per-stage and project-page Regenerate panels, autonomous-mode persistence); NFR-6 reworded to permit the new endpoints with the same sandbox.
- `specs/development/spec_driven/findings/dossier.md` — appended "Addendum (follow-up 001)" calling out atomic write, server-side prompt assembly, and the autonomous-mode-as-CLAUDE.md-contract decisions.
- `specs/development/spec_driven/validation/acceptance_criteria.md` — AC-23 rewritten so PUT/POST hit the sanctioned endpoints and only PATCH/DELETE/upload return 405.
- `specs/development/spec_driven/validation/security.md` — SEC-10 expected-behavior block rewritten for the new mutation surface; pass criterion updated to enforce the three-route, three-verb shape.
- `specs/development/spec_driven/validation/system_tests.md` — SYS-10 rewritten to round-trip a scratch file via PUT, exercise the regen-prompt endpoint, and re-confirm PATCH/DELETE/upload remain 405.
- `specs/development/spec_driven/validation/unit_tests.md` — 8.11 rewritten so the routing-surface unit covers PUT-200 / POST-regen-200 / PATCH-405 / DELETE-405.
- `projects/spec_driven/backend/libs/api.py` — added `PUT /api/file`, `GET /api/stages`, `POST /api/regen-prompt`.
- `projects/spec_driven/backend/libs/file_writer.py` — new module: atomic temp+rename write, same sandbox/extension/size/symlink rules as the reader.
- `projects/spec_driven/backend/libs/regen_prompt.py` — new module: canonical six-stage definition + prompt builder (inlines current `revised_prompt.md` and `follow_ups/*.md`).
- `projects/spec_driven/frontend/src/api.ts` — added `saveFile`, `fetchStages`, `buildRegenPrompt` and their types.
- `projects/spec_driven/frontend/src/components/Editor.tsx` — new file-level editor (Save/Discard/Close, Ctrl+S, dirty indicator).
- `projects/spec_driven/frontend/src/components/Reader.tsx` — wired Edit toggle, structured Q/A view dispatch, Regenerate panel hook (panel + Q/A view files arrive in subsequent commits per the in-progress task list).

Pending follow-on edits not auto-applied:
- `CLAUDE.md` — needs the new `## Regeneration prompts & autonomous mode` section (next on the in-progress task list, will be done in this same session).
- The frontend pieces still in flight: `QaView.tsx`, `RegeneratePanel.tsx`, project parent route, CSS for editor/Q-A blocks/regen panel. Tracked under tasks #3–#5; the changelog will not get a second entry for these because they belong to the same follow-up 001.

No conflicts found in:
- `specs/development/spec_driven/findings/angle-prior-art-readonly-viewers.md`
- `specs/development/spec_driven/findings/angle-two-pane-navigator-reader-ux.md`
- `specs/development/spec_driven/findings/angle-markdown-link-resolution-patterns.md`
- `specs/development/spec_driven/findings/angle-filesystem-readonly-viewer-risks.md`
  (these are historical research outputs; their findings still apply to the editable scope and the dossier addendum captures the deltas)
- `specs/development/spec_driven/validation/strategy.md`
- `specs/development/spec_driven/validation/bdd_scenarios.md`
- `specs/development/spec_driven/validation/accessibility.md`
- `specs/development/spec_driven/validation/performance.md`

## Autonomous regen — 2026-05-02 (run spec_driven-20260502-autoregen)
Source: user invoked the full-pipeline autonomous regen prompt (EXECUTION MODE: AUTONOMOUS, all six stages selected).
Summary: Re-ran every stage. Stage 1 was a no-op (revised_prompt already canonical, only the timestamp line was bumped). Stages 2–5 received targeted updates rather than full rewrites — preserving prior user-facing Q&A and research, and adding new content for the two follow-up-001 areas that prior runs only addended (in-place markdown editor UX; autonomous-mode header / copy-paste regen pattern). Stage 6 implemented the new spec language.

Auto-updated:
- `specs/development/spec_driven/user_input/revised_prompt.md` — bumped "Last regenerated" line to mark this as an autonomous full-pipeline regen.
- `specs/development/spec_driven/interview/qa.md` — added Round 3 (autonomous, follow-up-001 categories) with judgment-call answers for editing-ux, qa-structured-view, regen-panel, and autonomous-mode. Each answer is annotated `*(judgment call — chose X because Y)*` and bound to the FR/CLAUDE.md slice it informs. Rounds 1–2 (real user-facing Q&A) preserved verbatim.
- `specs/development/spec_driven/findings/angle-markdown-editor-ux.md` — new angle file (researched via WebSearch + WebFetch by a subagent: GitHub web editor, Obsidian, MkDocs Material, GitBook, Notion, VS Code Web). 8 evidence-backed recommendations.
- `specs/development/spec_driven/findings/angle-autonomous-mode-and-copypaste-regen.md` — new angle file (researched via WebSearch + WebFetch: Claude Code plan mode, OpenAI Model Spec, Cursor rules, Aider, AGENTS.md/Codex, Continue.dev, Spec Kit, JetBrains Junie). 8 recommendations.
- `specs/development/spec_driven/findings/dossier.md` — angle list updated to 6; added 4 new cross-cutting insights (editor and file-server must not trust each other; header-based mode contracts non-standard; editor save and pipeline regen are the same mutation shape; etc.); added recommendations 17–24 (dirty dot, stay-in-editor, persistent inline error banner, literal header + MUST NOT pairing, CLAUDE.md backing, no Jinja in v1, section breakdown beside Copy, warn-don't-truncate). Addendum reworked to point at the two new angle files.
- `specs/development/spec_driven/final_specs/spec.md` — Run id bumped to autoregen. FR-14c extended with the verbatim imperative line under autonomous mode AND the warn-don't-truncate size policy (50 KB warn / 1 MB hard ceiling). FR-40c extended with dirty-dot indicator + deep-equality dirty computation. FR-40e extended with persistent inline banner. FR-42 extended with the section-breakdown line (FR-42d) and the size-warning banner (FR-42e). FR-43 references the same. FR-44 documents the cross-tab `storage` event mechanism. New OQ-8/9/10.
- `specs/development/spec_driven/validation/strategy.md` — Run id bumped; FR/AC counts updated.
- `specs/development/spec_driven/validation/acceptance_criteria.md` — Run id bumped. New AC-24 (dirty dot), AC-25 (persistent banner), AC-26 (size policy warn-don't-truncate), AC-27 (breakdown line + warning banner).
- `specs/development/spec_driven/validation/bdd_scenarios.md` — Run id bumped. New Features: Editor dirty-dot + persistent error banner; Regen-prompt size policy (Scenario Outline with three Examples rows); Regen panel section breakdown.
- `specs/development/spec_driven/validation/unit_tests.md` — Run id bumped. New Group 11 (regen-prompt size policy + section breakdown — 6 cases) and Group 12 (editor dirty-state + persistent error banner — 4 cases).
- `specs/development/spec_driven/validation/system_tests.md` — New SYS-21 (warn-don't-truncate end-to-end), SYS-22 (editor dirty-dot + banner Playwright round-trip).
- `projects/spec_driven/backend/libs/regen_prompt.py` — new `RegenPromptResult` dataclass + `build_regen_prompt_result` wrapper; 50 KB warn / 1 MB hard ceiling enforcement.
- `projects/spec_driven/backend/libs/api.py` — `POST /api/regen-prompt` now returns `{prompt, warning, selected_stages_count, follow_ups_count, autonomous, bytes}` and a 413 on hard-ceiling overflow.
- `projects/spec_driven/frontend/src/api.ts` — `buildRegenPrompt` now returns `RegenPromptResponse` (not raw string); error path threads through structured error keys.
- `projects/spec_driven/frontend/src/components/RegeneratePanel.tsx` — added section breakdown line beside Copy button; warning banner when API returns a `warning` field; build-error banner.
- `projects/spec_driven/frontend/src/components/Editor.tsx` — separated `lastSavedText` from `initialText` (deep equality dirty); added filled-circle dirty-dot in toolbar; converted save error from in-toolbar text to a persistent inline banner above the textarea.
- `projects/spec_driven/frontend/src/styles.css` — new classes for `.editor-dirty-dot`, `.editor-error-banner`, `.regen-summary-line`, `.regen-breakdown`, `.regen-warning`, `.regen-error`.

No conflicts found in:
- `.claude/agents/*.md` (manager contracts unchanged)
- `CLAUDE.md` autonomous-mode section (already byte-for-byte aligned with the new FR-14c imperative line)
- `projects/spec_driven/backend/libs/{exposed_tree,file_reader,file_writer,repo_root,safe_resolve,tree_walker}.py` (unchanged)
- `projects/spec_driven/frontend/src/components/{QaView,Sidebar,Reader,Breadcrumb,RefreshButton,BrokenLink,ProjectPage}.tsx` (the new dirty-dot/breakdown logic lives in Editor.tsx and RegeneratePanel.tsx only)
- `specs/development/spec_driven/validation/{security,performance,accessibility}.md` (no behavioral changes to the surfaces they cover; the new editor banner is a string change inside an already-asserted `<div role="alert">`).

## Clean-state autonomous regen — 2026-05-02 (run spec_driven-20260502-clean)
Source: user clarified the regeneration contract — "regenerate means regenerate from a clean state, which means remove all previous files and caches" — and ran the full-pipeline autonomous regen under that rule.
Summary: All stage 2-5 spec artifacts and the entire `projects/spec_driven/` folder were deleted on disk, then every artifact was regenerated from scratch reading ONLY the inputs (`user_input/*`, prior stages' new outputs, `CLAUDE.md`, `.claude/agents/*`). No prior file content carried forward.

Hardening before the run (the contract addition):
- `CLAUDE.md` — added `### Regeneration semantics: read-zero from prior outputs` subsection under `## Regeneration prompts & autonomous mode`. Per-stage delete-then-regenerate table; explicit prohibition on surgical edits during regeneration; audit-event contract (`regen.delete.planned` / `regen.delete.completed` / `regen.write.completed`).
- `projects/spec_driven/backend/libs/regen_prompt.py` — added the read-zero contract paragraph to the assembled prompt's `### Constraints` section, plus the audit-event guidance, so every future copy-paste prompt carries the rule.

Files deleted before regen (real `rm -rf`, not logical):
- `specs/development/spec_driven/{interview,findings,final_specs,validation}/` (all 17 files).
- `projects/spec_driven/` (45+ files including backend Python, frontend TS/CSS, tests, package-lock, node_modules, dist, .vite cache). Empty `frontend/` directory entry persisted due to an IDE file-handle lock; all CONTENT was deleted.

Files regenerated:
- `specs/development/spec_driven/user_input/revised_prompt.md` — timestamp bumped (intake stage has no prior outputs to delete; revised_prompt is rewritten from raw + follow-ups in place).
- `specs/development/spec_driven/interview/qa.md` — clean-slate Round 1 with judgment-call answers across 7 probe categories under autonomous mode.
- `specs/development/spec_driven/findings/{dossier.md, angle-prior-art-readonly-viewers.md, angle-two-pane-navigator-reader-ux.md, angle-markdown-link-resolution-patterns.md, angle-filesystem-readonly-viewer-risks.md, angle-markdown-editor-ux.md, angle-autonomous-mode-and-copypaste-regen.md}` — six fresh research angles produced by parallel researcher subagents using real WebSearch + WebFetch, ~100 cited sources total.
- `specs/development/spec_driven/final_specs/spec.md` — 44 FRs, 16 NFRs, 27 ACs, 9 OQs.
- `specs/development/spec_driven/validation/{strategy.md, acceptance_criteria.md, bdd_scenarios.md, unit_tests.md, system_tests.md, security.md, performance.md, accessibility.md}` — 303 testable items total (27 AC + 70 BDD + 129 unit + 24 system + 8 perf + 20 sec + 25 a11y).
- `projects/spec_driven/{Makefile, README.md, backend/**, frontend/**}` — full FastAPI + React app rebuilt from the spec by two parallel implementation subagents (backend 25 files / ~1475 LOC, frontend 23 files / 11 components).

Validation outcomes:
- One blocker raised by runtime validation (extension-vs-EXPOSED_TREE check ordering on `findings/diagram.png` — AC-8 expected 415 but the implementation returned 404). Fixed by separating structural-membership from extension-whitelist enforcement: `is_inside` no longer couples extension into the specs/ glob, file_reader still does the 415 extension check after membership. Three files revised; all tests green after.
- Backend pytest: **50 passed, 2 skipped** (2 Windows-symlink + os.replace-PermissionError tests skip on Windows).
- Frontend `tsc -b`: **exit 0** (strict mode, noUnused* clean).
- Frontend `vite build`: produces `dist/` bundle.
- Smoke test: `python main.py` boots; `GET /api/tree` returns 200 with the development task type and 3 agents; `GET /api/file?path=specs/development/spec_driven/final_specs/spec.md` returns 200 with the new spec content; `POST /api/regen-prompt {autonomous: true}` emits the literal `# EXECUTION MODE: AUTONOMOUS` header, the verbatim imperative line, AND the read-zero contract language in the constraints section.
- Backend deps installed via repo `.venv` (`fastapi`, `uvicorn[standard]`, `pydantic`, `pytest`, `httpx`).
- Frontend deps installed via `npm install` (managed by the impl-frontend subagent).

Audit:
- `.audit/adhoc_agents/2026-05-02/spec_driven-20260502-clean/events.jsonl` (full event stream including delete/spawn/write/validation events).
- `.audit/adhoc_agents/2026-05-02/spec_driven-20260502-clean/spawns/` (8 spawn audit pairs: 6 researchers + 5 validation level specialists + 2 implementation builders).

## Follow-up 002 — 2026-05-03 02:54:50
Source: user_input/follow_ups/002-20260503-025450-friendly-regen-copy-ui.md
Summary: Make the assembled regen prompt friendly to read and easy to copy. After Build prompt, the prompt renders inline inside a bordered block (no inner `<details>`) with a header bar carrying the title, a "Wrap" soft-wrap toggle (default ON), and a prominent **Copy** button. The duplicate copy button in the actions row is removed; the section-breakdown line stays beside "Build prompt".

Auto-updated:
- `specs/development/spec_driven/user_input/revised_prompt.md` — bumped "Last regenerated" line; rewrote the per-stage Regenerate panel bullet under "Regeneration tooling" to describe the inline prompt block + header-bar Copy + soft-wrap toggle.
- `specs/development/spec_driven/final_specs/spec.md` — User journey #10 rewritten to drop the inner `<details>` opening step and call out the header-bar Copy + soft-wrap toggle. FR-42(d) clarified that the breakdown line lives beside the "Build prompt" button. FR-42(e) clarified that the warning banner renders above the prompt block. FR-42(f) rewritten end-to-end: bordered `regen-prompt-block` with header bar (title + Wrap toggle + prominent Copy), `<pre>` defaulting to soft-wrap, `aria-live="polite"` on the Copy button, fixed min-width to prevent label-flip layout shift.
- `specs/development/spec_driven/validation/acceptance_criteria.md` — AC-22 "And on success the assembled prompt is rendered…" line rewritten to match the new block + header bar layout, and the breakdown-line line clarified to live in the actions row beside "Build prompt".
- `specs/development/spec_driven/validation/bdd_scenarios.md` — Feature "Build per-stage regen prompt": scenario "Build a prompt for the Findings stage" rewritten so the assembled-prompt-rendering line names the bordered `regen-prompt-block`, header bar, "Wrap" toggle, and **Copy** button. Scenario "Above 1 MB the endpoint returns 413" updated so the failure path asserts `regen-prompt-block` is NOT rendered. Scenario "Copy-to-clipboard flips its label briefly" renamed to "Copy flips its label briefly" and rewritten to drive the header-bar **Copy** button. New scenario "Soft-wrap toggle controls prompt-body wrapping" added — covers default-ON wrap, toggling-off → horizontal-scroll behavior, and the no-localStorage-persistence rule.
- `specs/development/spec_driven/validation/system_tests.md` — SYS-23 large-case assertion #3 wording adjusted from "no prompt is opened in `<details>`" → "the `regen-prompt-block` is not rendered". SYS-24 step 5 rewritten so the inspector clicks the header-bar **Copy** button (or reads the `<pre>` directly) instead of expanding a `<details>`.
- `projects/spec_driven/frontend/src/components/RegeneratePanel.tsx` — replaced the inner `<details>"View assembled prompt"</details>` with an always-visible `regen-prompt-block`. Added `softWrap` state (default true), header bar (title + Wrap checkbox + prominent Copy button), and the `regen-prompt-pre--wrap` modifier class. Removed the duplicate "Copy to clipboard" button from `regen-actions`; the row now keeps "Build prompt" + the section-breakdown summary span.
- `projects/spec_driven/frontend/src/styles.css` — new classes `.regen-prompt-block`, `.regen-prompt-header`, `.regen-prompt-title`, `.regen-wrap-toggle`, `.regen-copy-btn-prominent` (GitHub-green primary, fixed min-width 80px so the "Copy" → "Copied!" flip doesn't shift layout), and `.regen-prompt-pre--wrap` (soft-wrap modifier). Bumped `.regen-prompt-pre` font-size 12 → 13, line-height to 1.55, max-height 480 → 520. The deprecated `.regen-prompt-details` class entry from styles is no longer referenced (kept harmless until a future cleanup pass).

No conflicts found in:
- `specs/development/spec_driven/interview/qa.md` (Round 3 q&a-structured-view answer is about Q/A view, not the regen prompt's UI; unaffected).
- `specs/development/spec_driven/findings/dossier.md`, `findings/angle-*.md` (research outputs predate this UI tweak; conclusions still hold).
- `specs/development/spec_driven/validation/{strategy.md, unit_tests.md, security.md, performance.md, accessibility.md}` (no language naming the inner `<details>` or "Copy to clipboard" string; assertions exercised against the API contract or unrelated UI surfaces remain valid).
- `projects/spec_driven/backend/libs/regen_prompt.py`, `backend/libs/api.py` (no contract change to `POST /api/regen-prompt`).
- `projects/spec_driven/frontend/src/api.ts`, `src/autonomousMode.ts`, `src/components/Editor.tsx`, `src/components/ProjectPage.tsx` (downstream consumers of the panel and unrelated components — unaffected).
- `CLAUDE.md` (no change to state surfaces, regen contract, or pinning rules).

## Stage 6 regeneration — 2026-05-03 11:45:22
Run id: spec_driven-20260503-114522
Trigger: User invoked "rebuild the spec driven project using the specs and validation strategy" — full read-zero regeneration of stage 6 outputs per CLAUDE.md regen contract.
Audit log: .audit/adhoc_agents/2026-05-03/spec_driven-20260503-114522/events.jsonl

Read-zero deletes (regen.delete.planned x14 → regen.delete.completed):
- Entire `projects/spec_driven/` folder removed before rebuild (backend libs, frontend src, package.json, tsconfig, vite.config, index.html). No surgical preservation; new generation reads only the canonical inputs (final_specs/spec.md + validation/* + CLAUDE.md + revised_prompt + follow_ups + interview/promoted.md).

Regenerated:
- Backend (FastAPI, 127.0.0.1:8765 only): `libs/{repo_root,safe_resolve,exposed_tree,tree_walker,file_reader,file_writer,promotions,stages,regen_prompt,api_security,api,__init__}.py`, `main.py`, `pyproject.toml`, `requirements.txt`, `Makefile`, `README.md`. Pin pin-001 verbatim in regen-prompt output. PATCH/DELETE on /api/file → 405; PUT without same-origin → 403; traversal/ADS/CON.md → single 404.
- Backend tests: `tests/conftest.py` + `tests/unit/test_{safe_resolve,file_reader,file_writer,regen_prompt,promotions,tree_walker,api}.py`. 133 cases pass. Includes the two regression-2026-05-02-clean cases (uniform `children` field + consumer-walk).
- Frontend (React + Vite + react-router-dom + react-markdown + rehype-sanitize + rehype-highlight): `src/{main.tsx,App.tsx,api.ts,types.ts,styles.css,autonomousMode.ts,localStorage.ts}`, `src/lib/{qaParser.ts,linkResolver.ts}`, `src/components/{Sidebar,Reader,Editor,QaView,QaErrorBoundary,RegeneratePanel,ProjectPage,Home,Breadcrumb,BrokenLink}.tsx`, `src/markdown/{Renderer,CodeView,JsonlView,ImagePlaceholder}.tsx`. SPA builds to `backend/static/` so `make run-prod` is a single process.
- Frontend tests: `test/{setup.ts,qaParser.test.ts,linkResolver.test.ts,autonomousMode.test.ts,Sidebar.test.tsx,QaErrorBoundary.test.tsx}` plus `test/fixtures/qa/{interactive,autonomous}.md`. 20 vitest cases pass. Includes regression-2026-05-02-clean coverage: qaParser autonomous form, Sidebar node.children walk, QaErrorBoundary as a real `Component` class (not try/catch).
- E2E: `frontend/playwright.config.ts` + `frontend/e2e/dogfood.spec.ts` (10 SYS-NN scenarios). Written, NOT executed in this run — Playwright browser drivers were not invoked. User runs via `make e2e`.

Verification covered in this run:
- Backend pytest: 133/133 passing. Single 404 on traversal/ADS/CON.md/short-name; 415 on .exe/.svg/.html/.png-write; 413 on >1 MB; verb whitelist 405 with `Allow: GET, PUT`; Origin/Host validation 403; regen-prompt header verbatim + autonomous imperative + read-zero in Constraints; promotions roundtrip + idempotence + stage_folder allowlist + parse_promoted_text; tree_walker uniform-children regression + consumer-walk regression.
- Frontend vitest: 20/20 passing.
- Production build: `npm run build` emits `backend/static/index.html` + `backend/static/assets/*` (1.4 MB JS / 467 KB gzip).
- Smoke: `python main.py` → 127.0.0.1:8765 binds correctly; `/`, `/file/*`, `/project/*`, `/api/tree`, `/api/file`, `/api/regen-prompt`, `/assets/*` all return 200.

Pending manual verification (per accessibility.md A11Y-17 + system_tests.md manual-walkthrough trigger): visual hierarchy of QaView Q/A tints, focus-visibility under real keyboard, motion/animation perceptibility, NVDA screen-reader sanity, forced-colors mode, 200% zoom, prefers-reduced-motion. Run `make e2e` to execute the Playwright suite.

`0.0.0.0` audit (SEC-20): zero hits across `projects/spec_driven/` — main.py + Makefile + README + libs all use 127.0.0.1 wording without the LAN-bind literal.
