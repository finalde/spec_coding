---
target_stage: 6
target_artifacts:
  - .claude/agent_refs/project/ai_video.md
  - specs/ai_video/xianxia_new/final_specs/spec.md
  - specs/ai_video/xianxia_new/validation/strategy.md
  - my_novel/feng_shou_lu/README.md
  - my_novel/feng_shou_lu/scenes/s1_无寿崖.md
  - my_novel/feng_shou_lu/scenes/s2_落雁渊.md
  - my_novel/feng_shou_lu/scenes/ref_images/  # DELETE
  - my_novel/feng_shou_lu/episodes/ep01/prompts/shot01.md
  - my_novel/feng_shou_lu/episodes/ep01/prompts/shot02.md
  - my_novel/feng_shou_lu/episodes/ep01/prompts/shot03.md
  - my_novel/feng_shou_lu/episodes/ep01/prompts/shot04.md
  - my_novel/feng_shou_lu/episodes/ep01/prompts/shot05.md
  - my_novel/feng_shou_lu/episodes/ep01/prompts/shot06.md
  - my_novel/feng_shou_lu/episodes/ep01/prompts/shot07.md
severity: high
---

# Follow-up draft 003 — 2026-05-24 06:56:52 UTC

Summary: 两个简化 pipeline 的硬契约改动 (一并落地):
1. **scenes/ref_images/ 子目录全面废止** — mirror 角色单文件 pattern (rule 12.5 v3 已对 characters/ref_images/ 做过同样废止). 每场景 1 个且仅 1 个 `scenes/{name}.md` 文件, Seedream 立绘 prompt 作为「---」分隔的第二段嵌入同一文件.
2. **shot prompts 中 startframe / lastframe Seedream 静帧 prompt 嵌入块全面废止** — rule 5 的「三段式 shotNN.md」(Shot context + 视频 prompt + Seam-frame still prompts) 收缩为「二段式」(Shot context + 视频 prompt). rule 11 整个 seam-frame still-image pipeline 标记 abolished. 后续 Kling / Seedance 跨 shot 续接依赖描述层连续性 (相同的角色一句话锁定 + 场景一句话锁定 + 光线/色调 + 渲染样式 / 负向 verbatim) 与视频模型自身的 turntable mp4 + 场景 PNG reference, 不再依赖 Seedream PNG 静帧锁帧.

## 用户原话

> for fenshoulu, under scenes, remove the concept of ref_images, there should be 1 and only 1 md files for a given scene
>
> also please make sure you note this down in your spec driven workflow, remove all ref_images related instructions
>
> under shorts remove startframe and end frame prompt please, also remove related instruction from the spec driven

(「shorts」按上下文判定为「shots」typo: 用户在 ep01/prompts/shotNN.md 中已经看到 startframe / lastframe Seedream 嵌入块, 要求移除. 与 scenes/ref_images/ 废止 同属「简化 PNG 资产 pipeline」连贯主线.)

## 用户意图抽象

「我不希望 pipeline 强制产出多余的 Seedream PNG 静帧资产 — 角色 turntable mp4 + 场景 single-file 立绘已经够支撑 Kling/Seedance 视频生成, 多余的 seam-frame PNG 步骤增加渲染时间 / API 成本 / asset 管理负担, 而不带来与描述层连续性等价的额外价值. 简化到底.」

## 改动 1: scenes/ref_images/ 全面废止 — 单文件 scene pattern

### 跨项目 rule 改动 (common-level)

`.claude/agent_refs/project/ai_video.md` rule 12.3 修订:

