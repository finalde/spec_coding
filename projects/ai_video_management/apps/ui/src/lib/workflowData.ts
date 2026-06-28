/** workflowData — single source of truth for the AI 短剧 pipeline visualization.
 *
 * Everything the WorkflowPage renders lives here: the six stages (with their
 * pre-reading / 内建提问 / QC skills / 避坑 / 产物 AND a per-stage internal-flow
 * Mermaid diagram), the review-suite call order, the three mechanisms, and the
 * overview Mermaid diagram. Adding detail later = edit this one file:
 *   - richer per-stage drill-down → extend Stage.detailDiagram / add fields
 *   - new sub-flow window → add a field + render it in StageDrawer
 * The components are intentionally generic so new data shows up with no code change.
 */

export type Layer = "横切" | "单镜" | "整集" | "全剧" | "整集+全剧";

export interface ReviewStep {
  ord: string;
  layer: Layer;
  skill: string;
  duty: string;
  conditional?: string;
}

export interface Stage {
  n: number;
  title: string;
  output: string;
  reads: string[];
  asks: string[];
  qc: string[];
  qcLabel: string;
  pitfalls: string[];
  accent: string;
  /** Internal flow of this stage, rendered in the stage drawer. */
  detailDiagram: string;
}

export const STAGES: Stage[] = [
  {
    n: 1,
    title: "核心创意立项",
    output: "1_立项/concept.md",
    reads: ["本 playbook", "agent_refs/project/ai_video.md (rule 14.1 / 14.2)", "BLUEPRINT §4"],
    asks: [
      "赛道题材（古风仙侠复仇）",
      "单集时长（90–120s）",
      "总集数 / 篇幅（自适应）",
      "目标平台（全平台 9:16）",
      "核心爽点主线（必填）",
      "核心人物对立（必填）",
      "每集硬钩规则（结尾必预埋危机 / 伏笔）",
    ],
    qc: ["人工确认"],
    qcLabel: "人工确认三件套：主角诉求 + 反派动机 + 长线伏笔齐全",
    pitfalls: ["不能模糊脑洞就开工", "反派必有自洽动机（非工具人）", "必须长线伏笔（玉佩 / 黑影式暗线）"],
    accent: "#0969da",
    detailDiagram: `flowchart TD
  a["读 concept 上游意图<br/>ai_video.md 14.1/14.2 · BLUEPRINT §4"] --> b{{"多选题 · 7 问<br/>赛道/时长/集数/平台/爽点/对立/钩规则"}}
  b --> c["起草立项策划单"]
  c --> c1["核心爽点主线 1 句"]
  c --> c2["人物对立: 主角诉求 + 反派动机 + 关键配角 + 暗线"]
  c --> c3["每集硬钩规则"]
  c1 & c2 & c3 --> d["concept.md"]
  d --> e{"人工确认<br/>三件套齐?"}
  e -->|否| b
  e -->|是| f["✓ 进阶段 2"]`,
  },
  {
    n: 2,
    title: "世界观 + 锁定人设",
    output: "2_世界观人设/{world.md, characters/, scenes/, props/, casting.md, style_guide.md}",
    reads: [
      "本 playbook",
      "CLAUDE.md AI-video 节",
      "agent_refs/project/ai_video.md (rule 1b / 12.1 / 12.3 / 12.5 / 12.7-A / 12.8)",
      "agent_refs/project/general.md",
      "1_立项/concept.md",
    ],
    asks: [
      "时代 / 地域（古风·架空王朝）",
      "力量体系 + 特效尺度（藏锋·无外放）",
      "势力划分（几方对立）",
      "角色清单（主 / 配 / 暗线清点）",
      "逐角色锁定（面部 / 服化 / 声口 / 动作 / voice_id / 调色）",
      "全剧调色（冷峻 / 暖金 / 阴郁…）",
      "场景清单（≥2 镜复用的地点）",
    ],
    qc: ["ai_videos__格式契约"],
    qcLabel: "格式契约：锁定串 byte-identical / voice_id 锁 / 零 hex / bg 档齐 / 眼睛不发光",
    pitfalls: [
      "脸靠选角图锁（不写五官）",
      "服装靠 byte-identical 复制锁",
      "藏锋规则必写进 world.md 力量体系",
      "色彩零 hex（用自然色名）",
    ],
    accent: "#8250df",
    detailDiagram: `flowchart TD
  a["读 concept · ai_video.md 1b/12.1/12.3/12.5/12.7-A/12.8"] --> b{{"多选题<br/>时代/力量/势力/角色清单/逐角色锁定/调色/场景"}}
  b --> w["world.md<br/>bg 代号 · 藏锋力量规则 · 势力"]
  b --> ch["characters/{角色}/"]
  ch --> ch1["Seedream ref 图 prompt"]
  ch --> ch2["turntable 建立视频"]
  ch --> ch3["锁定描述符 byte-identical"]
  ch --> ch4["voice_id 全剧锁定"]
  b --> sc["scenes/{场景}/ 场景档 + bg plate"]
  b --> ca["casting.md voice_id 总表"]
  b --> sg["style_guide.md 全剧渲染样式串"]
  w & ch1 & ch2 & ch3 & ch4 & sc & ca & sg --> qc{{"QC · ai_videos__格式契约<br/>锁定串/voice_id/零hex/bg档齐/眼不发光"}}
  qc -->|blocker=0| done["✓ 进阶段 3"]
  qc -->|blocker| b`,
  },
  {
    n: 3,
    title: "分集大纲",
    output: "3_大纲/arc_outline.md",
    reads: ["本 playbook", "BLUEPRINT §4", "1_立项/concept.md", "2_世界观人设/（world / 人物卡 / 场景档 / casting / style_guide）"],
    asks: [
      "总集数切割方式（三幕骨架 + 一行/集）",
      "每集三联标注（上集承接 / 本集核心 / 下集伏笔）",
      "起承转钩四段（开场钩 / 铺垫 / 反转爽点 / 钩尾悬念）",
      "每段镜数 + 时长（起2–3 / 承4–6 / 转3–5 / 钩尾1–2，合计 90–120s）",
      "每集钩尾类型（危机 / 情感 / 实力 / 信息 四选一）",
      "节奏规划（压抑慢镜 / 冲突快切 / 悬念长暗镜）",
    ],
    qc: ["ai_videos__剧情连贯", "ai_videos__全剧序列"],
    qcLabel: "剧情连贯（整集）+ 全剧序列（全剧）：跨集承接 / 钩 / 爽点单调递进 / 无重复宣告",
    pitfalls: ["强制标镜号区间（S{aa}–S{bb}）", "每集结尾必预埋钩（四类择一）", "长线伏笔跨集呼应不矛盾", "不引入 world.md 未有设定"],
    accent: "#1a7f37",
    detailDiagram: `flowchart TD
  a["读 concept + 世界观人设"] --> b{{"多选题<br/>切割/三联标注/四段镜数预算/钩类型/节奏"}}
  b --> c["逐集编排"]
  c --> c1["三联: 上集承接 · 本集核心 · 下集伏笔"]
  c --> c2["起承转钩四段 + 镜号区间 S{aa}–S{bb}"]
  c --> c3["钩尾类型四选一"]
  c1 & c2 & c3 --> d["arc_outline.md"]
  d --> q1{{"QC · 剧情连贯<br/>整集: 情节链/动机/爽点"}}
  q1 --> q2{{"QC · 全剧序列<br/>全剧: 跨集承接/钩/爽点递进/无重复宣告"}}
  q2 -->|blocker=0| done["✓ 进阶段 4"]
  q2 -->|blocker| b
  note["敏捷: 只定骨架 + 前几集细纲<br/>后续各集留松"] -.-> c`,
  },
  {
    n: 4,
    title: "单集文学剧本（台词）",
    output: "4_剧本/episodes/epNN/{script.md, dialogue.md}",
    reads: [
      "本 playbook",
      "3_大纲/arc_outline.md",
      "2_世界观人设/characters/{角色}.md（声口模板 / voice_id）",
      "world.md",
    ],
    asks: [
      "本集起承转钩拆段（沿用 arc_outline 预算）",
      "台词口语化强度（强口语·脱口而出 / 短句 / 语气词）",
      "内心独白 OS 用量（仅关键节点）",
      "系统 UI 文字风格（鎏金对话框·极简冷冽·仅主角可见）",
      "三类台词标注（口头对白 / 内心独白 / 系统 UI 逐行标）",
    ],
    qc: ["ai_videos__台词大师", "ai_videos__白话大师"],
    qcLabel: "台词大师（说人话 / 因果 / 声口 / 情绪 / 节奏）+ 白话大师（台词仍书面时过）",
    pitfalls: ["严禁跳过剧本直接写 prompt", "去书面长句 / 对仗 / 破折号堆砌", "白话铁律（禁古语·吾 / 汝 / 乃 / 之乎者也）"],
    accent: "#bf3989",
    detailDiagram: `flowchart TD
  a["读 arc_outline + 人物卡声口模板 + world.md"] --> b{{"多选题<br/>拆段/口语强度/OS用量/系统UI/三类标注"}}
  b --> s["script.md"]
  s --> s1["镜号 | 时长 | 场景 | 画面动作"]
  s --> s2["台词三类标注: 口头对白 / 内心独白 / 系统UI"]
  b --> dlg["dialogue.md 纯台词"]
  s1 & s2 & dlg --> q1{{"QC · 台词大师<br/>说人话/因果/声口/情绪/人称/节奏"}}
  q1 --> q2{{"QC · 白话大师<br/>朗读测试·去文言/对仗/翻译腔"}}
  q2 -->|blocker=0| done["✓ 进阶段 5"]
  q2 -->|blocker| b`,
  },
  {
    n: 5,
    title: "分镜运镜设计",
    output: "5_6_分镜与prompt/episodes/epNN/{shotlist.md, shots/shotNN/shotNN.md}（运镜字段）",
    reads: [
      "本 playbook",
      "BLUEPRINT §4 / §5 / §6",
      "agent_refs/project/ai_video.md (rule 5 / 12.4)",
      "agent_refs/project/ai_video_jingbie.md · ai_video_shouweizhen.md",
      "4_剧本/episodes/epNN/script.md",
      "2_世界观人设/characters · scenes · style_guide",
    ],
    asks: [
      "每场景连贯镜序（按 script 镜号顺拆）",
      "每镜情绪目的（先标情绪再出机位·本阶段命门）",
      "走位与相对朝向（按方位 plate 锁同侧 + 写死相对朝向）",
      "单镜时长（3–15s 按 beat 给）",
      "光影色调基调（跟 style_guide 情绪光表）",
    ],
    qc: ["ai_videos__站位朝向", "ai_videos__运镜", "ai_videos__动作表演", "ai_videos__光线色调", "ai_videos__时长节奏"],
    qcLabel: "五道审查：站位朝向 + 运镜 + 动作表演 + 光线色调 + 时长节奏（含打斗→武打设计，涉超自然→特效设计）",
    pitfalls: [
      "先情绪后机位（禁堆运镜名词）",
      "A 别背对 B 说话",
      "同角色每镜只具名一次",
      "动作配时间窗 / 配角有反应",
      "内心独白视线写死落点；眼睛不写发光",
    ],
    accent: "#9a6700",
    detailDiagram: `flowchart TD
  a["读 script + 人设/场景/style_guide<br/>+ 景别 ref + 首尾帧 ref"] --> b{{"多选题<br/>镜序/情绪目的→机位/走位朝向/时长/光影"}}
  b --> sl["shotlist.md 连贯镜序"]
  sl --> loop["逐镜 shots/shotNN/shotNN.md 运镜字段"]
  loop --> f1["情绪目的 → 构图机位"]
  loop --> f2["走位 + 相对朝向（方位 plate）"]
  loop --> f3["动态运镜 + 动作分秒"]
  loop --> f4["单镜时长 3–15s 按 beat"]
  loop --> f5["光影色调"]
  f1 & f2 & f3 & f4 & f5 --> qc{{"QC · 五道审查（单镜）<br/>站位朝向 · 运镜 · 动作表演 · 光线色调 · 时长节奏"}}
  qc --> cond["含打斗 → 武打设计<br/>涉超自然 → 特效设计"]
  cond -->|blocker=0| done["✓ 进阶段 6"]
  qc -->|blocker| b`,
  },
  {
    n: 6,
    title: "标准化 AI 分镜 Prompt",
    output: "5_6_分镜与prompt/episodes/epNN/{各 shotNN.md（五层+配音）, all_shot_prompts.md, intro_cards.md}",
    reads: [
      "本 playbook",
      "阶段 5 的 shotNN.md（运镜字段）",
      "2_世界观人设/characters/{角色}.md（角色识别标签 / voice_id）",
      "2_世界观人设/scenes · style_guide.md",
      "4_剧本/episodes/epNN/{script.md, dialogue.md}",
    ],
    asks: [
      "目标生成模型（Seedance + Kling）",
      "渲染风格（影视级真人写实仙侠·全剧统一渲染样式串）",
      "负面词块（沿用全剧固定负面词块）",
      "字幕策略（prompt 零字幕·后期自加）",
    ],
    qc: ["ai_videos__格式契约", "ai_videos__审查总编排"],
    qcLabel: "格式契约（K1–K26）+ 出片前全 审查总编排（单镜→整集→全剧三层）",
    pitfalls: [
      "特效严限无外放·人物不自发光（禁金光 / 瞳光 / 裂纹）",
      "台词与画面剥离（画面零字幕）",
      "剪影暗线只写轮廓禁五官",
      "多角色同框同角色只具名一次",
    ],
    accent: "#cf222e",
    detailDiagram: `flowchart TD
  a["读 阶段5 运镜字段 + 角色识别标签 + voice_id + 剧本"] --> b{{"多选题<br/>生成模型/渲染风格/负面词块/字幕策略"}}
  b --> p["每 shotNN.md 五层 prompt"]
  p --> p1["场景 bg"]
  p --> p2["锁定角色识别标签"]
  p --> p3["剧情分镜动作 + 台词块（零字幕）"]
  p --> p4["光影氛围"]
  p --> p5["渲染参数 + 负面词块"]
  b --> tts["## 台词配音 prompt（voice_id 锁）"]
  p1 & p2 & p3 & p4 & p5 & tts --> asm["all_shot_prompts.md 汇编"]
  asm --> q1{{"QC · 格式契约 K1–K26"}}
  q1 --> q2{{"QC · 审查总编排 0→9<br/>单镜 → 整集 → 全剧"}}
  q2 -->|blocker=0| done["✓ 本期完成: 标准化 AI 分镜 Prompt"]
  q2 -->|blocker| b`,
  },
];

