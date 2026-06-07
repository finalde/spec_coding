---
target_stage: 6
target_artifacts:
  - my_novel/nvdi_tuihun_houhuile/chapters/0001-第1集 接旨退婚.md
  - episodes/ep01/shots/*/shot*.md
severity: high
---

# Follow-up draft 006 — 2026-05-31
本项目从「无源小说」模式切换到 chapter-first：先写完整 ep01 小说正文，每镜小说段改为该章节的 200-400 字 verbatim 引用。

## 抽象指令

用户审阅 shot 档时发现每镜的「小说原文」过于简短（~20-40 字），期待其篇幅与一部完整小说相当。根因：本项目按 ai_video.md rule 5 v3 的「无 reader-side novel」模式运作，每镜小说段是按该 shot beat 现写的短片段，且不存在完整源小说（raw_prompt.md 明确 "there is no novel prose source"）。

决议：**将本项目升级为 chapter-first / reader-side-novel-exists 模式**（与 feng_shou_lu 一致）：

1. 在 `my_novel/nvdi_tuihun_houhuile/chapters/0001-第1集 接旨退婚.md` 写一份 ≥5000 字中文小说正文（canonical source-of-truth），覆盖 ep01 全部 28 镜的剧情弧（接旨退婚 + 锋芒初露），叙事连贯如一部正文章节；并建 `my_novel/nvdi_tuihun_houhuile/README.md` 扉页。
2. 每个 shotNN.md 顶部由 `## 小说原文`（短片段）改为 `## Chapter excerpt (from chapters/0001-第1集 接旨退婚.md)` + 该镜对应的 200-400 字 chapter prose **verbatim 引用**（连续镜头拼起来即原章节）。
3. 代码块内 `情节:` 字段同步更新为该 excerpt 的纯文本（verbatim，无粗体）。
4. chapter 为源，script.md / shotlist.md 维持为既有 derived 产物（剧情 beat 一致，不在本次重生成）。
