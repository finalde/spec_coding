# Follow-up draft 009 — 2026-05-11

Summary: 把已有的 drama-row "🏷 重命名" 按钮升级为 "📥 导入 + 重命名" 一键流程 —— 后端扫描用户 OS 的 Downloads folder（过去 7 天 by mtime 的 image / video 文件），对每个文件按文件名 substring-match 该 drama 下 `characters/c*/` + `scenes/s*/` + `episodes/ep*/prompts/shot*/` folder 名，把文件 `shutil.move` 到匹配最长的子目录；无匹配文件丢进新建的 `ai_videos/{drama}/not_matched/`；移动完成后调用现有 `MediaRenamer.rename_drama()`（新增 `excluded_folder_names={"not_matched"}` 跳过未分类桶，保留原始文件名供用户人肉triage）。

## 用户原话

> lets add a new functionality to the ai_video_management, enrich the rename button, it should go to the chrome downloads folder, look at past week's all image and video format files, they are all related to ai videos, based on the file name, use your best guess to put it into either charactors foldre or scene folders or shot folders under ai_videos you think relavent, if not, create a not matched folder on ai video management, I will move it myself, after you move the file then apply rename same logic as before

## 决策 (interactive 收集，2026-05-11 19:56)

| 问 | 用户答 |
|---|---|
| 按钮设计 | Enrich existing button: 一次 click → import then rename。 |
| not_matched 目标 | `ai_videos/{drama}/not_matched/`（per-drama 桶，sandbox 内，sidebar 可见）。 |
| 分类器算法 | Substring match against this drama's 现有 folder 名，longest-match 胜；tie → shot > scene > character。 |
| 时间窗口 | 过去 7 天（by file mtime），与"past week"一致。 |

## 功能要求 (UI 层)

1. **按钮文案变化**: drama-row 上原 "🏷 重命名" → "📥 导入 + 重命名"；in-flight "导入并重命名中…"；title `按文件名分类导入 Downloads 内的近 7 天图片/视频到此 drama，并按 parent folder 重命名`。
2. **点击行为**: 单 API 调用 → 后端依次执行 import + rename → 返回合并 summary → toast 显示 `已导入 N / 未分类 M / 已重命名 K / 失败 E`。Tree refresh 触发让新导入文件立即出现在 sidebar。
3. **In-flight 防重复**: 同一 drama path 处于 in-flight 时再次点击 no-op（与 follow-up 007 的 `renamingPath` 同机制）。
4. **失败模式**: ApiError 类型直接展示 `detail.kind`；Downloads 目录不存在 → toast 显示 `downloads_dir_missing`，不抛白屏。

## 分类器算法 (后端)

输入：filename basename (不含 ext)，drama 下三类 candidate 子目录。
对每个 candidate folder：
- 用 folder basename 作 primary token；若 basename 含 `_`，每个下划线-split part (length ≥ 2) 也作 token。
- shot folder 额外加入 `{ep_name}_{shot_name}` 与 `{ep_name}` token，让 `kling_ep01_shot01_xxx.mp4` 之类的文件名也能命中。
- token 与 filename 均 `.lower()` 后比对；token 是 filename 的 substring 则该 candidate 得分为 max(matched token length)，否则不参与。

胜出选择：
- score 最高者胜。
- score = 0 → 文件丢进 `not_matched/`。
- score 相同 → 按类型优先级 shot > scene > character；类型相同 → folder basename 字典序最小者胜（稳定 tiebreaker）。

理由（why this scoring）：
- 字符串前缀如 `c1_` 与 `s7_` 短而通用，单独命中容易误判。把整个 `c1_沧冥` 作 primary token、`c1` / `沧冥` 作回退 token，可让 `kling_c1_沧冥_test.mp4` 命中长 token (length 5)，让 `kling_c1.mp4` 命中短 token (length 2)。两者都比 not_matched 好。
- 类型优先级 shot > scene > character 对应分类粒度：shot 文件名通常最 specific（含 epNN / shotNN），优先匹配以免被 character 名"沧冥"过早抢走。

## 后端 endpoint

