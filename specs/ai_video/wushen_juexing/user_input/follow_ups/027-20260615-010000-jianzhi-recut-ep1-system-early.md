---
target_stage: 6
target_artifacts:
  - ai_videos/wushen_juexing/episodes/ep01/
  - ai_videos/wushen_juexing/episodes/ep02/
  - ai_videos/wushen_juexing/world.md
  - final_specs/spec.md
severity: high
---

# Follow-up draft 027 — 2026-06-15（监制大改）

用户以「监制 skill」(ai_video__dialogue_master) 身份审 EP1 剧情/台词/运镜连贯性并大改。

## 抽象后的指令
1. EP1 剧情/台词/运镜不够连贯——重排、按因果衔接。
2. **系统早现**：开场不久系统就出来，给男主二选一【苟活 / 硬刚】；选【硬刚】即**激活武神觉醒系统**。
3. **和系统对话太少**——全程增加主角↔系统来回（监制 P4）。
4. 可增 shot 做铺垫，或移部分到 EP2。

## 落地
- world.md §四：系统机制改为「早现 + 苟活/硬刚二选一、选硬刚激活；断绝走出再领武神躯大礼」。
- EP1 re-cut 为 14 镜/~90s：穿越→至暗→**系统早现二选一**→选硬刚激活→有底气硬刚对峙(系统撑腰)→回忆铺垫→决心断绝(hook)。
- EP2（溢出段 7 镜/44s）：断绝走出→系统送大礼武神躯觉醒→震惊→宣言→凌虚子末镜。
- spec FR-7/FR-7b、arc_outline EP1/EP2、各 publish 同步。

## ⚠ 事故记录（render 数据丢失）
执行 re-cut 时，归档命令对含空格的渲染文件名 word-split 失败、`mv` 静默未移动，随后 `rm -rf shots` 把仍在 `renders/` 内的 **17 个用户渲染 mp4 一并删除**（gitignored、不在回收站、不可恢复）。**唯一幸存：`episodes/ep01/ep01.mp4`（91s 全集合成片，含全部已渲染镜头画面）。** 教训：删除前必须用 `find -print0 | xargs -0` / 逐文件确认归档成功再删；已在复盘中记录。
