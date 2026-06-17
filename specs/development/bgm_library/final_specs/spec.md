# Spec — bgm_library

Run: bgm_library-20260616-123238
task_type: development · target: `projects/ai_video_management/`
Compiled from: revised_prompt.md + interview/qa.md + findings/dossier.md (含 2026-06-16 后续决议)

## 1. 目标与范围

在 `ai_video_management` webapp 中新增一个**共享的「背景音乐库」（BGM library）模块**，整体逐文件镜像现有演员库（`actor__*` 切片 + `ai_videos/_actors/`），实现：AI 自动生成（Stable Audio 自托管）、固定情绪分类管理、UI 网格浏览/试听/生成、跨剧本按全局唯一 id 引用、assignments 反查、以及成片合成工具 `tools/mux_av.py`。

**本期交付边界（v1）：**
- ✅ 共享 BGM 库落盘结构 `ai_videos/_bgm/{category}/bgm_NNNN/`
- ✅ webapp `bgm__*` DDD 切片（含 UI 生成入口）
- ✅ BGM 库 UI 视图（网格 + 试听 + 分类 filter + assignments 反查）
- ✅ `tools/stableaudio_gen.py`（独立子进程生成脚本）
- ✅ `tools/mux_av.py` **v1 = 单 BGM 合成**（一个视频 + 一条台词 MP3 + 一条 BGM）
- ✅ 剧本侧 `bgm.md` cue 时间线格式 + `.claude/agent_refs/project/ai_video.md` 规则增补
- ❌ **不含**：generate-diverse / archetype（actor 有，BGM 省略）；多 cue 整条 `bgm.md` 自动编排（留后续）

## 2. 后端选型（已定，覆盖 revised_prompt 的 MusicGen）

- **生成后端 = Stable Audio（开源权重自托管）**。MusicGen 权重 CC-BY-NC 非商用，与「商用安全」冲突，已弃用。
- **许可证**：Stable Audio Open / 3.0 开源权重档 = **Stability AI Community License**（年收入 < 100 万美元免费商用，含分发与变现输出）。来源：stability.ai/license、HF `stabilityai/stable-audio-open-1.0`。
- **推理**：官方 `Stability-AI/stable-audio-tools`，`get_pretrained_model` + `generate_diffusion_cond`，torch 2.0+，**本机 GPU**。支持 `prompt` / `seconds_total` / `seed`。
- **元数据落值**：`generator=stable_audio`、`model=stable-audio-open-1.0`、`license=Stability AI Community License`。
- **seed = best-effort 复现**（不像 actor 的硬复现），spec/README 注明。

## 3. 库落盘结构 `ai_videos/_bgm/`

```
ai_videos/_bgm/
  {category}/                      # 12 类情绪枚举之一，既是目录层也是元数据字段
    bgm_0001/                      # 全局唯一 id，跨 category 唯一
      bgm_0001.md                  # 元数据表 + 生成 prompt
      bgm_0001.mp3                 # 生成产物
  _deleted/_bgm/                   # 软删除目标（镜像 actor 的软删）
```

- **id 分配**：全局唯一 `bgm_NNNN`（`^bgm_\d{4,}$`），跨 category。**与 actor 的关键结构差异**：actor 库扁平 `_actors/actor_NNNN/`，BGM 多一层 `{category}/`，故 id 分配需**跨 category 扫描全局最大号 +1**，仍用 `mkdir(exist_ok=False)` 原子占位。
- **category 枚举（12 类，folder 兼 filter 字段）**：
  `tension`（紧张对峙）/ `combat`（打斗）/ `climax_hype`（高燃爽点）/ `faceslap`（打脸爽感）/ `tragic`（悲情）/ `warm`（温情）/ `romance_pain`（虐恋）/ `suspense`（悬疑）/ `daily`（日常）/ `flashback`（回忆）/ `theme_open`（片头主题）/ `system_cue`（系统提示音；标注为本仓自定）。
- **`bgm_NNNN.md` 元数据表**（镜像 `actor_0001.md` 格式）字段：
  `category / mood / bpm / duration / loopable / intensity(1-5 int) / instruments / generator / model / seed / license / notes`（+可选 `tags`）；表后接 `## 生成 prompt` 块（英文 Stable Audio prompt）。

