---
target_stage: 6
target_artifacts:
  - .claude/agent_refs/project/ai_video.md   # rule 12.5 v4 → v5 hybrid folder pattern
  - specs/ai_video/xianxia_new/final_specs/spec.md   # FR-5 file paths
  - my_novel/feng_shou_lu/characters/*/  # RENAME 11 folders to c{N}_{pinyin}/
  - ai_videos/feng_shou_lu/characters/*/  # SYNC rename mirror
  - my_novel/feng_shou_lu/episodes/ep01/prompts/shot*.md   # path references
  - my_novel/feng_shou_lu/README.md
severity: high
---

# Follow-up draft 008 — 2026-05-24 07:40:00 UTC

Summary: 11 character folder 重命名为 `c{N}_{pinyin_slug}/` (webapp-compatible) + 内部 bible 文件名保留 Chinese `{中文名}.md`. Fix: ai_video_management webapp casting feature 无法 assign actor 因 dropdown 空 (`apps/ui/src/lib/dramas.ts:22` 用 `/^c\d+(_.*)?$/` 过滤 character folders; backend `_CHARACTER_DIR_RE` 同正则). v4 folder pattern (纯 Chinese 名) 无法通过过滤. v5 hybrid (c-prefix folder + 中文 bible 文件) 解决 webapp 兼容性同时保留 cross-doc 中文 readability.

## 用户原话

> 還有我需要你fix assign actor to charactor,現在無法assign

## 用户意图

「webapp casting UI 现在 assign 不了 — 我点 actor 然后选 character 时 dropdown 空. 修好.」

## 根因

webapp 两处过滤强制 character folder 名匹配 `^c\d+(_.*)?$`:

- frontend: `apps/ui/src/lib/dramas.ts:22` — `extractDramas()` 只把匹配 `c{N}_{slug}` 的 folder 加入 dropdown 选项.
- backend: `libs/infrastructure/writers/character_video__writer.py:63` `_CHARACTER_DIR_RE`, 用于 shot prompt 解析 + 校验.

follow-up 004 选了纯中文 folder 名 (`characters/裴知秋/`). 不匹配 c-prefix 正则, dropdown 空 → 无法 assign.

## 改动 1: agent_refs/project/ai_video.md rule 12.5 v4 → v5 (hybrid)

新 folder 命名规则:

- folder 名: `c{N:02d}_{pinyin_slug}/` (webapp `^c\d+(_.*)?$` 兼容; NN 零填 2 位; pinyin 全小写下划线分隔).
- 文件名 inside folder: `{中文名}.md` (主 bible 文件名保留 Chinese for cross-doc readability + grep friendliness).
- 编号约定: 按 ep01 出场顺序 + 角色重要性 manually assign — 主角 + 前世 + 师父 + 主女主 + 童年姐姐 + 6 betrayers = c01-c11.

11-角色 mapping (xianxia_new feng_shou_lu):

| c{N} | 中文名 | pinyin slug | 新 folder |
|---|---|---|---|
| c01 | 裴知秋 | pei_zhi_qiu | `c01_pei_zhi_qiu/裴知秋.md` |
| c02 | 裴长砚 | pei_chang_yan | `c02_pei_chang_yan/裴长砚.md` |
| c03 | 闻砚清 | wen_yan_qing | `c03_wen_yan_qing/闻砚清.md` |
| c04 | 容漪 | rong_yi | `c04_rong_yi/容漪.md` |
| c05 | 阮瑶 | ruan_yao | `c05_ruan_yao/阮瑶.md` |
| c06 | 卫长烛 | wei_chang_zhu | `c06_wei_chang_zhu/卫长烛.md` |
| c07 | 应砚之 | ying_yan_zhi | `c07_ying_yan_zhi/应砚之.md` |
| c08 | 戚归砚 | qi_gui_yan | `c08_qi_gui_yan/戚归砚.md` |
| c09 | 池洇 | chi_yin | `c09_chi_yin/池洇.md` |
| c10 | 阮惘 | ruan_wang | `c10_ruan_wang/阮惘.md` |
| c11 | 言息 | yan_xi | `c11_yan_xi/言息.md` |

## 改动 2: cross-doc path reference 更新

- 7 shot prompts (shot01-shot07) Reference uploads checklist 中 `characters/{中文名}/{中文名}.md` → `characters/c{N}_{pinyin}/{中文名}.md`.
- README.md item 5 同步更新.
- spec.md FR-5 11-row table 同步更新.

## 改动 3: ai_videos/ mirror sync

`ai_videos/feng_shou_lu/characters/` 端 11 folder 同步重命名 (mv 11 个旧名 → 新 c-prefix 名).

## v4 → v5 rationale

v4 选了纯中文 folder 名以达成「user-facing readability」. 实际上 webapp 的 dropdown / shot-concat / casting feature 全部依赖 c-prefix folder 正则; 纯中文 folder 不被 enumerable.

v5 hybrid 兼顾两者:
- folder 名 c-prefix → webapp 兼容
- 文件名内部中文 → cross-doc grep + 人类 readability + script 中 row #10 一句话锁定 仍 byte-identical

主要 trade-off: cross-doc path 引用从 `characters/{name}/{name}.md` (短) → `characters/c01_pei_zhi_qiu/裴知秋.md` (略长). 但 path 仍 readable, 不影响 byte-identical 锁定 (锁定串本身仍是 row #10 中文).

## 改动 4: 不修改 webapp 正则

我们 *不* 改动 webapp 的 `_CHARACTER_DIR_RE` 或 `dramas.ts:22` 正则 — 一方面这是 ai_video_management 项目的 contract, 改动需要单独 spec_driven follow-up; 另一方面 mozun_chongsheng 项目已经按 c-prefix 工作, 改正则会破坏既有项目 path 引用. 选择重命名我们的 folder 比修改 webapp 更小风险.

## Out of scope

- 不重命名 character bible 文件本身的内容 (bible body 内 angle 引用 / cross-doc reference 不动).
- 不动 mozun_chongsheng 项目 (它已经 c-prefix).
- 不修改 webapp Python / TypeScript 代码.
- 不动 scenes/ (scene file 是单文件 ID 化场景 token 已是 s{N}_xxx pattern, 与 c-prefix 同结构, webapp 兼容).

## Acceptance

- `my_novel/feng_shou_lu/characters/c{N}_{pinyin}/{中文名}.md` × 11 已存在.
- `ai_videos/feng_shou_lu/characters/c{N}_{pinyin}/{中文名}.md` × 11 sync mirror 已存在.
- 7 shot prompts 中 `characters/{中文名}/{中文名}.md` 全部替换为 `characters/c{N}_{pinyin}/{中文名}.md`.
- README.md item 5 + spec.md FR-5 + agent_refs rule 12.5 (v4 → v5) + revised_prompt.md + changelog.md 已修补.
- webapp casting UI dropdown 弹出 11 个 c{N}_{pinyin} 选项, 用户可 assign actor.

## 验证

```bash
ls /c/workspace/spec_coding/ai_videos/feng_shou_lu/characters/
# expect: c01_pei_zhi_qiu c02_pei_chang_yan ... c11_yan_xi
```
