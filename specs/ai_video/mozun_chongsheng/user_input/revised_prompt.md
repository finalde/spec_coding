# Revised prompt — mozun_chongsheng

**task_type:** ai_video
**sub_type:** novel（多集，episodes/epNN/ 布局）
**task_name:** mozun_chongsheng
**Composed from:** `raw_prompt.md`
**First generated:** 2026-05-09 16:42:05
**Last regenerated:** 2026-05-21 22:15:05 — header bump for follow-up 030（小说文本 @-ref header 改用「中文剧名」而非 task_name pinyin slug；char/scene id 去掉 `cN_` / `sN_` 前缀，只保留中文名。具体到本项目：小说名 = `魔尊归来`（README H1），人物 / 场景名取 `## Reference placeholders` 段去前缀的中文部分。例：`沧冥請參考:@魔尊归来_沧冥，长阶顶請參考:@魔尊归来_长阶顶`。029 引入的 `## 小说文本 / Novel prose` 段保持有效，仅 @-ref header 格式重述更易读。已写入的 ep01 / ep02 共 20 shots 已采新格式；ep03 / ep04 / ep05 30 shots 在后续补段时直接采新格式。`agent_refs/project/ai_video.md` 模板段 + 029 follow-up 文档示例同步更新。）**Prior bump:** 2026-05-21 20:26:46 — header bump for follow-up 029（每 shotNN.md 新增 `## 小说文本 / Novel prose` 段，位置在 `## Reference placeholders` 之后、`## 视频 prompt` 之前；200-400 字仙侠小说式散文派生自 Shot context Summary + 动作 timed beats + 台词 + 场景 / 色调，禁止复制 timed-beats 行 / placeholder / 技术语。`agent_refs/project/ai_video.md` 规则 12.4 必填子项加第 6 项「小说文本 / Novel prose」+ 新增专门规则块。ep01 / ep02 共 20 shots 已 backfill 完成；ep03-05 30 shots backfill pending。）**Prior bump:** 2026-05-19 20:22:33 — header bump for follow-up 028 (cross-project ripple from ai_video_management follow-up 099). **Character turntable rule #12.5 v10.2 → v11** (supersedes 027 v10.2 patch applied this same day morning). 时长 7s → 7s (unchanged), schedule unchanged (same 3 static landings + 2 transitions + same CANONICAL_VIEWS (1.0, 3.5, 6.0) timestamps), **仅 prompt rendering 简化**. **Why v10.2 → v11 same day**: 用户 empirical 测试 v10.2 渲染 (今天早上由 027 触发) 后立即报告: "the camera did not move as you intended in the charactor prompt, I think kling got confused, you need to tell it in a more simple way and only once in the prompt. currently the it shart to turn around to side view at only about 5s." Root cause: v10.2 prompt 把 motion 路径在 4 字段 (镜头 + 动作 + 节奏 + 负向 qualifier 段落) 用 "motion bridge" / "static landing" / "locked-framing" / "锁定机位" 技术 jargon 重复描述, 模型 average 多 conflicting 描述而 under-commit to motion, motion 实际延迟到 ~5s 才开始。v11 fix: motion ONLY 在 动作 timed beats 字段一次描述, plain Chinese; 镜头 = 仅 framing/lens specs (no motion path); 节奏 = one sentence; 负向 = 10 项简单 bans 无 qualifier 段落; 锁定机位 jargon 全部移除 (model 可能把 "锁定" 当 "全程不要动" 理解)。**项目落地**: 10 character md files patched via two-script sequence: `patch_chars_v11.py` (12 substitutions / file covering 文件说明 + h1 + table heading + 3 table 用途 rows + 场景 + 镜头 + 节奏 + 负向 + 动作 6-line block 通过 regex 保留 character name + 标志台词 #1/#2 + 台词 5-line enumeration block 同样保留 character content), then `patch_chars_v11_fix.py` (corrective patch for title line + 光线 line where script 1 patterns missed due to actual file wording differing from rule template). 10/10 confirmed at v11, zero v10.2 motion-jargon markers remaining。Per-character 标志台词 preserved verbatim — slot 4 现在 ONCE 出现在 动作 5-7s beat (与 slot 5 同行), 比 v10.2 的 split-across-3-beats 更简单。锁定机位 jargon 移除 — 改用 "镜头围绕角色顺时针绕 90° 到角色左侧身" / "镜头停在左侧身角度不动" 描述。**No code change** to ai_video_management — `CANONICAL_VIEWS (1.0, 3.5, 6.0)` 不变。**用户后续手工步骤** (out-of-band): (a) re-render the 10 character turntable mp4s at 7s with v11 prompt — v10 + v10.2 renders invalidated; (b) upload one v11 mp4 to Kling for empirical test (motion 应在 ~2s 启动而非 v10.2 实测的 ~5s) — 如仍延迟到 ~3s+, 退到 v12 (shift schedule earlier, 牺牲 0-2s truncate-compat, CANONICAL_VIEWS front 1.0 → 0.5) 或 v13 multi-clip (3 separate static clips concatenated at filesystem level, most bulletproof); (c) click 🖼 (now on direct-mp4 + sibling-tile) — 3 picks all from static lock frames; (d) re-trigger ai_video_management 短角色合辑 + ✂ 截到 2s tool — 0-2s 切片 content byte-identical (unchanged from v10/v10.2)。**027 (v10.2) marked SUPERSEDED at top** with note pointing to 028. Iteration count = 5 character-ref patches in two days, of which 4 applied to disk (024 v8 → 026 v10 morning → 027 v10.2 morning+ → 028 v11 evening; 025 v9 specced but never applied). **Prior bump:** 2026-05-19 00:06:05 — header bump for follow-up 027 (cross-project ripple from ai_video_management follow-up 098). **Character turntable rule #12.5 v10 → v10.2** (supersedes 026 v10 patch applied this same day). 时长 7s → 7s (unchanged absolute value but structurally different: v10 = single 4s continuous 180° orbit, v10.2 = 5-phase = static front + 1s motion + static side + 1s motion + static back). 镜头 「单镜头连续运镜 single continuous take · 9:16 竖屏 · 3 阶段连续运动 (0-2s 锁定 + 2-6s 缓慢顺时针 180° orbit ≤ 45°/s + 6-7s 锁定背面)」 → 「单镜头连续运镜 single continuous take · 9:16 竖屏 · 5 阶段 timed beats (0-2s 锁定正面 + 2-3s motion bridge 0°→90° + 3-4s 锁定左侧身 + 4-5s motion bridge 90°→180° + 5-7s 锁定背面 settle)」. **Why v10 → v10.2 same day**: 用户 empirical 测试 v10 渲染 (今天早上由 026 触发) 后立即发现 v10's 假设失败 — 模型 under-rotates v10's single 4s continuous orbit (~22°/s actual vs 45°/s spec), 且 motion 段 4-5s 才真正启动, 7s 视频末帧仍在 ~90° 侧身, 根本没到 180° 背面。用户原话: "the side is still almost front, the back picture actually shows side ... the video does not have a backview in it"。Root cause: 视频模型不精确遵循 timed-beat 速度指令, 「slow continuous orbit at 45°/s for 4s」 给模型太多 latitude。v10.2 把 latitude 取消, 用 **3 个 static landings + 2 个 1s motion bridges** 代替 single continuous orbit — 每个 motion bridge 必须精确终止在指定角度 (90° at t=3s, 180° at t=5s), static lock 段镜头完全不动。**角度契约从「时间 × 速度」改为「明确 landing 角度 hold」**: 抽帧管线现在 anchor 在 static lock 段而非依赖模型估算 orbit 进度。**Code change** (in ai_video_management 098): `libs/domain/value_objects/character_video__valueobject.py` `CANONICAL_VIEWS` side timestamp 4.0 → 3.5 (mid 3-4s static side, was in v10's motion segment), front t=1.0s + back t=6.0s 不变 (但 back pick 现在落在 v10.2's 2s static back window 中段而非 v10's motion-tail)。**项目落地**: 10 character md files (`ai_videos/mozun_chongsheng/characters/c{1..10}_*/c{N}_*.md`) patched via two-script sequence: `patch_chars_v10_2.py` (13 fixed + 4 regex per file, 17 substitutions / file) for the 文件说明 / heading / 镜头 / 动作 heading / 节奏 / 负向 (13 → 14 items) / table / enumeration changes, then `patch_chars_v10_2_fix.py` (1 multi-line regex per file) to split v10's combined 3-5s + 5-7s beats into v10.2's 3-line structure (3-4s static side + 4-5s motion bridge + 5-7s static back), preserving 标志台词 #1 + #2 via capture groups. 10/10 confirmed at v10.2, zero v10 markers remaining. Per-character 标志台词 unchanged — slot 4 (标志台词 #1) now spans 3-4s static side hold + 4-5s motion to back; slot 5 (标志台词 #2) fully sits in 5-7s static back settle. 0-2s + 一/二 byte-identical content preserved cross v8/v9/v10/v10.2. **用户后续手工步骤** (out-of-band): (a) re-render the 10 character turntable mp4s at 7s with v10.2 prompt — v10 renders from this morning are invalidated by v10.2's structural change; (b) upload one v10.2 mp4 to Kling for validator empirical test before batch-render — hypothesis: bookended motion segments with 0 velocity at landing boundaries ≠ v6 whip-pan; retreat paths v10.3 (drop one bridge, lose back) / v10.4 (drop both bridges, lose side+back) / v11+ multi-clip; (c) click 🖼 button (now on direct-mp4 + sibling-tile per 097) — 3 picks all from static lock frames; (d) re-trigger ai_video_management 短角色合辑 + ✂ 截到 2s tool — 0-2s 切片 content unchanged。**026 (v10) marked SUPERSEDED at top** with note pointing to 027. Same-day double pivot (026 v10 morning, 027 v10.2 evening) — empirical feedback loop from rendering + clicking extract caught v10's flaw within hours. **Prior bump:** 2026-05-18 22:40:47 — header bump for follow-up 026 (cross-project ripple from ai_video_management follow-up 096). **Character turntable rule #12.5 v8 → v10** (skips v9 implementation entirely; 025's v9 script was specced but never run, so the character md files were still at v8 when 026's script ran — patched v8 → v10 in one pass). 时长 7s → 7s (unchanged in absolute terms but the v10 7s is structurally different from v8's 7s: v8 was full static, v10 is 0-2s static + 2-6s slow ccw 180° orbit + 6-7s static back lock). 镜头 「静态单镜头 locked camera · 零运动 · 正面全身远景 ~35mm wide」 → 「单镜头连续运镜 single continuous take · 3 阶段连续运动 with locked framing + no dolly + no zoom + 180° orbit · 正面 medium-full ~40mm 等效」. **Why skip v9**: after follow-up 093 went live (ai_video_management's 「抽 3 视图 + 音频」 pipeline), v9's 15s slow-push-in + slow-orbit + reverse-dolly design was exposed as producing inconsistent 3-still framings — v9's dolly-in and reverse-dolly vary head-size-in-frame across the take, so front pick (t=1.0s wide) / side pick (t=7.0s mid-pull-back ~1/3 frame) / back pick (t=9.0s near-wide but still mid-pull-back) come out at 3 different framings — they cannot be used as a coherent 3-view character sheet for downstream image-to-video reference. 用户在 ai_video_management 096 clarifying 中明确选 locked-framing 全程 (3-still consistency) 而非 mixed-framing + dedicated face MCU (v9 风格)。**v10 3-phase camera path**: 0-2s 锁定机位 正面 medium-full (一+二, byte-identical content to v8/v9 — only framing tightened wide ~35mm → medium-full ~40mm) + 2-6s 缓慢顺时针 180° orbit at 45°/s (相机距角色距离锁定全程, no dolly, no zoom — 仅旋转) + 6-7s 锁定机位 背面 medium-full settle。**抽帧时间戳** (in ai_video_management's `CANONICAL_VIEWS` value object, updated by sibling 096): front t=1.0s (mid 0-2s static, 跨 v9/v10 unchanged), side t=4.0s ((4.0-2.0)×45°/s = exactly 90°), back t=6.0s ((6.0-2.0)×45°/s = exactly 180°)。All 3 picks share IDENTICAL medium-full framing because v10 forbids dolly / zoom — only the angle changes。Face MCU window from v9 is sacrificed (head ~1/5 frame ≈ 360-400px tall at 9:16 1080p in v10 vs ~1/3 frame in v9's MCU window); user explicitly accepted this trade-off。Dialogue slot 3 (2-3s) / 4 (3-5s) / 5 (5-7s) retimed to match v10's 3 phases (slot 4 covers orbit 0-90° / 4-row at t=4.0s side landing; slot 5 covers orbit 90-180° + back-lock settle / 5-row at t=6.0s back landing)。Negatives bumped from v9's 11 items to v10's 13 items: added explicit `不要 任何 dolly / zoom / 推拉镜头` + `不要 任何 framing 变化` + `不要 mid-shot freeze` bans, kept all anti-cut + speed-cap + direction-reversal bans from v9 hypothesis (slow continuous motion + locked framing should pass Kling validator if v9 passes)。**项目落地**: 10 character md files (`ai_videos/mozun_chongsheng/characters/c{1..10}_*/c{N}_*.md`) patched via one-shot Python script `C:/Users/light/AppData/Local/Temp/patch_chars_v10.py` — 19 substitutions per file (15 fixed-string + 4 regex with capture groups preserving character-specific 标志台词 #1 + #2 and character name in slot 3 自我识别). All 10 confirmed at v10, zero v8 markers remaining (sanity check: `static-camera single-shot` / `同机位同构图` / `7 秒内无任何镜头运动` / `5 段静态单 shot` / `(reference 上传硬上限 v8)` — all zero across all 10 files)。Per-character `标志台词` content (#1 + #2 in slots 4 + 5) unchanged across v8 / v9 / v10 — only the surrounding camera-direction wording changed。No code change to ai_video_management project in this sibling follow-up (the CANONICAL_VIEWS timestamps update lives in ai_video_management 096)。**用户后续手工步骤** (out-of-band): (a) 重新渲染 10 份角色 turntable mp4 at 7s with v10 prompt — existing v8 renders (if any) are invalidated because v10's orbit changes visual content; pre-v10 mp4s extracted at new (1.0, 4.0, 6.0) timestamps would produce 3 identical frontal pngs (v8 was static) instead of 3 distinct angles; (b) upload one v10 mp4 to Kling for validator empirical check before batch-rendering (fail-fast retreat: v10.1 = drop orbit / keep 7s static = degraded v8 with v10 negative-prompt wording; v10.2 = insert ~0.3s holds at 90° + 180°); (c) validator pass 后批量渲 10 份 + click 🖼 "提取三视图+音频" button (follow-up 093 feature) — 3 extracted pngs will form a coherent character sheet at identical medium-full framing across all 10 characters; (d) 重新触发 ai_video_management 短角色合辑 + ✂ 截到 2s tool 验证 0-2s 切片 byte-identical content to v8 (still: 静态 + 正面 + 一/二; only framing tighter)。**025 (v9, never applied) marked SUPERSEDED at top** with note pointing to 026 — v9 stays on file as audit trail of the abandoned 15s mixed-framing attempt。Risk acknowledged: v10 is hypothesis (slow continuous orbit + locked framing passes Kling validator); if rejected, retreat paths v10.1 / v10.2 documented in 026 + cross-cutting rule #12.5 v10 attribution footer。**Prior bump:** 2026-05-18 19:49:56 — header bump for follow-up 025 (cross-project ripple from ai_video_management follow-up 092). **Character turntable rule #12.5 v8 → v9** (supersedes 024 v8 patch): 时长 7s → **15s**, 镜头 「静态单镜头 locked camera · 零运动」 → 「单镜头连续运镜 single continuous take · 5 阶段连续运动」. 用户拒绝 v8 trade-off (静态全身远景下面部 ~1/6 frame 太小, 侧身/背面 silhouette 全失), 092 直接 reversal v8 走 slow-motion 路线。v9 hypothesis: Kling validator 的 cut/transition 判定核心因子是**速度 + 方向反转**, 不是 motion 本身; v5/v6 fast 360° (~720°/s) + 6-segment push/pull reversals 触发 validator; v9 走 ≤ 45°/s slow orbit + monotone push-in + reverse-dolly 隐藏在 orbit 弧线 + 13-15s 锁定收尾。**5 阶段连续运镜**: 0-2s 锁定 (与 v8 byte-identical) + 2-5s 缓慢 dolly-in 到面部 medium close-up (face clear) + 5-13s 缓慢顺时针 360° orbit + 同段 reverse-dolly 回 wide (侧身 + 背面 reveal) + 13-15s 锁定收尾。Dialogue slot #3 (2-5s) / #4 (5-10s) / #5 (10-15s) 重排; 0-2s 一/二 byte-identical 跨角色 preserved (下游 ai_video_management 2s 切片输出在 v8 + v9 完全相同)。负向 11 项: drop no-camera-motion + no-cut 双重 ban; add slow-motion-only ≤45°/s + no-reversal + no-stop-and-go + no-spin-blur Kling-validator-aware bans。**项目落地**: 10 character md files (`ai_videos/mozun_chongsheng/characters/c{1..10}_*/c{N}_*.md`) 由 one-shot Python 脚本应用 v8 5-segment static dynamics → v9 5-phase slow-motion dynamics + 时长 7s → 15s + 镜头/动作/节奏/负向 lines swap + dialogue table 时段 column retime. 用户 review 后跑 script. 每角色现有 标志台词 #1 + #2 (088 → 091 → 092 已 plug 入) 留在 slots #4 + #5 with new time windows (now 5-10s / 10-15s). No code change to ai_video_management project (2s trim path 仍 slices byte-identical first 2s)。**用户后续手工步骤** (out-of-band): (a) 跑 patch script 改 10 character md files; (b) 重新渲染 1 份 turntable mp4 + 上传 Kling 做 validator empirical test (fail-fast 退路: v9.1 = drop orbit, push-in only 5s clip; 或 v8 = 7s static); (c) validator pass 后批量渲 10 份并上传; (d) 重新触发 ai_video_management 短角色合辑确认 0-2s 切片 byte-identical to v8。Risk acknowledged: v9 是 hypothesis, 退路两条已记录。**Prior bump:** 2026-05-18 00:15:44 — header bump for follow-up 024 (cross-project ripple from ai_video_management follow-up 091). **Character turntable rule #12.5 v6 → v8 (skip v7)**: Kling validator 拒收 v6 15s casting reel renders with `"the current video contains cuts or transitions, and no clear, complete character is detected"`. 诊断: v5/v6 + planned v7 全部在 0-2s 段做 fast 360° orbit (判 cut/transition + spin blurs character) + v6/v7 在 tail 加 push-in/pull-out/pan (同样判 transitions)。v7 (planned 7s 3-camera-move, follow-up 023 + 090) superseded before implementation; v8 = **7s 全程静态正面单镜头 single take**: 镜头零运动 (no orbit / push-in / pull-out / pan / tilt / zoom), 5 段 timed beats 全部「同机位同构图」开头, 角色仅自然呼吸 + 头部微动 + 说话。0-2s 段保 一/二 byte-identical 跨角色 truncate-compat 但**弃 360° silhouette pass** (incompatible with Kling 单 shot 硬契约; truncate output 现仅 frontal voice baseline)。2-7s 段 per-character: 三 + 自报姓名 / 标志台词 #1 baseline / 标志台词 #2 catch+peak+final-lock。**项目落地**: 10 character md files 一次性 Python 脚本应用 v6 7-segment → v8 5-segment + 镜头 6-move enum → static-camera declaration + 8-row table → 5-row + 时长 15s → 7s + 负向 v6 multi-camera bans drop + v8 single-shot bans add + v5 360°-related negatives cleanup。10/10 verified 0 残留 v5/v6 stale 标记 + character-specific dialogue 正确 plug 入。No code change to ai_video_management project. **用户后续手工步骤** (out-of-band): 重新渲染 10 份 turntable mp4 按 v8 7s static-camera prompt + 上传 Seedance/Kling 验证 validator 通过 + 重新触发 ai_video_management 短角色合辑 / ✂ 截到 2s 工具确认 0-2s 切片仍 self-sufficient (frontal full-body + 一/二). **Prior bump:** 2026-05-17 23:13:50 — header bump for follow-up 022 (cross-project ripple from ai_video_management follow-up 088). **Character turntable rule #12.5 v5 → v6**: 时长 4s → **15s casting reel** (Seedance reference upload ceiling 2026-05 中旬放宽到 ≥ 15s, 同 rule #12.10 v3 scene-walkthrough dim-comparable)。**保留** v5 的 0-2s 自包含契约 byte-identical 跨角色 (一 + 二 + 正面定场 + 360° 回正); ai_video_management 短角色合辑 `_CONCAT_SEGMENT_S = 2.0` + ✂ 截到 2s 按钮 仍 self-sufficient。**新增** 2-15s per-character casting reel: 6 个 camera moves (推近 / 反向 90° / 拉远 3/4 / 横向 pan 360° / 拉近 medium / 特写) + 4 句台词来自该角色 bible 自身 `## 标志台词或口头禅` 段 (3 句 verbatim plug into slots 4/5/7; 最短一句 reuse 作 slot 8 catch close) + 8-11s silent 表情 range capture + 13-15s 标志特征点 final-lock close-up。**项目落地**: 10 个 character md files (`ai_videos/mozun_chongsheng/characters/c{1..10}_*/c{N}_*.md`) 一次性 Python 脚本应用 v5 4-segment dynamics → v6 7-segment dynamics + 4-row table → 8-row table + 标题/文件说明/节奏/时长/负向 line uniform header edits; 每角色 3 句台词从其 bible 自身段提取 plug 入。10/10 文件 验证 0 残留 v5 4s dynamics opener ✓ + c1 沧冥/c10 司空玄 spot-checks 验证 character-specific dialogue 正确 plug 入。No code change to ai_video_management project. **用户后续手工步骤** (out-of-band): 按更新后的 c{N}.md 重新渲染 10 份角色 turntable mp4 (≤ 15s) 并上传 Seedance 验证 + 重新触发 ai_video_management shot-char 合辑 / ✂ 截到 2s 工具确认 0-2s 切片仍 self-sufficient。**Prior follow-up 021** (ep01 retrofit 收尾 follow-up 020；不引入新规则，仅 ep01/shot04-shot10 7 个 shot + ep01/shotlist.md 由 legacy 10s schema 扩到 15s — 沿用 020 的 acceptance trigger). **Prior bump:** 2026-05-17 19:28:26 — header bump for follow-up 019 (cross-project ripple from ai_video_management follow-up 078). **Character turntable rule #12.5 v4 → v5**: 时长 2.9s → 4s (Seedance reference upload ceiling relaxed; more on-screen seconds for identity capture) + Arabic "1, 2, 3" → 中文「一, 二, 三」 + 动作 beats 3 段 (0-1 / 1-2 / 2-2.9) → 4 段 (0-1 / 1-2 / 2-3 / 3-4) + **前 2s 自包含契约**: 「一」+「二」必须在 2.0s 前完成发声 + 镜头回正到正面，对齐 ai_video_management 短角色合辑 `_CONCAT_SEGMENT_S = 2.0` 切片边界 + ✂ 截到 2s 按钮的下游截取；3-4s 新增 1s 面部特写定格作为 face viewer final lock。**项目落地**: 10 个 character md files (`ai_videos/mozun_chongsheng/characters/c{1..10}_*/c{N}_*.md`) 内嵌 ```text``` fence + bottom 配音对照表 全部 byte-stable transformations 应用；section header + 文件说明 line 同步。c10_司空玄 此前已部分手工 migrate，仅补 section header + 文件说明 line 尾段。No code change to project. **用户后续手工步骤** (out-of-band): 按更新后的 c{N}.md → 视频 reference prompt 段重新渲染 10 份角色 turntable mp4 (≤ 4s) 并上传 Seedance 验证。**Prior follow-up 020** (用户："change all the shots to be in 15s length, this should give you more room for more details for each shot, both 台词，运镜and 动作"). **Shot duration 全部 10s → 15s** (per updated `CLAUDE.md § AI video rules` bullet 1 + `agent_refs/project/ai_video.md` 规则 #6 + 12.4 表第 13 行 + 12.4-B `时长` 行 — 三处一致表述 15 s default/target，老 12.4-B `Always 10s` 与 12.4-B Scope footer `set 时长: 15s` 的内部矛盾就此 resolve)。**台词 promoted to first-class shot field** — CLAUDE.md "Visuals only in v1" 收窄到 audio synthesis only (no TTS / no music)，dialogue 文本 always allowed (按 rule 12.4 三选一 内嵌硬字幕 / 后期软字幕 / 默剧)。**项目落地**: 50 shot mds (`ai_videos/mozun_chongsheng/episodes/ep{01..05}/prompts/shot{01..10}/shot{NN}.md`) Duration / 时长 全部 → 15s；动作 beats 延展至 0–15s (5–7 拍, 每拍 2–3 s)；镜头 + 运镜 ≥ 5 个 time window (≥ 1 个落在 10–15s 段)；台词 ≥ 1 行 (或显式 默剧)；2000-字 soft cap 保留 (优先 trim 反应 行)。5 个 shotlist.md 时长列同步 10s → 15s。**Kling 10s 渲染**: 15 s 用 2 个 back-to-back Kling call (≤10s + ≤5s)，中间用 shotNN_lastframe.png 做 mid-seam — 用户侧渲染步骤，schema 始终写 15s。不动: scene/character bibles / style_guide / arc_outline / publish.md / Seam-frame seedream prompt 内容。**Prior follow-up 018** (短剧故事 + 台词大师 review role) (短剧故事 + 台词大师 review role)。**新增工作流角色**：每个 shot / episode / shotlist item 经"短剧故事 + 台词大师"审阅，按 D1–D6（通俗易懂 / 信息量 / 节奏 / 角色声口 / 反转密度 / 名场面字数）+ S1–S5（钩落 / 情节链 / 反 anachronism / 视觉差 / 名字反差）评分，失败项以 inline patch list 输出（不写散文 review）。本 follow-up 在 `.claude/agent_refs/validation/ai_video.md` 加 validation level #9，在 `.claude/agent_refs/project/ai_video.md` 加 §12.4-D 准则；同时对 mozun_chongsheng 现有 50 shots 做首次 master pass，主要修复点：ep01/shot03 方鼎元 台词与 ep01/shot02 沧冥 雷同（S5）→ 用 太清掌教 ceremony cadence 区分；ep01/shot04 白月清 台词 forward-ref 璃月（S3 anachronism）→ 改 in-scope 目标。

