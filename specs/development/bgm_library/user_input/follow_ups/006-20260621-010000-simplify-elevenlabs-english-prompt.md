# Follow-up draft 006 — 2026-06-21

简化 BGM 流程：只出 prompt，外部用 ElevenLabs 出乐再导入；移除 Kling/MP4→MP3。

## 背景
用户不再用 Kling 出视频取音轨，改为到 ElevenLabs 自己生成背景音乐、下载、导入。只需要最优质的（英文）prompt。

## 变更
1. prompt 改为**单一英文版**（ElevenLabs 为英文训练）。移除中文 Kling prompt 段 + KLING_BGM_NOTE + 中文模板/形容词。sidecar 只保留一段：`## 生成提示词（英文 · 复制到 ElevenLabs）`。
2. 保留**首行 KEY（bgm_NNNN）** 便于下载后按文件名一键路由导入；本地回读喂模型前会 strip 掉这行。
3. mood / 配器 的中文下拉预设在生成 prompt 时**翻译成英文**（自定义自由文本原样保留），避免中英混杂、提升 ElevenLabs 质量。
4. **删除 MP4→MP3 全链路**：import_video / _extract_audio_to_mp3 / _ffmpeg_exe / _VIDEO_EXTENSIONS / POST import-video 路由 / BgmCommand.import_video / repository 协议 / 两个错误（BgmNoDownloadVideoError、BgmAudioExtractFailedError）/ UI「🎬 从视频提取(MP4→MP3)」按钮 + importBgmVideo。
5. 保留：本地 GPU 生成（可选）、导入下载音乐（import_audio，含 KEY 优先匹配）。

## 备注
- 既有 live sidecar 已迁移为单段英文 + key 格式。
- UI 文案仍中文；只有「复制到 ElevenLabs」的 prompt 正文是英文。
