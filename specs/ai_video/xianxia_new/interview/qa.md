# Interview — xianxia_new (working slug)

Run: `xianxia_new-20260524-101931`

## Metadata

- **task_type:** ai_video
- **sub_type:** novel (confirmed Round 1, Q1 — matches mandatory `agent_refs/interview/ai_video.md` rule 1)
- **genre:** 仙侠 (xianxia) — *locked* (Round 1, Q2)
- **task_name (provisional):** `xianxia_new`. Final pinyin slug + Chinese title to be derived in stage 4 from the protagonist's name + central conceit; folder will be renamed at that point.
- **Interview shape:** Shape A (parent-direct generation; categories tight enough not to require fan-out workers).
- **Rounds run:** 1 (of 3 budgeted).

## Categories probed

1. **Sub-type + genre lock** — closes ai_video.md rule 1 (mandatory) + revised_prompt open question 1.
2. **Scale (episode count + per-episode length + stage-4 detail batch)** — closes revised_prompt open questions 2 & 6; drives stage-4/6 scope.
3. **Protagonist archetype + audience tier + viewpoint** — closes revised_prompt open questions 3, 4, 5; sets character bible direction.
4. **Opening hook + system-twist + cultivation system + series-hook strategy** — closes revised_prompt open question 7; drives ep01 design + cross-episode pacing.
5. **Target platforms + stage-3 research priority + trend stance** — closes revised_prompt open question 8; drives stage-3 research angle weighting.

