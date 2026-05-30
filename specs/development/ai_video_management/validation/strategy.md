# Validation strategy — ai_video_management

Run: ai_video_management-20260505-002710
Stage: 5 (validation strategy)
Inputs consumed: `final_specs/spec.md` + 6 parallel level-specialist outputs.

> **Follow-up 039 amendment (2026-05-13):** path references to `backend/`, `frontend/`, `backend/libs/` in this strategy + sibling validation modules (`acceptance_criteria.md`, `bdd_scenarios.md`, `backend_tests.md`, `e2e.md`, `security.md`, `accessibility_and_manual.md`) are remapped to `apps/api/`, `apps/ui/`, `libs/{infrastructure,domain,application,common}/`. Validation acceptance is otherwise unchanged. New blocker: cross-layer imports violating dependency arrows in `.claude/agent_refs/project/development.md` §1.

## Levels chosen

| Level | File | Why |
|---|---|---|
| **acceptance_criteria** | `validation/acceptance_criteria.md` | Always required. 30 scenarios (24 automated + 6 manual) grouped by U1–U7 work units; covers all 8 primary flows + maps to FR-1..FR-85 + NFR-1..NFR-7. |
| **bdd_scenarios** | `validation/bdd_scenarios.md` | Always required. 9 features × 39 scenarios grouped by load-bearing contract: tree+sub_type detection / shot-pair / shotlist table / image-ref / locked-block pill / regen-prompt scope axis / cross-tree link / Origin/Host gate / localStorage namespacing. |
| **backend_tests** | `validation/backend_tests.md` | 13-module pytest matrix + boot-smoke + cross-platform skip + consumer-walk + parser-regex-against-real-artifact. Covers `validation/development.md` moves #2, #4, #5, #6, #10. |
| **security** | `validation/security.md` | 9 SEC-* check groups (~80 individual checks): ORIGIN-HOST, PATH-TRAVERSAL, EXTENSION-ALLOWLIST, BODY-CAP, MTIME-CONCURRENCY, CSP, SANITIZE, PROMOTE-STAGE6, LOOPBACK-ONLY. Covers `validation/development.md` move #11 (header-mutating-layer pre-rewrite + post-rewrite + real-proxy three shapes). |
| **e2e** | `validation/e2e.md` | 2 Playwright projects (`prod-mode` + `dev-mode`) × 11 spec files / 14 scenarios covering all 8 render-dispatch paths. Covers `validation/development.md` moves #1 (multi-mode parity), #8 (per-render-component), #9 (error-boundary coverage via `pageerror` listener catching React-reconciliation throws). |
| **accessibility_and_manual** | `validation/accessibility_and_manual.md` | 12 a11y checks (A11Y-01..12) + 12 manual walkthrough steps (M-01..12) + 4 sign-off hard gates. Covers `validation/development.md` move #7 (manual UI walkthrough before sign-off) + `general.md` principle 4 (manual walkthrough is a level too) + principle 6 (carve-out re-check). |

**Levels NOT included** (and why):
- **performance** — NFR-2 budgets (200ms tree, 50ms file read, 300ms ShotPairView render) are soft targets; not strict SLAs warranting their own level. Surface in manual walkthrough as "perceived latency <300ms" check (M-05).
- **regulatory / compliance** — n/a; localhost dev tool, no PII, no external data egress.
- **load** — n/a; single-user localhost.

## Per-level summary

### Acceptance criteria

- 30 scenarios (24 automated + 6 manual) grouped by U1–U7 work units. Each carries `# 来源 FR` citation + `[automated]` / `[manual_walkthrough_only]` tag.
- Coverage matrix at end maps every FR-1..FR-85 + NFR-1..NFR-7 to ≥1 scenario.
- All 11 required moves from `validation/development.md` landed as testable scenarios with severity hooks: U3.3 (Origin/Host three shapes), U6.6 (real on-disk fixtures + real React Error Boundary + grep-check forbidding `try { return <X /> } catch`), U3.11 (boot-smoke structural assertion), U7.2 (≥2 Playwright profiles per advertised mode), U7.1 (Makefile `uv` rejection without pip fallback), U7.4 (pinned-item preservation, stage-6 excluded per spec FR-32).

### BDD scenarios

- 9 features × 39 scenarios grouped by load-bearing contract (not by FR or work unit). Data tables enumerate variants for the sub_type regex (8 rows), scope axis (8-row sub_type × scope matrix), Origin/Host admit/reject (8 rows), and the 4 stage-6 prompt-body variants.
- Severity routing table at end:
  - **Critical elevations:** stages-1–5 prompt drift between `ai_video_management` and `spec_driven` (carve-out conflict class from `spec_driven-006`); locked-block regex bug (XSS via sanitization bypass); PUT-image-200 (read-only contract violated); IPv6 / 0.0.0.0 bind.
  - **Blocker elevations:** missing pre-rewrite shape in Origin/Host tests (per `development.md` rule 11 — the precise gate that re-introduces the `spec_driven-006` cross-port 403); render-mode dispatch failures (per rule 8); per-file-mirror cross-tree-link target.
