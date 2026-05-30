# Raw prompt — xianxia_new (working slug)

**task_type:** ai_video
**sub_type:** novel
**Working task_id:** `xianxia_new-20260524-101931`
**Captured:** 2026-05-24

The user's original turn covered two distinct asks. The folder-rename portion was handled as follow-up 113 to `specs/development/ai_video_management/` (rename `novels/` → `downloaded_novels/`, add `my_novel/`). What follows is the *new-novel-creation* portion that this spec-driven task addresses.

## 用户原话（中英混排）

> under ai_videos_management rename current downloaded novels folder to downloaded_novels, I am going to introduce a new folder called my novel, under my novel, I am going to ask you to take a look at existing downloaded novels, and then make up a new novel for me, 題材仍然是某一類，比如仙俠，請把諸多小説當作baseline，編排一部新的小説，而且保證不會有版權重複問題，但是要保持小説的競猜性，你可以從多部小説中提取要素，更換人名，然後你還要與時俱進，從網上research跟多有關此類型題材的信息系和熱點，把他融入到小説中。小説的最終目的是拍攝ai短劇

## 用户多选裁决（pre-skill 已通过 AskUserQuestion 收集）

1. **顶层布局**：`downloaded_novels/` + `my_novel/` 两个同级目录。已通过 follow-up 113 落地。
2. **新小说创作工作流**：通过 `/agent_team`（task_type=ai_video, sub_type=novel）跑完整 spec-driven 六阶段。
3. **webapp 同步更新**：全量 — `_ALLOWED_TOP_LEVEL`、`ExposedTree`、tree_reader、container、CLI、frontend types、tests。已通过 follow-up 113 落地。

## 隐含约束（来自原话 + 项目约定）

- 题材：仙侠（用户原话「題材仍然是某一類，比如仙俠」— 仙侠是举例还是确定？interview 阶段确认；目前按仙侠推进）。
- 基线语料：`downloaded_novels/xianxia/` 下的 14 本小说（fanren_xiuxian_zhuan、cong_jianshu_xiuxing、gou_zai_liangjie_xiuxian、gou_zai_xiuxianjie、gou_zai_yaowu_luanshi、guangyin_zhiwai、jie_jian、meiqian_xiu_shenme_xian、shan_he_ji、shei_rang_ta_xiuxian_de、wode_moni_changsheng_lu、xuanjian_xianzu、zhen_wen_changsheng、zhutian_daozu）。
- 版权安全：人名、地名、功法名、宗门名、世界观签名都要改；不能让任何一幕 / 一段情节链可单独追到任一本源书。
- 文学性：保持「競猜性」— 仙侠读者期待的伏笔 / 悬念 / 反转密度。
- 时代感：从网络抓 2025–2026 仙侠 / 短剧 / 网文 / 抖音 / 小红书热点融入。
- 终极用途：AI 短剧（每个 shot ≤ 15 s；角色少；prop 简单；AI 图像 / 视频生成友好）。
- 文件落地：原稿 → `my_novel/{slug}/`；AI 视频产物 → `ai_videos/{slug}/`；本任务的 spec 流水线 → `specs/ai_video/{task_name}/`（本目录）。
- 命名约定：folder = pinyin/English；README + 内容 = Chinese（per `agent_refs/project/ai_video.md` rule 1）。最终 slug 在 interview 阶段确定 — 当前 `xianxia_new` 仅为 spec-folder 占位。

## 项目侧前置事实

- `downloaded_novels/xianxia/` 下的 14 本均为完整下载（部分新章节正在被 follow-up 111 的拆分流程整理；不阻塞本任务的研究阶段）。
- `my_novel/` 当前仅含 `.gitkeep`，等待本任务 stage 6 写入第一个项目。
- 上层 webapp `ai_video_management` 已识别 `my_novel/` 顶层目录（follow-up 113）。
- 本仓库 `agent_refs/project/ai_video.md` 对 ai_video sub_type=novel 的小说项目布局有约束（episodes/epNN/、字幕三选一、9:16、≤15 s 等），将在 stage 4/5 严格遵守。
