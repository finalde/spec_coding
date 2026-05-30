# Follow-up draft 111 — 2026-05-24
Summary: 把 `downloaded_novels/{cat}/{slug}/{slug}.md`（3–19 MB 单文件）按章节拆成 `downloaded_novels/{cat}/{slug}/chapters/{NNNN}-{title}.md`（典型 5–80 KB / 章），删除原拼接文件，让前端能通过 `/api/file`（`MAX_FILE_BYTES = 1 MiB`）真正打开每一章。Downloader 同步切换到 per-chapter 写盘；新增一次性 splitter CLI 处理 11 本已下载的小说；`_meta.json.chapters[].file` 记录每章相对文件名。Follow-up 101 第 109 行明确把"分页 / 单文件超 1 MiB 打不开"留作未来 follow-up，本 follow-up 即兑现。

## 用户原话
> under ai_video_management novels, the downloaded novel are too big in one md file, plesae split them into multiple md files so it is easy to view on frontend

## 用户多选裁决
1. 拆分粒度：**每章一个 .md**（granular nav，章级单位即用户阅读单位）。
2. 原拼接 `{slug}.md`：**删除**（不留双份；前端读 chapters/ 目录即可，整书下载场景目前没有 spec 化需求）。
3. 落地范围：**Both — 立即拆分已存在 11 本 + 同步改 writer**，新下载的小说从一开始就是 per-chapter 形态。

## 设计

### 文件夹形态（一次拆分到位 + 未来下载延续）

```
downloaded_novels/
├── _index.md                                     # 现有，writer 重写时保留
└── xianxia/
    └── fanren_xiuxian_zhuan/
        ├── _meta.json                            # 现有；新增 chapters[].file 字段
        └── chapters/
            ├── 0001-第1章 山边小村.md
            ├── 0002-第2章 青牛镇.md
            └── ...
```

旧 `{slug}.md` 在 splitter 跑完后删除。`chapters/` 目录是 splitter 与 writer 共用的唯一落盘位置，无双份。

### 文件命名规则

- `{NNNN}-{sanitized_title}.md`
  - `NNNN` = 4 位零填充章节 idx（`fanren_xiuxian_zhuan` 现有 ~2400 章，4 位足够；超过 9999 章再考虑 5 位 — 现已下载的最大 fanren 也未到 3000）。
  - `sanitized_title` = `chapter.title` 经过 `_safe_filename_segment()` 净化：去除 Windows 禁用字符 `<>:"/\|?*`、控制字符、首尾空白与 `.`；保留中文 / 全角空格 / 中文标点；上限 80 字符（章节标题极少超过该长度，超出截尾不会影响 `_meta.json` 中的 `title` 显示）。
- 文件正文：`# {chapter.title}\n\n{body}\n`（H1 仍为完整标题，便于在 Reader 视图内一目了然）。
- 文件名沿用 follow-up 004 中文文件名豁免 — 前端 Sidebar `Reader` 已经能正确显示中文 / `/api/file` URL-decode 自动处理。

### `_meta.json` 形态

`ChapterRecord` 新增可空字段：

```python
@dataclass
class ChapterRecord:
    idx: int
    title: str
    url: str
    done: bool = False
    hash: str | None = None
    error: str | None = None
    file: str | None = None     # NEW — chapters/<file> 相对路径；None = 未下载 / 旧 schema
```

`done == True` 但 `file is None` 即表示 splitter 还没跑（兼容旧元数据）。Splitter 跑完后所有 done 章节都填上 `file`。Writer 写章节时同步赋值。`to_json` / `from_json` 序列化对应字段，旧文件读不到字段时返回 `None`（向后兼容，splitter 会一次性回填）。

### Writer 改造（`libs/infrastructure/writers/novel__writer.py`）

`_ensure_index` / `_download_one_chapter` 不再 append 到 `{slug}.md`：

