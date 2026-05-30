---
target_stage: 6
target_artifacts:
  - ai_videos/feng_shou_lu/characters/   # NEW (mirrored)
severity: low
---

# Follow-up draft 005 — 2026-05-24 07:18:00 UTC

Summary: Mirror 11 character folders from `my_novel/feng_shou_lu/characters/` → `ai_videos/feng_shou_lu/characters/`. Required because `ai_video_management` webapp's casting feature (`libs/infrastructure/writers/casting__writer.py`) only scans `ai_videos/{drama}/characters/` per its drama-dir design — feng_shou_lu's character bibles live in `my_novel/feng_shou_lu/characters/` per spec FR-13 (MVP scope: bulk of files in my_novel/, ai_videos/ has only README).

## 用户原话

> 角色分配時候，找不到fenshoulu裏的角色

(Casting UI 在 ai_videos/feng_shou_lu/ 看不到角色, 因为该目录只有 README; 角色 bible 在 my_novel/feng_shou_lu/characters/.)

## 用户选择

> Mirror — copy 11 character folders into ai_videos/feng_shou_lu/characters/

Pros: 最简单 / 无 code 改动 / webapp 立即可用. Cons: 文件 duplicate; 后续 my_novel/ 端的更新需要 re-mirror.

## 改动

```bash
cp -r my_novel/feng_shou_lu/characters/* ai_videos/feng_shou_lu/characters/
```

11 个角色 folder (`{中文名}/{中文名}.md`) 镜像到 ai_videos/ 端. 内容 byte-identical 与 my_novel/ 端.

## 单一事实源契约

`my_novel/feng_shou_lu/characters/` 仍是 **canonical source of truth** (spec FR-5 default). `ai_videos/feng_shou_lu/characters/` 是 **mirrored copy** 供 webapp casting feature 使用 / read-only consumption. 任何角色 bible 修订 都应在 my_novel/ 端做, 然后 re-mirror.

## Future follow-up (deferred)

如果 my_novel/ 端的 character bible 修订 频繁, 应考虑:
(a) 在 `apps/cli/` 新增 `mirror_my_novel.py` 一键 sync 命令; 或
(b) 在 ai_video_management webapp 添加 `my_novel/` 端的扫描支持 (architectural fix, 需要 spec_driven 流水线下的 ai_video_management follow-up).

本 follow-up 仅作 one-shot mirror, 不引入 sync 自动化.

## Out of scope

- 不 mirror scenes/ episodes/ 等其他子目录 — 用户仅报告 casting (角色分配) 受影响, 其他 feature 出现时再处理.
- 不修改 webapp casting writer 逻辑.
- 不在 ai_videos/ 端添加 .gitignore 排除 mirrored 副本 (默认保留 git tracked, 便于其他人 fork 后无需手动 re-mirror).

## Acceptance

- `ai_videos/feng_shou_lu/characters/{中文名}/{中文名}.md` × 11 已存在 + 内容与 my_novel/ 端 byte-identical.
- changelog.md 已追加 follow-up 005 条目.
