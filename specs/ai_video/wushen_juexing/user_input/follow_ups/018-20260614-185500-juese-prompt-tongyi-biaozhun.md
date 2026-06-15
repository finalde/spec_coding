---
target_stage: 6
target_artifacts:
  - ai_videos/wushen_juexing/characters/
  - final_specs/spec.md
  - validation/consistency.md
severity: high
---

# Follow-up draft 018 — 2026-06-14

沈婉 prompt 仍和主角 video prompt 天差地别——所有角色按同一标准；并保证未来新角色统一。

## 抽象后的指令
- 角色 prompt 必须**全部统一到同一标准**（rule #12.5 v11 的「视频 reference prompt」：7s 单 take 转身 + 中文计数 + 造型锁定/面部细节/镜头/光线/渲染等齐全字段 + 计数台词表）。
- 沈婉(c9) 此前是旧式简版（Seedream 立绘 + 临时转盘），与 c1–c8 的 v11 标准不一致 → 升级到同标准。
- 我 follow-up 016 给 c1–c8 追加的「角色转盘」段是冗余（它们已有 v11）→ 删除。
- **保证未来新角色统一**：标准写入 spec FR-5（指向 rule 12.5 v11 + c1 范例）+ 新增机检 consistency C-7。

## 落地
- c1–c8：删冗余「# 角色转盘 video prompt」段（保留各自 v11 视频 reference prompt + 计数台词表）。
- c9 沈婉：删旧式立绘+临时转盘，重建为 v11 视频 reference prompt（按沈婉锁定描述符填充）+ 计数台词表。
- spec FR-5 重写为「角色 prompt 统一标准 rule 12.5 v11」+ 未来一致性保证；validation 新增 C-7（机检每角色档恰 1 个 v11 段 + 计数台词、无旧式段）。
