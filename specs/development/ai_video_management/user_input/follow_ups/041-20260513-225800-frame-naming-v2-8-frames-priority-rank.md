# Follow-up draft 041 — 2026-05-13

Summary: 重做场景视频抽帧的命名 + 帧数 + 排序约定。**5 帧 → 8 帧；扁平 `_f{N}_{role}` → 描述性 `_r{rank}_{role}_{shot_size}`；rank 1-8 = "如果只能上传 N 张参考图先选谁" 的优先级**。同时把 `frames/` 加进 `MediaRenamer` 的 excluded 集，否则用户跑 drama-level rename 时 8 个精心命名的 PNG 会被改成 `frames1.png ~ frames8.png`（这是当前实测 bug —— s1_长阶顶/frames/ 里现在就是 `frames1..frames5.png`，user 完全看不出谁是 hero 谁是 detail）。

## 用户原话

> in ai video management, for the frames folder generated under a scene folder, I need better naming convention for the frame files, you should tell me things like if is hero wide or reverse wide, and there should be a fixed 8 pictures frames generated? per your strategy from the video or whatever number you think is the best. Also please rank the pictures with order, in case I can only upload 3 as reference, I know which one to upload.

## 帧数 = 8 的理由

15s walk-through reference video（rule #12.10 v3）由 **5 个 canonical dwell** (每个 ≥0.8s 静止锁机位 = 锐利非 blur) + **4 段 transition** (motion = 偶发 blur) 构成。8 帧 = 5 个 dwell anchor + 3 个战略 transition 中间帧，覆盖正交角度空隙（side / threequarter / mediumclose 三个 dwell 没有的角度档）。10 帧会加入冗余（front-quarter, back-quarter），diminishing return；6 帧需要砍掉 vert/aerial 或 detail，丢失关键信息。**5 帧 → 8 帧的 marginal cost 极低**（ffmpeg seek 慢一帧 ~100ms，总耗时 1-3s → 2-5s，user 无感知）；**marginal value 高**（多出 side / threequarter / mediumclose 三个角度直接对应实际 shot 拍摄的常见构图）。

## 8 帧 schema（按 rank 优先级，timestamp 由 walk-through 路径决定）

| rank | timestamp | role | shot_size | focal | 抽帧理由 |
|------|-----------|------|-----------|-------|----------|
| **r1** | 11.4s | mid | medium | 35mm | dwell #4。最常用 shot focal。**只能上传 1 张时首选**。 |
| **r2** | 0.5s | hero | wide | 24mm | dwell #1。正面建场。**第二张 = 上下文范围**。 |
| **r3** | 14.6s | detail | telephoto | 85mm | dwell #5。材质纹理。**第三张 = 特写细节**。 |
| **r4** | 4.4s | reverse | wide | 28mm | dwell #2。背向 / 反向 shot 用。 |
| **r5** | 7.9s | vert | wide | 28mm | dwell #3。高位俯瞰 OR 低位仰望（per scene file 的 `镜头:` 字段，本规则不区分，role 名通用为 `vert`）。 |
| **r6** | 2.5s | side | wide | 26mm | transition (between hero→reverse 中点)。90° 正交侧面，给 hero/reverse 两个 wide 找不到的中间角度信息。 |
| **r7** | 10.0s | threequarter | oblique | 32mm | transition (between vert→mid 中点)。3/4 oblique 角度，bridging 高位/低位与中景。 |
| **r8** | 13.0s | mediumclose | medium | 50mm | transition (between mid→detail 中点)。50mm 中近焦，bridge mid 与 detail 的焦段空隙。 |

**Rank 1-3 设计意图**：覆盖三档不同焦段（medium / wide / telephoto）+ 三个不同视角（正面中景 / 正面全景 / 正面特写）。如果只上传 3 张，shot prompt 拿到的是"中景默认 + 大全景上下文 + 材质特写"三个 most-distinct 参考。这比"hero + reverse + vert 三个 wide"（全部 wide，焦段单一）信息密度高得多。

