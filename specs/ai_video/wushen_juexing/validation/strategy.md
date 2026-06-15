# Validation strategy — wushen_juexing

Run: wushen_juexing-20260613-170909
spec: specs/ai_video/wushen_juexing/final_specs/spec.md
工作单元粒度: EP1（novel 一集 = 一个 work unit）。本轮只产 EP1。

## Schema precedence note（load-bearing）
`validation/ai_video.md` move #4 仍引用已废止的分离文件 schema（`shotNN_kling.md`/`_seedance.md`/`_lastframe_seedream.md`/`shot01_startframe_seedream.md` + seam-frame pipeline）。`project/ai_video.md` rule 5 v3 + rule 11 已**废止 seam-frame**，改为**单文件 `episodes/ep01/shots/shotNN.md` 内含三 code block（## 起始帧 / ## 结束帧 / ## 视频 prompt）**。按 CLAUDE.md precedence（project ref > stage ref），**验证以现行单文件三块 schema 为准**；出现旧分离文件反而判 blocker（structure_schema S-SCHEMA-OLDFILES）。

## Levels chosen
- **acceptance_criteria** — 始终包含；7 个 Gherkin flow 覆盖骨架/角色/EP1 素材/前10秒铁律/时长/零hex/publish。
- **bdd_scenarios** — 始终包含；8 个 feature 行为（冷开场/首爽点/二段打脸/末镜钩/行动→反应/钩子密度/四色辨识/觉醒 motif），含反例。
- **structure_schema** — ai_video 必需（move 1/2/4/5）：layout、零 hex、shot 三块 schema、废止字段、时长、比例、语言合规。
- **consistency** — ai_video move 3：角色 bible+立绘存在、一句话锁定 byte-identical、四主色不撞、觉醒态登记为状态变体。
- **story_dialogue** — ai_video move 9（短剧故事+台词大师）：台词四轴+hook落地+情节链+声口+前10秒铁律。
- **publish_compliance** — ai_video move 5/6：publish.md 字段齐备+IAA 标注+敏感词/构图人工复核。

不含：unit/system/performance/security/accessibility —— 本任务无代码、无 UI、无外部输入，不适用。

## Per-level summary

### acceptance_criteria（blocker 级门槛）
- 骨架文件齐备且中文（README/world/style_guide/arc_outline）；world 含铁律句「资质决定上限的高度，体质改写上限本身」可 grep。
- 4 角色 bible + 立绘 prompt 齐备，一句话锁定跨引用 byte-identical。
- EP1 五件套（script/dialogue/shotlist/shots/publish）齐备；前 10 秒铁律 S01 即冲突；总时长 ∈ [85,100]、约 14–18 镜、≤15s/镜；零 hex；publish 含 IAA。

### bdd_scenarios
- 可走查行为 + 显式反例（世界观旁白前置 / 打脸顺序颠倒 / 反应镜缺失 / hex 命中 = FAIL），绑定计时锚点 6s/30s/120s/末镜。
- 二段打脸顺序铁律：先王体资质→再武神躯，顺序不可颠倒。

### structure_schema（greppable，6 组）
- Layout（rule 2 novel skeleton + `cN_中文名/cN_中文名.md` 同名非补零）；零 hex `grep -rnE '#[0-9a-fA-F]{6}'`=0；shot 三块（小说原文加粗出场名 / Shot context / 起始帧·结束帧·视频）+ 紧凑中文标签 `01集NN镜{视|始|末}`；必填视频字段（骨架版允许）；**禁字段**（负向/场景视角锚/body 角色/块内重复标题行）；时长 ≤15s·`时长合计`∈[85,100]·镜数∈[14,18]；语言 ≥95% 中文。
- 结构/schema/时长/hex/语言失败 = blocker；加粗名缺失、多拍和校验、OS 口型 = warning。

