# Follow-up draft 015 — 2026-05-10

Summary: 把所有用于"建模"角色 / 场景的 reference 视频 prompt 时长从 12s 压到 **2.9s**（Seedance 等下游视频模型的 video reference 上传约束）。角色 turntable 5 句多情绪台词 → "1, 2, 3" 三个数字（byte-identical 跨所有角色，仅作声线 timbre + 咬字基线 anchor）；动作 beats 重排为 全身远景定场 + 360° 快环 + 面部中近景推近 三段，最大化 2.9s 内信息密度。**新增**：场景 reference 视频 prompt 段（rule #12.10）— 与 Seedream 立绘 image prompt 并存于场景文件，2.9s 内 广角全景 + 中景横移 + 长焦推近 三段，为 Seedance 提供场景 video reference。

## 用户原话

> 把所有用于生成人物和场景的视频prompt压缩为2.9秒，所以可能他们之说1，2，3，4，5之类的就好了，你自行决定，重点是生成的视频要给seedance足够的reference理解人物的长相，全貌，声音

> 现在我用你的prompt生成的视频大概是12~15秒，由于上传视频的限制，我为每个人物和背景建模的视频最好限制在2.9秒内

## 决策

- **2.9s 硬上限来源**：Seedance 等支持 video-as-reference 的下游模型对 reference 上传时长有约束（2026 年实测 ≤ 2.9s 最稳）。原 12s turntable / 12-15s 场景片超限会被截断 / 拒绝。
- **运镜可极快**：reference 视频不是给观众看的，是给模型抓 feature 的。运镜可极快但要稳定不抖。
- **角色台词压到 "1, 2, 3"**：用户授权"自行决定"，方案 A — 三个数字 byte-identical 跨所有 10 角色，约 0.9s/数字节奏自然，足够 Seedance 抓 timbre + 咬字基线。多情绪 / 多音域分化（原 v3 的 5 句多情绪样片）由后续 shot prompt 内的 dialogue script 承担。
- **场景增加 video reference 段**（rule #12.10 NEW）：每场景文件保留原 Seedream 立绘 image prompt（image-only fallback / 静帧 reference），追加 2.9s video reference prompt 段，为 Seedance 提供 video reference。s1_长阶顶/ 等文件夹已有 user 渲染的 *1.mp4 / *2.mp4 / *3.mp4 多视频，rule 把现状形式化。

## 工作流变更

**Before（follow-up 014）**：

- Character turntable: 12s, 5 句多情绪台词（自报家门 / 标志台词 / 低声 / 高声 / 数字校准）。
- Scene file: bible + Seedream 立绘 image prompt 两段 schema，无 video reference prompt。

**After（follow-up 015）**：

- Character turntable: **2.9s**, "1, 2, 3" 三数字 byte-identical。动作 beats 三段 — 全身远景定场 / 360° 快环 / 面部中近景推近。
- Scene file: bible + Seedream 立绘 image prompt + **场景 reference video prompt** 三段 schema。video prompt 2.9s, 三段 — 广角全景定场 / 中景轨道横移 / 长焦推近至材质细节。
- Rule #12.5 → v4；新增 rule #12.10。

## Why now

User 实测 video reference 上传时遇到 2.9s 硬上限 ；原 12s turntable + 12-15s 场景视频均超限。现存已渲染 mp4 资产（c1_沧冥1.mp4 / c1_沧冥2.mp4 / s1_长阶顶[1-3].mp4 等）按新 prompt 重渲一次即可继续工作流。

## 影响范围

- `.claude/agent_refs/project/ai_video.md` — rule #12.5 v3 → v4；新增 rule #12.10。
- `ai_videos/mozun_chongsheng/characters/c{1..10}_*/c{N}_*.md`（10 文件）— 镜头 / 动作 / 台词 / 节奏 / 时长 / 5-line 表 → 3-line 表 surgical replace。
- `ai_videos/mozun_chongsheng/scenes/s{1..6}_*/s{N}_*.md`（6 文件）— append 场景 reference video prompt 段。
- `specs/ai_video/mozun_chongsheng/user_input/revised_prompt.md` — header bump。
- `specs/ai_video/mozun_chongsheng/changelog.md` — append follow-up 015 entry。

## 不影响

- shot prompts (`episodes/ep{NN}/prompts/shot{NN}/shot{NN}.md`) — shot prompt schema 不变；scene reference 视频上传逻辑由 user 操作时识别，不引入新 prompt 字段。
- final_specs / validation / interview / findings — 角色 / 场景 reference 时长是输出层细节，不影响 spec / 策略层 invariants（FR / NFR 不变；AC-3 角色一致性的 byte-identical 锁定描述符不变）。
