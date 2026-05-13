# Changelog — ai_video_management

Append-only follow-up audit log. Each entry records what the follow-up changed and which downstream artifacts were patched in the same turn.

## Follow-up 033 — 2026-05-13 00:25:47
Source: user_input/follow_ups/033-20260513-002547-filename-convention-and-filters.md
Summary: 用户："lets introduce some convention for the actor file names, it should be always {民族}__{性别}__{年龄段}.jpg, and then in the main 演员池page, lets add filters, like filter by race, filter by gendor, filter by age etc. and make your best guess to update existing actors to follow this new rule"。三个相关改动：jpg 文件名约定 + grid filter UI + 自动 migration。

Backend:
- `libs/actor_pool.py`:
  - 新增 `_NEW_FILENAME_RE = re.compile(r"^[^/\\]+__[^/\\]+__[^/\\]+\.jpg$")` + helper `_attrs_to_filename(attrs)` 返回 `{ethnicity}__{gender}__{age_range}.jpg`
  - 新增 helper `_find_actor_jpg(folder)`：先找匹配 `_NEW_FILENAME_RE` 的 jpg，没有则 fallback 找 `{folder.name}.jpg` (legacy)
  - 修改 `generate_batch`：jpg 路径 `actor_folder / _attrs_to_filename(attrs)` 替代 `actor_folder / f"{actor_id}.jpg"`
  - 修改 `list_actors`：先校验 sidecar 存在，然后 `_find_actor_jpg(child)` 找 jpg；image_path 反映实际 filename
  - 修改 `actor_exists`：`_find_actor_jpg(folder) is not None`
  - 修改 `_reap_incomplete_folders`："有 jpg" 检查改为 `_find_actor_jpg`，partial migration 中间状态不被误判为 incomplete
  - 新方法 `migrate_filenames() -> dict[str, int]`：idempotent 扫 `_actors/`，per-folder try/except；已含 `_NEW_FILENAME_RE` jpg → skip；含 legacy `actor_NNNN.jpg` + sidecar → parse attrs → rename；目标已存在 → skip；返回 `{migrated, skipped, errors}`；跳过 `_deleted/_actors/`（构造期不动）
  - `ActorPool.__init__` 末尾自动调 `migrate_filenames()`（try/except 兜底，best-effort，不阻塞启动）
- 零 API 改动 — 全部 frontend / sidecar 兼容自动 fall through

Frontend:
- `src/components/ActorGrid.tsx`:
  - 加常量 `FILTER_ALL = "__all__"`
  - 新增 3 个 state: `filterEthnicity` / `filterGender` / `filterAgeRange`，default `FILTER_ALL`
  - 派生 `filteredActors`：先 filter，再分页
  - filter 变化时 `setPage(0)`
  - header `<h2>` 显示 `filtered / total`
  - 新增 `<div className="actor-grid-filters">` 三个 `<select>` (民族/性别/年龄段) + "全部" default option，复用 `ATTR_OPTIONS`
- `src/styles.css`：加 `.actor-grid-filters` (flex + gap + flex-wrap) + label/select 样式
- 零 api.ts 改动

Spec / validation:
- `final_specs/spec.md` FR-9f: 描述新文件名 `{ethnicity}__{gender}__{age_range}.jpg`；sidecar 保持 `actor_NNNN.md` 不变；migration 在 `__init__` 自动跑
- `final_specs/spec.md` FR-91: 加 filter UI 描述 + filter→page reset 0 + header 显示 `filtered/total`
- `validation/security.md` 无新 carve-out — migration 仅 rename 在 EXPOSED_TREE 内；filter 纯前端
- `validation/acceptance_criteria.md`: U3.15 加 jpg 文件名格式 + sidecar 不变 + auto-migrate 断言；U3.18 加 filter UI 断言

User-input:
- `user_input/revised_prompt.md`：composed-from 加 033；Last regenerated 改 2026-05-13 00:25:47；header summary 重写为 033 内容；Prior 032/031 更新

Auto-updated:
- `projects/ai_video_management/backend/libs/actor_pool.py` — `_NEW_FILENAME_RE` + `_attrs_to_filename` + `_find_actor_jpg` + generate path + `list_actors` + `actor_exists` + `_reap_incomplete_folders` + `migrate_filenames` + 构造期自动调用
- `projects/ai_video_management/frontend/src/components/ActorGrid.tsx` — 3 filter state + filteredActors + 3 dropdown UI + header count
- `projects/ai_video_management/frontend/src/styles.css` — `.actor-grid-filters` rules
- `specs/development/ai_video_management/final_specs/spec.md` — FR-9f / FR-91 改写
- `specs/development/ai_video_management/validation/acceptance_criteria.md` — U3.15 / U3.18 加断言
- `specs/development/ai_video_management/user_input/revised_prompt.md` — header / composed-from / 033 summary
- `specs/development/ai_video_management/user_input/follow_ups/033-20260513-002547-filename-convention-and-filters.md` (NEW)

No conflicts found in:
- follow-up 032 (preview-then-confirm)：preview 计算的 prompt 不依赖 jpg filename，033 不动 preview 流程
- follow-up 031 (anti-wax prompt)：prompt 内容不变，仅文件名约定改
- follow-up 030 (grid bulk/assign)：filter 与 select mode 互相独立；filter + select 同时使用：在 filtered set 上 select / delete / assign
- follow-up 028 (ActorGrid)：filter 是新 surface，分页 / tile click 行为保留
- follow-up 026 (actor delete) + 014 (casting)：actor_id (folder 名) 仍稳定，casting.md 不需要重写
- backend tests：boot-smoke 7/7 仍 pass；migration 在空 `_actors/` 上 no-op

Verification:
- `_attrs_to_filename(attrs)` → `'asian__male__18-25.jpg'` ✓
- `generate_batch` 写入 `actor_0001/asian__male__18-25.jpg` 而非 `actor_0001.jpg` ✓
- `list_actors` 返回新文件名路径 ✓
- `migrate_filenames` legacy → 新格式 + idempotent re-run noop ✓
- `pytest tests/test_boot_smoke.py`: 7/7 ✓

## Follow-up 032 — 2026-05-13 00:19:36
Source: user_input/follow_ups/032-20260513-001936-grid-page-size-and-prompt-preview.md
Summary: 用户："每页的演员展示上限可以多一点， 比如50个，当batch gen以前，加一个步骤，然我review 以下你准备发给kling api的prompt的final 版本，我确定之后点另一个button 在执行"。两个小改: PAGE_SIZE 12→50；新 `POST /api/actors/preview-prompts` endpoint + `generate_batch` 接 `seeds: list[int]` 实现字节级一致 preview-then-confirm。

Backend:
- `libs/actor_pool.py` 新增 `preview_prompts(attrs, count, resolution)` 方法：校验 attrs/count/resolution → 计算 N 个 `{seed: base_seed+i, prompt: _build_prompt(attrs, _variance_for(seed, gender))}` 返回 `{prompts: [...], resolution}`；不写磁盘 / 不调 Kling / 不分配 actor folder
- `generate_batch` 签名加 `seeds: list[int] | None = None`：当提供时校验 `len == count` + 全 int（否则 `InvalidAttribute`）；主循环改为 `seed = seeds[i] if seeds is not None else base_seed + i`
- `libs/api.py`: `GenerateActorsBody.seeds: list[int] | None = None`；新 endpoint `POST /api/actors/preview-prompts` 复用同 body（seeds 字段被 preview 忽略）→ 调 `actor_pool.preview_prompts` → 200 + JSON；新 method-not-allowed handler → 405；`actors_generate` 把 `body.seeds` 传给 `generate_batch`
- docstring endpoint count 15 → 16；endpoint 列表加 `POST /api/actors/preview-prompts`

Frontend:
- `src/api.ts` 加 `PromptPreviewResult` interface + `previewPrompts(req)` POST `/api/actors/preview-prompts`；`GenerateActorsRequest.seeds?: number[]`
- `src/components/ActorPoolGenerator.tsx` 大改:
  - 新 state: `previewBusy` / `preview: PromptPreviewResult | null` / `previewError`
  - 主按钮 onClick 从 `onSubmit` 改为 `onPreview`：调 `previewPrompts` → 设 preview state → 自动打开内嵌 `PromptPreviewModal`
  - `onSubmit` 重写为 `onConfirmGenerate`：从 preview 取 seeds，构造 worker pool，每 worker 调 `generateActors({..., seeds: [previewSeeds[slot-1]]})`
  - 新内嵌组件 `PromptPreviewModal`: 显示 N 张 `<details>` 卡片，summary 显示前 180 字符 + 展开；footer "取消" / "✓ 确认发送 (N)"
  - 主按钮 label：`"预览 prompt"` / `"计算预览中…"` / `"生成中… (X/N)"`
  - Modal close 重置 preview state
- `src/components/ActorGrid.tsx`: `PAGE_SIZE = 12` → `PAGE_SIZE = 50`
- `src/styles.css`: 加 `.prompt-preview-panel` / `.prompt-preview-hint` / `.prompt-preview-list` / `.prompt-preview-card` / `.prompt-preview-meta` / `.prompt-preview-seed` / `.prompt-preview-toggle` / `.prompt-preview-body` 8 条 rules

Spec / validation:
- `final_specs/spec.md` 新增 **FR-9j** `POST /api/actors/preview-prompts` 完整契约 (body / response shape / 无副作用 / preview→confirm 流程)
- `final_specs/spec.md` FR-9f body 加 `seeds?: list[int]`；详述 seeds 校验
- `final_specs/spec.md` FR-88: 主按钮改为 "预览 prompt"；描述内嵌 PromptPreviewModal + 确认发送 流程
- `final_specs/spec.md` FR-91: PAGE_SIZE 12 → 50（两处）
- `validation/security.md` 无新 carve-out — preview 是 read-only dry-run（无 Kling 调用 / 无文件 IO）；seeds 来自用户但走 InvalidAttribute 校验，仅作为 `_variance_for` RNG seed（无路径 / shell injection 面）；JSON response ~75KB / 50 prompts × 1500 chars 仍合理范围
- `validation/acceptance_criteria.md` U3.15 加 preview→confirm seeds 字节级一致 + seeds 长度校验 + seeds 类型校验 + 405 + PAGE_SIZE=50 断言

User-input:
- `user_input/revised_prompt.md`：composed-from 加 032；Last regenerated 改 2026-05-13 00:19:36；header summary 重写为 032 内容；Prior 031/030/029 与 032 的 surface 关系更新

Auto-updated:
- `projects/ai_video_management/backend/libs/actor_pool.py` — `preview_prompts` + `generate_batch` seeds 参数
- `projects/ai_video_management/backend/libs/api.py` — `GenerateActorsBody.seeds` + 新 endpoint + method-not-allowed + docstring
- `projects/ai_video_management/frontend/src/api.ts` — `PromptPreviewResult` + `previewPrompts` + `GenerateActorsRequest.seeds`
- `projects/ai_video_management/frontend/src/components/ActorPoolGenerator.tsx` — preview 流程改写 + `PromptPreviewModal`
- `projects/ai_video_management/frontend/src/components/ActorGrid.tsx` — PAGE_SIZE 50
- `projects/ai_video_management/frontend/src/styles.css` — 8 条 preview-modal rules
- `specs/development/ai_video_management/final_specs/spec.md` — 新 FR-9j + FR-9f/FR-88/FR-91 改
- `specs/development/ai_video_management/validation/acceptance_criteria.md` — U3.15 加 preview 断言
- `specs/development/ai_video_management/user_input/revised_prompt.md` — header / composed-from / 032 summary
- `specs/development/ai_video_management/user_input/follow_ups/032-20260513-001936-grid-page-size-and-prompt-preview.md` (NEW)

No conflicts found in:
- follow-up 031 (anti-wax prompt)：032 preview 显示的就是 031 改写后的 prompt，含 anti-wax + camera cue —— preview 真实反映 Kling 收到的内容
- follow-up 030 (grid bulk/assign)：PAGE_SIZE 50 不影响 select 模式 / 跨页 selection / bulk delete / assign 流程
- follow-up 029 (variance + resolution + Pillow)：preview 调 `_variance_for` 与 `_build_prompt`，与 generate 同代码路径
- follow-up 027 (concurrency)：seeds 流让每个 worker 用确定的 seed，9 路并发不变
- follow-up 026 (actor delete)：032 不动 delete 路径
- backend tests：boot-smoke 7/7 仍 pass

Verification:
- `preview_prompts(attrs, 3, 'normal')` 返 3 个 {seed, prompt}，每 prompt ≥1000 字符 + 含 anti-wax keywords ✓
- `generate_batch(attrs, 3, 'normal', seeds=preview.seeds)` 写入 sidecar，prompt 与 preview 字节级一致 ✓
- `generate_batch` seeds 长度 mismatch → `InvalidAttribute` ✓
- `generate_batch` seeds 含非 int → `InvalidAttribute` ✓
- `pytest tests/test_boot_smoke.py`: 7/7 ✓
- 全套 `pytest tests/`: 18 pass / 5 pre-existing fail（零回归）

## Follow-up 031 — 2026-05-13 00:16:00
Source: user_input/follow_ups/031-20260513-001600-photorealism-no-wax-face.md
Summary: 用户："请确保kling生成的人像是真人，目前生成的太假了，一看就是AI生成的，有的甚至像是蜡像脸"。Backend-only prompt 改写修 Kling 输出的蜡像脸 / 过度光滑 / 完美对称问题。

Backend:
- `libs/actor_pool.py`:
  - 改写 `_build_prompt(attrs, variance="")`:
    - 移除 `"photorealistic"` + `"sharp focus"` + `"8k"` 三个 AI/CG-correlated token（这些 token 在训练数据中常关联 render/CG aesthetic，把 Kling 推向蜡像脸）
    - 开头从 `"portrait headshot of ..."` → `"candid unposed portrait photograph of ..."`（candid + photograph 暗示真实照片）
    - 末尾追加固定段: `"natural ambient lighting, neutral uncluttered background, natural skin texture with visible pores and subtle imperfections, slight natural facial asymmetry, RAW unedited photograph aesthetic, no plastic skin, no waxy smoothness, no symmetrical perfection, no CG render look"` — positive 描述 + "no X" 形式的 anti-token（Kling text-to-image 不支持 negative_prompt 字段，但 prompt 内含 "no X" 仍有缓解效果）
  - 新增第 **18 个 variance pool `_VARIANCE_PHOTOREALISM`** (12 items): 真实相机 / 镜头 / 胶卷感 — Canon EOS R5 85mm f/1.4, Sony A7 IV 50mm f/1.8, Fujifilm X-T5 classic-chrome, Hasselblad medium-format, Kodak Portra 400 grain, Cinestill 800T halation, Leica M11, iPhone 15 Pro candid, Nikon Z9 105mm f/1.4, Pentax 67 medium-format, 35mm point-and-shoot, Polaroid SX-70。每 fragment 60-90 字符
  - `_variance_for(seed, gender)` 末尾加 `rng.sample(_VARIANCE_PHOTOREALISM, k=2)` — batch 中每张抽 2 个不同 camera/film cue，使一批生成像多个摄影师拍的而非同一 AI 出
- 长度 length-guard 不变（仍 ≥1000 chars）；signature 兼容

Frontend:
- 零改动 — 用户感知通过 backend prompt 改写自动生效，UX surface 不变

Spec / validation:
- `final_specs/spec.md` FR-9f: "17 池" → "18 池"；加 anti-wax 永久注入描述 (移除 photorealistic/sharp focus/8k + 追加 RAW/natural skin/no waxy 等)
- `validation/security.md`: 无新 carve-out — variance pool 仍 server-side hardcoded，prompt 改写不引入新输入面
- `validation/acceptance_criteria.md` U3.15: 加三项断言 — (a) sidecar 不含 "photorealistic"/"sharp focus"/"8k" 单独 token；(b) sidecar 含 "candid"/"natural skin texture"/"no waxy smoothness"/"RAW unedited"；(c) sidecar 至少含一项 `_VARIANCE_PHOTOREALISM` camera cue

User-input:
- `user_input/revised_prompt.md`：composed-from 加 031；Last regenerated 改 2026-05-13 00:16:00；header summary 重写为 031 内容；新增 "Prior follow-up 030" 行；Prior 029 描述更新（031 在其 17 池基础上加 PHOTOREALISM 第 18 池）

Auto-updated:
- `projects/ai_video_management/backend/libs/actor_pool.py` — `_build_prompt` 重写 + 新 pool + `_variance_for` 增 sample
- `specs/development/ai_video_management/final_specs/spec.md` — FR-9f 文案
- `specs/development/ai_video_management/validation/acceptance_criteria.md` — U3.15 加三断言
- `specs/development/ai_video_management/user_input/revised_prompt.md` — header / composed-from / 031 summary + Prior 030/029 行
- `specs/development/ai_video_management/user_input/follow_ups/031-20260513-001600-photorealism-no-wax-face.md` (NEW)

No conflicts found in:
- follow-up 030 (grid bulk delete + assign)：030 仅改 frontend，031 仅改 backend prompt，正交
- follow-up 029 (rich variance + resolution)：031 在其 17 池基础上加第 18 池；`_build_prompt` 签名不变；resolution / Pillow / length-guard / sidecar 不动
- follow-up 027 (concurrency)：generate_batch 主循环不动；只是每张的 prompt 文本变化
- 已存在的 actor_0001..0009 sidecar：不重新生成（retro-fit 不在范围）；新生成立刻有 anti-wax + camera cue
- backend tests：boot-smoke 7/7 仍 pass

Verification:
- `_build_prompt(attrs)` 输出不含 "photorealistic" / "sharp focus" / "8k"，含 "candid"/"natural skin texture"/"RAW unedited"/"no waxy" ✓
- `_variance_for(seed=1, 'male')` 输出含至少一个 `_VARIANCE_PHOTOREALISM` 元素（Canon/Sony/Fujifilm/etc. 关键词出现）✓
- variance 长度仍 ≥1000 ✓
- `pytest tests/test_boot_smoke.py`: 7/7 ✓
- 全套 `pytest tests/`: 18 pass / 5 pre-existing fail（零回归）

## Follow-up 030 — 2026-05-13 00:11:16
Source: user_input/follow_ups/030-20260513-001116-grid-bulk-delete-and-assign.md
Summary: 用户："在演员池页面，加入以下功能，第一个是bulk delelte，第二个功能是assign charactor, 给我drop down的选项，先选择哪个短剧，在选择短剧里的人物，然后确定后，此演员会标记参演这部短剧的这个角色。一个演员可以同时出演多部剧.you may need a more powerful data store to store this kind of relationship..."。Interactive 决策: 复用 per-drama `casting.md`（many-to-many 原生支持）+ 单一 window.confirm + 客户端 loop 批量删除。**零 backend 改动** — 全部 frontend feature 走现有 endpoints。

Frontend:
- `src/components/ActorGrid.tsx` 大幅扩展：
  - 新增 props `tree: TreeNode | null`, `onChange: () => void`
  - 新 state: `selectMode` / `selectedIds: Set<string>` (跨页保留) / `busyBulk` / `assignOpen`
  - 派生 `DramaChoice[]` from tree (`extractDramas`)：filter `ai_videos/` 直接子目录 non-`_*`，对每个 drama 找 `characters/c*/` 子目录名
  - Tile click: select mode → `toggleSelected(id)`；否则 → navigate (现有行为)
  - Header 加 "✅ 选择" / "✕ 退出选择" 切换按钮
  - Tiles 加 `actor-tile-selected` class + checkmark overlay
  - Sticky footer bar (selectMode 时显示)：`已选 N / 总 M` + 全选 / 全清 / 🗑 批量删除 / 🎬 分配角色 按钮
  - `onBulkDelete`：window.confirm 单次 → loop `deleteActor(id)` for each id → 累计 ok/fail/unassign 计数 → toast + tree reload + onChange
  - 新内嵌组件 `AssignCharacterModal`：drama `<select>` + character `<select>` (filter regex `^c\d+(_.*)?$`) + notes textarea + 确认按钮 → loop `castingAssign(drama.path, role, actor_id, notes)` for each selected id → toast + onChange
- `src/App.tsx`：`<Route path="/actors" element={<ActorGrid tree={tree} onChange={() => setRefreshKey(...)} />} />`
- `src/styles.css`：加 `.actor-grid-header-actions` / `.actor-tile-selected` (蓝边 + box-shadow) / `.actor-grid-checkbox` (overlay 左上角圆形 checkbox) / `.actor-grid-select-bar` (sticky bottom + box-shadow) / `.actor-grid-select-count` (monospace) / 按钮 hover/disabled + `.actor-grid-bulk-delete` 危险红 hover

Backend:
- 零改动。所有逻辑走现有：
  - `POST /api/actors/delete` (FR-9i / follow-up 026) — 自带 cascade unassign
  - `POST /api/casting/assign` (FR-9g / follow-up 014)
  - `GET /api/tree` (FR-10) — 提取 dramas + characters

Spec / validation:
- `final_specs/spec.md` FR-91 大幅扩展：select mode + 跨页 Set selection + sticky footer + bulk delete 单 window.confirm + loop + per-actor 错误隔离 + assign modal (drama dropdown 从 tree 派生 + character dropdown regex `^c\d+(_.*)?$` + loop castingAssign + per-drama casting.md 原生支持多剧) 全部说明
- `validation/security.md` 无新 carve-out — 全部复用已有 endpoint surfaces
- `validation/acceptance_criteria.md` U3.18：加 select mode 切换 / 跨页 selection 保留 / 批量删除 toast + cascade / assign 模态 drama+character dropdown + 多剧分配同 actor 不冲突 断言

User-input:
- `user_input/revised_prompt.md`：composed-from 加 030；Last regenerated 改 2026-05-13 00:11:16；header summary 重写为 030 内容；Prior 029 / 028 与 030 的 surface 关系标注

Auto-updated:
- `projects/ai_video_management/frontend/src/components/ActorGrid.tsx` — select mode + bulk delete + AssignCharacterModal + 派生 dramas
- `projects/ai_video_management/frontend/src/App.tsx` — `<ActorGrid tree onChange />` props
- `projects/ai_video_management/frontend/src/styles.css` — 8 条新 rules + sticky footer
- `specs/development/ai_video_management/final_specs/spec.md` — FR-91 扩展
- `specs/development/ai_video_management/validation/acceptance_criteria.md` — U3.18 扩展
- `specs/development/ai_video_management/user_input/revised_prompt.md` — header / composed-from / 030 summary
- `specs/development/ai_video_management/user_input/follow_ups/030-20260513-001116-grid-bulk-delete-and-assign.md` (NEW)

No conflicts found in:
- follow-up 029 (rich variance + resolution)：030 不动 generate 路径
- follow-up 028 (ActorGrid)：030 在其基础上扩展，分页 + 单 tile click → detail 默认行为不变
- follow-up 026 (actor delete)：030 通过 client-side loop 复用相同 endpoint
- follow-up 014 (CastingView)：030 写入相同 `casting.md` markdown 表；CastingView 读视图自动反映新写入
- `backend/libs/casting.py.Casting.unassign_actor_everywhere`：bulk delete 时每张都自动 cascade unassign
- backend tests：boot-smoke 7/7 仍 pass（零 backend 改动）

Verification:
- `pytest tests/test_boot_smoke.py`: 7/7 ✓
- 全套 `pytest tests/`: 18 pass / 5 pre-existing fail (与 029 同基线，零回归)
- Frontend tsc：新 ActorGrid 类型零错误（vite.config.ts 2 个 pre-existing path-typing 错误与本 follow-up 无关）

## Follow-up 029 — 2026-05-13 00:00:12
Source: user_input/follow_ups/029-20260513-000012-richer-variance-and-resolution-picker.md
Summary: 用户："当生成一个batch的时候，你需要加一些random的形容词到prompt里，... 你至少要加1000字以上的random形容词，然后在发给kling api。 然后生成的时候应该让我选在像素，default可以不用2k，4k 普通画质就可以"。Interactive 决策：resolution 选项 = 普通 / 2K / 4K，default 普通。

Backend:
- `libs/actor_pool.py` 加 17 个 variance pool tuples（gender-aware look archetype + gender-aware face features + jawline + cheekbones + brow + nose + lips + eyes + hair length/style/color + skin tone/texture + expression + mood + lighting + photography）；每池 8-14 项，每项 30-60 字符
- 重写 `_variance_for(seed, gender)`：每池 1-3 picks，~30-40 fragments 总和；末尾 `while len(result) < 1000:` 兜底循环；同 seed 完全可复现
- 加 `_RESOLUTION_PRESETS = {"normal": None, "2k": 2048, "4k": 4096}` + `DEFAULT_RESOLUTION = "normal"` + `RESOLUTION_OPTIONS = frozenset(...)`；常量 `JPEG_QUALITY = 95`
- `generate_batch(attrs, count, resolution="normal")` 签名扩展；校验 `resolution in RESOLUTION_OPTIONS` 否则 raise `InvalidAttribute`；Kling 返回 bytes 后若 `target_px is not None` 调 `_resize_jpeg(bytes, target_px)`；失败归入 `errors[]: resize_failed`，batch 继续
- 新静态方法 `_resize_jpeg(jpeg_bytes, target_px)`：Pillow `Image.open(BytesIO)` → `.convert("RGB")` → `.resize((target_px, target_px), Image.LANCZOS)` → `save(buf, "JPEG", quality=95)`
- `_build_sidecar(actor_id, attrs, prompt, seed, resolution="normal")` 加 resolution 字段到属性表
- `result.generated[i]` 携带 `"resolution"` 字段
- `__all__` 加 `DEFAULT_RESOLUTION` + `RESOLUTION_OPTIONS`
- imports 加 `random` (follow-up 027 已加) + `io.BytesIO` + `from PIL import Image`
- `libs/api.py`：`GenerateActorsBody.resolution: str = "normal"`；`actors_generate` 把 `body.resolution` 传给 `generate_batch`
- `backend/requirements.txt` 加 `pillow>=10.0`

