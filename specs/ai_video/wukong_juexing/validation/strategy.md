# Validation strategy — wukong_juexing

Run: wukong_juexing-20260503-201831
Stage: 5 (validation strategy)
Inputs consumed: `final_specs/spec.md` + 5 parallel level-specialist outputs.

## Levels chosen

| Level | File | Why |
|---|---|---|
| **acceptance_criteria** | `validation/acceptance_criteria.md` | Always required (validation playbook). Maps the 5 Primary-flow steps + 6 stage-6 work units to Gherkin scenarios with `# 来源 FR` annotations. |
| **bdd_scenarios** | `validation/bdd_scenarios.md` | Always required. 7 load-bearing features × 32 scenarios; groups behaviors by contract (character lock, style lock, dual-prompt asymmetry, hook+thumbnail, loop-back, descriptor specifics, publish skeleton). |
| **schema_compliance** | `validation/schema_compliance.md` | Covers ai_video required moves #1 (language), #2 (≤15s shot atomicity), #4 (dual-prompt), #5 (aspect ratio + hook), #6 (publish metadata). ~80 mechanical `SCH-*` checks runnable via grep / Python parsing. Hard prerequisite for content_lock. |
| **content_lock** | `validation/content_lock.md` | Covers ai_video required move #3 (character consistency byte-equality) and the load-bearing locks: palette/token vocabulary, Q1–Q5 specifics, dual-template asymmetry semantics, hook+thumbnail and loop-back contracts, register anchor phrase. 25 `blocker`-level checks. Includes paste-ready `DescriptorChecker` Python implementation. |
| **manual_walkthrough** | `validation/manual_walkthrough.md` | Covers ai_video required move #8. The post-render visual gate that automation cannot replace: on-model character / on-style register / hook viability / thumbnail viability / loop closure / cinematic flow. 13 walkthrough checks + 10 carve-out cross-checks + 4 sign-off gates. |