## 4. webapp DDD 切片（逐文件镜像 actor）

target: `projects/ai_video_management/`。每个 actor 文件对应一个 bgm 文件，**层级与命名 1:1**：

| 层 | actor 文件 | 新增 bgm 文件 |
|---|---|---|
| domain/value_objects | `actor__valueobject.py` | `bgm__valueobject.py`（`BgmAttrs` frozen dataclass + category/loopable enums + `validate_bgm_id`） |
| domain/errors | `actor__error.py` | `bgm__error.py` |
| domain/repositories | `actor__repository.py` | `bgm__repository.py`（protocol） |
| infrastructure/errors | `actor__error.py` | `bgm__error.py`（含新增 `StableAudioFailedError` / `StableAudioMissingError`） |
| infrastructure/writers | `actor__writer.py` | `bgm__writer.py`（`BgmPool`：id 分配 / md build·parse / reaper / 软删） |
| infrastructure/writers | `actor__chinese_prompt.py` | `bgm__prompt.py`（每情绪枚举一个默认 Stable Audio prompt 模板，带 bpm/intensity/instruments 槽） |
| application/dtos | `actor__dto.py` | `bgm__dto.py`（Qdto + Cdto） |
| application/mappers | `actor__mapper.py` | `bgm__mapper.py` |
| application/queries | `actor__query.py` | `bgm__query.py`（list / get / filter-by-category / assignments 反查） |
| application/commands | `actor__command.py` | `bgm__command.py`（`generate` / `delete`） |
| apps/api/routes | `actor__route.py` | `bgm__route.py`（自己的 `APIRouter()`） |
| apps/api/routes | `__init__.py` | 注册 `bgm` router |
| apps/api | `app_factory.py` | 加 bgm 错误行 + eager-mkdir `_bgm/` |
| apps/api | `container.py` | 接线 `bgm_pool` / `bgm_command` / `bgm_query` |

**两处与 actor 的唯一分歧（其余照搬）：**
1. **`bgm__command.generate`** 用 `subprocess.run([...tools/stableaudio_gen.py...])` 替换 actor 的 Kling HTTP 块，写出 `bgm_NNNN.mp3`；torch/重依赖隔离在脚本端，webapp 进程不背。失败映射 `StableAudioFailedError` / `StableAudioMissingError`。
2. **assignments 反查**扫 `ai_videos/<drama>/episodes/ep*/bgm.md`（及 short 根 `bgm.md`）里的 `bgm_NNNN` token（不是 `casting.md`）。扫描器放 `BgmPool` / `BgmReferenceReader`，形状仿 `Casting.find_assignments_for_actor`（遍历剧目、跳过 `_` 开头目录、parse）。

**省略**：actor 的 `generate-diverse` / archetype。`create-prompts`（仅写 prompt 不生成、供离线回填）可选保留。

## 5. UI：BGM 库视图

- **零服务端新增播放**：现有 `/api/media` + `MEDIA_EXTENSIONS` 已服务 `.mp3`（`audio/mpeg`）。
- `BgmGrid` 镜像 `ActorGrid`：网格卡片 + `<audio>` 试听（复用 `mediaUrl()`，模式同 `VoiceGrid`）+ **分类 filter**（12 枚举）+ assignments「哪些剧引用了此 BGM」。
- **生成入口**（仿 actor）：preview prompt + generate 按钮，表单填 category / duration / bpm / intensity / instruments，POST 触发 `bgm__command.generate`。
- DDD 分层不适用于 UI 代码（标准 React）。

## 6. `tools/stableaudio_gen.py`（独立子进程脚本）

- **CLI 契约**：`--prompt --seed --duration --model --out [--dry-run]`。
- 推理 `get_pretrained_model` + `generate_diffusion_cond`，输出经 ffmpeg → mp3（`loudnorm` 纯音乐 -16 LUFS 建议）。
- **独立 `requirements.txt`**（torch / stable-audio-tools），**不进** webapp 主依赖。
- `--dry-run` 仅打印将执行的 prompt/参数，供 webapp 校验路径。
- seed best-effort（注明）。

## 7. `tools/mux_av.py` v1（单 BGM 合成）

