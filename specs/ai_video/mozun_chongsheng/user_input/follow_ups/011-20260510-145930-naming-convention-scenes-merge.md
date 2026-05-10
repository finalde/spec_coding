# Follow-up draft 011 — 2026-05-10

Summary: 三件事：(A) **合并 scenes/ ref_images 文件**到主 scene 文件 (mirror characters pipeline per follow-up 009)；删除 `scenes/ref_images/` 子目录；每 scene 一个自包含 `.md` 文件含 bible + 场景 reference prompt。(B) **新命名约定**: characters 用 `c{N}_{中文名}.md` (e.g., `c1_沧冥.md`); scenes 用 `s{N}_{shortname}.md` (e.g., `s1_长阶顶.md`)；placeholder 同步：`{ref_c{N}_{中文名}}` / `{ref_s{N}_{shortname}}`。(C) **引用一致性校验**：所有 shot.md 中引用的 character / scene file path + placeholder 必须对应到实际存在的 `c{N}_*.md` / `s{N}_*.md` 文件。

## 用户原话

> under scenes folder similar to charactor, combine ref_images and md files out side, also ake sure each md file contains similar strucutre as charactors, and has a prompt I can copy paste, also in the episode/shotNN.md, you may reference charactors and scenes, make sure whatever is referenced, there is a actual md files under charactors foldre or scene foldres. Actually lets create some convention here, all charactors start with c{number}_{name} like c1_沧溟, and all scene follows s{number}_{name}, we can follow this convention in both md file name as well as reference in the prompt

## (A) Naming convention 锁定

### Characters (10):

| N | 旧 filename | 新 filename | placeholder |
|---|---|---|---|
| 1 | 沧冥-魔尊本相.md | c1_沧冥.md | `{ref_c1_沧冥}` |
| 2 | 叶无尘-乞丐转生.md | c2_叶无尘.md | `{ref_c2_叶无尘}` |
| 3 | 苏璃月-紫霄圣女.md | c3_苏璃月.md | `{ref_c3_苏璃月}` |
| 4 | 柳红袖-红袖招老板娘.md | c4_柳红袖.md | `{ref_c4_柳红袖}` |
| 5 | 苓夭夭-药王谷医师.md | c5_苓夭夭.md | `{ref_c5_苓夭夭}` |
| 6 | 白月清-紫霄宫主.md | c6_白月清.md | `{ref_c6_白月清}` |
| 7 | 赵焚天-玄炎宗主.md | c7_赵焚天.md | `{ref_c7_赵焚天}` |
| 8 | 方鼎元-太清掌教.md | c8_方鼎元.md | `{ref_c8_方鼎元}` |
| 9 | 韩夺心-万剑宗主.md | c9_韩夺心.md | `{ref_c9_韩夺心}` |
| 10 | 司空玄-影神殿主.md | c10_司空玄.md | `{ref_c10_司空玄}` |

排序原则：1-2 主角形态 → 3-5 三女主 → 6-10 五大宗主反派。

### Scenes (6 立档):

| N | 旧 filename | 新 filename | placeholder |
|---|---|---|---|
| 1 | 沧冥魔域-黑金大殿长阶顶.md | s1_长阶顶.md | `{ref_s1_长阶顶}` |
| 2 | 沧冥魔域-黑金大殿内.md | s2_大殿内.md | `{ref_s2_大殿内}` |
| 3 | 玄炎宗-铸器堂.md | s3_铸器堂.md | `{ref_s3_铸器堂}` |
| 4 | 太清门-金殿密室.md | s4_金殿密室.md | `{ref_s4_金殿密室}` |
| 5 | 凡间小镇-破庙墙角.md | s5_破庙.md | `{ref_s5_破庙}` |
| 6 | 雪山冰原.md | s6_雪山.md | `{ref_s6_雪山}` |

排序原则：cross-ep chronological 出现顺序 (ep01 first → ep05 last)。

