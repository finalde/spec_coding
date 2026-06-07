---
target_stage: 6
target_artifacts:
  - ai_videos/nvdi_tuihun_houhuile/scenes/s1_陈国公府正厅/
  - .claude/agent_refs/project/ai_video.md
severity: medium
---

# Follow-up draft 014 — 2026-06-01
背景图/视频 prompt 首行加 key (供下载文件含 key → 导入+重命名归位); 强调影视级写实质感 (现生成太卡通), 增加细节/质感/美感, 如制作精良古装剧场景。

## 抽象指令

1. 在 prompt 起始加入 key 信息 (如 `bg3_朝东_东侧墙`), 使下载的文件包含此信息; 确保导入+重命名功能能把相应下载文件导入指定 folder。
2. prompt 应强调场景风格要真实 —— 现生成的图片太像卡通; 要增加更多细节、要有质感、美感, 像一部制作精良的古装剧的场景。

## 落地

1. **key 首行**: 6 个朝向 prompt 的 ```text``` 块首行 = `{plate_id}`; scene 主档 walk-through 视频 prompt 首行 = `s1_陈国公府正厅`。生成/下载文件名带 key, 导入+重命名据此归位 (mp4→scene 根, png→同名子 folder)。scene 主档「命名/导入约定」补一条 prompt-首行-key 说明。
2. **写实质感**: 6 个朝向 prompt + 视频 prompt 增加 `风格:` 行 (影视级真人实拍写实 + cinematic + 4K HDR + 超写实 photorealism + 电影级布光色彩分级 + 制作精良古装剧置景美感, 类比 琅琊榜/长安十二时辰/知否) + `质感/细节:` 行 (木纹包浆/石材纹理/漆面微裂/黄铜氧化/宣纸烫金/斜光浮尘/丁达尔光束) + 强化 `负向` (不要 卡通/动画感/3D游戏场景/CG渲染感/塑料质感/扁平光/廉价置景/过曝失真)。
3. **ai_video.md** 规则补 (per follow-up nvdi 014): prompt 首行写 key + 场景写实质感要求 (anti-cartoon)。
