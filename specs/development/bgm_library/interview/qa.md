# Interview — bgm_library

Run: bgm_library-20260616-123238

## Categories probed
- 生成调用方式 — MusicGen 自托管怎么接入 webapp，决定 bgm__writer 架构与依赖边界。
- UI 生成入口 — 库视图是否含从 UI 触发生成，决定 query/command/route 面。
- mux 范围 — tools/mux_av.py 是否本期交付，决定 stage-6 work unit 数量。
- 分类体系 — category 取固定枚举 / 双层 / 自由，决定 value object 与 UI filter。
- cue 落盘 — 剧本侧 BGM 引用写在哪，决定 assignments 反查源。

## 预先确定（对话已澄清，未列为问题）
- **id 方案**：全局唯一 `bgm_NNNN`，跨 category（仿 `actor_NNNN`）。用户原话「每个背景音乐都有 unique id …… 就像演员一样」已锁定。
- **库共享**：单一共享库 `ai_videos/_bgm/`，非每剧独立。

## Round 1

### 生成调用方式
**Q:** MusicGen 自托管怎么被 webapp 调用生成 mp3？
- A: tools/ 子进程脚本 — 仿 kling_autopilot，独立 `tools/musicgen_gen.py` 跑推理，webapp 通过 subprocess 调用；torch/audiocraft 重依赖与 GPU 隔离在脚本端，webapp 进程不背重依赖。

### UI 生成入口
**Q:** BGM 库 UI 是否含「从 UI 触发生成」按钮？
- A: 含生成（仿 actor）— UI 有 preview prompt + generate 按钮，填情绪/时长/BPM 等参数点生成。

### mux 范围
**Q:** tools/mux_av.py（视频+台词MP3+BGM 合成，sidechain duck）这期是否一并实现？
- A: 一并实现 — 本期同时交付 mux_av.py（ffmpeg：视频流 copy + 台词 MP3 + BGM，BGM sidechain duck 让位人声）。

### 分类体系
**Q:** BGM 分类（category）用哪套体系？
- A: 固定情绪枚举 — 预设 N 类（紧张对峙/打斗/悲情/温情/悬疑/日常/高燃爽点/片头主题 等），UI 从枚举选，可预填默认。

### cue 落盘
**Q:** 剧本里的 BGM cue（引用 bgm_NNNN + 起止/音量/duck）写在哪？
- A: 每集/每短一个 bgm.md — 仿 dialogue.md/subtitles.md，每集（novel）或项目根（short）一个 bgm.md 时间线，集中管理；assignments 从它反查「哪些剧引用了某 bgm」。

## Team consensus
All categories marked clear after 1 round.
