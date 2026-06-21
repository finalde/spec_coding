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

## Follow-up 005 — 2026-06-21 00:00:00
Source: user_input/follow_ups/005-20260621-000000-chinese-kling-prompt-dual-language.md
Summary: BGM 提示词改双语——中文「Kling 出 BGM」版（复制进 Kling，画面黑屏只取音乐）+ 英文「Stable Audio 本地模型」版；UI 文案全中文。本地 SIGILL/torchsde/torchcodec/ffmpeg 生成链路修复（HF_HUB_DISABLE_XET、soundfile 存盘、imageio-ffmpeg）。

Auto-updated:
- tools/stableaudio_gen.py — HF_HUB_DISABLE_XET=1（绕开 hf_xet 原生扩展 SIGILL）；改用 soundfile 存 WAV（替代依赖 torchcodec 的 torchaudio.save）
- tools/stableaudio_gen.requirements.txt — 增 torchsde（CosineDPMSolverMultistepScheduler 必需）
- libs/infrastructure/writers/bgm__prompt.py — _CATEGORY_TEMPLATE_ZH/_INTENSITY_ADJ_ZH + _compose(zh) + build_bgm_prompt_zh / build_bgm_prompt_kling（中文乐曲描述 + KLING_BGM_NOTE 尾注）
- libs/infrastructure/writers/bgm__writer.py — sidecar 双段（中文 Kling / 英文模型）；_read_sidecar_generation 按「英文」表头回读模型用英文；_fenced_block_under_header 辅助；generate_batch/create_prompts_batch/preview_prompts 同出中英两版（prompt=中文、prompt_en=英文）
- libs/application/dtos/bgm__dto.py + mappers/bgm__mapper.py — BgmPreviewPromptQdto 增 prompt_en 透传
- apps/ui/src/components/{BgmPoolGenerator,BgmView,BgmGrid,BgmEpisodePanel}.tsx — BGM 文案全中文（prompt→提示词 等）
- apps/ui/src/api.ts — BgmPreviewSlot 增 prompt_en?
- libs/infrastructure/readers/tree__reader.py — _bgm/{category} 文件树显示中文（悬疑 等）
- ai_videos/_bgm/*/bgm_000{1..6}/*.md — 6 条既有 sidecar 迁移为双段（英文段 byte 不变）

Verify: test_bgm_library 13 passed；UI tsc 通过；bgm_0001 本地 GPU 端到端出 mp3 成功（841KB）；6 条 sidecar 回读英文段 assert 通过。
No conflicts found in: findings/, final_specs/spec.md（库结构/引用/删除契约不变，提示词内容由单语变双语属生成细节）, validation/*

## Follow-up 005 addendum — 2026-06-21（prompt 细化 + key + MP4→MP3）
- libs/infrastructure/writers/bgm__prompt.py — 中英模板大幅细化（速度/动态/织体/空间/情绪用途）；build_bgm_prompt_kling 增 bgm_id 参数：Kling 中文 prompt 首行放 KEY（bgm_NNNN），便于下载文件按 key 路由回正确轨道
- libs/infrastructure/writers/bgm__writer.py — _newest_download(extensions, prefer_key) 通用取件（文件名含 key 优先于更新的无关文件）；import_video(bgm_id) = MP4→MP3（取最新视频、ffmpeg 抽音轨到 bgm_NNNN.mp3、源视频留在 Downloads）；_extract_audio_to_mp3 + _ffmpeg_exe(imageio-ffmpeg)；_VIDEO_EXTENSIONS
- libs/domain/errors/bgm__error.py — BgmNoDownloadVideoError / BgmAudioExtractFailedError
- libs/domain/repositories/bgm__repository.py + libs/application/commands/bgm__command.py — import_video
- apps/api/routes/bgm__route.py — POST /api/bgms/{id}/import-video；app_factory 注册两个新错误（404 bgm_no_download_video / 500 bgm_audio_extract_failed）
- apps/ui/src/{api.ts, components/BgmView.tsx} — importBgmVideo + 「🎬 从视频提取(MP4→MP3)」按钮（有/无音频两态都有）
- ai_videos/_bgm/suspense/bgm_000{1,2} — 现存轨道再迁移（细化模板 + 首行 key）
- tests/test_bgm_library.py — +test_import_audio_prefers_keyed_download、+test_import_video_extracts_audio（15 passed）

Verify: test_bgm_library 15 passed；UI tsc 通过；真 ffmpeg 抽音轨冒烟（mp4→mp3 15KB）OK。
注：会话中用户经 webapp 删除了旧 bgm_0001–0006（软删到 _deleted/_bgm/，可恢复）并新建了 2 条 prompt-only 轨；非脚本所为。

## Follow-up 006 — 2026-06-21 01:00:00
Source: user_input/follow_ups/006-20260621-010000-simplify-elevenlabs-english-prompt.md
Summary: 简化流程——只出单一英文 prompt（供 ElevenLabs），保留首行 KEY 便于一键导入；mood/配器中文预设译英；删除 Kling/MP4→MP3 全链路。

Auto-updated:
- libs/infrastructure/writers/bgm__prompt.py — 改单一英文 build_bgm_prompt（细化模板保留）+ build_bgm_prompt_keyed（首行 bgm_NNNN KEY）；新增 _MOOD_EN/_INSTRUMENTS_EN 预设译英；删除中文模板/形容词/Kling 函数/KLING_BGM_NOTE/_compose(zh)
- libs/infrastructure/writers/bgm__writer.py — sidecar 单段「英文 · 复制到 ElevenLabs」；_read_sidecar_generation strip 首行 KEY 再喂模型；删除 import_video/_extract_audio_to_mp3/_ffmpeg_exe/_VIDEO_EXTENSIONS；generate/create/preview 用 keyed/英文
- libs/domain/errors/bgm__error.py — 删 BgmNoDownloadVideoError/BgmAudioExtractFailedError
- libs/domain/repositories/bgm__repository.py + application/commands/bgm__command.py — 删 import_video
- apps/api/routes/bgm__route.py — 删 POST import-video；app_factory 删两错误注册
- libs/application/dtos/bgm__dto.py + mappers/bgm__mapper.py — 删 BgmPreviewPromptQdto.prompt_en
- apps/ui/src/api.ts — 删 importBgmVideo + BgmPreviewSlot.prompt_en
- apps/ui/src/components/BgmView.tsx — 删「🎬 从视频提取(MP4→MP3)」按钮 + onImportVideo + import_video busy 态
- ai_videos/_bgm/*/bgm_000{1..5} — 现存轨道迁移为单段英文 + key
- tests/test_bgm_library.py — 删 import_video 测试；+test_prompt_carries_key_line_and_readback_strips_it；preview 测试改断言英文