- 纯 ffmpeg，无 pydub。视频流 `-c:v copy`（不重编码）+ 台词 MP3 + 一条 BGM。
- **filtergraph 核心**：`[bgm][dialogue]` 顺序 `sidechaincompress`（BGM 被压、台词作 sidechain key——顺序反了是经典错误）+ `amix=normalize=0`（关键，否则台词被悄悄减半）+ `-c:a aac`。
- **CLI 签名**：`--video --dialogue --bgm --out` + `--bgm-volume --duck-threshold/ratio/attack/release（默认 0.03/8/40/400）--bgm-start --fade-in/out --audio-bitrate`。
- 循环 `-stream_loop`/`aloop` + `apad` 补静音 + `afade` 淡入淡出；`ffprobe` 取时长拼串。
- **缺台词**（不 duck，BGM 直接铺）/**缺 BGM**（仅台词）行为矩阵按 angle-2 交付。
- **v1 只消费单 BGM**，整条 `bgm.md` 多 cue 拼接留后续。

## 8. 剧本侧 cue / `bgm.md`

- **落盘**：novel 每集 `ai_videos/<drama>/episodes/epNN/bgm.md`；short 项目根 `bgm.md`。仿 `subtitles.md` 极简、行式、可 grep。
- **cue 行格式**：`起-止(秒) bgm_NNNN | vol= | duck=on/off | fade=in/out`（pipe 分隔）。同时满足三方消费者：`grep -o 'bgm_[0-9]\{4\}'` 反查、行式 parse 供 `mux_av.py`、终端可读供作者。
- cue 语义 ↔ mux filtergraph 一一对应：`duck=on/off`→是否 `sidechaincompress`、`fade=`→`afade`、`loopable`→`-stream_loop`+trim。

## 9. 规则同步 `.claude/agent_refs/project/ai_video.md`

surgical 增补一节「BGM 库 + cue 契约」：库结构 `_bgm/{category}/bgm_NNNN/`、情绪库一次生成跨剧按 id 复用、12 情绪枚举、`bgm.md` cue 行格式、与 render-side 字幕烧录(rule 11c)是独立路径、license 字段语义。一次一条原则，附本 run 引用。

## 10. 验收锚点（供 Stage 5 细化）

1. **DDD 合规**：`bgm__*` 切片层级/单一职责严格对齐 actor；route→单一 application Query/Command 方法；commands 走 domain；强类型；文件 < 100 行优先。
2. **id 全局唯一**：跨 category 扫描分配、`mkdir(exist_ok=False)` 原子、并发不撞号。
3. **生成路径**：webapp `generate` → subprocess `stableaudio_gen.py` → 产出 `bgm_NNNN.mp3` + 写 `.md` 元数据表；webapp 进程无 torch 依赖。
4. **UI**：网格渲染 + mp3 试听可播 + 分类 filter 生效 + assignments 反查正确（构造一条 `bgm.md` 引用可被反查到）。
5. **mux**：给定 video+dialogue+bgm 产出成片，`-c:v copy` 不重编码、台词响度不被 amix 减半、duck 生效（台词段 BGM 让位）。
6. **cue 三方可消费**：grep 反查、parse、人读。
7. **许可证正确**：元数据 license = Stability AI Community License，README 注明商用边界与 seed best-effort。

## 11. 已定决议（Stage 5 sign-off, 2026-06-16）

- **删除守卫**：删除一个 `bgm_NNNN` 前**扫 assignments**（仿 actor）——若任一剧的 `bgm.md` 仍引用它，**拒删并报错**，要求先解绑。软删仅在无引用时执行到 `_deleted/_bgm/`。
- **cue `vol=` 单位 = 0-1 线性**（如 `vol=0.6` = 60% 线性增益）；`mux_av.py` 内部按需转 dB。
- **生成 `duration` 不设硬上限**（用户接受：本机自用、无并发；security 的 GPU-time DoS 仅记 observe-only，不做门）。
- **carve-outs 全部确认**（v1 既定 out-of-scope）：mux v1 仅单 BGM；无 generate-diverse/archetype；seed best-effort；`mux_av.py` 不经 web（CLI-only）；无独立性能门。
- `system_cue` 暂归 BGM，标注本仓自定（未改）。
- `create-prompts` 离线导入流程可选、不阻塞 v1（未改）。
