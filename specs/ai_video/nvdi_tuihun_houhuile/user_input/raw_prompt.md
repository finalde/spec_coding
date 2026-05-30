# Raw prompt — nvdi_tuihun_houhuile (女帝退婚后悔了)

Source: 2026-05-24 conversation. User chose lightweight incremental authoring (NOT the full agent_team 6-stage pipeline) because they want to co-generate the drama beat-by-beat rather than front-load interview/research/spec/validation.

## Project intent

- **Title (Chinese):** 女帝退婚后悔了
- **task_name:** `nvdi_tuihun_houhuile` (pinyin per rule #1, user chose `nv-` over `nu-`)
- **task_type:** `ai_video`
- **sub_type:** `novel` (multi-episode short drama, user said "先放一个 episode" implying more to come)
- **Genre:** 古风 / 装废逆袭 / 女帝重逢悔婚 / 男频爽文
- **Core trope:** 男主陈凡（陈国公府三公子）被女帝退婚，外人看是被嫌弃的纨绔，实际是装废多年的隐藏强者，重获自由后开启逆袭。题目"退婚后悔了"暗示女帝后期将悔婚回头，男主已不愿。

## Provided seed (ep01 opening dialogue)

太监：奉天承运，女帝诏曰，陈国公府三公子陈凡，纨绔放荡，不学无术，得不配位，今解除朕与其之婚约，钦此。
陈凡（内心独白）：5 年了终于解脱了，美好生活要来了。
太监：陈凡，接旨吧。
陈凡：陈凡接旨，谢主隆恩。
太监：哼，陈国公，因为令郎，女帝很不开心，该怎么做，就不用老奴说了吧。
陈国公：老臣明白，老陈一定亲自进京请罪。

User-confirmed setting (this conversation): 陈国公府正厅（太监携旨上门宣读，非朝堂）。

## Authoring approach

- Light-touch spec-driven. Skip full stage-2 interview / stage-3 research / stage-5 validation strategy generation for now; just minimum stage-1 (this file) + stage-4 (rolling `final_specs/spec.md` updated as the drama grows).
- Stage 6 (execution) drives the conversation: episode → script → shotlist → shot prompts, one beat at a time, user reviewing each.
- If the drama grows large or starts repeating mistakes, escalate to full agent_team pipeline retroactively.

## Layout (rule 12.8 v2 + rule #2 v3 novel sub_type)

```
ai_videos/nvdi_tuihun_houhuile/
├── README.md             # Chinese, 项目概要 + 使用说明 + 角色清单 + 风格关键词
├── world.md              # 世界观 (生长中, ep01 仅最小骨架)
├── style_guide.md        # 风格指南 (生长中)
├── arc_outline.md        # 全集大纲 (ep01 only for now)
├── characters/
│   ├── c1_陈凡/c1_陈凡.md            # ML, 男主 (双层人格 装废 + 真实强者)
│   ├── c2_女帝/c2_女帝.md            # FL, 主女主 (ep01 仅诏书提及, 未出场)
│   ├── c3_陈国公/c3_陈国公.md         # 男主父亲
│   └── c4_太监/c4_太监.md             # 配角, 宣旨太监
├── scenes/
│   └── s1_陈国公府正厅/s1_陈国公府正厅.md
└── episodes/
    └── ep01/
        ├── script.md     # 接旨 scene 全本对话 + 动作 + 内心 OS
        ├── shotlist.md   # ~6 shots, 3-15s each
        └── shots/
            └── shotNN/shotNN.md # 按 rule #5 v3 + rule #12.6 v2 schema (folder-per-asset per rule 12.9; canonical `shots/` per ai_video.md rule #2 v3 post xianxia_new/011)
```

`my_novel/nvdi_tuihun_houhuile/` reader-side novel prose pipeline (rule #2 v3) deferred for now — there is no novel prose source. If we decide to back-fill chapter prose later, add it then.

## Open questions (capture, do not block)

- 男主修为体系（武修 / 仙修 / 系统）？— defer to when ep01 内心独白触及。
- 女帝设定（年龄 / 段位 / 朝堂权势）？— defer to女帝实出场集。
- 退婚后陈凡的下一步（出走 / 表面顺从 / 立刻被父亲杖责）？— 决定 ep02 走向。