**Levels NOT included** (and why):
- **unit_tests** — no executable code under test in this ai_video task; outputs are `.md` prompt files. The closest analog is schema_compliance (which IS included).
- **system_tests** — no integrations to test; the user runs Seedream + Kling + Seedance externally.
- **performance** — no spec-level latency / throughput requirement; rendering performance is an external-tool concern.
- **security** — no auth, secrets, or untrusted input on the spec surface.
- **accessibility** — no UI under our control; YouTube Shorts handles a11y on the consumer side. (Note: the spec's no-text-overlay rule is a creative choice, not an a11y concession.)

## Per-level summary

### Acceptance criteria

- 28 automated Gherkin scenarios + 6 manual-only scenarios, organised by stage-6 work unit (U1–U6) plus a cross-cutting block (language, paths, pin preservation).
- Coverage matrix verifies reverse-coverage of FR-1..FR-42 + NFR-2/3/4/5/6/7/8 (NFR-1 is documentation-only).
- Load-bearing scenarios: 11-file byte-equal locked-descriptor (AC-U4-02), Kling/Seedance dual-prompt asymmetry (AC-U4-06), 38s sum + ≤10s per-shot (AC-U3-02), 9:16 triple-redundancy (AC-U4-03), thumbnail contract at t≈2s (AC-U4-10), loop-back contract (AC-U4-11), Chinese-content ≥95% (AC-X-01), publish 6-section + dual-time-window (AC-U5-01/03).

### BDD scenarios

- 7 features × 32 scenarios (27 automated + 5 manual). Each scenario carries concrete example data tables: violation modes, per-shot durations, hex anchors, hashtag candidates, 标题 length, per-shot emission posture.
- Coverage maps FR-11..FR-41 + NFR-1/2/3/6 to feature × scenario × mode.
- Severity routing table: blockers (locked-descriptor drift, palette-vocabulary leaks, dual-prompt schema violations, publish-metadata bound failures), warnings (tool-version pin gaps), `requires_manual_walkthrough` (visual register coherence, thumbnail quality, loop closure, weighty register, platform preview).

### Schema compliance

- 8 file-type check groups + 1 language-compliance suite, ~80 mechanical `SCH-*` checks. Each: unique id, absolute target glob, pass condition, severity, audit-event tag.
- Boundary with content_lock made explicit: schema layer answers "is the field there and does its value fall in the enum"; cross-file byte-identity, palette/token vocabulary lock, descriptor specifics, semantic anchors all belong to content_lock.
- Provides `validators/locked_descriptor.py` skeleton (`extract_locked_block`, `extract_role_field_block`) — the **shared API both schema_compliance and content_lock import**, single source of truth for sentinel logic.
- Language compliance aggregated into one shared `SCH-LANG-*` suite (per ai_video.md move #1) — 95% CJK threshold runs once globally with per-file routing.

### Content lock

- 9 contract groups / 25 `blocker`-level checks: locked-descriptor byte-equality across 11 files (sentinel regex `【孙悟空 · 觉醒态 · 锁定描述符 v1】 ... 禁用 卡通线条、cel-shading、二次元大眼、低多边形。`), 10-hex palette allowlist, 6-token lighting + 5-pattern motion + 2-rule transition vocabulary locks (note: FR-31 already excluded white-flash transition, so transition catalog is `hard cut` + `match cut` only — 2 rules, not 3), 禁用 register list with `negative_prompt:` / `约束:` allow-region carve-outs, Kling↔Seedance asymmetry quartet, Q1–Q5 specifics (金箍棒 length + emission + fur + stars + hex context), Shot 01 缩略图契约, Shot 05 回环契约, 美术风锚点.
- Boundary: content_lock is a hard prerequisite for acceptance_criteria BDD and manual_walkthrough — descriptor drift makes visual review meaningless. Stage 6 runs schema → content → acceptance/BDD → manual sequentially per work unit.
- Executable artifact: `validators/content_lock_descriptor.py` complete `DescriptorChecker` class with frozen dataclass result, sentinel regex, whitespace-normalised compare (`re.sub(r"\s+", " ", ...)`), JSONL event emission, `exit 0/1` contract. Stage-6 invocation: `uv run python validators/content_lock_descriptor.py <project_root> <events_path>`.

### Manual walkthrough

- 13 numbered walkthrough checks: 立绘 on-model lock, cross-shot character consistency (blind), 黑神话 register, palette eyedrop, 0–2s hook, FR-29 thumbnail standalone readability, FR-30 loop closure, inter-shot transitions, full-cut cinematic flow, third-party-observer validation, hook/climax/loop sign-off shots, single-shot independence, render-side artefact sweep.
- 10 carve-out re-check (per validation/general.md principle 6): walks the spec's 10 Out-of-Scope items + flags any contract-drift (severity = `critical`, halts walkthrough).
- 4 sign-off gates: 13 walkthrough checks all pass + 10 carve-outs all confirmed + user subjective ≥7/10 + literal "manual walkthrough 通过" reply. On sign-off the parent writes two `events.jsonl` lines: `validation.pass level=manual_walkthrough` + `pipeline.halted reason=done` — closing the upstream `validation.requires_manual_walkthrough` event.

## Cross-cutting concerns

1. **Sentinel logic is shared.** Both schema_compliance and content_lock extract the locked-descriptor block via the same sentinel regex. The `locked_descriptor.py` shared module from level 03 is the single source of truth — content_lock IMPORTS it, doesn't reimplement. Stage 6 must wire this dependency cleanly.

2. **Level ordering on each work unit.** Per the boundary established by levels 03 and 04: `schema_compliance` runs first; on `pass`, `content_lock` runs; on `pass`, `acceptance_criteria` + `bdd_scenarios` run (these can run in parallel since both are read-only criteria checks). `manual_walkthrough` is deferred to a single end-of-project pass after **all** work units have passed automated levels — not per-unit. This matches `ai_video.md` move #8 ("after all automated levels pass for a work unit (one episode for novels, the whole short for shorts)").

3. **Per-work-unit level applicability.**

| Unit | schema | content | accept | bdd | manual |
|---|---|---|---|---|---|
| U1 character | ✓ | ✓ | ✓ | ✓ | (deferred to whole-short pass) |
| U2 style_guide | ✓ | ✓ | ✓ | ✓ | (deferred) |
| U3 narrative | ✓ | ✓ | ✓ | ✓ | (deferred) |
| U4 prompts | ✓ | ✓ | ✓ | ✓ | (deferred) |
| U5 publish | ✓ | (n/a — palette/descriptor not in publish scope; content_lock skipped with `validation.skipped` neutral event) | ✓ | ✓ | (deferred) |
| U6 readme | ✓ | ✓ (light: keyword-sync only) | ✓ | ✓ | (deferred) |
| Whole-short final pass | ✓ | ✓ | ✓ | ✓ | ✓ |

4. **Skipped vs failed semantics.** When `content_lock` cannot run because schema_compliance failed (descriptor block missing entirely → sentinel regex returns no match), the event is `validation.skipped` with reason `prerequisite_unmet`, NOT a fail. This avoids double-counting the same root cause. Once schema is fixed, content_lock re-runs.

5. **Tool-version pin (NFR-1).** Spec assumes Kling 2.1 Pro / Seedance 1.0 Pro. Tools are moving fast (Kling 3.0 / Seedance 2.0 in rollout). The `validation/strategy.md` does not auto-fail on prompts that opt into newer-tier features — but bdd_scenarios surfaces a `warning` level when a prompt uses syntax outside the 2.1 Pro / 1.0 Pro reference set. Treat as `warning`, not `blocker`.

6. **Spec carve-outs (per validation/general.md principle 6).** The 10 Out-of-Scope items in `final_specs/spec.md` were each cross-checked at stage 5. Sign-off:
   - **Multi-character scenes** — confirmed: nowhere in the spec or workflow does the user need a second character.
   - **Multi-episode structure** — confirmed: explicit short layout (no `episodes/`).
   - **Audio / music / SFX prompts** — confirmed: no shot file declares an `音效:` field; publish.md omits music suggestions.
   - **Text overlays + dialogue + lip-sync** — confirmed: shot files have no `字幕` field; FR-19 禁用 list and `agent_refs/project/ai_video.md` rule 4 align.
   - **Distribution variants beyond YouTube Shorts** — confirmed: cross-publish appendix in publish.md is *informational*, not generated as separate files.
   - **Stage-6 actual rendering** — confirmed: deliverables are prompts; user runs externally.
   - **English-language publish variant** — confirmed: deferred to v2 follow-up.
   - **Separate cover-still Seedream prompt** — confirmed: Shot 01 doubles as thumbnail (FR-29).
   - **黑神话 IP-tag** — confirmed: publish.md hashtag candidate list explicitly excludes `#黑神话悟空` from the recommended top-3.
   - **AI-uncontrollable transitions (white flash)** — confirmed: FR-31 locks transition vocabulary to `hard cut` + `match cut` (transition rule count is 2, not 3 — see content_lock summary above).

   No carve-out conflicts with delivered behavior. No contract-drift detected.

## How runtime validation will use this

Stage 6 runtime mode (per validation playbook) will:

1. **For each of U1..U6 (sequential):**
   - Append `validation.started` with the unit's applicable levels (per the matrix above) and `pre_reading_consulted` (this strategy.md + the per-level files + ai_video.md / general.md).
   - Spawn validators in parallel — one general-purpose worker per applicable level. Each validator uses the shared `validators/locked_descriptor.py` module + its own level file as the criteria source.
   - Validators emit `validation.issue.raised` per issue with `{id, level, severity, location, description, suggested_fix}`, OR `validation.pass` if all clear.
   - On `blocker` issues: parent revises the unit (max 3 rounds per `CLAUDE.md` § Iteration bounds), appending `exec.revision.applied`. Same `issue_id` repeating across 2 rounds → `pipeline.halted`.
   - On `warning` issues: log to events.jsonl, do not block.

2. **After all 6 units pass automated levels:** parent runs the **whole-short final pass** — re-runs schema + content + acceptance + bdd across all 12 generated files. This catches cross-unit drift that per-unit checks could miss (e.g., a hex code introduced in U2's style_guide.md but not yet propagated to U4's shot files).

3. **After whole-short final pass passes:** parent emits `validation.requires_manual_walkthrough` and surfaces the `manual_walkthrough.md` script to the user. User runs the 13 checks + 10 carve-out re-check externally (after generating立绘 and rendering 5 shots). Once user replies "manual walkthrough 通过": parent writes `validation.pass level=manual_walkthrough` + `pipeline.halted reason=done`.

4. **Audit-event tags.** Every check carries an `events.jsonl` audit-event tag in the form `check=<slug>, path=<file>, severity=<level>`. Per `validation/general.md` principle 5: a level without audit events is treated as if it didn't run.

## Promotion-preservation check

Per `validation/general.md` principle 8 + ai_video.md required move #7:

- This task does NOT have any `<stage>/promoted.md` sidecars (the spec_driven webapp wasn't used for any pin operations on this task; the dossier and spec were generated end-to-end without webapp interaction).
- Therefore promotion-preservation checks are **skipped at v1** for all spec-pipeline stages (interview, findings, final_specs, validation).
- Stage 6 (project code) does not support promotion in v1 per ai_video.md required move #7 — no check generated.

If a future regen is run after the user pins items via the webapp, the strategy must be re-derived (one new level: `promotion_preservation`); for this run there is nothing to preserve.

## Output paths recap

- `validation/acceptance_criteria.md`
- `validation/bdd_scenarios.md`
- `validation/schema_compliance.md`
- `validation/content_lock.md`
- `validation/manual_walkthrough.md`
- `validation/strategy.md` (this file)

Stage 6 reads `strategy.md` first to learn level applicability per work unit, then dispatches to the per-level files for criteria detail, and uses `validators/locked_descriptor.py` (to be created in stage 6 alongside the other shared validator code, OR placed under `tools/` per CLAUDE.md project rules) for shared sentinel extraction.