Common probes intentionally skipped (per `interview/general.md` principle 1 — only what's load-bearing):
- **Aspect ratio** — defaults to 9:16 per `agent_refs/project/ai_video.md` rule 7; no signal in the revised prompt to override.
- **Tone / visual references** — deferred to stage 3 character-design research; empty user answer is admitted per ai_video.md rule 2.
- **Cast-size budget** — deferred to stage 4 (more naturally derived once the cultivation faction map exists). Hard ceiling ≤ 5 named characters per episode is set by ai_video.md `sub_type=novel` § 3 (rule for short-drama feasibility).
- **Recurring locations** — deferred to stage 3 baseline-extraction angle (the 14 baseline novels will surface typical recurring locations; we adopt or rework).

## Round 1

### Category 1 — Sub-type + genre lock

**Q1 (sub-type):** novel (60-ep multi-episode short-drama) or short (≤60s)?
- A: **novel (60-ep multi-episode short-drama) (Recommended)** — multi-episode short-drama format. Default 60 eps × ~6–10 clips of ≤15 s. Output layout uses `episodes/epNN/`. Matches stated 'AI 短剧' delivery goal and the spec-driven novel pipeline.

**Q2 (genre lock):** Lock xianxia, switch to xuanhuan, switch to xiuzhen, or defer?
- A: **Lock xianxia (仙侠) (Recommended)** — aligns with the 14-novel baseline corpus under `downloaded_novels/xianxia/`. Genre-fidelity checklist (cultivation realms, sect/loose-cultivator/demonic-faction topology, foreshadow/payoff density) is unambiguous from this lock.

### Category 2 — Scale

**Q3 (episode count):** 60 / 30 / 100+ / 10?
- A: **60 episodes (Recommended)** — `ai_video.md` novel default. Standard 1-season 短剧 length. Each ep 1–2 min → total ~60–120 min of finished video.

**Q4 (per-episode length):** 1–2 min / 3–5 min / 5–8 min?
- A: **1–2 minutes (Recommended)** — 短剧 platform default. Each episode = ~6–10 clips of ≤15 s. Highest paid-conversion density on Douyin / 红果 / Kuaishou 2025–2026.

**Q11 (detail batch size for stage 4):** 3 / 5 / 10 / 60 (all)?
- A: **5 episodes (Recommended)** — ai_video.md default. Stage 4 fully specs ep01–05 (script, shots, prompts); ep06–60 land as one-line synopses in `arc_outline.md`. Later stage-4 regen with `scope=episodes 6..10` extends detail. Tightest feedback loop — render ep01 before committing to ep06+.
- **Override per follow-up 001 (2026-05-24):** **detail batch = 1 (ep01 only)**. User shifted to "fail-fast / iterate per episode" cadence — render ep01, review, learn, then decide whether ep02 enters the next pipeline run. The 60-ep design intent (full reveal cadence, all characters, world, style) stays at design depth; only shot-level production is restricted to ep01 in this run.

### Category 3 — Protagonist + audience + viewpoint

**Q5 (protagonist archetype):** 重生复仇 / 卷王 / 反套路懒人 / 散修登仙?
- A: **重生复仇 (reborn-with-future-knowledge) (Recommended)** — strongest 2025–2026 paid-conversion archetype in xianxia 短剧. Frontloaded payoff (every flashback = immediate revenge / face-slap setup). Baseline contributors to triangulate from: `mozun_chongsheng` (the existing sibling project), `zhen_wen_changsheng`. Differentiator vector: what the protagonist remembers + against whom.

**Q6 (audience tier):** 男频硬核 / 女频 / 全龄?
- A: **男频硬核 (male-skewing, cultivation-grind / face-slap / power-fantasy core) (Recommended)** — matches the 14-book baseline tone. Conversion-tested on Douyin / 红果 xianxia 短剧. Emotional beats: revenge, face-slap, brotherhood, master-protege, treasure-hunt.

**Q7 (viewpoint):** 第三人称跟主角 / 全知 / 第一人称?
- A: **第三人称跟主角 (close third) (Recommended)** — short-drama default. Camera-friendly: every scene either contains the protagonist or is signaled as 'meanwhile elsewhere'. Easiest to storyboard for AI short-drama production.

### Category 4 — Opening hook + system-twist + cultivation + series strategy

**Q8 (ep01 opening hook):** 渡劫失败/被背叛 / 灭门之夜 / 拍⊥成为魔尊 / 拾到神器/系统觉醒?
- A: **拾到神器 / 系统觉醒 (item/system awakens)** — *non-Recommended pick by the user* (recommended was 渡劫失败/被背叛). User combined this hook with the 重生复仇 archetype (Q5) → the rebirth + system-awakens combo. Risk per Round 1 framing: saturated trope unless twisted. Twist captured in Q12.

**Q12 (system twist — Round-1 follow-up to Q8's non-default pick):** parasitic / sentient-with-agenda / stolen / no-twist?
- A: **Hostile / parasitic system (system feeds on user's lifespan or memories) (Recommended)** — strong differentiator. Each level-up costs the protagonist something irrevocable. Built-in suspense engine (when will the cost catch up?). Pairs with reborn-revenge — the system IS the price of the second chance.

**Q9 (cultivation system novelty):** 经典境界 / 反套路 / 全新独创?
- A: **经典境界 (练气-筑基-金丹-元婴-化神-炼虚-合体-大乘) (Recommended)** — standard 8-stage xianxia ladder. Reader muscle memory; clearest 'where am I in the power curve' shorthand for 短剧 audience. Copyright-safe (generic). All 14 baselines use variants.

**Q10 (series hook strategy):** 集集 cliffhanger / 5-ep closed mini-arc / episodic?
- A: **集集 cliffhanger (every episode ends mid-beat) (Recommended)** — 短剧 platform payment standard. Each ep ends on a reveal / sword-mid-swing / 'who is this masked man'. Maximizes paid-conversion. Pairs naturally with 1–2 min format.

### Category 5 — Platforms + research + stance

**Q13 (target platforms — multi-select):**
- A: **抖音 Douyin (Recommended) + 红果短剧 (Recommended) + YouTube Shorts** — 3-platform mix. Note: `视频号 (WeChat Channels)` not selected. YouTube Shorts pick implies an English/SEA-subtitle pass in a future task (out of v1 scope but factor into title/cover design now). Cliffhanger structure works on all three.

**Q14 (stage-3 research priority):** 短剧爆款 / 网文头部 / 抖音+小红书讨论 / AI 短剧赛道范式?
- A: **短剧爆款 — 仙侠 短剧 决策理论 (Recommended)** — recent Douyin/红果 xianxia head titles, their hook structures, paid-conversion case studies, what's flopping. Most directly actionable for our output format (短剧).

**Q15 (trend stance):** 平衡 / 主要跟随 / 主要反向?
- A: **平衡跟随 + 主动反向 (Recommended)** — follow proven beats (cliffhanger cadence, face-slap density, betrayal-then-revenge structure) but explicitly avoid ≥2 saturated tropes (e.g., 'school-uniform demon empress', 'green-tea sister-in-law'). Best of both: paid-conversion stays high; reader fatigue avoided.

## Team consensus

All 5 categories marked clear after 1 round (cap budget: 3).

## Design summary (for stage 3 / 4 reference)

The resulting xianxia 短剧 sits in the **system-rebirth-revenge** subgenre with a **parasitic-cost** twist that turns the genre's usual "level up, get stronger, win" engine into a "level up, lose something, choose what to win". Specifics:

- **Protagonist:** male, mid-late stage cultivator betrayed during 渡劫 or breakthrough in his past life; reborn into early-stage body with a hostile system tied to his rebirth that consumes lifespan/memories per level-up.
- **Central tension:** revenge against past-life betrayers, escalating cultivation, racing the parasitic cost. The parasitic system gives short-drama-friendly continuous stakes (it's always charging).
- **Faction map:** standard xianxia trifecta — 正道 sects / 散修 / 魔门 — with the past-life betrayers seeded across all three (no single faction is "the enemy"; multiple revenge targets cross factions, creating per-episode targets).
- **Cultivation system:** 8-stage classic — 练气、筑基、金丹、元婴、化神、炼虚、合体、大乘. Protagonist returns at 练气 with 大乘-tier knowledge; the suspense is *how much can he execute before the system bills him*.
- **Episode shape:** 60 eps × 1–2 min each, every ep ends on a cliffhanger. Stage-4 spec covers ep01–05 in full; ep06–60 stay at outline level until subsequent stage-4 regen.
- **POV:** close-third, camera follows protagonist.
- **Platform mix:** Douyin + 红果 (primary; CN) + YouTube Shorts (secondary; overseas — subtitle pass deferred).
- **Trend stance:** follow per-ep cliffhanger + face-slap engine + revenge structure (proven); avoid 2+ saturated tropes (to be enumerated in stage-3 trend-research angle output).

## Open items deferred to later stages

| Item | Stage | Notes |
|---|---|---|
| Final Chinese title + pinyin slug | stage 4 | Derived from the protagonist's name + parasitic-system conceit; the spec compilation stage proposes 2–3 candidates and we pick. Triggers a `mv specs/ai_video/xianxia_new/` to the final slug, plus `my_novel/{final_slug}/` + `ai_videos/{final_slug}/` creation at stage 6. |
| Protagonist name + past-life identity + 5–10 betrayer names | stage 3 (character-anonymization angle) → stage 4 character bible | Names must avoid baseline-corpus collision (14 books); checked in stage-5 copyright-clearance validation. |
| Sect names + 魔门 organization names + key faction signatures | stage 3 (baseline-extraction angle) → stage 4 world.md | Cross-novel element matrix flags what to rename. |
| Saturated tropes to actively avoid (≥ 2 per trend stance) | stage 3 (trend-research angle) | Web research surfaces; concrete list lands in `findings/angle-trend_research.md`. |
| Cast-size budget per episode (≤ 5 named) | stage 4 / stage 5 | Hard ceiling set by ai_video.md sub_type=novel rules; per-ep enforcement in stage-5 short-drama-feasibility validator. |
| Recurring scene list for `world.md` + `scenes/` | stage 3 / stage 4 | Stage-3 baseline extraction surfaces canonical xianxia locations; stage-4 spec picks ~6–10 recurring scenes worth locking down per ai_video.md rule 12.3. |
| YouTube Shorts subtitle / cover localization | post-v1 follow-up | Marked in revised_prompt as out-of-scope for this task; will appear as a follow-up after stage 6 ships ep01. |

## Pre-reading consulted

Recorded in `.audit/adhoc_agents/2026-05-24/xianxia_new-20260524-101931/events.jsonl` as the stage's first `stage.started` event with `pre_reading_consulted` array of `{path, sha256}` for:

- `.claude/skills/agent_team/playbooks/interview.md`
- `.claude/agent_refs/interview/general.md`
- `.claude/agent_refs/interview/ai_video.md`
- `.claude/agent_refs/project/general.md`
- `.claude/agent_refs/project/ai_video.md`
