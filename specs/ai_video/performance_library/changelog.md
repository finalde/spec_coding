## Follow-up 001 — 2026-06-13 11:35:57
Source: user_input/follow_ups/001-20260613-113557-web-nav-chinese.md
Summary: 演技库在 web UI 左侧导航用中文显示，不要拼音。

Auto-updated:
- final_specs/spec.md — FR-12 注明 nav label 显示中文（display_name），来源 _emotion.md H1 / README 《》标题；路径仍英文/拼音。
- projects/ai_video_management/libs/infrastructure/readers/tree__reader.py — 新增 `_sidecar_zh_label()`，从 `{emotion}/_emotion.md` H1 取中文名（剥除 `（拼音）` 注解）设为 directory node 的 display_name；`_walk_filtered` 调用之。库根 `_performances` 经 README H1 `《表演演技库》` 由既有 `_project_zh_title` 解析。
- ai_videos/_performances/README.md — H1 改为 `# 《表演演技库》— …`，使 `_project_zh_title` 干净提取「表演演技库」作 nav label。

验证: TreeReader 实跑确认 nav 显示 库根「表演演技库」+ 10 情绪全中文（压抑隐忍 / 爽感反转 / 崩溃失控 / …）。webapp tree 测试 7/8 通过（1 失败为预先存在、与本改动无关的 wukong_juexing fixture 缺失）。

No conflicts found in: interview/qa.md, findings/, validation/（显示层改动，不触及内容契约 / 四维 schema / 验证回路）。

## Follow-up 002 — 2026-06-13 11:53:50
Source: user_input/follow_ups/002-20260613-115350-render-prompts-and-import.md
Summary: 端到端渲染-导入工作流：可 copy-paste prompt 清单 + 下载视频一键归位到 perf 栏目。

Auto-updated:
- final_specs/spec.md — 新增 FR-15（渲染队列 + 一键导入 + 导入 tag 约定）。
- ai_videos/_performances/_testrig.md — 新增「导入 tag 约定」段 + 骨架模板首行加 tag。
- ai_videos/_performances/*/perf_*/perf_*.md — 91 个 render 块首行加 `演{NNNN}{克|即|始}` tag（tools/add_perf_import_tags.py）。
- ai_videos/_performances/{yayi_yinren,shuanggan_fanzhuan,bengkui_shikong}/_render_queue.md — 生成的可复制渲染队列（tools/build_render_queue.py）。
- projects/ai_video_management/libs/infrastructure/writers/downloads__writer.py — 新增 import_performances() + _collect_perf_folders() + _PERF_TAG/_PERF_MARKER_ROLE 常量。
- projects/ai_video_management/libs/application/commands/downloads__command.py — path=_performances 时 dispatch 到 import_performances。
- projects/ai_video_management/apps/ui/src/components/Sidebar.tsx — _performances 根「📥 导入检验视频」按钮 + 🎬 图标。
- tools/add_perf_import_tags.py, tools/build_render_queue.py — 新增工具脚本。

新增测试: projects/ai_video_management/tests/test_downloads_import_performances.py（3 测试全过：按 tag 路由+规范重命名 / 未匹配进 _not_matched / 重导入覆盖）。前端 tsc --noEmit 通过。

No conflicts found in: interview/qa.md, findings/, validation/strategy.md（新增工作流，不改四维 schema / 验证回路判定）。

## Follow-up 003 — 2026-06-13 12:25:00
Source: user_input/follow_ups/003-20260613-122500-generic-single-prompt.md
Summary: 表演库 generic 化：一个通用 prompt（不分 Kling/Seedance）+ 演员由用户上传（任意 actor，image-to-video）+ 表演室场景 + 按情绪灯光。

Auto-updated:
- final_specs/spec.md — FR-11 重写为 v2（generic 通用 prompt / 上传演员 / 表演室 / 按情绪灯光）；FR-15 导入 tag 去模型标记、视频→renders/。
- ai_videos/_performances/_testrig.md — 重写 v2。
- ai_videos/_performances/*/_emotion.md — 加「灯光氛围（检验视频）」行（tools/set_emotion_lighting.py，10 文件）。
- ai_videos/_performances/*/perf_*/perf_*.md — 38 条检验视频双块→单通用块、起始帧去演员化（tools/genericize_perf_prompts.py + 手修 perf_0035/0036 的 表情与姿态 变体）；表演文本逐字保留。
- ai_videos/_performances/*/_render_queue.md — 重生成（tools/build_render_queue.py，53 块）。
- projects/ai_video_management/libs/infrastructure/writers/downloads__writer.py — 导入器适配新 tag：演{NNNN}→renders/（原名）、演{NNNN}始→canonical startframe。
- projects/ai_video_management/tests/test_downloads_import_performances.py — 更新为新 tag 方案（9 测试全过）。
- tools/set_emotion_lighting.py, tools/genericize_perf_prompts.py — 新增。

验证: importer 9 测试全过；webapp tree 实跑确认 _performances 中文 label + render_queue 可浏览；全库 0 残留（无 actor_0001 / 纯浅灰 / ### Kling/Seedance / 旧克即 tag）。

No conflicts found in: interview/qa.md, findings/, validation/strategy.md（generic 化是检验视频外层 wrapper 的收敛，不改四维 schema / 物理动作铁律 / 验证回路判定）。

## Follow-up 004 — 2026-06-13 13:55:00
Source: user_input/follow_ups/004-20260613-135500-dual-scorer-feedback.md
Summary: 双评分者评分闭环——webapp 每个 perf 页面打分按钮 + Claude 抽帧评分 + 合议 accept/revise。

Auto-updated:
- final_specs/spec.md — 新增 FR-16（你 + Claude 评分 + 合议）。
- ai_videos/_performances/_testrig.md — 新增「评分与合议」段（含 Claude 抽帧评分流程）。
- ai_videos/_performances/*/perf_*/perf_*.md — `## 实测与验证` 改双评分者表 + decision + 合议（tools/migrate_validation_block.py，38 条）。
- projects/ai_video_management/libs/infrastructure/writers/perf_score__writer.py — 评分引擎（update_scores_text 纯函数 + PerfScorer）。
- projects/ai_video_management/libs/application/commands/perf_score__command.py — 命令层。
- projects/ai_video_management/apps/api/routes/perf_score__route.py + routes/__init__.py — POST /api/perf-score。
- projects/ai_video_management/apps/api/container.py — perf_scorer Singleton + perf_score_command Factory + imports。
- projects/ai_video_management/apps/ui/src/api.ts — perfScore() + PerfScoreResult。
- projects/ai_video_management/apps/ui/src/components/PerfScorePanel.tsx — 评分面板（新增）。
- projects/ai_video_management/apps/ui/src/components/Reader.tsx — isPerfEntry 时挂 PerfScorePanel。
- tools/extract_perf_frames.py, tools/perf_rate.py, tools/migrate_validation_block.py — 新增。

