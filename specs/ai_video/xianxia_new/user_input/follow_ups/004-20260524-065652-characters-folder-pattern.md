---
target_stage: 6
target_artifacts:
  - .claude/agent_refs/project/ai_video.md
  - specs/ai_video/xianxia_new/final_specs/spec.md
  - my_novel/feng_shou_lu/README.md
  - my_novel/feng_shou_lu/characters/*.md       # MOVE to characters/{name}/{name}.md
  - my_novel/feng_shou_lu/episodes/ep01/prompts/shot*.md   # PATCH path references
severity: high
---

# Follow-up draft 004 — 2026-05-24 06:56:52 UTC

Summary: characters/ 改为 **folder-per-character** pattern. 每角色 1 个 `characters/{中文名}/` 文件夹 + 主 bible 文件 `characters/{中文名}/{中文名}.md`. 文件夹内允许 sibling 文件 (按角色复杂度按需添加 — dual-state turntable / 单独 Seedream 立绘 / 配音参考详档 / etc.). v3 single-file pattern 被 v4 folder pattern 取代.

## 用户原话

> and for charactors, there should be a folder istead of 1 md file only, please note this down in your spec driven framework

## 用户意图抽象

「v3 把 bible + turntable 塞到单文件已经达到上限了 — 双形态主角 (裴知秋) 在单文件里堆 2 套锁定描述符 + 2 个 turntable + 各自 5-row 配音表 = ~700 行, 难以 review. 单文件还把所有未来可能的 character-level 资产 (额外 Seedream 立绘 / 单独配音参考 / 等) 都挤压到一个文件. 给每角色一个文件夹, 主 bible 文件保留为入口, 但允许按需 split sibling 文件. 这是 v3 单文件 collapse 的反向 expand. 此 follow-up 与 003 (scenes 单文件 + seam-frame 废止) 是 *同一 turn 的连贯简化思路*: 把 single-source-of-truth 放在对应的 folder/file 的 *合理* 粒度上 — scenes 一个文件就够 (≤ 100 行); characters 给一个文件夹 (灵活 expand 到多文件).」

## 改动 1: agent_refs/project/ai_video.md rule 12.5 v3 → v4

- `characters/ref_images/` global 子目录 abolished (v3 已 abolish, v4 保持 abolished 状态 — 角色专属 ref 资产归并到 `characters/{中文名}/` 文件夹下).
- `characters/{中文名}/` folder per character (mandatory).
- `characters/{中文名}/{中文名}.md` 主 bible 文件 (mandatory, 入口文件, 含 rule #12.1 bible 全段 + 默认 turntable prompt).
- Optional sibling files inside folder (按需添加, stage-6 validator 不强制要求 sibling 文件存在):
  - `state_a_turntable.md` / `state_b_turntable.md` — dual-state 角色单独 turntable.
  - `state_a_seedream.md` / `state_b_seedream.md` — dual-state Seedream 立绘 prompt.
  - `dual_affiliation_cover.md` / `dual_affiliation_truth.md` — dual-affiliation 角色 (戚归砚) 双层视觉档案.
  - `{anything}.md` — 角色专属补充片段.

## 改动 2: Cross-reference path 更新 (xianxia_new feng_shou_lu)

所有引用 `characters/{中文名}.md` 的 cross-doc 路径改为 `characters/{中文名}/{中文名}.md`. 影响:

- 7 shot prompts (shot01-shot07) Reference uploads checklist 中的角色 reference 路径
- my_novel/feng_shou_lu/README.md 角色清单段 (隐性引用)
- script.md 角色出场段 (如有路径引用)

## 改动 3: 项目层落地

```bash
cd my_novel/feng_shou_lu/characters
for c in 裴知秋 裴长砚 闻砚清 容漪 阮瑶 卫长烛 应砚之 戚归砚 池洇 阮惘 言息; do
  mkdir -p "$c"
  git mv "$c.md" "$c/$c.md"
done
```

11 角色文件全部从 `characters/{中文名}.md` 移到 `characters/{中文名}/{中文名}.md`.

## v3 → v4 演进 rationale

v3 单文件 trade-off: 收 — 跨文件依赖少, 入口直接; 失 — 大文件难 review, 角色资产堆叠.

v4 folder trade-off: 收 — 文件粒度合理, 允许角色专属资产按需 split; 失 — 需要遵守 `{name}/{name}.md` 作主入口的约定, 多了一层目录.

用户判定 v4 收益 > 失. v4 supersedes v3.

## Out of scope

- 此 follow-up 不动 scenes pattern (scenes 仍是 single-file per follow-up 003).
- 此 follow-up 不强制 sibling 文件 split — 现 11 角色仍以 `{name}/{name}.md` 主 bible 单文件落地; sibling 文件 (state-A/B 单独 turntable / 单独 Seedream 立绘 / 等) 按用户后续 follow-up 按需添加.
- mozun_chongsheng 项目按 v3 既有状态保留, 不追溯改造为 v4.

## Acceptance

- `.claude/agent_refs/project/ai_video.md` rule 12.5 已 修订为 v4 (folder pattern) + 加 follow-up 004 origin note.
- `my_novel/feng_shou_lu/characters/{中文名}.md` × 11 → `my_novel/feng_shou_lu/characters/{中文名}/{中文名}.md` × 11 (folder + 主 bible 文件).
- 7 shot prompts 中的角色 reference 路径已替换为 `characters/{中文名}/{中文名}.md`.
- `my_novel/feng_shou_lu/README.md` 已修补 (角色清单段路径 / 使用说明段 item 5 — 「characters/{name}.md」 → 「characters/{name}/{name}.md」).
- `specs/ai_video/xianxia_new/final_specs/spec.md` 已修补 (FR-5 文件清单段路径).
- `specs/ai_video/xianxia_new/changelog.md` 已追加 follow-up 004 条目.