**Rank 4-5 是次轴补强**（背向 / 高低）；**rank 6-8 是 transition 帧填空**（侧面 / 3/4 / 中近）。User 可以视具体 shot 需求挑选 — 比如某 shot 要拍角色站在场景中部往上看，那 r5 (vert) 比 r4 (reverse) 更重要，但 r1 (mid) 仍然第一选。

## 命名约定 v2

```
{scene_folder}_r{rank}_{role}_{shot_size}.png
```

例（场景 `s1_长阶顶`，scene folder name = parent dir name）：

```
frames/
├── s1_长阶顶_r1_mid_medium.png
├── s1_长阶顶_r2_hero_wide.png
├── s1_长阶顶_r3_detail_telephoto.png
├── s1_长阶顶_r4_reverse_wide.png
├── s1_长阶顶_r5_vert_wide.png
├── s1_长阶顶_r6_side_wide.png
├── s1_长阶顶_r7_threequarter_oblique.png
└── s1_长阶顶_r8_mediumclose_medium.png
```

**关键属性**：

1. **Rank 前置 → 字典序 = 优先级**。`ls frames/` 自动按 r1→r8 排序，user 一眼看到先选谁。
2. **Role + shot_size 双标签**。role 是语义角色（hero / detail / threequarter），shot_size 是光学档（wide / medium / telephoto / oblique）。两者一起回答 "这张图能用在什么 shot"。
3. **保留 scene folder 前缀**（follow-up 035 amendment 已确立的规则）。任何 mp4 take 在同 scene folder 抽帧都覆盖同一组 8 个 PNG。

## v1 → v2 迁移与 idempotent 覆盖

旧的 5 帧 `_f{N}_{role}.png` 文件 + 任何被 `MediaRenamer` 改名的 `framesN.png` 残留，在新 extract 之前 sweep 清掉：在 `FrameExtractor.extract()` 开头，对 `frames/` 子目录里的 **所有 `*.png` 文件**做一次 `unlink()`（不递归，只清 frames/ 顶层）。

为什么 sweep 整个目录而非只清 v1 pattern：`frames/` 在本契约里专属于 frame extraction 输出，不会有其它来源的 PNG 进来。Sweep 整个目录 = 彻底 idempotent，零残留风险（包括将来万一再改 schema v3 时）。

## `MediaRenamer` 排除 `frames/`

**当前 bug 实测**：`ai_videos/mozun_chongsheng/scenes/s1_长阶顶/frames/` 现状是 `frames1.png` ~ `frames5.png`（不是预期的 `s1_长阶顶_f1_hero.png`）。原因 — follow-up 035 抽帧后，user 又点了 drama-level "重命名 media"（FR-9b），`MediaRenamer` 把 `frames/` 子目录里所有文件按 follow-up 007 规则改成 `{parent-folder-name}{N}.{ext}` = `frames{N}.png`。精心命名的 role 信息 100% 丢失。

**修复**：两条 `MediaRenamer.rename_drama(...)` 的 caller 都加入 `"frames"` 排除：
- `backend/libs/api.py` line 277 的 `POST /api/rename-media` handler — 新加 `excluded_folder_names=frozenset({"frames"})`（之前不传参，等价于空集）。
- `backend/libs/downloads_importer.py` line 120 的 `import-from-downloads` 之后的链式 rename — 已传 `frozenset({NOT_MATCHED_DIR_NAME})`，本改动扩展为 `frozenset({NOT_MATCHED_DIR_NAME, "frames"})`。

—— 与 follow-up 009 的 `not_matched` 排除同一机制。Rename 工作流今后两条路径都跳过 frames/ 子目录，frame extraction 的命名约定得以持久化。

注：`MediaRenamer.rename_drama` 已有 `excluded_folder_names` 参数（follow-up 009 引入），本改动只是补 caller-side 的集合传递，零 libs API 变更。

## API 响应 schema 扩展

