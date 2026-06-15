# 固定测试台（test rig）v2 — `_performances/` 库级常量

> 本文件是表演演技库的**控制变量基准**。每条 entry 的检验视频用**一个通用 prompt**（model-agnostic，不分 Kling/Seedance）渲染：除「锁定文本块（表演描述）」一个槽位外，景别 / 机位 / 时长 / 画幅 / 表演室场景固定，灯光按当前情绪氛围。验证打分只有在控制变量成立时才可比。

## v2 设计要点（follow-up 003）

- **演员由你上传**：考察的是演技，actor 可任意替换。prompt **不固定演员**——你上传任意 actor 参考照，用 image-to-video 渲染。建议：**同一情绪内**比较不同 entry 时用**同一张**参考照，使「唯一变量 = 表演描述」成立；跨情绪可换演员。
- **一个通用 prompt**：不再分 Kling 版 / Seedance 版（二者本就字节相同）。一条 entry 一个 `## 检验视频` 通用 prompt，你粘进任意模型（Kling / Seedance / Sora / Veo …）渲染。
- **表演室场景**：场景是简洁表演室 / 排练室，无宏大布景、无道具——只保留适合当前情绪的灯光氛围。
- **灯光按情绪**：灯光氛围取自当前情绪 `{emotion}/_emotion.md` 的「灯光氛围（检验视频）」行（如 压抑隐忍=冷调低饱和柔和侧光）。
  > 取舍说明：灯光承载情绪氛围（写实、贴合表演室），而非全局中性。代价是灯光也在轻微「演」情绪；为保打分可比，**同一情绪内所有 entry 用同一套灯光 + 同一演员**，表演仍是唯一被比较的变量。

## 固定的常量

| 变量 | 值 |
|------|----|
| 演员 | **你上传的任意 actor 参考照**（image-to-video），同情绪内保持同一张 |
| 场景 | 简洁表演室 / 排练室，无道具、无布景 |
| 景别 | 近景，人物占画 60–70%，肩部以上入镜 |
| 机位 | 正面平视，水平视线，镜头全程静止（无运镜） |
| 时长 | **按 beat 分配（4–15s，非固定）**：强度1 微表情=4s，强度2–3 单拍=5s，强度4 濒临=7s，强度5 失控=9s；显式多拍渐进条按拍数 ~2.5s/拍（8–15s）、时间窗等比放大。15s 是 Kling/Seedance 单视频上限、是上限不是目标——给短 beat 配长时长只会让模型编造填充动作。由 `tools/set_perf_durations.py` 分配。 |
| 灯光 | 按当前情绪 `_emotion.md`「灯光氛围（检验视频）」 |
| 画幅 | 9:16 |

## 通用 prompt 骨架（唯一可变槽位 = `{{锁定文本块}}`）

```
演{NNNN}
[演员: 上传任意 actor 参考照，image-to-video]
表演室内，近景，正面平视，镜头静止，{{本情绪灯光氛围}}，9:16，时长 {{按 beat 分配的秒数}}。
表演: {{本 entry 的锁定文本块，逐字节嵌入}}
```

> 首行是导入 tag（见下方「导入 tag 约定」）。高强度 / 微表情条另配「起始帧」块（见末节），其 prompt 在 `表演室…灯光` 后加一行 `[起始帧: 本条 ## 起始帧表情 生成的静帧]`。

**机检判据**：每条 entry 检验视频 prompt 去掉首行 tag、`[演员…]` 行与 `{{锁定文本块}}` 槽位后，与本骨架按字节 diff 必须为零（灯光随情绪切换）。

## 导入 tag 约定（下载视频一键归位的关键）

每个 render prompt 块的**首行**是紧凑导入 tag：

| 产出物 | tag | 下载后归位 |
|--------|-----|------------|
| 检验视频（任意模型） | `演{NNNN}` | → `perf_{NNNN}/renders/`（保留原文件名，多模型渲染共存） |
| 起始帧静帧（Seedream/即梦图） | `演{NNNN}始` | → `perf_{NNNN}__startframe.png`（规范名，单张参考帧） |

