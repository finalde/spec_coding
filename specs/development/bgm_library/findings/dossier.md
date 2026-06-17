# Findings dossier — bgm_library

Run: bgm_library-20260616-123238

## Angles researched
1. musicgen-selfhost — 怎么自托管 MusicGen，让 `tools/musicgen_gen.py` 按 (prompt, seed, duration) 确定性产 1 条 mp3。
2. ffmpeg-duck-mux — 视频流 copy + 台词 MP3 + BGM sidechain duck 的可用 ffmpeg 方案与 `mux_av.py` 参数面。
3. actor-slice-mirror — actor DDD 切片逐文件蓝图，BGM 要 1:1 复刻什么。
4. bgm-metadata-cue — 固定情绪分类枚举 + 单曲元数据 schema + 每集 `bgm.md` cue 时间线格式。

## Cross-cutting insights
- **BGM 生成在 webapp 里走「子进程 + 离线模型」、与 actor 的「HTTP 调 Kling」是唯一架构差异，其余切片可逐文件镜像。** `bgm__command.generate` 用 `subprocess.run(tools/musicgen_gen.py …)` 替换 actor 的 Kling HTTP 块写出 `bgm_NNNN.mp3`；id 分配、.md 元数据表读写、reaper、软删除到 `_deleted/` 全部照搬。 *(musicgen-selfhost + actor-slice-mirror)*
- **mp3 播放/服务端零新增。** 现有 `/api/media` + `MEDIA_EXTENSIONS` 已服务 `.mp3`（`audio/mpeg`），UI 复用 `mediaUrl()` + `<audio>`（VoiceGrid 既有模式），BgmGrid 镜像 ActorGrid。 *(actor-slice-mirror)*
- **cue 行格式同时满足三方消费者：** `grep -o 'bgm_[0-9]\{4\}'` 供 assignments 反查、行式 parse 供 `mux_av.py`、终端可读供作者。统一管道分隔：`起-止(秒) bgm_NNNN | vol= | duck= | fade=`，仿 `subtitles.md` 的极简。 *(bgm-metadata-cue + actor-slice-mirror + ffmpeg-duck-mux)*
- **duck 由台词 MP3 作 sidechain key 驱动 BGM**，cue 的 `duck=on/off` 直接映射到 `mux_av.py` 是否对该段启用 `sidechaincompress`；`fade=`→`afade`；`loopable`→`-stream_loop`+trim。cue 语义与 mux filtergraph 一一对应。 *(ffmpeg-duck-mux + bgm-metadata-cue)*

## Per-angle highlights

### musicgen-selfhost
- `pip install audiocraft`（钉 Python 3.9 + torch 2.1.0 + ffmpeg）；默认 `musicgen-small`（~4GB VRAM，唯一 CPU 可忍受的尺寸；30s 片段 CPU 数分钟 / 中端 GPU 数十秒）。
- **30s 是单次硬上限**；更长/可循环用 continuation（`extend_stride`）。输出 32kHz，`audio_write(strategy="loudness")` 后 ffmpeg→mp3。
- prompt 设计：genre+instrumentation+mood+BPM 叠加（如 "tense cinematic confrontation, low strings + timpani, staccato, 90 bpm, instrumental"），与固定情绪枚举一一映射成默认模板。MusicGen 本就无人声，契合 BGM。
- ⚠️ **许可证（与 revised_prompt 假设冲突）**：AudioCraft 代码 MIT，但 **MusicGen 权重 CC-BY-NC 4.0 = 非商用**；未找到权重的商用授权。元数据 `license` 默认应记 `CC-BY-NC-4.0`。
- ⚠️ **确定性弱**：`set_generation_params` 无 seed 参；靠 `torch.manual_seed(seed)`，但 issue #111 报告固定 seed 仅复现前 ~2–3 秒 → 存 seed 是 best-effort，不是 actor 库那种硬复现。

