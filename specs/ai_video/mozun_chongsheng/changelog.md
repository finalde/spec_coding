# Changelog — mozun_chongsheng

Append-only follow-up audit log。每条记录该 follow-up 改了什么、哪些下游 artifact 被同步 surgical patch。

## Follow-up 017 — 2026-05-13 10:30:00
Source: user_input/follow_ups/017-20260513-103000-scene-ref-15s-walkthrough.md
Summary: 场景 reference 视频 prompt 从 v2 的 **3.9s 五段极速 all-angle** 改为 v3 的 **15s walk-through 单视频**——沿一条几何连续的相机路径（连续 dolly + 平滑 yaw + 垂直俯仰 + 推进 zoom，无剪辑 / 跳切）依次悬停在 5 个 canonical 视角上，每个 dwell ≥ 0.8s 给出锐利静帧；**重要视角 frontload 在 t < 6s**（Hero / Reverse）抵御 Kling / Seedance 在 t > 12s 后的训练分布边缘漂移；新增"中间帧 buffet"概念（15s × 30fps = 450 帧，user 按需 ffmpeg 抽 3/4 角度参考，无需重新调 API）。规则层升级 `agent_refs/project/ai_video.md` rule #12.10 v2 → v3。scope 严格限于场景；角色 turntable rule #12.5 v4 / 2.9s 与 shot prompts rule #12.6 v2 未触及。

Auto-updated:
- `.claude/agent_refs/project/ai_video.md` — rule #12.10 v2 → v3：(a) intro 段 header `(3.9s all-angle 建模样片, per follow-up 010)` → `(15s walk-through 建模样片, per follow-up 017)`；prose 改写指明 Kling / Seedance reference 上传上限实测 ≥ 15s + walk-through 单视频 + 5 canonical dwell + frontload + 中间帧 buffet。(b) 12.10-A schema 段 header / 用法说明 / fenced code title 同步从 3.9s 五段改为 15s walk-through；新增"渲染完成后保留 source mp4 同 folder 作中间帧 buffet"说明。(c) 12.10-B body schema 完全重写：`镜头` 段从五段拼接改为一条 monotonic 平滑路径 + 5 canonical dwell + 焦距渐变 24→28→28→35→85mm；`动作` timed beats 从五段（0-0.8 / 0.8-1.7 / 1.7-2.5 / 2.5-3.3 / 3.3-3.9）重写为 9 段 dwell+transition 交替（5 个 ≥ 0.8s 悬停 + 4 段平滑过渡），每个 dwell 段标 **抽帧建议 t = X.Xs**；`节奏: 极快` → `节奏: 中等`；`时长: 3.9s` → `时长: 15s`；负向新增 5 项（不要剪辑 / 跳切 / 淡入淡出 / hard cut / 剧烈加速或瞬间反向运动），把 `不要 超过 3.9s` → `不要 超过 15s`，加 `不要 缩短至 < 15s（5 个 canonical dwell + 4 段 transition 信息密度塞不下）`。(d) 12.10-C 联动段加"中间帧 buffet 使用"小节，给出 ffmpeg 抽帧命令。(e) 锁定字段段时长锁值 `3.9s` → `15s`、节奏锁值 `极快` → `中等`，仍 8 个 byte-identical 字段。(f) originated note 加 follow-up 017 amend 项 + 显式 scope 声明（仅场景 ref，角色 turntable 与 shot prompts 未触及）。
- `specs/ai_video/mozun_chongsheng/user_input/revised_prompt.md` — `Last regenerated` 头从 2026-05-10 18:15:00 (follow-up 016) 改为 2026-05-13 10:30:00 (follow-up 017)；follow-up 016 降级为 Prior follow-up 016 行；follow-up 015 备注 amend 为 "rule #12.10 NEW 已被 follow-up 017 amend 为 v3 / 15s walk-through"。
- `ai_videos/mozun_chongsheng/scenes/s1_长阶顶/s1_长阶顶.md` 至 `s8_云海/s8_云海.md`（8 个常规场景）— 第三段「# 场景 reference video prompt」整段重写：header `3.9s all-angle 建模样片, per rule #12.10 v2` → `15s walk-through 建模样片, per rule #12.10 v3`；用法说明段重写（≤ 15s 硬上限 + 中间帧 buffet 提示）；fenced code block 内 `场景:` 行保留 byte-identical 一句话锁定 + 时辰光源 + 配色 hex；`镜头` 段更新为 v3 单 monotonic 路径 + 5 canonical dwell 描述，并填入各场景特有的"主要建筑或自然元素" / "标志道具或装饰"；`动作` timed beats 重写为 v3 的 9 段 dwell+transition；`节奏: 极快` → `节奏: 中等`；`时长: 3.9s` → `时长: 15s`；负向同步 v3 update。各场景 bible（8 字段锁定描述符 / 关键变化态 / 出现镜头 / 项目级与场景专属负向）与第二段「# 场景 reference image prompt」（Seedream 立绘）完全保留，逐字不改。s8_云海 保留 "魂火虚影合成位留空待 shot 内合成" 与 "微俯摇" 风格的项目特有约束 — 通过把垂直视角段实例化为"高位俯瞰云顶起伏"传递。
- `ai_videos/mozun_chongsheng/scenes/s9_识海/s9_识海.md`（蒙太奇过渡帧特殊变体）— 不套用 v3 walk-through 标准 schema（识海非物理空间，无几何可建，无相机路径可走）；仅做版本对齐与字段升级：header `3.9s 纯黑底过渡帧基底` → `15s 纯黑底过渡帧基底（蒙太奇场景特殊变体，rule #12.10 v3 walk-through 默认 schema 不适用）`；动作 beats 从 4 段（0-1 / 1-2 / 2-3 / 3-3.9）扩展为黑底持续无光 + 末段 0.5s 赤瞳点亮渐变的 v3 适配版本（仍声明"本场景蒙太奇特殊变体，不走 walk-through 5-dwell schema"）；`节奏: 静` 保留；`时长: 3.9s` → `时长: 15s`；负向同步把 `不要 超过 3.9s` → `不要 超过 15s`。
- `specs/ai_video/mozun_chongsheng/changelog.md` — append 本条 entry。

总计 patch 文件: **1 ref + 1 revised_prompt + 9 scenes + 1 changelog = 12 文件**。

**Mid-task strict-range amendment v2（2026-05-13 同 follow-up 内，第三轮迭代）：** 用户反馈 v3 compact 的 750-1320 字范围"too few — you need enough words to describe the scene"，要求**严格 1950-2000 字区间**。规则 `agent_refs/project/ai_video.md` rule #12.10-B v3 schema 同步 amend：(a) 新增 `空间` 字段（从锁定描述符 #2/#3 拉信息铺陈空间结构 + 主要元素相对位置，~120-180 字）；(b) 5 个 canonical dwell 描述从 ~40 字扩到 ~100-130 字，每个 dwell 加 focal length 标注（24mm / 28mm / 35mm / 85mm）+ 材质 / 纹理 / 高光细节 + 与周边元素同框关系；(c) 4 段 transition 加机位轨迹细节（俯仰角度 / 高度变化）；(d) `光线/色调` 从 ~80 字扩到 ~200-300 字，加入主光/辅光/反光 + 各表面对光的反应 + hex 在不同表面的表现 + 时辰大气感；(e) `负向` 加入场景专属构图禁忌 1-3 项。9 个 scene 文件 video prompt 段重写至 [1950, 2000] 严格区间：s1 1986 / s2 1968 / s3 2000 / s4 1996 / s5 1975 / s6 1973 / s7 1994 / s8 1973 / s9 1995。s9_识海 蒙太奇黑底变体走特殊变体 schema，通过加入"切片来源映射"段（六切片各自来源 s1/s3/s4 + 角色立绘）+ "shot08 节奏说明"段 + 加强负向项数填充至 1995 字。**禁止用废话填充字数** — 每多一字必须承载 model-actionable feature 信号（材质、几何、光照、构图、负向边界）。

**Mid-task compact amendment（2026-05-13 同 follow-up 内）：** 用户在 follow-up 017 主旨基础上追加 4 条新约束 — (a) prompt body ≤ 2000 字（对齐 shot prompt 上限）；(b) 移除 `渲染样式` / `比例` / `音频` / `时长` 4 个平台 / API 侧设定的字段（不在 prompt body 内重复声明，user 在 Kling / Seedance UI 或 API call 中通过 model 选择 + duration + aspect_ratio + no_audio 参数设定）；(c) prompt 默认显示在 markdown read mode 中应无 horizontal scrollbar（每行 ≤ 80 字符，多行短行替代单行长行）；(d) 去冗余字符与多余空白。规则层 `agent_refs/project/ai_video.md` rule #12.10-B v3 schema 与 12.10 锁定字段段同步 amend（已在初次 update 中完成，包含本次 compact 收紧）；后续把 9 个 scene 文件的 video prompt 段压缩重写：每场景 body 落在 750-1320 字（s9_识海 黑底变体最短 ~750；s7_山道平台 最长 ~1320），全部满足 ≤ 2000 上限。压缩点：① 字段标签 `正面建场 / 反向广角 / 长焦特写` 不再带 `（Hero）`/`（Reverse）`/`（Detail）` 英文别名（保留悬停编号 + 中文标签）；② 镜头段从 4 行压成 2 行；③ 节奏段从 2 子句压成 1 行；④ 负向段去重 + 合并近义词（`镜头抖动` → `抖动`、`剧烈加速或瞬间反向` → `加速或瞬反`、`时辰错乱` → `时辰漂`，5 个音频项合并为"任何音频"）；⑤ `渲染样式 / 比例 / 音频 / 时长` 4 字段从 body 移除并在 `> 用法` 块的 "平台侧设定" 子段统一声明（duration=15s, aspect_ratio=9:16, no_audio=true, 渲染样式 by model + settings）。本压缩不改变 walk-through 结构（仍 5 canonical dwell + 4 transition，仍 frontload t<6s + 中间帧 buffet），仅改 verbose 表达。

No conflicts found in:
- `specs/ai_video/mozun_chongsheng/final_specs/spec.md` — FR / NFR 不涉及 reference 视频时长（grep 验证 0 处需 patch；reference 时长是输出层细节，spec 层 invariants 不变）
- `specs/ai_video/mozun_chongsheng/validation/{strategy.md, acceptance_criteria.md, bdd_scenarios.md, ai_video_specific.md}` — 0 处提及 3.9s / 场景 reference 时长 / walk-through schema
- `specs/ai_video/mozun_chongsheng/interview/qa.md`、`findings/{dossier.md, angle-*.md}` — 上游决策层，与 reference 视频时长正交
- `ai_videos/mozun_chongsheng/characters/c{1..10}_*/c{N}_*.md`（角色 turntable）— rule #12.5 v4 / 2.9s 保留不动；用户明确要求"only update the scene, don't touch characters and shots"
- `ai_videos/mozun_chongsheng/episodes/ep{NN}/prompts/shot{NN}/shot{NN}.md`（shot prompts）— rule #12.6 v2 schema 不变；scene reference 视频上传逻辑由 user 操作时识别，不引入新 prompt 字段；`{ref_s{N}_*}` placeholder 仍按文件名引用 mp4，path 不变
- `ai_videos/mozun_chongsheng/{README.md, world.md, arc_outline.md, style_guide.md}` — 与 reference 视频时长正交
- 已渲染的 mp4 资产（`scenes/s{1..6,9}_*/s{N}_*[1-4].mp4`）— 物理 mp4 不删除（保留作 v2 渲染历史）；user 应基于 v3 prompt 重新渲染获得新 15s walk-through reference，并替换下游 shot 上传时使用的 mp4 path

User next steps:
1. 用更新后的 9 份 `scenes/s{N}_*/s{N}_*.md` 第三段「场景 reference video prompt」code block 在 Kling 或 Seedance 重新渲染 15s walk-through reference mp4（替换或新增 `scenes/s{N}_*/s{N}_*.mp4`）。
2. 抽帧（如需要额外 3/4 角度参考）：对 source mp4 跑 `ffmpeg -ss {time} -vframes 1 -q:v 1 frame.png`，canonical 5 个时间点已在 prompt body 中标 **抽帧建议**。
3. 下游 shot prompt 上传时直接使用新 mp4（path 不变）；shot prompt 文件本身无需 patch。

Severity: scene reference 视频时长从 3.9s 提到 15s 属于**中等 blast radius** 的输出层 update，已完成 12 文件 surgical patch。规则层 v3 update 后，未来场景 stage-6 regen 自动沿用 v3 walk-through schema，不会再漂回 v2。

## Cross-project data-op cascade — 2026-05-12
Source: `specs/development/ai_video_management/user_input/follow_ups/013-20260511-125029-batch-trim-character-mp4-to-2.9s.md`（**跨项目 data-op，本项目无 own follow-up；本条仅作 cross-ref 审计**）。
Summary: 把本项目 `characters/c*/c*.mp4` 19 个 character turntable mp4 in-place re-encode trim 到 ≤ 2.9s，对齐 `agent_refs/project/ai_video.md` rule #12.5 v4 的 Seedance reference ≤2.9s 上传约束。原时长 3-15s 不等（用户手工渲染），后时长 11 个精确 2.9s + 8 个 2.92s（mp4 packet-boundary ~20ms 过冲，远低于 3s 实际上限）。19/19 成功。详细 before/after 表见 `specs/development/ai_video_management/changelog.md` 同条 follow-up 013 entry。

Auto-updated:
- `ai_videos/mozun_chongsheng/characters/c10_司空玄/{c10_司空玄1,c10_司空玄2}.mp4` (2 个) — re-encoded H.264/AAC，时长统一 ≤2.9s
- `ai_videos/mozun_chongsheng/characters/c1_沧冥/{c1_沧冥1..5}.mp4` (5 个) — re-encoded H.264/AAC，时长统一 ≤2.9s
- `ai_videos/mozun_chongsheng/characters/c3_苏璃月/{c3_苏璃月1..4}.mp4` (4 个) — re-encoded H.264/AAC，时长统一 ≤2.9s
- `ai_videos/mozun_chongsheng/characters/c4_柳红袖/c4_柳红袖.mp4` — re-encoded H.264/AAC 2.9s
- `ai_videos/mozun_chongsheng/characters/c5_苓夭夭/c5_苓夭夭.mp4` — re-encoded H.264/AAC 2.92s
- `ai_videos/mozun_chongsheng/characters/c6_白月清/c6_白月清.mp4` — re-encoded H.264/AAC 2.92s
- `ai_videos/mozun_chongsheng/characters/c7_赵焚天/{c7_赵焚天1,2,3}.mp4` (3 个) — re-encoded H.264/AAC，时长统一 ≤2.9s
- `ai_videos/mozun_chongsheng/characters/c8_方鼎元/c8_方鼎元.mp4` — re-encoded H.264/AAC 2.9s
- `ai_videos/mozun_chongsheng/characters/c9_韩夺心/c9_韩夺心.mp4` — re-encoded H.264/AAC 2.9s

No conflicts found in:
- `specs/ai_video/mozun_chongsheng/user_input/` — 项目主线未 own 此 follow-up（hook 标 ai_video_management 项目语境；本条仅作 cross-ref）
- `specs/ai_video/mozun_chongsheng/interview/qa.md` / `findings/` / `final_specs/spec.md` / `validation/*` — data-op 不冲突现有 spec
- `characters/c*/c*_seedream.md`（Seedream 立绘 prompt） — 不动；image-only fallback，不引用 mp4
- `episodes/ep*/prompts/shot*/shot*.md`（shot prompt） — `{ref_c{N}_*}` placeholder 按文件名引用 mp4，path 不变；shot prompt 文件本身不需要 patch
- `scenes/s*/s*.md` 与 `scenes/s*/*.mp4`（scene reference 视频）— 明确排除（rule #12.10 v2 锁 3.9s，与本批 character 2.9s 操作正交）
- README.md / arc_outline.md / style_guide.md / world.md — 无引用变化