export const REVIEW_SUITE: ReviewStep[] = [
  { ord: "0", layer: "横切", skill: "ai_videos__格式契约", duty: "字段 / 字幕 / 锁定 / hex / 字数 / 比例时长 机械校验" },
  { ord: "1", layer: "单镜", skill: "ai_videos__台词大师", duty: "台词：说人话 / 白话 / 因果 / 信息量 / 声口 / 情绪 / 人称 / 节奏" },
  { ord: "1b", layer: "单镜", skill: "ai_videos__白话大师", duty: "白话口语化专项·朗读测试·去文言 / 对仗格言 / 翻译腔" },
  { ord: "2", layer: "单镜", skill: "ai_videos__站位朝向", duty: "站位 / 朝向 / 眼神 / 走位（别背对说话、防角色重复）" },
  { ord: "3", layer: "单镜", skill: "ai_videos__运镜", duty: "景别 / 角度 / 镜头 / 运镜 / 180°轴线 / 视线匹配 / 相邻镜不重复" },
  { ord: "4", layer: "单镜", skill: "ai_videos__动作表演", duty: "动作配时间轴 / 落钩不干站 / 配角反应 / 微表情 / 四层密度" },
  { ord: "4b", layer: "单镜", skill: "ai_videos__武打设计", duty: "打戏专项：招式 / 攻防回合 / 受击打击感 / 藏锋边界", conditional: "仅打斗" },
  { ord: "5", layer: "单镜", skill: "ai_videos__时长节奏", duty: "时长合理性裁决：台词念得完 / 动作演得开 / 不赶不拖" },
  { ord: "6", layer: "单镜", skill: "ai_videos__光线色调", duty: "光线色调随情绪 / 场景一致 / 色彩锁定 / 回忆滤镜 / 眼不发光" },
  { ord: "6b", layer: "单镜", skill: "ai_videos__特效设计", duty: "特效专项：威能 / 法术 / 灵气 / 玉佩 / 暖流 / 系统UI / 异象", conditional: "仅超自然" },
  { ord: "7", layer: "整集", skill: "ai_videos__剧情连贯", duty: "情节链 / 动机 / 爽点落地 / 系统互动 + 相邻镜衔接 + 跨镜重复" },
  { ord: "8", layer: "全剧", skill: "ai_videos__全剧序列", duty: "跨集查重宣告 / 签名台词 / 开场结尾 + 爽点递进 + 跨集专名" },
  { ord: "9", layer: "整集+全剧", skill: "内建·立意安全 gate", duty: "红果新规：低俗 / 血腥 / 价值观倾斜 + 正向立意是否兑现" },
];