- Cross-feature overlaps documented: ShotPairView panes reuse `MarkdownView` so Feature 5 regression implicitly fails Feature 2.4; persisted mode key shared between RegeneratePanel and namespacing.

### Backend tests

- 13-module pytest matrix covering `repo_root, safe_resolve, exposed_tree, tree_walker, file_reader, file_writer, promotions, regen_prompt, stages, api_security, api, sub_type_lookup, main`. Each row tagged with severity (`critical | blocker | warning`).
- **Move-#2 `test_tree_consumer_walk` skeleton** — recursive `node.children` descent + forbidden-legacy-key list (`videos`, `episodes`) + `project_meta` assertion against `wukong_juexing` resolving to `sub_type="short"`.
- **Move-#4 `test_boot_smoke.py` skeleton** — subprocess uvicorn boot + IPv4 socket wait + `GET /` + 3-section `/api/tree` shape + IPv6 refusal.
- **Move-#10 `test_lookup_against_real_wukong_juexing_qa_md`** — load-bearing test against the actual on-disk `qa.md` from run `wukong_juexing-20260503-201831`, accounting for backtick-wrapping, AUTONOMOUS judgment-call markup, and CRLF.
- **Move-#5 skip-marker matrix** — codifies POSIX-vs-Windows test gating.
- **Move-#6 `test_makefile_no_uv_invocation`** — static check enforces the `uv run` ban as a `blocker`-severity gate.

### Security

- 9 SEC-* check groups, ~80 individual checks tied 1:1 to FR-3, FR-7, FR-8, FR-11..FR-17, FR-28, FR-32. Every row carries id / endpoint(s) / attack scenario / pass condition / severity.
- **Move #11 (header-mutating-layer)** enforced: SEC-ORIGIN-HOST-07/-08 cover the raw `Origin: http://127.0.0.1:5174` direct-to-backend shape (the regression that shipped past `spec_driven-006`), -09..-12 cover post-rewrite happy paths and loopback-alias cross-products, -14 demands a Playwright profile through the real Vite proxy. Stage-5 sign-off is `blocker` if any of -07/-08/-14 is missing.
- **2 intentional status-code divergences from spec_driven** recorded inline so stage-6 doesn't port-verbatim them away:
  - **FR-28** chose **400** over spec_driven's 415 for PUT-extension reject (more accurate semantically — wrong content kind, not unsupported media).
  - **FR-15** made `If-Unmodified-Since` strictly **required** (missing → 400) where spec_driven treated it as optional.
- 5 v1 carve-outs surfaced for user reconfirmation per `general.md` principle 6: no auth, no file-delete endpoint, no CSRF token beyond Origin, fixed-palette dark `<pre>`, no rate limit.

### E2E

