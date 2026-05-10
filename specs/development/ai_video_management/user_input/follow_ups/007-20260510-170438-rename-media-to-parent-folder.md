# Follow-up draft 007 — 2026-05-10
Summary: 在 ai_video_management webapp 加一个"按 parent folder 命名 media 文件"的功能 — 短剧级别的 button，一点扫整个当前短剧下所有 folder，把每个 folder 里的图片+视频文件 rename 成跟其所在 folder 同名（重复时附加数字 1/2/3）。

## 背景 / 用户场景
- 用户从 Seedance 下载 video 后放进 `ai_videos/{drama}/{characters|scenes|shots}/{asset}/` 文件夹，下载下来的原始文件名通常含时间戳/任务 ID/中英混排（例：`jimeng-2026-05-10-6390-柳红袖 · 红袖招老板娘 — 角色 reference 转身样片（turntab....mp4`、`kling_20260510_VIDEO_白月清___紫霄宫主_3014_0.mp4`），既不便引用也不便在文件管理器排序。
- 用户希望命名规则与现存惯例一致 —— 例如 `ai_videos/mozun_chongsheng/characters/c1_沧冥/` 下已有的 `c1_沧冥1.mp4`、`c1_沧冥2.mp4`，即"以所在 folder 的 name 为前缀，附加序号"。

## 功能要求 (UI 层)
1. **按钮位置**: 短剧（drama / project）级别 —— 即 `ai_videos/{drama}/` 这一层 tree 节点的 row 上（紧邻已有的 `subtype-badge` "短/剧" pill），文字 / icon 风格保持轻量（例如 `🏷 重命名` 或 `重命名媒体`），不破坏 sidebar 节奏。
2. **点击行为**: 触发后端扫描该短剧 folder 整棵树（递归），按规则 rename 所有 image / video 文件；操作完成后 refresh tree（用户能立即看到改名结果）；并在某个轻量位置 surface 结果摘要（已重命名 N 个 / 跳过 M 个 / 失败 K 个），失败时显示错误。
3. **范围限制**: 只 touch image + video 文件（与 `MEDIA_EXTENSIONS` 一致：`.png .jpg .jpeg .webp .gif .bmp .mp4 .mov .webm .mkv .avi .m4v`）。其他文件（`.md`、`.json` 等）原样不动。
4. **避免双击重复触发** / **避免在进行中再次点击**: button 在 in-flight 期间 disabled。

## 重命名规则 (后端)
- 对短剧目录递归遍历每个 folder（`_EXCLUDED_DIRS` 仍排除：`node_modules`、`.git`、`.audit`、`__pycache__`、`.pytest_cache`、`dist`、`build`、`.vite`）。
- 在每个 folder 内：
  - 收集 immediate children 的 image + video 文件（不下钻子文件夹的 media）。
  - 按扩展名分组（`.mp4` 归一组、`.png` 归另一组），每组独立处理：
    - 若该扩展只有 **1** 个文件：目标名 = `{folder_name}{ext}`（不带数字）。
    - 若该扩展有 **多个** 文件：按当前文件名 lexicographic 排序后，目标名依次为 `{folder_name}1{ext}`、`{folder_name}2{ext}`、…。
  - 若文件当前名 === 目标名 → 跳过（no-op）。
  - 若两个文件冲突（pass-1 中其中一个的目标名等于 pass-1 中另一个的源名），先把所有需 rename 的文件 rename 到临时唯一名（例如 `.__rename_tmp_{uuid}__{i}{ext}`），再 pass-2 rename 到最终目标名 —— 两阶段避免 collision。
- "Parent folder name" 取 file 的 immediate 父目录的 basename（与 `Path.parent.name` 一致），不做转义；目录名已是文件系统合法字符。
- Drama 自己（`ai_videos/{drama}/`）直接 children 中的 media 文件也按规则处理（parent = drama name）。

## 安全 / 边界
- 入参 `path` 必须 `safe_resolve` 后落在 `ai_videos/{drama}` 这一层（顶级一段必须是 `ai_videos`，且必须是其 immediate child directory，不能是 `ai_videos/` 本身、也不能是更深层的子目录 —— rename 是 drama-scoped 操作）。
- Origin/Host gate 与现有 `PUT /api/file` 一致（state-changing endpoint）。
- 无 If-Unmodified-Since 要求 —— 文件名修改本身就是 atomic per-file，且 batch rename 不需要 RFC 7232 配对。
- 拒绝 symlink；遇到任何 OSError 单独记录到 errors 列表，但不中断 batch。

## 后端 endpoint
- `POST /api/rename-media`，body `{ "path": "ai_videos/{drama}" }`，返回 `{ "renamed": [{from, to}, ...], "skipped": [path, ...], "errors": [{path, message}, ...] }`。HTTP code 200 if path valid（即使部分文件失败 —— 部分失败的细节在 body 内）；400 if path 形状不对；404 if path 不存在 / 不在 sandbox 内 / 不是 drama-level；405 for 非 POST。

## 前端最小改动
- `api.ts` 加 `renameMedia(path)` helper。
- `Sidebar.tsx` 在 drama 节点 row（depth=1 且 `project_meta` 非空）渲染一个 inline button —— 点击触发 `renameMedia` → 显示 in-flight spinner → 完成后调用现有 `refreshTree` 通道（`onSelect` 之外需 expose 一个 `onTreeReload` 回调），并在 console + a11y live region 报告结果。
- `App.tsx` 把 tree refresh 函数 thread 进 Sidebar；保持 light theme。
- 不引入任何新的 modal / popover library（用现有的 inline DOM）。

## 不在本 follow-up 范围
- 不增加 / 移除目录；不删除文件。
- 不处理子文件夹之间的 media 跨 folder 合并（每个 folder 独立处理）。
- 不为非 ai_videos 顶级（如 `research/`）开放 rename —— 只 drama 适用。
- 不做 dry-run 预览模式（v1 直接执行；后续若需要可加 `?dry_run=true`）。
- 不写 backend pytest（与 follow-up 005 / 006 一致地推迟到批量补测）。
