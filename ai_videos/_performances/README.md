# 《表演演技库》— AI 短剧通用演技资产库

把人类表演方法提炼成一批 **generic、跨剧目复用、经检验视频实证验证**的表演 prompt 条目（entry），供所有短剧的 shot prompt 直接 reference。与 `_actors/`（演员试镜库）、`_voices/`（声线库）同属 `ai_videos/` 下的下划线前缀共享资产库：`_actors` 锁「长什么样」，`_voices` 锁「声音什么样」，`_performances` 锁「怎么演」。

## 为什么要这个库

角色外观、场景、声线在本体系里都已资产化、可逐字复用；唯独「表演 / 演技」每个 shot 都是现场即兴撰写，质量不稳定、经验不沉淀。而表演恰是 AI 视频模型（Kling / Seedance）服从性**最弱、最不可预测**的维度——所以**经实测验证**的表演 prompt 才有资产价值，未验证的描述词网上随处可得。这个库的核心价值不是「收集演技词」，而是「沉淀经双模型验证、知道在哪个渲染器上 land 的表演锁定块」。

## 目录布局

```
_performances/
├── README.md            # 本文件
├── _testrig.md          # 固定测试台（控制变量基准）— 所有检验视频在此渲染
├── _calibration.md      # 中文 vs 英文锁定块校准实验（stage-6 前置）
├── _reference_usage.md  # 引用样例：entry 如何嵌入一个真实 shot prompt
└── {emotion}/           # 每种情绪一个目录（英文/拼音名）
    ├── _emotion.md      # 情绪定义 + 三层模型 + 子类型 + 本情绪 entry 清单
    └── perf_NNNN/       # 每条 entry 一个文件夹（全局连续编号，零补四位）
        ├── perf_NNNN.md           # entry 本体
        ├── perf_NNNN__startframe.png  # 起始帧静帧（如适用，gitignored）
        └── renders/               # 检验视频（一键导入归位；多模型渲染共存，gitignored）
            └── 演NNNN*.mp4
```

路径英文/拼音，文件内容中文。检验视频 mp4 / 起始帧 png 是 per-machine 可重生缓存，已被 `.gitignore` 的 `ai_videos/**/*.mp4`、`*.png` 覆盖；git 只追踪 markdown。

## 四维分类 schema

每条 entry 的 frontmatter 标注四维，全部锚定真实表演 pedagogy（非凭空发明）：

| 维度 | 取值 | 锚定的权威标度 |
|------|------|----------------|
| `emotion` | 情绪名（如 压抑隐忍） | 按短剧功能主轴（爽感/痛感/欲望/惊悚）选 |
| `intensity` | 整数 1–5 | **FACS A–E 强度标度**（见下） |
| `style` | 内敛压抑 / 外放爆发 | Laban Effort Flow（bound↔free） |
| `carrier` | 面部 / 眼神 / 肢体 / 呼吸 / 复合 | FACS AU 分区；复合 = Chekhov Psychological Gesture |

可选 frontmatter：`subtype`（如 强忍泪水）、`au_ref`（FACS AU 组合，仅 metadata 不进 prompt body）、`lma_tag`、`mffr`（Molding/Flowing/Flying/Radiating，复合条）、`stance`（反派/主角，仅当同情绪需区分）。

### 强度 1–5 ＝ FACS A–E gloss

强度 1→5 主要是**同一 AU 集在升强度 + 后段招募张口 AU**，而非换一组肌肉：

- **强度1（A 痕迹 / 微表情）**：一两个核心 AU、低强度、单区域。微表情易被模型丢，默认配起始帧。
- **强度2（B 轻度）**：核心 AU 显现，仍含蓄。
- **强度3（C 清晰 / 宏表情）**：完整规范 AU 组合，中段最可控。
- **强度4（D 强烈）**：高强度、濒临、身体开始招募。
- **强度5（E 极致 / 失控）**：满强度 + 张口 AU（AU25/26/27）+ 全身招募；内敛情绪在此为「失守 / 决堤」（外放）。

### 物理动作铁律（最重要的一条）

每条 entry 的 `## 锁定文本块` 只写**可观察物理动作 + 主动动词**，**严禁裸情绪名作表演描述**（情绪名只在 frontmatter 与标题）。理由：表演学（Stanislavski「情绪无法被指挥，动作可以」）与 AI 模型实测（裸情绪名被忽略、命名肌肉动作才 land）双重背书。正例：「眉内角上提、嘴角下拉抿紧、屏息后喉头一动」；反例：「表现悲伤」。

## 引用用法（给 shot 作者）

库稳定后，任何短剧 shot 想要某种演技效果时：