### ffmpeg-duck-mux
- 一遍 `sidechaincompress`，输入顺序 `[bgm][dialogue]`（BGM 在前=被压信号，台词在后=sidechain key），反了是经典错误。推荐 CLI 暴露默认 `threshold=0.03 ratio=8 attack=40 release=400`。
- 纯 ffmpeg 足够，无需 pydub：`aloop`/`-stream_loop` 循环、`afade` 淡入淡出、`apad` 补静音、`amix=normalize=0`（关键，否则台词被悄悄减半）、`-c:v copy -c:a aac`。Python 只需 `ffprobe` 取时长 + 拼 filtergraph 串。
- 交付了完整 `mux_av.py` CLI 签名：`--video/--dialogue/--bgm/--out` + `--bgm-volume --duck-threshold/ratio/attack/release --bgm-start --fade-in/out --audio-bitrate`，含缺台词/缺 BGM 的行为矩阵。

### actor-slice-mirror
- BGM 需平行文件集：`value_objects/bgm__valueobject.py`（`BgmAttrs` + enums + `validate_bgm_id ^bgm_\d{4,}$`）、`errors/bgm__error.py`、`repositories/bgm__repository.py`、`writers/bgm__writer.py`（`BgmPool`）、`dtos`/`mappers`/`queries`/`commands`、`routes/bgm__route.py` + `routes/__init__.py` 注册、`app_factory.py` 错误行+eager-mkdir、`container.py` 的 `bgm_pool`/`bgm_command`/`bgm_query` 接线。
- 磁盘镜像 actor：`ai_videos/_bgm/bgm_NNNN/{bgm_NNNN.mp3, bgm_NNNN.md}`，同样 `mkdir(exist_ok=False)` 原子 id 分配、markdown 表 build/parse、reaper、软删到 `_deleted/_bgm/`。
- 两处与 actor 分歧：① `generate` 走 `subprocess.run(tools/musicgen_gen.py)`，新增 `Musicgen{Failed,Missing}Error`；② 反查扫 `ai_videos/<drama>/episodes/ep*/bgm.md` 里的 `bgm_NNNN` token（不是 casting.md），扫描器放 `BgmPool`/`BgmReferenceReader`，形状仿 `Casting.find_assignments_for_actor`/`assigned_actor_ids`（遍历剧目、跳过 `_` 开头目录、parse）。
- 建议**省略** actor 的 `generate-diverse`/archetype；`create-prompts`（仅 prompt 离线导入）流程对 BGM 可保留为可选。

### bgm-metadata-cue
- 固定 12 类情绪枚举（folder 兼 filter 字段）：`tension/combat/climax_hype/faceslap/tragic/warm/romance_pain/suspense/daily/flashback/theme_open/system_cue`，源自短剧按 beat 选曲实践（2026 BGM 指南 + 爱给网情绪分桶库）；`system_cue` 标注为本仓自定/practitioner-opinion。
- 元数据表镜像 `actor_0001.md`：`category / mood / bpm / duration / loopable / intensity(1-5 int) / instruments / generator / model / seed / license / notes (+可选 tags)`。
- cue 行：`起-止(秒) bgm_NNNN | vol= | duck=on/off | fade=in/out`，pipe 分隔、行式、可 grep。
- 实务 LUFS：人声 -14、duck 后垫底 -30…-35、纯音乐 -16，建议终端 `loudnorm`。

