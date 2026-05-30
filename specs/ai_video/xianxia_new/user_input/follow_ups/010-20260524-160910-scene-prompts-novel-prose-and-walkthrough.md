---
target_stage: 6
target_artifacts:
  - ai_videos/feng_shou_lu/scenes/s1_无寿崖.md
  - ai_videos/feng_shou_lu/scenes/s2_落雁渊.md
  - ai_videos/feng_shou_lu/README.md
severity: medium
---

# Follow-up draft 010 — 2026-05-24

场景 prompts 需要 novel-prose-grade 细节密度（per project ref rule 12.4-E）+ 补齐缺失的 15s walk-through 场景视频 reference prompt（per project ref rule 12.10）.

## 抽象指令

`ai_videos/feng_shou_lu/scenes/s{N}_*.md` 当前的 Seedream 立绘 prompt 段只有 ~5 行结构化 `[细节]` 列表，且缺失 rule 12.10 强制的 15s walk-through 场景视频 reference prompt。后果：(a) Seedream 拿到的细节信号过稀，PNG 走"AI generic 仙侠"模板，达不到唯美写实；(b) Kling / Seedance 没有 scene reference mp4 可上传，下游 shot 的场景一致性完全靠 description-layer continuity 单点支撑，画面会漂。

本 follow-up 把 2 个立档场景档（s1_无寿崖 / s2_落雁渊）按下列契约改写：

1. **增厚现有 Seedream 立绘 image prompt 的 `[细节]` 段** —— 从结构化短列表升级为 200-300 字感官散文，载入：(a) 材质纹理（梧桐叶的绒毛 / 鸟骨的风化层 / 青石的苔痕 / 渊壁的湿润）；(b) 风 / 雾 / 尘 / 光的物理行为（落叶翻面方向、苇草伏倒角度、灰晨光的尘埃可见度、月光在石面的折射）；(c) 各表面对主光源的真实反应（白梧桐叶背的浅褐光泽、鸟骨的冷暖中性反射、渊底水洼的镜面、淡剑痕在斜阳下的浅黄褐色）。不修改 `[主体]` / `[风格]` / `[参数]` 与负向段（保留 byte-identical 锁定）。
2. **新增 rule 12.10 的 15s walk-through 场景视频 reference prompt** —— 严格按 rule 12.10-B schema：1950 ≤ chars ≤ 2000 的 body，6 字段（场景 / 时辰 / 配色 / 空间 / 镜头 / 动作 / 光线=色调 / 节奏 / 负向），5 个 canonical dwell ≥ 0.8s + 4 段平滑过渡，重要视角 frontload 在 t < 6s，焦距渐变 24mm → 28mm → 28mm → 35mm → 85mm。`渲染样式` / `比例` / `音频` / `时长` 4 字段移到 API 侧（duration=15s, aspect_ratio=9:16, no_audio=true）不入 body。
3. **s1 加渡劫态变体 image prompt** —— s1 默认立绘走静默态（适配 ep17 / ep49 / ep60 多集复用），新增一份独立的渡劫态变体 prompt（~1500 字）专门服务 ep01/shot01 cold open + ep08 倒叙 unfiltered 回放，避免 shot prompt 重复 inline 铺叙紫黑夜 + 雷光紫白闪 + 落叶逆吹 + 崖边剑光寒。变体共享 8-字段锁定描述符 + 一句话锁定 byte-identical，仅光影状态 / 大气 / 动态元素差异。
4. **README.md scenes 段同步** —— 渲染产物布局加 `scenes/s{N}_*.mp4` + `scenes/s1_无寿崖_渡劫态.png`；使用说明 §3 新增 walk-through mp4 渲染步骤 + 变体 PNG 渲染步骤；rule 12.10 mp4 作为 shot prompt 的 scene reference 上传（与 character turntable.mp4 同列处理）。

## 不动的契约

- 8-字段锁定描述符（含 #8 一句话锁定）跨段 byte-identical（rule #12.7 v2 锁定）。
- `[主体]` 段 / `[参数]` 段 / 负向段全部保留 byte-identical。
- shot prompts 内的 `场景:` 单行 token 不动（保留 byte-identical 复用契约 per rule 12.3 v2）。
- 一句话锁定 ≤30 字硬上限不动。
- 立绘默认光影态（s1=静默态 / s2=黎明态）不动；变体仅作 sibling section。

## 触发原因

用户原话："在 fenshoulu 裏的場景 prompt，要跟多類似於小説細節的描述，我需要生成唯美逼真的場景視頻還有圖片。" 用户已通过多选锁定范围：s1 + s2 两文件 / Seedream 立绘增厚 + 15s walk-through 新增 + s1 渡劫态变体三件套。
