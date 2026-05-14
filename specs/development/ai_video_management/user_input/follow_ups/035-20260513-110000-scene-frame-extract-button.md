# Follow-up draft 035 — 2026-05-13

Summary: 新增 "🎞 Extract Frames" 按钮于 SiblingMedia 的每个 .mp4 tile（非 archived 视频），点击后调用新的 `POST /api/extract-frames` 端点，对 source mp4 用 imageio-ffmpeg 抽取 5 个 canonical 参考帧（t=0.5/4.4/7.9/11.4/14.6s，对齐 `agent_refs/project/ai_video.md` rule #12.10 v3 的 hero/reverse/vert/mid/detail 抽帧建议时间点），输出 PNG 至与 mp4 同 folder（命名 `{stem}_f{N}_{role}.png`）。下游 shot 视频生成时可直接将这 5 张 PNG 作为场景 reference image 上传给 Kling/Seedance。

## 用户原话

> now I can generate a 15s scene video we disucssed about about the scene, now lets add a new button for the scene, when click, you take pictures from those scene, where the pictures will be used as a reference about the scene to generate shot videos

## 决策

- **抽帧时间点 = rule #12.10 v3 的 5 个 canonical 抽帧建议**：t=0.5 (hero) / 4.4 (reverse) / 7.9 (vert) / 11.4 (mid) / 14.6 (detail) — 与 scene reference video prompt 的 walk-through 5 dwell 对齐。每帧输出独立 PNG，命名 `{video_stem}_f{N}_{role}.png` 便于和 source mp4 配对。
- **按钮位置 = SiblingMedia 的每个 .mp4 tile**：与现有 Archive 按钮并列，仅在视频文件 + 非 archived 状态显示。匹配现有 per-tile 操作模式，无需引入 scene-level 概念（任何视频都可抽帧，包括非场景 reference）。
- **ffmpeg 来源 = imageio-ffmpeg pip 包**：自带 ffmpeg-win-x86_64-v7.1.exe binary，无需 user 系统级安装。已在 user 环境实测可用。新增 `imageio-ffmpeg>=0.5` 到 `requirements.txt`。
- **错误处理**：(a) 非视频扩展名 → 400 `not_a_video`；(b) 文件不存在 → 404 `not_found`；(c) ffmpeg 不可用 → 500 `ffmpeg_missing`；(d) 所有 5 帧都失败 → 500 `extract_failed`；(e) 部分帧失败（如 mp4 < 15s 在 seek-past-end 仍然返回最后一帧不算失败；ffmpeg 真返回非 0 才算）→ 200 返回 + `failures` 字段列出失败的 timestamp/role/error。
- **幂等性**：ffmpeg `-y` 覆盖输出。再次点击按钮直接覆盖 PNG，不报错。
- **PNG drops in same folder** → SiblingMedia 的 useEffect 已经在 onChange 后自动 refresh tree，5 张 PNG 立即出现在同一 SiblingMedia 视图中作为新 tiles。

## 工作流变更

**Before**：场景 reference video 渲染后，user 想把单帧作为 shot 视频生成的图像 reference 需要：(a) 下载 mp4 到本地；(b) 用本地 ffmpeg/QuickTime/PotPlayer 截图；(c) 上传回到 ai_video_management 项目目录；(d) 重新刷新 webapp tree。

**After**：在 webapp SiblingMedia 视图中点击 .mp4 tile 上的 "🎞 Extract Frames" 按钮 → 后端 ffmpeg 直接抽取 5 帧 PNG 落到同 folder → tree 自动 refresh → 5 张 PNG 立即可见可下载可作为 shot prompt 的 reference image 上传给 Kling / Seedance。

## Why now

User 在 mozun_chongsheng 项目已经按 rule #12.10 v3 (15s walk-through) 生成了第一个场景 reference video（s1_长阶顶3.mp4，实测 15.07s）。Walk-through 视频的 5 个 canonical dwell 视角（hero / reverse / vert / mid / detail）正是 shot 视频生成时需要的 background reference image 来源。Manual 抽帧工作流摩擦大；让 webapp 一键完成是自然的下一步。本 button 是 rule #12.10 v3 抽帧建议时间点的 webapp implementation。

## 影响范围

- `projects/ai_video_management/backend/libs/frame_extractor.py` — 新建。`FrameExtractor` class mirror `MediaArchiver` 风格；`CANONICAL_FRAMES` 常量列 5 个 (timestamp, role) 元组；`VIDEO_EXTENSIONS` frozenset；`InvalidPath` / `NotFound` / `NotVideo` / `FfmpegMissing` / `ExtractFailed` 异常；`FrameResult` 与 `ExtractResult` 不可变 dataclass。
- `projects/ai_video_management/backend/libs/api.py` — (a) docstring 端点计数 16 → 17；(b) 新增 `ExtractFramesBody` Pydantic model；(c) import `frame_extractor` 各 symbol；(d) 在 `create_app` 内实例化 `FrameExtractor`；(e) 新增 `@app.post("/api/extract-frames")` handler + `@app.api_route(..., methods=[GET/PUT/PATCH/DELETE])` 405 兜底。
- `projects/ai_video_management/backend/requirements.txt` — 新增 `imageio-ffmpeg>=0.5`。
- `projects/ai_video_management/frontend/src/api.ts` — 新增 `ExtractedFrame` / `ExtractFramesResult` interface + `extractFrames(path)` 函数。
- `projects/ai_video_management/frontend/src/components/SiblingMedia.tsx` — (a) import `extractFrames`；(b) `MediaTile` props 增加 `extracting` + `onExtractFrames`；(c) tile 内增加 `.sibling-media-actions` 容器包裹两个按钮；(d) 仅在 `isVideo && !archived` 显示 "🎞 Extract Frames" 按钮；(e) SiblingMedia 增加 `extractingPath` state + `handleExtractFrames` async handler，使用现有 `announce` aria-live 反馈；(f) 两处 `<MediaTile>` 实例传入新 props。
- `projects/ai_video_management/frontend/src/styles.css` — `.sibling-media-archive-btn` 选择器扩展到 `.sibling-media-extract-btn`（共享样式）；新增 `.sibling-media-actions` 容器样式（flex column gap 4px，stretch 子元素）。

## 不影响

- 其余端点 / lib 模块 / 组件不变。
- Backend 安全模型不变 — `FrameExtractor` 复用 `ExposedTree.is_inside` + `SafeResolver.resolve` + 拒绝 symlink。
- 现有 archive / unarchive / delete 按钮行为不变。
- 蒙太奇黑底特殊变体（s9_识海）— 抽帧逻辑通用，对黑底视频也能抽出 5 个相同的黑帧 PNG（user 不必对 s9 点抽帧按钮，但点了也不报错）。

## 实测验证

`s1_长阶顶3.mp4`（15.07s 已渲染 reference）抽帧成功：5 帧均生成 ~1.2-1.3 MB PNG，MD5 各不相同（确认非 duplicate）。失败 0 项。
