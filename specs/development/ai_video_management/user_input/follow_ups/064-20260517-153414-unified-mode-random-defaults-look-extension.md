# Follow-up draft 064 — 2026-05-17

Summary: 三个耦合改动 — (1) 合并 "标准模式 / 多样化随机模式" 为 ONE 模式，去掉 radio toggle；(2) 每个下拉菜单加 "🎲 随机" sentinel option 作 DEFAULT，用户可以混合 — 部分字段固定 + 部分随机；(3) `look` 字段加 5 个新 enum 值：`righteous` (正义) / `sinister` (阴邪) / `seductive` (妩媚) / `cunning` (狡诈) / `innocent` (天真)，覆盖人物性格/气质维度（原 look 偏物理外貌）。每 slot 独立随机滚 (不再做 10-archetype even-distribution)；用户想要 archetype 平衡可手动选 `look=阴邪` 等。Frontend 客户端 roll random + 调既有 preview-prompts(count=1, seeds=[seed_i]) per slot；后端 `preview_prompts` 扩 optional `seeds` 参数让 frontend 显式控 seed 避免 `time.time()` 毫秒精度同 base_seed 冲突。

## 用户原话

> combine 标准模式和多样化随机模式 into one，in each dropdown, we could have an 随机option, when selectd, you can just randrom it, and 随机is the default value, also add more drop down option like 正义，阴邪，妩媚，狡诈，天真 etc

## 决策

| 项 | 决策 | 理由 |
|---|---|---|
| Mode 合并 | 移除 generator-mode-toggle radio；单一模式 | 用户原话 "combine into one" |
| Random sentinel | 前端常量 `RANDOM_SENTINEL = "__random__"`；每个下拉的第一个 option `<option value="__random__">🎲 随机</option>` | 与 backend closed-enum 不冲突（backend 永不收到 sentinel — frontend 在 preview/confirm 前 resolve）|
| Default 值 | 全部 6 个字段 default = "随机" | 用户原话 "随机 is the default value"；用户必须显式选具体值 |
| Resolution / count | resolution 也加 "随机" 选项；count 仍是 input（默认 5） | 一致；resolution 默认 normal 改为 随机 |
| Random rolling 位置 | **frontend**（client-side `random.choice(ATTR_OPTIONS[field])`） | 简单；后端不动；每 slot 独立滚 |
| 10-archetype 平衡逻辑 | **去掉** | 用户没要求保留；新 look 选项已覆盖 archetype 语义 |
| Preview 路径 | 既有 `previewPrompts({count: 1, ...slot.attrs, seeds: [base + i]})` 调 N 次，并行 Promise.all | 复用既有 endpoint；count=1 + 显式 seeds 让每 slot 独立 |
| Confirm 路径 | 既有 worker pool + per-slot generateActors | 不动 |
| 新 look 值 | `righteous` / `sinister` / `seductive` / `cunning` / `innocent` | 用户列举的 5 个；slug 用英语保持与 backend closed-enum 一致 |
| 中文 label | 正义 / 阴邪 / 妩媚 / 狡诈 / 天真 | 与用户列举一致 |
| Backend 修改 | (a) `LOOK_OPTIONS` 加 5 values；(b) `_LOOK_PROMPT_FRAGMENT` 加 5 mapping；(c) `preview_prompts` 加 optional `seeds: list[int] | None` 参数 | 最小后端改动 |
| `preview_prompts` seeds 行为 | 提供时使用；不提供时回落 `base_seed + i` | 与 generate_batch seeds 语义对称 |
| Look prompt fragment 翻译 | 用 English adjective + character archetype + 关联 visual cue | 给 Kling 足够 specificity (e.g., "righteous expression with virtuous determined gaze") |
| 旧 `generate-diverse` endpoint | 保留 backward compat；UI 不再用 | 同 follow-up 059 |
| Diverse 模式 preview-diverse endpoint | 保留 backward compat；UI 不再用 | 同 |
| ActorGrid filter | 加新 look 值的 ATTR_LABELS_ZH 映射也覆盖 | 自动得益（follow-up 063 已用 ATTR_LABELS_ZH）|

## 新 look 值 backend prompt fragments

| slug | name_zh | prompt fragment (English) |
|---|---|---|
| righteous | 正义 | upright virtuous demeanor with steady honest gaze, dignified moral bearing |
| sinister | 阴邪 | sinister calculating expression, subtle predatory composure, shadowed cheekbones |
| seductive | 妩媚 | seductive enchanting expression, half-lidded inviting gaze, soft red lips |
| cunning | 狡诈 | cunning sharp-eyed expression, slight knowing smirk, calculating raised brow |
| innocent | 天真 | innocent unspoiled expression, soft wide-eyed gaze, gentle natural smile |

## 功能要求

### Backend

`libs/infrastructure/writers/actor__writer.py`:
1. `LOOK_OPTIONS` frozenset：加 5 个 slug。
2. `_LOOK_PROMPT_FRAGMENT` dict：加 5 个 mapping per 上表。
3. `preview_prompts` 签名：加 optional `seeds: list[int] | None = None` 参数；inside loop `seed = seeds[i] if seeds else (base_seed + i)`；validation: if seeds provided, must be list of int length == count.
4. (无) — 不动 generate_batch（已支持 seeds）。

