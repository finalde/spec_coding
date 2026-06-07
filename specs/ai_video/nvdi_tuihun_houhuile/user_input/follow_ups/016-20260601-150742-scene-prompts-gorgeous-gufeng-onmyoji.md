---
target_stage: 6
target_artifacts:
  - ai_videos/nvdi_tuihun_houhuile/scenes/s1_陈国公府正厅/
  - .claude/agent_refs/project/ai_video.md
severity: medium
---

# Follow-up draft 016 — 2026-06-01
把场景 prompt 那层改成「绚丽唯美古风」，要很多细节和古风唯美元素，参考郭敬明《阴阳师（晴雅集）》的场景风格；依此重新生成 scene 的所有 prompt。

## 决策 (interactive 澄清)
- **写实↔唯美平衡 = 电影级唯美打底真实**：保留真实材质质感打底 (木纹/石材/金属/丝绸)，叠加绚丽唯美元素 (金箔描金/云雾/飞花/纱幔/烛火宫灯/琉璃/丁达尔光束/暖金 bokeh/浮尘流光)；`负向` **放宽**「反 CG」改求电影级唯美 CG 氛围 (不写「不要 CG 渲染感」，改「不要 廉价游戏CG感」)，但仍守 反卡通/反塑料/反扁平/反廉价。修正 follow-up 014 的「必须真人实拍写实 + 强禁 CG」。
- **应用范围 = 仅 scene 的所有 prompt**：walk-through 视频 prompt + 6 张朝向 plate prompt + 旧 single 场景立绘 prompt。**shot prompt 不动** (29 个 shot 的渲染样式保持原样)。

## 约束 (不可破)
- 重写各 plate 的 `主体:` 行**仍以方位词开头** (`{scene} {方位}视角 — …`)，否则 follow-up 015 的导入归位 (按方位段路由) 会坏。6 个方位词 (朝北/朝南/朝东/朝西/高位俯瞰/案前) 均原位保留。
- 视频 prompt 的几何相机路径 / dwell 锁机位 / ≤15s / 纯视觉无音频 约束不变；唯美元素 (飞花/袅烟 ambient 轻飘) 不构成镜头抖动。

## 落地
- 8 个 prompt 块 (6 plate + 1 视频 + 1 立绘) 的 `主体/光线/质感/风格/构图/负向` 全部重写注入唯美 DNA。
- ai_video.md「质感/美术方向」规则改为：真实质感打底为通则，美术方向 per-project (默认写实 / 唯美古风 opt-in)；nvdi 选唯美古风。
