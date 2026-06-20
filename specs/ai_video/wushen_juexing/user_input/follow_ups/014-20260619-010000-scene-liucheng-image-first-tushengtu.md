# Follow-up draft 014 — 2026-06-19
场景方向背景图流程改为 image-first：用一张全局图作 reference + 各方向 prompt 图生图，取代「从 mp4 抽帧为主」。

## 指令（抽象后）

- 用户反馈：从 walk-through mp4 抽出来的各方向背景图**质量不太好**。
- 提议（采纳）：改流程——出**一张比较全局的参考图**，各方向用「该方向 prompt + 这张全局图」走**图生图（image→image）**生成各方向背景，质量更高、跨方向更一致。
- 这与平台能力一致（image→image 支持；mp4→图片不支持）。

## 改后流程

1. 步骤一 text→image 出一张全局建场参考底图（空间/材质/配色/光源）。
2. 各方向：该方向 `{plate_id}.md` prompt + 上传全局底图作 reference → 图生图 → 该方向 bg PNG。参考图锁材质/配色/光源/风格，prompt 驱动机位/构图（prompt 须写全该方向几何）。
3. 步骤二 walk-through 视频仍生成，用途改为 **shot 视频 reference**，不再是方向背景图来源。
4. 抽帧（🧭 按钮 + 截帧时点表）降为**兜底**：某方向图生图转不过去（朝南 reverse / 俯瞰）时抽一张含正确机位的帧作图生图 reference 再精修。

## 风险/注意

- 单张全局（偏正面）底图对大转角（朝南/俯瞰）可能转不过去 → 各方向 prompt 必须写全该方向机位几何；实在不行用抽帧兜底。
- 代码无需改：🧭 按钮 + ScenePlateExtractor + 截帧时点对齐 全部保留作兜底。

## 通用规则

已回填 `.claude/agent_refs/project/ai_video.md` 场景生成流程：image-first → 各方向 image→image 为主路径，抽帧兜底，walk-through 视频用途=shot reference。
