# Follow-up draft 002 — 2026-05-09

Summary: 三件事一并办：(a) 人物年龄观感全面下调，加 帅气 / 俊朗 / 貌美 / 英气 关键词；(b) 服饰整体上档次（锦缎 / 绣纹），尤其 老板娘柳红袖 由"朱红绣肚兜"（暴露）改为"朱红绫上襦 + 锦缎围裙"（妖娆但不暴露）；(c) 全部角色文件改用 中文名 命名（`沧冥-魔尊本相.md` 等）便于在 ai_video_management webapp 一眼识别。

## 用户原话

> 人物要长得青春帅气或貌美一点，不要显得太老，还有再ai_video_management里面，产生的artfacts可以以中文名命名，我好知道哪个文件对应的是哪个人物。还有穿着也要上档次一点， 比如老板年可以妖娆但不能太暴露

## (A) 角色年龄向下调

| 角色 | follow-up 001 后年龄 | 002 新年龄观感 |
|---|---|---|
| 沧冥 (魔尊本相) | 三十出头 | 看似二十五（实修千年）|
| 叶无尘 (乞丐) | 十七八 | 十八（不变）|
| 苏璃月 (圣女) | 二十出头 | 十九 |
| 柳红袖 (老板娘) | 二十六七 | 二十二 |
| 苓夭夭 (药王谷) | 二十一二 | 十八 |
| 白月清 (紫霄宫主) | 五十出头但养颜如三十 | 看似三十（实修四百年）|
| 赵焚天 (玄炎宗主) | 四十五左右 | 看似三十五 |
| 方鼎元 (太清掌教) | 六十五左右（鹤发银白长须） | 看似四十（去鹤发 / 银白长须，改三缕短须）|
| 韩夺心 (万剑宗主) | 四十出头 | 看似三十 |
| 司空玄 (影神殿主) | 三十五左右 | 看似三十（已合适）|

仙侠惯例支持："修为不老" — 渡劫期巅峰修为者外貌冻龄是合理的，反派 5 宗主仍是 几百年 修为底子，只是观感年轻。

## (B) 服饰升级

通用替换：
- "广袖" → "锦绣广袖"
- "长袍" → "锦缎长袍"
- "道袍" → "锦缎道袍"
- "炼器袍" → "锦缎炼器袍"
- "披风" → "锦缎披风"
- "绣领" → "云纹绣领" (已用)

**关键改动 · 柳红袖 老板娘**：

| 项 | 旧 | 新 |
|---|---|---|
| 上身 | 朱红绣肚兜（直接露肩 + 锁骨） | **朱红绫上襦** (高领 + 长袖 + 锦绣腰封) |
| 外罩 | 浅黄围裙 | **浅黄锦缎围裙** |
| 下身 | 黑色绑腿裤 | 黑色绑腿裤（保留） |
| 整体 | 暴露感强 | **妖娆 (腰肢)、典雅 (锦缎)、不暴露** |

视觉关键词：曲线柔美 / 锦缎光泽 / 腰肢纤盈 / 唇红肌雪 — 妖娆 = 通过腰肢曲线 + 步态 + 唇眼神情，而非露胸露肩。

## (C) 中文文件命名

所有 `characters/*.md` + `characters/ref_images/*_seedream.md` 改为 中文名 + 角色身份。命名格式：`{中文名}-{身份标签}.md` (角色文件) / `{中文名}-{身份标签}-立绘.md` (ref_image)。

| 旧 (English/pinyin) | 新 (中文) |
|---|---|
| `characters/沧冥-魔尊本相.md` | `characters/沧冥-魔尊本相.md` |
| `characters/叶无尘-乞丐转生.md` | `characters/叶无尘-乞丐转生.md` |
| `characters/苏璃月-紫霄圣女.md` | `characters/苏璃月-紫霄圣女.md` |
| `characters/柳红袖-红袖招老板娘.md` | `characters/柳红袖-红袖招老板娘.md` |
| `characters/苓夭夭-药王谷医师.md` | `characters/苓夭夭-药王谷医师.md` |
| `characters/白月清-紫霄宫主.md` | `characters/白月清-紫霄宫主.md` |
| `characters/赵焚天-玄炎宗主.md` | `characters/赵焚天-玄炎宗主.md` |
| `characters/方鼎元-太清掌教.md` | `characters/方鼎元-太清掌教.md` |
| `characters/韩夺心-万剑宗主.md` | `characters/韩夺心-万剑宗主.md` |
| `characters/司空玄-影神殿主.md` | `characters/司空玄-影神殿主.md` |
| `characters/ref_images/{X}_seedream.md` | `characters/ref_images/{中文名}-{身份}-立绘.md` (10 份) |

**与 `agent_refs/project/ai_video.md` 规则 1 的关系**: 该规则原本要求"folder/file names inside ai_videos/{name}/ 是 English/pinyin"。本 follow-up 在两个层面处理:
1. 在 `mozun_chongsheng` 项目下记录 divergence note (per CLAUDE.md "Per-project deviations live in specs/ai_video/{name}/ with a divergence note")
2. 同步 amend `agent_refs/project/ai_video.md` 规则 1 to allow Chinese filenames as an option (broader institutional update — 现代 Windows + git 已能稳定处理 UTF-8 路径，原"clean tooling"理由不再 strict)

## (D) 锁定描述符更新（byte-identical 重锚）

每个角色的 第 10 字段"一句话锁定" 在加 俊朗 / 貌美 / 英气 / 锦缎 等关键词后会变化。所有 `episodes/ep01..ep05/prompts/shot{NN}_kling.md` + `_seedance.md` 中的 `角色:` 行需要 byte-identical 同步。

10 个 OLD → NEW lock string 由 Python 脚本批量 find/replace 到 100+ shot prompts。

## 期望行为

1. ai_video_management webapp 打开 `ai_videos/mozun_chongsheng/characters/` 时直接看到中文文件名（"沧冥-魔尊本相.md" / "苏璃月-紫霄圣女.md" 等）。
2. 渲染立绘时，新 lock 描述触发 Seedream 输出更年轻 / 帅气 / 貌美 / 锦绣服饰的 PNG。
3. Kling/Seedance 视频跟随新立绘 PNG 与新 prompt 文本，整体观感年轻化、上档次化、柳红袖不再暴露。
4. 现有 follow-up 001 锁定的"影视级真人写实"渲染样式 不变。

## Out of scope

- 不重写 world.md / arc_outline.md / style_guide.md（仅做引用路径更新；故事 / 调色 / 节奏不变）
- 不调整 60 集大纲 / 修为 / 钩列表 / 卷边界
- 不改 follow-up 001 锁定的渲染样式（继续 真人写实 / cinematic / live-action）
- 不改抖音 + YouTube Shorts 发布平台 / publish.md 模板