Verify: test_bgm_library 15 passed；UI tsc 通过；无悬挂引用（grep 干净）。

## Follow-up 007 — 2026-06-21 02:00:00
Source: user_input/follow_ups/007-20260621-020000-global-import-and-longer-prompt.md
Summary: 清空现有 BGM 重生成；导入改为左侧导航全局一键（像 _actor）；删每页单独导入；prompt 重写为 ≥1000 字符结构化长文。

Auto-updated:
- ai_videos/_bgm/* + _deleted/_bgm — 删除全部现有轨道（清空重生成）
- libs/infrastructure/writers/bgm__prompt.py — build_bgm_prompt 重写为结构化长 brief（风格/情绪/能量/编曲结构/动态/制作混音/用途/纯音乐约束/时长，~1700+ 字符）+ _CATEGORY_SCENE/_INTENSITY_DYNAMICS
- libs/infrastructure/writers/downloads__writer.py — 新增 import_bgms（按 bgm_NNNN key 全局归位音频）+ _collect_bgm_folders + _clear_audio_files + BGM 常量
- libs/application/commands/downloads__command.py — drama_name=_bgm → import_bgms 分发
- libs/infrastructure/writers/bgm__writer.py — 删 import_audio/_newest_download/_clear_audio + 死常量(_AUDIO_EXTENSIONS/_IMPORT_WINDOW_SECONDS/_DOWNLOADS_ENV_VAR)；docstring 更新
- libs/domain/{errors/bgm__error.py(删 BgmNoDownloadAudioError), repositories/bgm__repository.py(删 import_audio)}
- libs/application/commands/bgm__command.py — 删 import_audio
- apps/api/routes/bgm__route.py(删 import-audio 路由) + app_factory.py(删 BgmNoDownloadAudioError 注册)
- apps/ui/src/api.ts — 删 importBgmAudio
- apps/ui/src/components/BgmView.tsx — 删每页导入按钮+handler+busy 态；空态提示改指向左侧全局导入
- apps/ui/src/components/Sidebar.tsx — _bgm 根新增「📥 导入下载音乐」按钮（onRenameClick → /api/import-from-downloads）
- tests/ — 删 2 个 import_audio 测试；+test_prompt_is_long_and_detailed(≥1000)；+test_downloads_import_bgms.py(3 测试：按 key 归位/未匹配+非音频跳过/覆盖)

Verify: test_bgm_library + test_downloads_import_bgms + test_boot_smoke = 24 passed；UI tsc 通过；prompt 实测 ~1700–1800 字符；grep 无悬挂引用。

## Follow-up 008 — 2026-06-21 03:00:00
Summary: BGM 编排页解锁分配——每条 cue 先选类型(默认 cue 情绪/已分配轨道类型，含「全部类型」)再选 BGM，不再锁死只能选 cue 指定类型下的轨道。

Auto-updated:
- apps/ui/src/components/BgmEpisodePanel.tsx — 每行新增类型下拉(pickCat 状态)；BGM 列表按所选类型(或全部)过滤；已分配轨道即使跨类型也保留可见；选项显示带类型标签
- apps/ui/src/styles.css — .bgm-ep-cat-select 间距

Verify: UI tsc 通过。后端 assign 本就不校验类型匹配(仅校验轨道存在+有音频)，无需改动。