- `演` = 演技库标记（区别于剧目 shot 的 `{NN}集{NN}镜` tag）；`{NNNN}` = 4 位 perf 号。
- **为什么是首行**：Kling 用 prompt **前 9 个字符**给下载文件命名；tag 仅 5–6 字符、落在窗口内且每条唯一——下载文件名形如 `演0003xxxx.mp4`，导入器据此归位。若不加 tag、prompt 都以同样的场景句开头，则所有 entry 下载撞名、无法归位。

**一键导入流程**（webapp 侧栏 `_performances`「📥 导入检验视频」→ `POST /api/import-from-downloads`，path=`ai_videos/_performances`）：
1. 复制某条 entry 的 `## 检验视频` 通用 prompt（含首行 tag）→ 上传你的 actor 参考照 → 粘进任意视频模型 → 生成并下载。
2. 点导入按钮；导入器扫描下载文件夹近 7 天媒体，按文件名 `演{NNNN}` 归位：视频进 `perf_NNNN/renders/`（原名共存），`演{NNNN}始` 静帧重命名为 `perf_NNNN__startframe.png`。
3. 未匹配文件落 `_performances/_not_matched/`，供人工归类。
4. 在该 entry 的 `## 实测与验证` 渲染表回填分数（模型列记录你用的是 Kling / Seedance / 其他）。

> tag 与 ai_video.md rule 12.4「{NN}集{NN}镜」shot tag 同源同理（都解决 Kling 9 字符截断撞名）；由 `tools/add_perf_import_tags.py` 写入；新撰写的 entry 必须自带首行 tag。

## 评分与合议（你 + Claude，follow-up 004）

评分是对**这条（唯一通用）prompt** 统一打分，不分渲染模型。每条 entry 的 `## 实测与验证` 是一张双评分者表：**你** 和 **Claude** 各按三轴 1–5 打分一次（表演达意 / 情绪可识别 / 是否过火；过火越低越好）。单轴**达标** = 表演达意≥4 且 情绪可识别≥4 且 是否过火≤2。

**合议（自动结算）：**
- **accept**（→ `validation_status: validated`）：你与 Claude **均达标**。
- **revise**（→ `needs_revision`）：双方都评过、但未同时达标 → 按失败轴改 prompt。
- **pending**（→ `pending_review`）：尚有一方未评。

**你评分（webapp）**：打开任一 perf 页面，顶部有「表演评分」面板——三轴点 1–5、写笔记、保存。写回 `POST /api/perf-score`，自动重算合议。

**Claude 评分（需先有视频）**：你下载检验视频、一键导入到 `perf_NNNN/renders/` 后：
1. 抽帧：`python tools/extract_perf_frames.py {emotion}/{perf_id}` → 帧落在 `renders/_frames/`（Claude 读图不读 mp4，故抽帧来看；连续动作流畅度标注为「静帧推断」）。
2. Claude 看帧（+ 起始帧 png）后评分：`python tools/perf_rate.py {emotion}/{perf_id} {达意} {可识别} {过火} "笔记"`——复用与 webapp 相同的评分引擎，写 Claude 行并重算合议。

结合双方分数后：accept 即定稿；revise 则按失败轴（达意↓=词汇具体化/拆 beat；可识别↓=补判别器 AU/补内敛第三层；过火↑=降强度副词/改起始帧）改 prompt、重渲、重评。

## 起始帧块（高强度 / 微表情条）

强度 ≥4 与强度 1（微表情易被丢）默认配「起始帧」：先用 entry `## 起始帧表情` 的 Seedream prompt（基于你上传的 actor 参考照 + 峰值表情）生成一张峰值静帧，作 image-to-video 起始帧；检验视频只承担从该帧出发的动作插值，避开「从文字合成峰值表情」的僵硬。起始帧 prompt 同样沿用表演室 / 景别 / 情绪灯光 / 画幅常量，首行 tag 为 `演{NNNN}始`。