Frontend:
- `src/api.ts`：`GenerateActorsRequest.resolution?: string`；`ATTR_OPTIONS.resolution = ["normal", "2k", "4k"] as const`
- `src/components/ActorPoolGenerator.tsx`：`useState<string>("normal")` for resolution；onSubmit pass through；useCallback dep 加 resolution；form-grid 加第 7 个 dropdown "画质"，option label "普通 (~1024px, Kling 原始)" / "2K" / "4K"

Spec / validation:
- `final_specs/spec.md` FR-9f 重写：body 加 `resolution`；详述 17 池 + ≥1000 字符 length-guard + Pillow Lanczos resize + `resize_failed` 错误类
- `final_specs/spec.md` FR-86：加 `resolution` enum 行
- `final_specs/spec.md` FR-88：六 → 七 dropdown，注明 resolution UX
- `validation/security.md` carve-out #7：加 (d) Pillow image-decode + resize hardening（仅信任 Kling JPEG / 已 SSRF-vetted / 5MB cap 前置 / 失败兜底）+ (e) resolution enum closed schema；Pillow 新 dep 跟踪上游 advisories
- `validation/acceptance_criteria.md` U3.15：标题加 "+ 029 rich variance + resolution"；新增 ≥1000 字符断言 + resolution=2k → 2048×2048 / 4k → 4096×4096 / normal → Kling 原始 / 8k → 400 invalid_attribute 四个分支

User-input:
- `user_input/revised_prompt.md`：composed-from 加 029；Last regenerated 改 2026-05-13 00:00:12；header summary 重写为 029 内容；Prior 028 / 027 描述与 029 的 surface 关系

Auto-updated:
- `projects/ai_video_management/backend/libs/actor_pool.py` — 17 池 + `_variance_for` 重写 + `_RESOLUTION_PRESETS` + `_resize_jpeg` + `generate_batch` 签名 + `_build_sidecar` resolution 字段 + `__all__`
- `projects/ai_video_management/backend/libs/api.py` — `GenerateActorsBody.resolution` + 传参
- `projects/ai_video_management/backend/requirements.txt` — `pillow>=10.0`
- `projects/ai_video_management/frontend/src/api.ts` — `GenerateActorsRequest.resolution` + `ATTR_OPTIONS.resolution`
- `projects/ai_video_management/frontend/src/components/ActorPoolGenerator.tsx` — 第 7 dropdown + state + dep
- `specs/development/ai_video_management/final_specs/spec.md` — FR-9f 重写 + FR-86 / FR-88 扩展
- `specs/development/ai_video_management/validation/security.md` — carve-out #7 加 (d) / (e)
- `specs/development/ai_video_management/validation/acceptance_criteria.md` — U3.15 扩
- `specs/development/ai_video_management/user_input/revised_prompt.md` — header / composed-from / 029 summary
- `specs/development/ai_video_management/user_input/follow_ups/029-20260513-000012-richer-variance-and-resolution-picker.md` (NEW)

No conflicts found in:
- follow-up 028 (ActorGrid)：029 不动 grid 路径；grid 仍用 `/api/actors` + lazy thumbnail，2K/4K 选项不影响 grid 行为
- follow-up 027 (concurrency + race-safe)：029 在 `_variance_for` 函数体扩展 pools，不动外层并发 / 分配 / cap
- follow-up 026 (actor delete)：029 不重叠 delete 路径
- follow-up 025 (Kling-only)：KlingProvider / JWT / SSRF-vet / cap 完全不动；resolution upscale 仅作用于 provider 返回的 bytes
- 已生成的 `_actors/actor_0001..0009` 老 sidecar：不重写（历史 artifact 保留；未来 regen 才有 `resolution` 字段 + 长 variance prompt）
- backend tests：boot-smoke 7/7 仍 pass

Verification (inline smoke):
- `_variance_for(seed=1, gender='male')` 输出长度 ≥ 1000；`_variance_for(seed=1, gender='male')` 二次调用 byte-equal（可复现）✓
- `_variance_for(seed=1, gender='male')` ≠ `_variance_for(seed=2, gender='male')` (不同 seed 不同 variance) ✓
- `_resize_jpeg(test_1024_jpeg, 2048)` 输出 Pillow 解码 size = (2048, 2048) ✓
- `_resize_jpeg(test_1024_jpeg, 4096)` 输出 size = (4096, 4096) ✓
- `generate_batch(attrs, count=1, resolution="invalid")` raise InvalidAttribute ✓
- `pytest tests/test_boot_smoke.py`: 7/7 ✓
- 全套 `pytest tests/`: 18 pass / 5 pre-existing fail (与 028 同基线，零回归)

## Follow-up 028 — 2026-05-12 23:43:09
Source: user_input/follow_ups/028-20260512-234309-actor-grid-view.md
Summary: 用户："current view of actors is only one at a time, need to first give me a grid like view to compare all pictures you could do paging if cannot fit all into one page, but one at a time is not efficient"。**新 `ActorGrid` 视图**: 一屏多图对比的演员池 grid，替代单张点击 workflow。**零 backend 改动** — 全部走 follow-up 014 已存的 `GET /api/actors` + follow-up 005 的 `GET /api/media`。

Frontend:
- `src/components/ActorGrid.tsx` (NEW)：React 组件，mount 时 `listActors()` → 内部 state；`PAGE_SIZE = 12`；响应式 CSS grid `repeat(auto-fill, minmax(180px, 1fr))`；每 tile 是 `<button>` 含 `<img loading="lazy">` + `actor_NNNN` + 4 个属性 chip (ethnicity / gender / age_range / look)；click 触发 `navigate('/file/' + encodeURIComponent(image_path))`；pagination 控件 (首页 / 上一页 / `第 N / M 页` / 下一页 / 末页) 仅 `actors.length > 12` 时渲染；empty / loading / error 三态 (error banner + reloadKey state-bump 重试)；`aria-live="polite"` 在页码指示
- `src/App.tsx`：import `ActorGrid`；加 `<Route path="/actors" element={<ActorGrid />} />`
- `src/components/Sidebar.tsx`：import `useNavigate` from `react-router-dom`；构造期拿 `navigate`；在 `isActorsRoot` 现有 🎭 生成演员 按钮后加 🔲 网格 按钮 sibling，onClick 跳 `/actors`
- `src/styles.css`：新增 14 条 `.actor-grid-page` / `.actor-grid-header` / `.actor-grid-pagination` / `.actor-grid-page-indicator` / `.actor-grid` / `.actor-tile` (hover + focus-visible) / `.actor-tile-image` / `.actor-tile-meta` / `.actor-tile-id` / `.actor-tile-chips` / `.actor-tile-chip` / `.actor-grid-empty` rules

Backend:
- 零改动（`GET /api/actors` from follow-up 014 已满足全部数据需求）

Spec / validation:
- `final_specs/spec.md` 新增 **FR-91** ActorGrid 完整契约 (route / fetch / tile / pagination / empty/loading/error 三态)
- `final_specs/spec.md` 扩 **FR-87** 提及网格按钮 + 路由 + 入口位置
- `validation/acceptance_criteria.md` 新增 **U3.18** scenario：空池 empty state / 5 actors 无分页 / 13 actors 跨页 2 / 25 actors 3 页 / tile click → `/file/{path}` / error retry
- `validation/acceptance_criteria.md` 覆盖矩阵加 `FR-91 | U3.18 (ActorGrid 分页，follow-up 028)`
- `validation/security.md` 无新 carve-out — grid 是纯 GET 读取面 (`/api/actors`)，follow-up 014 carve-out 已涵盖；本 follow-up 不引入新写入面或新出站 HTTP

User-input:
- `user_input/revised_prompt.md`：composed-from 加 028；Last regenerated 改 2026-05-12 23:43:09；header summary 重写为 028 内容；Prior 027 / 026 跟 028 的 surface 关系标注

Auto-updated:
- `projects/ai_video_management/frontend/src/components/ActorGrid.tsx` (NEW) — paginated grid
- `projects/ai_video_management/frontend/src/App.tsx` — 加 `/actors` route + import
- `projects/ai_video_management/frontend/src/components/Sidebar.tsx` — 加 🔲 按钮 + `useNavigate`
- `projects/ai_video_management/frontend/src/styles.css` — 14 条新 CSS rules
- `specs/development/ai_video_management/final_specs/spec.md` — FR-91 新增 + FR-87 扩展
- `specs/development/ai_video_management/validation/acceptance_criteria.md` — U3.18 scenario + matrix
- `specs/development/ai_video_management/user_input/revised_prompt.md` — header / composed-from / 028 summary
- `specs/development/ai_video_management/user_input/follow_ups/028-20260512-234309-actor-grid-view.md` (NEW)

No conflicts found in:
- follow-up 027 (concurrency + variance)：028 不动 generate 路径或 actor_pool，完全正交
- follow-up 026 (actor delete)：028 不重叠 delete 按钮，sidebar 🗑 仍是删除入口；grid 是 read-only
- follow-up 025 (Kling-only)：028 不动 provider
- follow-up 014 (CastingView)：CastingView 的 assign-mode grid 是 drama-scoped + filtered；ActorGrid 是 pool-level + 无 filter，surface 独立
- follow-up 022 (sidebar collapse-all)：028 加按钮但不动 collapse 逻辑
- `_actors/_deleted/` (follow-up 026)：grid 不显示已删除 actor（`GET /api/actors` 只 list `_actors/` 不含 `_deleted/`），一致行为

Verification:
- `pytest tests/test_boot_smoke.py`: **7/7 通过** ✓ (零 backend 改动)
- 全套 `pytest tests/`: 18 pass / 5 pre-existing fail (与 follow-up 027 完成时同样基线，零回归)
- TypeScript 编译：新 `ActorGrid.tsx` 导入 / 类型零错误（vite.config.ts 的 2 个 pre-existing path-typing 错误与本 follow-up 无关）
- 手工验证：route `/actors` 渲染、tile click 跳 `/file/...`、pagination 按钮 disabled/enabled 切换正确

## Follow-up 027 — 2026-05-12 23:26:56
Source: user_input/follow_ups/027-20260512-232656-concurrency-and-variance.md
Summary: 用户："current generation of actor picture is too slow, kling api allow 9 concurrent request, please remove any limitation on your side and leverage the 9 concurrency on kling api, also, when I let you do batch generation, you should introduce a lot of variance to the text on top of the basic info, ..."。**两个独立修复**: (1) **9-way 并发** — frontend `ActorPoolGenerator` 从串行 await 改用 9-worker pool (`CONCURRENCY=9` 对齐 Kling API)；20 张 batch 从 ~50s 降到 ~6-9s。Backend FastAPI sync endpoint 已经跑在 threadpool，9 个并发请求自然分配 9 个工作线程。(2) **Per-image variance** — `_variance_for(seed, gender)` 从 5 个 server-side 英文 tuple pool (gender-specific face features / skin tones / face shapes / eye descriptors / hair descriptors) 按 seed 抽 fragment 注入 prompt，避免同 base prompt 产生 near-duplicates。**Race-safe ID 分配**：之前的 "pre-compute `next_id + offset`" 在 9 并发下同 id 冲突；改用 `_allocate_actor_id` 循环 `mkdir(exist_ok=False)` 原子分配；`_reap_incomplete_folders` 独立提取，仅 batch 开始调一次（之前混在 `_next_actor_id_num` 内会跟 concurrent allocators 互相 reap）。**`MAX_BATCH_COUNT` 20→50**。

Backend:
- `libs/actor_pool.py`: import 加 `random`；新增 `_MAX_ID_ALLOC_SCAN = 1000` 常量
- 加 5 个 variance pool tuples (`_VARIANCE_FACE_FEATURES_MALE/FEMALE`, `_VARIANCE_SKIN_TONES`, `_VARIANCE_FACE_SHAPES`, `_VARIANCE_EYE_DESCRIPTORS`, `_VARIANCE_HAIR_DESCRIPTORS`)，每池 6-8 项 English fragments
- 新 module-level fn `_variance_for(seed, gender) -> str`：`random.Random(seed)` 每池 `choice` 一项 join 成单字串；同 seed 同 gender 完全可复现
- `ActorPool._build_prompt(attrs, variance: str = "") -> str`：在 base parts 中 `attrs.look` 之后 / `style` 之前插入 variance（不传时行为不变，向后兼容）
- 新方法 `ActorPool._allocate_actor_id(actors_dir) -> tuple[str, Path]`: `mkdir(exist_ok=False)` 循环往上找 free slot；OSError → `GenerationDirMissing`；1000 attempts 越界也 `GenerationDirMissing`
- `_reap_incomplete_folders(actors_dir)` 提取为独立 staticmethod（之前嵌在 `_next_actor_id_num` 里跟并发 race）；`_next_actor_id_num` 现在纯扫描无副作用
- `generate_batch` 主循环重写：开头 `_reap_incomplete_folders` 一次；每张图片 `_allocate_actor_id` 原子分配 → `_variance_for(seed, gender)` → `_build_prompt(attrs, variance=...)` → provider call → sidecar 用 varianced prompt
- `MAX_BATCH_COUNT = 50`

Frontend:
- `src/components/ActorPoolGenerator.tsx`:
  - 加常量 `CONCURRENCY = 9` + `MAX_BATCH_COUNT = 50`
  - `Progress.current: number` → `Progress.inFlight: number`
  - `onSubmit` 主循环重写为 worker pool：`claimSlot` 抽 slot；9 个 worker `await Promise.all([])` 并发；每 worker 循环到 slot 用完；`inFlight` 计数随 in-flight workers 起落；`cancelledRef` 检查放在 `claimSlot` 内 — 取消时新 slot 拿不到，已 in-flight 的 worker 完成后正常 tally
  - count 输入 `max={20}` → `max={MAX_BATCH_COUNT}`；clamp 同步
  - Button busy 文字 `生成中… (current / total)` → `生成中… (done+failed / total)` (current 已被 inFlight 替换，进度按"已完成数"展示更直观)
  - `ProgressPanel`：增 `⚡ 并发 N` chip 显示当前 in-flight workers
- `src/styles.css`：加 `.progress-inflight { color: #1e40af; font-weight: 600; }`

Spec / validation:
- `final_specs/spec.md` FR-9f 重写：详述 race-safe `_allocate_actor_id` (mkdir-exist_ok-False atomic) + variance pool 注入流程 + 9 并发 backend threadpool 路径；count cap 20→50
- `final_specs/spec.md` FR-88: 模态 count input 上限 20→50；描述 9-worker pool + `⚡ 并发 N` chip
- `validation/security.md` carve-out #7：增 3 项硬化 — (a) race-safe ID allocation 关闭 9 并发下的 ID 冲突 race；(b) variance pools server-side hardcoded，无新 prompt-injection 面；(c) count cap 50 仍 bound 总 outbound HTTP wave
- `validation/acceptance_criteria.md` U3.15：标题加 "+ 027 concurrency + variance"；新增断言 (sidecar prompt 互不相同 / 至少含一个 variance fragment / count cap 改 21→51 / 9 并发 distinct ids)

User-input:
- `user_input/revised_prompt.md`：composed-from 加 027；Last regenerated 改 2026-05-12 23:26:56；header summary 重写为 027 内容；Prior 026 与 Prior 025 重写描述跟 027 的 surface 关系

Auto-updated:
- `projects/ai_video_management/backend/libs/actor_pool.py` — variance pools + `_variance_for` + `_allocate_actor_id` + `_reap_incomplete_folders` + 重写 `generate_batch` + cap 50
- `projects/ai_video_management/frontend/src/components/ActorPoolGenerator.tsx` — worker pool + cap 50 + progress shape (current→inFlight) + 并发 chip
- `projects/ai_video_management/frontend/src/styles.css` — `.progress-inflight` rule
- `specs/development/ai_video_management/final_specs/spec.md` — FR-9f 重写 + FR-88 改写
- `specs/development/ai_video_management/validation/security.md` — carve-out #7 第一段增 3 项硬化
- `specs/development/ai_video_management/validation/acceptance_criteria.md` — U3.15 扩
- `specs/development/ai_video_management/user_input/revised_prompt.md` — header / composed-from / 027 summary
- `specs/development/ai_video_management/user_input/follow_ups/027-20260512-232656-concurrency-and-variance.md` (NEW)

No conflicts found in:
- follow-up 026 (actor folder delete)：027 改 generate 路径，026 改 delete 路径，正交
- follow-up 025 (Kling-only)：027 仍用同一 KlingProvider，只是前端并发数 + variance + race-safe 分配；KlingProvider 的 JWT / SSRF-vet / 30s timeout / 5MB cap 全部不动
- follow-up 023 (mp4 delete)：完全独立 surface
- follow-up 018 (pollinations retry)：retry 代码 follow-up 025 已删；027 不依赖 retry
- `backend/libs/api.py` / `backend/libs/casting.py`: `ActorPool(exposed, resolver)` 构造签名不变；`generate_batch(attrs, count)` 公开签名不变
- `backend/tests/` 全部测试：boot-smoke 7/7 仍 pass；其他测试不依赖 actor_pool generate 路径
- 已生成的 `_actors/actor_0001..0009/actor_NNNN.md` 老 sidecar 中无 variance fragment 字样：那是 follow-up 027 之前生成的，retroactive 不重写；用户用新按钮重新生成才会有 variance

Verification (inline smoke):
- `_variance_for(seed=1, gender='male')` 与 `_variance_for(seed=2, gender='male')` 输出不同；同 seed 多次调用输出相同 ✓
- `_build_prompt(attrs, variance=v)` 含 v；`_build_prompt(attrs)` 不含 ✓
- 9 个线程并发调 `_allocate_actor_id(空 _actors/)` → 9 个 distinct actor_0001..0009 ✓
- `_reap_incomplete_folders` 仍正确回收 jpg-less folders；保留有 jpg 的 folder ✓
- `pytest tests/test_boot_smoke.py`: **7/7 通过** ✓
- 全套 `pytest tests/`: 18 pass / 5 pre-existing fail (与 follow-up 026 完成时同样 5 个 wukong_juexing-fixture failures，零回归)

## Follow-up 026 — 2026-05-12 23:10:14
Source: user_input/follow_ups/026-20260512-231014-actor-folder-delete.md
Summary: 用户："lets add a delete button at actor folder level, after delete, it will be moved to _delete folder similar to the mp4 delete feature"。**Sidebar 每个 `ai_videos/_actors/actor_NNNN/` 行加 🗑 软删除按钮**：移动整个 actor folder 到 `ai_videos/_deleted/_actors/actor_NNNN/`（镜像 follow-up 023 的 `_deleted/` 子路径 pattern，但作用于 folder 而非单文件）。Interactive 决策："Auto-unassign then delete" → cascade-unassign 模式：endpoint 先 sweep 所有 drama 的 `casting.md` 移除引用该 actor_id 的行，再原子 rename folder。响应携带 `unassigned: [{drama, role}]` 列表供 UI 报告。

Backend:
- `libs/actor_pool.py` 加 4 个 exceptions: `ActorNotFound` / `ActorAlreadyDeleted` / `ActorDeleteTargetExists` / `ActorDeleteFailed`；加方法 `ActorPool.delete_actor(actor_id: str) -> dict[str, str]`：校验 `_ACTOR_ID_RE` → `is_dir()` + `is_symlink()` reject → target = `resolver.root / "ai_videos" / "_deleted" / "_actors" / actor_id` → target.exists 拒 → mkdir parents → atomic `src.rename(target)` → 返回 `{from, to}`；`__all__` 扩展含 4 个新 exceptions
- `libs/casting.py` 加方法 `Casting.unassign_actor_everywhere(actor_id: str) -> list[dict[str, str]]`：walk `ai_videos/` 直接 children（跳 `_`-prefix system folders 与 non-dir / symlink），对每个 drama 的 `casting.md` parse → 过滤 actor_id 匹配的行 → 若有移除则 `_write()` 重写文件（复用 `assign()` 的 atomic temp+os.replace 路径）→ 累计 `{drama, role}` 返回；不动 unchanged casting.md 减少 mtime churn
- `libs/api.py` import 加 4 个新 actor_pool exceptions；新 Pydantic `DeleteActorBody { actor_id: str }`；新 endpoint `POST /api/actors/delete`：cascade 先 (OSError → 500 `cascade_failed`)，folder move 后；exception 映射 `InvalidAttribute` → 400 `invalid_actor_id`、`ActorNotFound` → 404 `actor_not_found`、`ActorDeleteTargetExists` → 409 `target_exists`、`ActorDeleteFailed` → 500 `move_failed`；method-not-allowed handler `GET/PUT/PATCH/DELETE` → 405；docstring endpoint count 14 → 15

Frontend:
- `src/api.ts` 加 `interface DeleteActorResult { from, to, unassigned: { drama, role }[] }` + `export async function deleteActor(actorId)` POST `/api/actors/delete`
- `src/components/Sidebar.tsx` 加 `ACTOR_ID_RE = /^actor_\d{4,}$/` 常量；`deletingActorId` state；`onActorDeleteClick` useCallback (window.confirm → deleteActor → 复用 `renameToast` surface 上 "已删除 actor_NNNN（解除 N 个 casting 引用）")；render loop 派生 `isActorEntry` flag (path parts.length===3 且 parts[0]==="ai_videos" 且 parts[1]==="_actors" 且 parts[2] 匹配 ACTOR_ID_RE) + 在该行 render 🗑 按钮（与 `_actors/` 的 🎭 生成演员 sibling pattern）；按钮 in-flight label "删除中…"
- `src/styles.css` 加 `.actor-delete-btn` rule（与 `.drama-rename-btn` 同基线尺寸；hover 时 border-color → `var(--error-border, #c53030)`；disabled opacity 0.55）

Spec / validation:
- `final_specs/spec.md` 新增 **FR-9i** `POST /api/actors/delete` 完整契约：body shape / cascade-first 顺序 / 状态码 / 符号链接 reject / `_next_actor_id_num` 不扫 `_deleted/` 故 ID 可复用 / EXPOSED_TREE 不变；扩 **FR-87** 加 row-level 🗑 按钮描述（hides under `_deleted/`）
- `validation/security.md` carve-out 加 **#7-bis**：4 项硬化 (actor_id shape strict、source/target 完全 derived 无 user-path、symlinks reject、atomic rename) + 3 项 residual risk (GUARDED_ROUTES gap 与 carve-out #7 同步、ID 复用是 intentional v1、cascade multi-file 非原子 race window) + coverage matrix 加 FR-9i 行 → `SEC-ACTORS-DELETE`
- `validation/acceptance_criteria.md` 加 **U3.17** scenario：fixture 2 个 actor + 2 个 drama casting.md → POST /api/actors/delete → 验证 unassigned 列表 + folder 移动 + casting.md 重写 + 重复删除返 404 + shape 400 + 不存在 actor 404 + ID slot 复用 + 405；coverage 矩阵加 `FR-9i | U3.17 (actors/delete，follow-up 026)`

User-input:
- `user_input/revised_prompt.md`：composed-from 加 026；Last regenerated 改 2026-05-12 23:10:14；header summary 重写为 026 范围；prior follow-up 025 标记为 "保持有效；026 在其上加新写入面 `POST /api/actors/delete`"

Auto-updated:
- `projects/ai_video_management/backend/libs/actor_pool.py` — 4 个新 exceptions + `delete_actor()` 方法 + `__all__` 扩展
- `projects/ai_video_management/backend/libs/casting.py` — `unassign_actor_everywhere()` 方法
- `projects/ai_video_management/backend/libs/api.py` — import 扩展 + `DeleteActorBody` + `POST /api/actors/delete` 实现 + method-not-allowed handler + docstring endpoint count 15
- `projects/ai_video_management/frontend/src/api.ts` — `DeleteActorResult` + `deleteActor()`
- `projects/ai_video_management/frontend/src/components/Sidebar.tsx` — 🗑 button + state + callback + 派生 flag
- `projects/ai_video_management/frontend/src/styles.css` — `.actor-delete-btn` rule
- `specs/development/ai_video_management/final_specs/spec.md` — FR-9i 新增 + FR-87 扩展
- `specs/development/ai_video_management/validation/security.md` — carve-out #7-bis + coverage matrix FR-9i 行
- `specs/development/ai_video_management/validation/acceptance_criteria.md` — U3.17 scenario + coverage matrix FR-9i 行
- `specs/development/ai_video_management/user_input/revised_prompt.md` — header / composed-from / 026 summary
- `specs/development/ai_video_management/user_input/follow_ups/026-20260512-231014-actor-folder-delete.md` (NEW)

