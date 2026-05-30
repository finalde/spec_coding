# Validation strategy — xianxia_new (working slug → `feng_shou_lu`)

Run: `xianxia_new-20260524-101931`
**Stage 5 — strategy mode** (run once)
**Synthesis confidence:** high · 7 workers all returned `complete`
**MVP scope:** ep01 only (per follow-up 001)

## Levels chosen

| # | Level | Why this level (1-line) | File |
|---|---|---|---|
| 01 | **acceptance_criteria** | Gherkin scenarios for every FR + measurable NFR + AC item — the mechanical gate per `validation.md` always-include list. | `acceptance_criteria.md` |
| 02 | **bdd_scenarios** | Feature-level rollup behaviors per primary production flow (F1–F8), tying acceptance scenarios to `work_unit_kind` dispatch — playbook always-include. | `bdd_scenarios.md` |
| 03 | **ai_video_compliance** | The 6 mandatory ai_video.md format/schema/layout/aspect-ratio/publish-meta/pinned-items gates (rules 1/2/5/6/7 + 12.4 v2 schema). Includes the rule-4 → rule-5 single-`shotNN.md` reconciliation. | `ai_video_compliance.md` |
| 04 | **character_visual_consistency** | Image-first pipeline gate per ai_video.md rule 3 + 4 — byte-identical 一句话锁定 + face-differentiator across bible / 立绘 / every shot prompt in ep01. Includes mozun cross-project face-mark check. | `character_visual_consistency.md` |
| 05 | **copyright_clearance** | Auto-grep gate against 14-baseline BLACKLIST (baseline_extraction §2.5) + mozun_chongsheng cross-grep + wode_moni_changsheng_lu CCI-1 forbidden-zone fingerprint check. ~145 atomic terms. | `copyright_clearance.md` |
| 06 | **storyteller_dialogue_master** | ai_video.md rule 9 mandatory — the only content-quality validator. 8 review axes: 通俗易懂性 / 信息量 / 节奏 / 角色声口 / hook landing / 情节链 / station fidelity / anachronism. | `storyteller_dialogue_master.md` |
| 07 | **internal_consistency** | Narrative invariants no other level catches: parasitic-cost ledger (24-tick schedule), reveal cadence integrity (11-beat table), faction-system coherence, slug/title consistency, ep01-plants-future-payoff. | `internal_consistency.md` |

Levels NOT chosen (and why): **unit_tests** (no production code in this task — content artifacts only); **performance** (no latency / throughput requirement in spec NFRs); **security** (no auth / secrets / external input handled by the artifacts themselves; the rendering services Kling/Seedance/Seedream are out-of-scope per FR carve-outs); **accessibility** (not a UI task; subtitle readability captured in `style_guide.md` and surfaced via `validation.requires_manual_walkthrough` per ai_video.md rule 8).

## Per-level summary

### 01 acceptance_criteria
- **28 Gherkin scenarios** covering FR-1 through FR-14, **13 NFR `Rule:` assertions**, **7 AC master scenarios** — 48 gate checks total.
- Severity distribution: 0 critical, 39 blocker, 8 warning (NFR-7 cast-size & NFR-8 prop-density warning-tier; soft variants on shot-length / runtime / Chinese-content compliance).
- Carve-out review surfaced **2 stage-4 sign-off items** (not blockers): (a) § Out of scope #6 wording ambiguity (reads as banning all dialogue text until parenthetical narrowing; spec is internally consistent but recommend a 1-line sharpen). (b) FR-5 header inconsistency ("9 files" but table enumerates 10 — `裴长砚` archive file is the 10th).

### 02 bdd_scenarios
- **8 features** matching the primary production flow: F1 project_bootstrap · F2 character_bible · F3 world_and_style · F4 arc_outline · F5 scene_pack · F6 episode_full · F7 copyright_clearance · F8 audit_orchestration.
- **Rollup matrix: 14/14 FRs = 100% covered** by at least one Feature; all NFRs + ACs also mapped.
- Every Feature has ≥ 1 failure scenario. F6 (episode_full — the biggest unit) carries 5 distinct failure scenarios + 1 manual walkthrough; F8 (audit) carries 3 (skipped walkthrough, empty pre_reading, iteration-bound trip).

