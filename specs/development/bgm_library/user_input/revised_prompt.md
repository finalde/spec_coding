# Raw prompt — bgm_library

在 ai video 里加一个新模块：背景音乐（BGM）。将来根据不同的剧和场景放背景音乐，需要一个 AI 自动生成背景音乐的库。

要求（对话澄清后）：

1. 库是**共享的**，独立的背景音乐库模块，在 UI 上也显示。
2. 按不同**类型**给背景音乐分类；每一类下有多个子目录，子目录里有 prompt 或 spec，也有 prompt 对应生成的背景音乐。
3. 每个背景音乐都有 **unique id**，方便不同剧本 reference —— 就像演员一样。
4. 生成后端：**MusicGen 自托管**（开源、零调用费、权重可商用）。
5. 推进方式：走 `/agent_team` 正式 spec 流程。

模板参照（现有演员库 `ai_videos/_actors/`）：
- 库：`ai_videos/_actors/actor_NNNN/actor_NNNN.md`（元数据表 + 生成 prompt），全局唯一 id。
- webapp DDD 切片：`actor__route / __query / __command / __writer / __chinese_prompt / __dto / __repository / __valueobject / __mapper`。
- `assignments` 机制：查「哪几部剧引用了这个 actor」。
- UI：演员网格 + `CastingView.tsx`。


---

# Follow-up draft 001 — 2026-06-16
BGM generation form: preset dropdowns + optional free-text override; and make generation failures diagnosable.

## 指令
- **生成表单的自由文本字段改为「dropdown 预设 + 可选自定义框」**：mood（氛围）和 instruments（配器）原来是纯 free-text input，改为先给一个常用值的 dropdown（首项「（不限）」= 空），旁边再留一个 optional 的 free-text box；自定义框非空时优先，留空则用 dropdown 选项。预设是纯前端便捷词表（后端仍接受任意 ≤200 字自由文本，无新增枚举）。notes（备注）保持纯 textarea。
- **生成失败信息要可诊断**：子进程失败时，错误展示取的是 stderr 的「前 300 字」——那只是 traceback 头部，把真正的异常（如 `ModuleNotFoundError: No module named 'torchaudio'`）藏在了末尾。改为取 stderr 的**最后一行非空内容**（traceback 的异常摘要行），用户一眼能看到根因。
- **生成依赖说明**：实际生成需要 `tools/stableaudio_gen.requirements.txt` 的重型依赖（torch / torchaudio / stable-audio-tools / einops）装在专用 venv，并通过 `BGM_PYTHON` 环境变量指向该解释器；webapp 自身进程不装 torch。当前失败根因即该解释器缺 torchaudio / stable-audio-tools。


---

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


---

# Follow-up draft 003 — 2026-06-17
本地 BGM 生成后端从 stable-audio-tools 换成 diffusers（Python 3.13 兼容）。

## 指令
- **生成后端改用 diffusers 的 `StableAudioPipeline`**，加载同一套 `stabilityai/stable-audio-open-1.0` 开源权重。根因：原 `stable-audio-tools` 硬 pin 了 2023 年的旧依赖（`pandas==2.0.2` 等），这些在 Python 3.12/3.13 上没有预编译轮子、需从源码编译且失败；diffusers 加载相同权重、在新 Python 上干净安装。权重/许可不变（Stability AI Community License，商用安全），只是换加载器。
- `tools/stableaudio_gen.py` 的 CLI 契约保持不变（`--prompt/--seed/--duration/--model/--out/--dry-run`，仍输出 mp3，仍走 ffmpeg loudnorm），所以 webapp 的 `bgm__writer.py` 与既有测试无需改动；`--dry-run` 仍不导入 torch。
- `tools/stableaudio_gen.requirements.txt` 改为 `diffusers/transformers/accelerate/sentencepiece/protobuf/soundfile`（去掉 stable-audio-tools/einops 显式项）；GPU torch 单独从 pytorch.org 的 cuXXX index 装。
- **运行前置（一次性）**：① 专用 venv 装 GPU torch + 本 requirements；② 设 `BGM_PYTHON` 指向该 venv 解释器（webapp 重启后生效）；③ 权重 gated——在 HF 接受许可并 `huggingface-cli login`（或设 HF_TOKEN）。


---

# Follow-up draft 004 — 2026-06-20
Episode 级 BGM 编排：按剧情稀疏 cue 时间线 + 像 casting 一样把库内 bgm 分配进占位 + 一键烧录进带字幕的整集视频。

## 指令
- **每集一条稀疏 BGM cue 时间线**：落 `episodes/epNN/bgm/bgm.md`（独立 `bgm/` 文件夹 + md）。不是每秒都有 BGM，只在强烈激情/武打/悲伤等特定剧情段才铺；其余留白。每条 cue = 时间窗(整集秒数) + 期望情绪(category) + vol/duck/fade + 剧情注释。cue 编排由 AI-video pipeline 人工读剧本产出，不在 webapp 自动生成。
- **像 assign actor 一样 assign BGM**：webapp episode BGM 面板里给每个 cue 占位 `-` 按情绪从库选 `bgm_NNNN` 填入（改写 bgm.md 该行 slot）。
- **一键烧录**：把已分配 cue 按时间窗烧进**带字幕整集视频** `ep{NN}_zh.mp4`（非原视频/非 renders）→ 输出 `ep{NN}_zh_bgm.mp4`，**二次烧录覆盖**；源 `ep{NN}_zh.mp4` 保留作干净重烧源，`renders/` 原视频不动。
- duck=on 的 cue 在台词处用整集自身音轨 sidechain 让路；未分配 cue 跳过并在结果里报。