新增测试: projects/ai_video_management/tests/test_perf_score.py（6 测试：单边 pending / 双方达标 accept / 分歧 revise / 任一模型达标 accept / writer 端到端 / 路由接线 400）。全套 16 测试（含 import + boot smoke）通过；前端 tsc 通过。

No conflicts found in: interview/qa.md, findings/, validation/strategy.md（评分闭环是 FR-13 人工门的细化，不改四维 schema / 物理动作铁律）。

## Follow-up 005 — 2026-06-13 14:09:03
Source: user_input/follow_ups/005-20260613-140903-per-beat-duration.md
Summary: 检验视频时长按 beat 分配（4–15s），不固定 5s；多拍渐进条放长且时间窗等比放大。

Auto-updated:
- final_specs/spec.md — FR-11 ⑤ 时长由固定 5s 改为按 beat（4–15s）阶梯。
- ai_videos/_performances/_testrig.md — 时长行 + 骨架时长占位改为按 beat。
- ai_videos/_performances/*/perf_*/perf_*.md — 16 条时长调整（tools/set_perf_durations.py）：强度阶梯 + 4 条显式多拍条时间窗等比放大（perf_0035→12s / 0036·0037→10s / 0038→8s）。
- ai_videos/_performances/*/_render_queue.md — 重生成。
- tools/set_perf_durations.py — 新增。

验证: 全库静态检查通过（每条 1 个通用块 + 合议表）；perf_0035 时间窗 [0–2.4s]…[10.1–12s] 求和=12s、总和文本同步。

No conflicts found in: interview/qa.md, findings/, validation/strategy.md（时长是渲染参数，不改四维 schema / 物理动作铁律 / 评分回路）。

## Follow-up 006 — 2026-06-13
Source: user_input/follow_ups/006-*-uniform-prompt-scoring.md
Summary: 评分去模型维度，对唯一通用 prompt 统一打分（你 + Claude 各一行三轴）。

Auto-updated:
- final_specs/spec.md — FR-16 去模型维度。
- ai_videos/_performances/_testrig.md — 评分段去模型。
- ai_videos/_performances/*/perf_*/perf_*.md — 实测与验证表去「模型」列（38 条）。
- perf_score__writer.py / perf_score__command.py / perf_score__route.py — 去 model 参数；引擎按评分者 keyed。
- apps/ui/src/api.ts + components/PerfScorePanel.tsx — 去模型下拉/参数。
- tools/perf_rate.py + migrate_validation_block.py — 去 model 参数 / 新表结构。

验证: test_perf_score.py 6 测试全过（含路由 400 + 端到端 + 重评覆盖）；前端 tsc 通过；全库 0 残留模型列。

No conflicts found in: interview/qa.md, findings/, validation/strategy.md。

## Follow-up 007 — 2026-06-13
Source: user_input/follow_ups/007-*-complete-emotions-and-shot-reference.md
Summary: 补全全库 122 条 entry；shot 引用表演库（标注+按剧情融入非照抄）；shot 页面「按表演库重生成」按钮。

Auto-updated:
- ai_videos/_performances/{henli_yinzhi,zhenjing_cuoe,rouqing_shenqing,weiqu_kelian,buxie_chaofeng,xiuru_nankan,waifang_fennu}/perf_*/perf_*.md — 84 条 entry body（7 worker 并行）+ set_perf_durations + build_render_queue。
- final_specs/spec.md — FR-10 v2（融入非照抄）+ 新增 FR-17（重生成按钮）。
- .claude/agent_refs/project/ai_video.md — 新增 rule 9b（引用表演库）。
- ai_videos/_performances/_reference_usage.md — 重写为标注+融入样例。
- ai_videos/_performances/README.md — 引用用法/验证流程/当前状态/目录布局 更新去 drift。
- projects/ai_video_management: libs/infrastructure/readers/shot_regen__reader.py + libs/application/queries/shot_regen__query.py + apps/api/routes/shot_regen__route.py + container + routes/__init__ + apps/ui/src/api.ts + components/ShotRegenButton.tsx + components/Reader.tsx（isShotEntry 挂载）。

新增测试: tests/test_shot_regen.py（3：组装含最新锁定块 / 无标注返回提示 / 缺失 perf 标记）。全套 19 后端测试通过；前端 tsc 通过。

No conflicts found in: interview/qa.md, findings/, validation/strategy.md。
