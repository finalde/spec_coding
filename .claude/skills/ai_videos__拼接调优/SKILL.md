---
name: ai_videos__拼接调优
description: AI 短剧「首尾帧接缝」一键调优+拼接+评分工具。当用户说"调优/拼接 epN""用 seam_tune 拼 epN""给 epN 接缝调参/评分""seam 调优""拼接 ep2""出 ep3 的片"或想对某集出片并优化承接缝平滑度时触发。它对指定 ep 跑 tools/seam_tune.py(扫 trim×depth 为每个承接缝找最平滑接法·写回 seam_plan.json·拼出 ep{NN}.mp4)+ tools/seam_metrics.py(光流+SSIM 打分·存 dashboard sidecar),报告每缝最优参数/分数/秒数区间;承接帧差过大无法平滑时报为 prompt 问题。参数=ep 编号(如 ep2、3)。
---

# 首尾帧接缝调优 + 拼接 + 评分（seam tune / stitch / score）

把「找最优裁切&补帧参数 → 用最优方案拼成片 → 客观打分存 dashboard」串成一条命令工序，对**任意一集**反复调用。底层是两个仓库工具：`tools/seam_tune.py`（调优+拼接）与 `tools/seam_metrics.py`（评分），本 skill 只是按标准流程驱动它们并把结果讲清楚。

## 何时用
用户给一个 ep 编号要「调优 / 拼接 / 出片 / 接缝评分」时。典型：「调优 ep2」「拼接 ep3」「给 ep2 接缝调参并出片」「ep5 接缝评分」「seam_tune 跑一下 ep4」。

## 入参
**唯一参数 = ep 编号**（`ep2` / `2` / `ep02` 都接受）。可选：用户指定 drama（默认 `wushen_juexing`）、是否只调不出片、是否要多接法对比。

## 步骤

### 1. 解析 ep 目录
把编号零补到两位（`2`→`ep02`），用 Glob 找含 `seam_plan.json` 的 ep 目录：
`ai_videos/**/episodes/ep{NN}/seam_plan.json`
- 命中唯一 → 用它。
- 命中多个（多个 drama）→ 用 `AskUserQuestion` 问哪个 drama（AUTONOMOUS 模式则选 `wushen_juexing` 并在结尾注明）。
- 命中 0 个 → 报「ep{NN} 没有 seam_plan.json / 该集还没分镜」，停。

记 `EPDIR` = 该 ep 目录（路径含中文 `5_6_分镜与prompt`，下面命令务必整段加引号）。

### 2. 调优 + 拼接（seam_tune）
从仓库根 `C:\workspace\spec_coding` 跑（**必须** `PYTHONIOENCODING=utf-8`，否则中文路径的 print 在 Windows cp1252 stdout 上会崩）：
```bash
PYTHONIOENCODING=utf-8 python -u tools/seam_tune.py "<EPDIR>" --apply --build
```
- 它对每个**首尾帧承接缝**（由 shot 的 `衔接=承接` 决定，与当前 plan 方法无关，故已调过的缝仍会被重调）扫 `trim × depth`（trim-butt + RIFE）候选，每个候选用与 dashboard **同一套 cv2 四指标**打分，按**分层规则**选最优：**先比四项是否全 ≥80（达标的优先），达标档内按加权分排名；没有任何候选达标时用 leximin（字典序 maximin——先比最短板，最短板≈持平·差<3 分时再比次短板，依次类推；4×80 优于 3×100+1×79，且瓶颈板对所有候选都封顶在低值时不会为 0.x 的无意义提升牺牲其它板），加权分只做最后 tiebreak**。`--apply` 写回 `seam_plan.json`，`--build` 拼出 **`ep{NN}.mp4`**（默认正式名）。承接缝不会被选成裸硬切（至少裁切）。
- 该命令较慢（每缝建多个临时拼接 + RIFE 试桥），用 `run_in_background` 跑、跑完读输出。
- 变体：用户只想看参数不出片 → 去掉 `--build`；只想试不写盘 → 去掉 `--apply`。

**prompt 问题识别**：输出里若有 `seam ...: ... PROMPT problem`（承接帧差 >40，首尾帧根本不匹配）→ 任何 trim/depth 都救不了，**如实报给用户这是该 shot 的 prompt/承接帧问题**（建议重锁首尾帧或改运镜对齐景别），不要假装拼顺。

### 3. 评分 + 存 dashboard（seam_metrics）
```bash
PYTHONIOENCODING=utf-8 python -u tools/seam_metrics.py "<EPDIR>" --no-compare --save
```
- 给每个承接缝打分（M1 速度连贯 / M2 无冻结 / M3 无跳变 / M4 结构=SSIM 与运动补偿残差比取更差，加权均）+ **秒数区间**，`--save` 写 `ep{NN}.seam_scores.json`（打开该集页面自动显示 dashboard）。打分前**先按运动补偿残差的局部突出度经验定位真实接缝帧**（不信时长推算，dedup 会偏一两帧），否则硬切会因定位偏移漏测而虚高、RIFE 反被比下去。
- 用户要「多接法对比排名」→ 去掉 `--no-compare`（慢，每缝再跑硬拼/裁切/RIFE）。

### 4. 报告
给用户讲清楚：
- 每个承接缝：最优接法 + 参数（如 `trim@0.10`）、**分数**、在成片里的 **@秒数（区间）**。
- 全集 **总分 + 等级**（A/B/C/D）。
- ep{NN}.mp4 是否已生成。
- 若有 prompt 问题缝：单独列出、说明要改 prompt 不是改参数。

## 注意
- 只动**首尾帧承接缝**；硬切缝不碰。
- 反复可调用：对已是 trim 的缝也会重调，不会跳过。
- 仅按 plan 拼请走 webapp「拼接成片」按钮；**调优必须用本 skill / `seam_tune`**（webapp 不调优）。
- 评分慢（光流），`seam_metrics` 也用 `run_in_background`。
- 默认 INTERACTIVE：drama 不明就问；AUTONOMOUS 模式不问、按默认并注明。