export const MECHANISMS: { title: string; body: string }[] = [
  { title: "① 每步 QC 关卡", body: "每阶段末强制过审，blocker 清零方可进下一步（严格度 = 严）。由全流程编排强制。" },
  {
    title: "② 每次 update 复核",
    body: "任何对已有产物的改动 / 重生，默认跑受影响范围的 审查总编排 + 在 specs/ai_video/{name}/changelog.md 记一条。",
  },
  {
    title: "③ 反馈 → 进化",
    body: "用户每条实战反馈 → surgical 更新对应 playbook / 审查 skill / agent_refs + 记一条「教训」（带来源镜号 / 引用）。流程越用越强。",
  },
];

export const GLOBAL_DEFAULTS =
  "古风仙侠复仇为首要赛道 · 单集 90–120s · 9:16 多平台 · 藏锋·无外放 · 人设面部+服化+声口全锁 · 起承转钩四段 · 强口语白话 / OS 仅关键 · 鎏金极简系统 UI · 三声线解耦后期 mux · 情绪→运镜映射 · 单镜 3–15s 按 beat · Seedance+Kling · 影视写实仙侠 · 负面词块必填 · prompt 零字幕后期加 · 锁定描述符 + voice_id + Seedream ref图 + turntable · 多角色同框同角色只具名一次";