注意: scenes/ref_images/ 子目录里 6 个 `.md` 文件 (与上方文件 1:1 配对) 在合并后**全部删除**。

### Numbering rule (rule #12.8 NEW)

- Character: `c{N}_{中文名}` — N 从 1 起递增；中文名取角色档 `{中文名}-{身份}` 中的 `{中文名}` 部分（去掉 `{身份}` 后缀）。
- Scene: `s{N}_{shortname}` — N 从 1 起递增；shortname 取场景档 `{location}` 中的核心标识词 (e.g., `黑金大殿长阶顶` → `长阶顶`，`紫霄圣女` → `圣女`)。
- Numbering 一旦分配后**不可重排**（即使新增角色或场景也只能 append `c11_`, `s7_`，不可 renumber existing IDs）。
- N 从 1 开始（不是 0）；不补零（`c10_` 不写 `c010_`）。

## (B) Scene 文件 schema (rule #12.5 v3 类比，per follow-up 011)

合并后 `scenes/s{N}_{shortname}.md` 文件结构与 character file 同构：

````markdown
# {scene-name}

## 场景定位
（per follow-up 003 现有 bible 内容）

## 锁定描述符（8 字段，跨集 byte-identical）
（per follow-up 003 现有内容）

## 关键变化态
（per follow-up 003 现有内容）

## 出现镜头
（per follow-up 003 现有内容；可选更新 ep## shotNN 引用以匹配最新 shot 列表）

## 负向
（per follow-up 003 现有内容）

---

# 场景 reference prompt — Seedream / Midjourney / Imagen / Flux（场景立绘）

> **用法**：复制下方代码块整段，粘贴到 text-to-image 模型 → 输出场景立绘 PNG。该 PNG 可用作：① 后续 shot prompt 的 background reference（上传到 video 模型作 scene reference）；② 视频后期的背景板。

```text
{现有 ref_images/{name}-立绘.md 中 ## Prompt 段及其 8 子段 — 主体/构图、视角、时辰、背景、光源、风格、负向 — flatten 为 inline-labeled 形式 同 follow-up 005 character ref turntable schema 的扁平化方法}
```
````

`scenes/ref_images/` 子目录全部删除 + scene file rename per § (A) 表。

## (C) Shot file 引用更新 (50 文件)

每个 `shotNN.md` 文件需要：

1. **出场角色 table 第 3 列「character file」path 更新**: `characters/{中文名}-{身份}.md` → `characters/c{N}_{中文名}.md` (per § A 映射)。
2. **复用场景 段 / Reference placeholders table 第 3 列「来源」path 更新**: `scenes/{location}.md` → `scenes/s{N}_{shortname}.md` (per § A 映射)。
3. **Reference placeholders table 第 1 列 + 视频 prompt code block 内的 `{ref_xxx}` 占位符**全部 byte-rename:
   - `{ref_<旧char_short>}` → `{ref_c{N}_{中文名}}` (e.g., `{ref_沧冥}` → `{ref_c1_沧冥}`)
   - `{ref_<旧scene_short>}` → `{ref_s{N}_{shortname}}` (e.g., `{ref_长阶顶}` → `{ref_s1_长阶顶}`)

适用 placeholder 全表 byte-replace mapping:

