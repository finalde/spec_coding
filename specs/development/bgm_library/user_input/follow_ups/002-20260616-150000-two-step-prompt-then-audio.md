# Follow-up draft 002 — 2026-06-16
BGM 改为两步流程：先生成 prompt，再按条出音频（本地 GPU 或导入外部下载）。

## 指令
- **解耦 prompt 生成与音频渲染**。原来「生成 BGM」一步既分配 bgm_NNNN/ 又同步跑 Stable Audio 出 mp3。改为两步：
  - **步骤 1（批量，很快）**：UI「生成 BGM prompt」只分配 track 文件夹 + 写 sidecar（含解析好的 Stable Audio prompt / seed / duration），**不渲染音频**。结果条目带 `pending_audio` 标记、`audio_path: null`。
  - **步骤 2（按条）**：进入某条 BGM 详情页，二选一：
    - **本地 GPU 生成**：读回 sidecar 的 prompt/seed/duration，本地 Stable Audio 子进程渲染该条 mp3。
    - **导入下载音乐**：把 prompt 复制到外部平台出音乐、下载后，按 button 把 Downloads 里**最新的音频文件**（mp3/wav/m4a/flac/ogg，7 天窗口内）移动进该 track 作为 bgm_NNNN.mp3（覆盖旧渲染）。
- **reaper 语义修正**：原 reaper 删除所有「无 mp3 且超阈值」的 track 文件夹，会误删「prompt-only 待出音频」的 track。改为只回收**既无 sidecar 又无 mp3** 的空文件夹（崩溃残留）；有 sidecar 的 prompt-only track 永远保留。
- **生成失败信息**：见 follow-up 001（取 stderr 末行）。本地 GPU 生成依赖专用 venv + BGM_PYTHON（torch/torchaudio/stable-audio-tools）；导入外部下载这条路径**不需要 torch**，可立即使用。
