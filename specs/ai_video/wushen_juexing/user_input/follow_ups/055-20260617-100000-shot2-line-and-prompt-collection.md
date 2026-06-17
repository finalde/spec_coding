# Follow-up draft 055 — 2026-06-17
① EP2 shot2 内心台词"来了。先沉到骨子里"太突兀；② 要一个新文件：当前 EP 下所有 shot prompt 的集合。

---
target_stage: 6
target_artifacts:
  - episodes/ep02/shots/shot02/shot02.md
  - episodes/ep02/all_shot_prompts.md
severity: low
---

## 指令
1. **shot2 台词去突兀**（ai_video__dialogue_master·D5 情绪真实/D1 说人话）：系统刚告知"武神躯已注入体内"，主角反应却跳过"认出是什么"直接喊"先沉到骨子里"（命令式、跳 beat、像作者速记）。改为先认出再决定藏：`原来……这就是武神躯。先收着——这些人，还不配看见。`（18字/4s=4.5字/秒）。shot02 台词/情节/台词配音 + dialogue.md + script.md + source_novel.md + shotlist.md 六处同步。
2. **新文件 `episodes/ep02/all_shot_prompts.md`**：自动汇编全 14 镜的【视频 prompt】+【台词配音 prompt】代码块（含小标题 + 时长），复制即用；只读快照，改动改各 shot 源后重新汇编。
