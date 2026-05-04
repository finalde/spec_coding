# Interview refs — `task_type=ai_video`

Institutional memory loaded when the current task has `task_type=ai_video`. Layered on top of `general.md` in this same folder; per-task-type rules win when they conflict.

Stage 2 for ai_video tasks always starts with a sub-type fork; everything else hangs off that answer.

## 1. Mandatory first question — `sub_type`

The parent's first multi-choice question is always:

> Is this a multi-episode 短剧/novel project, or a single short-video project?
>
> - `novel` — multi-episode, default 60 eps × ~6–10 clips × ≤15 s each. Output layout has `episodes/epNN/`.
> - `short` — single-piece short, flat layout. Length target ≤60 s.

The parent picks the Recommended option from the revised prompt; if genuinely ambiguous, default Recommended to `short` (smaller commitment). Capture as `sub_type ∈ {novel, short}` in `qa.md` metadata. Every later probe and every stage-6 layout choice keys on this answer.

## 2. Common probe categories (both sub-types)

Always relevant; the parent can merge or skip per `general.md` principle 1, but should not invent canned alternatives.

- **Target platform** — Douyin / 快手 / YouTube Shorts / 视频号 (multi-select OK; drives platform-conventions research angle).
- **Cast size** — main characters + named supporting characters. Drives the Seedream ref-image budget and the character-design research angle.
- **Tone / visual references** — links or descriptors of comparable existing videos. Empty answer is allowed but flagged so research stage knows the visual direction comes from genre conventions only.
- **Aspect ratio** — confirm 9:16 default; ask only if the prompt suggests otherwise.
- **Genre** — captured per project. Refs are genre-agnostic by decision; do NOT pre-suggest a genre house-style.

## 3. Novel-only probes

Asked only when `sub_type=novel`:

- **Episode count** — default 60.
- **Per-episode length** — default 1–2 min (短剧 format), driving ~6–10 ≤15 s clips per episode.
- **Detail batch size** — how many episodes get full-detail spec at stage 4. Default 5; remaining episodes stay at one-line skeleton until the user runs a stage-4 regen for the next batch.
- **Series hook strategy** — cliffhanger / open-arc-with-weekly-resolution / episodic.
- **Recurring locations** — drives `world.md` depth.

## 4. Short-only probes

Asked only when `sub_type=short`:

- **Hook style** — opening 3-second pattern (question / shocking-image / on-screen-text-overlay / character-action).
- **Single-scene vs multi-scene** — drives shot-count budget.
- **Length target** — ≤60 s default; explicit override allowed up to ~90 s.
- **Payoff structure** — punchline / reveal / loop-back-to-hook / setup-without-resolution (cliffhanger short).

## 5. AUTONOMOUS-mode pre-fills

When `# EXECUTION MODE: AUTONOMOUS`, pre-answer every probe with best judgment + inline annotation per `general.md` principle 5.

| Probe | Default | Annotation source |
|---|---|---|
| `sub_type` | inferred from revised prompt; `short` if ambiguous | (judgment call — single-prompt requests are usually shorts) |
| platform | Douyin + YouTube Shorts | (judgment call — bilingual reach) |
| aspect ratio | 9:16 | matches `agent_refs/project/ai_video.md` rule 7 |
| prompt language | Chinese | matches `agent_refs/project/ai_video.md` rule 5 |
| (novel) episode count | 60 | matches sub-type contract |
| (novel) per-ep length | 1–2 min | matches 短剧 format default |
| (novel) detail batch | 5 | matches stage-4 incremental spec strategy |
| (short) length target | ≤60 s | matches platform conventions |
| (short) hook style | character-action | (judgment call — most general-purpose hook) |

## Update protocol

Surgical: one new probe / default per lesson. Cite source run id.