No conflicts found in:
- follow-up 023（mp4 delete）: 026 在 sub-path mirroring + soft-delete 语义上对齐；不抢同一文件路径（mp4 = file，026 = folder）
- follow-up 025（Kling-only provider）: 026 不动 actor_pool 的 Kling 调用面；新 `delete_actor` 与 Kling provider 独立
- follow-up 014（casting workflow）: 026 通过 cascade 主动保持 casting.md 一致；不破坏 FR-9g / FR-9h
- follow-up 022（sidebar collapse-all）: 026 加新按钮但不动 expand state 逻辑
- 已生成的 `_actors/actor_0001..0009/` 文件夹: 用户使用新按钮后会软删除，原 sidecar 内容（提到 "pollinations.ai" 的历史 artifact）随 folder 移到 `_deleted/_actors/`，不会被修改
- backend tests: 现有 7 boot-smoke 测试不依赖 actor_pool 写入面，未受影响

Verification (inline smoke):
- `python -c "from libs.actor_pool import ActorNotFound, ActorDeleteFailed, ActorDeleteTargetExists, ActorAlreadyDeleted; from libs.casting import Casting; from libs import api; print(hasattr(Casting,'unassign_actor_everywhere'), hasattr(api,'DeleteActorBody'))"` → `True True` ✓
- `pytest tests/test_boot_smoke.py`：**7/7 通过** ✓
- 全套 `pytest tests/`：18 pass / 5 pre-existing fail (与 follow-up 025 完成时同样的 5 个 wukong_juexing-fixture-missing failures，零回归)

## Follow-up 025 — 2026-05-12 22:51:47
Source: user_input/follow_ups/025-20260512-225147-kling-only-provider-and-env-file.md
Summary: 用户："Lets remove the rest options to generate pictures, only use kling api key, here is the key you can put it in some local env file that is not tracked by git" + 直接提供 Access/Secret Key。**把 face generation 收窄为 Kling-only**：删除 follow-up 021 引入的 multi-provider chain (Pollinations + AI Horde) + follow-up 024 的 chain-fallback 静默 skip 行为；Kling env vars 升为 **required**，缺失时启动期 failfast。**凭证存储**：新增 `projects/ai_video_management/backend/.env`（根 `.gitignore` `.env` pattern 已覆盖，不入 git）+ stdlib `libs/env_loader.py`（KEY=VALUE 解析，**不引入 python-dotenv**）+ `main.py` 与 `libs/asgi.py` 启动期 `load_env_file()`。

Backend:
- `libs/actor_pool.py` 重写：删除 `PollinationsProvider` + `AIHordeProvider` + `Provider` Protocol + `ProviderChain` + `_FetcherShimProvider` + `HttpFetcher` + `_default_fetcher` + `_parse_retry_after` + `_RETRY_BACKOFFS_SECONDS` + `_RETRY_AFTER_CAP_SECONDS` + `POLLINATIONS_BASE` + `_build_pollinations_url` + 全部 `AIHORDE_*` 常量 + `PROVIDERS_ENV_VAR` + `_DEFAULT_PROVIDER_NAMES` + `_PROVIDER_FACTORIES` + `_build_default_chain`
- `KlingProvider` 保留并升为唯一 provider；`from_env()` 行为不变；`ActorPool.__init__` 移除 `fetcher` + `chain` kwargs，新增 `provider: KlingProvider | None`；缺 env → 构造期 `RuntimeError("kling env keys missing; set KLING_ACCESS_KEY + KLING_SECRET_KEY ...")`
- `_build_sidecar` 字符串 "AI-generated actor face (pollinations.ai, follow-up 014)" → "(Kling text-to-image, follow-up 025)"
- `__all__` 收窄到 Kling-only + 通用常量
- `libs/env_loader.py` (NEW)：~30 行 stdlib `load_env_file(path: Path) -> int`；skip 空行 + `#` 注释；只 `os.environ.setdefault`（已存在 env 优先）；FileNotFoundError + OSError → return 0
- `main.py`：`load_env_file(Path(__file__).resolve().parent / ".env")` 在 import `libs.api` 前调用
- `libs/asgi.py`：同上，`Path(__file__).resolve().parent.parent / ".env"` (从 libs/ 上一级)

Frontend:
- `frontend/src/components/ActorPoolGenerator.tsx`：删除 `INTER_REQUEST_THROTTLE_MS = 2000` 常量 + 主循环 `await setTimeout(2000)` 块；删除 `phase: "throttling"` 状态 (`Progress.phase` 收窄到 `"idle" | "generating"`)；删除 ProgressPanel "⏸ 等待限速冷却…" 分支 + footer "等待 2s 防限速…" 按钮文本；删除 `<p className="rate-limit-hint">ℹ️ pollinations.ai 免费 endpoint 有限速 …</p>` banner
- `frontend/src/styles.css`：删除 `.rate-limit-hint { ... }` 整个 rule block（follow-up 018 引入的 CSS class 已无引用）

Spec / validation:
- `final_specs/spec.md` FR-9f 重写：删除 (a) Pollinations + (b) AI Horde 段；保留 Kling 段并提到 Kling env vars 升 required + .env 加载流程 + failfast；删除 `AI_VIDEO_MGMT_FACE_PROVIDERS` 提及；FR-9 master 注释 "outbound HTTP calls (pollinations.ai)" → "Kling text-to-image per follow-up 025"
- `validation/security.md` carve-out #7 重写：从 3-provider chain hardening 收窄为 Kling-only；新增 .env 加载流程 + .env 文件不在 EXPOSED_TREE (`projects/` 不在 FR-7 的 5 个 root 内) 的说明；residual risks 收窄为 (i) Kling 单点 + (ii) Kling CDN TOCTOU + (iii) 内容过滤 + (iv) 内网 egress
- `validation/security.md` 全文 `SEC-OUTBOUND-POLLINATIONS` → `SEC-OUTBOUND-KLING`（两处）
- `validation/acceptance_criteria.md` U3.15：标题 + Given 行的 monkey-patch 注释改为 Kling；新增 "KLING env 已设" precondition

User-input:
- `user_input/revised_prompt.md`：composed-from 加 025；Last regenerated 改 2026-05-12 22:51:47；header summary 替换为 025 内容（删除 024 长 summary 文本但保留 follow-up 024 reference）；Prior follow-up 024 标记为 "已被 025 部分覆盖：KlingProvider + JWT + aspect ratio mapper + SSRF-vet 保留，chain 抽象删除"

Auto-updated:
- `projects/ai_video_management/backend/.env` (NEW，untracked) — Kling access + secret key
- `projects/ai_video_management/backend/libs/env_loader.py` (NEW) — stdlib KEY=VALUE 加载器
- `projects/ai_video_management/backend/libs/actor_pool.py` — Kling-only 重写 (~340 行 net delete)
- `projects/ai_video_management/backend/main.py` — `load_env_file()` 调用
- `projects/ai_video_management/backend/libs/asgi.py` — `load_env_file()` 调用
- `projects/ai_video_management/frontend/src/components/ActorPoolGenerator.tsx` — throttle + hint UI 删除
- `projects/ai_video_management/frontend/src/styles.css` — `.rate-limit-hint` CSS 删除
- `specs/development/ai_video_management/final_specs/spec.md` — FR-9f Kling-only 重写
- `specs/development/ai_video_management/validation/security.md` — carve-out #7 Kling-only 重写 + SEC-OUTBOUND-KLING rename
- `specs/development/ai_video_management/validation/acceptance_criteria.md` — U3.15 Kling
- `specs/development/ai_video_management/user_input/revised_prompt.md` — header / composed-from / 025 summary
- `specs/development/ai_video_management/user_input/follow_ups/025-20260512-225147-kling-only-provider-and-env-file.md` (NEW)

No conflicts found in:
- `frontend/src/api.ts` / `frontend/src/components/Sidebar.tsx` / `frontend/src/components/Reader.tsx` / `frontend/src/components/ImageRefView.tsx`：HTTP API shape (`POST /api/actors/generate`) 不变
- `backend/libs/api.py` / `backend/libs/casting.py` / `backend/libs/media_archiver.py`：`ActorPool(exposed, resolver)` 构造签名兼容（新增的 `provider` kwarg 是可选）
- `backend/tests/`：无 actor_pool 测试 (follow-up 014-024 推迟 pytest)，无 `fetcher=` / `chain=` 引用，零回归
- 已生成的 `ai_videos/_actors/actor_0001..0009/actor_NNNN.md` sidecar 中 "pollinations.ai, follow-up 014" 字样：保留为历史 artifact（未来 regen 才覆盖）
- follow-up 014-024 follow-up draft 文件本身：保留为审计历史，不删
- `.claude/skills/agent_team/` 与 `.claude/agent_refs/`：本 follow-up 是 project-scoped instruction，不动 common surface

Verification (inline smoke):
- `load_env_file(backend/.env)` 加载 2 个 keys ✓；二次调用 already-set env 不被覆写 ✓；missing file → 0 ✓
- `actor_pool.__all__` 收窄；`PollinationsProvider` / `AIHordeProvider` / `ProviderChain` / `_FetcherShimProvider` / `POLLINATIONS_BASE` / `AIHORDE_BASE_URL` / `PROVIDERS_ENV_VAR` / `_build_default_chain` / `HttpFetcher` / `Provider` 全部 `hasattr` 为 False ✓
- `KlingProvider.from_env()` 加载 env 后返 `KlingProvider` instance ✓
- `_make_kling_jwt('AKtest','SKtest', exp_seconds=60)` 仍生成 3-part JWT ✓
- `ActorPool(FakeExposed, FakeResolver)` 在缺 env 时 raise `RuntimeError("kling env keys missing ...")` ✓
- `pytest tests/test_boot_smoke.py`: **7/7 通过** ✓
- 全套 `pytest tests/`: 18 pass / 5 pre-existing fail (sub_type_lookup / tree_walker + 2 origin-host edge — 全部在 stashed pre-025 tree 上同样 5 fail，零回归)
- Frontend `tsc --noEmit`：仅 vite.config.ts 的 2 个 pre-existing `path` typing 错误，actor-pool / sidebar 编辑零 error

## Follow-up 024 — 2026-05-12 23:30:00
Source: user_input/follow_ups/024-20260512-233000-kling-text-to-image-provider.md
Summary: 用户提议 "if I give you kling text to image api, would that help?" 后，先 push back 之前用户提的方案 A (TPDNE — StyleGAN/FFHQ documented Asian bias，命中率仅 10-30%，需 ML classifier 或人工 curation) 与方案 C (Generated.Photos — ToS 明禁 "caching, stockpiling, or downloading photos as stand-alone files")，研究确认两者均不可行；Kling 是真正适配（商业级 + 用户已有 access + ~1-3s/img + prompt-based attribute control）。**加 Kling 作为第 3 个 face provider，放 chain 首位**。

实现:
- 新增 `KlingProvider` 类：JWT HS256 + async submit + poll + r2-CDN download；遵循 follow-up 021 引入的 Provider Protocol
- `_make_kling_jwt(ak, sk)`：纯 stdlib (`hmac` + `hashlib` + `json` + `base64`)，3-segment JWT (header.payload.signature)，claims `{iss: ak, exp: now+1800, nbf: now-5}`；**不引入 `PyJWT` 依赖**
- `_kling_aspect_ratio(width, height)`：从 (512, 512) 推断 "1:1" / "16:9" / "9:16" / "4:3" / "3:4"（Kling 不接受任意分辨率必须 enum）
- `KlingProvider.from_env()`：lazy 读 `KLING_ACCESS_KEY` + `KLING_SECRET_KEY` env vars，缺任一返 None 让 chain factory 静默跳过
- 流程: POST `https://api.klingai.com/v1/images/generations` `{model_name: "kling-v1", prompt, aspect_ratio, n: 1}` → 检 `code == 0` → 拿 `data.task_id` → poll GET `/v1/images/generations?pageSize=500` 每 2s（max 120s）→ 找匹配 task → 检 `task_status == "succeed"` (or `"failed"` → raise) → `task_result.images[0].url` → 复用现有 `_is_safe_download_host` SSRF-vet → download with `follow_redirects=True` + 30s timeout + 5MB cap
- `_PROVIDER_FACTORIES["kling"] = lambda: KlingProvider.from_env()` —— factory 可返 None
- `_build_default_chain` 加 `if instance is None: continue` 支持 None-returning factories
- `_DEFAULT_PROVIDER_NAMES = ("kling", "pollinations", "aihorde")` —— Kling 优先；factory None→skip 让无 env 用户自动降级回 follow-up 021 chain（零 breaking change）
- `__all__` 加 `KlingProvider` / `KLING_BASE_URL` / `KLING_ACCESS_KEY_ENV` / `KLING_SECRET_KEY_ENV` / `KLING_DEFAULT_MODEL`

Spec / validation:
- `final_specs/spec.md` FR-9f 加 provider (c) Kling 描述：JWT HS256 stdlib-only 实现 + claims + async POST+poll+download 流程
- `validation/security.md` carve-out #7 hardening (g-bis): KLING_SECRET_KEY 仅 env 读、仅 `hmac.new` 输入用、不 log / 不进 URL / 不进 response；KLING_ACCESS_KEY 在 JWT `iss` claim 是 identifier 非 secret；`code != 0` 显式检查；JWT 每次 generate() 现生（30 分钟有效期，无 stale 风险）

前端零改动 — chain 对调用方透明，HTTP API shape 不变。

Auto-updated:
- `specs/development/ai_video_management/user_input/revised_prompt.md` — Last regenerated 改 2026-05-12 23:30:00；Composed-from 加 follow-up 024；header 摘要描述 push back 两方案 + Kling 选型 + 实现 + verification；prior follow-up 023 line 移到 prior 列表
- `projects/ai_video_management/backend/libs/actor_pool.py` — 新增 ~150 行 KlingProvider + JWT helpers + aspect ratio mapper + provider factory；`_PROVIDER_FACTORIES` 加 "kling" slot；`_build_default_chain` 支持 None-returning factory；`_DEFAULT_PROVIDER_NAMES` 加 "kling" 在最前；`__all__` 扩展
- `specs/development/ai_video_management/final_specs/spec.md` — FR-9f provider 列表加 (c) Kling
- `specs/development/ai_video_management/validation/security.md` — carve-out #7 (g-bis) Kling secret 硬化
- `specs/development/ai_video_management/user_input/follow_ups/024-20260512-233000-kling-text-to-image-provider.md` (NEW) — full follow-up draft 含 评估 / Kling API 摘要 / 实现 / 安全 / 不在范围

Verification (inline smoke):
- `from libs.actor_pool import KlingProvider, _make_kling_jwt, _kling_aspect_ratio, _build_default_chain, _DEFAULT_PROVIDER_NAMES` 全部 import 成功
- JWT 生成 byte-equality verify：解码 header `{"alg":"HS256","typ":"JWT"}` ✓；payload `{iss, exp, nbf}` 正确；signature `hmac.new(sk, header.payload, sha256)` byte-byte 匹配 ✓
- aspect ratio: 512×512 → "1:1"，1920×1080 → "16:9"，1080×1920 → "9:16" ✓
- `KlingProvider.from_env()`：无 env → None ✓；有 env (ak+sk) → KlingProvider instance ✓
- `_DEFAULT_PROVIDER_NAMES == ('kling', 'pollinations', 'aihorde')` ✓
- `_build_default_chain()` 有 env → `('kling', 'pollinations', 'aihorde')` ✓；无 env → graceful fallback `('pollinations', 'aihorde')` ✓
- `make boot-smoke`: **7/7 通过** ✓

No conflicts found in:
- 与 follow-up 023 (delete-media + `_deleted/`) 完全正交 —— 一个改 frontend reader + media_archiver，一个改 backend actor_pool outbound HTTP
- 与 follow-up 022 (sidebar collapse-all) 正交
- 与 follow-up 021 (multi-provider chain) 增强：在其 Provider 抽象基础上加新 provider 类
- 与 follow-up 020 / 019 (archive UI for direct media views) 正交
- 与 follow-up 018 (pollinations retry) 兼容：PollinationsProvider 仍封装 follow-up 018 retry 逻辑；Kling 不复用同样 retry (Kling 商业 endpoint 限速远松，简单 raise + chain failover 已足够)
- `validation/acceptance_criteria.md` U3.15 / U3.16 — pytest fixture 仍用 `fetcher=lambda` 路径通过 `_FetcherShimProvider`；Kling 不参与，无 conflict
- 所有 frontend 组件 / 其他 backend libs / casting.md / media archiver / api.py — 零影响

User next step:
1. 在 `app.klingai.com/global/dev` 创建账号 → API keys page → 拿 Access Key + Secret Key
2. PowerShell: `$env:KLING_ACCESS_KEY = "<your_ak>"` + `$env:KLING_SECRET_KEY = "<your_sk>"`
3. `make run-backend` 重启 backend 让 env 生效（`--reload` 只追代码改动，不追 env）
4. 点 "🎭 生成演员" → chain 现在 `kling,pollinations,aihorde` → 第 1 张走 Kling (~1-3s)，第 2 张走 pollinations，第 3 张走 AI Horde，第 4 张 wrap 回 Kling…
5. 若不设 env：chain 自动降级回 `pollinations,aihorde`，**完全没变化**，零风险
6. 单 Kling-only：`$env:AI_VIDEO_MGMT_FACE_PROVIDERS = "kling"` (跳过 pollinations + AI Horde fallback；要求 Kling 100% 可用)

Severity: Medium. Performance / user-blocking 真长效解（kling 商业级速度 10-30× 快过现有 free providers）；按用户 explicit 提议实现；零 breaking change（无 env 自动降级回 follow-up 021 chain）；secret handling hardening 已落地（hmac 计算 + 不 log + 不 leak）。改动范围：1 backend lib 加新类（~150 行）；前端零变动；API endpoint shape 零变动；安全 carve-out 扩展但所有新硬化点已落地。

## Follow-up 023 — 2026-05-12 22:15:39
Source: user_input/follow_ups/023-20260512-221539-delete-media-to-deleted-folder.md
Summary: mp4 / image reader 加 Delete 按钮 — soft-move 当前文件到 `ai_videos/_deleted/{保留 ai_videos 之下的子路径}`。新 backend endpoint `POST /api/delete-media` + 前端 Reader.tsx 双按钮 row（Archive + Delete）+ `_deleted/` 内文件两按钮全部隐藏。

Auto-updated:

**user_input:**
- `revised_prompt.md` — header bump：composed-from 末尾加 follow-up 023；Last regenerated 时间戳更新；follow-up 022 / 021 / 020 demote to "Prior"；新写 follow-up 023 summary（详述端点 mapping、target path 保留子结构、`_deleted/` 内按钮隐藏规则、警示红色 hover、不引入 in-app restore）。

**Generated outputs:**
- `backend/libs/media_archiver.py` —
  - 模块 docstring 加一段说明 follow-up 023 delete 行为。
  - 新增常量 `DELETED_DIR_NAME = "_deleted"`、`AI_VIDEOS_ROOT_NAME = "ai_videos"`。
  - 新增 exceptions `AlreadyDeleted`、`NotInAiVideos`。
  - `MediaArchiver` 新增 method `delete(self, rel: str) -> MoveResult`：复用 `_validate_media_source` 做 ext/sandbox/symlink 校验；relative parts[0] != "ai_videos" → `NotInAiVideos`；parts[1] == "_deleted" → `AlreadyDeleted`；target = `resolver.root / "ai_videos" / "_deleted" / Path(*parts[1:])`；`target.parent.mkdir(parents=True, exist_ok=True)`；target 存在 → `TargetExists`；`src.rename(target)` atomic；不删 src 原 parent。
- `backend/libs/api.py` —
  - 模块顶部 docstring：13 endpoints → 14 endpoints，列表加 `POST /api/delete-media`。
  - import from `media_archiver` 加 `AlreadyDeleted`、`NotInAiVideos`。
  - 新 endpoint `POST /api/delete-media` 复用 `ArchiveMediaBody` schema；mapping：InvalidPath→400 `invalid_path` / NotMedia→400 `extension_not_allowed` / NotInAiVideos→400 `not_in_ai_videos` / AlreadyDeleted→400 `already_deleted` / NotFound→404 `not_found` / TargetExists→409 `target_exists` / MoveFailed→500 `move_failed`。
  - 对应 method_not_allowed handler GET/PUT/PATCH/DELETE → 405 + Allow: POST。
- `frontend/src/api.ts` — 加 `export async function deleteMedia(path: string): Promise<ArchiveMediaResult>` POST `/api/delete-media`，复用 `ArchiveMediaResult` 类型。
- `frontend/src/components/Reader.tsx` —
  - import 加 `deleteMedia` from `../api`。
  - 加 `deleting: boolean` state。
  - 加 `onDeleteClick` useCallback (依赖 `[path, onSaved, navigate]`)：`window.confirm` 拦一次，确认后 `deleteMedia(path)` → 成功 announce + `onSaved()` + `navigate(/file/encoded)` → 失败 announce 错误 + button re-enable。
  - 派生 `isDeletedFile = path.startsWith("ai_videos/_deleted/")`、`mediaActionsBusy = archiving || deleting`、`deleteLabel`（`🗑 Delete` / `Deleting…`）。
  - `isVideo` / `isMediaImage` 分支：原 single archive button 包入新 `<div className="reader-media-actions">` flex row + Delete button；整个 actions 块在 `!isDeletedFile` 下渲染（`_deleted/` 内文件两按钮都隐藏，视频/图片仍正常播放）。
  - 两按钮共享 busy guard `disabled={mediaActionsBusy}` 防止并发 archive + delete。
- `frontend/src/styles.css` — 加 `.reader-media-actions`（flex row + justify-content center + gap 10px）+ `.reader-media-delete-btn`（基线尺寸同 archive；hover → color `--error-text` / bg `--error-bg` / border-color `--error-border` 警示红，全部复用既有 light-theme error 色板不引入新色）。

No conflicts found in: `SiblingMedia.tsx`（未触碰；批量 archive grid 仍服务 markdown / imageRef / shotPair 分支）; `Sidebar.tsx`（`_deleted/` 默认 walk 进 tree，无需 EXCLUDED_DIRS 改动；follow-up 022 的 collapse-all 让噪声可控）; `App.tsx`（onSaved 仍触发 tree refresh）; `exposed_tree.py`（`_deleted/` 不在 `_EXCLUDED_DIRS`，默认可见，与 `_actors/` 一致）; `_validate_media_source`（沿用 archive 路径校验链）; `interview/qa.md`, `findings/dossier.md`, `final_specs/spec.md`, `validation/*`（均未 prescribe 唯一目录布局 / 唯一移动语义 — follow-up 008 + 011 + 019 + 020 + 023 是 UX 渐进迭代）。

Verification (静态 reasoning + manual smoke 路径)：
- 后端：`media_archiver.delete("ai_videos/mozun/characters/c1/c1_1.mp4")` 预期返回 `{from: "ai_videos/mozun/characters/c1/c1_1.mp4", to: "ai_videos/_deleted/mozun/characters/c1/c1_1.mp4"}`；新建链上每级目录；原 c1/ folder 不删。
- 后端边界：non-media ext → `extension_not_allowed`；non-`ai_videos/` 路径 → `not_in_ai_videos`；已在 `_deleted/` 下 → `already_deleted`；target 已存在（罕见：先 delete 再撤销再 delete）→ `target_exists`。
- 前端：mp4 reader 显示 `<video>` + 两按钮 row；点 Delete → confirm 弹窗 "Move {filename} to _deleted/?"；OK → 请求 + navigate；Cancel → 不发请求。点 Archive 与 Delete 期间双向 disabled。点进已在 `_deleted/` 下的视频 → 视频正常播放，两按钮都不渲染。
- 安全：Origin/Host gate + sandbox + symlink reject + atomic rename 沿用既有契约，无新 carve-out。

## Follow-up 022 — 2026-05-12 22:07:24
Source: user_input/follow_ups/022-20260512-220724-sidebar-collapse-all-icon.md
Summary: Sidebar 顶部加 collapse-all 图标按钮 — 点击 `⊟` 折叠左 nav 全部 folder 节点。Toolbar 行紧贴 sidebar 顶部、`renameToast` 之上；状态利用现有 `expanded: Record<string,boolean>`，与 line-50 tree-init effect 的合并顺序天然兼容（collapse 跨 tree refresh 持久，新 folder 仍默认展开）。

Auto-updated:

**user_input:**
- `revised_prompt.md` — header bump：composed-from 末尾加 follow-up 022；Last regenerated 时间戳更新；follow-up 021 从 latest 降为 "Prior follow-up 021"；新写 follow-up 022 summary。

**Generated outputs:**
- `frontend/src/components/Sidebar.tsx` —
  - 加 `onCollapseAll` useCallback（依赖 `[tree]`）：walk tree → 把所有 `type` 非 file/image/video 的节点 path 收集进 `accum: Record<string, boolean>` 都设为 `false` → `setExpanded(accum)` 直接覆盖 prev。
  - 在 `<nav className="sidebar">` 内、`renameToast` 渲染之前，插入 `<div className="sidebar-toolbar">` 内置单按钮 `<button className="sidebar-collapse-all" aria-label="折叠全部" title="折叠全部 · Collapse all folders" onClick={onCollapseAll}>⊟</button>`。
  - 不动 line-50 / line-62 useEffect（tree-init 默认 expand-all 行为对新 folder 仍正确；`prev` 覆盖让 collapse 状态跨 tree refresh 持久）。
  - 不动 keyboard navigation / ActorPoolGenerator / renameToast 等既有 sidebar 功能。