**Prior regen 1:** 2026-05-13 10:30:00 — header bump for follow-up 017 (场景 reference 视频 prompt 从 v2 的 3.9s 五段极速 all-angle 改为 v3 的 15s walk-through 单视频：一条几何连续相机路径 + 5 个 canonical dwell（每个 ≥ 0.8s）+ 重要视角 frontload 在 t < 6s + 中间帧 buffet 概念。Rule #12.10 v2 → v3。仅触及场景 reference；角色 turntable rule #12.5 v4 / 2.9s 与 shot prompts rule #12.6 v2 未触及。)

**Prior follow-up 016:** 2026-05-10 18:15:00 — 把 follow-up 011 暂留为 placeholder 的三个未立档场景升级为完整 scene 文件（s7_山道平台 / s8_云海 / s9_识海；保持有效；本 follow-up 017 在此基础上 update 三者的 video reference 段从 3.9s 到 15s walk-through）。
**Prior follow-up 015:** 2026-05-10 17:09:02 — 角色 / 场景 reference 视频 prompt 12s → 2.9s + 角色 turntable "1,2,3" + 场景追加 video reference 段（rule #12.5 v4 保持有效；rule #12.10 NEW 已被 follow-up 017 amend 为 v3 / 15s walk-through）。
**Prior follow-up 014:** 2026-05-10 15:57:51 — folder-per-asset + media gitignore + webapp display（保持有效；本 follow-up 仅在 folder-per-asset 基础上更新 prompt 内容，不动 folder schema）。
**Prior follow-up 013:** 2026-05-10 15:41:33 — shot prompt ≤2000 字 + Markdown-style field-label 视觉渲染（保持有效）。
**Prior follow-up 012:** 2026-05-10 15:15:46 — photorealism + micro-details（保持在 character ref 内）。
**Prior follow-up 011:** 2026-05-10 14:59:30 — scenes 合并 + cN_/sN_ 命名约定（保持有效）。
**Prior follow-up 010:** 2026-05-10 14:46:48 — visual style + copy button + 人物台词（保持有效）。
**Prior follow-up 009:** 2026-05-10 14:08:54 — 合并 character files + Reference placeholders + 删 seam-frame embedded blocks（保持有效）。
**Prior follow-up 008:** 2026-05-10 13:44:00 — 面孔差异化 + 亚洲俊男靓女审美锚点（保持有效）。
**Prior follow-up 007:** 2026-05-10 13:25:13 — 单一自包含 shot 文件 (Shot context + 视频 prompt + Seam-frame still prompts 三段) — 第 ③ 段被本 follow-up 删除；前两段保留。
**Prior follow-up 006:** 2026-05-10 13:05:17 — per shot 合并 `_kling.md` + `_seedance.md` → 单文件（保持有效）。
**Prior follow-up 005:** 2026-05-10 11:34:24 — character ref 文件简化为单 video reference prompt（保持有效）。
**Prior follow-up 004:** 2026-05-10 10:36:01 — 角色 dual-prompt + 5 句台词 + Turntable 锁定字段（部分被 follow-up 005 覆盖：①号 image prompt 块已删；②号 video prompt + 5 句台词 + Turntable 锁定字段保持有效）。
**Prior follow-up 003:** 2026-05-10 09:50:45 — rule #12 model-agnostic 二件套抽象 + ~100 shot prompts 补 台词/节奏 字段 + 新增 scenes/ 复用场景层（保持有效）。
**Prior follow-up 002:** 2026-05-09 19:48:37 — 18-35 看似青春 + 锦缎绣纹 + 柳红袖不暴露 + 中文文件命名（保持有效）。
**Prior follow-up 001:** 2026-05-09 19:26:14 — 影视级真人写实 / cinematic / live-action 渲染样式锁定（保持有效）。

## Goal — 想做什么

制作一部 AI 驱动的中文 **仙侠 × 重生复仇** 短剧 **《魔尊归来》**（中文剧名已由用户在 stage 1 收尾时确认），约 60 集，每集 1.5 分钟（≈ 90 秒），总时长 ~ 90 分钟。每集以双 prompt（Kling + Seedance）驱动 AI 视频生成，配核心角色 Seedream 立绘做形象一致性锚点。

故事核心是一句话："**魔尊被正道伪君子联手镇压、转生于乞丐之身，从绝境一步步恢复实力，最终杀回正派大本营。**"

## Context — 设定与价值观

### 类型定位

- **赛道**：竖屏短剧（短视频平台主流形态：每集 ≤ 2 分钟、强情绪驱动、靠"爽"+"虐"快速勾人）。
- **题材**：仙侠（不是武侠）——有法宝、灵力、宗门、修为境界、神识空间等元素；同时融入"重生 / 转生"+"复仇 / 打脸"两大类型 trope。
- **道德底色**：反讽——所谓"正道"全是伪君子；男主魔尊不是单纯反派，而是被构陷的"反英雄"。这是与传统仙侠（《琉璃》《长月烬明》）正邪明晰路径的最大区别，更接近网络爽文 + 虐心叙事的混合。

### 视觉与美学（待 interview 收敛具体方向）

- 仙侠基础视觉语言：山门、剑气、雷劫、丹炉、灵力流光、长袍、发冠。
- 反派"正派伪君子"的双面性需要视觉化——明面"白衣胜雪 + 仙气飘飘"，背面"血色残忍"。
- 主角双形态：魔尊原形（黑袍 + 红瞳 + 魔气缠身）+ 乞丐转生形态（衣衫褴褛 + 神识压抑 + 双眼藏锋）。

### 输出规范（继承 `agent_refs/project/ai_video.md` 项目规则）

- 项目根目录：`ai_videos/mozun_chongsheng/`（路径英文 / 拼音；文件内容中文）。
- 多集制布局：`ai_videos/mozun_chongsheng/episodes/ep01/`、`ep02/`...`ep60/`，每集一个独立子目录承载 shotlist + Kling/Seedance prompts + 单集 publish.md。
- 共享资源在项目根：`characters/`（含每个角色的 Seedream 立绘 prompt + 锁定描述符）、`world.md`（世界观）、`style_guide.md`（视觉语言与配色）、`arc_outline.md`（60 集大纲）。
- 每个镜头 ≤ 15 秒；每个镜头同时给出 Kling prompt 与 Seedance prompt（双管线兼容）。
- 默认画幅 9:16（竖屏短剧）。
- v1 仅出"画面"，不出音频 prompt（音频后期人工 / 第三方 TTS 接入）。

## Desired outcome — 完工时应有的产出

### 项目级（`ai_videos/mozun_chongsheng/`）

- `README.md`（中文）—— 项目简介、剧情大纲、主创团队（如果有）、播出 / 渲染 / 后期 流程。
- `world.md`（中文）—— 世界观设定（修为体系、宗门版图、魔界 vs 正道、关键法宝 / 神识空间）。
- `style_guide.md`（中文）—— 视觉语言、配色、镜头法、字体、字幕规范。
- `arc_outline.md`（中文）—— 60 集大纲（每集一段一句话情节 + 关键转折点 + 高潮 / 虐点 / 爽点节奏）。
- `characters/{role_name}.md` + `characters/ref_images/{role_name}_seedream.md`（每个核心角色一份 Seedream 立绘 prompt + 一份角色档）。
- `publish/`（项目级发布元数据：标题候选、封面方案、平台适配模板）。

### 单集级（`ai_videos/mozun_chongsheng/episodes/epNN/`，N = 01..60）

- `episode.md`（中文）—— 本集剧情简介 + 上集回顾 + 下集预告 + 情绪节奏（钩子 / 转折 / 收尾）。
- `shotlist.md`（中文 + Markdown 表格）—— 本集所有镜头列表（shot_id / 时长 / 描述 / 角色 / 场景 / 配色）。每集约 6-12 个镜头（90 秒 ÷ 镜头时长）。
- `prompts/shot{NN}_kling.md` 和 `prompts/shot{NN}_seedance.md` —— 每个镜头一对 prompt 文件（双管线）。
- `publish.md`（中文）—— 本集发布元数据（标题、字幕、平台 hashtag、封面提示）。

### Pipeline 级（`specs/ai_video/mozun_chongsheng/`）

- 完整六阶段 spec-pipeline trail（user_input、interview、findings、final_specs、validation、changelog），用于支撑后续按集 / 按场景的 regen prompts。

## 用户已明确的硬约束（不需 interview 再问）

1. 集数：约 60 集（前后 5 集弹性）。
2. 单集时长：1.5 分钟左右（前后 30 秒弹性）。
3. 总剧情主轴：镇压 → 转生乞丐 → 恢复实力 → 反杀正派大本营。
4. 男主立场：原魔尊（被构陷），后转生（双重身份）。
5. 反派定位："正道伪君子"——非单一反派，而是一群虚伪的正派宗师。
6. task_type = ai_video，sub_type = novel；走 episodes/epNN/ 布局。
7. 渲染管线：Kling + Seedance 双 prompt + Seedream 立绘（继承 ai_video 工作流约定）。
8. 主语言：中文（叙事 + 字幕 + 角色台词）。

## 待 stage 2 interview 收敛的开放问题

为避免 stage 1 越权，以下问题不在本 revised prompt 中预设答案——留给 interview manager 团队提问：

1. **剧名**：使用《魔尊重生》临时标题，还是另起更具记忆点的中文剧名？
2. **女主 / 感情线**：是否设女主？若设，立场为正派良心 / 魔界遗孤 / 乞丐时认识的凡间少女 / 多女主？
3. **复仇 vs 救赎**：男主最终目标——纯复仇杀光正派 / 复仇后立新秩序 / 复仇过程中被女主感化转向救赎？
4. **修为体系**：参照"练气—筑基—金丹—元婴—化神—合体—大乘—渡劫"传统九阶，还是自创？
5. **正派伪君子的群像**：人数（5 / 7 / 9）、组织结构（联盟 / 宗主会 / 长老会）、伪君子的具体表现（双面 / 表里不一 / 以正道之名行私利）。
6. **关键道具 / 法宝**：是否有标志性法宝（如《琉璃》的鸿蒙炉、《沉香》的四瓣莲）？
7. **每集叙事节奏**：番剧式（每集独立钩子）/ 三集一组（短剧节奏组）/ 整段连续切分？
8. **60 集分卷**：是否分 4-6 大卷（如：序卷 → 觉醒卷 → 恢复卷 → 反击卷 → 终战卷）？
9. **视觉风格**：传统仙侠 / 暗黑仙侠（血色重）/ 国潮赛博 / 水墨写意？决定 style_guide.md 的核心调性。
10. **角色一致性**：核心角色立绘锁定到何种粒度（仅主角 / 主角 + 主要正派 / 全员）？
11. **典型镜头时长**：默认 5 秒 / 8 秒 / 10 秒 / 15 秒？决定每集镜头数与节奏密度。
12. **publish 平台**：抖音 / 视频号 / 快手 / 小红书 / B站 / YouTube Shorts —— 决定封面 + 标题模板。
13. **是否分两季**（30 集 + 30 集），或一季完结？

## Out of scope（v1 默认排除，除非 interview 明确加入）

- 音频 prompt 生成（v1 视觉 only，音频后期人工接入）。
- 真实剪辑 / 渲染 / 后期 —— pipeline 仅产出 prompt 文本与 Seedream 立绘 prompt；用户自行去 Kling / Seedance / Seedream 平台渲染。
- 多语言版本（v1 仅中文；英文 / 海外发行版作为 v2 follow-up）。
- 真人配音脚本与音乐版权 —— 不在 spec-pipeline 范围内。
- 与 `research/xianxia_storylines/` 中任何一部已有作品的直接复刻 / 改编（仅做风格与节奏借鉴）。

## 主线参考节奏（pipeline 内部假设，stage 4 spec 阶段会被 interview / research 矫正）

> 仅作为 stage 1 → stage 2 的"心理图景"，非定稿。

- **第一卷 · 镇压（约 5 集）**：开场即决战。魔尊与正派联军的最终战，被诱入阵法、神识被剐、本体被封。最后一刻一缕魂魄飞遁——
- **第二卷 · 乞丐重生（约 8 集）**：转生于一名底层乞丐少年身上。神识封闭、修为尽散，靠记忆与一丝魔气在凡间苟活。建立日常 + 隐忍线。
- **第三卷 · 觉醒（约 12 集）**：偶然机遇（古宅 / 法宝碎片 / 旧部相认 / 仇人路过）唤回部分修为。识破"正派伪君子"在乞丐城的搜捕行动。
- **第四卷 · 恢复（约 18 集）**：远走江湖，逐一寻回散落的本命法宝 / 神识碎片 / 旧部魔将。并在沿途收割小反派，建立"我已不是当年那只待宰的魔"。
- **第五卷 · 反击（约 12 集）**：直捣正派各分舵，逐一击破伪君子的根基与名声，揭穿真相。
- **第六卷 · 终战（约 5 集）**：杀回正派大本营。终战、揭幕、一句"当年你们怎么对我，今日我便十倍奉还"。开放或闭合结局留给 stage 2 interview 决定。

---

## Stage 1 用户决策记录（2026-05-09 16:42:05 收尾）

- task_name = `mozun_chongsheng` ✓ 已锁定。
- 中文剧名 = **《魔尊归来》** ✓ 已锁定（替代原临时标题《魔尊重生》）。
- 主线参考节奏（六卷 / 5+8+12+18+12+5）✓ 用户认可，作为 stage 2 interview 的起点；卷间集数尚可由 stage 2 进一步精调。
- 13 个 interview 开放问题 ✓ 用户未提前消除任何一个 → 全部带入 stage 2 由 interview team 处理。

Stage 1 完成。下一步：stage 2（interview，parent-direct）。
