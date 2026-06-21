# Follow-up draft 132 — 2026-06-21
在 webapp 加「一键生成末帧图片」按钮，配合新的「跨镜首帧承接」流程（承接镜的首帧＝上一镜成片末帧）。

---
target_stage: 6
target_artifacts:
  - libs/infrastructure/writers/frame__writer.py
  - apps/api/routes/frame__route.py
  - apps/ui/src/components/SiblingMedia.tsx
severity: low
---

## 背景
ai_video 流程新增「跨镜首帧承接」机制（见 `.claude/agent_refs/project/ai_video.md` 2026-06-21 amendment + `ai_videos__运镜` M8 / `ai_videos__格式契约` K26）：视觉连续的相邻镜，**下一镜（承接镜）的首帧 = 上一镜成片的实际末帧**（截帧上传，不另生成静帧）。webapp 需要把"截上一镜末帧"做成一键操作。

## 指令
给每个 **shot 渲染视频** tile 加一个按钮「⏮ 生成末帧」——一键截取该镜成片的**最后一帧**成 PNG，落 shot 根目录 `shot{NN}_lastframe.png`，供下一个承接镜作首帧参考图上传。二次点击覆盖。

## 实现（复用 frame 聚合 + burn-intro-cards 那套 ffmpeg/路径模式）
- 后端 `FrameExtractor.extract_last_frame(rel)`：`-sseof -3` 只解码尾段 + `-update 1` 让 PNG 留最后一帧；输出落最近 `shotNN` 祖先根（复用 `_shot_folder`）。复用 `_validate_video_source` + 既有 frame 错误类（`FfmpegMissingError`/`FrameExtractFailedError`/`NotVideoError`/`VideoNotFoundError`，已注册 handler，无需新增）。
- 应用层 `FrameCommand.extract_last_frame` + DTO `ExtractLastFrameResultCdto`（`{src,out}`）+ `FrameMapper.last_frame_to_cdto`。
- 路由 `POST /api/extract-last-frame`（加进既有 `frame__route` router，复用 `ExtractFramesBody`）。container 无需改（`frame_command` 已 wired）。
- 前端 `extractLastFrame(path)` api + `SiblingMedia.tsx`：state/handler/prop 镜像 `extractFrames`，按钮 gated `isShotVideoPath`，放 shot-video 按钮组首位。
- 测试 `tests/test_frame_last_frame.py`（5 例：`_shot_folder` 分支 + 真 ffmpeg 截帧落 shot 根 + 校验错误路径）。
- 校验：pytest 26 绿（boot smoke + scene_plate + intro_card + 本测试）；apps/ui `tsc -b` 干净。
