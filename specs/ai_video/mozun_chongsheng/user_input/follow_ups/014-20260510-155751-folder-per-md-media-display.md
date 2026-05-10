# Follow-up draft 014 — 2026-05-10

Summary: 三件事：(A) **每个 character / scene / shot .md 文件转为同名文件夹**，原 .md 移入文件夹内；user 后续生成的 mp4 / png 等媒体资产也放入该文件夹（与 prompt 同 location，便于关联）。(B) **ai_video_management webapp 升级**：直接显示 .png/.jpg/.webp 图片 + 播放 .mp4/.mov 视频（与 .md 一同渲染）。(C) **媒体文件 gitignore**：`ai_videos/**/*.{mp4,mov,webm,png,jpg,jpeg,webp,gif}` 不入 git；prompt .md 入 git。

## 用户原话

> 请把现有的charactor, scene, shotNN md 文件都放进一个同名的folder，然后里面放原有的md 文件。之后我生成好视频和图片以后也会放到里面，在ai_video_management里，可以直接显示和播放这些图片或video。但是帮我把图片和视频gitignore掉。

## 工作流变更

**Before（follow-up 013）**：

```
ai_videos/mozun_chongsheng/
├── characters/
│   ├── c1_沧冥.md
│   ├── c2_叶无尘.md
│   ...
├── scenes/
│   ├── s1_长阶顶.md
│   ├── s2_大殿内.md
│   ...
├── episodes/ep01/prompts/
│   ├── shot01.md
│   ├── shot02.md
│   ...
```

**After（follow-up 014）**：

```
ai_videos/mozun_chongsheng/
├── characters/
│   ├── c1_沧冥/
│   │   ├── c1_沧冥.md      # prompt 文件
│   │   ├── turntable.mp4    # (gitignored) user 生成的 turntable 视频
│   │   ├── ref.png          # (gitignored) Seedream 立绘 PNG
│   ├── c2_叶无尘/
│   │   ├── c2_叶无尘.md
│   ...
├── scenes/
│   ├── s1_长阶顶/
│   │   ├── s1_长阶顶.md
│   │   ├── ref.png          # (gitignored)
│   ...
├── episodes/ep01/prompts/
│   ├── shot01/
│   │   ├── shot01.md
│   │   ├── shot01_kling.mp4   # (gitignored) Kling 渲染输出
│   │   ├── shot01_seedance.mp4 # (gitignored) Seedance 输出
│   │   ├── shot01_thumbnail.png # (gitignored) 缩略图
│   ├── shot02/
│   │   ├── shot02.md
│   ...
```

每个 .md 文件 → 同名文件夹，文件夹内含 .md + (后续) 媒体资产。

## (A) 文件 / 文件夹 重组 — 16 chars+scenes + 50 shots = 66 mv ops

### Characters (10):
- `characters/c1_沧冥.md` → `characters/c1_沧冥/c1_沧冥.md`
- ... (10 总)

### Scenes (6):
- `scenes/s1_长阶顶.md` → `scenes/s1_长阶顶/s1_长阶顶.md`
- ... (6 总)

### Shots (50, ep01-ep05 × 10 each):
- `episodes/ep01/prompts/shot01.md` → `episodes/ep01/prompts/shot01/shot01.md`
- ... (50 总)

## (B) Path 引用更新（shot files 内引用 character / scene path）

post-014, shot files 内引用 character / scene path 需更新：

| OLD path | NEW path |
|---|---|
| `characters/c1_沧冥.md` | `characters/c1_沧冥/c1_沧冥.md` |
| `characters/c2_叶无尘.md` | `characters/c2_叶无尘/c2_叶无尘.md` |
| ... | ... (10 总) |
| `scenes/s1_长阶顶.md` | `scenes/s1_长阶顶/s1_长阶顶.md` |
| ... | ... (6 总) |

适用于 50 shot files 内的 出场角色 table + Reference placeholders source column。