- `frontend/src/styles.css` — 紧贴 `.sidebar-loading` 之后新增 `.sidebar-toolbar`（flex row + justify-content flex-end + border-bottom var(--border) + bg var(--bg-sidebar) + padding 4px 10px 6px）与 `.sidebar-collapse-all`（transparent bg / muted color / 16px / padding 2px 8px / border-radius 3px / hover → text + bg-toolbar + border / focus-visible → 2px solid var(--border-strong) outline）。

No conflicts found in: backend（纯前端 client-side state，零调用后端）; `App.tsx`（sidebar 仍接 `tree / currentPath / onSelect / onTreeReload` 旧 props，零 prop 签名变化）; `ActorPoolGenerator.tsx`（modal 触发逻辑不变）; `interview/qa.md`, `findings/dossier.md`, `final_specs/spec.md`, `validation/*`（均未 prescribe sidebar 必须无 toolbar / 默认全展开为契约 — 本 follow-up 是 UX 增量不是契约破坏）。

Verification (静态 reasoning)：点击按钮 → `setExpanded(allFalseMap)` → flat memo 重算 → 任何 `depth > 0` 的节点 `isOpen = expanded[path] === true` 为 `false` → 子节点不被 walk 进 flat array → 视觉上只剩 top-level；`depth === 0` 由 line 97 强制 `isOpen=true` 不受影响。用户实测路径 `ai_videos/mozun_chongsheng/characters/c1_沧冥/c1_沧冥1.mp4`：点 collapse-all 后 sidebar 应只看到 `ai_videos/`（或其下两个 top-level drama 名），其余隐藏；breadcrumb + reader 仍显示当前文件路径，用户可手动重新展开。键盘 Tab 到 button 后 Enter / Space 都触发 onCollapseAll。Focus-visible outline 走 `--border-strong` (#afb8c1) 已定义。

## Follow-up 021 — 2026-05-12 23:00:00
Source: user_input/follow_ups/021-20260512-230000-multi-provider-face-generation.md
Summary: 应用户提议"is pollination.ai the only site you could download free ai generated pictures? is there any other free alternative?"引入 **multi-provider face generation 架构**。Research 9 个候选（pollinations / AI Horde / Cloudflare Workers AI / Together AI / HuggingFace Inference / Puter.js / DeepAI / ZSky / Generated.Photos）；否决 Generated.Photos (ToS 禁 download)、Puter.js (browser-only 无 server-side path)、其他需要 signup / token / cold start 的。用户答**保留 pollinations + AI Horde fallback**（不引入 Cloudflare 因要 signup），策略 **round-robin per image with failover**。

Backend 重构：
- 新增 `Provider` Protocol：`name: str` + `generate(prompt, seed, width, height) -> bytes`
- 新增 `PollinationsProvider`：封装 follow-up 018 的 `_default_fetcher` 重试逻辑 + URL 构建。行为契约不变（3 retries on 429 + timeout，Retry-After honored capped 60s）
- 新增 `AIHordeProvider`：async POST→poll→download；base URL `https://aihorde.net/api/v2` + anonymous apikey `"0000000000"` 写死；流程 POST `/generate/async` → poll `/generate/check/{id}` 每 5s 直到 `done:true` 或 `faulted:true` (max 180s) → GET `/generate/status/{id}` 拿 `generations[0].img` (r2.dev URL) → SSRF-vet hostname (`_is_safe_download_host`: https only + 拒 loopback/RFC1918/link-local/multicast/reserved IPs via `socket.getaddrinfo`) → GET 该 URL with `follow_redirects=True` + 30s timeout + 5MB cap
- 新增 `ProviderChain` 类：`__init__(providers)` 拒空 list；`generate(...)` 每次前进 index 1 (round-robin)，失败时 fall through 同 chain 余下 provider 直到一个成功或全失败；全失败抛 `RuntimeError` 含 `last_exc` chain + 所有 provider 失败原因汇总
- 新增 `_FetcherShimProvider`：把 legacy callable `(url, timeout, max_bytes) -> bytes` 包成 Provider，让现有测试 `fetcher=lambda` 参数继续 work 无需重写
- 新增 `_build_default_chain()`：读 env var `AI_VIDEO_MGMT_FACE_PROVIDERS` (默认 `"pollinations,aihorde"`)，map 到工厂 dict；garbage 输入降级为单 pollinations chain
- `ActorPool.__init__` 签名扩展 `fetcher | chain | (env default)` 三路：fetcher 路径走 shim，chain 路径直接用，默认路径 `_build_default_chain()`
- `generate_batch` 把 `self._fetcher(url, ...)` 改为 `self._chain.generate(prompt, seed, IMAGE_WIDTH, IMAGE_HEIGHT)`；URL 构建从 ActorPool 移到 PollinationsProvider 内部
- 删除 `ActorPool._build_url` 静态方法（已下沉到 provider）

Spec / validation 改动：
- `final_specs/spec.md` FR-9f 重写：扩展为"通过 ProviderChain 调度，round-robin per image with failover"，列两 provider 完整流程契约
- `validation/security.md` Open carve-out #7 扩展：双 provider 各自的硬化（pollinations no-redirect / AI Horde SSRF-vet + follow-redirect 安全），加 4 类残余风险（双 provider 可用性依赖 / SSRF TOCTOU 子毫秒窗 / 无内容过滤 / localhost 触发外部 IO）

前端零改动 — chain 对调用方透明，`POST /api/actors/generate` body / response shape 不变。follow-up 017 frontend loop + follow-up 018 throttle 全部继续 work。

Auto-updated:
- `specs/development/ai_video_management/user_input/revised_prompt.md` — Last regenerated 改 2026-05-12 23:00:00；Composed-from 加 follow-up 021；header 摘要描述 research 否决理由 + 两 provider 流程 + chain 行为 + verification；prior follow-up 020 line 保留
- `projects/ai_video_management/backend/libs/actor_pool.py` — 完全重构 outbound HTTP 层：新增 ~200 行 Provider 抽象 + AIHordeProvider 实现 + ProviderChain 实现 + env-driven 默认工厂；删除 `ActorPool._build_url`；调整 `ActorPool.__init__` 接受 `chain` 参数 + 内部用 `self._chain.generate(...)`；imports 加 `socket` / `ipaddress` / `os` / `urlparse` / `Protocol`；模块 docstring + `__all__` 更新
- `specs/development/ai_video_management/final_specs/spec.md` — FR-9f 改写
- `specs/development/ai_video_management/validation/security.md` — Open carve-out #7 改写
- `specs/development/ai_video_management/user_input/follow_ups/021-20260512-230000-multi-provider-face-generation.md` (NEW) — full follow-up draft 含 research summary + 用户决策 + 架构设计 + 安全 / 边界扩展 + 不在范围

Verification (inline smoke checks):
- imports: 所有新 symbol (Provider / ProviderChain / PollinationsProvider / AIHordeProvider / `_build_default_chain` / PROVIDERS_ENV_VAR / `_is_safe_download_host`) 全部 import 成功
- `_build_default_chain()` 默认 → `('pollinations', 'aihorde')`
- `_is_safe_download_host`: sandbox 环境 DNS 受限故全 False（safe default）；reject `http://` (无 https) / `https://127.0.0.1` / `https://localhost` 均确认；生产 user 机器能 resolve `cdn.aihorde.net` → admit
- ProviderChain round-robin: A + B chain 调 3 次，A 始终 fail → A.calls=2 (起步位 0,_,0) + B.calls=3 (always 接管或起步) → 与设计一致
- ProviderChain failover: A fail + B ok → A.calls=1 + B.calls=1 + 返回 B bytes
- ProviderChain all-fail: 全 fail → RuntimeError 含 "all providers failed: A: ...; B: ..."
- ProviderChain([]) → ValueError
- ActorPool 集成: poll-always-fail + horde-ok chain → generate_batch(count=3) → 3 actor 全成功通过 horde 落盘
- Back-compat fetcher: `ActorPool(..., fetcher=lambda u,t,m: bytes)` → 仍能 generate 2 actor 通过 shim
- env var: `pollinations` → `('pollinations',)`；`aihorde,pollinations` → 逆序；`unknown,garbage` → 降级为 `('pollinations',)`
- `make boot-smoke`: **7/7 通过**（含 follow-up 014 加的 5 endpoint registration 断言）

No conflicts found in:
- `backend/libs/casting.py` / `media_renamer.py` / `media_archiver.py` / `downloads_importer.py` / `api.py` — 零影响；`api.py` 只用公共接口 `ActorPool` / `ActorAttrs` / `InvalidAttribute` / `GenerationDirMissing`，签名不变
- 所有前端组件 — chain 对前端透明，HTTP API shape 不变
- `validation/acceptance_criteria.md` Scenario U3.15 / U3.16 — 仍 valid；测试 fixture 用 `fetcher=lambda` 路径，通过 `_FetcherShimProvider` 走通
- 与 follow-up 020 (mp4 page single archive button) 完全正交

User next step:
1. Backend `--reload` (follow-up 012 默认) 自动检测 `libs/actor_pool.py` 改动 + reload。无需手动重启。
2. 可选设置 env var：PowerShell `$env:AI_VIDEO_MGMT_FACE_PROVIDERS = "pollinations,aihorde"` (默认值)；或 `"aihorde,pollinations"` 让 AI Horde 优先；或 `"aihorde"` 单 provider 跳过 pollinations。env 改动需 `make run-backend` 重启才生效（`--reload` 只追代码改动）。
3. 重试 count=20：第 1 张走 pollinations，第 2 张自动走 AI Horde；失败时另一 provider 接管。pollinations 限速但快，AI Horde 慢但无限速；混合后整体 throughput + 成功率应显著提升。
4. AI Horde 首次匿名调用 wait 可能 60-120s（kudos 0 → 队列末位）；后续 wait 通常 20-60s。如希望更快，独立 follow-up 加 Cloudflare Workers AI provider（需用户提供 free tier token）。

Severity: Medium. 用户报告的限速 blocker 的长效解。改动范围：1 backend lib 重构（新增 ~200 行 Provider 抽象 + AIHorde implementation），前端零变动；API 契约 / spec FR-9f 文字扩展但 endpoint shape 不变；安全 carve-out 扩展但所有新硬化点已落地。

## Follow-up 020 — 2026-05-12 21:57:51
Source: user_input/follow_ups/020-20260512-215751-mp4-page-single-archive-button.md
Summary: 收窄 follow-up 019：用户反馈 mp4 / image single-file reader 页面只要一个 archive 按钮，不需要 SiblingMedia grid + checkbox + toolbar。`isVideo` / `isMediaImage` 分支替换为内联 archive/unarchive 按钮，path-based 自动判定方向，成功后导航到新路径。`isImageRef` / `isShotPair` 分支的 SiblingMedia 保留不变。

Auto-updated:

**user_input:**
- `revised_prompt.md` — header bump：composed-from 末尾加 follow-up 020；Last regenerated 时间戳更新；follow-up 019 从 latest 降为 "Prior follow-up 019" 并注明 video + image 分支收窄、imageRef + shotPair 保留；新写 follow-up 020 summary。

**Generated outputs:**
- `frontend/src/components/Reader.tsx` —
  - import 加 `useNavigate` from react-router-dom、`archiveMedia` + `unarchiveMedia` from api。
  - 加 `archiving: boolean` state。
  - 加 `onArchiveToggle` useCallback：path 分段，`parts[length-2] === 'archive'` 判定 inArchive；调用 unarchive 或 archive；成功 `announceToast` + `onSaved()` + `navigate(/file/encoded)` 到新路径；失败公告。
  - 派生 `isArchivedFile` + `archiveLabel`（`📦 Archive` / `↺ Unarchive` / `Archiving…` / `Unarchiving…`）。
  - `isVideo` 分支：移除 follow-up 019 加的 `<SiblingMedia>`，回到单 `<div className="media-view">`，里面 `<video>` 之下加 `<button className="reader-media-archive-btn">`。
  - `isMediaImage` 分支：同上。
  - `isImageRef` / `isShotPair` 分支：**保留 follow-up 019 加的 SiblingMedia 不变**。
  - 文件底部加 module-level `announceToast` + `archiveErrorKind` helpers（与 SiblingMedia.tsx 内同名 helper 行为一致；不抽 util 文件以保持单文件修改）。
- `frontend/src/styles.css` — 新增 `.reader-media-archive-btn` 样式：inline-block、margin-top 12px、padding 6px 14px、light-theme bg-panel + text-muted、hover 时切到 bg-toolbar + text；disabled 时 cursor: progress + opacity 0.55。挂在 `.media-view video { width: 100%; }` 之后。

No conflicts found in: backend (`backend/libs/media_archiver.py` + `POST /api/archive-media` / `POST /api/unarchive-media` 已支持单 path 原子调用); `SiblingMedia.tsx`（未触碰；仍服务 markdown / imageRef / shotPair 分支）; `interview/qa.md`, `findings/dossier.md`, `final_specs/spec.md`, `validation/*`（均未 prescribe 单文件 archive UI 形态 — follow-up 008 + 011 + 019 的描述均为渐进迭代，本 follow-up 是 UX 收窄不是契约破坏）。

Verification: 用户实测路径 `ai_videos/mozun_chongsheng/characters/c1_沧冥/c1_沧冥1.mp4`。预期：reader 上半 `<video>`，正下方一个 "📦 Archive" 按钮；点击后请求 archive endpoint → 文件移到 `c1_沧冥/archive/c1_沧冥1.mp4` → URL 自动跳新路径 → reader 重新加载同一 mp4 但按钮变成 "↺ Unarchive"（用户可立刻 misclick recovery）。Sidebar 同时 refresh 显示新位置。Aria-live toast 公告 "Archived c1_沧冥1.mp4"。点 ImageRefView 或 ShotPairView 路径行为不变（仍显示 SiblingMedia 批量 grid）。

## Follow-up 019 — 2026-05-12 21:43:45
Source: user_input/follow_ups/019-20260512-214345-archive-ui-for-direct-media-views.md
Summary: archive feature 在 character / scene / shot folder 内**只对 markdown reader 可见**的回归 — follow-up 008 (per-tile archive) + 011 (批量 multi-select archive) 完全实现，但 `Reader.tsx` render-mode dispatch 只在 `isMarkdown` 分支挂 `<SiblingMedia>`。用户最自然的工作流是点 sidebar 里的 `.mp4` 直接看，走 `isVideo` 分支 → 没归档 UI。

Auto-updated:

**user_input:**
- `revised_prompt.md` — header bump：composed-from 末尾加 follow-up 019；Last regenerated 时间戳更新；follow-up 018 从 latest 降为 "Prior follow-up 018"；新写 follow-up 019 summary。

**Generated outputs:**
- `frontend/src/components/Reader.tsx` — `reader-body` JSX 内，`isVideo` / `isMediaImage` / `isImageRef` / `isShotPair` 四个分支各挂一份 `<SiblingMedia currentPath={path} knownPaths={knownPaths} onChange={onSaved} />`（props 与既有 markdown 分支完全一致），用 React fragment `<>...</>` 包住。零后端改动、零 CSS 新增、零新 endpoint。`isCasting` / `isShotlistTable` / `isJsonl` / `isCode` / `isTxt` 不挂（drama-root 级文件，无 ref-video 用例）。

No conflicts found in: backend (`backend/libs/media_archiver.py` + `POST /api/archive-media` / `POST /api/unarchive-media` 已支持 011 的批量循环用例); `SiblingMedia.tsx` (返回 `null` 当 `siblings.length === 0 && archived.length === 0` — 单文件文件夹无视觉回归); `styles.css` (复用 008 + 011 已有 grid / toolbar / checkbox 样式); `interview/qa.md`, `findings/dossier.md`, `final_specs/spec.md`, `validation/*` (均未 prescribe SiblingMedia 仅在 markdown 下渲染的 invariant — follow-up 005 的"在 markdown 渲染下方"是描述当时实现而非约束，本 follow-up 是 render-scope 扩展不是契约破坏).

Verification: 用户实测路径 `ai_videos/mozun_chongsheng/characters/c1_沧冥/` 含 1 个 `.md` + 8 个 `.mp4`。预期：点 sidebar 任一 mp4 → Reader 上半显示 `<video>`，下半显示 SiblingMedia grid（剩余 7 个 mp4 + 任何同 folder png/jpg），始终可见左上角 checkbox + section toolbar "📁 Folder media · 同 folder 媒体" + "Select all" / "Clear" / "📦 Archive Selected (N)"。Scene `s1_长阶顶/` (4 mp4)、shot folder 同 grid 行为。`isImageRef` (`_seedream.md`) + `isShotPair` 同样受惠 — 比如 character ref_images folder 内多张 _seedream.md 互为 sibling 时可批量归档实验稿。

## Follow-up 018 — 2026-05-12 22:30:00
Source: user_input/follow_ups/018-20260512-223000-pollinations-rate-limit-retry.md
Summary: 修用户实测中暴露的 **pollinations.ai 429 rate limit cascade**。用户 count=20 第 1 张成功后所有后续 429，所有 error 报相同 `actor_0003`。**两个独立 bug 合流**：(A) **限速无重试** — follow-up 014 `_default_fetcher` 单次 GET，pollinations.ai 免费 endpoint 限速激进，一连发 ≥2 请求即 429，无 backoff 直接冒泡。(B) **incomplete folder 占 ID** — follow-up 014 `_next_actor_id_num` 用 `_ACTOR_DIR_RE` regex 数 max+1，旧批失败时若 mkdir 成功但 jpg 没写盘（429 / timeout 在 stream 期间），cleanup 路径有时 swallow OSError 失败，残留空 folder 被下批算进 max → 死循环每次 `actor_0003`。

**三处修复**：

1. **Backend retry-with-backoff** (`actor_pool.py:_default_fetcher` 重写)：
   - 最多 3 次重试，backoff `[3s, 6s, 12s]` 累计 21s + httpx timeout
   - 单图 worst case wall-clock ~81s（仍远低于浏览器 fetch timeout，且前端 follow-up 017 已搬循环出 backend）
   - 429: honor `Retry-After` header（delta-seconds form per RFC 7231 §7.1.3）capped 60s；缺则用 backoff 默认
   - 读 / 连接 / 写 timeout: 同 backoff 重试
   - 其他 4xx/5xx（404/500/...）不重试直接 raise（避免浪费 wall-clock）
   - 新 helper `_parse_retry_after(header_value, default)` —— 解析 header_value or fallback to default, capped at 60s, 处理 garbage 输入
2. **Incomplete folder reap** (`actor_pool.py:_next_actor_id_num` 重写)：
   - 命中 `_ACTOR_DIR_RE` 但缺 `<id>.jpg` 的 folder：**不计 max**、立即 cleanup（删 folder 内任何 partial 文件 → rmdir）
   - cleanup 失败 silently swallow（与 `_cleanup_empty_folder` 一致，磁盘 dirty 不阻塞批次）
   - 副作用：用户**手动**创建的空占位 folder 会被删；不在 v1 contract 内，可接受
3. **Frontend inter-iteration throttle** (`ActorPoolGenerator.tsx`)：
   - 新增 `INTER_REQUEST_THROTTLE_MS = 2000` 常量
   - 每次 `await generateActors()` 完成后、下一轮开始前 sleep 2s（最后一轮不 sleep；cancelled 状态下也不 sleep）
   - `Progress.phase` 新 enum 字段 `"idle" | "generating" | "throttling"` —— UI 在 throttle 期间显示 `⏸ 等待限速冷却…` + 按钮文案 `等待 2s 防限速… (i / N)`
   - modal 内加 `.rate-limit-hint` 文字行告知用户机制："pollinations.ai 免费 endpoint 有限速 — 每张间隔 2 秒；遇到 429 后端自动重试 3 次（最长等 60s）"

Auto-updated:
- `specs/development/ai_video_management/user_input/revised_prompt.md` — Last regenerated 改 2026-05-12 22:30:00；Composed-from 加 follow-up 018；header 摘要描述两根因合流 + 三处修复 + verification；prior follow-up 017 line 移到 prior 列表。
- `projects/ai_video_management/backend/libs/actor_pool.py`：
  - 新增 module-level 常量 `_RETRY_BACKOFFS_SECONDS=(3.0, 6.0, 12.0)` + `_RETRY_AFTER_CAP_SECONDS=60.0` + helper `_parse_retry_after`
  - `_default_fetcher` 重写：retry loop 4 attempts (1 initial + 3 retries) over 429 / timeouts；honor Retry-After；non-retriable HTTP 错误 raise_for_status 冒泡；max_bytes cap 检查保留
  - `_next_actor_id_num` 重写：跳过 + cleanup incomplete folders；保留 OSError swallow 模式
- `projects/ai_video_management/frontend/src/components/ActorPoolGenerator.tsx`：
  - `Progress` interface 加 `phase: "idle" | "generating" | "throttling"` 字段；每个 `setProgress` 调用同步更新 phase
  - `onSubmit` for-loop 末尾加 inter-iteration sleep 块（带 cancellation check）
  - `ProgressPanel` 子组件根据 phase 渲染不同 emoji + 文字（throttle → ⏸ / generating → 🔄）
  - footer "生成中…" 按钮 label 根据 phase 拆两种文案
  - modal-body 新加 `<p className="rate-limit-hint">` 行告知用户机制
- `projects/ai_video_management/frontend/src/styles.css` — 新增 `.rate-limit-hint` 样式（small info bar，复用 `--text-muted` / `--bg-toolbar` / `--border` CSS vars）

Behavior changes:
- **Before**: count=20 → 第 1 张成功 → 第 2 张 timeout / 429 → cleanup → 第 3 张 mkdir 成功 → 429 → cleanup 失败遗留空 folder → 第 4-20 张都 mkdir 新 folder（next_id_num 把残留 folder 算进 max 不前进）→ 全部 429。最终用户得到 1 张图 + 19 个失败 error 都报 `actor_0003`。
- **After**: count=20 → 第 1 张成功 → sleep 2s → 第 2 张请求（若 429 → backend 自动等 Retry-After / 3s → retry → 大概率成功；最坏 4 attempts 后才彻底失败）→ 若成功 sidebar 立即多 1 个 folder + UI 显示 `🔄 生成中… 2 / 20` → 完成后 `⏸ 等待限速冷却…` 显示 2s → 第 3 张……持续。worst case 单图 81s + 2s throttle = 83s；count=20 worst case = ~27 min（远超用户期望但不会卡死）；nominal case 单图 < 30s + 2s throttle ≈ 8 min for 20 张。
- 残留 incomplete folder（包括用户先前批次失败留下的）在下次 generate_batch 调用时被 reap → ID 单调推进，不再卡 `actor_0003`。

Verification (smoke checks):
- Python imports: `from libs.actor_pool import ActorPool, _parse_retry_after, _default_fetcher` 成功。
- `_parse_retry_after` 单元: `None / "5" / "999" / "garbage"` → `3.0 / 5.0 / 60.0 / 3.0`（默认 / 解析 / cap / fallback）✓
- `_default_fetcher` 重试 unit-test（patch `httpx.Client` with FakeClient）:
  - Test 1: 429 + Retry-After=1 → 第 2 attempt 200 → 返回 bytes；elapsed ≥ 1s；calls=2 ✓
  - Test 2: 持续 429 + Retry-After=0 → 4 次尝试后 raise HTTPStatusError ✓
- `_next_actor_id_num` cleanup unit-test（tmpdir 模拟先前批次残留）:
  - pre-state: `actor_0001` (jpg+md ✓) + `actor_0002` (空 incomplete) + `actor_0003` (md only, 缺 jpg)
  - `generate_batch(count=1)` → 落 `actor_0002` (reclaim 该 slot) + cleanup `actor_0003` (incomplete)
  - 第二批 `generate_batch(count=1)` → 落 `actor_0003`（单调推进）✓
- `make boot-smoke`: **7/7 通过**，含 follow-up 014 加的 5 个 endpoint registration 断言。
- Frontend `npx tsc --noEmit`: 无新错误（仅两个 pre-existing `vite.config.ts` 错误）。

No conflicts found in:
- `final_specs/spec.md` FR-9f — `POST /api/actors/generate` 契约不变（仍 `count: 1..20` + invalid_attribute + actors_dir_unwritable 错误码面）；retry 在单次 HTTP 调用内部完成，对调用方透明。
- `validation/acceptance_criteria.md` U3.15 — fake fetcher 仅返回 stub bytes，不触发 retry 路径；测试断言仍 valid。如需覆盖 retry path，独立 follow-up 加 `_default_fetcher` 单元测试（本 follow-up 已在 inline smoke 验证）。
- `validation/security.md` carve-out #7 — 出站 HTTP 边界**不弱化**：retry 仍 single base URL hardcoded、URL-encoded prompts、follow_redirects=False、30s/请求 timeout、5MB cap；仅在 429 / timeout 时多 ≤3 次相同硬化的请求 + Retry-After 受信但 capped 60s（避免恶意 / buggy header 触发长 sleep DoS）。
- `agent_refs/project/ai_video.md` — 与本 follow-up 正交。
- 其他 backend libs (`casting.py` / `media_renamer.py` / `media_archiver.py` / `downloads_importer.py` / `api.py` 等) — 零影响。
- 其他前端组件 (`Sidebar.tsx` / `CastingView.tsx` / `Reader.tsx` / `ImageRefView.tsx` 等) — 零影响。

User next step:
1. Backend `--reload` (follow-up 012 默认开) 自动检测 `actor_pool.py` 改动 + reload；Vite HMR 自动重载 `ActorPoolGenerator.tsx` + `styles.css`。浏览器刷新即可。
2. **重要**：用户先前批次留下的 `_actors/actor_0002/` 等 incomplete folder 会在下次点 "🎭 生成演员" 时**自动被 reap**（看到 sidebar 内残留 folder 突然消失属正常）。
3. 重试 count=20 验证：每张间隔 2s + 429 自动重试；预期成功率显著高于上次（pollinations.ai 实际限速强度未知，nominal case 应该 ≥80% 通过；若仍大量失败，独立 follow-up 加 per-image inter-iteration 间隔到 5s+）。
4. 若仍频繁 429：考虑改用其他 AI face source（独立 research follow-up），或人工降低 batch size 到 ≤5。

Severity: Medium. 用户报告的实际可用性 blocker；后端 retry 是首次出站 HTTP 路径上的稳定性 hardening；folder reap 修 follow-up 014 的隐性 bug。改动范围：1 backend lib 重写 2 函数 + 1 frontend 组件加 phase state + 1 CSS 行。后端 / API 契约 / spec FR / 安全 carve-out 零变动。

## Follow-up 017 — 2026-05-12 22:00:00
Source: user_input/follow_ups/017-20260512-220000-actor-generation-progress-visibility.md
Summary: 修 follow-up 014 引入的 batch generate UX 问题 — 用户报告点 "🎭 生成演员" 选 count=20，磁盘只出现 1 张图片，剩 19 张状态不明（仍在跑？失败？已结束？）。**根因**：`POST /api/actors/generate` 同步串行循环 count 次 pollinations.ai 请求（每次 5–30s），count=20 worst case = 10 分钟，浏览器 fetch 默认 timeout ~5 min 中途断开 → 后端 silently 继续 loop、前端 catch ApiError 显示 "失败" toast、用户无任何 in-flight 状态指示。后端 errors[] 数组也因连接断开永远到不了前端。**Fix**：搬移循环到前端，**不动后端**。`ActorPoolGenerator` 重写：把 count=N 拆 N 次 count=1 串行调用，每次秒级返回；实时显示 progress bar + 累积 errors 列表 + 已生成 ID 列表；每次成功 / 失败立即调 `onGenerated()` 触发 sidebar refresh；"停止" 按钮设 cancellation flag (React `useRef`，避免 stale closure)，loop 跳出但当前 inflight 请求继续完成；modal 关闭时若 busy 触发 cancel 而不立即 unmount，等 inflight 结束再关。

Auto-updated:
- `specs/development/ai_video_management/user_input/revised_prompt.md` — Last regenerated 改 2026-05-12 22:00:00；Composed-from 加 follow-up 017；header 摘要描述同步循环 + 浏览器 timeout + 前端循环 fix；prior follow-up 016 line 移到 prior 列表。
- `projects/ai_video_management/frontend/src/components/ActorPoolGenerator.tsx` — 完全重写 `onSubmit`：从 1 次 `generateActors({count: N, ...})` 改为 N 次 `generateActors({count: 1, ...})` 串行循环；新增 `Progress` state interface (`done` / `failed` / `total` / `current` / `errors` / `generatedIds`)；`useRef<boolean>` 持有 cancellation flag（不用 state 因为 stale closure 会让 loop 看不见更新）；新加 `ProgressPanel` 子组件渲染进度条 + 摘要 (`✓ N · ✗ E · pct%`) + collapsible details（已生成 ID 列表 + 失败原因列表 with `#i: message`）；modal footer 在 busy 状态把 "取消" 按钮改 "停止"，busy 状态下 "关闭" 按钮 = "中断后关闭"；按钮文案 `生成中…` 改 `生成中… (i / total)` 实时刷新。
- `projects/ai_video_management/frontend/src/styles.css` — 新增 `.progress-panel` 容器 + `.progress-summary` + `.progress-ok` / `.progress-err` 颜色 + `.progress-bar` / `.progress-bar-fill` (CSS transition width 0.3s 让进度变化平滑) + `.progress-details` (collapsible summary / code block / ul) + `.progress-details-err` 错误列表色板。复用既有 `--accent` / `--border` / `--bg(-toolbar)` / `--error-text` / `--text(-muted)` CSS vars，无新增色板。

Behavior changes:
- **Before**: 点 "生成" count=20 → 浏览器发 1 个 POST → 等待 10 分钟 → 浏览器 timeout → 前端 toast `生成失败: 504` 或 `生成失败: Failed to fetch`；后端继续静默处理 19 张；用户不知所措。
- **After**: 点 "生成" count=20 → 前端发 20 个独立 POST 顺序 →
  - 进度条 0 → 100% 实时增长；
  - 数字 `0 / 20 → 1 / 20 → ... → 20 / 20`；
  - 每张完成后 sidebar 立即多 1 个 `actor_NNNN/` folder（onGenerated triggers tree reload）；
  - 任何一张失败：accumulator 加 error `#i: <reason>`，进度条仍前进 (failed 计入 done+failed)，loop 不中断；
  - 中途 "停止" → 当前 inflight 完成 → loop 跳出 → toast `已中断 — 已生成 X / 失败 Y / 跳过 Z`；
  - 关闭后再打开 modal：progress / toast / cancellation flag 全部重置（`useEffect [open]` 清理）。
- 单张请求 wall-clock ~5–30s，远小于浏览器 fetch timeout，故连接稳定不再 mid-batch 断开。
- 后端零改动 — pytest scenarios U3.15 仍 valid（仍用 count=3 单次调用），actor_pool.py 行为契约不变。

Verification (smoke checks):
- Frontend `npx tsc --noEmit`: 无新错误（仅两个 pre-existing `vite.config.ts` 错误与本 follow-up 无关）。
- 渲染流验证（手动 trace）：modal open → state 全部 default → 用户调参 → 点 "生成" → busy=true, cancelledRef=false, progress 初始 0/N → for-loop i=1..N → 每轮 setProgress current=i → await generateActors(count=1) → 解构 generated[0].id + errors[] → push 到 accumulator → setProgress 更新 → onGenerated 触发 tree refresh → 下一轮；loop 结束 → setProgress current=0 → setToast 总结 → setBusy=false。
- "停止" 按钮路径：busy 时点击 → cancelledRef.current=true → 当前 await 完成后 for-loop 头部检测 cancelledRef → break → 进入 toast 总结。Modal 仍打开，progress 显示部分结果，用户可看 errors 然后关闭。
- 关闭 modal 路径：点击 backdrop / 关闭按钮 → onCloseRequest → if busy: cancelledRef.current=true (modal 不 unmount，等 inflight 完成)；if !busy: onClose() 直接 unmount。useEffect[open] 在下次 open=true 时重置 state（toast/progress 清空, cancelledRef=false）。
- Race conditions: `setProgress` 在 await 前后各调一次，确保 UI 在 in-flight 期间也显示 `(i / N)`；errors / generatedIds 用浅拷贝 `[...errors]` 保证 React 检测变化触发 re-render。

No conflicts found in:
- `backend/libs/actor_pool.py` — `generate_batch(attrs, count)` 实现完全不动；`count=1` 走同一路径，`MIN_BATCH_COUNT=1` 已存在所以 count=1 一直 valid。
- `backend/libs/api.py` `POST /api/actors/generate` 契约不动；前端循环对后端透明。
- `final_specs/spec.md` FR-9f / FR-88 — spec 文字说 "count: 1..20"，前端拆 count=20 为 20 次 count=1 仍满足契约（每次都是合法 count）。如要在 FR-88 加 "frontend 串行循环显示进度" 行为约束，可独立 follow-up；本 fix 不弱化任何 FR。
- `validation/acceptance_criteria.md` Scenario U3.15 — 测试 `POST /api/actors/generate count=3` 一次成功 + invalid attr / count 边界。前端循环不改 backend 测试。
- `validation/security.md` carve-out #7 — 出站 HTTP 限制不变（每次 count=1 仍 30s timeout + 5MB cap + base URL hardcoded）；前端连发 20 次的总流量仍由 backend 单次限制控制，且每次串行（无并发放大）。
- `Sidebar.tsx` / `CastingView.tsx` / `Reader.tsx` 等其他前端组件 — 零影响。
- `casting.py` / `media_renamer.py` / 其他 backend libs — 零影响。

User next step:
1. Vite HMR 自动重载 `ActorPoolGenerator.tsx` + `styles.css` → 浏览器刷新 modal 立即可见新 UI。
2. 旧批未完成的 19 张：可能磁盘上没出现（pollinations.ai 限速 / 后端进程已不再运行 / mid-batch 失败），可直接再次点 "🎭 生成演员" 跑新 batch；ID 单调自增不会冲突（已生成的 actor_0001 保留，新批从 actor_0002 起）。
3. 跑 count=20 验证：观察 modal 进度条 + 数字一张张跳；每张完成 sidebar 同步出现新 actor folder。

Severity: Medium-Low UX bug (后端无数据丢失风险 / 无 security 影响). 改动范围：1 个前端组件重写 + CSS 进度条样式。Backend / API 契约 / spec FR 零变动。

## Follow-up 016 — 2026-05-12 21:30:00
Source: user_input/follow_ups/016-20260512-213000-jpg-preview-uses-api-media.md
Summary: 修用户报告的 `.jpg` preview bug — 点击 `ai_videos/_actors/actor_NNNN/actor_NNNN.jpg`，Reader 显示一大段 base64 文本而非图片。**根因**（两件事的交叉）：① `backend/libs/file_reader.py:72-74` 对 `.png`/`.jpg` 走 `base64.b64encode` 返回 JSON `{content: "<base64>", encoding: "base64"}` —— 浏览器把它当 JSON 收，不是图片字节；② `frontend/src/components/Reader.tsx:43` 的 `isMediaOnly = isMediaVideo || (isMediaImage && ext !== ".png" && ext !== ".jpg")` 显式把 png/jpg 排除在 media-only 之外，加上 render 分支 `isMediaImage && ext !== ".png" && ext !== ".jpg" ? <img src={mediaUrl(path)}>` 也排除，导致 png/jpg fall through 所有 isVideo/isCasting/isImageRef/isShotPair/.../isMarkdown/isTxt 条件，最终落到 `<pre className="text-view">{file.content}</pre>` 兜底，渲染 base64 文本。其他 image 扩展（webp/gif/bmp）和 video 扩展走 `/api/media` raw bytes 正常 —— 这个差异性 bug 潜在了 5+ follow-up（005 引入 /api/media 后留下的不一致），follow-up 014 引入大量 `.jpg` 资产后首次暴露。**Fix**：让 `.png`/`.jpg` 也走 `/api/media`：① `Reader.tsx:43` `isMediaOnly = isMediaVideo || isMediaImage`；② `Reader.tsx` render 分支去掉 `ext !== ".png" && ext !== ".jpg"` 双重否定，统一为 `isMediaImage`；③ `ImageRefView.tsx` 两处 `imageUrl()` 换 `mediaUrl()` + import 同步换名（修同根因的二次 bug —— 仓库目前无 `_seedream.png` 加载过，本 follow-up 顺手治 root cause）。`/api/media` 端点 sandbox 限制（`exposed.is_inside` + `resolver.resolve`）与 `/api/file` 等价，不弱化安全。

Auto-updated:
- `specs/development/ai_video_management/user_input/revised_prompt.md` — Last regenerated 改 2026-05-12 21:30:00；Composed-from 加 follow-up 016；header 摘要描述 base64 fall-through + 三处 fix；prior follow-up 015 line 移到 prior 列表。
- `projects/ai_video_management/frontend/src/components/Reader.tsx` — line 43 `isMediaOnly` 去掉 png/jpg 排除；render 分支 `isMediaImage && ext !== ".png" && ext !== ".jpg"` → `isMediaImage`。两处共 2 行改动。
- `projects/ai_video_management/frontend/src/components/ImageRefView.tsx` — import `imageUrl` → `mediaUrl`；line 55 (image-only layout) `imageUrl(...)` → `mediaUrl(...)`；line 86-87 (companion 立绘) `imageUrl(...)` → `mediaUrl(...)`。三处共 3 行改动 + 1 行 import。

Behavior changes:
- 点击 `.jpg` / `.png` 在 Reader 中：之前显示 base64 字符串墙（看上去像随机字符），现在显示 inline 图片（80vh max-height + center 对齐，与 `.webp`/`.gif`/`.mp4` 等同一 `.media-view` 容器）。
- ImageRefView companion 立绘右窗格：之前 `<img src="/api/file?path=...">` 加载 JSON 响应而失败渲染（HTTP 200 但 content-type=json），现在 `<img src="/api/media?path=...">` 加载 raw bytes 正常显示。注：仓库目前无 `_seedream.png` 资产被加载过，所以此分支的破损此前从未暴露。
- 之前 Reader load 对 png/jpg 也跑 `fetchFile()` 拿 base64 JSON（白白消耗 1MB cap 内的带宽 + memory）；现在跳过 `fetchFile()` 走 `/api/media` 流式响应，与其他 media 一致。

Verification (smoke checks):
- Frontend `npx tsc --noEmit`: 无新错误（仅两个 pre-existing `vite.config.ts` 错误与本 follow-up 无关）。
- 路径检查：点击 `ai_videos/_actors/actor_0001/actor_0001.jpg` → Reader 状态 `isMediaImage=true, isMediaOnly=true, ext=".jpg"` → load() skip fetchFile → setFile() 放 placeholder → render 分支命中 `isMediaImage` → `<img src={mediaUrl(path)}>` → 浏览器 GET `/api/media?path=ai_videos/_actors/actor_0001/actor_0001.jpg` → backend FileResponse 返回 image/jpeg bytes → 图片渲染。✓
- Existing `.png` paths in `characters/ref_images/` (e.g. 未来的 `_seedream.png`) 同理：之前 broken（不显示），现在正常渲染。✓
- `.webp/.gif/.bmp/.mp4` 等扩展：之前已通过 mediaUrl 正常工作，本 follow-up 零影响。✓

No conflicts found in:
- `backend/libs/file_reader.py` — base64 编码逻辑保留（其他调用方 e.g. potential 测试 / curl 直接 GET /api/file 可能仍依赖；本 follow-up 只改前端 render 路由，不改 `/api/file` 契约）。
- `backend/libs/api.py` `/api/media` endpoint — 不动；本身已有正确的 sandbox + MIME map + FileResponse + range support。
- `frontend/src/api.ts` `imageUrl` helper — 保留（公共 API，可能被 type-check / 测试 / 外部代码引用）；ImageRefView 已不再调用，可后续 follow-up 清理。
- `frontend/src/components/Sidebar.tsx` / `App.tsx` / `Editor.tsx` / `ShotPairView.tsx` / `ShotlistTableView.tsx` / `SiblingMedia.tsx` / `CastingView.tsx` 等 — 零影响。
- `final_specs/spec.md` FR-61 — spec 文字仍写 `<img src="/api/file?path={enc}&mtime={mtime}">`，但实际实现现在用 `/api/media`。这是 specs 的历史陈述 drift，**不阻碍 fix**；如需对齐，独立 follow-up 改 FR-61 + FR-19 image leaf 描述。
- `validation/*` — 无 acceptance scenario 显式断言 `.jpg` 渲染走 `/api/file` 还是 `/api/media`；行为契约「图片应当 inline 显示」继续满足。

User next step:
1. **若 backend + Vite dev server 都跑着**（follow-up 012 默认 `--reload` + Vite HMR）：浏览器刷新 `http://127.0.0.1:8766/` 即可。点 `_actors/actor_0001/actor_0001.jpg`（先用 "🎭 生成演员" 按钮生成至少 1 张）→ Reader 显示图片预览。
2. **若用 production build**（`make run-prod`）：需 `cd frontend && npm run build` 重建 + 拷贝到 `backend/static/`，然后重启 backend。

Severity: Low (UI render-only bug，no data corruption, no security impact). Surgical 5 行修改（Reader.tsx 2 行 + ImageRefView.tsx 3 行 + 1 import 换名）。`/api/file` 后端契约保留。

## Follow-up 015 — 2026-05-12 21:05:00
Source: user_input/follow_ups/015-20260512-210500-actors-bootstrap-folder.md
Summary: 修 follow-up 014 留下的 **chicken-and-egg UX bug** — 用户报告打开 webapp 后看不到 "🎭 生成演员" 按钮。**根因**：follow-up 014 的 `Sidebar.tsx` 把按钮 conditional 在 `dramaPathParts[1] === "_actors"` 行上，但 `ai_videos/_actors/` 目录只在 `ActorPool.generate_batch()` 第一行 `mkdir(parents=True, exist_ok=True)` 时 lazy 创建 —— 新用户从未触发过 endpoint，所以 TreeWalker `iterdir()` 看不到 `_actors/`，sidebar 不渲染该行，按钮永远不出现。**修复**：在 `api.py:create_app()` 实例化 `ActorPool` 后立即 eager `actor_pool.actors_dir().mkdir(parents=True, exist_ok=True)`。`exist_ok=True` 让已有 `_actors/` 安装零影响；`OSError` swallowed（与现有 `serve_static` 静默 mount-fail 模式一致 —— mkdir 失败不应阻止整个 webapp 起动）。

Auto-updated:
- `specs/development/ai_video_management/user_input/revised_prompt.md` — Last regenerated 改 2026-05-12 21:05:00；Composed-from list 加 follow-up 015；header 摘要描述 chicken-and-egg 根因 + fix 一行；prior follow-up 014 line 移到 prior 列表。
- `projects/ai_video_management/backend/libs/api.py` — `create_app()` 内 `actor_pool = ActorPool(...)` 后插入 3 行：`try: actor_pool.actors_dir().mkdir(parents=True, exist_ok=True) except OSError: pass`，带 3 行 inline comment 标注 follow-up 015 + 解释 chicken-and-egg。无其他 api.py 改动。
- `ai_videos/_actors/` — 当前仓库新建空目录（boot-smoke 运行 `create_app()` 时自动创建；前端 sidebar 重启后即可看到该行 + "🎭 生成演员" 按钮）。

Verification (smoke checks):
- `make boot-smoke` (pytest test_boot_smoke.py): **7/7 通过**，含 follow-up 014 加的 5 个 endpoint registration 断言。
- `ls ai_videos/`: 输出含 `_actors`（新建）+ `mozun_chongsheng`（既有），与预期一致。
- TreeWalker 行为：空 `_actors/` directory 通过 `_walk_project` 走，生成 `{type:"directory", children:[], project_meta: null}` 节点 —— sub_type_lookup 对空 folder 自然返回 None (无 episodes/ 无 script.md/shotlist.md)。前端 `Sidebar.tsx` `isAiVideoChild && dramaPathParts[1] === "_actors"` 触发 `isActorsRoot=true` → 渲染 🎭 emoji icon + "🎭 生成演员" 按钮（开 ActorPoolGenerator modal）。

No conflicts found in:
- 所有 frontend 代码 (`Sidebar.tsx` / `Reader.tsx` / `ActorPoolGenerator.tsx` / `CastingView.tsx` / `api.ts` / `styles.css` 等) — 行为契约不变；唯一改动是后端启动时 eager mkdir，前端 fetch tree 时新增一个 directory node。
- `actor_pool.py` lazy mkdir 仍在 `generate_batch` 第一行 — 双重保险（启动时已 mkdir，但若 follow-up 014 行为被独立调用也 safe）。
- `casting.py` / `media_renamer.py` / `downloads_importer.py` / 其他 backend libs — 零影响。
- `final_specs/spec.md` FR-87 (`_actors` 非 drama 约定) — 行为不变；FR-87 只规定 `_actors` 在 sidebar 中的展示规则，不规定 何时创建。新加的 eager mkdir 是 implementation detail，与 FR 契约 orthogonal。
- `validation/*` — 测试场景 U3.15 / U3.16 用 tmpdir fixture 显式创建 actor folder，与生产 eager mkdir 行为正交，不需改动。

User next step:
1. **若 backend 还在跑（follow-up 012 默认 `--reload`）**：uvicorn 自动 detect `libs/api.py` 改动 + reload，下次浏览器刷新 `http://127.0.0.1:8766/` 即可看到 sidebar AI Videos 下出现 `_actors/` 行（🎭 emoji）+ "🎭 生成演员" 按钮。
2. **若 backend 没跑或用了 `--no-reload`**：`make run-backend` 重启即可。

Severity: Low. UI bootstrap bug in follow-up 014；3-line fix；零业务逻辑改动；不影响已生成的 actor / cast 数据；不影响已有 webapp 行为。

## Follow-up 014 — 2026-05-12 20:15:00
Source: user_input/follow_ups/014-20260512-201500-actor-face-pool-casting-ref-video.md
Summary: 新增 **actor face pool + casting workflow** 大功能。① 在 `ai_videos/_actors/` 维护 AI 生成的演员人脸池，每张 face 一个 `actor_NNNN/{actor_NNNN.jpg, actor_NNNN.md}` folder；sidecar md 记录六字段属性表（ethnicity / gender / age_range / look / style / notes）+ 生成 prompt + seed。② backend 调用 **pollinations.ai 免费 API**（`https://image.pollinations.ai/prompt/{prompt}?model=flux&seed=...`，无 API key，无 signup，MIT 协议）完全自动批量生成 + 落盘 —— 这是 backend **首次** 出站 HTTP，硬化：base URL 写死、prompt URL-encoded as path、30s/请求超时、5MB 响应 cap、批量上限 20、`follow_redirects=False` 防 SSRF。③ `ai_videos/{drama}/casting.md` 维护 role → actor_id 映射，新 `CastingView` 渲染表格 + 缩略图 + filter chips + 一键复制 ref-video prompt（即 rule #12.5 的 2.9s Seedance turntable schema + 演员图路径 inline）。④ ref-video 生成本身不进 webapp —— 用户拿 prompt + 演员图 在 Seedance 外部跑，下载后走已有 follow-up 009 import 流程落到 `characters/c{N}_*/c{N}_*.mp4`。`_actors/` 通过下划线前缀标记非-drama（sub_type 检测 None，sidebar 不渲染 drama-only rename 按钮，改渲染 "🎭 生成演员" 按钮打开 ActorPoolGenerator 模态）。

Research (决策依据):
- thispersondoesnotexist.com — 仅随机脸无属性控制 → 否决
- Generated.Photos API — ToS 禁 caching / downloading / standalone files → 否决（与本功能直接冲突）
- HuggingFace Inference (SDXL/FLUX) — 要 token + 1000/day 上限 + cold start → 否决
- pollinations.ai — 0 auth + MIT 协议 + 属性 in-prompt 自然 label + 100% free → 选中

Auto-updated:
- `specs/development/ai_video_management/user_input/revised_prompt.md` — Last regenerated 改 2026-05-12 20:15:00；Composed-from list 加 follow-up 014；header 摘要描述三段功能（pool / casting / ref-video）+ pollinations.ai 选型 + sandbox 出站 HTTP 边界 + `_actors/` 前缀约定；prior follow-up 013 line 移到 prior 列表。
- `specs/development/ai_video_management/user_input/follow_ups/014-*.md` — 追加 `## 决策 (interactive 收集)` 段：四问答案（pool 位置 / face 生成姿势 / casting 持久化 / ref-video 姿势）+ 六字段属性 schema + 文件 layout + 5 个新 endpoint 契约 + 3 个前端组件 + 安全 / 边界扩展 + 不在范围列表。
- `specs/development/ai_video_management/final_specs/spec.md` — FR-1 backend libs 列表加 `actor_pool.py` + `casting.py` (follow-up 014)；FR-9 注释扩展提及 follow-up 014 的 3 个 state-changing endpoint + 出站 HTTP；新增段 `### Actor pool + casting (follow-up 014)` 含 **FR-9f/g/h** (POST /api/actors/generate, POST/DELETE /api/casting/assign 完整契约)、**FR-10b/c** (GET /api/actors, GET /api/casting)、**FR-86** (六字段闭合 enum schema)、**FR-87** (`_actors` 非 drama 约定 + 下划线前缀 system folder)、**FR-88** (ActorPoolGenerator 模态)、**FR-89** (CastingView 两 mode + ref-video prompt 复制按钮)、**FR-90** (sidebar `_actors/` 🎭 图标)。
- `specs/development/ai_video_management/validation/acceptance_criteria.md` — 新增 Scenario U3.15 (actor/generate 批量 + pollinations.ai 出站 + ID 自增 + invalid_attribute + count 边界 + per-image error 不 fail batch) + Scenario U3.16 (casting upsert / delete / GET /api/casting / GET /api/actors + 完整错误码面)；FR→Scenario 矩阵加 FR-9f→U3.15, FR-9g/h→U3.16, FR-10b/c→U3.16, FR-86→U3.15。
- `specs/development/ai_video_management/validation/security.md` — coverage matrix 加 FR-9f (`partial` 因首次出站 HTTP)、FR-9g/h (`partial` 因 Origin/Host gate 沿用现有 pattern，未扩展 GUARDED_ROUTES)、FR-86 (`covered`，闭合 schema 限制 prompt injection 面)；Open carve-outs #7 新增详述 `/api/actors/generate` 的 7 条出站硬化 + 3 类残余风险（外部依赖 / 无内容过滤 / localhost 触发外部 IO）+ casting 写也走相同 Origin gap。
- `projects/ai_video_management/backend/libs/actor_pool.py` (NEW) — `ActorPool` 类 + `ActorAttrs/ActorInfo/GenerateResult` dataclasses + 闭合 enum 常量 (ETHNICITY/GENDER/AGE_RANGE/LOOK/STYLE_OPTIONS) + `POLLINATIONS_BASE`/`MAX_BATCH_COUNT=20`/`MAX_RESPONSE_BYTES=5MB`/`DEFAULT_TIMEOUT_SECONDS=30`；`generate_batch(attrs, count)` 顺序循环：validate → mkdir `ai_videos/_actors/actor_NNNN/` → httpx GET pollinations.ai (stream, follow_redirects=False, max_bytes cap, timeout) → 写 jpg + 写 sidecar md（属性表 + prompt + seed）；per-image error → errors[] 不中断 batch + cleanup 空 folder；ID 通过扫描 max actor_NNNN+1 单调自增防覆盖；`_build_prompt` deterministic 英文 Seedream-style 拼接；`list_actors` 扫 _actors/ + 解析 sidecar md attrs；`actor_exists(id)` 给 casting 校验用；`fetcher` 参数允许测试注入 fake。
- `projects/ai_video_management/backend/libs/casting.py` (NEW) — `Casting` 类 + `CastEntry/CastingResult` dataclasses + `InvalidActorId/InvalidRole` 异常；`read(drama)` / `assign(drama, role, actor, notes)` / `unassign(drama, role)` 三入口；drama path validation 复用 `MediaRenamer.validate_drama`（同 invalid_drama_path / not_found 边界）；actor_id 校验通过 `ActorPool.actor_exists` 跨模块；assign 用 upsert 语义（同名 role 覆盖）；整文件 atomic temp-then-replace 重写，避免 markdown table line-level surgery 边界 case；表头固定为 `| role | actor_id | notes |`，empty notes 渲染为 `—`。
- `projects/ai_video_management/backend/libs/api.py` — module docstring "8 endpoints" → "13 endpoints"；imports 加 `ActorPool/ActorAttrs/InvalidAttribute/GenerationDirMissing` + `Casting/InvalidActorId/InvalidRole`；新 Pydantic models `GenerateActorsBody` / `CastingAssignBody` / `CastingUnassignBody`；instantiate `actor_pool = ActorPool(exposed, resolver)` + `casting = Casting(exposed, resolver, media_renamer, actor_pool)`；路由：`POST /api/actors/generate` (200 / 400 invalid_attribute / 500 actors_dir_unwritable / 405) + `GET /api/actors` (200 / 405) + `GET /api/casting` (200 / 400 invalid_drama_path / 404 not_found / 405) + `POST /api/casting/assign` (200 / 400 invalid_drama_path / 400 invalid_role / 400 invalid_actor_id / 404 not_found / 405) + `DELETE /api/casting/assign` (同 POST 错误码 + 404 role 不在 casting.md)。
- `projects/ai_video_management/backend/tests/test_boot_smoke.py` — `test_all_post_endpoints_registered` expected set 加 5 项：`("POST", "/api/actors/generate")` / `("GET", "/api/actors")` / `("POST", "/api/casting/assign")` / `("DELETE", "/api/casting/assign")` / `("GET", "/api/casting")`。`make boot-smoke` 7/7 通过。
- `projects/ai_video_management/frontend/src/api.ts` — 新增 types `ActorAttrs` / `ActorInfo` / `GenerateActorsRequest` / `GenerateActorsResult` / `CastEntry` / `CastingResult` + helpers `generateActors` / `listActors` / `fetchCasting` / `castingAssign` / `castingUnassign` + 闭合 enum 常量 export `ATTR_OPTIONS` 给前端下拉 + filter chips 使用。
- `projects/ai_video_management/frontend/src/components/ActorPoolGenerator.tsx` (NEW) — 模态对话框组件：六字段 select + count number input (1–20) + notes textarea + 提交按钮；in-flight disable + 进度文本；toast 显示 `已生成 N / 失败 E`；成功后 `onGenerated()` 触发 tree refresh。
- `projects/ai_video_management/frontend/src/components/CastingView.tsx` (NEW) — Reader 在 path 命中 `^ai_videos/[^/]+/casting\.md$` 时 dispatch 的渲染组件。两 mode：**read** = 渲染当前 casting 表（role / actor 缩略图 / 属性 / notes / row actions），row actions 含 `▶ 复制 ref-video prompt`（拼 rule #12.5 schema + actor.image_path）+ `🗑 取消`；**assign** = 角色名 input + filter chips（按 5 个属性筛 actor）+ actor 缩略图网格 → 点击 tile 调 `POST /api/casting/assign`。Toast announce 操作结果；onChange 回调让 Reader 刷新 sibling tree。
- `projects/ai_video_management/frontend/src/components/Reader.tsx` — import `CastingView`；新增 `isCasting` 检测（`/^ai_videos\/[^/]+\/casting\.md$/`）；render dispatch 在 `isImageRef` 之前优先匹配 `isCasting` → `<CastingView castingPath={path} onChange={onSaved} />`；Editor 按钮在 `isCasting` 时也隐藏（与 isShotPair / isImageRef 一致，casting 走自己的 mutation 路径）。
- `projects/ai_video_management/frontend/src/components/Sidebar.tsx` — import `ActorPoolGenerator`；新增 `generatorOpen` state；in render loop 新增 `isAiVideoChild` / `isSystemFolder` (name 起 `_`) / `isDrama` (重定义 = isAiVideoChild && !isSystemFolder) / `isActorsRoot` (`_actors`) 四个布尔；drama-row "📥 导入 + 重命名" 按钮现在排除 system folder（`_actors` 等不显示）；`_actors/` row 显示 🎭 emoji icon + "🎭 生成演员" 按钮（开 modal）；底部挂 `<ActorPoolGenerator>` 组件，关闭后若有生成则触发 `onTreeReload`。
- `projects/ai_video_management/frontend/src/styles.css` — 新增 modal 样式（`.modal-backdrop` / `.modal-panel` / `.modal-header` / `.modal-body` / `.modal-footer` / `.modal-toast(-ok/-err)` / `.form-grid` / `.form-field`）+ casting 样式（`.casting-view` / `.casting-header(-actions)` / `.casting-add-btn` / `.casting-toast(-ok/-err/-dismiss)` / `.casting-table` + 表头/行/缩略图/role/actor-cell/actor-id/missing/attrs/row-actions / `.casting-assign-pane(-form)` / `.casting-filter-chips` / `.casting-actor-grid` + tile/id/attrs）。全部 light-theme compliant，复用既有 CSS var `--accent` / `--border` / `--tint-a(-border)` / `--error-bg/text/border` / `--text(-muted)` / `--bg(-toolbar)`，无新增色板。

Verification (smoke checks):
- Python imports compile clean: `from libs.actor_pool import ActorPool, ActorAttrs` + `from libs.casting import Casting` + `from libs.api import create_app` 无异常。
- ActorPool smoke test（fake fetcher 返回 stub JPEG，tmpdir 模拟仓库）：3-batch 生成 ID 升序 actor_0001..0003，磁盘 jpg + md 都落盘；二次 batch 接 actor_0004..0005 单调自增；invalid `ethnicity="klingon"` → `InvalidAttribute`；count=21 → `InvalidAttribute`；`list_actors()` 解析回六字段属性表 + 跳过缺图/缺 md 的 folder。
- Casting smoke test（同 tmpdir + ActorPool 先生成 2 个 actor）：assign 创建 casting.md + 1 row；同 role 第二次 assign 覆盖；不同 role 第二次 assign 共 2 row；read 回正确顺序；unassign 减 1；invalid actor_0009 → `InvalidActorId`；path "ai_videos/" → `InvalidDramaPath`；role 含 `|` → `InvalidRole`。
- `make boot-smoke` (pytest test_boot_smoke.py): **7/7 通过**，含新加的 5 个 endpoint registration 断言。
- Frontend `npx tsc --noEmit`: 无新错误（仅 vite.config.ts 两个 pre-existing 错误，与本 follow-up 无关；与 follow-up 008-013 verification log 一致）。

Deferred (not in this follow-up):
- backend pytest for `actor_pool.py` + `casting.py` + 5 个新 endpoint 路由（与 follow-ups 005-013 一致推迟到批量补测；test_boot_smoke 已含 endpoint registration 断言作 baseline）。fixture 需要 monkey-patch `ActorPool._fetcher` 注入 fake JPEG bytes，以及 tmp_path drama scaffold。
- e2e Playwright 验证 ActorPoolGenerator 模态 + CastingView read/assign 两 mode + sidebar "🎭 生成演员" 按钮（同上推迟）。
- pool 内 actor 删除 endpoint (v1 用文件系统手工 rm；后续可加 `DELETE /api/actors/{id}`)。
- regenerate-same-attrs 功能（v1 不复用同 prompt + seed，每次 batch 都是新 seed）。
- 跨 drama casting clone / template（每 drama 独立 casting.md）。
- Origin/Host gate 扩展到新 POST/DELETE 端点（与现有 rename / archive / import 一致沿用现有 pattern；已知 security gap，留给独立 follow-up）。
- Actor attribute auto-classification (v1 attrs 来自用户填的表单 → 100% 准确，无 ML 推断需要)。
- ActorGalleryView 专用浏览模式（v1 简化：sidebar 展开 _actors/ 看 actor folders，每个 actor_NNNN.md 用现有 markdown view + SiblingMedia 渲染图）。

Severity: Medium-Low. Additive feature, no breaking changes to existing endpoints. 新 sandbox 边界（首次出站 HTTP）已通过 7 层硬化 + 残余风险记录在 security.md carve-out #7；用户决策"pollinations.ai 无 auth"避免引入 secret-handling；用户决策"ref-video 生成本身不进 webapp"保持 webapp 不直接调 Kling/Seedance API 的既有 invariant 不变。

No conflicts found in:
- `agent_refs/project/ai_video.md` rule #12.5 (character turntable 2.9s) — 本 follow-up 把 actor face + 这条规则的 prompt schema **组合** 后 expose 给用户，规则本身不动。
- `agent_refs/project/ai_video.md` rule #12.10 (scene reference 3.9s) — 与本 follow-up 正交。
- `projects/spec_driven/` — 完全不受影响。
- 其他 backend libs (`media_renamer.py` / `media_archiver.py` / `downloads_importer.py` / `file_reader.py` / `file_writer.py` / `api_security.py` / `exposed_tree.py` / `tree_walker.py` / `sub_type_lookup.py`) — 不动；`sub_type_lookup` 对 `_actors/` 自然返回 `None` (无 episodes/ 无 script.md/shotlist.md)；`exposed_tree.is_inside` 已 admit `ai_videos/**` 故 `_actors/` 自然 in sandbox。
- 其他前端组件 (`App.tsx` / `Editor.tsx` / `ShotPairView.tsx` / `ShotlistTableView.tsx` / `ImageRefView.tsx` / `SiblingMedia.tsx` / `Breadcrumb.tsx` / `BrokenLink.tsx` / `Home.tsx` / `ParseFallback.tsx`) — 保持不动。

## Follow-up 013 — 2026-05-12
Source: user_input/follow_ups/013-20260511-125029-batch-trim-character-mp4-to-2.9s.md
Summary: **一次性 data-op，webapp 代码零改动**。批量把 `ai_videos/mozun_chongsheng/characters/c*/c*.mp4` 19 个 character turntable mp4 in-place re-encode trim 到 ≤ 2.9s，对齐 rule #12.5 v4 的 Seedance reference ≤2.9s 上传约束 — 用户手工渲染的实际时长 3.04s–15.07s 不等，现已统一。ffmpeg 通过 `pip install --user imageio-ffmpeg` 拉的 v7.1 bundled binary（不污染系统 PATH）；每文件 `-t 2.9 -c:v libx264 -preset fast -crf 18 -c:a aac -movflags +faststart` 写 `<src>.trim.mp4` 临时文件 → atomic `os.replace` 覆盖原文件。结果：11 个文件 = 精确 2.9s，8 个文件 = 2.92s（mp4 packet-boundary 不可消的 ~20ms 过冲；远低于 3s 实际 Seedance 上限）。19/19 成功，无遗留 `.trim.mp4` 临时文件，无 stderr 错误。Hook 标 ai_video_management 项目，artifact 实际改动登记于 `specs/ai_video/mozun_chongsheng/changelog.md` cross-ref 条目。

Auto-updated:
- `specs/development/ai_video_management/user_input/revised_prompt.md` — Last regenerated 改 2026-05-12；Composed-from list 加 follow-up 013；header 摘要描述 19 文件 in-place re-encode 2.9s + 11+8 分布 + ffmpeg 来源；prior follow-up 012 line 移到 prior 列表。
- `ai_videos/mozun_chongsheng/characters/c*/c*.mp4` (19 文件) — in-place re-encoded H.264 / AAC 2.9s（详见下表）；mtime 全部跳到 2026-05-12 19:51；文件 size 大幅下降（原 3-15s 的源 vs 现统一 2.9s 后 size 比例缩放）。
- `.audit/trim_chars_2.9s.py` (NEW) — 复用脚本，imageio-ffmpeg locate ffmpeg binary + ffmpeg metadata 解析时长 + atomic temp-rename + JSON summary 输出。下次想再 trim character mp4（或其他 drama 的 character）直接改 `ROOT` 路径运行即可。
- `.audit/trim_chars_2.9s_result.json` (NEW) — 19 文件 before/after duration + encode 时长 JSON summary。
- `specs/ai_video/mozun_chongsheng/changelog.md` — 追加 cross-ref 条目记录 19 mp4 的 byte-level patch + 时长 before/after 表。

Before / after 时长（all 19）:

| 文件 | before | after |
|---|---|---|
| c10_司空玄/c10_司空玄1.mp4 | 2.9s | 2.9s |
| c10_司空玄/c10_司空玄2.mp4 | 3.04s | 2.92s |
| c1_沧冥/c1_沧冥1.mp4 | 12.04s | 2.92s |
| c1_沧冥/c1_沧冥2.mp4 | 15.07s | 2.9s |
| c1_沧冥/c1_沧冥3.mp4 | 3.04s | 2.92s |
| c1_沧冥/c1_沧冥4.mp4 | 4.06s | 2.9s |
| c1_沧冥/c1_沧冥5.mp4 | 4.04s | 2.92s |
| c3_苏璃月/c3_苏璃月1.mp4 | 15.07s | 2.9s |
| c3_苏璃月/c3_苏璃月2.mp4 | 15.07s | 2.9s |
| c3_苏璃月/c3_苏璃月3.mp4 | 12.04s | 2.92s |
| c3_苏璃月/c3_苏璃月4.mp4 | 15.07s | 2.9s |
| c4_柳红袖/c4_柳红袖.mp4 | 15.07s | 2.9s |
| c5_苓夭夭/c5_苓夭夭.mp4 | 12.04s | 2.92s |
| c6_白月清/c6_白月清.mp4 | 12.04s | 2.92s |
| c7_赵焚天/c7_赵焚天1.mp4 | 4.06s | 2.9s |
| c7_赵焚天/c7_赵焚天2.mp4 | 4.06s | 2.9s |
| c7_赵焚天/c7_赵焚天3.mp4 | 3.04s | 2.92s |
| c8_方鼎元/c8_方鼎元.mp4 | 4.06s | 2.9s |
| c9_韩夺心/c9_韩夺心.mp4 | 4.06s | 2.9s |

No conflicts found in:
- `projects/ai_video_management/` (webapp 代码 — 不 parse 时长字段；trimmed mp4 仍是合法 H.264/AAC，前端 `<video>` tag 照常播放)
- `agent_refs/project/ai_video.md` rule #12.5（character turntable 锁 2.9s — 本 op 是把 artifact 主动对齐到现有规则，无规则改动）
- rule #12.10 v2 (scene reference 3.9s) — 不在范围（scene mp4 不动）
- `ai_videos/mozun_chongsheng/scenes/` 任何 mp4（明确排除；rule 不同）
- `episodes/ep*/prompts/shot*/shot*.md` shot prompt — `{ref_c{N}_*}` placeholder 引用按文件名不按时长，path 不变；仅 mtime + 时长变了，shot prompt 文件本身不需要 patch
- `characters/c*/c*_seedream.md` Seedream 立绘 prompt — 不动
- `interview/qa.md` / `findings/` / `final_specs/spec.md` / `validation/*` — webapp scope / 数据-op 都不冲突

Operational notes:
- 之前用户报告的 `导入失败: Method Not Allowed`（follow-up 012）必须先 restart backend（`make run-backend` 现 default `--reload`，新 session 起就生效）— 否则点 `📥 导入 + 重命名` 按钮仍走旧进程。本 follow-up 与 012 是同一会话内独立 op，互不影响。
- `imageio-ffmpeg` 安装位置 `%LOCALAPPDATA%\Packages\PythonSoftwareFoundation.Python.3.13_*\LocalCache\local-packages\Python313\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe`；调用方式 `python -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())"` 给出绝对路径。后续如果要支持「webapp 内一键 trim」，backend 加 `imageio-ffmpeg` 依赖 + 新 endpoint，但本 follow-up 不引入这层（用户原 prompt 是 one-shot ask，没要功能化）。

## Follow-up 012 — 2026-05-11 12:28:33
Source: user_input/follow_ups/012-20260511-122833-backend-autoreload-stale-routes.md
Summary: 修复用户报告的 `导入失败: Method Not Allowed` bug — 根因诊断为 stale-backend：`backend/main.py` 用 `uvicorn.run(app, ...)` app-instance 启动，**不开 `--reload`**；follow-up 009 加的 `POST /api/import-from-downloads` 在代码层 register 正确（TestClient 命中 → 200），但用户的 Python 进程是 follow-up 009 之前启动的旧实例，浏览器 POST 撞 fastapi 默认 405 fallback（体 `{"detail":"Method Not Allowed"}`，被前端 `readJson` 当作 string detail 塞进 toast，渲染为带空格 Title Case 错误串）。修复：让 `make run-backend` 默认开 uvicorn `--reload`，新 endpoint 即时生效，dev workflow 不再要求手动重启。Immediate workaround：Ctrl+C → `make run-backend` 重启即可点按钮成功。

Auto-updated:
- `specs/development/ai_video_management/user_input/revised_prompt.md` — Last regenerated 改 2026-05-11 12:28:33；Composed-from list 加 follow-up 012；header 摘要描述根因 + 修复 + workaround；prior follow-up 011 line 移到 prior 列表。
- `projects/ai_video_management/backend/main.py` — 加 `--no-reload` argparse flag（default 不传 = reload 开）；reload 分支调 `uvicorn.run("libs.asgi:app", host=..., port=..., reload=True, reload_dirs=["libs"])` —— uvicorn reload 模式硬约束必须传 import-string 而非 app instance；no-reload 分支保持原 `create_app(...)` + `uvicorn.run(app, ...)` 行为不变，给 `make run-prod` 之后想跑长任务用。
- `projects/ai_video_management/backend/libs/asgi.py` (NEW) — `libs.asgi:app` 入口 module；闭包 `create_app(RepoRoot.find(), BoundOrigin(HOST=127.0.0.1, PORT=8766), serve_static=True)`；dev 模式下 `backend/static/` 为空（只有 .gitkeep），mount 不报错，SPA 由 Vite 5174 提供。
- `projects/ai_video_management/backend/tests/test_boot_smoke.py` — 新加 `test_all_post_endpoints_registered`：枚举 `app.routes` 的 `(method, path)` pair，断言 `{("POST","/api/rename-media"), ("POST","/api/archive-media"), ("POST","/api/unarchive-media"), ("POST","/api/import-from-downloads")}` 全部在内；下次有人 rename / typo / 漏 register 这四个 endpoint 之一，boot-smoke 立刻红，避免相同 stale-routes UX 退化。已 verify `make boot-smoke` 7/7 通过。

No conflicts found in:
- `Makefile` — `run-backend` target 不动（仍是 `python main.py`，新 default `--reload` 自动启用）
- `frontend/src/api.ts` `readJson` — string vs object detail 解析路径不变；stale-backend 不再发生后，405 体只会来自我们自己结构化 catch-all (`{detail:{kind:"method_not_allowed"}}`)，toast 串变 lowercase snake_case
- `OriginHostMiddleware.GUARDED_ROUTES` — 与本 bug 无关；POST endpoint 加 Origin/Host gate 留给后续 follow-up
- `final_specs/spec.md` / `validation/*` / `interview/qa.md` / `findings/` — 行为契约不变，只是部署 / 进程管理姿势改了
- 其它 backend libs / frontend 组件

## Follow-up 011 — 2026-05-11 20:25:46
Source: user_input/follow_ups/011-20260511-202546-batch-archive-media-multi-select.md
Summary: 在 SiblingMedia grid 加 multi-select + 批量 Archive / Unarchive — 每个 media tile 左上角 always-visible checkbox；per-section toolbar (`Select all` / `Clear` / `Archive Selected (N)` 或 `Unarchive Selected (N)`)；批量串行调用已存在的 `POST /api/archive-media` / `POST /api/unarchive-media`（无新 backend endpoint）；continue-on-error 聚合成功/失败 announce 到 `#aria-live-toast`；per-tile 单文件按钮保留兼容，批量 in-flight 期间整段 disabled。Selection state 在 active / archived 两 section 独立。范围 = SiblingMedia 已经覆盖的所有 folder（character / scene / shot / episode / 任何含 media 的 `.md` 同 folder）— 无需 per-folder 分别加。

Auto-updated:
- `specs/development/ai_video_management/user_input/revised_prompt.md` — Last regenerated bumped to 2026-05-11 20:25:46；Composed-from list 加 follow-up 011；header 摘要描述 multi-select + 批量按钮 + 无新 backend endpoint + continue-on-error；prior follow-up 010 line 移到 prior 列表。
- `specs/development/ai_video_management/final_specs/spec.md` — FR-9 注释扩展提及 follow-up 011 的批量层是 PURELY FRONTEND，循环已存在的 FR-9c / FR-9d endpoint，无新 endpoint。
- `projects/ai_video_management/frontend/src/components/SiblingMedia.tsx` — `MediaTile` 加 `selected` / `onToggleSelect` / `selectionBusy` props + 左上角 corner checkbox；`SiblingMedia` 新增两组独立 selection state (`selectedActive`, `selectedArchived`)、整段 `busy` 锁、批量 `handleBatchArchive` / `handleBatchUnarchive` 串行循环 + continue-on-error 聚合 announce；per-section `Toolbar` 子组件含 `Select all` / `Clear` / `Archive Selected (N)` (active) 或 `Unarchive Selected (N)` (archived)；per-tile 单文件按钮保留 + 共享 busy disable。
- `projects/ai_video_management/frontend/src/styles.css` — 新增 `.sibling-media-toolbar` (flex row, padding, light-theme bg) + `.sibling-media-toolbar button` 颜色 / disabled 灰阶 + `.sibling-media-item input.tile-checkbox` 左上角 absolute + 半透明白底 + scale 1.3。

No conflicts found in:
- backend `media_archiver.py` / `api.py`（批量纯前端循环已存在 endpoint，无 backend 改动）
- `interview/qa.md` / `findings/` / `validation/*`（webapp scope 未变；批量只是 UI 层增强已有的 FR-9c / FR-9d 功能）
- 其它 frontend 组件 (`Reader.tsx`, `api.ts` 等保持不动 — `onChange` 回调链已支撑 tree refresh)

## Follow-up 010 — 2026-05-11 12:04:54
Source: user_input/follow_ups/010-20260511-120454-scene-ref-video-3.9s-all-angles.md
Summary: **Cross-project rule change — ai_video_management webapp 本身不受影响**。把 ai_video pipeline 的 scene reference video prompt 时长上限 2.9s → **3.9s**；schema 从原"全景定场 + 中景横移 + 长焦推近"三段重写为"**正面建场 + 水平 360° 环绕 + 垂直三视角 + 中景横移 + 长焦特写**"**五段 all-angle 序列**（起手必须 front view）；prompt body 显式加 `音频: 无（视频纯视觉 reference）` 字段并把 byte-identical 字段集合 7→8。目标：给 Seedance 等下游 video 模型最大密度场景 reference，让它据此生成真正 shot 视频。Character turntable rule #12.5 保持 2.9s 不动。Hook 把本 prompt 归属到 ai_video_management 项目；用户在三选题中再次确认 follow-up 持久化位置 — 故登记于此。

Auto-updated:
- `specs/development/ai_video_management/user_input/revised_prompt.md` — Last regenerated 改 2026-05-11 12:04:54；Composed-from 加 follow-up 010；header 摘要描述 3.9s + 五段 all-angle + visuals-only + 跨项目改动范围；prior follow-up 009 line 移到 prior 列表。
- `.claude/agent_refs/project/ai_video.md` — rule #12.10 全段重写（"为什么 2.9s 硬上限" → "为什么 3.9s 硬上限"；schema header / 用法 / body header / timed beats / 节奏 / 时长 / 负向 全部由 2.9s 改 3.9s；schema body 从三段改五段；新增 `音频: 无` 行；byte-identical 字段集 7→8；origin 行追加 follow-up 010 来源）。
- `ai_videos/mozun_chongsheng/scenes/s1_长阶顶/s1_长阶顶.md` 至 `s9_识海/s9_识海.md`（9 文件） — 「场景 reference video prompt — Seedance / Sora / Veo / Runway Gen-3 / Kling」段全段重写：header `2.9s` → `3.9s`；用法说明 `≤ 2.9s 硬上限` → `≤ 3.9s 硬上限`；body header 描述更新为 `正面建场 + 水平 360° 环绕 + 垂直三视角 + 中景横移 + 长焦特写`；动作 timed beats 五段（0-0.8s 正面建场 / 0.8-1.7s 水平 360° 环绕 / 1.7-2.5s 垂直三视角 / 2.5-3.3s 中景横移 / 3.3-3.9s 长焦特写定格）；节奏行 `极快（2.9s 内...）` → `极快（3.9s 内...全角度覆盖）`；时长行 `2.9s` → `3.9s`；新增 `音频: 无（视频纯视觉 reference，不要 BGM / 音效 / 旁白 / 环境音）` 行；负向 `不要 超过 2.9s` → `不要 超过 3.9s`，并加 `不要 任何音频 / BGM / 音效 / 旁白 / 环境音`。
- `specs/ai_video/mozun_chongsheng/changelog.md` — 追加 cross-ref 条目指向本 follow-up，记录 9 个 scene .md 被 patch。

No conflicts found in:
- `projects/ai_video_management/` (webapp 代码 — 不解析 .md 时长字段，schema 改动只是字节差)
- `specs/development/ai_video_management/interview/qa.md` / `findings/` / `final_specs/spec.md` / `validation/*` (webapp scope 未变)
- `.claude/agent_refs/project/ai_video.md` rule #12.5 (character turntable，按用户确认保持 2.9s)
- 其它 `ai_videos/` 项目（目前仅 mozun_chongsheng 一个）

## Follow-up 009 — 2026-05-11 19:56:38
Source: user_input/follow_ups/009-20260511-195638-import-from-downloads-classifier.md
Summary: 把 drama-row "🏷 重命名" 按钮升级为 "📥 导入 + 重命名" 一键流程 — 后端扫描用户 OS 的 Downloads folder（过去 7 天 by mtime 的 image/video 文件，只 immediate children），按文件名 substring-match drama 下 `characters/c*/` + `scenes/s*/` + `episodes/ep*/prompts/shot*/` folder 名（含下划线-split tokens + shot 额外的 epNN_shotNN / epNN tokens），longest-match 胜（tie shot > scene > character）；无匹配 → `ai_videos/{drama}/not_matched/`；移完后调 `MediaRenamer.rename_drama()` 并 exclude `not_matched/`，保留原始文件名供用户人肉 triage。新增 `POST /api/import-from-downloads` endpoint。**首次允许后端读取 EXPOSED_TREE 外路径** — 源端硬化：只读 Downloads immediate children + 扩展名白名单 + mtime 窗 + 拒 symlink + basename 正则 + 长度上限。

Auto-updated:
- `specs/development/ai_video_management/user_input/revised_prompt.md` — Last regenerated bumped to 2026-05-11 19:56:38；Composed-from list 加 follow-up 009；header 摘要描述 import+rename 一键流程 + sandbox 外读取的硬化要点；prior follow-up 008 line 移到 prior 列表。
- `specs/development/ai_video_management/final_specs/spec.md` — FR-1 backend libs 列表加 `downloads_importer.py` (follow-up 009)；FR-9 注释扩展提及 follow-up 009 的 import endpoint + sandbox 外读取；新增 FR-9e 描述 `POST /api/import-from-downloads` 完整契约（drama-scope body / Downloads 源端硬化 / 分类器算法 / target_exists 处理 / chain 调 MediaRenamer.rename_drama exclude not_matched / 返回 schema / 错误码表）。
- `specs/development/ai_video_management/validation/acceptance_criteria.md` — FR→Scenario 矩阵加 FR-9e → U3.14 行；新增 Scenario U3.14 覆盖 7-fixture 文件分类正确性（character/scene/shot/unmatched）+ window 静默跳过 + 非 media 跳过 + symlink 跳过 + 二次空运行 + 错误码面 (400/404/405/500) + Origin/Host gate。
- `specs/development/ai_video_management/validation/security.md` — coverage matrix 加 FR-9b / FR-9c / FR-9d / FR-9e 行（FR-9e 标记 `partial` 因为新引入 sandbox 边界）；Open carve-outs 加 #6 详述 `/api/import-from-downloads` 是首个外读端点，列出 6 条硬化 + 2 类残余风险（destination collision 由 target_exists 兜底；任意名匹配靠 not_matched 兜底），明确若需更严格则后续 follow-up 加 per-file 用户确认。
- `projects/ai_video_management/backend/libs/downloads_importer.py` (NEW) — `DownloadsImporter` 类 + `ImportResult` dataclass + `_Candidate` 内部 dataclass + `DownloadsDirMissing` 异常；`import_drama(rel)` 入口 validate drama 路径（复用 `MediaRenamer.validate_drama`）→ 验证 Downloads 目录存在 → `_collect_candidates(drama)` 拉取 characters/scenes/shots 三类 candidate folder 及其 lowercase tokens → `_iter_downloads(cutoff)` 扫 Downloads immediate children 过滤 ext/mtime/symlink → 每文件 basename 形状校验 + `_classify` 选目标 → `dst.mkdir(parents=True, exist_ok=True)` + `shutil.move` → 目标已存在 / mkdir 失败 / move 失败均加入 errors[] 不中断 batch → 最后调 `MediaRenamer.rename_drama(rel, excluded_folder_names=frozenset({"not_matched"}))` 把 rename_result 塞入 ImportResult；`_classify` 用 tuple key 排序选最佳 (score, kind_priority, lex-tiebreak)；`_tokens(folder_name)` 抽 primary + 下划线-split tokens (length ≥ 2)，去重保序；`_is_safe_basename` regex + 长度检查；`_display_src` 把 Downloads 路径渲染为 `~/<rel>` 避免泄露 home；环境变量 `AI_VIDEO_MGMT_DOWNLOADS_DIR` 可覆盖 Downloads 默认路径以便测试；`NOT_MATCHED_DIR_NAME = "not_matched"` constant 公开导出。
- `projects/ai_video_management/backend/libs/media_renamer.py` — `rename_drama()` 签名加 optional kwarg `excluded_folder_names: frozenset[str] | None = None`（None / 空集时行为完全不变 — 现有 /api/rename-media 调用方零影响）；非空时 merge 进 `self._exposed.excluded_dirs()` 形成更大的 excluded set 传入 `_iter_folders`；新增 public method `validate_drama(rel)` 作 `_validate_drama` 的 thin wrapper，给 DownloadsImporter 用避免跨模块调私有。
- `projects/ai_video_management/backend/libs/api.py` — module docstring "7 endpoints" → "8 endpoints"；imports 加 `DownloadsImporter` + `DownloadsDirMissing`；`ImportFromDownloadsBody` Pydantic model；`downloads_importer = DownloadsImporter(exposed, resolver, media_renamer)` 实例化；`POST /api/import-from-downloads` 路由 (200 / 400 invalid_drama_path / 404 not_found / 500 downloads_dir_missing) + 405 method-not-allowed guard。
- `projects/ai_video_management/frontend/src/api.ts` — 新增 `ImportFromDownloadsResult` type (含 nested `rename: RenameMediaResult`) + `importFromDownloads(path)` POST helper。`renameMedia` helper 保留（不再被 Sidebar 调，但保留以兼容、便测试）。
- `projects/ai_video_management/frontend/src/components/Sidebar.tsx` — import 把 `renameMedia` 替换为 `importFromDownloads`；`onRenameClick` 改调 `importFromDownloads` + toast text 改 `已导入 N / 未分类 M / 已重命名 K / 失败 E`；button label "🏷 重命名" → "📥 导入 + 重命名"，aria-label / title 同步更新描述新行为（"从 Downloads 按文件名分类导入近 7 天的图片/视频，并按 parent folder 重命名"）。

Verification (smoke checks):
- Python imports compile clean: `from libs.downloads_importer import DownloadsImporter, NOT_MATCHED_DIR_NAME, DownloadsDirMissing` + `from libs.api import create_app` 无异常。
- 分类器 smoke test（ASCII fixture，7 sample filenames）：`kling_c1_aaa_test.mp4` → c1_aaa (character) ✓；`jimeng-yewuchen-pic.png` → c2_yewuchen (character) ✓；`ep01_shot01_kling.mp4` → shot01 (shot) ✓（通过 ep01_shot01 长 token 命中）；`random_file.mp4` → not_matched ✓；`shot03_v2.mp4` → shot03 (shot) ✓；`shandao_seedance.mp4` → s7_shandao (scene) ✓；`just_c1.mp4` → c1_aaa (character) ✓（短 token 命中也算）。
- Frontend `npx tsc --noEmit` 无新错误（仅 vite.config.ts 两个 pre-existing 错误，与本 follow-up 无关）。

Deferred (not in this follow-up):
- backend pytest under `backend/tests/` for `downloads_importer.py` + `api.py /api/import-from-downloads` 路由（与 follow-ups 005-008 一致推迟到批量补测）。fixture 需要 `AI_VIDEO_MGMT_DOWNLOADS_DIR` env override + tmp_path drama scaffold。
- e2e Playwright 验证按钮 + toast 行为（同上推迟）。
- dry-run 预览模式 (`?dry_run=true`) 允许用户在 move 前看到将分到何处。
- 单文件 import / 多选 import（v1 batch only）。
- 跨 drama 比对（v1 只匹配点击的 drama；如果文件名包含其他 drama 的 character/scene 名，会被分到 not_matched 而非其他 drama）。
- 防 collision 自动重命名（v1 target_exists 直接报 error；后续可加 `<basename>_1.mp4` 自动 suffix）。

Severity: Medium-Low. Additive endpoint, no breaking changes. Security 边界扩展（首次读 sandbox 外）已通过 6 层硬化 + 残余风险记录在 security.md carve-out #6；用户决策"`excluded_folder_names={"not_matched"}`"保证未分类文件的原始 Downloads 文件名留存。其他 endpoint 零影响。

## Follow-up 008 — 2026-05-10 20:18:26
Source: user_input/follow_ups/008-20260510-201826-archive-unarchive-media.md
Summary: 在 SiblingMedia 每个 media tile 上加一个 inline "📦 Archive" / "↺ Unarchive" 按钮，点击把单个 image/video 文件移动到（或移出）同 folder 下的 `archive/` 子目录。新增两个后端 endpoint `POST /api/archive-media` + `POST /api/unarchive-media`；archive/ 在 tree sidebar 作为常规 folder 显示（不加进 `_EXCLUDED_DIRS`）；unarchive 后若 archive/ 已空自动 rmdir；rename-media batch 不跳 archive/（archive/ 内文件按 parent name "archive" 也参与 rename — 用户决策）。

Auto-updated:
- `specs/development/ai_video_management/user_input/revised_prompt.md` — Last regenerated bumped to 2026-05-10 20:18:26；Composed-from list 加 follow-up 008；header 摘要描述新功能；prior follow-up 007 line 移到 prior 列表。
- `specs/development/ai_video_management/final_specs/spec.md` — FR-1 backend libs 列表加 `media_archiver.py` (follow-up 008)；FR-9 注释扩展提及 follow-up 008 的 archive endpoints；新增 FR-9c (`POST /api/archive-media`) 与 FR-9d (`POST /api/unarchive-media`) 描述 body / response / error surface (`400 invalid_path/extension_not_allowed/already_archived/not_in_archive`、`404 not_found`、`409 target_exists`、`500 move_failed`)；FR-9b 注释提示 archive/ 不被 rename-media 排除。
- `specs/development/ai_video_management/validation/acceptance_criteria.md` — FR→Scenario 矩阵加 FR-9b (U3.12) / FR-9c (U3.13) / FR-9d (U3.13) 行；新增 Scenario U3.12 (rename-media，补 follow-up 007 缺漏) + U3.13 (archive/unarchive-media 完整错误码面 + Origin/Host gate)。
- `projects/ai_video_management/backend/libs/media_archiver.py` (NEW) — `MediaArchiver` 类 + `MoveResult` dataclass + 异常 `InvalidPath/NotFound/NotMedia/AlreadyArchived/NotInArchive/TargetExists/MoveFailed`；`archive(rel)` 入口 validate path（在 sandbox 内 + ext ∈ MEDIA_EXTENSIONS + 文件存在 + 不是 symlink + parent 不是 archive）→ mkdir archive/（exist_ok=True）→ 检查目标不存在 → atomic `Path.rename()`；`unarchive(rel)` 入口 validate path + 要求 parent.name == "archive" → 检查目标 parent dir 不存在同名 → atomic rename → 若 archive/ 空则 rmdir（best-effort）；`ARCHIVE_DIR_NAME = "archive"` constant 公开导出。
- `projects/ai_video_management/backend/libs/api.py` — module docstring "5 endpoints" → "7 endpoints"；imports 加 `media_archiver` 全部异常 + `MediaArchiver`（用 `as ArchiveInvalidPath/ArchiveNotFound` 别名避免与 media_renamer 同名异常冲突）；`ArchiveMediaBody` Pydantic model；`media_archiver = MediaArchiver(exposed, resolver)` 实例化；`POST /api/archive-media` 路由 (200 / 400 invalid_path/extension_not_allowed/already_archived / 404 not_found / 409 target_exists / 500 move_failed) + `POST /api/unarchive-media` 路由 (同 400 套 + `not_in_archive` / 404 / 409 / 500)；两个端点各自的 GET/PUT/PATCH/DELETE 405 method-not-allowed guard。
- `projects/ai_video_management/frontend/src/api.ts` — 新增 `ArchiveMediaResult` type + `archiveMedia(path)` + `unarchiveMedia(path)` POST helpers，签名 `Promise<{from: string, to: string}>`。
- `projects/ai_video_management/frontend/src/components/SiblingMedia.tsx` — Props 加 `onChange?: () => void`；新 helper `findArchivedMedia` 扫 `<currentParent>/archive/` 内 media；新 `MediaTile` 子组件渲染 figure + per-tile "📦 Archive" / "↺ Unarchive" button（in-flight disabled、`aria-label`、tooltip）；section 内拆 "📁 Folder media" + "📦 Archived · 已归档" 两个 grid；archive / unarchive 成功后 `announce()` 写 `#aria-live-toast` 并调 `onChange`；错误时 announce 错误 kind。
- `projects/ai_video_management/frontend/src/components/Reader.tsx` — `<SiblingMedia>` 透传 `onChange={onSaved}`（命名复用：archive/unarchive 也是 tree mutation → 触发 refreshKey bump）。
- `projects/ai_video_management/frontend/src/styles.css` — 新增 `.sibling-media-archive-btn` (右下角浮动 inline button，11px pill 风格 + hover/disabled 状态) + `.sibling-media-item.is-archived` (opacity 0.7 + 灰阶 filter 0.5) 视觉降权区分已归档 tile。

Verification (smoke checks):
- Python imports compile clean: `from libs.media_archiver import MediaArchiver, ARCHIVE_DIR_NAME` + `from libs.api import create_app` 无异常。
- Frontend `npx tsc --noEmit` 无新错误（仅 vite.config.ts 两个 pre-existing 错误，与本 follow-up 无关）。
- 两个 endpoints 405 guard 与已有 `/api/rename-media` 形状一致。

Deferred (not in this follow-up):
- backend pytest under `backend/tests/` for `media_archiver.py` + `api.py /api/{archive,unarchive}-media` 路由（与 follow-up 005/006/007 一致推迟到批量补测）。
- e2e Playwright 验证 per-tile button 行为（同上推迟）。
- 批量归档 / 多选归档（v1 per-file，单独 follow-up 触发批量）。
- archive/ 嵌套层级限制（v1 不阻止 `archive/archive/`，只用 immediate parent.name 判定）。

Severity: Low — additive feature, no breaking changes, no schema changes to existing endpoints. archive/ 与 rename-media 的交互（archive/ 内文件也参与 rename）是用户主动选择的 design tradeoff，不属 bug。

## Follow-up 007 — 2026-05-10 17:04:38
Source: user_input/follow_ups/007-20260510-170438-rename-media-to-parent-folder.md
Summary: 在每个短剧（drama）level 加一个 "🏷 重命名" 按钮，点击触发后端递归扫描该短剧 folder 树下所有 image/video 文件，按 immediate parent folder name 重命名（同扩展名 1 个 → `{folder}.ext`，多个 → `{folder}1.ext`、`{folder}2.ext`、…，按 lexicographic 顺序）。新增 `POST /api/rename-media` endpoint；只 touch media 文件；非法路径 / 非 drama-level 拒绝；两阶段 temp-rename 处理 intra-folder collision；refresh tree on完成。

Auto-updated:
- `specs/development/ai_video_management/user_input/revised_prompt.md` — Last regenerated bumped to 2026-05-10 17:04:38；Composed-from list 加 follow-up 007；header 摘要描述新功能。
- `specs/development/ai_video_management/final_specs/spec.md` — FR-9 加注释指向 follow-up 007；新增 FR-9b 描述 `POST /api/rename-media` body / response / behavior；FR-10 提及 `/api/media` (follow-up 005) 的存在 (旧文未补齐) 并保持 read endpoints 列表完整。
- `projects/ai_video_management/backend/libs/media_renamer.py` (NEW) — `MediaRenamer` 类 + `RenameOp/RenameError/RenameResult` dataclasses + `InvalidDramaPath/DramaNotFound` 异常；`rename_drama(rel)` 入口验证 path 形状（必须 `ai_videos/{drama}`，immediate child of `ai_videos/`）+ 在 sandbox 内 + dir 存在；`_iter_folders` 递归（跳过 `_EXCLUDED_DIRS` + symlink）；`_plan_folder` 按扩展名分组生成 RenameOp 列表（已是 target name → skip）；`_apply_ops` 两阶段 temp-rename 避免 collision，OSError 单独记录到 errors 不中断 batch。
- `projects/ai_video_management/backend/libs/api.py` — module docstring 改 "4 endpoints" → "5 endpoints"；imports 加 `MediaRenamer/InvalidDramaPath/DramaNotFound`；`RenameMediaBody` Pydantic model；`media_renamer = MediaRenamer(exposed, resolver)` 实例化；`POST /api/rename-media` 路由 (200 / 400 invalid_drama_path / 404 not_found)；`/api/rename-media` GET/PUT/PATCH/DELETE 405 method-not-allowed guard。
- `projects/ai_video_management/frontend/src/api.ts` — 新增 `RenameMediaResult` type + `renameMedia(path)` POST helper。
- `projects/ai_video_management/frontend/src/App.tsx` — Sidebar prop 加 `onTreeReload={() => setRefreshKey((k) => k + 1)}` 让 sidebar 在 rename 完成后能 trigger 整树 refresh。
- `projects/ai_video_management/frontend/src/components/Sidebar.tsx` — props 加 `onTreeReload?`；新增 `renamingPath/renameToast` state + `onRenameClick` callback；导入 `renameMedia` + `ApiError`；drama 节点（path 形如 `ai_videos/{name}` 且 type==directory）row 上紧邻 subtype-badge 渲染 "🏷 重命名" button (in-flight disabled)；sidebar 顶部 conditional toast 显示结果摘要 (renamed/skipped/errors counts) 或错误信息，带 dismiss 按钮 + `aria-live="polite"` 公告。Button click `e.stopPropagation()` 避免触发 row 的 expand-collapse。
- `projects/ai_video_management/frontend/src/styles.css` — 新增 `.drama-rename-btn` (轻量 11px pill style，hover/disabled 状态) + `.sidebar-toast/.sidebar-toast-ok/.sidebar-toast-err/.sidebar-toast-dismiss` (顶置 inline notification using existing `--tint-a` / `--error-bg` 色板)。

Verification (smoke tests run in tempdir):
- 多文件 + 单文件 + 已正确命名 + 跨扩展名混合 → 正确分组、正确编号、正确 skip。
- swap-collision (`aaa.mp4` 抢 `foo1.mp4`，原 `foo1.mp4` push 到 `foo2.mp4`) → 两阶段 temp-rename 无数据丢失。
- 入参形状错误 (`research/foo`、`ai_videos/X/sub`) → `InvalidDramaPath`。
- 不存在的 drama → `DramaNotFound`。

Deferred (not in this follow-up):
- backend pytest under `backend/tests/` for `media_renamer.py` + `api.py /api/rename-media` 路由（与 follow-up 005/006 一致地批量补测）。
- e2e Playwright 验证按钮行为（同上推迟）。
- dry-run 预览模式 (`?dry_run=true`)。

Severity: Low — additive feature, no breaking changes, no schema changes to existing endpoints.

## Follow-up 006 — 2026-05-10 16:40:54
Source: user_input/follow_ups/006-20260510-164054-stale-runtime-instructions.md
Summary: 用户报告 follow-up 005 后 mp4 仍不在 webapp 左侧 nav 显示（user 已 drop `c3_苏璃月{1,2,3}.mp4` 共 3 个 video 文件 + 1 个 md 到 `ai_videos/mozun_chongsheng/characters/c3_苏璃月/`）。**根因：用户运行中的 webapp 进程没 reload 新代码**，不是代码 bug。验证：直接调用 `TreeWalker.build()` 已 emit `type: "video"` 节点；`MEDIA_EXTENSIONS` 包含 `.mp4`；`exposed.is_inside('ai_videos/mozun_chongsheng/characters/c3_苏璃月/c3_苏璃月1.mp4')` 返回 `True`。Zero code changes 本 follow-up — 仅记录 reload 操作步骤 + 标记 deferred quality-of-life improvements。

Diagnosis (verified):
- Files exist: 3 mp4 + 1 md in `c3_苏璃月/` folder (sizes 11.9MB / 12.0MB / 21.6MB / 10K).
- Backend code verified at runtime: `TREE_VISIBLE_EXTENSIONS` ⊃ `.mp4` ✓; `MEDIA_EXTENSIONS` ⊃ `.mp4` ✓; tree walker emits `video` type for mp4 leaves ✓.
- `backend/static/` is empty (just `.gitkeep`). `frontend/dist/` doesn't exist. → user is running vite dev server for frontend (auto-reloads) + `python main.py` for backend (NO auto-reload).
- `python main.py` is plain spawn (no `uvicorn --reload`), so backend stays on stale code until manually restarted.

Auto-updated:
- `specs/development/ai_video_management/user_input/revised_prompt.md` — Last regenerated bumped to 2026-05-10 16:40:54 + follow-up 006 摘要.
- (Zero code changes — follow-up 005 backend / frontend code is correct as written.)

User next steps (resolve immediately):

1. **Restart backend**: kill the running `python main.py` process (Ctrl+C in its terminal, or kill via Task Manager — the one bound to port 8766) → re-run `make run-backend` (or `cd backend && PYTHONPATH=. python main.py`).
2. **If using vite dev server (`make run-frontend`)**: should auto-reload; if stale, hard-refresh browser (Ctrl+F5).
3. **If using production build**: rebuild frontend (`cd frontend && npm run build`) and ensure backend's `static/` dir contains the built dist (currently empty — separate Makefile gap deferred).
4. **Verify** by selecting `c3_苏璃月/` folder in left nav → expect 4 children: `c3_苏璃月.md` (📄) + 3× `c3_苏璃月N.mp4` (🎬) → click any mp4 → inline HTML5 `<video controls>` plays in right Reader pane (HTTP range supported for seeking).

Deferred surgical follow-ups (independent):
- (a) Add `--reload` argv to `backend/main.py` for `uvicorn.run(... reload=True)` dev-mode hot-reload (would require switching `app` from instance to import-string — minor refactor).
- (b) Makefile `run-prod` should `cp -r frontend/dist/* backend/static/` after `build-frontend` so backend serves the bundle (currently `backend/static/` stays empty even after build).
- (c) Backend tests: `test_api_media_route.py` + `test_tree_walker_includes_video.py` (already deferred per follow-up 005).

Severity: Zero (no behavior change, no code change). This entry exists to document a runtime-state issue and to write the reload procedure into the project's follow-up log so future regressions on similar "code change not visible" reports have an immediate playbook.

## Follow-up 005 — 2026-05-10 16:18:39
Source: user_input/follow_ups/005-20260510-161839-media-display-playback.md
Summary: 用户把生成好的 video / image 放进 `ai_videos/{project}/{characters,scenes,shots}/{folder}/` 文件夹（per mozun_chongsheng follow-up 014 的 folder-per-asset schema），但 webapp 左侧 nav 不显示这些 media 文件 + 不能在 Reader 内 inline 显示 / 播放。修复：(A) 后端 `MEDIA_EXTENSIONS` 引入 (mp4/mov/webm/mkv/avi/m4v + jpeg/webp/gif/bmp 共 12 项)；`TREE_VISIBLE_EXTENSIONS = ALLOWED ∪ MEDIA` 让 sidebar 显示 media；视频 tagged 为 `"video"` (新 TreeNodeType)；新增 `/api/media` route by FastAPI FileResponse with proper MIME (bypass 1MB MAX_FILE_BYTES; HTTP range for video seeking)；(B) 前端 Reader 检测 video / image 扩展 → 直接渲染 `<video controls>` / `<img>`；新增 `SiblingMedia` 组件让用户查看 .md 时下方 grid display 同 folder 媒体；新增 `mediaUrl()` helper；Sidebar / linkResolver 加 "video" 类型识别 + 🎬 icon；CSS 加 `.media-view` + `.sibling-media-grid` styling.

Auto-updated:
- `specs/development/ai_video_management/user_input/revised_prompt.md` — Last regenerated bumped to 2026-05-10 16:18:39 + follow-up 005 摘要.
- `projects/ai_video_management/backend/libs/exposed_tree.py` — 新增 `MEDIA_EXTENSIONS` (12 项 image+video) + `TREE_VISIBLE_EXTENSIONS = ALLOWED ∪ MEDIA`. `ALLOWED_EXTENSIONS` / `MAX_FILE_BYTES` 不变（`/api/file` 行为对 .md/.json 等 unchanged；只添加新的 media surface).
- `projects/ai_video_management/backend/libs/tree_walker.py` — `_is_allowed_leaf` 改用 `TREE_VISIBLE_EXTENSIONS`；`_leaf_for` 扩展 type tagging：`.mp4/.mov/.webm/.mkv/.avi/.m4v` → `type: "video"`；`.png/.jpg/.jpeg/.webp/.gif/.bmp` → `type: "image"`. `_IMAGE_EXTENSIONS` / `_VIDEO_EXTENSIONS` 各自定义.
- `projects/ai_video_management/backend/libs/api.py` — 新增 `_MEDIA_MIME_MAP` (12 ext → MIME) + `GET /api/media` 路由 (查询 `path` → exposed.is_inside sandbox check → resolver.resolve → FastAPI FileResponse with media_type)；新增 `/api/media` PUT/PATCH/DELETE/POST 405 method-not-allowed guard (镜像 `/api/file` 的 method 限制风格)；module docstring 改 "3 endpoints" → "4 endpoints".
- `projects/ai_video_management/frontend/src/types.ts` — `TreeNodeType` 加 `"video"`.
- `projects/ai_video_management/frontend/src/api.ts` — 新增 `mediaUrl(path, mtime?)` helper return `/api/media?path=...&mtime=...`.
- `projects/ai_video_management/frontend/src/components/SiblingMedia.tsx` (NEW) — `<SiblingMedia currentPath knownPaths>` scans knownPaths for sibling media in same folder, renders `<img>` for images / `<video controls>` for videos via `mediaUrl()`. `findSiblingMedia` helper filters by parent prefix + media regex.
- `projects/ai_video_management/frontend/src/components/Reader.tsx` — extended `extOf` is now reused at component top; added `IMAGE_EXTS` / `VIDEO_EXTS` / `isMediaImage` / `isMediaVideo` / `isMediaOnly` flags. `load()` skips `fetchFile` for media-only paths (videos can exceed 1MB) — sets minimal placeholder file. Render branch adds: video → `<video controls src={mediaUrl(path)}>`; non-png-jpg image → `<img src={mediaUrl(path)}>`; markdown branch now appends `<SiblingMedia />` below `<Renderer />`. Edit toggle hidden for both image + video.
- `projects/ai_video_management/frontend/src/components/Sidebar.tsx` — `node.type` checks updated in 4 places to include `"video"` (auto-collapse / leaf detection / Enter-key select / leaf rendering branch). Added `🎬` icon for video tree leaves.
- `projects/ai_video_management/frontend/src/lib/linkResolver.ts` — `collectFilePaths` 添加 `"video"` type to leaf collection.
- `projects/ai_video_management/frontend/src/styles.css` — 新增 `.media-view` (full-bleed image/video with shadow + 80vh max) + `.sibling-media-grid` (folder-context gallery card with grid row of figure items, max 320×240 thumbnails).

