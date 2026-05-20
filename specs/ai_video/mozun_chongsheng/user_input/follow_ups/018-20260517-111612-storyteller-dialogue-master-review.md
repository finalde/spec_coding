# Follow-up draft 018 — 2026-05-17
Add a "短剧故事 + 台词大师" review role to the spec-driven workflow and apply its review pass to every shot already authored under `ai_videos/mozun_chongsheng/episodes/`.

## Intent

Every shot / episode / shotlist item the workflow emits should pass a storyteller-dialogue master review before being marked done. The master enforces two contracts:

1. **Dialogue** is 通俗易懂 (modern colloquial, understandable to any 抖音/快手 viewer in one hearing), 信息量大 (advances plot or stake), 节奏紧凑 (memorable / branded lines ≤ 7 字 where appropriate), 角色声口正确 (matches the character's 锁定描述符), 反转密度足够 (each shot lands at least one turn or reveal).
2. **Shot design** lands every named hook (黄金钩 / 反转 / cliff) within its declared seconds, is a non-removable beat in the episode's plot chain, has no anachronistic forward-references to later-arc characters, and avoids near-duplicate phrasing between two characters' threats within the same episode.

## Where this lives in the workflow

- **Common-level rules (not project-specific)** added in this same turn to:
  - `.claude/agent_refs/validation/ai_video.md` — new validation level **#9 — 短剧故事 + 台词大师**: the spec lists the criteria the level enforces and the severity table for failures.
  - `.claude/agent_refs/project/ai_video.md` — new section **§12.4-D 短剧故事 + 台词大师 review criteria**: the D1–D6 dialogue table + S1–S5 shot-design table + the master's output format (per-shot inline patch list, not prose review).
- **Project-scoped action (this follow-up)** = run the master pass against the current 50 shots under `ai_videos/mozun_chongsheng/episodes/ep01..ep05/prompts/shotNN/shotNN.md` and surgically patch the lines / shots that fail the criteria.

## Specific issues identified in the existing 50 shots (audit done in the same turn)

- **ep01/shot03** — 方鼎元 line "魔尊沧冥，今日便是你的劫数。" mirrors ep01/shot02 沧冥 "今日，便是你们的死期。" too closely (S5 duplication). 方鼎元 should speak with 太清掌教 piety/ceremony register (D4).
- **ep01/shot04** — 白月清 line "璃月，为师所行皆为道。" forward-references 苏璃月 who only enters the story ep14+ (S3 anachronism — `characters/c3_苏璃月` is not in ep01-ep05 cast). Replace with an in-scope target.
- **ep02 / ep03 / ep04** — most lines already pass the criteria; the master will do a per-line pass anyway and produce inline patches where needed.
- **ep05** dialogue is mostly minimal (default-mode + ceremony lines for the cliff) and already passes.

## Out of scope

- Re-authoring the 50 shots' plot. The master tweaks lines and shot-design metadata in-place; it does not redirect the story.
- Renaming character files, sect names, or hook structure. The audit is line-level + shot-design-level only.
- Walking back any of the prior follow-ups (016 scene stubs, 017 scene ref, etc.). They remain authoritative inputs.

## Audit deliverable (this turn)

Surgical edits applied to the failing shot mds (each edit changes only the failing 台词 line or the affected 动作 / 镜头 fragment). The audit findings live in this follow-up file as the patch list; the shot mds themselves carry the new line without a comment marker (per the master's "patches not prose" output convention in §12.4-D).