/** Overview Mermaid for the 流程图谱 view. Stage nodes are click-bound to
 * wfStageClick(n) (registered on window by WorkflowPage) → opens the drawer. */
export const PIPELINE_DIAGRAM = `flowchart TD
  start(["开始 / 从文件树派生进度续跑"]) --> s1
  s1["阶段 1 · 核心创意立项<br/><small>1_立项/concept.md</small>"] --> q1{{"QC · 人工确认"}}
  q1 -->|齐全| s2
  s2["阶段 2 · 世界观+锁定人设<br/><small>world / characters / scenes / casting / style_guide</small>"] --> q2{{"QC · 格式契约"}}
  q2 -->|blocker=0| s3
  s3["阶段 3 · 分集大纲<br/><small>3_大纲/arc_outline.md</small>"] --> q3{{"QC · 剧情连贯 + 全剧序列"}}
  q3 -->|blocker=0| s4
  s4["阶段 4 · 单集文学剧本<br/><small>episodes/epNN/script + dialogue</small>"] --> q4{{"QC · 台词大师 + 白话大师"}}
  q4 -->|blocker=0| s5
  s5["阶段 5 · 分镜运镜设计<br/><small>shotlist + shotNN.md 运镜字段</small>"] --> q5{{"QC · 站位/运镜/动作/光线/时长"}}
  q5 -->|blocker=0| s6
  s6["阶段 6 · 标准化分镜 Prompt<br/><small>五层 prompt + 台词配音 + all_shot_prompts</small>"] --> q6{{"QC · 格式契约 + 审查总编排"}}
  q6 -->|blocker=0| done(["✓ 标准化 AI 分镜 Prompt<br/>（阶段 7 渲染剪辑暂不做）"])

  click s1 call wfStageClick("1")
  click s2 call wfStageClick("2")
  click s3 call wfStageClick("3")
  click s4 call wfStageClick("4")
  click s5 call wfStageClick("5")
  click s6 call wfStageClick("6")

  classDef stage fill:#ffffff,stroke:#0969da,stroke-width:2px,color:#1f2328,cursor:pointer;
  classDef gate fill:#fff8c5,stroke:#9a6700,color:#59470d;
  classDef term fill:#dff7e6,stroke:#1a7f37,color:#1a7f37;
  class s1,s2,s3,s4,s5,s6 stage;
  class q1,q2,q3,q4,q5,q6 gate;
  class start,done term;`;
