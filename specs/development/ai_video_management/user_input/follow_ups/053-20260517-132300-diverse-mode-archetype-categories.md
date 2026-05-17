# Follow-up draft 053 — 2026-05-17

Summary: 新增 "多样化随机模式 (Diverse mode)" — 用户仅选 gender + ethnicity + count，后端按 **10 个 cinematic archetype** 均匀分布滚出 attrs（age_range / look / style / type_anchor）保证 batch 覆盖所有人物类型；每个 actor sidecar 记录 `archetype` 字段；ActorGrid 加 archetype filter chip。启动时一次性 best-effort backfill — 把现有 5 个 actor 映射到最近的 archetype。

## 用户原话

> 在UI上加一个新的演员生成模式，我只需要选择男女，还有种族，你帮我生成格式各样的人，又年轻俊美的，有老人，中年人， 有整齐的，有奸邪的，有妖媚的，又善良的，总之random生成各色各样的人，并把它们分类成小的类目，类目可以你来推荐，比如真是电影选角色是怎么归类的

## 交互问答记录

| 问 | 用户选 |
|---|---|
| 10-archetype 是否接受 | **Accept the 10 as proposed** |
| 分配策略 | **Even-distribution (default)** — guarantees coverage |
| Backfill 现有 5 | **Yes** — best-effort backfill from current attrs |

## 10 个 archetype 锁定表

| slug | 中文 | 适用 gender | age_range bias | look bias | style bias | type-anchor 池 (取自 follow-up 052) |
|---|---|---|---|---|---|---|
| `leading_hero` | 男主气场冷峻 | male | 18-25 / 26-35 | handsome / rugged / aristocratic | period-ancient-china / modern-casual / business | ex-soldier / rugby scrum-half / boxing-gym regular |
| `leading_warm` | 男主温润如玉 | male | 18-25 / 26-35 | handsome / soft / aristocratic | period-ancient-china / business | violinist / academic library / jazz pianist / engineering grad |
| `ingenue_kind` | 女主清纯善良 | female | 18-25 | beautiful / cute / soft | period-ancient-china / modern-casual | ceramic artist / veterinary student / ceramic-painter |
| `ingenue_lively` | 女主娇俏灵动 | female | 18-25 | cute / soft | modern-casual / streetwear / period-ancient-china | modern-dance choreographer / stable-hand / ceramic artist |
| `femme_fatale` | 女配妖媚 | female | 26-35 | beautiful / fierce / mature | period-ancient-china / business / fantasy | ballet dancer / documentary filmmaker / boxing trainer |
| `villain_cold` | 男配反派阴鸷 | male | 26-35 / 36-50 | rugged / aristocratic / fierce | period-ancient-china / business / sci-fi / fantasy | retired soccer player / factory-floor / old-money |
| `sage_elder` | 长辈宗师 | both | 51-65 / 65+ | mature / aristocratic / soft | period-ancient-china / business | northern fisherman / retired flight attendant / old-world matriarch / ethnomusicologist |
| `martial_drifter` | 江湖侠客 | both | 26-35 / 36-50 | rugged / mature / fierce | period-ancient-china / period-western | rock-climber / trail guide / fisherman weathered / park ranger |
| `everyman` | 市井百姓 | both | 26-35 / 36-50 | soft / mature / cute | modern-casual / streetwear | chef / second-generation immigrant / freelance editor / kitchen-back |
| `youth_fresh` | 少年清俊 | both | 18-25 | handsome / cute / soft | modern-casual / streetwear / period-ancient-china | long-distance runner / graduate humanities / field journalist |

注：`both` archetypes 自动 fork 为 male/female 两版本（按当前选 gender 取）。

## 决策