总计 patch 范围: **1 backend libs amend (exposed_tree + tree_walker + api) + 1 frontend types amend + 1 frontend api amend + 1 NEW SiblingMedia.tsx + 1 frontend Reader amend + 1 frontend Sidebar amend + 1 frontend linkResolver amend + 1 styles.css amend + 1 revised_prompt header bump = 9 file changes (8 modified + 1 new)**.

Behavior changes:
- `GET /api/tree` now includes `.mp4/.mov/.webm/.mkv/.avi/.m4v/.jpeg/.webp/.gif/.bmp` files under `ai_videos/**` and `research/**` (was previously only `.md/.json/.yaml/.yml/.jsonl/.txt/.png/.jpg`).
- New endpoint `GET /api/media?path=<rel>` returns raw bytes with proper Content-Type (no base64, no JSON wrapper, no 1MB limit). Same EXPOSED_TREE sandbox + same security headers as `/api/file`.
- Sidebar shows new media files with 🎬 icon for video / 🖼 icon for images (existing). User clicks → Reader displays inline.
- Markdown viewer (e.g., `c1_沧冥.md`) now shows a `📁 Folder media` gallery section below the markdown body, listing all media files in the same folder with inline previews.

No conflicts found in:
- `projects/ai_video_management/backend/libs/file_reader.py` / `file_writer.py` — unchanged (still allows only ALLOWED_EXTENSIONS for /api/file; /api/media is separate route bypassing the size limit).
- `projects/ai_video_management/backend/libs/api_security.py` — unchanged (`/api/media` is GET-only; only PUT routes are in GUARDED_ROUTES; SecurityHeadersMiddleware still applies via global middleware).
- `projects/ai_video_management/backend/libs/safe_resolve.py` / `repo_root.py` — unchanged (sandbox + path resolution reused as-is).
- `projects/ai_video_management/backend/tests/` — TBD: new `test_api_media_route.py` + `test_tree_walker_includes_video.py` deferred to independent surgical follow-up. Existing tests still pass (extension allowlist unchanged for /api/file).
- `projects/spec_driven/` — unchanged.