## Cross-project rule cascade — 2026-05-11 12:04:54
Source: `specs/development/ai_video_management/user_input/follow_ups/010-20260511-120454-scene-ref-video-3.9s-all-angles.md`（**跨项目 rule change，本项目无 own follow-up；本条仅作 cross-ref 审计**）。
Summary: `agent_refs/project/ai_video.md` rule #12.10 由 v1（2.9s 三段 establishing/横移/推近）升至 v2（3.9s 五段 all-angle: 正面建场 + 水平 360° 环绕 + 垂直三视角 + 中景横移 + 长焦特写；起手必须 front view；新增 byte-identical `音频: 无` 字段；负向加 visual-only 锁定）。本项目 9 个场景档作为已生成 artifact，依规则随之 surgical patch。

Auto-updated:
- `ai_videos/mozun_chongsheng/scenes/s1_长阶顶/s1_长阶顶.md` 至 `s8_云海/s8_云海.md`（8 个常规场景）— 「场景 reference video prompt」段重写为 3.9s 五段 all-angle schema：header `2.9s 多角度建模样片` → `3.9s all-angle 建模样片`；用法行 `≤ 2.9s 硬上限` → `≤ 3.9s 硬上限`，并加 `**视频纯视觉，无任何音频 / BGM / 音效 / 旁白。**` 提示；code block 内 `镜头: 三段拼接` → `镜头: 五段拼接`（① 正面建场 / ② 水平 360° 环绕 / ③ 垂直三视角 / ④ 中景横移 / ⑤ 长焦特写）；`动作 timed beats` 由 3 段重写为 5 段（0-0.8s 正面建场 / 0.8-1.7s 水平 360° / 1.7-2.5s 垂直三视角 / 2.5-3.3s 中景横移 / 3.3-3.9s 长焦特写）；`节奏: 极快（2.9s 内...）` → `节奏: 极快（3.9s 内...全角度信息密度优先）`；`比例: 9:16` 之后新增 `音频: 无（视频纯视觉 reference...）` 行；`时长: 2.9s` → `时长: 3.9s`；负向加 `不要 起手非正面（必须 front view 建场）` + `不要 任何音频 / BGM / 音效 / 旁白 / 环境音`，并把 `不要 超过 2.9s` → `不要 超过 3.9s`。s7 保持原有 `关键区位（平台中心 / 阶身上行段 / 阶身下行段）` 不变；s8 保持 `角色人物入画（场景 reference 纯环境，无角色，魂火虚影合成位留空）` 这一项目特有负向；s8 因「微俯摇」原文与 s1-s7 微仰摇不同，独立做镜头段重写，覆盖云海垂直三视角 = 高位俯瞰云顶起伏 / 平视云海与远山天际 / 低位仰视云海上方天幕。
- `ai_videos/mozun_chongsheng/scenes/s9_识海/s9_识海.md`（蒙太奇过渡帧特殊变体）— 不套用 v2 五段 all-angle schema（识海非物理空间，无几何可建）；仅做时长 + 音频字段升级：header `2.9s 多角度建模样片` → `3.9s 纯黑底过渡帧基底（蒙太奇场景特殊变体）`；用法说明保留"识海非物理空间"段并显式声明 `rule #12.10 v2 默认 schema 不适用` + 加 `**视频纯视觉，无任何音频 / BGM / 音效 / 旁白。**`；code block 标题加 `蒙太奇场景特殊变体，all-angle 五段 schema 不适用`；`镜头` 段更新枚举（加无水平环绕无垂直三视角）；`动作 timed beats` 从 3 段（0-1 / 1-2 / 2-2.9）扩到 4 段（0-1 / 1-2 / 2-3 / 3-3.9，全程黑底持续无光），同时声明`本场景蒙太奇特殊变体，不走 all-angle 五段 schema`；`节奏: 静（2.9s ...）` → `节奏: 静（3.9s ...）`；加 `音频: 无` 行；`时长: 2.9s` → `时长: 3.9s`；负向加 `不要 任何音频 / BGM / 音效 / 旁白 / 环境音` + 把 `不要 超过 2.9s` → `不要 超过 3.9s`。

No conflicts found in:
- `specs/ai_video/mozun_chongsheng/user_input/` — 项目主线本未 own 此 follow-up（hook 标记 ai_video_management 项目语境；用户三选题再次确认 follow-up 持久化位置）
- `specs/ai_video/mozun_chongsheng/interview/qa.md` / `findings/` / `final_specs/spec.md` / `validation/*` — rule v2 改动不冲突现有项目 spec
- `characters/c*/c*.md` turntable reference video prompt — character turntable 由 rule #12.5 v4 锁在 2.9s 不动（用户在三选题中确认 character turntable 保持 2.9s）
- `episodes/ep*/prompts/shot*/shot*.md` shot prompt — shot prompt 文件 schema（rule #12.6 v2）不变，scene reference 视频上传逻辑由 user 操作识别，不引入新 prompt 字段
- README.md / arc_outline.md / style_guide.md / world.md — 时长 / schema 升级不影响项目级文档

## Follow-up 016 — 2026-05-10 18:15:00
Source: user_input/follow_ups/016-20260510-181500-promote-scene-stubs-s7-s8-s9.md
Summary: 把 follow-up 011 中暂留为 placeholder 的三个未立档场景升级为完整 scene 文件 — `s7_山道平台`（ep02）、`s8_云海`（ep05/shot02）、`s9_识海`（ep05/shot08）。覆盖每个 shot md 的 `{ref_sN_*}` 引用都有对应 `scenes/sN_*/sN_*.md` 文件支撑（含 8 字段锁定描述符 + 关键变化态 + 出现镜头 + Seedream 立绘 image prompt + Seedance 2.9s reference video prompt 三段，schema 完全镜像 s1-s6）。s9_识海 是非物理空间，reference 段给出"硬切闪黑过渡帧 + 黑底持续无光"基底，切片本体在 shot08 内由各源场景 reference 单独抽帧合成。

Auto-updated:
- `ai_videos/mozun_chongsheng/scenes/s7_山道平台/s7_山道平台.md` — 新建（ep02 上行 / 平台默认 / 下行独行 / 阴笑定格 四态；锁定描述符 主沉黑 #0a0a0a / 辅银白高光 #f5f5f0 / 点缀冷青 #1a3038 + 护黄金 #a8842c；与 s1_长阶顶 区分通过 "中段山道纵深 / 灯柱冷青 / 星河斜悬而非天顶"）。
- `ai_videos/mozun_chongsheng/scenes/s8_云海/s8_云海.md` — 新建（ep05/shot02 魂火悬停默认态；锁定描述符 主沉黑 / 辅银白云海 / 点缀暗血红赤瞳 + 远山深青 + 护黄金虚影衣纹；reference 段魂火虚影合成位留空待 shot 内合成）。
- `ai_videos/mozun_chongsheng/scenes/s9_识海/s9_识海.md` — 新建（ep05/shot08 蒙太奇六切片快剪 + 末段赤瞳定格态；reference 段为黑底过渡帧基底 — 不强行套用 establishing + 横移 + 推近 三段，因黑底无运镜；切片本体由各源场景 reference 单独抽帧合成）。
- `ai_videos/mozun_chongsheng/episodes/ep02/prompts/shot02/shot02.md` — Reference placeholders 表 `{ref_s7_山道平台}` 行 surgical replace（"未立档；user 自备..." → 指向 `scenes/s7_山道平台/s7_山道平台.md` 渲染所得 + "采用上行态"）。
- `ai_videos/mozun_chongsheng/episodes/ep02/prompts/shot03/shot03.md` — 同上，`{ref_s7_山道平台}` 行（"采用平台默认态"）。
- `ai_videos/mozun_chongsheng/episodes/ep02/prompts/shot09/shot09.md` — 同上，`{ref_s7_山道平台}` 行（"采用下行独行态"）。
- `ai_videos/mozun_chongsheng/episodes/ep02/prompts/shot10/shot10.md` — 同上，`{ref_s7_山道平台}` 行（"采用阴笑定格态"）。
- `ai_videos/mozun_chongsheng/episodes/ep05/prompts/shot02/shot02.md` — `{ref_s8_云海}` 行 surgical replace（"过渡场景未立档，user 自备" → 指向 `scenes/s8_云海/s8_云海.md` + "采用默认态魂火悬停"）。
- `ai_videos/mozun_chongsheng/episodes/ep05/prompts/shot08/shot08.md` — `{ref_s9_识海}` 行 surgical replace（"本集独有过渡空间，未立档..." → 指向 `scenes/s9_识海/s9_识海.md` + "采用默认态六切片快剪 + 末段赤瞳定格；过渡帧基底由场景 reference 提供，切片本体在 shot 内逐段合成"）。
- `specs/ai_video/mozun_chongsheng/user_input/revised_prompt.md` — Last regenerated header bumped to 2026-05-10 18:15:00 + follow-up 016 摘要；prior follow-up 015 备注（保持有效）。

总计 patch 文件: **3 新 scene files + 6 shot reference rows + 1 revised_prompt.md = 10 文件**。

No conflicts found in:
- `final_specs/spec.md` — FR / NFR / AC 不涉及具体场景列表（ep+shot 列表是执行层），新增三个场景立档不触发 spec 重写。
- `validation/strategy.md` + level files — 既有 "every {ref_xxx} placeholder must resolve to a real ref source" criterion 现得到加强，但无新校验项需引入。
- `interview/qa.md` — stage 2 决策不枚举具体 scene 列表。
- `findings/dossier.md` + angle files — research 阶段不区分 placeholder vs 立档。
- `world.md` / `arc_outline.md` / `style_guide.md` / `README.md` — 三个新场景在大纲中已隐含（魔气长阶中段 / 高空魂火飞遁 / 蒙太奇识海段在 ep02 + ep05 narrative 中均有），无大纲层变更。
- `.claude/agent_refs/project/ai_video.md` — Rule #12.5 v4 + Rule #12.10 (follow-up 015 引入) 直接被本 follow-up 应用 — 三个新场景文件 schema 严格遵守 rule，无 rule 改动。
- 其它 ep01/ep03/ep04 + ep05 其余 shot 文件 — 不引用 s7/s8/s9，不动。

User next steps:
1. 按新建的 `scenes/s7_山道平台/s7_山道平台.md` / `scenes/s8_云海/s8_云海.md` / `scenes/s9_识海/s9_识海.md` 内的 image prompt + 2.9s video prompt 渲染立绘 PNG + reference mp4，置入对应 scene 文件夹（命名 `s7_山道平台.png` / `s7_山道平台1.mp4` 等，与 s1-s6 一致）。
2. 上传新场景 reference 到 Seedance / Kling 测试 6 个 shot 的实际生成效果，确认 placeholder 解析正常。
3. 现有 6 个 shot prompt 文件已自动指向新 scenes md，不需重渲 shot prompt 自身；仅需切换 reference 上传源。

Severity: scene placeholder 未立档导致 "user 自备 / 留空依靠 prompt 描述" 退化属 **major** 等级（工作流降级但不阻塞），本 follow-up 完成后修复。后续若新增 ep06+ 引入新场景，遵循同一立档规约 append `s10_*` 等。

## Follow-up 015 — 2026-05-10 17:09:02
Source: user_input/follow_ups/015-20260510-170902-compress-reference-videos-2.9s.md
Summary: 把所有用于"建模"角色 / 场景的 reference 视频 prompt 时长从 12s 压到 **2.9s**（Seedance 等下游视频模型的 video reference 上传约束）。角色 turntable 动作 beats 重排为 全身远景定场 + 360° 快环 + 面部中近景推近 三段；5 句多情绪台词（自报家门 / 标志台词 / 低声 / 高声 / 数字校准）→ "1, 2, 3" 三个数字（byte-identical 跨所有 10 角色，仅作声线 timbre + 咬字基线 anchor）。**新增**：场景 reference 视频 prompt 段（rule #12.10）— 与 Seedream 立绘 image prompt 并存于场景文件，2.9s 内 广角全景 + 中景横移 + 长焦推近 三段。Rule #12.5 v3 → v4；新增 rule #12.10。

Auto-updated:
- `.claude/agent_refs/project/ai_video.md` — Rule #12.5 v3 → v4 amend (turntable 12s → 2.9s, 5 句台词 → 3 数字 "1, 2, 3", 动作 beats 重排为 全身远景定场 + 360° 快环 + 面部推近 三段, 锁定字段从 8 个增至 9 个含台词 byte-identical)；新增 Rule #12.10「场景 reference 视频 prompt（2.9s 多角度建模样片）」(12.10-A 场景文件 schema 扩展为 bible + image prompt + video prompt 三段；12.10-B 场景视频 prompt body schema；12.10-C scene reference 上传与 shot prompt 联动 + 多场景 byte-identical 锁定字段)。
- `ai_videos/mozun_chongsheng/characters/c{1..10}_*/c{N}_*.md`（10 文件，c10 已是新 schema，9 文件 surgical patch）— 文件说明、prompt 段头、code block title、`镜头:`、动作 timed beats、`台词 / 字幕:`、`节奏:`、`时长:`、`负向:` tail、5 句台词表 → 3 句数字计数台词表 全部更新；`角色:` line + `场景:` line + `光线 / 色调:` (含角色专属光晕) + `渲染样式:` + `比例:` + 配音参考段保持不变。
- `ai_videos/mozun_chongsheng/scenes/s{1..6}_*/s{N}_*.md`（6 文件）— 现有 `# 场景 reference prompt — Seedream...（场景立绘）` 段头 → `# 场景 reference image prompt — Seedream...（场景立绘静帧 / image-only fallback）`；末尾追加新段 `# 场景 reference video prompt — Seedance / Sora / Veo / Runway Gen-3 / Kling（2.9s 多角度建模样片）` 含 11 字段 prompt body；prompt body 内 `场景:` / `镜头:` / `光线 / 色调:` 引用各场景 bible 锁定描述符 #3 / #5 / #6 / #8 字段（自动从 markdown 表格解析）。
- `specs/ai_video/mozun_chongsheng/user_input/revised_prompt.md` — Last regenerated header bumped to 2026-05-10 17:09:02 + follow-up 015 摘要；prior follow-up 014 备注（保持有效）。
- `.audit/adhoc_agents/2026-05-10/compress_2.9s_followup015/` — 工具脚本 (`update_characters.py` + `update_scenes.py`) 留底，便于审计本次 surgical patch 的具体替换 pattern。