| 项 | 决策 | 理由 |
|---|---|---|
| Mode 实现 | **新 endpoint** `POST /api/actors/generate-diverse` 而非复用 generate 加 mode flag | 输入 schema 不同（diverse 不收 age/look/style/notes）— 单独 endpoint 不污染既有 GenerateActorsBody 的 closed enum 校验 |
| Endpoint body | `{count, gender, ethnicity, resolution?}` (不含 age_range / look / style / notes / seeds) | 用户仅选两个字段 |
| Backend roll 实现 | `_distribute_archetypes(count) -> list[ArchetypeRoll]` 算 even-distribution；每 slot 按 archetype 表 random 抽 age/look/style/type-anchor | even = `count // 10` 轮 + `count % 10` 随机补；保证 small count 也覆盖优先 archetypes |
| Even-distribution 顺序 | 按 archetype 表顺序循环；剩余 slot 随机抽 | 用户对 archetype 列表顺序敏感 — leading_hero 优先 |
| 单 gender 时跳过 | 是 — `male`/`female` 单 gender 时只取 `gender == 'male'` 或 `'female'` 或 `'both'` 的 archetype | gender filter 显式 |
| `youth_fresh` male batch 抽到时 | 用 male-bias 子集 (handsome, modern-casual, 长跑男, etc.) | both archetypes 内部 gender-aware |
| Archetype 写入 sidecar | 是 — sidecar md 加 `archetype` 行 (在 attrs table 内) | persistence + 后续 ActorGrid filter 读取 |
| `ActorInfo.archetype` | 新增 optional 字段；`/api/actors` response 返回；ActorGrid 显示 chip + filter | 前端 filter chip |
| Backfill | 启动时一次性 `migrate_archetypes()` best-effort — 已有 sidecar 无 archetype 字段 → 按 (age, look, style) tuple 查 archetype 反查表，写回 sidecar；OSError 静默跳过 | 不阻塞启动；多次启动幂等 |
| `migrate_archetypes()` 反查表 | 用 archetype 表正向计算 `(age, look, style) → archetype`；若 fall through 取 `everyman` 兜底 | 简单确定性 |
| UI 模式切换 | `ActorPoolGenerator` modal 顶部 radio: "标准模式" / "多样化随机模式" | 单一组件内 toggle，UX 一致 |
| Diverse 模式 UI 字段 | 仅显示 gender / ethnicity / count / resolution；其它 attrs 隐藏 | 用户原意 |
| Preview-then-confirm (follow-up 032) | diverse 模式**不走 preview** | 预览 N 个 random prompt 价值低；diverse 模式 confirm 直接 generate |
| ActorGrid filter | 加第 4 个 dropdown "archetype"，全部 + 10 个选项 + "未分类" | 与现有民族/性别/年龄段 filter 同 pattern (follow-up 033) |
| Sidebar 不变 | actor folder 在 `_actors/` 平铺，不按 archetype 分子目录 | 文件系统层简洁；filter 是查询层 |
| Body shot (follow-up 052) | diverse 模式同样产生 face + body | 默认行为，无需特殊 opt-in |

## 功能要求

### Backend

**`libs/infrastructure/actor_pool__writer.py`**：

1. 加 archetype 常量表 — `_ARCHETYPES: tuple[ArchetypeSpec, ...]` (10 项)。每项 dataclass：
   ```python
   @dataclass(frozen=True)
   class ArchetypeSpec:
       slug: str            # e.g. "leading_hero"
       name_zh: str         # e.g. "男主气场冷峻"
       gender_filter: str   # "male" | "female" | "both"
       age_ranges: tuple[str, ...]
       looks: tuple[str, ...]
       styles: tuple[str, ...]
   ```

2. 新 method `generate_diverse_batch(gender, ethnicity, count, resolution, notes_prefix="") -> GenerateResult`：
   - validate gender / ethnicity / count / resolution
   - `_distribute_archetypes(count, gender)` → list of `ArchetypeSpec` 长度 == count
   - 每 slot：从 spec 随机抽 (age_range, look, style)；compose `ActorAttrs(gender, ethnicity, age_range, look, style, notes=spec.name_zh)`
   - reuse existing 单 slot 生成路径 (allocate id → variance → face+body Kling → write)
   - 写入 sidecar 时**额外**记录 `archetype = spec.slug`（在 attrs table 内）
   - return `GenerateResult` 内每 generated entry 加 `archetype` field

3. `_distribute_archetypes(count, gender) -> list[ArchetypeSpec]`：
   - filter `_ARCHETYPES` for `spec.gender_filter == "both" or spec.gender_filter == gender` → eligible
   - eligible 长度 = N；rounds = `count // N`；rem = `count % N`
   - 结果 = (eligible × rounds) + `random.sample(eligible, rem)` 顺序循环

4. `_build_sidecar` 加可选 `archetype: str | None = None` 参数；sidecar table 加 `| archetype | {slug} |` 行（None 时省略行）。

5. `_parse_sidecar` 读 `archetype` 字段（如缺则 None）。

6. `migrate_archetypes()` 启动时一次性 sweep：扫 `_actors/actor_*/` 每个 sidecar md，若缺 `archetype` 字段则用 `_classify_actor_attrs(attrs)` 推断并 surgical-patch sidecar（在 attrs table 尾部插入行）。OSError swallow + count。
   - `_classify_actor_attrs(attrs) -> str`：扫 `_ARCHETYPES`，第一个 `gender_filter` 匹配 + `attrs.age_range in spec.age_ranges` + `attrs.look in spec.looks` + `attrs.style in spec.styles` 返回 slug；fall-through 返 `"everyman"`。

7. `ActorInfo` dataclass 加 `archetype: str | None = None` 字段；`list_actors` 解析 sidecar 填充。

**`libs/infrastructure/api.py` (post-051 → `apps/api/routes.py`)**：

