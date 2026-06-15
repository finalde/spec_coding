---
target_stage: 6
target_artifacts:
  - projects/ai_video_management/libs/infrastructure/writers/actor__writer.py
  - projects/ai_video_management/libs/infrastructure/writers/downloads__writer.py
  - projects/ai_video_management/apps/ui/src/components/ActorPoolGenerator.tsx
severity: medium
---

# Follow-up draft 124 — 2026-06-13
演员生成新增「只生成 prompt（默认）」模式：不调用 Kling，直接落地 actor 文件夹 + sidecar，用户自行 copy 到 Kling/Seedance 出图，下载后一键导入归位。

## 意图（抽象后）
演员池生成器当前只有「预览 prompt → 确认 → 9 路并发调 Kling 出图」一条路径。新增一个并设为**默认**的模式：

1. **只生成 prompt（prompt-only，默认）**：点「创建 prompt」即在 `ai_videos/_actors/actor_NNNN/` 下分配文件夹并写 sidecar `.md`，**不调用任何出图 API**。face / body 两条 prompt 各自以演员 id 前缀打头（如 `id0009f, …` / `id0009b, …`），这样用户把 prompt 粘到 Kling 或 Seedance 出图、下载下来的文件名会带上该 id，可据此回填到对应 actor 文件夹。一条 prompt 同时适用 Kling 与 Seedance（不另造 Seedance 专用 prompt）。
2. **一键导入**：提供按钮，扫描 OS Downloads（沿用 perf 库 `import_performances` 的 tag-路由机制），按文件名里的 `idNNNN[f|b]` tag 把下载图片归位成对应 actor 文件夹的 face / body 规范 jpg。无 tag / 无对应 actor 的文件进 `_not_matched/`。
3. 原「直接调 Kling」模式保留为非默认选项。

face + body 与现有生成器输出保持一致（face 主图 + body 全身参考）。

## 落地（stage-6 净增量）
- `actor__writer.py`：`ActorPool.create_prompts_batch(...)` —— 分配 id、构建 face/body prompt、按 `_actor_import_tag(id_num, is_body)` 给 prompt 打 `idNNNN[f|b]` 前缀、只写 sidecar（无 jpg、无 Kling 调用）。`_reap_incomplete_folders` 跳过含 sidecar `.md` 的文件夹（prompt-only 待导入 actor 不被回收）。`_build_sidecar` 加 `pending_import` 形参（body_image 行显示「待导入」+ 导入说明）。
- `downloads__writer.py`：`DownloadsImporter.import_actors()` —— 镜像 `import_performances`，按 `_ACTOR_IMPORT_TAG = re.compile(r"id(\d{4,})([fb])", re.IGNORECASE)` 路由，face→`_attrs_to_filename`、body→`_attrs_to_body_filename`，下载图统一 `_reencode_to_jpeg` 转 JPEG 落地（face/body jpg 凭文件名后缀被 `_find_actor_jpg`/`_find_actor_body_jpg` 发现，sidecar 不另记录文件名，故无回填步骤）。
- 应用层 / 路由：新增 `ActorCommand.create_prompts` + `POST /api/actors/create-prompts`；`ActorRepository` 协议补 `create_prompts_batch`。导入**复用现有** `POST /api/import-from-downloads` —— `DownloadsCommand.import_drama` 按 `drama_name == "_actors"` 分流到 `import_actors`（与 perf 库 `_performances` 分流同构），不新增路由。
- 前端：`api.ts` 加 `createActorPrompts()`（导入复用现有 `importFromDownloads`）；`ActorPoolGenerator.tsx` 加模式切换（prompt-only 默认）+ 创建后的 prompt 面板（每个 actor id + face/body 复制按钮）；`Sidebar.tsx` actors 根加「📥 导入演员」常驻按钮（复用 `onRenameClick` → `importFromDownloads("ai_videos/_actors")`）。

## 判断点
- 导入 tag 用 `idNNNN[f|b]`（ASCII，f=face / b=body）而非裸 `0009`：裸数字易与文件名里的时间戳等冲突（perf 库正是为此用 CJK `演NNNN` tag），加 `id` 前缀 + 显式 f/b marker 既保留用户要的「prompt 以 id 打头」语义，又避免误匹配且能区分 face/body。