- **2-project Playwright config** (`prod-mode` baseURL=`http://127.0.0.1:8766`, `dev-mode` baseURL=`http://127.0.0.1:5174`) — multi-mode parity per move #1; the dev-mode `baseURL` deliberately points at the Vite port so the proxy `configure` hook is part of the test surface, preventing the `spec_driven-006` Origin-rewrite regression from re-introducing silently.
- **11 spec files / 14 scenarios** covering all 8 render-dispatch paths (MarkdownView, ShotPairView, ShotlistTableView, ImageRefView, QaView, JsonlView, CodeView, ImagePlaceholder). Each scenario opens a real triggering file under `ai_videos/wukong_juexing/` or `specs/ai_video/wukong_juexing/` (verified-on-disk).
- Asserts: `main` non-empty + render-mode-specific selector + `consoleErrors === []` + **`pageerror` listener** (load-bearing addition catching React-reconciliation throws that the move #9 `try { return <Foo /> } catch` anti-pattern misses).
- 5 stage-6 test-fixture prerequisites flagged: sample `.jsonl`, locked-block in `characters/main.md`, companion `.png` for `main_seedream.md`, two temp ai_video projects for sub_type=short and sub_type=None scope-toggle gating.

### Accessibility + manual walkthrough

- **12 a11y items (A11Y-01..12)**: light-theme chrome WCAG AA, dark `<pre>` carve-out contrast, keyboard focus visibility, copy-button `aria-label`, shared `aria-live="polite"` toast region, `<html lang="en">` + `<div lang="zh-Hans">`, image alt text, sub-type badge `aria-label`, visible "查看规格" link text, locked-block pill `title` / `aria-describedby`, RegeneratePanel form labels, color-not-only-differentiator. Severities all `blocker`.
- **12 manual walkthrough steps (M-01..12)**: ordered script run in BOTH `make run-prod` and `make run-backend + make run-frontend` per move #1 multi-mode parity. Covers visual hierarchy, contrast spot-check, keyboard focus, motion, <300ms perceived latency, then ai_video-specific real-data walks: ShotPairView dual pane + copy + aria-live (M-08), ShotlistTableView row click → shot-pair navigation (M-09), ImageRefView present/absent dual states (M-10), locked-block pill render on `【孙悟空 · 觉醒态 · 锁定描述符 v1】` (M-11).
- **Spec carve-out re-check** — walked all 11 spec § Out of scope items; zero hard conflicts. The FR-79 light-chrome vs FR-74/FR-80 dark `<pre>` apparent tension is pre-resolved by `agent_refs/project/development.md` rule 1 carve-out section, then closed by separate A11Y-01/A11Y-02 tests.
- **4 sign-off hard gates** (general.md principle 4): (1) all A11Y checks pass; (2) manual script passes in both modes; (3) user explicitly signs the carve-out table; (4) levels 01..05 must already be `validation.pass` before this level starts.

## Cross-cutting concerns

1. **Backend↔frontend field-name mirroring** (`validation/development.md` move #3). The TreeNode shape from FR-19 is consumed at three sites: backend `tree_walker.py` (emit), frontend `Sidebar.tsx` (render with `node.children` recursion), frontend `Reader.tsx` (path/type dispatch). Backend tests must reference `node.children` / `node.project_meta` exactly as the frontend does — no `tree["projects"]` / `tree["videos"]` legacy. Cross-cut owner: backend_tests level (consumer-walk test).

2. **Header-mutating-layer parity** (`validation/development.md` move #11). The Vite dev-server proxy at port 5174 rewrites `Origin: http://127.0.0.1:5174` → `Origin: http://127.0.0.1:8766` so the backend gate sees the same shape `make run-prod` produces. Three test shapes required: pre-rewrite (browser direct → backend, expect 403), post-rewrite (rewritten → backend, expect 200), real proxied (browser → Vite → backend, full e2e). Cross-cut: security level (SEC-ORIGIN-HOST-07/-08/-14) + e2e level (dev-mode profile).

3. **Locked-block regex generality** (FR-65, FR-66). Pattern `【.+? · .+? · 锁定描述符 v\d+】[\s\S]*?禁用 .*?。` must work for any character — not Wukong-hardcoded. Backend test takes the wukong_juexing descriptor as one fixture; a synthetic-character fixture (e.g., `【NAME · 状态 · 锁定描述符 v2】 ... 禁用 ...。`) is a second fixture. Cross-cut: backend_tests + bdd_scenarios.

4. **Status-code divergences from spec_driven**. Two intentional differences (FR-28 → 400 not 415; FR-15 → required, not optional). Stage-6 implementers must NOT port-verbatim spec_driven's 415 / optional behavior. Documented in `validation/security.md`. Cross-cut owner: security level + spec_driven-port comments in stage-6 implementation.

5. **localStorage key namespacing** (FR-72, NFR-3). Both webapps may run simultaneously; their localStorage keys must not collide. Pattern: `ai_video_management.<feature>.<version>` (e.g., `ai_video_management.autonomous_mode.v1`). Backend cannot enforce this — it's a frontend invariant tested in BDD scenario Feature 9 + Vitest unit test for `autonomousMode.ts`.

6. **Promotion preservation check** (`validation/general.md` principle 8 + `validation/ai_video.md` move #7). This task does NOT have any `<stage>/promoted.md` sidecars at v1 (the spec_driven webapp wasn't used for any pin operations on the `ai_video_management` task itself). Skipped in v1 strategy. If a future regen runs after pinning, strategy must be re-derived with a `promotion_preservation` level added.

7. **Voice pool — explicit no-HTTP carve-out** (follow-up 115). The voice pool (U8) deliberately has zero outbound-HTTP surface: no Kling-equivalent endpoint, no provider env vars, no JWT, no SSRF vet. Stage-6 implementers must NOT port the actor pool's `_validate_outbound_url` / Kling JWT helper / 429-retry loop into the voice modules. Validators MUST grep-fail if `httpx.AsyncClient` / `urllib.request` / outbound URL literals appear anywhere under `libs/infrastructure/writers/voice__*.py` or `libs/infrastructure/clients/voice_*.py` (the latter file must not exist at all). Cross-cut owner: backend_tests level (U8 row) + security level (SEC-VOICE-* future check group, deferred until U8 lands; v1 audit surface is FR-9v5 multipart upload only).

## How runtime validation will use this

Stage 6 runtime mode will:

1. **For each of U1..U7 (sequential per dependency chain):**
   - Append `validation.started` with the unit's applicable levels (per the matrix below) + `pre_reading_consulted` (this strategy.md + applicable per-level files + `validation/general.md` + `validation/development.md` + `agent_refs/project/development.md`).
   - Spawn validators in parallel — one general-purpose worker per applicable level.
   - Validators emit `validation.issue.raised` per issue with `{id, level, severity, location, description, suggested_fix}` OR `validation.pass` if all clear.
   - On `blocker` issues: parent revises (max 3 rounds per `CLAUDE.md` § Iteration bounds). Same `issue_id` repeating across 2 rounds → `pipeline.halted`.
   - On `critical` issues: halt immediately, no revision rounds without explicit user approval.
   - On `warning` issues: log, do not block.

2. **Per-work-unit level applicability:**

| Unit | acceptance | bdd | backend_tests | security | e2e | a11y_manual |
|---|---|---|---|---|---|---|
| U1 backend libs core | ✓ | ✓ | ✓ | partial (sandbox / safe_resolve only) | n/a | n/a |
| U2 backend tree+regen | ✓ | ✓ | ✓ | partial (regen scope + sub_type detection) | n/a | n/a |
| U3 backend api+main+security | ✓ | ✓ | ✓ | ✓ (full) | n/a | n/a |
| U4 frontend scaffolding | ✓ | ✓ | n/a | n/a | boot-smoke (Vite + bundle build) | ✓ (light theme baseline) |
| U5 frontend ported components | ✓ | ✓ | n/a | n/a | per-component (MarkdownView, QaView, JsonlView, CodeView, ImagePlaceholder, Editor) | ✓ |
| U6 frontend new ai_video views | ✓ | ✓ | n/a | n/a | per-view (ShotPairView, ShotlistTableView, ImageRefView) | ✓ |
| U7 Makefile + README + e2e | ✓ | ✓ | n/a | partial (CSP header + bind config) | ✓ (full multi-mode) | ✓ |
| U8 voice pool (follow-up 115) | ✓ | ✓ | ✓ (voice composition + casting parser; NO outbound-HTTP tests) | ✓ (FR-9v5 multipart audio upload — extension allowlist, 10 MiB cap, sandbox, symlink-reject; NO SSRF / no provider-key surface to vet) | ✓ (VoiceView + VoiceGrid + audio playback; FR-9v5 drop-zone + upload) | ✓ (audio player keyboard accessibility, caption-style `aria-label` on play buttons in grid) |
| Whole-project final pass | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ + manual walkthrough |

3. **After all 7 units pass automated levels:** parent runs the **whole-project final pass** — re-runs all levels across the full project, including cross-unit drift checks (e.g., a TreeNode shape change in U2 not propagated to a Sidebar.tsx read in U5).

4. **After whole-project final pass passes:** parent emits `validation.requires_manual_walkthrough` and surfaces `accessibility_and_manual.md`'s 12-step walkthrough script. User runs the script in BOTH `make run-prod` AND `make run-backend + make run-frontend` modes. Once user replies "manual walkthrough 通过": parent writes `validation.pass level=manual_walkthrough` + `pipeline.halted reason=done`.

5. **Audit-event tags.** Every check carries an `events.jsonl` audit-event tag in the form `check=<slug>, path=<file>, severity=<level>`. Per `validation/general.md` principle 5: a level without audit events is treated as if it didn't run.

## Promotion-preservation check

Per `validation/general.md` principle 8 + `validation/ai_video.md` move #7:

- This task does NOT have any `<stage>/promoted.md` sidecars at v1.
- Promotion-preservation checks are **skipped at v1** for all spec-pipeline stages (interview, findings, final_specs, validation).
- Stage 6 (project code) does NOT support promotion in v1 per spec FR-32.
- If a future regen runs after the user pins items via the new ai_video_management webapp itself (or via the existing spec_driven webapp targeting `ai_video_management`'s artifacts), the strategy must be re-derived with a `promotion_preservation` level added.

## Output paths recap

- `validation/acceptance_criteria.md`
- `validation/bdd_scenarios.md`
- `validation/backend_tests.md`
- `validation/security.md`
- `validation/e2e.md`
- `validation/accessibility_and_manual.md`
- `validation/strategy.md` (this file)

Stage 6 reads `strategy.md` first to learn level applicability per work unit, then dispatches to the per-level files for criteria detail.