### 03 ai_video_compliance
- **7 validators (V-1 through V-7); 6 of 7 emit `blocker` on primary failure**; V-7 escalates to `critical` on missing pin (n/a this run — empty `promoted.md`).
- **Rule-4 → rule-5 reconciliation locked in:** validator checks for **one** self-contained `shotNN.md` (with embedded seam-frame code blocks per ai_video.md rule #5 / #12.4 v2), accepting either `shots/shotNN.md` (flat) or `shots/shotNN/shotNN.md` (rule #12.8 v2 folder variant). Legacy 3-file pattern is NOT validated.
- **Most likely ep01 failure mode:** V-4 schema drift on `shotNN.md` — `动作:` timed-beat sum ≠ `时长:` (rule #12.4 v4 contract) + `负向:` line under-populating from the 14 项扩展 photorealism + 11 项 AI-同质化 items per rule #12.7-B+/C. Mitigation: stage 6 re-pastes from `style_guide.md` verbatim, not paraphrases.
- **Work_unit_kind taxonomy:** `pre_flight` → `per_file` → `per_shot` → `per_prompt_file` → `per_episode` → `per_stage_regen`. Parent halts on V-2 failure for a shot before running V-4 on the same shot.

### 04 character_visual_consistency
- **8 validators (V-CV-1 through V-CV-8); 7 of 8 blocker**; V-CV-7 (multi-character ≥4 expansion rule) `warning`-only — the ep01 倒叙 montage shot (6 betrayers + 主角 + 师父 cameo) is the expected warning site.
- **Most fragile validator: V-CV-4** — byte-identical 一句话锁定 across all 7 ep01 shot prompts. Drift surface scales O(shots × characters); mitigated by stage-6 escalation message "copy the bible's row #10 value byte-for-byte; stop re-typing".
- **Pre-clearance at strategy-compile time:** 裴知秋's `左眼下方 0.3cm 灰青胎记` face-differentiator clears V-CV-8 against mozun's catalog (opposite side from 沧冥's `右眼下方 0.5cm 朱砂痣`; no other mozun character occupies 眼下).
- Drift-detection algorithm: Unicode NFC + whitespace folding only; punctuation / digit width / quotation marks NOT folded (semantic edits correctly trip the gate).

### 05 copyright_clearance
- **7 validators (V-CR-1 through V-CR-7); ~145 atomic BLACKLIST terms** (≈ 95 from 14-baseline §2.5 + ≈ 50 from mozun sample) — will grow at stage-6 runtime via recursive grep of `ai_videos/mozun_chongsheng/`.
- **Highest-risk accidental-use term: `万仙盟`** (wode_moni's 正派联盟 — CCI-1 forbidden zone). Structurally tempting because our 散修 organization (`流烛盟`) + mozun's `中州五道盟` demonstrate the "X盟" instinct. Stage-6 grep flags this specifically. Rank-2 risk: `沈烬` / `烬`-family (saturated 2025–2026 minefield from CCI-2).
- **Empty-folder补抓 recommendation:** stage 6 does NOT block on the 3 empty baseline folders (`cong_jianshu_xiuxing` / `gou_zai_xiuxianjie` / `zhutian_daozu`). V-CR-7 writes a hard SIGN-OFF gap-note declaring the under-spec'd status; next-iteration (ep02+) validator catches any post-download name conflict.

### 06 storyteller_dialogue_master
- **8 review axes per ai_video.md rule 9 / §12.4-D:** 4 per-shot (通俗易懂性 / 信息量 / 节奏 / 角色声口) + 4 cross-shot (黄金钩 landing / 情节链 / station fidelity / no anachronism). Patches emit as per-shot inline JSON-envelope events that the parent applies surgically.
- **Most-likely ep01 first-pass blocker:** Axis-7 anachronism — **容漪 named in spoken dialogue** before her ep05 full debut (spec FR-5 locks her ep01 to visual-only cameo).
- **Cross-shot risk:** Axis-8 + Axis-4 — the 6 倒叙 betrayers collapsing into interchangeable "今日便是你的劫数"-style reversal lines, defeating the ep08/ep10/ep17/ep28/ep49/ep60 face-recognition payoff. Mitigated by the spec's 6-template voice-distinct matrix (卫长烛 礼训式 / 应砚之 朝堂书面感 / 戚归砚 江湖兄弟感 / 池洇 杀手低沉 / 阮惘 命数感 / 言息 神位预言感).
- **Proposed NFR-9b (surfaces to stage-4 sign-off):** 弹窗 template byte-identity across episodes. ep01 sets canonical form `代价已计算 · 寿元 -N / 修为 +1`; ep02+ drift = blocker. Cross-episode reveal cadence depends on this being recognizable to viewers as a recurring franchise beat.

### 07 internal_consistency
- **7 validators (V-IC-1 through V-IC-7); 6 of 7 blocker-primary**; V-IC-6 blocker on slug/title drift + warning on `xianxia_new` leftovers.
- **Highest-leverage validator: V-IC-1 (parasitic-cost ledger)** — per dossier CCI-2 the parasitic system is the project's load-bearing differentiator. If V-IC-1 fails, the project's central conceit is mute on screen. Canonical 24-row schedule (1 tick at ep01 → 24 ticks exhausted at ep60) baked into the level file as a reference table.
- **Reveal cadence reference table** (11 beats: ep01 / ep08 / ep10 / ep17 / ep20 / ep28 / ep30 / ep35 / ep49 / ep50 / ep60) restated in the level for stage-6 lookup.
- **3 under-spec'd narrative dependencies surfaced for stage-4 attention** (NOT blockers — refinements):
  1. `world.md` § 三方势力格局 currently lists 正派/散修/魔门 but does NOT declare 朝堂 / 太师府 as a non-sect political entity → 应砚之's faction assignment dangles. V-IC-4.4 will fire as a real gap unless stage 6 extends world.md to include the朝堂 layer.
  2. 戚归砚's 流烛盟 ↔ 忘川教 dual-affiliation must be explicitly written into both `world.md` and `characters/戚归砚.md` (V-IC-4.2 pre-scripted on this).
  3. Cumulative ledger arithmetic (24 ticks exhausted at ep60) should be re-stated as a hard target in `characters/裴知秋.md` 累计 ledger field so stage-6 ep02+ work doesn't drift past 24.

## Cross-cutting concerns

### CC-1 — Level execution order matters per work unit
Per ai_video_compliance worker, the parent runs validators in priority order to avoid wasted iterations:
1. **`ai_video_compliance`** (schema gate — fastest; any file with broken schema doesn't deserve content review).
2. **`internal_consistency`** (narrative break catch — runs before character_visual because narrative breaks would propagate as descriptor drift downstream).
3. **`character_visual_consistency`** (byte-identical cross-file).
4. **`copyright_clearance`** (auto-grep — runs whenever a content file lands).
5. **`acceptance_criteria` + `bdd_scenarios`** (rollup gate at episode_full close).
6. **`storyteller_dialogue_master`** (content quality — last, because lower-cost gates have already filtered out shots that won't pass syntax / consistency / IP gates).

### CC-2 — State that resets between work units
- The 倒叙 montage shot in ep01 carries 6 named characters. After it finishes, the per-shot character-count budget (NFR-7 ≤ 5) resets — subsequent ep01 shots do NOT carry that 6-character debt.
- Parasitic ledger state PERSISTS across shots within ep01 and across episodes in arc_outline.md — V-IC-1 reads the cumulative count, NOT per-shot delta.
- Iteration cap (CLAUDE.md § Iteration bounds): 3 revision rounds per work unit; same `issue_id` repeats across 2 iterations → halt. Wall-clock cap: 30 minutes per unit.

### CC-3 — The 倒叙 montage shot is the highest-risk single artifact in ep01
Three validators converge on it as the most likely failure site:
- **V-CV-7** (multi-character expansion rule — warning expected; budget over NFR-1 soft limit).
- **V-CV-4** (byte-identical 一句话锁定 across 6 betrayer cameos — drift surface peak).
- **Axis-8 storyteller** (anachronistic name reference + reused dialogue templates across the 6 cameos).
Stage-6 strategy: produce the montage shot LAST in the work unit so the other 6 shots have already locked in each character's anchor string by byte-comparison; the montage then re-uses those locked strings verbatim.

### CC-4 — Promotion-preservation check (playbook required section)
For each spec-pipeline stage with a non-empty `<stage>/promoted.md`, every pin MUST appear verbatim in the regenerated artifact for that stage (parsed via `parse_promoted_text` in `libs/promotions.py`, asserted modulo whitespace). Severity: missing pin = `critical`.

**Status this run:** No `promoted.md` files exist yet under `specs/ai_video/xianxia_new/` (interview/promoted.md / findings/promoted.md / final_specs/promoted.md / validation/promoted.md are all absent). This check is dormant. If the user pins items via the spec_driven webapp in subsequent runs, the check activates automatically.

**Stage 6 (project code under `my_novel/` and `ai_videos/`) does NOT support promotion in v1** — this check is NOT generated for stage-6 work units.

### CC-5 — Cross-project mozun_chongsheng coupling
Two validators check against mozun:
- **V-CV-8** (face-differentiator non-collision) — pre-cleared at strategy time.
- **V-CR-4** (named-entity cross-grep) — runs at stage 6 against `ai_videos/mozun_chongsheng/` recursively.
Stage 6 must NOT modify any `ai_videos/mozun_chongsheng/` files. If a stage-6 worker accidentally writes into the wrong project directory, that's a path-traversal-class failure (per validation/general.md §7 + general principle 2 blast-radius severity).

## How runtime validation will use this strategy

### Work_unit_kind taxonomy (proposed for stage 6)

| Work unit kind | Artifacts produced | Levels run | Pass/fail policy |
|---|---|---|---|
| `pre_flight` | folder-tree skeleton; README + slug check before content starts | V-3 (layout) + V-IC-6 (slug consistency) | All-blocker; halts stage 6 immediately on failure |
| `world_and_style` | `world.md` + `style_guide.md` | V-1 (language) + V-IC-4 (faction coherence) + V-IC-5 (motif spec) | Blocker policy standard |
| `arc_outline` | `arc_outline.md` | V-1 + V-IC-2 (reveal cadence) + V-IC-1 (ledger) + V-CR-5 (wode_moni fingerprint) | Blocker; halts forward stages until cadence beats land |
| `character_bible` | one `characters/{name}.md` + `characters/ref_images/{name}_seedream.md` | V-1 + V-CV-1 + V-CV-2 + V-CV-3 + V-CV-5 + V-CV-6 (双形态 only for 裴知秋) + V-CV-8 + V-CR-3 (etymology) | One-character at a time; blocker on schema or face-mark collision |
| `scene_pack` | `scenes/s1_…md` + `scenes/s2_…md` + their `ref_images/…_seedream.md` | V-1 + V-3 (file presence) + ai_video_compliance scene schema (rule 12.3) | Standard |
| `script_and_shotlist` | `episodes/ep01/script.md` + `episodes/ep01/shotlist.md` | V-1 + V-IC-2 + V-IC-3 (character plant) + V-IC-7 (over-arc plants) + Axis-6 情节链 | Blocker policy |
| `shot_prompt` | one `episodes/ep01/shots/shotNN.md` | V-1 + V-2 (15s atomicity + 动作 sum) + V-4 (schema 14-field) + V-5 (比例 + cover_frame) + V-CV-1/2/4/5/6 (per-character checks) + V-CR-2 (BLACKLIST grep) + Axis-1/2/3/4 (per-shot storyteller) + V-IC-5 (motif if level-up beat) | All blocker. CC-1 priority order applied. Iterate to 0 blockers + ≤ 2 warnings or halt at 3 rounds |
| `episode_full` (closing pass) | the assembled ep01 | All 7 levels run as the final regression gate; cross-shot V-CV-4 / Axis-5/7/8 + V-CR-6 SIGN-OFF + V-IC-7 (over-arc plant rollup) + manual_walkthrough event | Episode-level pass-or-block; emits `validation.requires_manual_walkthrough` before declaring done (ai_video.md rule 8) |
| `publish_pack` | `episodes/ep01/publish.md` | V-1 + V-6 (publish meta) + Axis-1 (title 通俗易懂) | Blocker on missing field or budget |
| `copyright_clearance_seal` | populates `copyright_clearance.md` SIGN-OFF | V-CR-1 + V-CR-2 + V-CR-4 + V-CR-5 + V-CR-6 + V-CR-7 | Critical on any unresolved BLACKLIST hit. Final gate before AC-7 manual walkthrough |

### Audit-event protocol (each work unit)

```
validation.started   { ts, work_unit_id, work_unit_kind, levels: [...], pre_reading_consulted: [{path, sha256}] }
validation.issue.raised { ts, work_unit_id, issue_id, level, severity, location, description, suggested_fix }
validation.pass      { ts, work_unit_id }     # all levels pass
validation.requires_manual_walkthrough { ts, work_unit_id, prompt: "<text>" }  # ai_video.md rule 8
pipeline.halted      { ts, work_unit_id, reason }  # iteration bound trip or critical
```

### Manual walkthrough triggers (ai_video.md rule 8)

After all automated levels pass for `episode_full`, parent emits `validation.requires_manual_walkthrough` with prompt:

> "Open `characters/ref_images/` (preview the 9 立绘 prompts in random order), `episodes/ep01/shotlist.md`, and 2–3 shot prompts in random order — confirm character description matches across shots and the shot list reads as a coherent scene. Then read `episodes/ep01/script.md` end-to-end and confirm: (a) the 0:03–0:30 倒叙 montage face-plants the 6 betrayers visibly enough that ep08-ep60 callbacks will land, (b) the parasitic-cost system弹窗 has the canonical `代价已计算 · 寿元 -N / 修为 +1` form, (c) the cliffhanger 师父 剪影 → 正脸闪一帧 transition reads as a hook (not as a continuity break)."

User confirmation closes the work unit. Per AC-7 this is required before MVP ep01 is declared done.

## Stage-4 sign-off items (surfaced before stage 6)

Workers surfaced 6 items that warrant stage-4 sign-off — none are blockers, but stage 6 inherits them as known-refinements:

| # | Item | Source | Recommended resolution |
|---|---|---|---|
| 1 | § Out of scope #6 wording reads as banning all dialogue text (parenthetical narrowing fixes it but reads awkwardly) | acceptance_criteria worker | Sharpen wording at stage-4 sign-off: explicitly state "v1 visual-only applies to AUDIO synthesis; dialogue text remains a first-class shot field per ai_video.md rule 12.4 三选一". |
| 2 | FR-5 header says "9 files" but enumerates 10 (`裴长砚` archive is 10th) | acceptance_criteria worker | Update FR-5 header count to "10 files (9 active + 1 archive)". |
| 3 | NFR-9b proposed: 弹窗 template byte-identity across episodes | storyteller_dialogue_master worker | Add NFR-9b to spec; sets canonical弹窗 form at ep01 → ep02+ drift = blocker. |
| 4 | `world.md` § 三方势力格局 doesn't currently declare 朝堂 / 太师府 as a non-sect entity (应砚之 dangling) | internal_consistency worker | Stage-6 `world_and_style` work unit extends 三方 → 三方 + 朝堂 political layer (4 categories). |
| 5 | 戚归砚 dual-affiliation (流烛盟 + 忘川教) needs explicit write-up in both `world.md` and `characters/戚归砚.md` | internal_consistency worker | Stage-6 character_bible work unit treats 戚归砚 as the exception: documents both affiliations + the cover-vs-truth tension. |
| 6 | 累计 ledger arithmetic (24 ticks exhausted at ep60) should be a hard target in `characters/裴知秋.md` 累计 ledger field | internal_consistency worker | Stage-6 character_bible: adds a `累计 ledger` row to 裴知秋.md with the 24-tick target. |

## Stage-6 readiness

Stage 6 can begin with the strategy as-is. The 6 sign-off items above are recorded as inherited refinements; stage 6 work units pick them up at the appropriate work_unit_kind. No stage-5 regen required.

## Pre-reading consulted

Recorded in `.audit/adhoc_agents/2026-05-24/xianxia_new-20260524-101931/events.jsonl` as the stage 5 `stage.started` event with `pre_reading_consulted` array of `{path, sha256}` for:

- `.claude/skills/agent_team/playbooks/validation.md`
- `.claude/agent_refs/validation/general.md`
- `.claude/agent_refs/validation/ai_video.md`
- `.claude/agent_refs/project/general.md`
- `.claude/agent_refs/project/ai_video.md`

## Worker spawn audit

| worker | status | confidence | notable |
|---|---|---|---|
| `level-specialist-01-acceptance_criteria` | complete | high | 48 gate checks; 2 stage-4 sign-off items surfaced |
| `level-specialist-02-bdd_scenarios` | complete | high | 8 features; 100% FR rollup; every feature has ≥1 failure scenario |
| `level-specialist-03-ai_video_compliance` | complete | high | Rule-4 → rule-5 reconciliation locked in |
| `level-specialist-04-character_visual_consistency` | complete | high | Pre-cleared 裴知秋 face-mark vs mozun |
| `level-specialist-05-copyright_clearance` | complete | high | ~145 BLACKLIST terms; `万仙盟` flagged as highest-risk |
| `level-specialist-06-storyteller_dialogue_master` | complete | high | Proposed NFR-9b for弹窗 template byte-identity |
| `level-specialist-07-internal_consistency` | complete | high | 3 under-spec'd narrative dependencies surfaced for stage 4 |

Each worker's `prompt.md` + `output.md` lives at `.audit/adhoc_agents/2026-05-24/xianxia_new-20260524-101931/spawns/{worker_id}/`.