- `POST /api/import-from-downloads`，body `{ "path": "ai_videos/{drama}" }`
  - 验证 path 形状（与 `rename-media` 一致：immediate child of `ai_videos/`，drama 存在，sandbox 内）。
  - 验证 Downloads 目录存在（`Path.home() / "Downloads"`，可被环境变量 `AI_VIDEO_MGMT_DOWNLOADS_DIR` 覆盖以便测试）。Downloads 不在则 500 `downloads_dir_missing`。
  - 扫描 Downloads **immediate children** (不下钻子目录) 为 media-ext + mtime ≥ now - 7×86400 + 非 symlink 的 candidate files。
  - 对每个 candidate file → 分类 → `shutil.move` 到目标 folder（目标 folder 不存在则 `mkdir`，跨 FS safe）。
  - 目标已存在同名 → 该文件加入 `errors[]` (kind=`target_exists`)，不覆盖、不重试。
  - 完成 move 后，调用 `MediaRenamer.rename_drama(path, excluded_folder_names={"not_matched"})`。
  - 返回 `{ moved: [{from, to, kind}], unmatched: [{from, to}], errors: [{path, message}], rename: <RenameResult.to_payload()> }`。`kind` ∈ `character|scene|shot`。`from` / `to` / `path` 均为字符串：`from` 是 Downloads 内绝对路径的 basename + 上层 marker（避免泄露完整 home 路径，但保留可调试性 → 用 `~/Downloads/<basename>` 形式渲染）；`to` 与 `path` 是仓库 root 相对路径。
  - HTTP 200 if drama 验证通过（部分 file-level 失败的细节在 body 内）；400 `invalid_drama_path`；404 `not_found`；405 method-not-allowed；500 `downloads_dir_missing`。

## 安全 / 边界 (新 sandbox 扩展)

- **新读路径**: Downloads 文件夹在 EXPOSED_TREE 之外。本 follow-up 的后端首次允许"从沙箱外读 + 移动 file 到沙箱内"。
  - 限制范围：只读 Downloads 目录的 immediate children；不下钻；不读子目录；不读其他非 Downloads 路径。
  - 文件名验证：basename 必须是合法文件系统名（`SafeResolver` 单段名校验：无 `..`、无 `/`、无 NUL、长度合理）。这一步阻止 Downloads 目录里万一有"逃逸名"的文件被 move 进 sandbox。
  - Symlink 拒绝：Downloads 内 symlink 跳过（不 follow，不 move）。
  - **不删除任何 Downloads 文件**：只 `shutil.move`（rename / cross-FS copy + unlink），文件原地从 Downloads 消失并出现在目标，这与"用户预期"一致；不另开 copy-only 模式。
- **写路径**: 目标 folder 在 EXPOSED_TREE 内（drama 内）。`mkdir` parents 限制在 drama 子目录；写权限继承 file_writer 现有模式。
- Origin/Host gate：与现有 `POST /api/rename-media` / `PUT /api/file` 一致。
- 不绑定 `If-Unmodified-Since`：move 是 file-level atomic，不存在并发编辑 race。

## 前端最小改动

- `api.ts`: 新增 `importFromDownloads(path)` POST helper + `ImportFromDownloadsResult` type，签名 `Promise<{moved, unmatched, errors, rename: RenameMediaResult}>`。`renameMedia` helper 保留（其他代码不调，但保留以兼容、便测试）。
- `Sidebar.tsx`: drama-row button onClick 改调 `importFromDownloads`；toast summary 改 `已导入 N / 未分类 M / 已重命名 K / 失败 E`；button label 改 "📥 导入 + 重命名"。
- `App.tsx` / `styles.css`: 无变更。

## 不在本 follow-up 范围

- 不引入 dry-run 预览模式（v1 直接 move；后续若需要单独 follow-up）。
- 不引入多选 / 单文件 import（只 batch import）。
- 不引入用户自选 Downloads 路径 UI；只通过环境变量 `AI_VIDEO_MGMT_DOWNLOADS_DIR` 覆盖。
- 不写 backend pytest（与 005/006/007/008 一致地推迟到批量补测）。
- 不写 e2e Playwright（同上）。
- 不改 `MediaRenamer` 默认 `excluded_folder_names`；只通过 import endpoint 显式传入 `{"not_matched"}`。其他 `/api/rename-media` 调用方行为不变。
