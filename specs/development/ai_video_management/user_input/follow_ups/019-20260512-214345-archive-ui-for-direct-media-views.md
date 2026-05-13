# Follow-up draft 019 — 2026-05-12

Summary: archive feature 在 character / scene / shot folder 内**只对 markdown reader 可见**的回归 — 用户最自然的工作流是点 sidebar 里的 mp4 文件直接看视频，但此时 Reader 走 `isVideo` 分支只渲染 `<video>`，没有 SiblingMedia → 没有 checkbox、没有 toolbar、没有 Archive Selected。follow-up 008 + 011 的批量归档完全实现但用户看不见。本 follow-up 把 SiblingMedia 渲染范围从「.md only」扩展到「任何 single-file media reader 视图」。

## 用户原话

> for the mp4 file i put under charactors and scenes foders, lets introduce a fuction called archive basically under each charactor, there will be multiple mp4 video reference, I need to select one and move the rest to archive, so I could just select those unwanted ones and then say archive, then it should be moved to a local archive folder under current charactor folder, apply the same to scene, shot, and all ai videos

用户描述的就是 follow-up 008 + 011 已实现的功能契约，但实测看不见 — 经诊断确认是 **render 入口缺失**，非后端 / 逻辑 bug。

## 根因

`projects/ai_video_management/frontend/src/components/Reader.tsx` 的 render-mode dispatch（line 142-178）目前只在 `isMarkdown` 分支底下挂 `<SiblingMedia>`（line 172）。其他分支：

| 分支 | render | SiblingMedia 挂载 |
|---|---|---|
| `isVideo` (mp4/mov/webm/mkv/avi/m4v) | `<video controls>` | ❌ 缺失 |
| `isMediaImage` (png/jpg/jpeg/webp/gif/bmp，非 ImageRefView) | `<img>` | ❌ 缺失 |
| `isImageRef` (`_seedream.md`) | `<ImageRefView>` | ❌ 缺失 |
| `isShotPair` (`shotNN_kling.md` / `shotNN_seedance.md`) | `<ShotPairView>` | ❌ 缺失 |
| `isCasting` (`casting.md`) | `<CastingView>` | ❌ 缺失（但 casting.md 在 drama root，无 ref-video 用例，**out of scope**） |
| `isShotlistTable` (`shotlist.md`) | `<ShotlistTableView>` | ❌ 缺失（drama root，**out of scope**） |
| `isMarkdown` 默认 | `<Renderer>` | ✅ 已有 |

典型 character 文件夹（实测 `ai_videos/mozun_chongsheng/characters/c1_沧冥/` 有 1 个 `.md` + **8 个 `.mp4`**）：用户点任一 mp4 → 看到 video 但没归档 UI；只有点 `c1_沧冥.md` 才会看到 SiblingMedia 的 8 个 sibling 视频 + 批量归档 toolbar。这违背"point and click" 直觉。

## 决策（无 interactive 问题，按用户原文契约推断）

| 问 | 决策 |
|---|---|
| 把 SiblingMedia 挂哪些 reader 分支？ | `isVideo` + `isMediaImage` + `isImageRef` + `isShotPair`。casting.md 和 shotlist.md 在 drama root，**out of scope**（也可挂但当前无用例，保留 v1 留白）。 |
| 挂载位置 | 直接挂在该分支主元素之后，作为 `reader-body` 的兄弟节点。`<SiblingMedia>` 返回 `null` 当 folder 无 sibling media — 零回归。 |
| props 来源 | 跟现 markdown 分支完全一致：`currentPath={path}`、`knownPaths={knownPaths}`、`onChange={onSaved}`。 |
| 行为差异 | 无。`findSiblingMedia` 已排除 `currentPath` 自身 — 用户点 `c1_沧冥1.mp4` 后 SiblingMedia 显示 `c1_沧冥2.mp4` ~ `c1_沧冥8.mp4` + 同 folder 的 png / jpg；他可勾选 1-7 中不要的，点 Archive Selected。这就是用户要的 UX。 |
| 视觉 | `<SiblingMedia>` 默认 grid 已在 light-theme 灰背景下良好；不引入新样式。已有 `🎬 当前视频` ↑ `📁 Folder media · 同 folder 媒体` ↓ 的纵向布局对 video 分支同样适用。 |

## 功能要求

1. **Reader.tsx 修改范围限定 line 142-178 的 `reader-body` JSX**。其他逻辑（fetch、save、conflict、editing）零改动。
2. **四处新增 `<SiblingMedia>`**（每处都用同一份 props）：
   - `isVideo` 分支 `<video>` 之后。
   - `isMediaImage` 分支 `<img>` 之后。
   - `isImageRef` 分支 `<ImageRefView>` 之后。
   - `isShotPair` 分支 `<ShotPairView>` 之后。
3. **`isCasting` / `isShotlistTable` / `isJsonl` / `isCode` / `isTxt` 不挂载** — 它们是 drama-root 级 markdown / 配置文件，所在文件夹无 character/scene/shot mp4 用例。如未来 casting.md 旁需要管理媒体，单独 follow-up。
4. **零后端改动** — `POST /api/archive-media` + `POST /api/unarchive-media` (follow-up 008) 已存在；SiblingMedia 内部循环复用 (follow-up 011)。
5. **零样式新增** — 复用 follow-up 005 + 008 + 011 已有的 `.sibling-media-grid` / `.sibling-media-toolbar` / `.sibling-media-item` 等 CSS。

## 安全 / 边界

- 不引入新 endpoint 调用 — 复用现有 archive / unarchive media handlers，保持 Origin/Host gate、sandbox、symlink 拒绝、原子 rename 等已验证契约。
- 不影响 editing flow — `editing && !isImage && !isVideo` (line 132) 已确保 video / image 不进入 Editor 分支。
- `<SiblingMedia>` 返回 `null` 当 `siblings.length === 0 && archived.length === 0`（SiblingMedia.tsx line 233）— 单文件文件夹（没有兄弟 media）下不会渲染空白 section，无视觉回归。

## 不在本 follow-up 范围

- 不引入 folder-level archive UI（无 file 选中时显示文件夹媒体列表）— 走 Reader 路由 `/file/:path`，路由不变；当前的"点一个 sibling 文件看到批量 UI" 流程已满足用户原话。
- 不挂载到 CastingView / ShotlistTableView / JsonlView / CodeView — 当前无 ref-video 用例。
- 不调整 SiblingMedia 内部 grid 排序 / 分页 / 缩略图大小 — 复用 follow-up 011 实现。
- 不写 frontend Vitest / e2e Playwright（与 follow-up 005 ~ 018 一致，推迟到批量补测）。
- 不重命名 SiblingMedia → `FolderMediaPanel` 等更通用的名字 — 名字仍准确（它确实显示 "siblings"），重命名是 churn。
