# Follow-up draft 017 — 2026-05-13

Summary: 把场景 reference 视频 prompt 从 v2 的 **3.9s 五段极速 all-angle** 改为 v3 的 **15s walk-through 单视频**——沿一条几何连续的相机路径（连续 dolly + 平滑 yaw + 垂直俯仰 + 推进 zoom，无剪辑 / 跳切）依次悬停在 5 个 canonical 视角上，每个 dwell ≥ 0.8s 给出锐利静帧；**重要视角 frontload 在 t < 6s**（Hero / Reverse）以抵御 Kling / Seedance 在 t > 12s 后的训练分布边缘漂移；新增"中间帧 buffet"概念——15s × 30fps = 450 帧，user 可后续按需 ffmpeg 抽取额外 3/4 角度参考图，无需重新调 API。规则 update 仅触及场景 reference（rule #12.10 family）；角色 turntable（rule #12.5 v4 / 2.9s）与 shot prompts（rule #12.6 v2）**未触及**。

## 用户原话

> 我只想用一个视频，我可以选择用 kling 或 seedance 生成，视频长度上限是 15 秒

> good the spec driven agent is capable of generate specs for ai videos, part of the spec is about generate scene, could you update the claude settings and agent files such that the scene prompt generated (which I will manually copy to seedance and kling to generate video) meets your above requirement, as well as the ai_video requirement, so your above requirement is really common to all scenes. I think currently the length is only 4s, you can change it to 15s at max. Also please only update the scene, don't touch characters and shots. After you change the claude settings, then update spec for all current ai_videos and then use the new spec to update all scenes already generated.

## 决策

- **时长锁值 3.9s → 15s**：Kling / Seedance 当前 tier 实测 reference 上传上限可达 ≥ 15s（v2 的 3.9s 假设过保守）。
- **单视频 walk-through 替代五段极速序列**：v2 的 3.9s 五段（正面建场 + 水平 360° + 垂直三视角 + 中景横移 + 长焦特写）信息密度极高但每段 dwell < 0.8s，导致 (a) canonical 帧带 motion blur，参考图锐利度不足；(b) 极快运镜下模型偶发"跟不上"，中段材质 / 几何漂移。v3 沿一条 monotonic 平滑路径，dwell + transition 交替，每个 canonical 视角悬停 ≥ 0.8s。
- **5 canonical 视角不变**：Hero（正面建场）/ Reverse（反向广角）/ Vertical（垂直俯瞰或仰望，二选一）/ Mid-track（中景横移定格）/ Detail（长焦特写）—— 与 v2 球面采样 KPI 对齐，但布置在 15s 内。
- **Frontload 重要视角**：Hero 在 t = 0.5s，Reverse 在 t = 4.4s（均 < 6s）。Kling / Seedance 在 t > 12s 后进入训练分布边缘，常见失败模式（材质漂、几何变形、长尾噪点）集中在视频后段；frontload 后即便后段翻车，损失的是次要参考图。
- **新增"中间帧 buffet"**：15s × 30fps = 450 帧，5 个 canonical 帧 + 约 350 帧免费 3/4 角度参考。user 后续若 shot 需要某个 3/4 偏移角度，可对 source mp4 手动 ffmpeg 抽取，无需重新调 API。Source mp4 保留与 scene 文件同 folder（与 folder-per-asset rule #12.9 兼容）。
- **运镜约束**：monotonic 平滑、无剪辑 / 跳切 / 淡入淡出 / hard cut / 剧烈加速或瞬间反向；速度可慢可中等；全程无抖动。8 个 byte-identical 锁定字段（镜头 / 光线色调 / 节奏 / 渲染样式 / 比例 / 音频=无 / 时长=15s / 负向）保持跨场景一致，仅 `场景:` 段随场景变化。
- **scope 严格限于场景**：用户明确要求"only update the scene, don't touch characters and shots"。
  - Rule #12.5 v4（character turntable 2.9s）**不动** —— 单体 360° 在 2.9s 内已足够覆盖，无球面采样信息密度问题。
  - Rule #12.6 v2（shot prompts）**不动** —— scene reference 视频上传逻辑由 user 操作时识别，不引入新 prompt 字段。
  - 角色文件 `characters/c{1..10}_*/c{N}_*.md` **不动**。
  - Shot prompt 文件 `episodes/ep{NN}/prompts/shot{NN}/shot{NN}.md` **不动**。