`ExtractFramesResult.frames[*]` 现有字段 `{timestamp, role, path}` 之外新增：
- `rank: int` (1-8)
- `shot_size: str` (`wide` / `medium` / `mediumclose` / `telephoto` / `oblique`)

Frontend `api.ts::ExtractedFrame` interface 同步加这两字段（保持 optional 兼容性 — 但 backend 一定填，前端不需要 `?`）。

## 影响范围

- `projects/ai_video_management/backend/libs/frame_extractor.py` —
  - `CANONICAL_FRAMES` 改 tuple shape 为 `(timestamp, role, shot_size, rank)`，元素从 5 个扩到 8 个，按 timestamp 升序排（顺序 = ffmpeg seek 顺序，非 rank 顺序）。
  - `FrameResult` dataclass 新增 `rank: int` 与 `shot_size: str` 字段；`to_payload()` 同步暴露。
  - `extract()` 开头加 sweep 步骤：`frames/` 目录里所有 `*.png` 先 `unlink()`。
  - Filename 模板从 `{prefix}_f{idx}_{role}.png` 改为 `{prefix}_r{rank}_{role}_{shot_size}.png`。
  - 模块顶部 docstring 同步重写（8 帧 + rank + shot_size + sweep 语义 + idempotent 覆盖）。
- `projects/ai_video_management/backend/libs/api.py` — `media_renamer.rename_drama(body.path)` 调用加 `excluded_folder_names=frozenset({"frames"})`。
- `projects/ai_video_management/backend/libs/downloads_importer.py` — 末尾的 `self._renamer.rename_drama(...)` 调用，`excluded_folder_names` 从 `frozenset({NOT_MATCHED_DIR_NAME})` 扩到 `frozenset({NOT_MATCHED_DIR_NAME, "frames"})`。
- `projects/ai_video_management/frontend/src/api.ts` — `ExtractedFrame` interface 加 `rank: number` 与 `shot_size: string`。
- `specs/development/ai_video_management/user_input/revised_prompt.md` — 文件列表追加 041 + header bump。
- `specs/development/ai_video_management/final_specs/spec.md` — 在 FR-9j 与 FR-9i 之间插入 **FR-9r** 新条目（场景视频抽帧端点契约 v2：8 帧 + rank + shot_size + sweep + frames/ 排除于 rename）。
- `specs/development/ai_video_management/changelog.md` — append follow-up 041 条目。

## 不影响

- `POST /api/extract-frames` 端点路由 / 请求 body shape / HTTP status code 全部不变。
- Frontend SiblingMedia / Reader 的抽帧按钮交互不变（toast 文案保留 generic "Extracted N frames"，N 现在永远是 8 + failures 数）。
- 其它 mp4 / 图像处理路径不变（archive / unarchive / delete / hard-delete / import-from-downloads 全部正交）。
- Scene reference video 生成本身（rule #12.10 v3 的 15s walk-through schema）不变 —— 本 follow-up 只动 webapp 侧的 post-render 抽帧实现，不影响 prompt 输出。
- `_actors/` 路径下任何视频 / 图像不受影响（actor 没有 frame extraction 工作流）。
- 现有测试 — backend 无 `frame_extractor` 测试（只有 boot smoke）；frontend 无该模块测试。不新增测试。
- agent_refs/project/ai_video.md rule #12.10-C 的"中间帧 buffet"段说"user 后续若 shot 需要某个 3/4 偏移角度作为额外参考，可在 source mp4 上手动 ffmpeg 抽取" —— 现在那段建议被 webapp 一键 8-frame 抽帧 + 描述性命名取代，但 rule 文本本身不动（保留作为"用户也可以手动覆盖"的退路）。
- Follow-up 039 的 `apps/+libs/` layout 改造尚未应用到 code；当迁移时 `frame_extractor.py` 与 `media_renamer.py` 会随之搬到 `libs/infrastructure/` 或 `libs/application/`，本 follow-up 的语义随之搬走，行为不变。
