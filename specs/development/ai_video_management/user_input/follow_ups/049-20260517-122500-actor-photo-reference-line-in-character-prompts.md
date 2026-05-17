# Follow-up draft 049 — 2026-05-17

Summary: 每个角色 reference turntable prompt 的 fenced ` ```text ` 代码块在 `角色:` 段后追加一行 `参考图: 请参考附加的演员照片 {actor_photo_path}`，提示视频模型把上传的演员照片视为面部 reference。**Placeholder 形式为 `{actor_photo_path}`**（user 复制 prompt 时手填实际 jpg 相对路径，留为未来 webapp 可自动替换的接缝）。**两层落地**：(1) 立刻 patch 现有 `ai_videos/mozun_chongsheng/characters/c{1..10}_*/c{N}_*.md` 共 10 份文件；(2) 同时更新 `.claude/agent_refs/project/ai_video.md` rule #12.5 的 turntable prompt schema 模板，保证未来任何 ai_video 项目通过 agent_team 生成的 character ref 文件都自动包含这一行。

## 用户原话

> ok, for all the chrarctor prompt, we should add one line, like please reference attached actor photo {placeholder}

## 交互问答记录（启动前）

| 问 | 用户选 |
|---|---|
| Placeholder 形式 | **literal `{actor_photo_path}` slot**（保留 token，未来可自动替换为 `_cast.md` 内 actor face path） |
| 插入位置 | **Right after `角色:` paragraph (first content line in the prompt)** |
| 是否未来生效 | **Yes — also amend `.claude/agent_refs/project/ai_video.md`** |

## 决策

| 项 | 决策 | 理由 |
|---|---|---|
| 行文字 | `参考图: 请参考附加的演员照片 {actor_photo_path}` | 与 prompt 内其它中文 sections (`角色:` / `场景:` / `镜头:` / ...) 风格一致；中文动词 "请参考" 比 user 原英文更贴近 Seedance / Kling 等国产 / 中文支持模型 |
| Placeholder token | `{actor_photo_path}` | 与现有 `{中文名}` / `{rule 12.4 v1 prompt body — ...}` 这种 curly-brace placeholder 视觉风格一致；token name 自解释 — 是 actor 的 face jpg 相对路径 |
| 插入精确位置 | 在 fenced ` ```text ` 代码块内，`角色: ...` 段之后空 1 行，然后是新的 `参考图: ...` 行，再空 1 行，然后 `场景: ...` | 与 prompt 现有"section 之间空一行"格式一致；视觉上是独立段落 |
| 是否动 `_cast.md` / webapp resolve | **否**（v1 留 literal token，未来可加 webapp 在 Reader 视图自动展示 + 在导出时替换） | 保持 v1 极简；user 复制到 Seedance 时手填实际 jpg path（从 `characters/{role}/_cast.md` 看 actor link） |
| Rule #12.5 schema 改动 | 在 line 513 (`角色: ...`) 之后加 schema line `参考图: 请参考附加的演员照片 {actor_photo_path}` | 未来 agent_team stage 6 生成 character ref 时按此 schema；与已 byte-identical 锁定的 9 个字段 (`场景 / 镜头 / 光线 / ...`) 协议一致 |
| Byte-identical 锁定列表 | 新 `参考图:` 行**全角色 byte-identical**（仅 placeholder token 不变，user 自填）| Rule #12.5 v4 已说明 turntable prompt 大部分字段 byte-identical 仅 `角色:` 段随角色变化；新行也归入 byte-identical 集 |
| 影响范围 | 仅 character ref prompt（fenced text 块）—— shot prompts (rule #12.4) / scene prompts (rule #12.10) / seam-frame seedream prompts 不动 | user 指明 "character prompt"；shot prompts 已有 `## 出场角色 — 上传以下 turntable reference 视频到模型` 表格作为 ref 引用，不需要重复 actor photo 提示 |
| 现有 10 个文件 | 全部 in-place 修改，保留原文件其它内容（角色 bible + 配音对照表 等不动）| 单点 surgical insert，0 风险 |

## 功能要求

### 1. agent_refs 改动（未来生效）

**`.claude/agent_refs/project/ai_video.md` rule #12.5 schema 块**：
- 在 line 513 `角色: {一句话锁定 byte-identical} + ...` 行之后空一行，新增：
  ```
  参考图: 请参考附加的演员照片 {actor_photo_path}
  ```
- 在 "Turntable 视频 prompt 锁定字段（10+ 角色 byte-identical...）" 段（line 559–561）的字段列表加 `参考图`（位于 `角色` 之后、`场景` 之前）。

### 2. 现有 10 份 character md (data-op)

**`ai_videos/mozun_chongsheng/characters/c{1..10}_*/c{N}_*.md`**：
- 在每份 file 的 fenced ` ```text ` 代码块内、`角色: ...` 段（实际行 91 in c1，等价位置 in c2..c10）之后空 1 行处插入：
  ```
  参考图: 请参考附加的演员照片 {actor_photo_path}
  ```
- 后面紧接 1 空行 + 已有 `场景: ...` 段，保持段落间一致空行格式。
- 其余内容（bible 段 / 配音对照表 / 弧光 / 关键场景 / etc.）byte-identical 不动。

### 3. Spec / validation

- 不动 `final_specs/spec.md`（webapp 不变 — 这是 ai_video 任务的内容契约，不是 development webapp 的 FR）。
- 不动 `validation/acceptance_criteria.md` 同理。
- `user_input/revised_prompt.md`：header bump for 049。
- `changelog.md` 加 follow-up 049 entry。

## 安全 / 边界

- **纯内容编辑**，0 backend / 0 endpoint / 0 frontend / 0 schema 变化。
- **`_cast.md` 不动**：那是 follow-up 043 的 actor-character 关联文件；本 follow-up 不读不写。
- **Placeholder 不自动 resolve**：未来如要在 webapp Reader 视图 inline-resolve `{actor_photo_path}` → 实际 actor jpg path（从 `_cast.md` 查找），是 separate follow-up；本次保持 string-literal。
- **跨角色 byte-equality**：新 `参考图:` 行所有角色完全相同（只有 `{actor_photo_path}` token，不展开），保留 turntable 合集剪辑可行性（rule #12.5 v4 设计）。
- **不破坏现有合集**：rule #12.5 v4 已声明 turntable 10+ 角色合集需要 byte-identical 字段；本 follow-up 加的新行也是 byte-identical，向后兼容。
- **未来 `_actors/` 复用约束**：placeholder token 选 `{actor_photo_path}` 而非 `{actor_jpg}` / `{演员图}` 等，因为 webapp `Reader.tsx` 等地方未来可用 regex `\{actor_photo_path\}` 精确匹配做 inline-resolve；token name 拼写稳定要紧。

## 不在本 follow-up 范围

- 不在 webapp Reader / ActorView 加 inline-resolve 逻辑（webapp 改动留给独立 follow-up）。
- 不动 shot prompt (rule #12.4) / scene prompt (rule #12.10) / seam-frame seedream (rule #12.4) — user 仅说 "character prompt"。
- 不为其它 dramas 改动 — 当前 ai_videos/ 下仅 `mozun_chongsheng` 一份。
- 不动 character bible 文本（角色定位 / 锁定描述符 / 性格 / 配音参考 / 弧光 等）。
- 不写 pytest / vitest。
- 不动 audit log。
- 不引入新 placeholder 自动解析 / Editor 内 token-highlight UI。