- **废止**: `scenes/ref_images/{scene}_seedream.md` 单独文件路径.
- **新增**: 每场景 1 个且仅 1 个 `scenes/{scene}.md` 文件. Seedream 立绘 prompt 作为「---」分隔的第二段嵌入同一文件, 类似 rule 12.5 v3 character 单文件 pattern.
- **文件结构** (per 12.3 v2):

  ````markdown
  ---
  worker_id: ...
  stage: ...
  ...
  ---

  # {scene-name}

  ## 场景定位
  ...

  ## 锁定描述符（8 字段, 跨集 byte-identical）
  ...

  ## 关键变化态
  ...

  ## 出现镜头
  ...

  ## 负向
  ...

  ---

  # Seedream 立绘 prompt — {scene-name}

  参考: scenes/{scene-name}.md
  画幅: 9:16 竖屏 / 4K 原生分辨率
  默认光影态: {variant}

  ## Prompt

  【场景立绘 · 9:16 · 锁定光影 {variant}】

  [主体]
  {从 scenes/{name}.md row #8 一句话锁定 byte-identical 复制}
  ...

  [细节]
  ...

  [风格]
  ...

  [参数]
  ...

  ## 负向
  {re-paste style_guide §9 baseline + 场景专属}
  ````

### 项目层落地

- `my_novel/feng_shou_lu/scenes/s1_无寿崖.md` ← append Seedream 立绘 section (内容 from `scenes/ref_images/s1_无寿崖_seedream.md`)
- `my_novel/feng_shou_lu/scenes/s2_落雁渊.md` ← append Seedream 立绘 section
- DELETE `my_novel/feng_shou_lu/scenes/ref_images/` (整个子目录 + 2 文件)

## 改动 2: shot prompts startframe / lastframe Seedream 静帧 embedded blocks 全面废止

### 跨项目 rule 改动 (common-level)

`.claude/agent_refs/project/ai_video.md` rule 5 修订:

- **废止**: 「三段式 shotNN.md」第三段 (Seam-frame still prompts: startframe Seedream + lastframe Seedream embedded code blocks).
- **新规** (rule 5 v2): 每 shotNN.md 仅含 2 段 — ① Shot context + ② 视频 prompt fenced ```text``` block. 不再嵌入任何 Seedream PNG 静帧 prompt.

`.claude/agent_refs/project/ai_video.md` rule 11 修订:

- 整段 「Seam-frame still-image pipeline」标记为 **abolished** (历史 archive 保留, 但 stage-6 validator 不再 grep / 不再校验 seam-frame 块存在).
- Loop-back contracts / Workflow / Frame-prompt body structure / Per-shot prompt files (mandatory) 列表全部 archive.

`.claude/agent_refs/project/ai_video.md` rule 12.4 v2 schema 表 (字段顺序与必填矩阵) 修订:

- 「静帧 seam」列整列删除 (字段 #6 主体定义 / #7 姿态 frozen instant 仅静帧使用, 现一并 archive).
- 视频 shot 列保留 14 字段.

### 跨 shot 续接的替代契约 (rule 11 abolition 之后)

跨 shot 视觉一致性现完全依赖 **描述层连续性**:

1. 角色 一句话锁定 byte-identical (从 character bible row #10 复制) 在每个 shot 的 `角色:` 字段中重复使用.
2. 场景 一句话锁定 byte-identical (从 scene bible row #8 复制) 在每个 shot 的 `场景:` 字段中重复使用.
3. 光线 / 色调 + 渲染样式 + 负向 verbatim 跨 shot 重复使用 (从 style_guide §4 + §10 + §9 复制).
4. 角色 turntable mp4 reference 在 Reference uploads checklist 中 cross-shot 同 mp4 复用.
5. 场景 PNG (从 Seedream 立绘 prompt 渲染) 在 Reference uploads checklist 中 cross-shot 同 PNG 复用.

Kling / Seedance 在描述 + reference video/PNG 一致性下保持 视觉连贯; 不再 hard-pin 每帧 seam.

### 项目层落地 (7 shot prompts)

7 个 shotNN.md (shot01-shot07) 全部:

- 删除 `## Seam-frame still prompts` section 及其所有 fenced code blocks (startframe + lastframe).
- shot01.md 特殊: 既删除 startframe block 也删除 lastframe block.
- shot02-shot07.md: 仅删除 lastframe block.
- Reference uploads checklist 中 `scenes/ref_images/s{N}_*_seedream.md` 路径 → 更新为 `scenes/s{N}_*.md` (统一文件).
- shotlist.md 中 `seam-frame contract` 列内容保留作 *剧情节拍说明* (前/后帧来源描述) 但不再指向具体 PNG 文件; 标记为「内容连续性描述」.

## 改动 3: 下游产物 walk + 修补

### `specs/ai_video/xianxia_new/final_specs/spec.md` 修补

- **FR-7** 修补: 「Scene files (2 files) + Scene立绘 prompts (2 files)」收缩为「Scene files (2 files, single-file pattern)」. Scene 立绘 prompt 作为「---」分隔的第二段嵌入同一文件.
- **FR-9** 修补: shotlist.md 表头 `seam-frame contract` 列保留但语义改为「内容连续性描述」(前/后帧 *剧情节拍* 描述, 不指向具体 PNG).
- **FR-10** 修补: shotNN.md 二段式 (Shot context + 视频 prompt). 删除「Seam-frame still prompts as embedded code blocks per rule 12.4 v2 + 7 (lastframe every shot; startframe only shot01)」一句.
- **NFR-12** 修补: 「All cross-document references resolve」grep 不再包含 `scenes/ref_images/` 或 seam-frame `_seedream.md` 路径.

### `specs/ai_video/xianxia_new/validation/strategy.md` 修补

- 「scene_pack 关联 ref_images/ 段子」全部 archive — 现在 scene_pack 工作单元只产出 1 个 `scenes/{name}.md` 文件 (含 立绘 section).
- shot_prompt 工作单元的 V-2/V-3/V-4 不再 grep seam-frame block 存在性.
- CC-3 montage 描述中保留 seam-frame *剧情节拍说明* (不指向 PNG).

### `my_novel/feng_shou_lu/README.md` 修补

- 「使用说明」items 7+8 (scene files + scene ref_images) → 合并为 item 7 (scenes/{name}.md 单文件含 立绘 section).
- 「使用说明」item 11 (shotNN.md 中嵌入式 seam-frame Seedream prompt) → 删除「+ 嵌入式 seam-frame Seedream prompt」字样.
- 「工作流」diagram: 删除「scenes/ref_images/s{N}_*_seedream.md → Seedream 渲染场景立绘 PNG」之后的「episodes/ep01/prompts/shotNN.md 中的 seam-frame seedream 块 → Seedream 渲染每镜 start/last frame PNG」一行. 单 scene 文件下放 Seedream 立绘 section reference.

## Rationale

1. **简化 asset pipeline**: scenes/ref_images/ 2 文件 + 7 shots × 2 (startframe shot01 + lastframe 7) = 总 10 个 Seedream PNG 资产 step → 砍至 2 个 (仅 scenes 立绘 PNG, 每场景 1 张). User 估算 -80% Seedream 渲染开销.
2. **统一 single-file pattern**: characters (rule 12.5 v3) 已为单文件, scenes 同步对齐 — pipeline 结构上更对称, 用户认知负担更低.
3. **简化 stage-6 validator**: 不再需要 grep seam-frame block 存在性 / 主体定义 / 姿态 frozen instant / 渲染样式 / 比例 / 负向 5 字段必填矩阵. shot prompt validator 简化为 14 字段 video schema 单一表.
4. **承担 trade-off**: 失去 Seedream PNG 静帧 hard-pin 的 seam 锁帧 — 改为描述层连续性 + reference video/PNG 复用. 信任 Kling/Seedance 在统一 reference + 一致描述下能自然保持视觉连贯; 用户接受这一精度 trade-off 换取 pipeline 简化.

## Out of scope

- 此 follow-up 不动 character 单文件 pattern (rule 12.5 v3 already shipped, scenes 跟进对齐).
- 此 follow-up 不动 character ref_images 历史 archive (rule 12.2 早已 deprecated, 不需要再次修改).
- 此 follow-up 不重新渲染已写的 11 character bibles (它们的 divergence note 已经记录 ref_images/ 废止的逻辑, 仅适用于 characters; 此处 scenes 单文件遵循同样模式, 新写的 scene bible 不需要 divergence note — agent_refs 已被同步更新).
- 此 follow-up 不动 Stage 1-4 产物 (interview / qa.md / findings / dossier / etc.) — 它们的 ref_images / seam-frame 描述属于历史快照, 不重写.

## Acceptance

- `.claude/agent_refs/project/ai_video.md` rule 5 / 11 / 12.3 / 12.4 v2 已修订并加 follow-up 003 origin note.
- `specs/ai_video/xianxia_new/final_specs/spec.md` FR-7 / FR-9 / FR-10 / NFR-12 已修补.
- `specs/ai_video/xianxia_new/validation/strategy.md` 已修补 (seam-frame validators archive).
- `my_novel/feng_shou_lu/scenes/{s1_无寿崖,s2_落雁渊}.md` 已 append 立绘 section.
- `my_novel/feng_shou_lu/scenes/ref_images/` 已 deleted.
- `my_novel/feng_shou_lu/episodes/ep01/prompts/shot{01..07}.md` 已删除 `## Seam-frame still prompts` section.
- 所有 shot prompts 中 `scenes/ref_images/s{N}_*_seedream.md` reference 已替换为 `scenes/s{N}_*.md`.
- `my_novel/feng_shou_lu/README.md` 已修补 (items 7+8 合并 / item 11 删除 seam-frame 字样 / 工作流 diagram 简化).
- `specs/ai_video/xianxia_new/changelog.md` 已追加 follow-up 003 条目.