1. `_ensure_index` 不再写 `body_path` 的 header；改为 `mkdir -p chapters/` 与可选 `_index_header.md`（per-novel header — 标题 / 作者 / 来源）放在小说根 README 形态：`downloaded_novels/{cat}/{slug}/README.md`（不在 chapters/ 里，避免被 sidebar 当成第 0 章）。
2. `_NovelState.body_path` 删除；改为 `chapters_dir: Path`。
3. `_download_one_chapter` 写 `chapters_dir / _build_chapter_filename(chapter)`，正文是 `f"# {chapter.title}\n\n{body_text}\n"`，并把相对文件名写回 `chapter.file` + `_write_meta`。
4. Resumable 语义不变：`chapter.done == True` 即 skip；只是判定的物理证据从"`.md` append 偏移"变成"`chapters/{file}` 文件存在"。
5. Idempotency：写文件前若 `chapters_dir / file` 已存在则覆写（避免重复 download 导致脏文件）；`_write_meta` 仍是 tmp+rename 原子写。

### Splitter CLI（`apps/cli/novel_split.py` — 新增）

一次性脚本，对 `downloaded_novels/**/*/{slug}.md` 全量处理：

```
python -m apps.cli.novel_split                # 全部小说
python -m apps.cli.novel_split <slug>         # 单本
python -m apps.cli.novel_split --dry-run      # 只打印不写盘
```

流程：
1. 读取 `_meta.json` 拿 `chapters[]`。
2. 读取 `{slug}.md`，正则切分 `^## (?P<title>.*?)$` 与下一个 `^## ` 之间的 body。
3. 把切好的 body 依 `chapter.idx` 顺序写入 `chapters/{NNNN}-{sanitized}.md`（H1 用 `# {title}`）。
4. `chapter.file` 字段回填到 `_meta.json`；`chapter.done` 保持原状不动。
5. 写 `README.md`（包含小说标题 / 作者 / 来源），删除原 `{slug}.md`。
6. 若切分后的章节数与 meta 章节数不一致，打印 WARN 并不删除原文件（safety net — 用户人工 review）。

Splitter 与 writer 共用 `_safe_filename_segment` / `_build_chapter_filename` helper（提到模块顶层；如果 writer 不希望 import CLI 模块，把 helper 提到 `libs/common/` 反而更干净 — 但为了最小变更，保留在 writer 模块，splitter `from ... import` 复用）。

### Tree reader（`libs/infrastructure/readers/tree__reader.py`）

`_novels_section` 现在的 `_walk_filtered(novel_dir, self._is_allowed_leaf)` 会自动递归到 `chapters/` 子目录并把每章 `.md` 当 leaf 渲染。**不需要代码改动**。Sidebar `expanded[novel_dir]` 默认收起（follow-up 101），用户点开后看到 README + _meta.json + chapters/ 三个子条目；展开 chapters/ 才看到逐章文件。

### Tests / 回归

- 既有 `tests/test_tree_walker_consumer_walk.py` 对 novels section 有 assertion — 现仍能正常walk（添加新嵌套层级不会破坏 walker）。
- 不新增专用测试（最小变更原则；splitter 是一次性运维脚本，writer 行为通过 splitter 输出可用即间接验证）。

### Out of scope

- 章节 "上一章 / 下一章" navigation UI（前端独立 follow-up；splitter 输出本身已含 `_meta.json.chapters[].file` 顺序）。
- 小说级 search / 关键字跳转（v1 仍靠浏览器 Ctrl+F 章内搜）。
- 拆分粒度切换（per-chapter 已是用户挑选粒度）。
- 把 helper 提到 `libs/common/`（保留 writer 内私有，splitter import 即可；后续若有第三方使用者再升格）。

## Touch list

- **NEW**: `projects/ai_video_management/apps/cli/novel_split.py`
- **Modified**: `projects/ai_video_management/libs/infrastructure/writers/novel__writer.py` — `ChapterRecord.file` 新字段；`_NovelState.chapters_dir` 替代 `body_path`；`_ensure_index` 写 README + mkdir chapters/；`_download_one_chapter` 写 per-chapter；新增 `_safe_filename_segment` + `_build_chapter_filename` helper。
- **No-change verified**: `libs/infrastructure/readers/tree__reader.py`（`_walk_filtered` 已能递归 chapters/）；`libs/common/exposed_tree.py`（`MAX_FILE_BYTES` 不变，per-chapter 文件远小于 1 MiB）；`apps/api/routes/novel__route.py`（GET /api/novels 仍按 _meta.json complete 字段聚合）。
- **Runtime**: 跑 `python -m apps.cli.novel_split` 处理已下载的 11 本小说。
- **Audit**: `specs/development/ai_video_management/user_input/revised_prompt.md` header bump（111）；`specs/development/ai_video_management/changelog.md` 追加条目。