Severity: Low blast radius (additive only — new MEDIA_EXTENSIONS set, new /api/media route, new SiblingMedia component, new TreeNodeType variant). Existing /api/file + /api/tree contracts preserved (same ALLOWED_EXTENSIONS for /api/file; tree includes new media file types but field names unchanged). Webapp boots and renders existing markdown / image / shot-pair content without regression.

User next steps:
1. Drop a turntable.mp4 into `ai_videos/mozun_chongsheng/characters/c1_沧冥/` → refresh webapp → see `turntable.mp4` appear in left nav under `c1_沧冥/` folder with 🎬 icon → click → video plays inline in Reader.
2. Drop a `ref.png` into `scenes/s1_长阶顶/` → see it in nav with 🖼 icon → click → image displays at 80vh max-height.
3. Open any character / scene / shot `.md` file → see markdown content + new `📁 Folder media · 同 folder 媒体` section at bottom listing all media in same folder with inline previews.

Out of scope (deferred to independent surgical follow-up):
- Backend tests for `/api/media` route + tree_walker video inclusion.
- Audio file support (.mp3 / .wav / .m4a / .ogg).
- Video thumbnail generation (HTML5 `<video preload="metadata">` already provides poster frame fallback).
- PUT /api/media for uploading media via webapp (current contract is read-only — user drops files via filesystem).
- frontend test for SiblingMedia + media route detection.