1. 新 endpoint `POST /api/actors/generate-diverse`：
   - body `GenerateDiverseBody { count: 1..50, gender, ethnicity, resolution? }`
   - 调 `pool.generate_diverse_batch(...)` → mapper → DTO
   - errors 同 `generate`：400 / 405 / 500
2. 405 handler 覆盖 GET/PUT/PATCH/DELETE。
3. Docstring endpoint count 18 → 19。

**`libs/application/` (后端 DDD 层 per follow-up 051)**：

1. `actor__cdto.py` — 新增 `GenerateDiverseInputCdto { count, gender, ethnicity, resolution }`；`ActorInfo` Qdto 加 `archetype: str | None`。
2. `generate_diverse_actors__command.py` — 新 Command file，包装 `pool.generate_diverse_batch`。
3. `actor__mapper.py` — 加 diverse-to-cdto 映射。

### Frontend

**`apps/ui/src/api.ts`**：

1. 加 `GenerateDiverseActorsRequest { count, gender, ethnicity, resolution? }`。
2. 加 `generateDiverseActors(req)` POST `/api/actors/generate-diverse`。
3. `ActorInfo` 加 `archetype?: string | null`。

**`apps/ui/src/components/ActorPoolGenerator.tsx`**：

1. 加 mode state `mode: "standard" | "diverse"`。
2. 顶部 radio：标准模式 / 多样化随机模式。
3. diverse 模式：隐藏 age_range / look / style / notes / seeds 控件；仅显示 gender / ethnicity / count / resolution。
4. diverse 模式 confirm 直接调 `generateDiverseActors` (不走 preview)。
5. 进度条 / 失败统计 复用现有逻辑。

**`apps/ui/src/components/ActorGrid.tsx`**：

1. 加 archetype filter dropdown（与现有民族/性别/年龄段 filter chip 同 pattern）。
2. 选项：全部 / 10 archetype 中文名 / 未分类。
3. client-side filter actors by `actor.archetype === filterValue`。

**`apps/ui/src/components/ActorView.tsx`**：

1. metadata table 渲染 `archetype` 行（如有）。

**`apps/ui/src/styles.css`**：无新 class — 复用 actor-grid filter / form-field 样式。

### Spec / validation

- `final_specs/spec.md`:
  - 新 **FR-9t** `POST /api/actors/generate-diverse` 端点契约 + 10 archetype 表 + even-distribution 算法。
  - FR-9f / FR-10b / FR-86 / FR-88 / FR-91 / FR-92 各加 archetype mention 段。
- `validation/acceptance_criteria.md`:
  - 新 U3.25 scenario：diverse 模式 → 10 actor → 每 archetype 各 1；20 actor → 每 archetype 各 2；11 actor → 每 archetype 各 1 + 1 random extra；`/api/actors` 返回每 actor 的 archetype；ActorGrid filter 工作。
- `revised_prompt.md` header bump for 053。
- `changelog.md` append。

### Cross-task

- `specs/ai_video/mozun_chongsheng/changelog.md` parallel entry — 行为契约前置；现有 5 actor 启动时自动 backfill archetype（mozun_chongsheng character 也将能用 archetype 反查理想 actor）。

## 安全 / 边界

- **Kling cost**：与 052 相同；diverse N actors → 2N Kling calls；无额外加倍。
- **`generate_diverse_batch` 并发**：复用 existing batch 的 sequential 调用；frontend 9-worker pool (follow-up 027) 继续起作用（每 worker call diverse with count=1 即可，但 even-distribution 在 count=1 不有意义 → diverse 模式禁用 frontend 并发，单调用 count=N）。**接受 v1**。
- **Migrate 幂等**：sidecar `archetype` 字段已存在则跳过；多次启动安全。
- **`classify_actor_attrs` 漏分类**：fall-through 用 `everyman` 不是 None — 保证所有 actor 启动后都有 archetype；用户若不满意可手编 sidecar。
- **Notes field 在 diverse 模式**：自动写入 archetype 中文名（如 `男主气场冷峻`） — 帮助用户在 ActorGrid 浏览时一眼识别；用户可手动编辑 sidecar 改 notes。

## 不在本 follow-up 范围

- 不引入 archetype-specific 视觉 prompt 重写（archetype 仅控制 attrs 抽样 + sidecar 标签；prompt 走 follow-up 052 variance + 052 type_anchor pool）
- 不引入 frontend 9-worker pool concurrency for diverse mode（单 backend call N images 即可）
- 不引入 archetype-grouped sidebar 折叠
- 不引入 dynamic archetype 编辑 UI（10 archetypes hardcoded in backend；users 想加新 archetype 走代码 PR）
- 不引入 archetype × character 兼容性自动建议（"该 character 适合 leading_hero archetype 的 actor"）
- 不写 backend pytest / frontend Vitest（统一推迟）
- 不动 follow-up 052 的 face/body 双图、cast/ copy、variance pools
