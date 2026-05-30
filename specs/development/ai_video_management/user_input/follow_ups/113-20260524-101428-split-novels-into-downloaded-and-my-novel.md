# Follow-up draft 113 — 2026-05-24
Summary: 把现有顶层目录 `novels/` 重命名为 `downloaded_novels/`（即"下载来的他人小说"基线语料），并新增同级目录 `my_novel/`（我自己撰写的原创小说，为 AI 短剧生产准备）。webapp `ExposedTree` 现在容纳三个顶层根：`ai_videos/`、`downloaded_novels/`、`my_novel/`。沙箱白名单、tree-reader 分区、容器 DI、CLI 下载器、前端类型注释、相关测试同步更新。`my_novel/` 不应用 `_meta.json.complete == True` 筛选（原创稿不是爬下来的，没有 complete 字段），按子目录原样呈现。

## 用户原话
> under ai_videos_management rename current downloaded novels folder to downloaded_novels, I am going to introduce a new folder called my novel, under my novel, I am going to ask you to take a look at existing downloaded novels, and then make up a new novel for me, 題材仍然是某一類，比如仙俠，請把諸多小説當作baseline，編排一部新的小説，而且保證不會有版權重複問題，但是要保持小説的競猜性，你可以從多部小説中提取要素，更換人名，然後你還要與時俱進，從網上research跟多有關此類型題材的信息系和熱點，把他融入到小説中。小説的最終目的是拍攝ai短劇

## 用户多选裁决
1. **顶层布局**：`downloaded_novels/` + `my_novel/` 两个同级目录（不在外层包一层 parent；不用复数 `my_novels/`）。
2. **新小说创作工作流**：通过 `/agent_team`（task_type=ai_video, sub_type=novel）跑完整 spec-driven 六阶段，研究阶段拆为 baseline 提取 / 题材网络热点 / 人物去版权化三个 angle。
3. **webapp 同步更新**：全量改 — `_ALLOWED_TOP_LEVEL`、`ExposedTree`、tree_reader、readers/writers、routes、DTO、前端类型、CLI、tests 都一起改到位，不留分裂状态。

## 设计

### 目录形态

```
spec_coding/
├── ai_videos/                            # 不变
├── downloaded_novels/                    # 从 novels/ 重命名而来（保留 git 历史）
│   └── xianxia/
│       ├── fanren_xiuxian_zhuan/
│       ├── ...                           # 14 本下载小说全部跟随
│       └── zhutian_daozu/
└── my_novel/                             # 新增；初始只含 .gitkeep
    └── (跑 /agent_team 后落 my_novel/{slug}/)
```

### webapp `ExposedTree` 沙箱

`libs/common/safe_resolve.py` 与 `libs/common/exposed_tree.py` 的 `_ALLOWED_TOP_LEVEL`：

```python
_ALLOWED_TOP_LEVEL: frozenset[str] = frozenset({"ai_videos", "downloaded_novels", "my_novel"})
```

`ExposedTree`：
- `novel_dirs()` → 拆分为 `downloaded_novel_dirs()` + `my_novel_dirs()` 两个公开方法，分别返回各自 root 下的一级子目录。

### tree_reader 分区

`libs/infrastructure/readers/tree__reader.py` 改输出三个 section（顺序固定）：

1. **"AI Videos"**（保持不变）
2. **"Downloaded Novels"**（原 "Novels" 改名 + 指向 `downloaded_novels/`；保留 `_meta.json.complete == True` 筛选 + CANONICAL_NOVELS 排序 + 中文 display_name 映射）
3. **"My Novel"**（新增；指向 `my_novel/`；不应用 complete 筛选；按 `name.lower()` 字典序排序；项目目录有 `README.md` H1 中文标题时填 `display_name`，与 ai_videos section 共用 `_project_zh_title()` 抽取器）

### 容器 DI

`apps/api/container.py`：
- `novels_root` 提供者 → 重命名为 `downloaded_novels_root`，并新增 `my_novel_root`。
- `NovelDownloader`、`NovelQuery` 的 `novels_root` 参数都绑定到 `downloaded_novels_root`（这两个类的"novels"指的是"下载来的小说"概念）。

### CLI 下载器

`apps/cli/novel_download.py` 的 `_resolve_novels_root()` 改为查找 `downloaded_novels/`（而非 `novels/`）；`NOVELS_ROOT` 环境变量名保留（向后兼容）但语义指向新位置。打印的标签从 `novels_root:` 改为 `downloaded_novels_root:`。