`libs/domain/repositories/actor__repository.py`:
- 更新 `preview_prompts` Protocol 签名加 `seeds: list[int] | None = None`。

`libs/application/queries/actor__query.py` `ActorQuery.preview_prompts`:
- pass `input_cdto.seeds` 到 `pool.preview_prompts`。

`libs/application/dtos/actor__dto.py` `GenerateActorsInputCdto`:
- 已有 `seeds: list[int] | None` field（follow-up 032）；无需改。

`apps/api/routes.py`:
- `_generate_input(body)` 已 plumb `seeds`；无需改。

### Frontend

`apps/ui/src/api.ts`:
1. `ATTR_OPTIONS.look`: append 5 new slugs `["handsome", "beautiful", "cute", "mature", "rugged", "soft", "aristocratic", "fierce", "righteous", "sinister", "seductive", "cunning", "innocent"]`。
2. `ATTR_LABELS_ZH.look`: 加 5 entries。
3. 新 export `RANDOM_SENTINEL = "__random__"`。
4. 新 helper `rollRandomAttr(field)`：return `ATTR_OPTIONS[field][Math.floor(Math.random() * ATTR_OPTIONS[field].length)]`。
5. 新 helper `resolveAttrs(formValues, RANDOM_SENTINEL)`：replace each `__random__` with a random roll.

`apps/ui/src/components/ActorPoolGenerator.tsx`:
1. **删除** `mode` state 与 mode toggle radio。
2. 每个下拉初始 state `useState<string>(RANDOM_SENTINEL)`。
3. 每个 `<select>` 第一个 `<option>` 是 `🎲 随机` (value=RANDOM_SENTINEL)；其余 options 不变。
4. `onPreview`：
   - 不再分 mode 分支。
   - 计算 `base_seed = Date.now()`。
   - 对每个 slot i in [0, count): 用 `rollRandomAttr` resolve 6 字段 + assign `seed = base_seed + i`。
   - Parallel call `previewPrompts({count: 1, ...resolved_attrs, resolution: resolved_resolution, seeds: [seed]})` × N 次。
   - 聚合 results into PromptPreviewResult shape `{prompts: [{seed, prompt, body_prompt}], resolution}`，每 entry 还附 attrs (frontend-resolved)。
5. `onConfirmGenerate` worker loop：
   - 既有 path 已支持 per-slot attrs（follow-up 059）。
   - 每 slot 从 `preview.prompts[slot-1]` 取 attrs；调 `generateActors({count: 1, ...attrs, seeds: [slot.seed]})`。

`apps/ui/src/styles.css`: 无新 class（既有 form-grid 兼容）。

### Spec / validation

- `final_specs/spec.md` FR-86 (closed enum schema): look enum 加 5 values。
- `validation/acceptance_criteria.md`：deferred batch。

### User input + audit

- `revised_prompt.md` header bump for 064。
- `changelog.md` append 064 entry。

## 安全 / 边界

- **Closed enum 完整性**：5 新 look values 加入 LOOK_OPTIONS 后通过 `_validate_attrs` 检查；preview-prompts + generate-actors 全部接受。
- **Backward compat**: 既有 actor sidecar 用旧 8 look slugs；list_actors 解析不受影响。
- **`migrate_archetypes`** (follow-up 053)：旧 sidecar 用旧 look → archetype 反查表仍工作；新 look 没在 archetype spec 内 → `_classify_actor_attrs` fall through 到 `everyman`。**接受 v1** — 用户用新 look 时手动决定角色定位即可。
- **Random sentinel 不流入后端**：frontend 在每个 preview/confirm call 前 resolve 为具体 slug；backend 始终见 valid enum。
- **Seeds 显式 control**：preview-prompts 新加 `seeds` param，保证 N 个 parallel calls 不会因毫秒精度共用 base_seed。
- **Cost preview**: 预览 N 个 actor → N 个 backend HTTP 调用（每个 < 100ms 因纯 compute）；并行 → < 1 秒。
- **Cost generate**: 每 actor 仍 2 Kling calls (face + body)；新 mode 不变。
- **UX 默认随机**: 用户首次开模态，所有 6 字段都是 🎲 随机；点 "预览 5 个 prompt" → 5 个完全随机 attrs 组合。

## 不在本 follow-up 范围

- 不动 generate-diverse / preview-diverse endpoints (backward compat)。
- 不删 ActorPoolGenerator 的 mode 相关 import / state 注释 — 留着 simple cleanup 给下次。
- 不加 "全选随机 / 全选具体" 快捷按钮。
- 不动 ActorGrid filter（既有 archetype filter + look filter 仍工作）。
- 不写 vitest / pytest。
- 不动 follow-up 053 archetype 反查 / migrate_archetypes。
- 不收紧/扩 look enum 之外的字段（ethnicity / gender 等）。