## 工作流变更

**Before（follow-up 010 v2）**：
- 场景 reference video prompt: **3.9s**, 五段拼接（正面建场 + 水平 360° + 垂直三视角 + 中景横移 + 长焦特写），每段 0.7-0.9s，运镜极快、稳定不抖即可。
- 时长 / 负向 等 7 字段 byte-identical 跨场景；锁定值 `时长 = 3.9s`、`节奏 = 极快`。

**After（follow-up 017 v3）**：
- 场景 reference video prompt: **15s**, 一条几何连续的相机路径 + 5 个 canonical dwell（每个 ≥ 0.8s）+ 4 段平滑 transition。重要视角 frontload 在 t < 6s。
- 8 个字段 byte-identical 跨场景（v3：从 v2 的 7 字段保留并 amend 时长 / 节奏 / 负向）；锁定值 `时长 = 15s`、`节奏 = 中等`、负向新增 5 项（不要剪辑 / 跳切 / 淡入淡出 / hard cut / 剧烈加速或瞬间反向运动）。
- Rule #12.10 v2 → v3。

## Why now

User 在第三方场景 3D 建模 / AI 短剧场地一致性的对话中（2026-05-13）明确指定：(a) 只想用一个视频；(b) Kling 或 Seedance 二选一；(c) 视频长度上限 15s。当前 spec 沿用的 v2 是 3.9s 五段，与新的 15s 上限不对齐；且 v2 的"每段 < 0.8s"在实测中导致参考图锐利度不足。本次升级把上述对话沉淀的 walk-through 设计（priority frontloading + 几何连续路径 + 中间帧 buffet）固化为 ai_video.md 的常驻规则，适用于本项目（mozun_chongsheng）与未来所有 ai_video 项目。

## 影响范围

- `.claude/agent_refs/project/ai_video.md` — rule #12.10 v2 → v3（intro 段 + 12.10-A schema 段 + 12.10-B body schema 段 + 12.10-C 联动段 + 锁定字段 paragraph + originated note）。
- `specs/ai_video/mozun_chongsheng/user_input/revised_prompt.md` — header bump，记录 follow-up 017。
- `specs/ai_video/mozun_chongsheng/changelog.md` — append follow-up 017 entry。
- `ai_videos/mozun_chongsheng/scenes/s{1..9}_*/s{N}_*.md`（9 文件）— rewrite 第三段「# 场景 reference video prompt」整段：header 行（v2 → v3）+ 用法说明段 + ```text fenced block body（v2 3.9s 五段 schema → v3 15s walk-through schema）。各场景 bible（8 字段锁定描述符 / 关键变化态 / 出现镜头 / 负向）与第二段「# 场景 reference image prompt」（Seedream 立绘）**完全保留**，逐字不改。

## 不影响

- `specs/ai_video/mozun_chongsheng/final_specs/spec.md` — FR / NFR 不涉及 reference 视频时长（输出层细节），grep 验证 0 处需 patch。
- `specs/ai_video/mozun_chongsheng/validation/*` — strategy / acceptance_criteria / bdd / ai_video_specific 0 处提及 3.9s / 场景 reference 时长。
- `specs/ai_video/mozun_chongsheng/interview/qa.md`、`findings/*` — 上游决策层，与 reference 视频时长正交。
- `ai_videos/mozun_chongsheng/characters/c{1..10}_*/c{N}_*.md`（角色 turntable）— rule #12.5 v4 / 2.9s 保留不动。
- `ai_videos/mozun_chongsheng/episodes/ep{NN}/prompts/shot{NN}/shot{NN}.md`（shot prompts）— rule #12.6 v2 schema 不变。
- 已渲染的 mp4 资产（`scenes/s{1..6,9}_*/s{N}_*[1-4].mp4`）— 物理 mp4 不删除（保留作 v2 渲染历史），但 user 应基于 v3 prompt 重新渲染一次以获得新的 15s walk-through reference，并替换下游 shot 上传时使用的 mp4 path。
- `style_guide.md` / `world.md` / `arc_outline.md` — 与 reference 视频时长正交。

Severity: scene reference 视频时长从 3.9s 提到 15s 属于**中等 blast radius** 的输出层 update。仅触及 9 个 scene 文件 + 1 个 ref + 2 个 spec 元数据文件。规则层 update 完成后，未来场景 stage-6 regen 自动沿用 v3 schema。
