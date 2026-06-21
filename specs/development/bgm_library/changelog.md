# bgm_library — changelog

## Follow-up 001 — 2026-06-16 14:00:00
Source: user_input/follow_ups/001-20260616-140000-mood-instrument-presets-and-error-tail.md
Summary: 生成表单 mood/instruments 改为 dropdown 预设 + 可选自定义框；生成失败错误信息改取 stderr 末行（暴露真正异常）。生成失败根因=运行解释器缺 torchaudio/stable-audio-tools（环境问题，非代码 bug）。

Auto-updated:
- apps/ui/src/api.ts — 新增 BGM_MOOD_PRESETS / BGM_INSTRUMENT_PRESETS 前端预设词表
- apps/ui/src/components/BgmPoolGenerator.tsx — mood/instruments 改为 dropdown(预设)+可选自定义框；自定义优先、留空回退预设
- libs/infrastructure/writers/bgm__writer.py — _run_stableaudio 失败时取 stderr 末行非空内容（原先取前 300 字隐藏了真正异常）

No conflicts found in: final_specs/spec.md, findings/, validation/* (生成依赖/venv 契约本就在 spec 与 stableaudio_gen.requirements.txt 中描述，无需改动)

## Follow-up 002 — 2026-06-16 15:00:00
Source: user_input/follow_ups/002-20260616-150000-two-step-prompt-then-audio.md
Summary: BGM 拆成两步——步骤1「生成 prompt」(prompt-only，不出音频)；步骤2 按条「本地 GPU 生成」或「导入下载音乐」(Downloads 最新音频)。reaper 修正为保留 prompt-only track。导入路径不需要 torch。

Auto-updated:
- libs/infrastructure/writers/bgm__writer.py — create_prompts_batch (prompt-only) / generate_audio(bgm_id) / import_audio(bgm_id) / _read_sidecar_generation / _newest_download_audio / _clear_audio；reaper 跳过有 sidecar 的 prompt-only 文件夹；新增 _AUDIO_EXTENSIONS / Downloads 解析
- libs/domain/errors/bgm__error.py — 新增 BgmSidecarUnreadableError / BgmNoDownloadAudioError
- libs/domain/repositories/bgm__repository.py — 协议新增 create_prompts_batch / generate_audio / import_audio
- libs/application/{dtos,mappers,commands}/bgm__* — BgmAudioResultCdto；audio_to_cdto；BgmCommand.create_prompts / generate_audio / import_audio
- apps/api/routes/bgm__route.py — POST /api/bgms/create-prompts、/{bgm_id}/generate-audio、/{bgm_id}/import-audio
- apps/api/app_factory.py — 注册 BgmSidecarUnreadableError(422) / BgmNoDownloadAudioError(404)
- apps/ui/src/api.ts — createBgmPrompts / generateBgmAudio / importBgmAudio + BgmAudioResult
- apps/ui/src/components/BgmPoolGenerator.tsx — 主按钮改为「生成 prompt」(create-prompts)，文案改两步说明
- apps/ui/src/components/BgmView.tsx — 无音频时显示「🎧 本地 GPU 生成」「📥 导入下载音乐」按钮；有音频时显示「♻ 重新导入下载」
- tests/test_bgm_library.py — 新增 create_prompts/generate_audio/import_audio/reaper-preserves-prompt-only 4 测试

Tests: test_bgm_library 13 passed；UI tsc 通过。
No conflicts found in: final_specs/spec.md, findings/, validation/* (两步流程是生成路径的细化，spec 的 track 落盘结构/引用/删除契约不变)

## Follow-up 003 — 2026-06-17 10:00:00
Source: user_input/follow_ups/003-20260617-100000-diffusers-backend-py313.md
Summary: 本地生成后端 stable-audio-tools → diffusers StableAudioPipeline（同一 stable-audio-open-1.0 权重）。原因：stable-audio-tools 硬 pin pandas==2.0.2 等旧依赖在 py3.12/3.13 无轮子、编译失败。CLI 契约不变，webapp/测试不受影响。

Auto-updated:
- tools/stableaudio_gen.py — _generate 改用 diffusers.StableAudioPipeline（model id 自动补 stabilityai/ 前缀，fp16@cuda，200 steps，output_type=pt，torchaudio 存 wav→ffmpeg mp3）；docstring 注明 py3.13 原因 + HF gating
- tools/stableaudio_gen.requirements.txt — diffusers/transformers/accelerate/sentencepiece/protobuf/soundfile；GPU torch 单独装；安装/HF 登录说明
- 环境（非仓库文件）：.venv-stableaudio 装 torch2.11+cu128(CUDA 可用)+torchaudio+diffusers0.38+transformers5.12；BGM_PYTHON 用户环境变量已指向该 venv

Verify: torch.cuda.is_available()=True；StableAudioPipeline 导入 OK；模型 model_info 可访问（token 已就绪）；真机 10s 生成测试进行中。
No conflicts found in: final_specs/spec.md, findings/, validation/* (spec 写的是「自托管 Stable Audio 开源权重」，diffusers 加载器满足该意图；如需可在 findings/angle-musicgen-selfhost.md 追注加载器选择)

## Follow-up 004 — 2026-06-20 16:23:12
Source: user_input/follow_ups/004-20260620-162312-episode-bgm-cue-assign-burn.md
Summary: Episode 级 BGM 编排——稀疏 cue 时间线 `episodes/epNN/bgm/bgm.md`（pipeline 人工写）+ webapp 像 casting 一样按情绪 assign 库内 bgm_NNNN + 一键烧录进带字幕整集视频 `ep{NN}_zh.mp4` → `ep{NN}_zh_bgm.mp4`（重烧覆盖、duck=on 台词让路、未分配 cue 跳过）。

Auto-updated (new DDD slice `episode_bgm__*`):
- libs/domain/value_objects/episode_bgm__valueobject.py — BgmCue + 稀疏 cue 行式 grammar(parse/serialize；slot=bgm_NNNN|-、cat=情绪、vol/duck/fade/注释)
- libs/domain/errors/episode_bgm__error.py — 路径/cue/源缺失/track缺音频/ffmpeg/mux 命名错误
- libs/domain/repositories/episode_bgm__repository.py — read/assign/unassign/burn 协议
- libs/infrastructure/writers/episode_bgm__writer.py — EpisodeBgmManager：read、assign(改写 slot)、burn(多 cue ffmpeg filtergraph：aloop→atrim→volume→afade→adelay，duck 用源音轨 sidechaincompress，amix normalize=0，-c:v copy)
- libs/infrastructure/writers/bgm__writer.py — BgmPool.audio_path_for(bgm_id)（公开按 id 解析 mp3 绝对路径）+ 协议同步
- libs/application/{dtos,mappers,commands,queries}/episode_bgm__* — EpisodeBgmCommand(assign/unassign/burn) + EpisodeBgmQuery(read)
- apps/api/routes/episode_bgm__route.py — GET /api/episode-bgm、POST/DELETE /assign、POST /burn；routes/__init__ 注册；container 接线 episode_bgm_manager/command/query；app_factory 注册 10 个 episode-bgm 错误
- libs/infrastructure/readers/bgm_reference__reader.py — 反查扫描兼容 `episodes/epNN/bgm/bgm.md`（保留旧 `epNN/bgm.md`）
- apps/ui/src/api.ts — readEpisodeBgm/assignBgmCue/unassignBgmCue/burnEpisodeBgm + 类型
- apps/ui/src/components/BgmEpisodePanel.tsx — episode BGM 面板（cue 表 + 按情绪过滤的分配下拉 + 试听 + 🎵 烧录按钮）；Reader.tsx 在 `…/episodes/epNN/bgm/bgm.md` 挂载；styles.css 样式
- tests/test_episode_bgm.py — parse/serialize、read、assign/unassign、未知 bgm 拒绝、窗口未命中、burn(跳过未分配/无分配报错/缺源报错)、filtergraph 形状、非 episode 路径（10 测试全过）
- ai_videos/wushen_juexing/.../episodes/{ep01,ep02}/bgm/bgm.md — 按剧本人工产出的稀疏 cue 编排（ep01 7 条 / ep02 8 条，全待分配）
- .claude/agent_refs/project/ai_video.md — 增补「episode 级 BGM cue + folder + 烧录」规则

Verify: test_bgm_library + test_episode_bgm + test_episode_concat = 29 passed；UI tsc 通过 + vite build 通过；真 ffmpeg 多 cue mux 冒烟（duck+非duck）出片带音轨 OK。
No conflicts found in: findings/, validation/* (烧录是 v1「mux 多 cue 留后续」的兑现，spec 的库结构/引用/删除契约不变；final_specs/spec.md §7 的 v1 单 BGM mux 仍在，episode 烧录是其多 cue 上位)