## Recommendations for the spec
1. **逐文件镜像 actor 切片**，仅在 `bgm__command.generate` 用 subprocess 调 `tools/musicgen_gen.py`、`bgm__repository` 反查扫 `bgm.md` 两点分歧。省略 generate-diverse/archetype。
2. **`tools/musicgen_gen.py` 与 `tools/mux_av.py` 是两个独立交付**，CLI 契约按 angle-1 / angle-2 的签名定稿；各带独立 `requirements.txt`（torch/audiocraft 不进 webapp 主依赖）。
3. **库结构**：`ai_videos/_bgm/{category}/bgm_NNNN/`（按用户要求 category 作目录层）+ `bgm_NNNN.md`（12 字段元数据表 + 生成 prompt）+ `bgm_NNNN.mp3`；id 全局唯一跨 category。**注意**：actor 库是扁平 `_actors/actor_NNNN/`，而 BGM 用户明确要 `{category}/` 分层——这是与 actor 的一处结构差异，id 分配需跨 category 扫描全局最大号。
4. **cue/`bgm.md`**：novel 每集 `episodes/epNN/bgm.md`，short 项目根 `bgm.md`；格式 `起-止(秒) bgm_NNNN | vol= | duck= | fade=`。
5. **生成 prompt 模板**：每个情绪枚举一个默认 MusicGen prompt 模板，带 bpm/intensity/instruments 槽。
6. **mux**：`mux_av.py` 纯 ffmpeg，`[bgm][dialogue]` sidechaincompress + amix(normalize=0) + `-c:v copy`，参数 CLI 暴露。
7. **元数据 `license` 默认 `CC-BY-NC-4.0`**，并在 README/规则注明 MusicGen 权重非商用限制。

## Post-research decisions (user, 2026-06-16)

调研后向用户回澄清，结论覆盖了 revised_prompt 的「MusicGen 自托管」选择：

- **生成后端从 MusicGen 换成 Stable Audio（开源权重自托管）。** 原因：MusicGen 权重 CC-BY-NC 非商用，用户要商用安全。Stable Audio Open / 3.0 开源权重档为 **Stability AI Community License — 年收入 < 100 万美元免费商用**（含分发与变现输出），权重在 HuggingFace，可本地 GPU 自托管。来源：stability.ai/license、HF stable-audio-open-1.0。
  - 推理用官方 `Stability-AI/stable-audio-tools`（`get_pretrained_model` + `generate_diffusion_cond`，torch 2.0+，GPU），支持 prompt / `seconds_total` / seed。
  - 工具改名 **`tools/stableaudio_gen.py`**（取代 `musicgen_gen.py`），CLI 契约不变：`--prompt --seed --duration --model --out [--dry-run]`，独立 `requirements.txt`，subprocess 调用，torch 不进 webapp。
  - 元数据 `generator=stable_audio`、`model=stable-audio-open-1.0`（或 3.0 档）、`license=Stability AI Community License`。架构其余（id 分配/.md 表/UI/assignments/mux）全部不变。
- **运行宿主：本机有 GPU** → 默认 model 用 Stable Audio Open（GPU，30s 片段数秒~数十秒）；`--model` 仍做 CLI 参数。
- **`tools/mux_av.py` v1 = 单 BGM 合成**（一个视频 + 一条台词 MP3 + 一条 BGM，duck/fade/loop）；多 cue 整条 `bgm.md` 编排留后续。
- **seed best-effort**（接受，spec/README 注明）。

## Open questions surviving research
- **【需用户决策】MusicGen 权重 CC-BY-NC 4.0 非商用** — 若成片要商用发布（红果/抖音/YouTube 变现），权重授权是冲突点。选项：接受（仅自用/演示）、换商用安全后端（Stable Audio / 自训）、或留作占位。 *(musicgen-selfhost)*
- **运行宿主 CPU vs GPU** — 决定默认 model 尺寸与生成时长预期；本机有无 GPU？ *(musicgen-selfhost)*
- **seed 仅 best-effort 复现** — 是否接受（actor 库 seed 是硬复现，BGM 做不到）。 *(musicgen-selfhost)*
- **`mux_av.py` v1 是单 BGM 单次合成，还是消费整条 `bgm.md` 多 cue 拼接？** 建议 v1 单 BGM + 后续加多 cue 编排。 *(ffmpeg-duck-mux + bgm-metadata-cue)*
- **`system_cue` 归 BGM 还是 SFX**；cue 重叠策略；vol 用 dB 还是 0-1 线性。 *(bgm-metadata-cue)*
- **是否保留 `create-prompts` 离线导入流程**（仅 prompt 不生成，供离线跑模型后回填）。 *(actor-slice-mirror)*