| 旧 | 新 |
|---|---|
| `{ref_沧冥}` | `{ref_c1_沧冥}` |
| `{ref_叶无尘}` | `{ref_c2_叶无尘}` |
| `{ref_苏璃月}` | `{ref_c3_苏璃月}` |
| `{ref_柳红袖}` | `{ref_c4_柳红袖}` |
| `{ref_苓夭夭}` | `{ref_c5_苓夭夭}` |
| `{ref_白月清}` | `{ref_c6_白月清}` |
| `{ref_赵焚天}` | `{ref_c7_赵焚天}` |
| `{ref_方鼎元}` | `{ref_c8_方鼎元}` |
| `{ref_韩夺心}` | `{ref_c9_韩夺心}` |
| `{ref_司空玄}` | `{ref_c10_司空玄}` |
| `{ref_长阶顶}` | `{ref_s1_长阶顶}` |
| `{ref_大殿内}` | `{ref_s2_大殿内}` |
| `{ref_铸器堂}` | `{ref_s3_铸器堂}` |
| `{ref_金殿密室}` | `{ref_s4_金殿密室}` |
| `{ref_破庙}` | `{ref_s5_破庙}` |
| `{ref_雪山}` | `{ref_s6_雪山}` |
| `{ref_山道平台}` (未立档 placeholder, ep02) | `{ref_s7_山道平台}`（追加为 s7 立档 OR 保持 inline 描述 — 建议立档以遵循 cN/sN 一致性，但 follow-up 011 暂留为 placeholder pending 用户确认是否升级立档；如保持，placeholder 仍 carry s7_ 前缀以遵循命名约定） |
| `{ref_云海}` (未立档, ep05) | `{ref_s8_云海}` (相同处理) |
| `{ref_识海}` (未立档, ep05) | `{ref_s9_识海}` (相同处理) |

注：未立档 location placeholder 也接受新命名约定 prefix，方便用户后续立档时 number 已分配，无需 renumber。

## (D) Reference validation contract (NEW)

`stage-6` validator 扩展 schema check (出补丁单 NFR-16):

- 每 shot.md 中所有 `{ref_c{N}_*}` placeholder 必须有对应 `characters/c{N}_*.md` 文件存在。
- 每 shot.md 中所有 `{ref_s{N}_*}` placeholder 必须有对应 `scenes/s{N}_*.md` 文件存在 OR `s{N}_` 前缀已分配但 location 未立档（保留 placeholder ok）。
- Reference placeholders table 的「来源」列 path 必须与实际 character/scene 文件 path byte-identical。
- 出场角色 table 的「character file」列 path 必须与实际 character 文件 path byte-identical。
- 任何 dangling placeholder (引用但无文件) = blocker。

## (E) Rule #12.8 NEW (写入 agent_refs)

`.claude/agent_refs/project/ai_video.md` 新增 rule #12.8「Character/Scene 命名约定 cN_/sN_」：

- Filename pattern: `c{N}_{name}.md` for characters; `s{N}_{name}.md` for scenes
- Placeholder pattern: `{ref_c{N}_{name}}` / `{ref_s{N}_{name}}`
- N: 1-based ascending; preserved across project lifecycle (no renumbering); new entries append.
- Reference validation: stage-6 validator checks all placeholders resolve to actual files.

## 期望行为

1. `characters/` 下文件名形如 `c1_沧冥.md`...`c10_司空玄.md` (10 个文件，无 ref_images/ 子目录).
2. `scenes/` 下文件名形如 `s1_长阶顶.md`...`s6_雪山.md` (6 个文件，无 ref_images/ 子目录).
3. 每 shot.md 中 placeholder 命名形如 `{ref_c1_沧冥}` / `{ref_s1_长阶顶}`，path 引用形如 `characters/c1_沧冥.md` / `scenes/s1_长阶顶.md`.
4. 用户可一眼通过 `c1_` / `s1_` 前缀知道是 character or scene 及其 number；新增 character/scene 时 append `c11_` / `s7_`，不破坏现有引用。
5. follow-up 001-010 锁定全部保持有效。

## Out of scope

- 不立档新场景 (ep02 山道平台 / ep05 云海 + 识海 等仍保留 inline 描述 + placeholder rename; 立档与否独立 follow-up)。
- 不修改 shot file 三段 schema (Shot context + Reference placeholders + 视频 prompt 三段保留)。
- 不修改 character bible / scene bible 内容（除路径引用 + cN_/sN_ filename rename）。
- 不修改 spec_driven webapp。
- 不修改 ep06-ep60 stage-4 regen 范围。
