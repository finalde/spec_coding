---
target_stage: 6
target_artifacts:
  - .claude/agent_refs/project/ai_video.md
  - ai_videos/nvdi_tuihun_houhuile/characters/c1_陈凡/c1_陈凡.md
  - ai_videos/nvdi_tuihun_houhuile/characters/c3_陈国公/c3_陈国公.md
  - ai_videos/nvdi_tuihun_houhuile/characters/c4_太监/c4_太监.md
  - ai_videos/nvdi_tuihun_houhuile/episodes/ep01/shots/
severity: high
---

# Follow-up draft 001 — 2026-05-24

Two intertwined items from the same conversation turn:

## 1. 演员参考照片解读契约 (Actor photo directive)

User-stated rule:

> 我上传的演员照片是没有化妆，带过假发的，短剧任务需要根据角色需要装扮，化妆，戴假发，不要完全按找演员照片来。

**Abstracted intent** (this becomes a common-level rule, applies to every ai_video project, not just nvdi_tuihun_houhuile):

When user uploads actor reference photos to AI video models (Kling / Seedance / Sora / Veo / Runway) as character face/build ground truth, the photo is **素颜 + 戴现成假发** (the actor's daily / 试镜 state), NOT the character's final look. The AI model MUST treat the photo as face anchor only — 五官 / 脸型 / 体型 / 真人皮肤质感 / 年龄观感 取自照片; 装扮 / 化妆 / 假发款式 / 发色 / 服装 / 道具 / 神情 / 气质 strictly per prompt body's character设定. 不要 carry 演员日常素颜 / 现成短假发 / 现代发型 / T-shirt 等 modern 元素入画.

**Reason this is a contract, not a hint:** 短剧 actor pools typically have one actor per multiple roles. If the directive is implicit, model defaults to carrying the photo's actual look — every character ends up looking like "the same person with default short wig and bare face", losing character differentiation across the drama.

## 2. `prompts/` → `shots/` rename (project-scoped)

User edited both `ai_videos/feng_shou_lu/README.md` and `ai_videos/nvdi_tuihun_houhuile/README.md` so the per-shot folder is named `shots/` instead of canonical `prompts/`. Both existing ai_video projects now use `shots/`. The canonical rule in `agent_refs/project/ai_video.md` (rule #2 v3 layout diagram lines 45-51 + rule #12.9 layout lines 1174-1180) still says `prompts/` — this is a known drift that may want to be promoted to canonical in a future follow-up. For now, keep project-scoped: rename `ai_videos/nvdi_tuihun_houhuile/episodes/ep01/prompts/` → `shots/` to match the user's README, patch refs in raw_prompt.md.

## Scope of this follow-up

- (a) **Common-level rule update**: Add new sub-rule `12.5-A 演员参考照片解读契约` to `.claude/agent_refs/project/ai_video.md`, inserted before rule 12.6. New contract paragraph 必须 byte-identical re-paste in every character's turntable prompt body 在 `主体:` 行下方一行。
- (b) **Project rename**: `ai_videos/nvdi_tuihun_houhuile/episodes/ep01/prompts/` → `shots/` (already done by user); patch `specs/.../raw_prompt.md` reference accordingly.
- (c) **Project character bibles**: Apply directive to c1_陈凡 / c3_陈国公 / c4_太监 turntable prompts (skip c2_女帝 — placeholder, no turntable prompt yet). Each gets the byte-identical contract paragraph + a per-character 装扮锚 line listing concrete deviations from typical actor photo (古装束发 vs 现代发型, 是否有须 / 假发款式 / 装扮 vs 素颜).

## Open question (defer)

Should `prompts/` → `shots/` be promoted to canonical in `agent_refs/project/ai_video.md` rule #2 + rule #12.9? Both existing ai_video projects (feng_shou_lu + nvdi_tuihun_houhuile) now use `shots/`. Recommendation: yes, but ask user in next follow-up rather than silently propagating.
