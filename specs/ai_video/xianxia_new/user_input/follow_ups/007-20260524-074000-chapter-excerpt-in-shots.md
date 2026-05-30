---
target_stage: 6
target_artifacts:
  - .claude/agent_refs/project/ai_video.md   # rule 5 v2 → v3 (3-section shot file)
  - specs/ai_video/xianxia_new/final_specs/spec.md   # FR-10 update
  - my_novel/feng_shou_lu/episodes/ep01/prompts/shot*.md   # 7 files, insert excerpt section
severity: medium
---

# Follow-up draft 007 — 2026-05-24 07:40:00 UTC

Summary: 每个 `shotNN.md` 在头部新增 `## Chapter excerpt` section (~200-400 字 from chapter.md §N), 紧接 `## Shot context`. 给 Kling / Seedance 模型同时看到 novel prose detail + 镜头 schema. shot prompt 视频 body 继续聚焦动作 + 角色互动 micro-detail; chapter prose 提供 surrounding mood / 内心 OS / 感官 context.

## 用户原话

> 我們需要把小説跟多細節帶入shot裏，比如顯示小説的描述，然後再shot， shot跟多的是體現動作還有各個角色互動的細節，剩下的描述小説跟家詳細

## 用户意图

「shot prompt 现在只有 schema (角色 / 场景 / 镜头 / 动作 / etc.), AI 看到的世界缺乏 prose mood. chapter.md 已 ship 高密度小说篇章 (~10,943 字). 把 chapter 对应该 shot 的 200-400 字 inline 引入 shot prompt, AI 同时看到 (a) 小说叙述描述 (用于环境 mood / 内心 OS / 感官 anchor) + (b) shot schema (用于动作精确 timing / 角色互动 micro-detail). shot prompt 视频 body 继续聚焦 action + interaction, prose 段填补 surrounding context.」

## 改动 1: agent_refs/project/ai_video.md rule 5 v2 → v3

每个 `shotNN.md` 文件结构改为 **3 段式** (post-007 v3):

1. **`## Chapter excerpt`** (新) — 从 `chapter.md` 对应 §N 段截取的 200-400 字 novel prose. inline 引用 (块引用 `>` 或直接段落). 用以给 AI 模型 + 人类 review 提供 surrounding mood / 内心 OS / 感官 anchor 的完整 prose context.
2. **`## Shot context`** — Summary / Characters / Scene / Duration / Reference uploads checklist (unchanged from v2).
3. **`## 视频 prompt`** — fenced ```text``` 12-field schema (per rule 12.4 v2 post-003) — unchanged.

prose 段不在 fenced ```text``` block 内, 不被 AI 模型当成 prompt 输入 (取决于 Kling / Seedance 的 markdown 解析行为). 但人类 review 时, prose + shot schema 并列, review 体验改善.

## 改动 2: 视频 prompt body 内容微调

video prompt body 继续聚焦 14-字段 schema 中的「动作 timed beats + 角色 micro-detail」, 不需要把 chapter prose 内的 mood / 感官 / 内心 OS 全部 inline (会超字数上限 + 与 prose section 冗余). 视频 prompt 与 chapter prose 是 **互补关系**:

- chapter prose: 完整叙述 + mood + 内心 OS + 感官. 给人类读者 + AI 模型作 surrounding context.
- 视频 prompt: 精确动作 + 角色互动 + face-mark / 一句话锁定 / 标志台词 / 寄生 motif 等 byte-identical 锚. 给 AI 视频模型作渲染指令.

## 改动 3: 项目层落地 (ep01 7 shots)

每个 shot 对应的 chapter §N 段映射:

| shot | chapter section | excerpt 字数 |
|---|---|---|
| shot01 渡劫死亡 | §1 渡劫之夜 | ~300 字 |
| shot02 montage 上半 (卫/应/戚) | §2 前 3 vignettes | ~300 字 |
| shot03 montage 下半 (池/阮/言 + 容漪) | §2 后 3 vignettes + 容漪 cameo 段 | ~300 字 |
| shot04 童身渊底苏醒 | §3 part 1 (苏醒段) | ~300 字 |
| shot05 罗盘 + motif | §3 part 2 (motif 五拍段) | ~400 字 (motif 较密) |
| shot06 自取新名 | §4 水面上的「知秋」二字 | ~300 字 |
| shot07 cliffhanger | §5 渊口那道剪影 | ~400 字 (cliff 较密) |

excerpt 选取原则: 直接 quote chapter 段中**最直接对应该 shot 视觉的 prose**, 不重写不浓缩. 块引用格式 `> ...`. Chapter prose 与 shot 视觉 1-to-1 对齐.

## 改动 4: spec.md FR-10 update

FR-10 改为 3-section schema (chapter excerpt + shot context + 视频 prompt). chapter excerpt 段是 episode 内 cross-reference 锚点, 不要求 byte-identical (chapter 是 source-of-truth, excerpt 只是 quote section).

## 改动 5: 下游 walk

- agent_refs/project/ai_video.md rule 5 v2 → v3 + rule 12.4 v2 schema 描述补充 (chapter excerpt section 在 shot 文件最前).
- spec.md FR-10 update.
- 7 shot prompts (shot01-shot07) 插入 `## Chapter excerpt` section.
- ep02+ 后续 episode shot prompts 默认 3-段式. agent_refs 的 update 已确保 future writers 默认走 v3.

## Out of scope

- 不重写 chapter.md (已 ship).
- 不重写 视频 prompt body (chapter prose 不挤入视频 prompt 内, 是 sibling 段, 不重叠).
- shotlist.md / script.md / publish.md 不动 (chapter excerpt 仅在 shot prompt 层).

## Acceptance

- 7 shot prompts 全部含 `## Chapter excerpt` section, 各 200-400 字 from chapter §N.
- agent_refs/project/ai_video.md rule 5 已修订为 v3 (3-section).
- spec.md FR-10 已 update.
- changelog.md 已追加.
