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