### consistency（漂移/缺失 = blocker）
- C-1 bible 存在；C-2 未声明角色引用=blocker；C-3 立绘 prompt 存在（内嵌或独立，不锁文件名——适配本项目单文件 per-character）；C-4 一句话锁定跨 EP1 byte-identical；C-5 四主色不撞；C-6 觉醒态暖金裂纹登记为裴知秋状态变体。
- 关键提醒：dossier 残留占位名「裴玄」已被 spec 定名「裴知秋」取代——bible/shot 一律用 **裴知秋**。

### story_dialogue（短剧故事+台词大师，inline patch 格式）
- 台词四轴（通俗易懂/信息量/节奏≤15字/声口）；声口表锚定 spec 站位（裴知秋隐忍→锋锐 / 裴昭轻蔑 / 裴霆威严冷酷 / 凌虚子清冷）。
- 台词失败=warning+改写；hook 未落地 / 声口矛盾 / 后续 arc 名字早现 = blocker；撞句模板=warning。
- 红果前 10 秒铁律 hardwired：禁世界观旁白前于冲突=blocker、第1分钟首爽点缺位=blocker、3分钟末弱/缺 cliffhanger=blocker。禁前向引用清单：门派名号细节、~40集身世真相、未登场红颜/兄弟线人名。

### publish_compliance（13 条）
- P-1..P-11 自动 blocker：标题≤30字 / 副标题 / 简介≤200字 / 5–10 hashtags / 封面指定镜号 / `变现模式: IAA 免费+广告`（禁付费充值）/ 5 题材标签全在 / 总集数80·4–5字推广关键词 / 72h 运营提示。（follow-up 010：prompt 不写比例，不再校验）
- P-12/P-13 = `requires_manual_walkthrough`（主观）：神/帝/王命名 + 羞辱桥段审核尺度（NFR-5）；EP1 hook 镜构图（move 5 novel）。

## Cross-cutting concerns
- **裴知秋定名一致性**：dossier 视觉角度遗留「裴玄」，全部 stage-6 产物必须用 spec 定名「裴知秋」——consistency 与 story_dialogue 双重把关，避免 anachronism/drift。
- **3 分钟双爽点张力**：行业主流 1–2 分钟，本剧 3 分钟需双爽点（系统首爽 + 觉醒大爽），bdd + story_dialogue 共同盯节奏，防中段松。
- **二段打脸顺序**：王体资质→武神躯顺序不可颠倒（bdd 反例 + story_dialogue hook 落地）。
- **零 hex 是跨文件不变量**：structure_schema 全树 grep + acceptance 双查。
- **敏感词/审核**：NFR-5 体质境界名（神/帝/王）与羞辱桥段 → 人工复核，不自动阻断。

## How runtime validation will use this（stage 6, work_unit_kind=ai_video_episode）
EP1 work unit 写完后，并行 spawn 6 个 validator（每 level 一个），各读其 level 文件 + EP1 产物：
- structure_schema / consistency / publish_compliance / acceptance：greppable 自动检查（layout、零hex、时长合计、字段、byte-identical、publish 字段）。
- story_dialogue / bdd：逐镜走查台词与 hook 落地，输出 inline patch list。
- pass 判定：0 blocker。warning 记录不阻断。任一 blocker → surgical 修 → `exec.revision.applied` → 重验，cap 3 轮（CLAUDE.md 迭代界限）；同 issue_id 连续两轮未消 → `pipeline.halted`。
- 全自动 level 通过后，emit `validation.requires_manual_walkthrough`：提示用户打开 character 立绘 + shotlist + 随机 2–3 个 shot prompt，确认跨镜角色描述一致、shotlist 读起来连贯，并复核敏感词/hook 构图（P-12/P-13）。用户确认关闭 EP1 work unit。

## Promotion-preservation check
本任务各 spec 阶段当前**无 `<stage>/promoted.md` sidecar**（用户未 pin 任何条目），故无 pin 需保留。一旦后续用户在 webapp pin 条目：interview/findings/final_specs/validation 四阶段的每个 pin 必须在该阶段重生成产物中 verbatim 出现（missing pin = critical）。Stage 6（`ai_videos/` 代码/产物）v1 不支持 promotion，不生成此检查。
