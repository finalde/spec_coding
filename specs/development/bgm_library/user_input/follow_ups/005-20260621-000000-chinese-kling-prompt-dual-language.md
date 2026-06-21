# Follow-up draft 005 — 2026-06-21

BGM 生成提示词改为双语，并新增 Kling「只取背景音乐」版本；UI 文案全中文。

## 背景
用户已购 Kling 年卡，想用 Kling 出视频后只取其中的背景音乐，不想再为音乐另买付费服务。本地 Stable Audio（English-trained T5）继续保留作为备选。

## 变更
1. 每条 BGM 的 sidecar 现写两段提示词：
   - **`## 生成提示词（中文 · Kling 出 BGM 用）`** — 纯中文乐曲描述 + 固定「用途说明」尾注，告诉 Kling：本提示词用于生成视频，但只取背景音乐，画面可纯黑屏/极简静止，重点放在音乐上。这是用户复制进 Kling 的主路径，也是 UI 详情页展示/复制的内容。
   - **`## 生成提示词（英文 · Stable Audio 本地模型用）`** — 英文，喂给本地 GPU 模型（`tools/stableaudio_gen.py`）。`_read_sidecar_generation` 按「英文」表头回读此段。
2. preview / create-prompts 的返回里 `prompt` = 中文 Kling 版，新增 `prompt_en` = 英文版。
3. BGM 相关 UI 文案残留英文词（prompt→提示词、mood→氛围、instruments→配器、notes→备注 等）全部改中文；保留 BGM/BPM/GPU 缩写。
4. 既有 6 条 sidecar 已迁移为双段格式（英文段与原文件 byte 一致，音频可复现不变）。

## 备注
- Stable Audio Open 1.0 的文本编码器以英文训练，故本地模型仍喂英文；用户已知该取舍。
- 中文段与英文段共享同一 seed 选中的 intensity 序号，两段对应。