### 前端类型

`apps/ui/src/types.ts` 中 `display_name` 注释更新，提及 `downloaded_novels/{category}/{slug}/` 与 `my_novel/{name}/` 两种使用场景。前端代码没有任何地方 hardcode `"Novels"` 字符串（只有 `Home.tsx` 通过 `c.name === "AI Videos"` 拿 AI Videos 区，本次不受影响）。

### 测试

- `test_tree_walker_consumer_walk.py`
  - `test_tree_sections_order` 断言由 `["AI Videos", "Novels"]` → `["AI Videos", "Downloaded Novels", "My Novel"]`。
  - 原 `test_novels_section_walks_repo_novels_dir` 拆为 `test_downloaded_novels_section_walks_repo_downloaded_novels_dir` 与 `test_my_novel_section_walks_repo_my_novel_dir`。
- `test_boot_smoke.py::test_get_tree_returns_expected_sections` 与 `test_api_security_three_shapes.py::test_get_tree_unguarded` 的 section 名单同步更新。

### Phase B：用 `/agent_team` 产出第一部原创仙侠小说

新发 spec-driven 任务 `task_type=ai_video, sub_type=novel`，最终产物布局：

- 小说原稿：`my_novel/{slug}/`（中文文件内容；slug 为 pinyin/英文）。
- AI 短剧产物：`ai_videos/{slug}/`（character refs、shot 列表、Kling/Seedance prompts 等）。
- spec-driven 流水线：`specs/ai_video/{slug}/` 全套阶段产物。

研究阶段 angle（playbook 里会重写，这里先框定方向）：
1. **`angle-baseline_extraction.md`** — 把 `downloaded_novels/xianxia/` 14 本小说作为 baseline，抽取可复用要素：世界观骨架（修炼境界体系、宗门 / 散修 / 魔门三方格局）、主角原型（卷王 / 反套路懒人 / 重生 / 散修登仙）、典型升级节奏、女配 / 死敌 / 师父原型、关键钩子（夺舍、家族复仇、传承空间、莫名信物）。每条要素附"来自哪 N 本"和"哪些必须改名 / 改设定才不撞版权"。
2. **`angle-trend_research.md`** — 走 WebSearch / WebFetch，研究 2025–2026 仙侠短剧 / 网文 / 短视频热点（短剧平台爆款选题、爆款标题模板、当下读者讨厌的反派塑造、最近 6 个月仙侠类抖音 / 小红书话题、付费转化率高的情绪节点）。把热点融进设定与剧情节拍。
3. **`angle-character_anonymization.md`** — 系统化的人物 / 地名 / 功法名去版权化策略：把基线小说里的专有名词逐条列出，给出我方替代命名规则（如"灵根 → 道骨"、"凡人 → 散修"等避免直接撞名），并产出新主角 / 反派 / 师门的最终命名表。

验证阶段（stage 5）针对 short-drama 落地新增专项 level：
- 商业可行性（爆款选题 / 平台合规 / 付费节奏）。
- 版权清查（与 baseline 小说的差异度逐项核查）。
- 视觉化可行性（每幕能不能拍成 ≤15 s AI 短剧 shot）。

执行阶段（stage 6）产出：
- `my_novel/{slug}/README.md`（中文标题 + 概要）。
- `my_novel/{slug}/world.md`、`characters/`、`outline.md`、`episodes/epNN/{script,shots}.md`（per `agent_refs/project/ai_video.md` 的 novel 子类型约定）。

## 落地不动的旧规则

- `_meta.json.complete == True` 筛选仅对 `downloaded_novels/` 应用（原 follow-up 104 规则的语义保持）。
- 章节级 per-file 拆分（follow-up 111）继续生效，只是路径前缀从 `novels/` 变成 `downloaded_novels/`。
- ttkan/sudugu 双源 fallback、jitter、splitter（follow-up 107/109/111）完全不动。
- `agent_refs/project/ai_video.md` 的 novel 子类型规则不动；只是新增"小说原稿放在 `my_novel/`"这一上游事实。

## 不在本 follow-up 范围内

- 新仙侠小说本身的内容产出 — Phase B 通过 `/agent_team` 独立跑。
- 旧 `novels/` 路径相关的、未被本仓库代码引用的外部 reference（如其他 spec 文档里出现的字面量 `novels/`）— 历史文档不追溯改写，新文档全部使用新路径。