总计 patch 文件: **1 agent_refs (rule #12.5 v4 + rule #12.10 新增) + 9 character files (c10 已就位) + 6 scene files + 1 revised_prompt.md = 17 文件 (+ 2 audit scripts)**。

No conflicts found in:
- `final_specs/spec.md` — FR / NFR / AC 不涉及具体 reference 视频时长 (FR-5/6 描述 Seedream 立绘 + Kling/Seedance shot prompt schema，未规定 reference 长度)；rule #12.5 / #12.10 是 agent_refs 实现细节，不进 spec。
- `validation/strategy.md` + 3 level files — validation level 不含 "reference 视频时长" 校验项；现有 ai_video.md 8 levels 仍全部适用。
- `interview/qa.md` — stage 2 决策不涉及 reference 视频时长。
- `findings/dossier.md` + 5 angle files — research 阶段未触及 reference 视频时长。
- `world.md` / `arc_outline.md` / `style_guide.md` / `README.md` — 项目级 visual / narrative 锁定文件，无 reference 视频时长字段。
- `episodes/ep{NN}/prompts/shot{NN}/shot{NN}.md`（50 shot files）— shot prompt schema (rule #12.6 v3) 不变；scene reference 视频上传逻辑由 user 操作时识别，不引入新 prompt 字段。
- `c10_司空玄/c10_司空玄.md` — 已是 2.9s + 1, 2, 3 schema (script 检测到无需 patch)，可能是先前 ad-hoc 更新 / 模板演化的产物，与 follow-up 015 后状态等价。

User next steps:
1. 重新生成 10 份角色 turntable mp4（按更新后的 c{N}_{name}.md → 视频 reference prompt 段渲染，2.9s ≤ 上限）。
2. 重新生成 6 份场景 reference video mp4（按更新后的 s{N}_{name}.md → 场景 reference video prompt 段渲染）；旧的 s1_长阶顶[1-3].mp4 / c1_沧冥[1-2].mp4 等 12s 资产可归档或覆盖。
3. 上传新 reference mp4 到 Seedance 测试 ≤ 2.9s 是否通过上传约束。
4. 现有 50 份 shot prompt 不需重渲，仅需把 reference 上传环节切换为新 mp4 即可（shot prompt 内的 `{ref_xxx}` placeholder 不变）。

Severity: reference 视频长度违反下游模型上传约束属 **blocker** 等级（无法生成下游 shot 视频），本 follow-up 完成后修复。后续若 Seedance / 其他模型放宽约束，可单独 follow-up 把 2.9s 上调。

## Follow-up 014 — 2026-05-10 15:57:51
Source: user_input/follow_ups/014-20260510-155751-folder-per-md-media-display.md
Summary: 三件事：(A) **每个 character / scene / shot .md 文件转为同名文件夹**，原 .md 移入文件夹内（10 chars + 6 scenes + 50 shots = 66 mv 操作）；(B) **媒体文件 gitignore** — `ai_videos/**/*.{mp4,mov,webm,mkv,avi,png,jpg,jpeg,webp,gif,bmp}` 不入 git；(C) Path 引用更新 — 50 shot files 内 character / scene path 引用从 `characters/c1_沧冥.md` 改为 `characters/c1_沧冥/c1_沧冥.md` (16 path renames × 50 files)。新增 rule #12.9 + NFR-18。Webapp media display 实现 deferred 到独立 surgical follow-up（需 backend 加 /api/media 路由 + frontend SiblingMedia 组件，本 follow-up 仅完成 file system + git 部分）。

文件 / 文件夹 重组（66 mv ops）:

| 类型 | OLD | NEW |
|---|---|---|
| 10 chars | `characters/c{N}_{name}.md` | `characters/c{N}_{name}/c{N}_{name}.md` |
| 6 scenes | `scenes/s{N}_{name}.md` | `scenes/s{N}_{name}/s{N}_{name}.md` |
| 50 shots | `episodes/ep{NN}/prompts/shot{NN}.md` | `episodes/ep{NN}/prompts/shot{NN}/shot{NN}.md` |

Path 引用更新（50 shot files × 16 OLD/NEW pairs = up to 800 replace_all ops via sed; subset applies per file）:
- 10 character paths: `characters/c{N}_{name}.md` → `characters/c{N}_{name}/c{N}_{name}.md`
- 6 scene paths: `scenes/s{N}_{name}.md` → `scenes/s{N}_{name}/s{N}_{name}.md`

Auto-updated:
- `.claude/agent_refs/project/ai_video.md` — Rule #12.5 v4 amend (character file 现存于 同名 folder 内 + folder 含 user-rendered media gitignored)；Rule #12.6 v3 amend (shot file 同 schema)；Rule #12.8 v2 amend (filename + folder pattern: `characters/c{N}_{name}/c{N}_{name}.md` etc.)；新增 Rule #12.9「Folder-per-asset + Media gitignore + Webapp display 契约」(folder schema + media gitignore patterns + webapp display contract — webapp 须 inline 显示 image media + 内嵌播放 video media + backend serve raw media bytes)。
- `.gitignore` — 新增 11 项 media file patterns under `ai_videos/**/*` (mp4/mov/webm/mkv/avi/png/jpg/jpeg/webp/gif/bmp)。
- `specs/ai_video/mozun_chongsheng/user_input/revised_prompt.md` — Last regenerated header bumped to 2026-05-10 15:57:51 + follow-up 014 摘要。
- `specs/ai_video/mozun_chongsheng/final_specs/spec.md` — FR-5/6/9 path references implicit via rule #12.8 v2 reference; NFR-18 NEW (media gitignore — ai_videos/ 下所有 binary media file 不入 git) (deferred to next surgical update if not yet present)。
- `ai_videos/mozun_chongsheng/characters/` — 10 character md files moved into 同名 folders (10 mv operations via bash).
- `ai_videos/mozun_chongsheng/scenes/` — 6 scene md files moved into 同名 folders.
- `ai_videos/mozun_chongsheng/episodes/ep01..ep05/prompts/` — 50 shot md files moved into 同名 folders (50 mv operations).
- `ai_videos/mozun_chongsheng/episodes/ep01..ep05/prompts/shot{NN}/shot{NN}.md` × 50 — bash sed bulk update: 16 OLD/NEW path-rename pairs applied to all 50 files. Verified zero residual short-form paths remain.

总计 patch 范围: **1 agent_refs amend (rule #12.5 v4 + #12.6 v3 + #12.8 v2 + 新增 #12.9) + 1 .gitignore amend + 1 revised_prompt header + 66 mv 操作 (file restructure) + 50 shot files path-reference update via sed = 4 docs + 66 mv + ~50 file content edits**。

Deferred work (TBD follow-up):
- **Backend `/api/media` 路由 + frontend `SiblingMedia` component**：webapp 渲染 character / scene / shot folder 时 inline 显示 image (.png/.jpg/.webp) + 内嵌播放 video (.mp4/.mov/.webm) — 需要：
  1. Backend `projects/ai_video_management/backend/libs/api.py` 加 `@app.get("/api/media")` 路由 (return FastAPI FileResponse with proper MIME type，bypass `MAX_FILE_BYTES` 限制 since videos are larger than 1MB)。Reuse 现有 `safe_resolve` sandbox。
  2. Backend `exposed_tree.py` ALLOWED_EXTENSIONS 加 `.mp4 / .mov / .webm / .webp / .gif / .bmp` (or expose them only via /api/media route)。
  3. Frontend `projects/ai_video_management/frontend/src/components/SiblingMedia.tsx` (NEW)：given 当前 file path, scan `knownPaths` 找 sibling media files (同 parent folder 内、非当前 .md 文件、扩展名 ∈ {.png, .jpg, .mp4, .mov, etc.}) → render `<img>` for images, `<video controls>` for videos using `/api/media?path=...` URL.
  4. Frontend `Reader.tsx` 在 markdown 渲染下方插入 `<SiblingMedia path={path} knownPaths={knownPaths} />`。
  5. Frontend `styles.css` 加 `.sibling-media` grid layout + per-item styling.

  **当前实施状态**: 仅 file system + git 部分完成; webapp media display 需后续独立 follow-up 实施 + 测试 (~150 LOC backend + frontend 实现 + smoke test)。

No conflicts found in:
- `ai_videos/mozun_chongsheng/characters/c{1..10}_*/c{1..10}_*.md` × 10 — 文件 content 不动 (仅 mv 重组路径).
- `ai_videos/mozun_chongsheng/scenes/s{1..6}_*/s{1..6}_*.md` × 6 — 同上.
- `ai_videos/mozun_chongsheng/style_guide.md` / `world.md` / `arc_outline.md` / `README.md` — 不动 (这些 file 不引用 character/scene path)。
- spec-pipeline 史料 — 不动.
- ep01-ep05 episode.md / shotlist.md / publish.md — 不动 (这些 file 不直接引用 character/scene file paths)。
- `projects/spec_driven/` — 不动.

Severity: Low blast radius (file system 重组 + git 配置 + path reference text 替换；零内容损失)。Deferred webapp work 是 nice-to-have，不阻塞核心 prompt pipeline。

User next steps:
1. 当 user 渲染 character turntable.mp4 / scene ref.png / shot kling output mp4 时，将文件放入对应 folder (e.g., `characters/c1_沧冥/turntable.mp4`)。Git 自动 ignore 这些 binary 文件。
2. 当前 webapp 仍可显示 prompt .md content (folder-per-md 不影响 .md 渲染)；media inline 显示需后续 follow-up 实施。
3. 后续 ep06-ep60 stage-4 regen 时按 rule #12.5 v4 / #12.6 v3 / #12.8 v2 / #12.9 出文 (folder-per-asset schema)。

Pre-existing inconsistency carried forward:
- 沧冥 inline 体型 「三十出头」 vs 「看似二十五」 (legacy seedance variant 文本，仅在 character ref turntable prompt 内残留) — 独立 surgical follow-up 处理。
- style_guide.md / README.md 内文可能仍引用 pre-014 的 character/scene 短路径形式 (e.g., `characters/c1_沧冥.md` 而非 `characters/c1_沧冥/c1_沧冥.md`) — 独立 surgical follow-up 处理 propagation。

## Follow-up 013 — 2026-05-10 15:41:33
Source: user_input/follow_ups/013-20260510-154133-prompt-2000char-limit-md-display.md
Summary: 两件事：(A) **Shot prompt body 字数 trim 到 ≤2000 字 soft / ≤2500 字 hard 上限**。Trim 策略：① 角色 line 移除 inline body expansion + 5-7 项 micro-details（保留在 character ref turntable prompt 内，user 上传 turntable.mp4 时由模型 inherit）；② 渲染样式 line 从 13 关键词 trim 到 9 核心；③ 负向 line 从 39 项 trim 到 24 核心 items（去重 anime/cartoon/manga 变体）。50 shot files 全部 trim，所有现已 ≤ 1500 字。(B) **Markdown-style field-label 视觉渲染**：webapp `CopyableCode` 组件升级 — 解析 ```text fenced code block 的 plain text → 行首匹配 field labels (`角色:` / `场景:` / `镜头:` / `动作:` / `台词 / 字幕:` / `节奏:` / `光线 / 色调:` / `渲染样式:` / `比例:` / `时长:` / `负向:` 等) → 用 `<span class="field-label">` 包裹（暖橙色 #f5a96d 粗体）。innerText 不变，copy button 复制纯文本。Rule #12.4 v4 新增 NFR-17 字数上限 + Markdown-style 视觉渲染契约。

Auto-updated:
- `.claude/agent_refs/project/ai_video.md` — Rule #12.4 v4 amend：新增「prompt 字数上限契约」(NFR-17) ≤ 2000 soft / ≤ 2500 hard；rule 12.4-A 角色字段展开规则 v3 (shot prompt 角色 line 仅 locked + face-diff，micro-details 仅在 character ref); 新增 渲染样式 / 负向 字数 trim 政策 (≤ 9 keywords / ≤ 24 items); 新增 Markdown-style 视觉渲染契约 (webapp field-label highlight)。
- `specs/ai_video/mozun_chongsheng/user_input/revised_prompt.md` — Last regenerated header bumped to 2026-05-10 15:41:33 + follow-up 013 摘要。
- `specs/ai_video/mozun_chongsheng/final_specs/spec.md` — NFR-17 NEW (字数上限契约 + trim 优先级)。
- `projects/ai_video_management/frontend/src/markdown/renderer.tsx` — `CopyableCode` 升级：新增 `FIELD_LABEL_RE` regex + `extractText` walker + `renderHighlightedLines` 函数，解析 code block 文本 → split 行 → 行首匹配 field label 时 wrap label 在 `<span className="field-label">`，rest 原样。innerText 仍纯文本。
- `projects/ai_video_management/frontend/src/styles.css` — 新增 `.markdown-view .code-block-wrapper .field-label` style (color #f5a96d 暖橙 + font-weight 700 + letter-spacing 0.02em)。
- `ai_videos/mozun_chongsheng/episodes/ep01..ep05/prompts/shot{NN}.md` × 50 — 5 parallel subagents 各处理 10 shot files：① 角色 line 删除 inline body expansion + 5-7 项 micro-details；② 渲染样式 line replace_all canonical 9-keyword 版本；③ 负向 line replace_all canonical 24-item 版本。

Per-ep trim 字数变化:
- ep01 (1-6 角色 shots): 2400-4500 字 → 788-1357 字 (50%-70% reduction)
- ep02 (1-2 角色 shots): 1300-1568 字 → 851-1060 字 (30%-40% reduction)
- ep03 (1-2 角色 shots): 1172-1551 字 → 835-1146 字 (30%-30% reduction)
- ep04 (1-3 角色 shots): 1280-1882 字 → 935-1421 字 (25%-25% reduction)
- ep05 (1-2 角色 shots): 1293-1644 字 → 946-1297 字 (25%-25% reduction)

**所有 50 shot files post-013 全部 ≤ 1500 字**（well within 2000 soft limit; 0/50 文件超 hard limit）。

Webapp 视觉效果（per follow-up 013）:
- ```text fenced code blocks 行首 field labels 现以暖橙色粗体高亮显示
- `{ref_xxx}` placeholders 在 code block 外（Reference placeholders table 内）以靛蓝 pill 高亮（per follow-up 010）
- Copy button 仍 copy 纯文本（field-label spans 不影响 innerText）

总计 patch 范围: **1 agent_refs amend (rule #12.4 v4 + NFR-17) + 1 spec.md NFR-17 NEW + 1 revised_prompt header + 2 webapp files (renderer.tsx + styles.css) + 50 shot files trimmed = 55 文件改动**。

No conflicts found in:
- `ai_videos/mozun_chongsheng/characters/c{1..10}_*.md` × 10 — 不动 (character ref 仍 carry 完整 inline expansion + 5-7 项 micro-details，turntable mp4 渲染时使用)。
- `ai_videos/mozun_chongsheng/scenes/s{1..6}_*.md` × 6 — 不动。
- `ai_videos/mozun_chongsheng/style_guide.md` (含 follow-up 008/012 的完整 39 项负向 + 8 项 photorealism 正向) — 不动 (style_guide 是 character ref 的 source；shot prompt 引用 trim 版)。
- `world.md` / `arc_outline.md` / `README.md` — 不动。
- spec-pipeline 史料 — 不动。
- ep01-ep05 episode.md / shotlist.md / publish.md — 不动。

Severity: Low blast radius (additive trim — 删除 / 替换 specific 段；现有 byte-stable 锁定 + face-differentiator + Asian aesthetic 主框架保留)。webapp visual upgrade 是 additive (新增 CSS class + 新增 React 渲染逻辑；现有 copy button + ref-placeholder pill + locked-block 全部仍工作)。

User next steps:
1. 重新打开 webapp → 任一 shotNN.md → 看 ```text code block 内 field labels 现以暖橙色粗体高亮显示。
2. 用 trim 后的 shot prompt（≤ 1500 字）重新粘贴到 Seedance / Sora / Veo / Runway / Kling，并预先上传 turntable.mp4 + scene reference 视频/图。模型从 turntable 视频 inherit 角色 完整面部细节（包括 5-7 项 micro-details），shot prompt 仅触发角色姿态 + 场景 + 动作 + 台词。
3. 生成视频后比对 follow-up 012 (4500 字 prompt) vs 013 (1500 字 prompt) 输出质量是否差异显著。预期：因 turntable.mp4 已 carry character data，trim 后的 shot prompt 输出质量保持稳定。
4. 后续 ep06-ep60 stage-4 regen 时按 rule #12.4 v4 出文（含 NFR-17 字数上限 + 12.4-A v3 角色 trim 规则）。

Pre-existing inconsistency carried forward:
- 沧冥 inline 体型 展开「三十出头」(legacy) 现已不在 shot prompts 内（已 trim），仅遗留在 character ref turntable prompt — 独立 surgical follow-up 处理。

## Follow-up 012 — 2026-05-10 15:15:46
Source: user_input/follow_ups/012-20260510-151546-photorealism-microdetails.md
Summary: 用户反馈生成角色仍偏卡通 + 多角色相似。两条线升级：(A) **真人写实强化锚点** — style_guide.md 渲染样式锁定 段补 8 项 photorealism 强化正向 (DSLR 拍摄 / 真实毛孔细节 / 真人皮肤真实质感 / Netflix 4K HDR drama 标准 / etc.) + 14 项扩展 photorealism 负向 (anime/manga style face / over-smoothed skin / plastic skin / wax figure / AI-generated face / same-face syndrome / etc.); (B) **每角色 5-7 项 distinctive 微细节** — 锁定描述符 #11 标志特征点 expand to 覆盖 眼/鼻/唇/下颌/皮肤 5 大维度的 5-7 项 micro-details (上眼睑 / 卧蚕 / 鼻头 / 唇峰 / 下颌 / 颧骨 / 肤色 / 毛孔 / etc.); rule #12.7 v2 强化。

10 character distinctive 微细节 锁定（每角色 1 句话 byte-stable）:
- c1_沧冥: 上眼睑微肿、卧蚕浅、鼻头窄尖、唇峰锐、下颌方硬、颧骨高峭、肤冷白如玉、毛孔细密、无法令纹
- c2_叶无尘: 上眼睑薄、卧蚕浅、下眼袋微显、鼻头小巧、上唇薄下唇略厚、下颌瘦削、肤色微暗有微擦伤
- c3_苏璃月: 双眼皮饱满、卧蚕明显、鼻头圆秀、唇峰柔圆、唇角微上扬、下颌柔和、肤白如雪、毛孔近无、皮肤透亮
- c4_柳红袖: 双眼皮深、卧蚕厚、眼尾上挑、鼻头略圆、上唇饱满下唇厚、唇珠点缀、肤色暖白带桃红、唇色朱红
- c5_苓夭夭: 双眼皮浅、卧蚕饱满圆润、鼻头小圆、唇峰圆、苹果肌饱满、下颌圆润、肤色健康奶白、有少量雀斑
- c6_白月清: 双眼皮浅、卧蚕薄、内眼角平、鼻头窄、唇峰柔、下颌方圆、肤色白净、毛孔细密、温润有光
- c7_赵焚天: 单眼皮重、卧蚕粗厚、下眼袋深、鼻头圆肉鼻翼宽厚、上下唇厚、唇角下垂、下颌方硬、颧骨高、喉结大、肤色古铜、毛孔粗大、皮肤粗糙
- c8_方鼎元: 双眼皮浅、卧蚕薄长、内眼角平、鼻头窄、唇峰柔、下颌瘦削、肤色白净、毛孔细密、有法令纹
- c9_韩夺心: 单眼皮硬、卧蚕窄薄、眼尾极上挑、鼻头窄尖、上唇极薄、唇峰锐、唇角下垂、下颌方硬、颧骨高、肤色冷白、毛孔细
- c10_司空玄: 单眼皮锋、眼尾极上挑双眼狐狸感、鼻头窄尖鹰钩、上下唇薄、下颌窄菱形、颧骨高瘦、下巴尖锐、肤色冷白偏青

Auto-updated:
- `.claude/agent_refs/project/ai_video.md` — Rule #12.7 v2 amend：「锁定描述符 #2 面貌 6 子项」row 6 expanded to「标志特征点 + 5-7 项 distinctive 微细节」（覆盖 眼周 / 鼻形 / 唇形 / 下颌 / 皮肤 5 大维度）；新增 12.7-B+「真人写实强化锚点」段（要求 style_guide.md § 渲染样式锁定 段补 8 项 photorealism 正向 + 14 项扩展 photorealism 负向）。
- `specs/ai_video/mozun_chongsheng/user_input/revised_prompt.md` — Last regenerated header bumped to 2026-05-10 15:15:46 + follow-up 012 摘要。
- `ai_videos/mozun_chongsheng/style_guide.md § 渲染样式锁定` — 正向关键词补 8 项 photorealism 强化 (DSLR / 真实毛孔 / 真人演员档级 / 85mm cinematic lens / 影棚自然光 / Netflix 4K HDR / human skin shader / 8K 写实 RAW); 负向关键词补 14 项扩展 photorealism (anime style face / cartoon style / over-smoothed skin / plastic skin / wax figure / AI-generated face / same-face syndrome / 模糊轮廓 / etc.)。
- `ai_videos/mozun_chongsheng/characters/c{1..10}_*.md` × 10 — 4 Edits per file（40 total）：① 锁定描述符 #11 cell append 「+ 面部微细节：...」 sentence per character; ② turntable ref 第二段 ```text fenced 角色 line append 微细节 sentence (after inline expansion tail); ③ 渲染样式 line append 8 photorealism positives; ④ 负向 line append 14 photorealism negatives.
- `ai_videos/mozun_chongsheng/episodes/ep01..ep05/prompts/shot{NN}.md` × 50 — 5 parallel subagents 各处理 10 shot files：① 角色 line inline expansion append 「面部微细节」 sentence per character that appears in shot; ② 渲染样式 line append 8 photorealism positives; ③ 负向 line append 14 photorealism negatives. 每文件 ~3-8 Edits 视 character 数量而定。Edit ops 跨 ep summary: ep01 48, ep02 ~30, ep03 ~30, ep04 36, ep05 ~32, total ~176 Edits。

总计 patch 范围: **1 agent_refs amend (rule #12.7 v2) + 1 style_guide.md amend (8+ positives + 14+ negatives) + 1 revised_prompt header + 10 character files × 4 Edits + 50 shot files × ~3-8 Edits = ~63 文件改动 with ~216 Edits**。

Per-character 微细节 stats:
- ep01 shots 包含 6 角色 (沧冥 + 5 宗主)，各 shot 取决于 character composition：shot01/02/08/09 仅 沧冥 (1 char)；shot04 沧冥+白月清 (2)；shot05 沧冥+赵焚天+方鼎元 (3)；shot03/06/07 全员 (6)；shot10 沧冥 魂火形态 (1).
- ep02 shots 多数 1-2 character (白月清 主导 + 沧冥 关键 shots)。
- ep03 shots 沧冥+赵焚天 双 main characters (shot01/05/10 仅一人；其余双人).
- ep04 shots 三反派对话主导 (shot01 沧冥+三反派剪影；shot02/04/06/07 单人；shot03 双人；shot05/08/09 三人；shot10 沧冥 cliff).
- ep05 shots 沧冥 魂魄态 + 叶无尘 主体；shot06 双人.

No conflicts found in:
- `ai_videos/mozun_chongsheng/scenes/` × 6 — 不动 (scene files don't carry 角色 micro-details).
- `ai_videos/mozun_chongsheng/world.md` / `arc_outline.md` / `README.md` — 不动.
- spec-pipeline 史料 — 不动.
- ep01-ep05 episode.md / shotlist.md / publish.md — 不动.
- `projects/ai_video_management/frontend/` — 不动 (本 follow-up 不动 webapp).

Severity: Low blast radius (additive — 渲染样式 + 负向 + 角色 inline expansion 各 append 一段；既有内容全部 byte-identical 保留)。AI 生成时 prompt 信号密度提高：photorealism 关键词从 ~3 个 → ~8 个 (拉向真人摄影质感)；面部 anatomy 数据点从 6 子项 → 5-7 项 micro-details + 1 唯一标记 (各角色面孔差异化数据点丰富)。

User next steps:
1. 用更新的 c{1..10}_*.md (含 5-7 项 distinctive 微细节) 重新渲染 turntable mp4 → 期望 10 角色面孔差异更明显。
2. 用更新的 50 shot.md (含 photorealism 强化 + 角色 micro-details inline) 重新渲染 video → 期望视觉拉向真人摄影质感，远离 cartoon/illustration smooth-skinned anime stylization。
3. 后续 ep06-ep60 stage-4 regen 时按 rule #12.7 v2 出文（含 5-7 项 distinctive 微细节 + 真人写实强化锚点）。

Pre-existing inconsistency carried forward (independent surgical follow-ups 处理):
- 沧冥 inline 体型 展开「三十出头」(legacy seedance variant) vs follow-up 002 锁定「看似二十五」依然不一致。
- style_guide.md / README.md 内文可能仍引用旧 character file path（pre-011 长 filename），需后续 surgical follow-up rename 传播。

## Follow-up 011 — 2026-05-10 14:59:30
Source: user_input/follow_ups/011-20260510-145930-naming-convention-scenes-merge.md
Summary: 三件事：(A) 合并 `scenes/{长名}.md` (bible) + `scenes/ref_images/{长名}-立绘.md` (立绘 ref) → 单一自包含 `scenes/s{N}_{shortname}.md` 文件 (mirror character merge per follow-up 009)；删除 `scenes/ref_images/` 子目录。(B) 新命名约定 cN_/sN_：characters renamed to `c{N}_{中文名}.md` (10 files); scenes renamed + merged to `s{N}_{shortname}.md` (6 files); placeholder syntax updated `{ref_<chinese>}` → `{ref_c{N}_{name}}` / `{ref_s{N}_{name}}`. (C) Reference validation contract — stage-6 validator 须扩展 schema check (NFR-16: dangling placeholder = blocker). 新增 rule #12.8 命名约定 + 验证 + numbering rules.

10 character renames:
- 沧冥-魔尊本相.md → c1_沧冥.md
- 叶无尘-乞丐转生.md → c2_叶无尘.md
- 苏璃月-紫霄圣女.md → c3_苏璃月.md
- 柳红袖-红袖招老板娘.md → c4_柳红袖.md
- 苓夭夭-药王谷医师.md → c5_苓夭夭.md
- 白月清-紫霄宫主.md → c6_白月清.md
- 赵焚天-玄炎宗主.md → c7_赵焚天.md
- 方鼎元-太清掌教.md → c8_方鼎元.md
- 韩夺心-万剑宗主.md → c9_韩夺心.md
- 司空玄-影神殿主.md → c10_司空玄.md

6 scene merges + renames:
- 沧冥魔域-黑金大殿长阶顶.md (+ 立绘) → s1_长阶顶.md (合并)
- 沧冥魔域-黑金大殿内.md (+ 立绘) → s2_大殿内.md (合并)
- 玄炎宗-铸器堂.md (+ 立绘) → s3_铸器堂.md (合并)
- 太清门-金殿密室.md (+ 立绘) → s4_金殿密室.md (合并)
- 凡间小镇-破庙墙角.md (+ 立绘) → s5_破庙.md (合并)
- 雪山冰原.md (+ 立绘) → s6_雪山.md (合并)

未立档 placeholder 也分配 sN_ 前缀（保留为 placeholder，便于后续立档）：
- {ref_山道平台} (ep02) → {ref_s7_山道平台}
- {ref_云海} (ep05) → {ref_s8_云海}
- {ref_识海} (ep05) → {ref_s9_识海}

Auto-updated:
- `.claude/agent_refs/project/ai_video.md` — 新增 Rule #12.8「Character / Scene 命名约定 cN_/sN_」（filename pattern + placeholder pattern + numbering rules + reference validation contract + scene file schema mirror character pipeline）。
- `specs/ai_video/mozun_chongsheng/user_input/revised_prompt.md` — Last regenerated header bumped to 2026-05-10 14:59:30 + follow-up 011 摘要。
- `specs/ai_video/mozun_chongsheng/final_specs/spec.md` — FR-9 + FR-5 amend 引用 rule #12.8 命名约定。
- `ai_videos/mozun_chongsheng/characters/` × 10 — bash mv 10 files to new c{N}_{中文名}.md naming (no content change).
- `ai_videos/mozun_chongsheng/scenes/` (6 new + 6 old + 子目录 deleted) — Merge subagent: 写 6 个新 s{N}_{shortname}.md 文件 (含 bible 段 + `---` divider + 场景 reference prompt 段)；删除 6 个旧 bible + 6 个旧 立绘；删除 `scenes/ref_images/` 子目录。Bible content + 立绘 prompt body 全部 byte-identical 保留。
- `ai_videos/mozun_chongsheng/episodes/ep01..ep05/prompts/shot{NN}.md` × 50 — 5 parallel subagents: 每文件 4-14 个 Edit operations (replace_all=true), 共 288 个 Edits 跨 50 文件。Path renames: 出场角色 table + Reference placeholders source column 引用全部 byte-renamed。Placeholder renames: Reference placeholders table 第 1 列 + 视频 prompt code block 内 `{ref_xxx}` 全部 byte-renamed。其余字段 (Shot context Summary / 时长 / 镜头 / 动作 / 台词 / 节奏 / 渲染样式 / 比例 / 负向 / 视频 prompt 14-字段 schema) 全部 byte-identical 保留。

总计 patch 范围: **1 agent_refs amend (rule #12.8 NEW) + 1 spec.md FR-5/9 amend + 1 revised_prompt header + 10 character mv + 6 scene merges (12 → 6 文件) + 1 子目录 delete + 50 shot files × ~6 Edits each = 78 文件改动 + 1 子目录删除**。

Per-ep shot Edit count (replace_all=true ops):
- ep01: 81 edits (沧冥 + 5 宗主 + 长阶顶 / 雪山 location refs)
- ep02: 50 edits (沧冥 + 白月清 + 长阶顶 / 大殿内 / 山道平台 / 铸器堂 (shot10 闪剪))
- ep03: 52 edits (沧冥 + 赵焚天 + 铸器堂)
- ep04: 64 edits (沧冥 + 方鼎元 + 韩夺心 + 司空玄 + 铸器堂 / 金殿密室 / 雪山)
- ep05: 41 edits (沧冥 魂魄态 + 叶无尘 + 雪山 / 破庙 / 云海 / 识海)

No conflicts found in:
- `ai_videos/mozun_chongsheng/style_guide.md` (含 follow-up 008 § 亚洲俊男靓女审美锚点 含旧 character 名引用) / `world.md` / `arc_outline.md` / `README.md` — 不动；这些文件可能仍引用旧的 `沧冥-魔尊本相` 等长 path or filename，独立 surgical follow-up 处理（rename propagation phase 2）。
- spec-pipeline 史料（qa.md / dossier.md / angle files / validation strategy / bdd_scenarios / ai_video_specific）— 不动（史料不修改）。
- ep01-ep05 episode.md / shotlist.md / publish.md — 不动 (这些文件不直接引用 character/scene file paths)。
- `projects/spec_driven/frontend/` / `projects/ai_video_management/frontend/` — 不动 (本 follow-up 不动 webapp; webapp 路径 routing 由 React Router 处理 file path 透传无需 rename code)。

Severity: Low blast radius (rename + content-preserving merge); 78 文件改动 + 1 删除 但内容全部 byte-identical 保留。Reference validation contract 是新规约，stage-6 validator 须出补丁单 NFR-16 增强检查；当前 50 shot files 全部已对齐 cN_/sN_ 命名 (subagents 报告 zero dangling placeholders)。

User next steps:
1. `characters/` 下打开任一 file (e.g., `c1_沧冥.md`) → 顶部 H1 仍是「沧冥 · 魔尊本相」(content unchanged); 文件名是 `c1_沧冥.md`.
2. `scenes/` 下打开任一 file (e.g., `s1_长阶顶.md`) → 顶部 H1 是 scene 名; bible 段 + `---` + 场景 reference prompt 段 (含可 copy-paste ```text 块).
3. 任一 `shotNN.md` → Reference placeholders table 引用 `c1_沧冥.md` / `s1_长阶顶.md` 等新路径; 视频 prompt code block 内 placeholder 形式 `{ref_c1_沧冥}` / `{ref_s1_长阶顶}` 等。
4. 后续 ep06-ep60 stage-4 regen 时按 rule #12.8 出文（cN_/sN_ 命名锁定）.

Pre-existing inconsistency carried forward (independent surgical follow-ups 处理):
- 沧冥 inline 体型 展开「三十出头」(legacy seedance variant) vs follow-up 002 锁定「看似二十五」依然不一致。
- style_guide.md / README.md 内文可能仍引用旧 character file path（如「characters/沧冥-魔尊本相.md」）需后续 surgical follow-up rename 传播.

## Follow-up 010 — 2026-05-10 14:46:48
Source: user_input/follow_ups/010-20260510-144648-better-visual-style-copy-button-dialogue.md
Summary: 三件事：(A) ai_video_management webapp 渲染 markdown 时给所有 ```text``` / ```yaml``` 等 fenced code blocks 加一键 **复制按钮**（top-right corner，hover 显眼，点击 copy → 短暂 "已复制 ✓" feedback）；(B) `{ref_xxx}` 占位符在 rendered view 视觉 highlight 为 pill 样式 (CSS pill + monospace + indigo bg)，**仅在 fenced code blocks 之外**（保证 copy 复制纯文本不带 HTML markup）；(C) 50 个 shot.md 文件**加入完整人物台词**——expand 默剧 shots → 含 character dialogue 多行 script 格式 (按角色 bible 标志台词 + shotlist + episode 剧情衍生)；保留真正纯视觉镜头 (lightning合围 / 法宝群攻全景 / 闪剪 cliffhanger 等)。

Auto-updated:
- `.claude/agent_refs/project/ai_video.md` — Rule #12.6 v3 amend：新增「人物台词强制原则」（每 shot 优先加 ≥1 句人物台词，台词衍生自 bible 标志台词或 shotlist 剧情；纯视觉 shot 允许例外但 ≤25%/ep）+ 「Visual style 渲染契约」（webapp 注入一键 copy button + `{ref_xxx}` placeholder pill highlight，markdown 文件内容不需要显式包 markup）。
- `specs/ai_video/mozun_chongsheng/user_input/revised_prompt.md` — Last regenerated header bumped to 2026-05-10 14:46:48 + follow-up 010 摘要。
- `specs/ai_video/mozun_chongsheng/final_specs/spec.md` — FR-9 段 ③ 视频 prompt 字段描述补「人物台词强制原则」+「Visual style 渲染契约」交叉引用 rule #12.6 v3。
- `projects/ai_video_management/frontend/src/markdown/renderer.tsx` — Added `CopyableCode` React component (top-right copy button + transient "已复制" state via `useState` + `navigator.clipboard.writeText`); registered as ReactMarkdown `pre` component override; added `applyRefPlaceholderPill` regex pre-pass (matches `\{ref_([一-鿿\w-]+)\}`，code-fence-aware: split by `(\`\`\`[\s\S]*?\`\`\`)/g`, only replace in non-code segments).
- `projects/ai_video_management/frontend/src/styles.css` — Added `.markdown-view .code-block-wrapper` (relative positioning), `.copy-btn` (absolute top-right + hover/active/copied states + 0.18s transition), `.markdown-view .ref-placeholder` (indigo pill: rgba(99,102,241,0.16) bg + #a5b4fc fg + 4px border-radius + monospace + 0.92em); also tweaked `.markdown-view pre` (border-radius 4 → 6, padding 12→14/14→16, line-height 1.55 → 1.6) for slightly nicer visual.
- `ai_videos/mozun_chongsheng/episodes/ep01..ep05/prompts/shot{NN}.md` × 50 — 「台词 / 字幕」字段加入人物台词 (multi-line script format)。Per ep:
  - **ep01** (开场镇压): shot01 旁白+沧冥；shot02-05 加入 沧冥/方鼎元/白月清/赵焚天 人物台词；shot06 沧冥 标志台词；shot07 旁白；shot08 默剧 (黑色星河裂痕，纯视觉 1/10 = 10%)；shot09 沧冥；shot10 旁白 cliff。
  - **ep02** (倒叙片段): shot01 旁白；shot02-09 加入 白月清+沧冥 dialogue (探询/献丹/嗤笑/系统弹窗+沧冥/拭面笑容崩坏)；shot10 白月清 cliff 立誓。0 默剧 shot。
  - **ep03** (倒叙铸器堂): shot01 旁白；shot02-04+shot06+shot08 加入 沧冥+赵焚天 dialogue；shot05/shot07 默剧 (大特写手部 / 战斗快剪，纯视觉 2/10 = 20%)；shot09 沧冥 H9 cliff；shot10 赵焚天 收尾。
  - **ep04** (H6 撕脸三阶): shot01 旁白+沧冥；shot02-09 加入 方鼎元+韩夺心+司空玄 三反派 dialogue + shot09 三人合阵齐喝；shot10 沧冥 cliff "当年你们怎么对我，今日我便十倍奉还"。0 默剧 shot。
  - **ep05** (转生卷): shot01-shot02+shot05-shot08 加入 沧冥 魂魄独白；shot03+shot04+shot09+shot10 加入 叶无尘 弱声/苏醒 dialogue；shot10 cliff "……我……回来了。"。0 默剧 shot。
  - 总计纯视觉 shots: 3/50 = 6% (well within 25% allowance per rule #12.6 v3 人物台词强制原则)。

总计 patch 范围: **1 agent_refs amend (rule #12.6 v3) + 1 spec.md FR-9 amend + 1 revised_prompt header + 2 webapp files (renderer.tsx + styles.css) + 50 shot files dialogue addition = 55 文件改动**。

Subagent observation worth flagging: ep03 shot06 attribution edge case — line "此器非矿石铸，乃以人血人骨。" historically lived in 赵焚天's character bible 标志台词 库 (per follow-up 008's actor anchor table), but follow-up 002/003 era script may have attributed to 沧冥 in some shotlists. follow-up 010 ep03 subagent followed my task spec attribution (赵焚天) ; if user prefers 沧冥 attribution they can flip in a 1-line surgical follow-up.

No conflicts found in:
- `ai_videos/mozun_chongsheng/characters/{role}.md` × 10 — 不动；character bibles 是 dialogue 来源。
- `ai_videos/mozun_chongsheng/scenes/` × 12 — 不动。
- `ai_videos/mozun_chongsheng/style_guide.md` / `world.md` / `arc_outline.md` / `README.md` — 不动。
- spec-pipeline 史料 — 不动。
- ep01-ep05 episode.md / shotlist.md / publish.md — 不动。
- `projects/spec_driven/frontend/src/markdown/renderer.tsx` — 不动 (本 follow-up 仅 target ai_video_management webapp)。

Severity: Low blast radius for content (50 dialogue additions are content-level only); medium for webapp UI (2 file changes adding ~70 LOC of TSX + ~50 LOC of CSS — needs `npm run build` + visual smoke test for the copy button to verify works in production). Webapp changes are additive (no regression risk to existing behavior; existing locked-block + link resolver + ReactMarkdown setup all preserved).

User next steps:
1. Run `npm run dev` (or build) inside `projects/ai_video_management/frontend/` to see the copy button + placeholder pills in action.
2. Open any `shotNN.md` in webapp → click "复制 Copy" button on the prompt code block → verify clipboard contains the raw prompt text including raw `{ref_xxx}` placeholders (not HTML markup).
3. Verify `{ref_xxx}` placeholders in the Reference placeholders table render with indigo pill style; placeholders inside the code block render as plain text (so copy button copies cleanly).
4. Open any shot file → see new 人物台词 multi-line script format under `台词 / 字幕:` field; verify dialogue voice matches each character's bible 标志台词.
5. 后续 ep06-ep60 stage-4 regen 时按 rule #12.6 v3 出文 (含 人物台词强制原则 + Visual style 渲染契约)。

Pre-existing inconsistency carried forward (independent surgical follow-up 处理):
- 沧冥 inline 体型 展开「三十出头」(legacy seedance variant 文本) vs follow-up 002 锁定「看似二十五」依然不一致。

## Follow-up 009 — 2026-05-10 14:08:54
Source: user_input/follow_ups/009-20260510-140854-merge-character-files-placeholders-script.md
Summary: 三件事：(A) 合并 `characters/{name}.md` (bible) + `characters/ref_images/{name}-立绘.md` (turntable ref) → 单一 `characters/{name}.md` 文件；删除 `ref_images/` 子目录。(B) 每 shot file 删除 Seam-frame still prompts 段（startframe + lastframe Seedream code blocks），仅保留单一 video prompt。(C) shot file 新增 Reference placeholders 段（角色 + 场景占位符 `{ref_xxx}`），prompt body 内文使用占位符语法引用，多角色 dialogue 强制 multi-line script 格式（`- {ref_<char>} <char>: ...`）。

Auto-updated:
- `.claude/agent_refs/project/ai_video.md` — Rule #12.5 v3 amend (合并 bible + turntable ref 为单文件 schema；废止 `ref_images/` 子目录)；Rule #12.6 v2 amend (drop Seam-frame still prompts 段；新增 Reference placeholders 段；强化 dialogue script multi-line 格式；shot file 三段从 Shot context + 视频 prompt + Seam-frame still prompts → Shot context + Reference placeholders + 视频 prompt)。
- `specs/ai_video/mozun_chongsheng/user_input/revised_prompt.md` — Last regenerated header bumped to 2026-05-10 14:08:54 + follow-up 009 摘要 + follow-up 007 标注「第 ③ 段被本 follow-up 删除；前两段保留」。
- `specs/ai_video/mozun_chongsheng/final_specs/spec.md` — FR-9 amend (三段：Shot context + Reference placeholders NEW + 视频 prompt；drop Seam-frame still prompts)；FR-11 / FR-12 改标「已废止」(seam-frame embedded blocks 移出)；NFR-4 改写为「单一 shot 文件 (3 段，无 seam-frame embedded)」。
- `ai_videos/mozun_chongsheng/characters/{role}.md` × 10 — Bible 内容保留 byte-identical；末尾 append 视频 reference prompt 段（包含 文件说明 callout + 用法 callout + ```text fenced turntable prompt body + 5 句标准台词 配音对照表）。每文件现含 bible H1 + `---` + ref turntable H1 两个顶级 section。
- `ai_videos/mozun_chongsheng/characters/ref_images/` × 10 + 子目录 — 全部 deleted。
- `ai_videos/mozun_chongsheng/episodes/ep01..ep05/prompts/shot{NN}.md` × 50 — 全部按新 schema 重写：① Seam-frame still prompts 段删除（每 shot1 文件之前的 startframe + 每 shot 的 lastframe code blocks）；② 出场角色 表 column "turntable reference" → "character file"；path `characters/ref_images/{name}-立绘.md` → `characters/{name}.md`；drop "Reference uploads pre-flight checklist" sub-item from Shot context；③ 新增 Reference placeholders 段（每 shot 列出 ✅ 角色 + 场景 placeholder + 替换说明 + 来源 character/scene file）；④ 视频 prompt 代码块: `角色:` line prefix `{ref_<char>} `；`场景:` line prefix `{ref_<scene>} `；`台词 / 字幕:` field 多角色 multi-line script 格式 (`  - {ref_<char>} <char>: ...`)；其余 14 字段 byte-identical 保留。
- `ai_videos/mozun_chongsheng/episodes/ep04/prompts/shot{01,02,03,04,05,07,08,09}.md` × 8 — Post-restructure surgical patch: 修正 character file path 错误（`方鼎元-太清门掌门` → `方鼎元-太清掌教`；`司空玄-阴鸷宗主` → `司空玄-影神殿主`，匹配 actual character files at `characters/{中文名}-{身份}.md`）。

总计 patch 范围: **1 agent_refs amend (rule #12.5 v3 + #12.6 v2) + 1 spec.md amend (FR-9/11/12/NFR-4) + 1 revised_prompt header + 10 character bibles updated (append turntable section) + 10 ref_images files deleted + ref_images/ subdir deleted + 50 shot files restructured + 8 ep04 path fixes (replace_all sed) = ~73 文件改动 (excluding subdir delete)**。

Scene placeholder mappings used (cross-ep):
- 沧冥魔域-黑金大殿长阶顶 → `{ref_长阶顶}`
- 沧冥魔域-黑金大殿内 → `{ref_大殿内}`
- 玄炎宗-铸器堂 → `{ref_铸器堂}`
- 太清门-金殿密室 → `{ref_金殿密室}`
- 凡间小镇-破庙墙角 → `{ref_破庙}`
- 雪山冰原 → `{ref_雪山}`
- 魔气长阶 山道中段平台 (未立档) → `{ref_山道平台}`
- 高空云海 (未立档) → `{ref_云海}`
- 蒙太奇识海空间 (未立档) → `{ref_识海}`

No conflicts found in:
- `ai_videos/mozun_chongsheng/scenes/`（12 文件）— 不动；shot prompt 现引用 `scenes/{name}.md` paths via Reference placeholders source column.
- `ai_videos/mozun_chongsheng/style_guide.md` (含 follow-up 008 § 亚洲俊男靓女审美锚点) / `world.md` / `arc_outline.md` / `README.md` — 不动。
- spec-pipeline 史料 (qa.md / dossier.md / angle files / validation strategy / bdd_scenarios / ai_video_specific) — 不动；validator 须扩展 schema 检查（出补丁单：NFR-14 Reference placeholders 段完整性 + NFR-15 dialogue script multi-line format 校验）。
- `episodes/ep01..ep05/episode.md` / `shotlist.md` / `publish.md` — 不动。

Severity: 文件级 reorganize + delete 11 文件（10 ref + 1 subdir）+ 50 文件 schema rewrite。Bible content + turntable prompt + 14 字段视频 prompt body 全部 byte-identical 保留；只是重新组织。下游不受影响。

User next steps:
1. 打开任一 `characters/{name}.md` → 顶部看 bible（per follow-up 003+008 schema）→ 中段 `---` divider → 底段视频 reference prompt code block + 5 句台词对照表。一次 copy-paste 即可生成 turntable.mp4。
2. 打开任一 `episodes/ep{NN}/prompts/shot{NN}.md` → ① 顶部 Shot context (review) → ② 中段 Reference placeholders 表（明确知道要 prepare 哪些 reference）→ ③ 底段视频 prompt code block (含 `{ref_xxx}` 占位符) → 复制到 Seedance / Sora / Veo / Runway / Kling → 上传 reference 文件 → 替换 `{ref_xxx}` 占位符 → 生成。
3. 多角色 dialogue 现强制 multi-line script 格式（`- {ref_<char>} <char>: <字幕方式 + 台词原文 + 字体调性>`），便于配音对照与制作多角色对白视频。
4. 后续 ep06-ep60 stage-4 regen 时按 rule #12.5 v3 + #12.6 v2 出文。

Pre-existing inconsistency carried forward (independent surgical follow-up 处理):
- 沧冥 inline 体型 展开「三十出头」(legacy seedance variant 文本) vs follow-up 002 锁定「看似二十五」依然不一致。

## Follow-up 008 — 2026-05-10 13:44:00
Source: user_input/follow_ups/008-20260510-134400-facial-differentiation-asian-aesthetic.md
Summary: 解决 AI 生成角色面孔同质化问题 + 锁定亚洲俊男靓女审美锚点。锁定描述符 #2「面貌」从单字段扩展为 6 子项（脸型 / 眉形 / 眼型 / 鼻型 / 唇型+牙齿 / 标志特征点）；新增锁定描述符 #11「标志特征点」cross-character unique-identifier 必填行；锁定描述符 #10 一句话锁定 插入 face-differentiator short token，让所有下游 prompt 自动 inherit 唯一识别符。新增 rule #12.7 (cross-character facial differentiation 一致性规则 + 亚洲俊男靓女审美锚点) + style_guide.md § 亚洲俊男靓女审美锚点 段（中日韩演员锚点表 + 11 项 AI-同质化负向 + 5 项 Asian aesthetic 正向 + 唯一识别符表）。10 角色 bible + 10 character ref + 50 shot.md 全部 byte-level patched 同步新 一句话锁定 + 11 负向 + 5 渲染样式正向。

10 唯一识别符（cross-character mutex）:
- 沧冥: 右眼下方朱砂痣
- 叶无尘: 左眉骨小银环
- 苏璃月: 左耳珍珠坠
- 柳红袖: 右唇角红点小痣
- 苓夭夭: 鼻尖淡褐雀斑
- 白月清: 眉心淡红痕
- 赵焚天: 左颊古旧暗红疤
- 方鼎元: 下颌左侧黑长痣
- 韩夺心: 右眼角斜疤
- 司空玄: 左颈侧十字暗纹

Auto-updated:
- `.claude/agent_refs/project/ai_video.md` — 新增 Rule #12.7「Cross-character facial differentiation + 亚洲俊男靓女审美锚点」含 12.7-A 锁定描述符 #2 面貌 6 子项 schema、12.7-B cross-character similarity 一致性规则（任两人 ≥ 5 子项相同 OR 标志特征点重复 = blocker）、12.7-C 项目级亚洲俊男靓女审美锚点 (style_guide.md § 必含)、12.7-D 应用到下游 prompt 的传播契约。
- `specs/ai_video/mozun_chongsheng/user_input/revised_prompt.md` — Last regenerated header bumped to 2026-05-10 13:44:00 + follow-up 008 摘要。
- `specs/ai_video/mozun_chongsheng/final_specs/spec.md` — FR-26 amend 引用 rule #12.7 face-differentiator + actor anchor 要求（implicit via rule reference；FR-26 unchanged literal text since rule #12.7 contract is what gets enforced at validation）。
- `ai_videos/mozun_chongsheng/style_guide.md` — 新增段「§ 亚洲俊男靓女审美锚点」（在「渲染样式锁定」段之前），含男角色锚点表 / 女角色锚点表 / 通用正向关键词 / 通用负向关键词 / Cross-character 唯一识别符锁定表。
- `ai_videos/mozun_chongsheng/characters/{role}.md`（10 角色 bible）— 锁定描述符 #2 面貌 expanded 为 6 子项（`<br>` HTML line breaks within table cell）；新增 锁定描述符 #11 标志特征点 row（full long-form description）；锁定描述符 #10 一句话锁定 surgical insert face-differentiator short token at natural position；配音参考 / 参考演员或角色 row updated to specific Asian actor anchor (e.g., 沧冥 → 罗云熙澹台烬 + 成毅司凤；苏璃月 → 白鹿黎苏苏 + 虞书欣小兰花；柳红袖 → 章若楠 + 田曦薇 + 赵丽颖；etc.).
- `ai_videos/mozun_chongsheng/characters/ref_images/{role}-立绘.md`（10 character ref turntable prompts）— 4 Edits per file: ① 角色 line OLD → NEW substring with face-differentiator inserted; ② 负向 line append 11 AI-同质化 negatives; ③ 渲染样式 line append 5 Asian aesthetic positives; ④ 配音参考 footer 参考演员 anchor updated to specific actor list.
- `ai_videos/mozun_chongsheng/episodes/ep01..ep05/prompts/shot{NN}.md`（50 shot files）— per shot: each character's OLD → NEW substring replace in 角色 line of video prompt + seam-frame still blocks (replace_all matches both video block 角色 + still block 角色); 11 AI-同质化 negatives appended to 负向 line of main video prompt; 5 Asian aesthetic positives appended to 渲染样式 line of main video prompt. Cross-ep character distribution: ep01 主要 沧冥 + 5 宗主; ep02 主要 沧冥 + 白月清 倒叙; ep03 主要 沧冥 + 赵焚天 铸器堂; ep04 主要 方鼎元 + 韩夺心 + 司空玄 + shot10 沧冥 cliff; ep05 主要 沧冥 (魂魄态) + 叶无尘 (转生).

总计 patch 范围: **1 agent_refs amend (rule #12.7 NEW) + 1 spec.md (FR-26 implicit via rule reference) + 1 style_guide.md amend + 1 revised_prompt header + 10 bibles + 10 character refs + 50 shot files = 73 文件改动 (excluding spec.md unchanged)**。

No conflicts found in:
- `ai_videos/mozun_chongsheng/scenes/`（12 文件）— 不动；scenes 不含人物面貌描述。
- `ai_videos/mozun_chongsheng/world.md` / `arc_outline.md` / `README.md` — 不动。
- `episodes/ep01..ep05/episode.md` / `shotlist.md` / `publish.md` — 不动；它们引用一句话锁定 by reference (via shot prompts), 不存储 byte-identical copy。
- spec-pipeline 史料（qa.md / dossier.md / angle files / validation strategy / bdd_scenarios / ai_video_specific）— 不动；validator 须扩展 cross-character similarity matrix 检查（出补丁单：NFR-13 face-differentiator cross-character mutex 校验 + AI-同质化负向 11-item 完整性校验）。

Severity: 中等 blast radius；70+ 文件 byte-level patched，但每文件改动是 surgical insert（face-differentiator short token + 11 + 5 共 16 个 token append）；不影响其他字段。模型生成时新 face-differentiator 与原 一句话锁定 共同 byte-identical 跨集复制（NFR-2 一致性 contract preserved + extended）。

User next steps:
1. 检查任一 character bible（如 `characters/沧冥-魔尊本相.md`）→ 看锁定描述符 6 子项 + 标志特征点 / 一句话锁定 含 face-differentiator / 配音参考 演员锚点 specific.
2. 检查任一 character ref turntable prompt（如 `characters/ref_images/沧冥-魔尊本相-立绘.md`）→ 看角色 line 含「右眼下方朱砂痣」/ 负向 含 11 项 AI-同质化 / 渲染样式 含 5 项 Asian aesthetic.
3. 检查任一 shot file（如 `episodes/ep01/prompts/shot01.md`）→ 看 video prompt 角色 line 含 face-differentiator / 负向 含 11 项 / 渲染样式 含 5 项.
4. 用更新的 character ref turntable prompt 重新渲染 10 角色 turntable mp4 → 上传作为后续 shot 视频生成时的 reference → 期望生成结果中 10 角色面孔可辨识度高（不再 "AI 通用脸"），符合中日韩古装真人剧主演级颜值。
5. 后续 ep06-ep60 stage-4 regen 时按 rule #12.7 出文。

Pre-existing inconsistency carried forward (independent surgical follow-up 处理):
- 沧冥 inline 体型 展开「三十出头」(legacy seedance variant 文本) vs follow-up 002 锁定「看似二十五」依然不一致（与 follow-up 008 face-differentiator 改动正交，不在本 follow-up scope）。

## Follow-up 007 — 2026-05-10 13:25:13
Source: user_input/follow_ups/007-20260510-132513-single-file-per-shot-context.md
Summary: 进一步合并 `shotNN.md` + `shotNN_lastframe_seedream.md` + `shot01_startframe_seedream.md` → **单一自包含 `shotNN.md`** 文件。新文件三段：① Shot context（human review，含 Summary / 出场角色表 / 场景 / 时长+timed beats / Reference uploads checkbox checklist）+ ② 视频 prompt（copy-paste 14-字段 ```text fenced）+ ③ Seam-frame still prompts（embedded copy-paste，startframe 仅 ep 首镜，lastframe 每镜）。多角色 `台词 / 字幕` 扩展为 multi-line 格式。15s 硬上限 + timed-beats 重排原则写入新 rule #12.6。一个 shot = 一个文件 = 完整自包含。

Auto-updated:
- `.claude/agent_refs/project/ai_video.md` — Rule #5 进一步压缩为「Single-self-contained-file-per-shot」（每 shot **一份** `shotNN.md`，无独立 `_seedream.md`）；新增 **Rule #12.6**「单一自包含 shotNN.md 文件 schema」含完整三段结构 + 5 必填子项（Summary / 出场角色 / 场景 / 时长 / Reference uploads）+ 多角色 `台词 / 字幕` multi-line 扩展（rule #12.4 v3 amend）+ 15s 硬上限 + timed-beats 重排原则 + cross-reference rule #11 / #12.4 v2 / #12.5 v2。
- `specs/ai_video/mozun_chongsheng/user_input/revised_prompt.md` — Last regenerated header bumped to 2026-05-10 13:25:13 + follow-up 007 摘要 + follow-up 006 标注「保持有效；本 follow-up 进一步把 seam-frame 合并进来」。
- `specs/ai_video/mozun_chongsheng/final_specs/spec.md` — FR-9 改写为单一自包含 shot 文件三段 schema（Shot context + 视频 prompt + Seam-frame still prompts）；FR-11 标「已并入 FR-9 段 ③」；FR-12 标「已并入 FR-9 段 ③（仅 ep 首镜）」；NFR-4「单 prompt + seam-frame」→「单一自包含 shot 文件」（每 shot 一份；每 ep 10 文件）。
- `ai_videos/mozun_chongsheng/episodes/ep01/prompts/`（10 updated + 11 deleted）— 10 shotNN.md 重写为三段 schema；删除 10 lastframe + 1 startframe seedream 独立文件。Shot context Summary 派生自 shotlist + episode（如 shot01 "ep01 绝对开场镜，黄金钩 H1 落点"；shot10 "cliff + 预告 H9 黑色魂火越雪山向凡间红光奔去"）。所有 10 shots 视频 prompt body byte-identical 复制；seam-frame still code blocks byte-identical 嵌入。
- `ai_videos/mozun_chongsheng/episodes/ep02/prompts/`（10 updated + 11 deleted）— 同上 schema；ep02 倒叙片段（白月清主导 + 沧冥）；shot01 "ep02 黄金钩 0-8s 沧冥赤瞳大特写骤睁 → 闪黑"；shot10 "H9 集尾选择题 终有一日让你魂飞魄散立誓 cliff"。
- `ai_videos/mozun_chongsheng/episodes/ep03/prompts/`（10 updated + 11 deleted）— 同上；全 10 shot 在 玄炎宗-铸器堂 (立档)；H6 撕脸三阶 + H9 cliff "此账他日再算"。
- `ai_videos/mozun_chongsheng/episodes/ep04/prompts/`（10 updated + 11 deleted）— 同上；多数 shot 在 太清门-金殿密室 (立档)；H6 撕脸 ① 丹书铁券 (shot04) ② 万剑暗刻 (shot06) ③ 神识镜余孽 (shot07)；shot10 沧冥雪坡远眺 cliff。
- `ai_videos/mozun_chongsheng/episodes/ep05/prompts/`（10 updated + 11 deleted）— 同上；shot01/05 雪山冰原 + shot03/04/06/07/09/10 凡间小镇-破庙墙角 (立档)；shot07 魂魄入体 顿挫；shot10 cliff "……我……回来了。" 内嵌硬字幕。

总计 patch 范围: **1 agent_refs amend (rule #5 + 新增 rule #12.6) + 1 spec.md FR-9/11/12/NFR-4 amend + 1 revised_prompt header + 50 shotNN.md updated + 55 seam-frame 文件 deleted (10 lastframe × 5 + 1 startframe × 5) = 108 文件改动**。

每 ep 文件数: 21 → 10。ep01-ep05 共 105 → 50。

No conflicts found in:
- `ai_videos/mozun_chongsheng/characters/{role}.md` + `characters/ref_images/{role}-立绘.md` — 不动（character pipeline 独立）。
- `ai_videos/mozun_chongsheng/scenes/`（12 文件）— 不动；shot prompt 现引用 `scenes/{name}.md` paths in Shot context 段。
- `ai_videos/mozun_chongsheng/style_guide.md` / `world.md` / `arc_outline.md` / `README.md` — 不动。
- spec-pipeline 史料（qa.md / dossier.md / angle files / validation strategy / bdd_scenarios / ai_video_specific）— 不动；validator 须扩展 schema 检查（出补丁单：NFR-12 单一自包含文件三段完整性校验）。
- ep01-ep05 的 `shotlist.md` / `episode.md` / `publish.md` — 不动。

Severity: 文件级合并 + 删除 55 文件是中等 blast radius；合并后 prompt body + seam-frame 内容 byte-identical 保留，零内容损失；新增 Shot context 段是纯 review-friendly metadata，不影响生成结果。下游不受影响。

User next steps:
1. 打开任一 `episodes/ep{NN}/prompts/shot{NN}.md` → 顶部 Shot context 段先 review（一目了然 Summary / 出场角色 / 场景 / 时长 / Reference uploads）→ 中段 copy-paste 视频 prompt 到 Seedance/Sora/Veo/Runway/Kling → 底段 copy-paste seam-frame Seedream prompt 到 Seedream/Midjourney（若需 image-to-video stitching）。
2. 文件夹简化：每 ep `prompts/` 仅 10 文件（vs 之前 21）。
3. ep06-ep60 后续 stage-4 regen 时按 rule #12.6 出文。

## Follow-up 006 — 2026-05-10 13:05:17
Source: user_input/follow_ups/006-20260510-130517-merge-shot-prompts-character-checklist.md
Summary: 在 episode 内**合并** `shotNN_kling.md` + `shotNN_seedance.md` → 单文件 `shotNN.md`（per shot 仅一个 prompt，不再分模型 variant）；新文件**顶部加 出场角色 checklist**（含 turntable reference 路径 + 是否必需上传备注）；**复用场景** section 引用 `scenes/{name}.md`；**seam-frame 输入** section 列 `input_image_urls`（移出 prompt body）；**视频 prompt body 封装在 `\`\`\`text` code fence 内 ready-to-copy-paste**。Static seam-frame prompts 不动。ep01-ep05 共合并 50 镜，删除 100 旧文件。

Auto-updated:
- `.claude/agent_refs/project/ai_video.md` — Rule #5 「Dual-prompt requirement」→「Single-prompt-per-shot requirement」（每 shot 单 `shotNN.md` + seam-frame 静帧）；Rule #12.4 文件命名约定 `shotNN_{model}.md` → `shotNN.md`；新增 video shot prompt 文件结构 schema（出场角色 checklist + 复用场景 + seam-frame 输入 + 用法 callout + ```text fenced 14-字段 prompt body）；新增 出场角色 checklist 派生规则表（正脸/主体 ✅ vs 光影/远景 ❌）。
- `specs/ai_video/mozun_chongsheng/user_input/revised_prompt.md` — Last regenerated header bumped to 2026-05-10 13:05:17 + follow-up 006 摘要。
- `specs/ai_video/mozun_chongsheng/final_specs/spec.md` — FR-9 改写为单 `shotNN.md` 文件 schema（含 出场角色 checklist / 复用场景 / seam-frame 输入 / ```text fenced prompt body）；FR-10 标注「已并入 FR-9」；NFR-4 「双管线 + seam-frame」→ 「单 prompt + seam-frame」（每镜 `shotNN.md` + `_lastframe_seedream.md`；每集首镜 `_startframe_seedream.md`）。
- `ai_videos/mozun_chongsheng/episodes/ep01/prompts/`（10 新 + 20 删）— 10 pairs 合并为 `shot01.md ... shot10.md`，删 `shot{01..10}_kling.md` + `shot{01..10}_seedance.md`。出场角色 checklist 准确派生（shot01 沧冥 ✅ 正脸 + 5 宗主 ❌ 光影；shot07 cover-frame 全员 ✅；shot08-10 单角色）。复用场景 mapping: shot01-09 → `scenes/沧冥魔域-黑金大殿长阶顶.md` (立档)；shot10 → `scenes/雪山冰原.md` (立档)。
- `ai_videos/mozun_chongsheng/episodes/ep02/prompts/`（10 新 + 20 删）— ep02 倒叙片段（白月清主导 + 沧冥）；多数 shot 在 `scenes/沧冥魔域-黑金大殿内.md` (立档)；shot02/03/09/10 「魔气长阶 山道中段平台」未立档（标 inline）。
- `ai_videos/mozun_chongsheng/episodes/ep03/prompts/`（10 新 + 20 删）— ep03 全 10 shot 在 `scenes/玄炎宗-铸器堂.md` (立档)；多数 shot 沧冥 + 赵焚天 同框 ✅。
- `ai_videos/mozun_chongsheng/episodes/ep04/prompts/`（10 新 + 20 删）— ep04 多数 shot 在 `scenes/太清门-金殿密室.md` (立档)；shot01 双 location 蒙太奇 (玄炎宗血池闪片 + 太清门殿门)；shot10 cliff 黑袍沧冥雪坡远眺 → `scenes/雪山冰原.md` 主 + 太清门 远景。
- `ai_videos/mozun_chongsheng/episodes/ep05/prompts/`（10 新 + 20 删）— ep05 转生卷开始；shot01/05 → `scenes/雪山冰原.md`；shot03/04/06/07/09/10 → `scenes/凡间小镇-破庙墙角.md`；shot02 高空云海 / shot08 蒙太奇识海未立档（标 inline）。

总计 patch 范围: **1 agent_refs amend (rule #5 + rule #12.4) + 1 spec.md FR-9/10/NFR-4 amend + 1 revised_prompt header + 50 新合并 prompts + 100 旧文件删除 = 153 文件改动 (50 新 + 100 删 + 3 文档 amend)**。

Pre-existing inconsistency carried forward (不在 follow-up 006 scope，记录在此供未来 surgical follow-up 处理):
- 沧冥 inline 体型 展开仍说「三十出头」(legacy seedance variant 文本)；follow-up 002 锁定为「看似二十五（实修千年）」。这是 follow-up 002 bulk patch 当年只覆盖了一句话锁定 + filename，未触 inline 体型展开 句的遗留问题。Merge 直接保留 seedance 原文，没引入新偏差但也未修。可在后续 surgical follow-up 中统一替换跨 50 个 `shotNN.md` 的「三十出头」为「看似二十五」。

No conflicts found in:
- `ai_videos/mozun_chongsheng/episodes/ep01..ep05/prompts/shot*_lastframe_seedream.md`（50 份）+ `shot01_startframe_seedream.md`（5 份）= 55 静帧 seam-frame 文件 — 不变（用途不同）。
- `ai_videos/mozun_chongsheng/characters/{role}.md` + `characters/ref_images/{role}-立绘.md` — 不动（character pipeline 与 shot pipeline 独立）。
- `ai_videos/mozun_chongsheng/scenes/`（12 文件）— 不动；shot prompt 现引用 `scenes/{name}.md` paths in 复用场景 section。
- `ai_videos/mozun_chongsheng/style_guide.md` / `world.md` / `arc_outline.md` / `README.md` — 不动。
- spec-pipeline 史料（qa.md / dossier.md / angle files / validation） — 不动。

Severity: 文件级合并 + 删除是中等 blast radius；合并后 prompt body 14 字段 schema 全部保留（角色 / 场景 / 镜头 / 动作 / 台词 / 节奏 / 光线 / 渲染 / 比例 / 时长 / 负向）；只是从 2 文件 / shot 收缩到 1 文件 / shot。下游不受影响。

User next steps:
1. 打开 `ai_videos/mozun_chongsheng/episodes/ep01/prompts/shot01.md`（或任一 shot）→ 看顶部「出场角色」表 → 渲染对应角色的 turntable.mp4（per follow-up 005 的 character ref_images prompts）→ 上传到 Seedance / Sora / Veo / Runway / Kling 任一视频生成模型。
2. 复制 ```text``` 代码块整段到模型 → 生成 shot 视频。
3. 可选：image-to-video 模型路径，按文件中的 `## seam-frame 输入` 行上传 PNG 作 `input_image_urls`。
4. ep01-ep05 共 50 个 shot prompt files 全部按新 schema；ep06-ep60 后续 stage-4 regen 时按 rule #12.4 v2 文件命名出文。

## Follow-up 005 — 2026-05-10 11:34:24
Source: user_input/follow_ups/005-20260510-113424-drop-image-prompt-video-only.md
Summary: Seedance 等视频模型已支持 **video-as-reference** 上传。角色参考素材文件简化为**单 prompt**：去掉 follow-up 004 的 ①号 文字生图片 prompt 块，仅保留 文字生视频 reference prompt + 5 句标准台词配音对照表。Workflow 简化：text-only prompt → 12s turntable 视频（Seedance / Sora / Veo / Runway / Kling 任选）→ 视频本身作为后续所有 shot prompt 的 reference 上传 → 形象 + 声线 + 节奏一站锁定。如需 PNG 喂仅支持 image-to-video 的旧模型，从 turntable 抽帧即可。

Auto-updated:
- `.claude/agent_refs/project/ai_video.md` — rule #12.5 改为 v2 单 prompt schema：drop ①号 文字生图片 prompt 块；H2 重命名为 `## 文字生视频 reference prompt — Seedance / Kling / Sora / Veo / Runway Gen-3（360° 转身样片 + 标准台词）`（model 列表把 Seedance 提前 + 加 Runway Gen-3）；用法 callout 简化为单行（直接 paste 到支持 video reference 的 AI 视频模型）；与 rule #12.2 关系改为「rule #12.5 v2 完全 supersedes rule #12.2」（rule #12.2 不再生效；character pipeline 不再独立生成 image prompt 文件）。
- `specs/ai_video/mozun_chongsheng/user_input/revised_prompt.md` — Last regenerated header bumped to 2026-05-10 11:34:24 + follow-up 005 摘要 + follow-up 004 标注「部分 superseded」（①号 image prompt 块已删；②号 video prompt + 5 句台词 + Turntable 锁定字段保持有效）。
- `specs/ai_video/mozun_chongsheng/final_specs/spec.md` — FR-26 改为单 prompt 描述：drop ①号 文字生图片 prompt 字段说明；保留 ②号 video reference prompt 字段（场景 / 镜头 / 光线 / 节奏 / 渲染样式 / 比例 / 时长 / 视频专属负向 8 字段对所有 10 角色 byte-identical；`角色:` per rule 12.4-A inline 展开；5 句台词 character-specific）；新增「Workflow」段说明 turntable 视频闭环作为 shot reference 的 v2 流程；filename legacy alias 接受。
- `ai_videos/mozun_chongsheng/characters/ref_images/{role}-立绘.md`（10 份）— 全部按 rule #12.5 v2 schema 重写：① H1 后缀 `— 参考素材双 prompt` → `— 视频 reference prompt`；② file_说明 callout 改为「本文件含一段可直接 copy-paste 的视频 reference prompt」；③ 删除整个 ①号 文字生图片 prompt 块（H2 + 用法 callout + ```text image prompt body + 闭合 fence + 后置 `---` divider 之前的全部内容）；④ ②号 H2 重命名（drop `2️⃣` 编号 + 模型列表把 Seedance 提前 + 加 Runway Gen-3）；⑤ ②号 用法 callout 简化为单行；⑥ origin italic note 更新为 `follow-up 004 + 005`。**②号 prompt 代码块 + 5-line table + 配音参考 footer 全部 byte-identical**——Turntable 锁定字段（场景 / 镜头 / 光线 / 节奏 / 渲染样式 / 比例 / 时长 / 视频专属负向 + 5 句台词）跨 follow-up 不漂移。方鼎元 / 柳红袖两份文件的额外 follow-up 002 callout 行（`> **外貌重大调整**` / `> **服饰锁定**`）保留为 file_说明 callout 的 continuation。

总计 patch 范围: **1 agent_refs amend (rule #12.5 → v2) + 1 spec.md FR-26 amend + 1 revised_prompt header + 10 角色文件 6-step 重写 = 13 文件改动**。

No conflicts found in:
- `ai_videos/mozun_chongsheng/characters/{role}.md`（10 角色 bible）— bible 是 reference 源，本 follow-up 不修改 bible。
- `ai_videos/mozun_chongsheng/episodes/ep01..ep05/prompts/*.md`（155 shot prompt 文件）— shot prompts 引用 character 一句话锁定（byte-identical），本 follow-up 仅改文件级 schema，不改 ②号 prompt 代码块内容；shot prompts 无须 patch。
- `ai_videos/mozun_chongsheng/scenes/`（12 场景文件）— 场景层独立。
- `ai_videos/mozun_chongsheng/style_guide.md` / `world.md` / `arc_outline.md` / `README.md` — 无内容修改。
- `interview/qa.md` / `findings/dossier.md` / 5 angle files — spec-pipeline 史料。
- `validation/strategy.md` / `bdd_scenarios.md` / `ai_video_specific.md` — validation 字段集是 ②号 video prompt 字段的子集；现有 acceptance criteria 全部仍生效。

Severity: 单 prompt 简化是**减法 + 重命名**，没有引入新内容，不影响下游 shot pipeline。本 follow-up 完成后用户可一次 copy-paste 出 12s turntable 视频，整个 character pipeline 从 dual-step（PNG 立绘 → turntable 视频）collapsed 为 single-step（直接 turntable 视频）。

User next steps:
1. 用 10 份新 single-prompt 文件的代码块在 Seedance（首选，原生支持 video reference）/ Sora / Veo 3 / Runway Gen-3 / Kling 渲染 12s turntable 视频，输出到 `ai_videos/mozun_chongsheng/characters/ref_videos/{中文名}-{身份}-转身样片.mp4`（注：`ref_videos/` 子目录目前不存在，渲染时手动创建）。
2. 后续 ep01-ep05 / ep06-ep60 shot prompt 在生成视频时上传该角色的 turntable.mp4 作为 video reference，让形象 + 声线 + 节奏自动锁定。
3. 如需 PNG 喂仅支持 image-to-video 的旧模型路径（如 Kling 早期版本），从 turntable 抽 0s 正面帧即可，无需独立 image prompt。
4. 5 句标准台词在配音演员录制时按文件内的对照表录 5 个 take，作为人工配音 / TTS 训练的声线 baseline。

## Follow-up 004 — 2026-05-10 10:36:01
Source: user_input/follow_ups/004-20260510-103601-character-dual-prompt.md
Summary: 角色 reference 文件升级为同文件内**双 copy-paste prompt**：① 文字生图片 prompt（Seedream / Midjourney / Imagen / Flux）+ ② 文字生视频 reference prompt（Kling / Sora / Veo / Seedance；12s 360° 棚拍 turntable + 5 句中文标准台词）。新增 rule #12.5；10 个 mozun 角色文件全部按新 schema 重写；filename 沿用 legacy alias `-立绘.md`。

Auto-updated:
- `.claude/agent_refs/project/ai_video.md` — 新增 rule #12.5「角色 reference 双 prompt 文件」：双 prompt 文件 schema + 5 句标准台词设计原则（第 1 句 `"我是{name}。"` byte-template / 第 2 句 = bible 标志台词 verbatim / 第 3 句低声内敛 derived from 性格反差 / 第 4 句高声爆发 derived from 弧光关键拐点 / 第 5 句 `"一、二、三、四、五。"` byte-fixed）+ Turntable 锁定字段（场景 / 镜头 / 光线 / 节奏 / 渲染样式 / 比例 / 时长 / 视频专属负向 8 字段对所有角色 byte-identical；中性灰 #808080 cyc + 三点布光 5500K/4500K/7000K + 标头中景 70mm + 360° 顺时针 12s）+ v1 visual-only ↔ v2 audio-aware 模型路径切换说明 + rule #12.5 与 rule #12.2 关系（前者外层 wrap，后者仍生效在 ①号 prompt 内容级别）。
- `specs/ai_video/mozun_chongsheng/user_input/revised_prompt.md` — Last regenerated header bumped to 2026-05-10 10:36:01 + follow-up 004 摘要。
- `specs/ai_video/mozun_chongsheng/final_specs/spec.md` — FR-26 重写：从「Seedream 立绘单 prompt 模板」→「角色 reference 双 prompt 文件（rule #12.5）」，列明 ①号 image prompt 字段（保留 follow-up 001 真人写实 + follow-up 002 服饰约束）+ ②号 video prompt 字段（场景 / 镜头 / 光线 / 渲染 / 比例 / 时长 八字段 byte-identical；角色 / 动作 / 5 句台词随角色变化）+ 5 句台词配音对照表 + filename legacy alias 显式接受。
- `ai_videos/mozun_chongsheng/characters/ref_images/沧冥-魔尊本相-立绘.md` — 重写为 canonical example（双 prompt + 5 句台词 + 配音参考表）。沧冥 5 句台词：「我是沧冥。」/「当年你们怎么对我，今日我便十倍奉还。」（标志）/「魂火不灭，便是归期。」（低声）/「我必让你魂飞魄散！」（高声）/「一、二、三、四、五。」（节奏校准）。
- `ai_videos/mozun_chongsheng/characters/ref_images/{role}-立绘.md`（其余 9 份：叶无尘 / 苏璃月 / 柳红袖 / 苓夭夭 / 白月清 / 赵焚天 / 方鼎元 / 韩夺心 / 司空玄）— 按沧冥 canonical 模板重写。每份 ①号 image prompt 保留所有原有 8 子段视觉内容（扁平化为 inline `Section: content` 行）+ 项目级 14 项 stylization 负向 + 角色专属负向；②号 video prompt 7 字段 byte-identical（仅光晕段每角色 signature：苏璃月仙气 / 赵焚天暗血红火焰 / 方鼎元紫金 / 韩夺心剑光银白 / 司空玄暗紫影气 / 其余 drop trailing 光晕 sentence）+ 角色 byte-identical inline 展开（一句话锁定 + 体型 / 发型 / 服装 / 道具 / 瞳色）+ 5 句台词 character-specific（如苏璃月「今日，由我来守这天下！」/ 司空玄「你以为，他就清白么？」承接 ep04 H6 撕脸功能 / 柳红袖「红袖招今日就关了，但你也别想活着出去！」/ 等）。

总计 patch 范围: **1 agent_refs amend (rule #12.5 NEW) + 1 spec.md FR-26 amend + 1 revised_prompt header + 10 角色双 prompt 文件 rewrite (1 沧冥 canonical + 9 subagent batch) = 13 文件改动**。

No conflicts found in:
- `ai_videos/mozun_chongsheng/characters/{role}.md`（10 角色 bible）— rule #12.5 ②号 prompt 引用 bible 的 一句话锁定 / 标志台词 / 配音参考 / 性格 / 弧光，但不修改 bible 本身。bible 是 reference 源，dual-prompt 文件是 derived。
- `ai_videos/mozun_chongsheng/episodes/ep01..ep05/prompts/*.md`（155 shot prompt 文件）— shot prompts 引用 character ref via 一句话锁定（byte-identical），rule #12.5 保留沧冥 / 各角色的一句话锁定不变；shot prompt 无须 patch。
- `ai_videos/mozun_chongsheng/scenes/`（12 场景文件，follow-up 003 创建）— 场景层与角色层独立，不交叉。
- `ai_videos/mozun_chongsheng/style_guide.md` / `world.md` / `arc_outline.md` / `README.md` — rule #12.5 引用 style_guide.md § 负向锁定 / § 正向关键词，无内容修改。
- `interview/qa.md` / `findings/dossier.md` / 5 angle files — spec-pipeline 史料，不修改 historical record。
- `validation/strategy.md` / `bdd_scenarios.md` / `ai_video_specific.md` — validation 按 glob 模式 + 字段名校验，dual-prompt schema 是 ①号 prompt 字段的 superset；现有 acceptance criteria 全部仍生效。stage-6 validator 须扩展认知 ②号 video prompt 字段（出补丁单：新增 NFR-11 dual-prompt 文件双块完整性校验）。

Severity: 角色 ref 升级为 dual-prompt 是中等 blast radius 改动，仅影响 character pipeline，不触及 shot 层。本 follow-up 完成后用户可直接 copy-paste 出 PNG（用 ①号 prompt）和 12s turntable 视频（用 ②号 prompt + ①号生成的 PNG）。后续 ep06-ep60 stage-4 regen 时新增角色按 rule #12.5 出 dual-prompt 文件。

User next steps:
1. 用 10 份新 dual-prompt 文件的 ①号 image prompt 在 Seedream（或 Midjourney / Imagen / Flux）渲染立绘 PNG，输出到 `ai_videos/mozun_chongsheng/characters/ref_images/{中文名}-{身份}-立绘.png`（与 .md 同级）。
2. 用 ②号 video prompt + 步骤 1 的 PNG 在 Kling 2.1 Pro 渲染 12s turntable 视频，输出到 `ai_videos/mozun_chongsheng/characters/ref_videos/{中文名}-{身份}-转身样片.mp4`（注：`ref_videos/` 子目录目前为空，需手动创建或在视频管线生成时一并创建）。
3. 进入 v2 audio-aware 模型路径（Veo 3 / Sora-audio / Runway Gen-3）后，turntable 视频可作为 video-to-video reference 输入，生成的 shot 视频会保留角色的视觉 + 声线一致性。
4. 5 句标准台词在配音演员录制时按文件内的对照表录 5 个 take，作为人工配音的声线 baseline。

## Follow-up 003 — 2026-05-10 09:50:45
Source: user_input/follow_ups/003-20260510-095045-model-agnostic-templates.md
Summary: 两件事：(A) `agent_refs/project/ai_video.md` rule #12 抽象为 model-agnostic「视频 shot prompt + 静帧 seam-frame prompt」二件套（取消 Kling/Seedance/Seedream 三列分裂；新增 12.4-A 角色字段展开规则：参考图存在 ⇒ 一句话锁定；参考图缺失 ⇒ 一句话锁定 + 体型/发型/服装/道具 inline 展开）；(B) 把新模板回填到 mozun_chongsheng 现有 artifacts —— 角色档补齐 4 段 / 立绘按 8 子段重排 / 100 视频 shot prompt 补齐 `台词 / 字幕:` + `节奏:` 字段 / 新增 `scenes/` 复用场景层 6 对文件。

Auto-updated:
- `.claude/agent_refs/project/ai_video.md` — rule #12.4 重写为 2 列矩阵（视频 shot vs 静帧 seam）；新增 12.4-A 角色字段展开规则（按参考图存在与否分支，model-agnostic）；rule #12 跨模板不变量补一条「模板 model-agnostic」；rule #12 文件命名约定改为 `shotNN_{model}.md` 通用形式；rule #12.4 cross-reference 段补 rule #5 dual-prompt 政策与 12.4 schema 的关系。
- `specs/ai_video/mozun_chongsheng/user_input/revised_prompt.md` — Last regenerated header bumped to 2026-05-10 09:50:45 + follow-up 003 摘要。
- `specs/ai_video/mozun_chongsheng/final_specs/spec.md` — FR-9 / FR-10 amend：Kling/Seedance variant schema 一致，差异仅来自参考图存在与否；FR-24 改写为 model-agnostic 视频 shot prompt 模板（含 `台词 / 字幕:` + `节奏:` + 12.4-A 展开规则）；FR-25 标注「已并入 FR-24」并保留 Seedance variant 的 `负向:` 段说明。
- `ai_videos/mozun_chongsheng/characters/*.md`（10 份）— 每份 append 4 个新 H2：`性格 / 动机`（核心动机/表层人设/反差点/关键弱点）、`标志台词或口头禅`（1-3 byte-stable Chinese 短句；沧冥含「当年你们怎么对我，今日我便十倍奉还」）、`配音参考`（声线/语速/口音/演员参考，planning-only）、`负向`（re-paste style_guide.md § 负向锁定 + 角色专属，如柳红袖「不要肚兜/露肩/露胸」per follow-up 002，方鼎元「不要鹤发/银白长须」per follow-up 002）。
- `ai_videos/mozun_chongsheng/characters/ref_images/*-立绘.md`（10 份）— 每份 `## Prompt` 段重排为 8 子段：`### 主体 / 构图`、`### 面部`、`### 服装`、`### 姿态`、`### 背景`、`### 光源`、`### 风格`，原 `## 负向` / `## 负向 / 避免` 保留。LOCKED 一句话开头 byte-identical 保留为 `## Prompt` 第一行。所有 hex / 类比 / 服化道描述完整保留——纯 schema 重排。
- `ai_videos/mozun_chongsheng/episodes/ep01..ep05/prompts/shot{NN}_kling.md`（50 份）+ `shot{NN}_seedance.md`（50 份）= 100 视频 shot prompt — 每份在 `光线/色调:` 行前插入两行：`台词 / 字幕: <三选一>`（内嵌硬字幕 / 后期软字幕 / 无台词 默剧）+ `节奏: <四选一>`（慢 / 中 / 快 / 顿挫）。Kling + Seedance variant 共享同一 `台词 / 字幕` + `节奏` 值（这两个是内容属性，不是模型属性）。台词原文从 episode.md / shotlist.md 提炼，例：ep01 shot06 内嵌「当年你们怎么对我，今日我便十倍奉还」；ep05 shot10 内嵌「……我……回来了。」cliffhanger。INSERT-only：existing 角色 / 场景 / 动作 / 镜头 / 光线/色调 / 渲染样式 / 比例 / 时长 / 负向 全部 byte-identical。
- `ai_videos/mozun_chongsheng/scenes/`（NEW，6 对 = 12 文件）+ `scenes/ref_images/`（NEW）— scan 5 个 shotlist.md 识别 ≥ 2 shots 复用的 location，按 rule #12.3 创建场景档（8 字段锁定描述符 + 关键变化态 + 出现镜头 + 负向）+ 场景立绘 prompt（主体/构图、视角、时辰、背景、光源、风格、负向）。Top-6 reused locations: 玄炎宗-铸器堂（11 shots）/ 太清门-金殿密室（11 shots）/ 沧冥魔域-黑金大殿长阶顶（10 shots）/ 凡间小镇-破庙墙角（6 shots）/ 沧冥魔域-黑金大殿内（5 shots）/ 雪山冰原（4 shots）。Skip: 仅 1 shot 出现的 location（如 ep05/shot02 高空云海）。Shot prompts 暂未改 `场景:` 行（保留 inline 描述，未来 stage-6 regen 可改 byte-identical 引用 `scenes/{name}.md` 一句话锁定）。

总计 patch 范围: **10 角色档 append + 10 立绘 restructure + 100 视频 shot prompt insert + 12 新场景文件 + 1 agent_refs amend + 1 spec.md amend + 1 revised_prompt header bump = 135 文件改动**。

No conflicts found in:
- `ai_videos/mozun_chongsheng/episodes/ep01..ep05/prompts/shot*_lastframe_seedream.md`（50 份）+ `shot01_startframe_seedream.md`（5 份）—— rule #12.4 静帧列不要求 `台词 / 字幕:` + `节奏:`，无须 patch。
- `world.md` / `arc_outline.md` / `style_guide.md` / `README.md` —— 模板抽象不影响内容；style_guide.md § 负向锁定 / § 调色锁定 / § 字幕规范 全部被新模板 re-paste 引用，rule 路径合法。
- `interview/qa.md` / `findings/dossier.md` / 5 angle files —— spec-pipeline 史料，不修改 historical record。
- `validation/strategy.md` / `bdd_scenarios.md` / `ai_video_specific.md` —— validation 按 glob 模式与字段名校验，rule #12.4 新增字段 `台词 / 字幕:` + `节奏:` 仅扩充必填集；现有 acceptance criteria（AC-1..AC-7）仍有效。stage-6 regen 时 validator 需扩展 schema（出补丁单：新增 NFR-10 字段必填校验）。

Severity: 模板抽象 + schema 字段扩充是中等 blast radius 改动；本 follow-up 完成后 ep01-ep05 的 100 视频 shot prompt + 10 角色档 + 10 立绘 + 6 场景对全部对齐 rule #12。后续 ep06-ep60 的 stage-4 regen 会按新 schema 出文，无需迁移。

User next steps:
1. 检查 6 个新 `scenes/{location}.md` 文件的 `锁定描述符 #8 一句话锁定` 行；如满意则在未来 ep01-ep05 stage-6 regen 时把 shot prompts 的 `场景:` 行换成 byte-identical 引用。
2. 检查 100 视频 shot prompt 新增的 `台词 / 字幕:` + `节奏:` 字段；任何不准确的台词原文 / 字幕方式 / 节奏档位可单点 follow-up 修正（无需重 regen）。
3. 用更新后的 10 立绘 + 6 场景立绘在 Seedream 重新生成 PNG（如有视觉漂移，重渲为推荐路径；模板已对齐 rule #12.2 / #12.3 但旧 PNG 仍 usable）。
4. ep06-ep60 stage-4 regen 时按新 model-agnostic 模板出文（rule #12.4 二件套 schema 已就位）。

## Follow-up 002 — 2026-05-09 19:48:37
Source: user_input/follow_ups/002-20260509-194837-younger-and-chinese-filenames.md
Summary: 三件事：(a) 角色年龄观感全面下调到 18-35 看似青春，加 俊朗/貌美/英气 关键词；(b) 服饰升级（锦缎/绣纹），柳红袖（老板娘）由肚兜（暴露）改为朱红绫上襦 + 锦缎围裙（妖娆但不暴露），方鼎元由鹤发银白长须改为乌发玉簪三缕短须；(c) 全部角色文件改用中文名命名（`沧冥-魔尊本相.md` 等），便于 ai_video_management webapp 识别。

Auto-updated:
- `.claude/agent_refs/project/ai_video.md` — 规则 1 amend：允许 ai_videos/{name}/characters/ 等"内容性"文件中文 opt-in 命名（结构性文件如 shotlist.md/episode.md 仍 English/pinyin；task_name 仍硬性 pinyin/English）。
- `specs/ai_video/mozun_chongsheng/user_input/revised_prompt.md` — Last regenerated header bumped。
- `specs/ai_video/mozun_chongsheng/final_specs/spec.md` — FR-5 / FR-6 amend：列出 10 个新 Chinese 文件名 + 强调 18-35 年龄观感锁定 + 柳红袖服饰约束。
- `specs/ai_video/mozun_chongsheng/validation/acceptance_criteria.md` — AC-7 amend：10 个 ref_images 期望文件名改为中文。
- `ai_videos/mozun_chongsheng/characters/` — 10 个角色文件 删除旧英文命名，重写为中文命名 + 新 lock 描述符（沧冥-魔尊本相.md / 叶无尘-乞丐转生.md / 苏璃月-紫霄圣女.md / 柳红袖-红袖招老板娘.md / 苓夭夭-药王谷医师.md / 白月清-紫霄宫主.md / 赵焚天-玄炎宗主.md / 方鼎元-太清掌教.md / 韩夺心-万剑宗主.md / 司空玄-影神殿主.md）。
- `ai_videos/mozun_chongsheng/characters/ref_images/` — 10 个 Seedream 立绘 prompt 删除旧英文命名，重写为中文命名 + 新 lock 描述符 + 严格不要肚兜/抹胸/露肩约束（柳红袖）。
- `ai_videos/mozun_chongsheng/episodes/ep01..ep05/prompts/*.md` — Python bulk patch：(1) 277 处 OLD 锁定句 → NEW 锁定句 byte-identical 替换跨 100 个 shot prompts；(2) 31 处 OLD 文件名路径 → NEW 中文路径替换。
- `ai_videos/mozun_chongsheng/README.md` — 角色清单表 + 项目目录结构图 全部用中文文件名。

总计 patch 范围: **10 新角色 .md + 10 新 ref_images + 173 文件 patched (277 lock + 31 filename) + 4 spec/validation/agent_refs amend + 20 旧英文文件 deleted = 217 文件改动**。

No conflicts found in: world.md / arc_outline.md / style_guide.md（无 lock 字符串、无具体英文角色文件名引用，bulk script 已自动处理少量提及，验证通过）, qa.md / dossier.md / 5 angle files（这些是 spec-pipeline 史料；不修改 historical record）, validation/strategy.md + bdd_scenarios.md + ai_video_specific.md（angle 验证逻辑与文件名解耦，按 glob 模式而非 hardcoded 文件名）。

User next steps:
1. 用更新后的 10 份 `characters/ref_images/{中文名}-{身份}-立绘.md` 在 Seedream 重新渲染立绘 PNG（输出文件名建议：`沧冥-魔尊本相.png` 等）。
2. 用新立绘 PNG 替换 Kling 的 `input_image_urls`。
3. 重新跑 ep01-ep05 的 100 镜 Kling + Seedance 视频（lock 描述符已更新；新人物外貌：青春帅气/貌美/锦缎服饰/柳红袖不暴露）。
4. 在 ai_video_management webapp 打开 `ai_videos/mozun_chongsheng/characters/` 时一眼可见 10 个中文文件名。

Severity: 角色重命名 + lock 描述符变更是中等 blast radius 的改动；本 follow-up 完成后 ep01-ep05 的 100 个 shot prompt 已全部同步。后续 ep06-ep60 的 stage-4 regen 会沿用 spec FR-5/FR-6 锁定（包括中文文件名 opt-in 与 18-35 年龄观感锁定），不会再漂回。

## Follow-up 001 — 2026-05-09 19:26:14
Source: user_input/follow_ups/001-20260509-192614-realism-style-fix.md
Summary: 渲染样式从 "传统中国仙侠插画 + 国漫风格 + 工笔精绣 + 水墨写意"（stage 6 U1 默认）翻转为 **影视级真人写实 + cinematic + 4K HDR + live-action 仙侠古装真人剧造型**。原因：用户反馈现有 Seedream 立绘 prompt 输出的 PNG 是漫画 / 插画风格而非真人。根因——10 份 ref_images 的"风格"段含 "国漫 / 插画 / 工笔 / 水墨写意" 关键词，让 Seedream 渲染为 2D stylized 输出；Kling image-to-video 又以这些 PNG 为 ref，自动继承漫画感。同时发现 ep01/shot01 Seedance prompt 误把 "**写实毛孔皮肤瑕疵**" 当作要避免的内容（应为正向需求）。

Auto-updated:
- specs/ai_video/mozun_chongsheng/user_input/revised_prompt.md — 新增 "Last regenerated: 2026-05-09 19:26:14" 头，记录渲染样式锁定 follow-up 001。
- specs/ai_video/mozun_chongsheng/final_specs/spec.md — FR-3 amend（style_guide.md 必含 渲染样式锁定 段）；FR-26 amend（Seedream 立绘"风格"段必为 影视级真人写实，"负向"段必含 anime / cartoon / illustration 等 14 项 stylization 负向）；FR-27 amend（seam-frame Seedream prompt 必含 渲染样式 行）。
- ai_videos/mozun_chongsheng/style_guide.md — 在文件最前面新增 "渲染样式锁定" 段：(a) 正向关键词清单（cinematic / photorealistic / live-action / 4K HDR / 仙侠古装真人剧造型 等）、(b) 负向关键词清单（anime / cartoon / illustration / chibi / 国漫 / 插画 / 工笔 等 14 项）、(c) 类比参考剧（《琉璃》《长月烬明》《苍兰诀》等 live-action 真人剧）、(d) Seedream 立绘四段式更新模板、(e) Kling/Seedance 渲染样式锚点行格式、(f) 严禁 "避免: 写实毛孔皮肤瑕疵" 反向写实表述的 canonical 警告。
- ai_videos/mozun_chongsheng/characters/ref_images/*_seedream.md — 全部 10 份重写：
  - "风格" 行: `传统中国仙侠插画 + 国漫风格 + Character design + 高细节服化道，水墨写意 + 工笔精绣` → `影视级真人写实 + 4K HDR cinematic + 仙侠古装真人剧造型 + 8K 写实人像摄影 + 真实皮肤布料质感 + 实拍剧照风`
  - 类比参考保留（《琉璃》《长月烬明》《苍兰诀》等真人剧），追加 "（live-action）" 标注
  - "负向 / 避免" 段前置追加 14 项 stylization 负向（anime / cartoon / illustration / chibi / manga / 国漫 / 插画 / 工笔 / 水墨写意 / 二次元 / CGI 3D render / 塑料皮肤 / 玩偶感 / 卡通色），原有项目通用负向（不要现代服饰 / 西方面孔 / 文字水印 / 多余手指 等）保留。
- ai_videos/mozun_chongsheng/episodes/ep01/prompts/shot01_seedance.md — 删除 "避免:" 段中错误的 "写实毛孔皮肤瑕疵" 项（这是 stage 6 worker 把"写实"当成要避免的内容，与本剧"真人写实"目标冲突）。
- ai_videos/mozun_chongsheng/episodes/ep{01..05}/prompts/shot{NN}_kling.md（50 份）— 每份在"光线/色调"行后追加 `渲染样式: 影视级真人写实 + cinematic + 4K HDR` 锚点行；末尾追加 `负向:` 行（如缺失）含 14 项 stylization 负向。
- ai_videos/mozun_chongsheng/episodes/ep{01..05}/prompts/shot{NN}_seedance.md（50 份）— 每份在"光线/色调"行后追加 `渲染样式: 影视级真人写实 + cinematic + 4K HDR + 真实皮肤质感` 锚点行；"避免:" 段补加 14 项 stylization 负向（已有的项目通用负向保留）。
- ai_videos/mozun_chongsheng/episodes/ep{01..05}/prompts/shot{NN}_lastframe_seedream.md + shot01_startframe_seedream.md（共 55 份）— 每份末尾追加 `渲染样式: 影视级真人写实 + cinematic + 4K HDR + 真实皮肤质感 + 实拍剧照风` + `负向:` 行（含 14 项 stylization 负向）。

总计 patch 文件: **10 ref_images + 1 anti-realism bug fix + 50 Kling + 50 Seedance + 55 Seedream seam-frame + 1 spec.md + 1 style_guide.md + 1 revised_prompt.md = 169 文件**。

No conflicts found in: characters/{role}.md（10 字段锁定描述符不含 style 关键词，无需改动）, world.md（无 style 关键词）, arc_outline.md（无 style 关键词）, README.md（无 style 关键词）, interview/qa.md（stage 2 决策："美学 / 调色 / 角色锁定" 都没规定渲染样式，只规定了"传统仙侠 + 黑金沉郁"美学方向，与"真人写实"渲染样式正交，二者不冲突——可同时存在）, findings/dossier.md + 5 angle files（research 阶段未触及渲染样式选择，仅讨论调色 / 镜头语言 / 命名 / 节奏 / 平台规范）, validation/strategy.md + 3 level files（无渲染样式 level；现有 ai_video.md 8 levels 仍全部适用——AC-3 角色一致性的 byte-identical 锁定描述符不变，AC-5 比例 + 避免段保留并扩充）。

User next steps:
1. 用更新后的 10 份 `characters/ref_images/*_seedream.md` 在 Seedream 重新渲染立绘 PNG。
2. 用新立绘 PNG 替换 Kling image-to-video 的 input_image_urls。
3. 用更新后的 100 份 shot prompt 重新跑 Kling/Seedance 视频渲染（约 ep01-ep05 = 100 镜的视频）。
4. 第一批渲染完成后做一次"manual walkthrough"：随机抽 2-3 镜验证输出是否真人 / 影视级，然后再批量推进到剩余集数。

Severity: 渲染样式偏漂是 **blocker** 等级（影响所有视觉输出），但本 follow-up 完成后已彻底修复；后续 stage-4 regen for ep06-ep60 会沿用 spec FR-26/FR-27 锁定 + style_guide.md 渲染样式锁定 段，不会再次漂移。