## Follow-up 004 — 2026-05-09 19:48:37
Source: user_input/follow_ups/004-20260509-194837-allow-chinese-filenames.md
Summary: ai_video_management 已支持 UTF-8 中文文件名（`is_inside` 仅拦截 backslash / NUL byte / 已知 excluded dirs；前端 React Sidebar 直接渲染 `node.name` 中文字符串），无需代码改动。本 follow-up 仅做规则与 spec 文档侧 amend，配合 mozun_chongsheng/002 让 `ai_videos/mozun_chongsheng/characters/` 等"内容性"目录可 opt-in 中文文件名。

Auto-updated:
- `.claude/agent_refs/project/ai_video.md` — 规则 1 amend：明确"内容性"文件可 opt-in 中文命名（结构性文件 shotlist.md / episode.md / shot{NN}_*.md 等仍 English/pinyin；task_name 仍硬性 pinyin/English 因 task_id 构造与跨平台 path stability）。
- `specs/development/ai_video_management/user_input/revised_prompt.md` — Composed-from header 加入 follow_ups/004；Last regenerated bumped 到 2026-05-09 19:48:37。

No conflicts found in: 
- final_specs/spec.md（FR-7 EXPOSED_TREE / FR-8 is_inside / FR-12 path-traversal 与字符集无关；UTF-8 中文路径段已通过现有 sandbox）
- 所有 backend libs（exposed_tree.py / safe_resolve.py / file_reader.py / file_writer.py / api.py / api_security.py 与字符集解耦，仅校验 backslash/NUL/leading-slash/excluded-dirs）
- 所有 frontend src 代码（Sidebar.tsx / Reader.tsx 用 React 渲染 node.name 字符串，浏览器原生支持 UTF-8）
- validation/* 与 tests/*（path-traversal 测试覆盖 ASCII 与 percent-encoded UTF-8 已存在；中文 path segment 通过现有测试集）

不需 code 改动；现有 webapp 直接支持。

## Follow-up 003 — 2026-05-09 15:21:35
Source: user_input/follow_ups/003-20260509-152135-research-folder-and-viewer.md
Summary: Introduce a new repo-root `research/` folder for free-form reference dumps, and surface its contents through the ai_video_management webapp's sidebar viewer alongside the existing AI Videos section. First content drop: 8 仙侠剧 storyline mds (+ index README) under `research/xianxia_storylines/`, sourced from public material on Wikipedia / 百度百科 / 豆瓣 / mainstream press. Backend `EXPOSED_TREE` widened to admit `research/**`; tree walker emits a new `Research` section at the canonical position 2 (after AI Videos). No frontend code changes — Sidebar walks `tree.children` uniformly, so the new section surfaces with working disclosure carets / keyboard nav / file-open behavior automatically. Same Origin/Host gate, same path-traversal hardening, same extension allowlist apply to research files.

Auto-updated:
- specs/development/ai_video_management/final_specs/spec.md — FR-7 amended (5 EXPOSED_TREE roots, research/** added as #2); FR-8 amended (`is_inside` admits `ai_videos/` and `research/`); FR-18 amended (sections in fixed order: AI Videos, Research, Specs, Context — Specs/Context still not-yet-implemented; AI Videos and Research are live); FR-43 amended (sidebar fixed-order section list updated). No new FR/NFR/AC.
- specs/development/ai_video_management/user_input/revised_prompt.md — Composed-from header bumped to include follow-up 003; new "Last regenerated" line at 2026-05-09 15:21:35 documenting the EXPOSED_TREE extension and content drop.
- projects/ai_video_management/backend/libs/exposed_tree.py — new module-level `_ALLOWED_TOP_LEVEL` frozenset {`ai_videos`, `research`}; `is_inside` keys off the set instead of a hardcoded `if first == "ai_videos":`; new `research_dirs()` accessor symmetrical to `ai_video_dirs()`. Class docstring updated to call out the two roots and reference follow-up 003.
- projects/ai_video_management/backend/libs/tree_walker.py — new `_research_section()` method paralleling `_ai_videos_section()`. Walks `research/` recursively via the existing `_walk_filtered` helper using `_is_allowed_leaf`. NO `project_meta` payload (research dirs don't have a sub_type). `build()` updated to include `_research_section()` ordered after `_ai_videos_section()` (matches FR-18).
- projects/ai_video_management/backend/tests/test_tree_walker_consumer_walk.py — `test_tree_single_ai_videos_section` renamed/replaced by `test_tree_sections_order` (asserts `["AI Videos", "Research"]`); old `test_no_other_sections_in_tree` dropped (replaced by the order assertion); new `test_research_section_walks_repo_research_dir` asserts the Research section exists, has `type=section`, and contains at least one child when the repo's `research/` directory has content.
- projects/ai_video_management/backend/tests/test_boot_smoke.py — `test_get_tree_returns_single_ai_videos_section` renamed to `test_get_tree_returns_expected_sections`; assertion updated to `["AI Videos", "Research"]` per FR-18.
- projects/ai_video_management/backend/tests/test_api_security_three_shapes.py — `test_get_tree_unguarded` assertion updated to `["AI Videos", "Research"]` per FR-18.
- research/xianxia_storylines/ — NEW directory at repo root. 9 markdown files: `README.md` (index), `sansheng_sanshi_shili_taohua.md` (三生三世十里桃花 2017), `xiangmi_chenchen_jin_rushuang.md` (香蜜沉沉烬如霜 2018), `liu_li.md` (琉璃 2020), `chenxiang_ru_xie.md` (沉香如屑·沉香重华 2022), `cang_lan_jue.md` (苍兰诀 2022), `chang_yue_jin_ming.md` (长月烬明 2023), `lian_hua_lou.md` (莲花楼 2023, tagged 武侠 not strict 仙侠 — flagged in-file), `yu_feng_xing.md` (与凤行 2024). Each file captures basic info, one-line setting, multi-volume plot synopsis, character table, key虐点/名场面 list, genre tags, AI-video visual-element notes, source citations.

No conflicts found in: interview/qa.md, findings/* (research is not a pipeline output and does not participate in regen prompts; FR-30/FR-32 promotion gates already exclude `ai_videos/{name}/` and now implicitly exclude `research/` too since `stage` allowlist remains `{interview, findings, final_specs, validation}`), validation/* (no AC referenced the section count directly; AC-Level-2 schema assertions still hold — TreeNode shape unchanged), projects/ai_video_management/backend/libs/{api.py, file_reader.py, file_writer.py, safe_resolve.py, repo_root.py, sub_type_lookup.py, api_security.py} (untouched — they all key off `is_inside` for sandbox enforcement, so the EXPOSED_TREE extension flows through automatically), projects/ai_video_management/frontend/src/* (untouched — Sidebar walks `tree.children` uniformly, Reader's path-based render-mode dispatch already handles `.md`/`.png`/`.jpg` under any path; locked-block pill, breadcrumb, link resolver all path-agnostic).

Discovery (out of scope, not fixed): 5 pre-existing backend test failures stem from `ai_videos/wukong_juexing/` no longer existing in the repo (`ai_videos/` is currently empty): `test_put_file_loopback_alias_admit`, `test_put_file_extension_rejected_as_400`, `test_lookup_wukong_juexing_is_short`, `test_lookup_shot_count_for_wukong_juexing`, `test_ai_videos_section_has_project_meta_for_wukong`. These are independent of follow-up 003 and predate this turn — flagged for a future follow-up that either (a) re-creates a synthetic ai_video fixture at `tests/fixtures/`, or (b) marks these tests as `@pytest.mark.skipif(not (repo_root() / "ai_videos" / "wukong_juexing").is_dir(), reason="...")`.

## Follow-up 001 — 2026-05-05 12:15:36

Source: `user_input/follow_ups/001-20260505-121536-ai-videos-only-scope.md`
Summary: narrow ai_video_management scope to `ai_videos/` only — drop `specs/`, `CLAUDE.md`, `.claude/` from EXPOSED_TREE; drop the regen-prompt + pinning + stages features along with their endpoints and frontend surface.

Auto-updated:

**user_input:**
- `revised_prompt.md` — regenerated as raw + follow-up 001; goal section now states "focused viewer/editor"; out-of-scope list expanded to include spec-pipeline operations.

**Generated outputs (`projects/ai_video_management/`):**
- `backend/libs/safe_resolve.py` — `_ALLOWED_TOP_LEVEL` reduced to `{"ai_videos"}`; `.claude/` and `specs/` branches removed from `resolve()`.
- `backend/libs/exposed_tree.py` — entire module rewritten; `is_inside` admits only `ai_videos/`; `claude_root_files`, `claude_skill_files`, `claude_agent_refs`, `specs_ai_video_dirs`, `CANONICAL_STAGES`, `SCRATCH_DIRNAME` constants removed.
- `backend/libs/tree_walker.py` — `_specs_section()`, `_context_section()`, `_build_dotclaude_node()` removed; `build()` now returns a single "AI Videos" section.
- `backend/libs/sub_type_lookup.py` — heuristic switched from `qa.md` parse to `episodes/` directory existence + `script.md`/`shotlist.md` presence (specs/ no longer reachable).
- `backend/libs/api_security.py` — `GUARDED_ROUTES` reduced to `{("PUT", "/api/file")}`.
- `backend/libs/api.py` — entire module rewritten; `/api/regen-prompt`, `/api/promote` (POST + DELETE), `/api/stages` endpoints removed; `RegenPromptBody`, `PromotePostBody`, `PromoteDeleteBody`, `ScopeEpisodeRange` Pydantic models removed.
- `backend/libs/regen_prompt.py` — DELETED.
- `backend/libs/promotions.py` — DELETED.
- `backend/libs/stages.py` — DELETED.
- `backend/tests/test_boot_smoke.py` — assertions updated to expect single AI Videos section; added explicit `test_stages_endpoint_dropped`, `test_regen_prompt_endpoint_dropped`, `test_promote_endpoint_dropped`.
- `backend/tests/test_sub_type_lookup.py` — switched from qa.md-fixture tests to episodes/-directory + shotlist-presence heuristic tests; added synthetic novel + synthetic short + empty-project cases.
- `backend/tests/test_tree_walker_consumer_walk.py` — assertion updated to expect `["AI Videos"]` instead of three sections; added `test_no_specs_or_context_section_in_tree` guard.
- `backend/tests/test_api_security_three_shapes.py` — switched all guarded-route probes from `POST /api/regen-prompt` to `PUT /api/file`; added `test_put_file_extension_rejected_as_400` (image-write rejection at 400).
- `frontend/src/App.tsx` — `/project/:type/:name` and `/stage/:type/:name/:stage` routes removed; `Home` import simplified.
- `frontend/src/types.ts` — removed: `Stage`, `StageModule`, `RegenWarning`, `RegenResult`, `ScopeKind`, `ScopeEpisodeRange`, `PromoteRequest`, `UnpromoteRequest`, `PromoteResult`, `RegenRequest`, `StaleWriteDetail`. Kept: `TreeNode`, `ProjectMeta`, `FileResult`, `WriteResult`, `ApiError`.
- `frontend/src/api.ts` — removed: `fetchStages`, `postRegenPrompt`, `postPromote`, `deletePromote`. Kept: `fetchTree`, `fetchFile`, `putFile`, `imageUrl`.
- `frontend/src/components/Home.tsx` — dropped `Link` to project pages; project list now renders as plain entries with sub-type badges only; added explanatory paragraph pointing users to spec_driven for regen.
- `frontend/src/components/Sidebar.tsx` — `classifySpecPath` and `navigateForNode` removed; `useNavigate` import removed; double-click behavior now toggles directory only.
- `frontend/src/components/Reader.tsx` — entire module simplified; removed `RegeneratePanel`, `QaView`, `QaErrorBoundary` imports + dispatch arms; cross-tree "查看规格" link removed; pinning logic + `pinContext` + `extractMarkdownItemBody` + all `postPromote`/`deletePromote` calls removed.
- `frontend/src/markdown/renderer.tsx` — `PinContext`, `PinButton`, `extractPinId`, custom `p` and `li` overrides for pin buttons removed; locked-block pre-render preserved.
- `frontend/src/components/RegeneratePanel.tsx` — DELETED.
- `frontend/src/components/ProjectPage.tsx` — DELETED.
- `frontend/src/components/StagePage.tsx` — DELETED.
- `frontend/src/components/QaView.tsx` — DELETED.
- `frontend/src/components/QaErrorBoundary.tsx` — DELETED.
- `frontend/src/lib/autonomousMode.ts` — DELETED (no regen panel).
- `frontend/src/lib/qaParser.ts` — DELETED (no QaView).
- `frontend/e2e/golden_path.spec.ts` — Specs/Context section assertions removed; "POST /api/regen-prompt" foreign-Origin test replaced with "PUT /api/file" foreign-Origin test; new `Spec routes return 404` assertion added confirming `specs/...` and `CLAUDE.md` are unreachable.
- `README.md` — overview rewritten as "focused viewer/editor"; spec-pipeline language removed; coexistence note now says "spec-pipeline operations live in spec_driven on port 8765"; sub_type detection note clarified as heuristic.

**Spec-pipeline artifacts that retain stale references** (not auto-patched per "smallest change that resolves the conflict" — surfaced here so future regens know):
- `interview/qa.md` — Regen-scope-UI category and Sidebar-organisation category are now obsolete; cross-tree-link probe is moot. Future stage-2 regen would re-derive these from the revised prompt and naturally drop them.
- `findings/dossier.md` + per-angle files — extensive references to specs/, regen prompts, sub_type-from-qa.md. Historical record; future stage-3 regen would re-derive.
- `final_specs/spec.md` — many FRs (FR-7 EXPOSED_TREE, FR-9 mutation surface, FR-22..FR-24 sub_type, FR-30..FR-39 regen + promote, FR-43..FR-46 sidebar, FR-65..FR-66 locked block, FR-70..FR-78 RegeneratePanel + cross-tree, FR-82..FR-85 tests) need surgical patches OR full stage-4 regen. Recommended: full stage-4 regen via spec_driven once user confirms follow-up 001 is final.
- `validation/strategy.md` + per-level files — security.md, e2e.md, accessibility_and_manual.md all reference dropped features. Recommended: full stage-5 regen via spec_driven once stage 4 is updated.

No conflicts found in: `findings/angle-spec-driven-parallel-audit.md` (read-only inventory), `validation/divergences.md` (does not exist for this project).

Backend test verification: 22/22 pytest pass after follow-up 001 patches.

## Follow-up 002 — 2026-05-05 13:05:48

Source: `user_input/follow_ups/002-20260505-130548-zero-claude-coupling.md`
Summary: zero-coupling cleanup. Backend must not read or reference `CLAUDE.md`, `.claude/`, or `specs/` even at internal-anchor level. Source code grep for those literals across `projects/ai_video_management/` returns nothing after this follow-up.

Auto-updated:

**user_input:**
- `revised_prompt.md` — header amended to compose from raw + 001 + 002; preface line rewritten to drop spec_driven cross-reference and assert anchor-on-`ai_videos/`.

**Generated outputs:**
- `backend/libs/repo_root.py` — `RepoRoot.find()` now walks up looking for an `ai_videos/` child directory; the parent of that match becomes the workspace root. `CLAUDE.md` + `.claude/` no longer referenced. New `ANCHOR_DIR_NAME` constant.
- `backend/libs/safe_resolve.py` — comment cleanup (no behavioral change).
- `backend/libs/exposed_tree.py` — docstring rewritten without follow-up / spec_driven reference.
- `backend/libs/tree_walker.py` — docstring rewritten.
- `backend/libs/sub_type_lookup.py` — module docstring rewritten without specs/ / qa.md narrative.
- `backend/libs/api.py` — module docstring trimmed; comment in PUT handler rephrased without "FR-28" / "spec_driven" terms.
- `backend/libs/api_security.py` — comment cleanup.
- `backend/libs/file_writer.py` — `MissingIfUnmodifiedSince` docstring + inline comment rephrased without "FR-15" / "spec_driven" references.
- `backend/tests/conftest.py` — `repo_root()` helper switched to `ai_videos/`-based anchor (matching `RepoRoot.find()`).
- `backend/tests/test_boot_smoke.py` — docstrings cleaned of "follow-up 001" / "Per follow-up" narrative.
- `backend/tests/test_sub_type_lookup.py` — module docstring rewritten.
- `backend/tests/test_tree_walker_consumer_walk.py` — docstrings cleaned; `test_no_specs_or_context_section_in_tree` renamed to `test_no_other_sections_in_tree`.
- `backend/tests/test_api_security_three_shapes.py` — module + per-test docstrings rewritten; "Port 8765 (spec_driven)" → "Any port other than 8766".
- `frontend/src/components/Reader.tsx` — docstring trimmed.
- `frontend/src/components/Home.tsx` — explanatory paragraph pointing users to "spec_driven webapp on port 8765" removed.
- `frontend/src/components/ShotPairView.tsx` — docstring trimmed; "FR-50" mention removed from inline error message.
- `frontend/src/components/ShotlistTableView.tsx` — docstring trimmed.
- `frontend/src/components/ImageRefView.tsx` — docstring trimmed.
- `frontend/src/styles.css` — "(FR-44)" / "(FR-65, FR-66)" comment annotations removed.
- `frontend/e2e/playwright.config.ts` — "(catches the spec_driven-006 Origin-rewrite regression)" softened to "(catches Origin-rewrite regressions)".
- `frontend/e2e/golden_path.spec.ts` — "Per follow-up 001" comments removed; the "Spec routes return 404" test rewritten as "Out-of-sandbox paths return 404" with non-specs probe paths (`node_modules/anything.md`, `../escape.md`, `random_top_level/file.md`).
- `frontend/test/shotPairing.test.ts` — `specs/ai_video/...` test paths replaced with paths that don't reference specs/.
- `README.md` — entire file rewritten removing all references to `specs/`, `spec_driven`, `CLAUDE.md`, `.claude/`, follow-up numbers. Architecture section now describes the `ai_videos/`-anchor strategy.

Backend test verification: 22/22 pytest pass.

Verification grep for `spec_driven|specs/|CLAUDE|.claude|FR-\d+|follow-up` across `projects/ai_video_management/` (case-insensitive): **zero matches**.

Note: The `specs/development/ai_video_management/` directory itself (this audit trail) continues to use those terms — it's the agent_team workflow's persistence surface, not webapp source. The webapp reads none of it.