1. **标注**：shot.md 的 `## Shot context` 加一行 `表演库参考: perf_NNNN (情绪·强度·风格·载体) — 用于 <角色> <剧情 beat>`。
2. **按剧情融入（非照抄）**：把该 entry `## 锁定文本块` 的物理动作要点改写进 shot 的 `动作:` / `表情:`——保留物理动作内核与关键肌肉动作，但按本镜角色/机位/时长/剧情重新措辞、拆 beat。**不照抄**整段。
3. 更新表演库后，shot 页面点「🎭 按表演库重生成」可重新融入（FR-17）。

完整前后对比见 `_reference_usage.md`。库条目永远 generic（无剧目专名）。

## 验证流程（库建设者 + 验证者）

1. **撰写**：按四维 + 物理动作铁律写 `## 锁定文本块`，生成沿用 `_testrig.md` 骨架的**一个通用检验视频 prompt**（model-agnostic，唯一变量 = 锁定块）。entry 初始 `status: pending_review`。
2. **渲染打分（你 + Claude 对 prompt 统一打分）**：上传你的 actor 参考照，把通用 prompt 渲成视频、下载、一键导入（侧栏「📥 导入检验视频」→ `renders/`）。**你**在 perf 页面「表演评分」面板按三轴 1–5 打分；**Claude** 抽帧（`tools/extract_perf_frames.py`）看后用 `tools/perf_rate.py` 也评一次。过火越低越好，锚点按**精品微表情派**偏严。
3. **合议**：你与 Claude **均达标**（达意≥4 且 可识别≥4 且 过火≤2）⇒ `accept`(validated)；双方都评过但未同时达标 ⇒ `revise`(needs_revision)；一方未评 ⇒ `pending`。
4. **迭代**：revise → 按失败轴诊断改写（达意↓=词汇具体化/拆 beat；可识别↓=补判别器 AU/补内敛第三层；过火↑=降强度副词/改起始帧）→ 重测。

## 模型版本复验（重要）

`validated` 不是永久属性，是「截至某模型版本/日期的 validated」。Kling / Seedance 大版本跳变会使服从性结论失效——届时该模型为 passing_model 的**高强度（intensity≥4）条目强制复验**，过火基线整体漂移时全部复验。复验**追加新渲染行、不删旧行**（旧行是版本对照历史 + text-vs-起始帧 A/B 数据集）。每行渲染记录必带 `模型版本@日期`。

## 情绪索引（10 种短剧高频情绪，按题材承重力排序）

| # | 情绪 | 目录 | 功能主轴 | perf 范围 | 状态 |
|---|------|------|----------|-----------|------|
| ① | 压抑隐忍 | `yayi_yinren/` | 痛感 | perf_0001–0014 | **entry 已撰写**（14 条，pending_review，待渲染打分） |
| ② | 爽感反转/扬眉吐气 | `shuanggan_fanzhuan/` | 爽感 | perf_0015–0026 | entry 已撰写（12 条，pending_review） |
| ③ | 崩溃失控 | `bengkui_shikong/` | 痛感 | perf_0027–0038 | entry 已撰写（12 条，pending_review） |
| ④ | 狠戾/阴鸷 | `henli_yinzhi/` | 痛→爽 | perf_0039–0050 | entry 已撰写（12 条，pending_review） |
| ⑤ | 震惊错愕 | `zhenjing_cuoe/` | 惊悚 | perf_0051–0062 | entry 已撰写（12 条，pending_review） |
| ⑥ | 柔情/深情 | `rouqing_shenqing/` | 欲望 | perf_0063–0074 | entry 已撰写（12 条，pending_review） |
| ⑦ | 委屈/装可怜 | `weiqu_kelian/` | 欲望/痛感 | perf_0075–0086 | entry 已撰写（12 条，pending_review） |
| ⑧ | 不屑/嘲讽 | `buxie_chaofeng/` | 爽感 | perf_0087–0098 | entry 已撰写（12 条，pending_review） |
| ⑨ | 羞辱难堪 | `xiuru_nankan/` | 爽感反向 | perf_0099–0110 | entry 已撰写（12 条，pending_review） |
| ⑩ | 外放愤怒 | `waifang_fennu/` | 痛感/爽感 | perf_0111–0122 | entry 已撰写（12 条，pending_review） |

每个情绪目录的 `_emotion.md` 含：情绪定义（锚 FACS AU 核 + 短剧实战套路）、风格二分、子类型、本情绪 entry 清单（roster 表）。全库 perf 编号全局连续（perf_0001–0122）。

## 当前状态

- **全 10 情绪 122 条 entry 已撰写**（perf_0001–0122），四维槽位铺满，全部 `pending_review`，**等待渲染 + 你/Claude 评分合议**。时长按 beat 分配（4–12s）。
- **前置实验**：`_calibration.md`（中文 vs 英文）待渲染——在它得出「中文 land」结论前，所有中文 body 为待验证产物。
- **渲染队列**：每情绪 `_render_queue.md` 列出可复制 prompt。
- **下一步**：逐条渲染打分；accept 即定稿，revise 按失败轴改 prompt。shot 引用见 `_reference_usage.md`。
