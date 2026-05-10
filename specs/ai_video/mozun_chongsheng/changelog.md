# Changelog — mozun_chongsheng

Append-only follow-up audit log。每条记录该 follow-up 改了什么、哪些下游 artifact 被同步 surgical patch。

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
