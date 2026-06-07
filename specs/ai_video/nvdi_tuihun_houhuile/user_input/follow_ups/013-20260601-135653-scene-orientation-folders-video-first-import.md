---
target_stage: 6
target_artifacts:
  - ai_videos/nvdi_tuihun_houhuile/scenes/s1_陈国公府正厅/
  - .claude/agent_refs/project/ai_video.md
severity: medium
---

# Follow-up draft 013 — 2026-06-01
场景背景图改 folder-per-朝向: 每朝向一个 folder, 内含该朝向 prompt 的 md; video-first 流程 (先生成全景 mp4 → 上传 → 各朝向出图); 命名支持导入功能把 mp4/png 归位到对应 folder。

## 抽象指令

关于 scene: 每一个朝向都应有一个 folder, folder 下有一个 md 文件 (md 里是该朝向的 prompt)。流程: 先用最外面最全面的 video prompt 生成一段视频, 上传后据此生成每个朝向的 picture。prompt 命名要让"导入功能"能把下载好的场景 MP4 与 PNG 放到对应 folder。

## 落地

1. **folder-per-朝向**: `scenes/s1_陈国公府正厅/{plate_id}/{plate_id}.md` × 6 (bg1_朝北_长案主位 / bg2_朝南_厅门 / bg3_朝东_东侧墙 / bg4_朝西_西窗 / bg5_高位俯瞰 / bg6_案前虚化背景), 各 md 内为该朝向 image prompt (image-from-video reference 框架)。先前内联在 scene 主档的 6 段 prompt 已移入各 folder。
2. **video-first 流程**: scene 主档「场景 reference video prompt」(15s walk-through) 生成 `s1_陈国公府正厅.mp4` (存 scene 根) → 上传作参考 → 各朝向 md prompt 据此出静帧。
3. **命名 / 导入约定**: prompt/folder/输出文件三者同名 (文件名即归位键)。`s1_陈国公府正厅.mp4` → scene 根 folder; `{plate_id}.png` → 同名子 folder。
4. **scene 主档**「背景图系统」段改为 流程 + 索引表 + 命名约定 (不再内联 prompt)。
5. **ai_video.md** 规则更新 (per follow-up nvdi 011+013): folder-per-朝向 + video-first + 命名/导入约定。

注: shot `参考:` 行已是 `陈国公府正厅·背景图 {plate_id}：place_holder` (follow-up 011), plate_id = folder 名, 无需再改。