## (C) Webapp 升级 — 媒体文件渲染

修改 `projects/ai_video_management/frontend/src/`:

1. **`api.ts`**: 现有 file API 已能 list 任意文件；media files (png/jpg/mp4) 也可由 backend serve（目前 backend 应已能 serve raw bytes for any path under `ai_videos/`；如未 implement，需 backend 加 `/api/media?path=...` 路由 return raw bytes with correct MIME type）。
2. **`components/Reader.tsx`** 或新组件：当 user 选中 character / scene / shot folder（vs 选中 .md 文件）时：
   - 显示该 folder 下所有 .md 文件渲染（默认显示 same-name .md, 即 c1_沧冥/c1_沧冥.md）。
   - 列出该 folder 下所有 media files：
     - .png/.jpg/.webp → `<img>` inline display
     - .mp4/.mov/.webm → `<video controls>` HTML5 player
   - Media files 按文件名排序展示。
3. **`components/Sidebar.tsx`**: tree view 显示 folder + 内容；user click folder → load folder view (md + media) 而非单文件 view。

## (D) gitignore — 媒体文件

修改 root `.gitignore`:

```
# Media files generated under ai_videos/ — heavy binaries, do not commit
ai_videos/**/*.mp4
ai_videos/**/*.mov
ai_videos/**/*.webm
ai_videos/**/*.png
ai_videos/**/*.jpg
ai_videos/**/*.jpeg
ai_videos/**/*.webp
ai_videos/**/*.gif
```

prompt .md / shotlist.md / episode.md / etc. 仍入 git。

## (E) Rule #12.5 v4 / #12.6 v3 / #12.8 v2 amend

`.claude/agent_refs/project/ai_video.md`:
- **Rule #12.5 v4** (character file schema)：character 现存于 `characters/c{N}_{name}/c{N}_{name}.md` (folder of same name)；该 folder 内可含 user 生成的 turntable.mp4 + ref.png 等 media 资产 (gitignored).
- **Rule #12.6 v3** (shot file schema)：shot 现存于 `episodes/ep{NN}/prompts/shot{NN}/shot{NN}.md`；该 folder 内可含 user 生成的 shot rendered videos / thumbnails (gitignored).
- **Rule #12.8 v2** (naming convention)：folder name 与 .md filename 一致（`c1_沧冥/` 含 `c1_沧冥.md`）。Path references 形如 `characters/c1_沧冥/c1_沧冥.md` (full path including folder).
- **新增 rule #12.9 (NEW)**「Media asset gitignore + webapp display 契约」：character / scene / shot folder 内的 media files (mp4/mov/png/jpg/webp/gif) 不入 git；webapp 渲染 folder 时 inline 显示 media。

## (F) Spec FR amends

`specs/ai_video/mozun_chongsheng/final_specs/spec.md`:
- FR-5 / FR-6 / FR-9 amend：character / scene / shot path 形如 `{type}/{N}_{name}/{N}_{name}.md` (folder + same-name md)。
- 新增 NFR-18 (NEW)「Media gitignore」：ai_videos/ 下所有 binary media file 不入 git。

## 期望行为

1. ai_videos/mozun_chongsheng/ 目录树变成 folder-per-asset 形式：每个 character / scene / shot 是一个 folder.
2. user 在 webapp 打开任一 folder → 看到该 folder 内 md prompt 渲染 + 任何已生成的 media files (图片直接显示，视频可播放).
3. git 仓库 size 不会因为 media files 膨胀 (通过 .gitignore).
4. follow-up 001-013 锁定 全部保持有效；本 follow-up 仅 file system 重组 + webapp UI 增强 + gitignore.

## Out of scope

- 不实际渲染 / 上传 media files (user 自行做).
- 不修改 character / scene / shot prompt content (仅 file path/folder rename + path 引用更新).
- 不修改 ep06-ep60 stage-4 regen 范围.
- 不修改 spec_driven webapp.
