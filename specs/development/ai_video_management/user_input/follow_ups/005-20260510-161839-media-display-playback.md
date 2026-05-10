# Follow-up draft 005 — 2026-05-10

Summary: 用户已开始把生成好的视频和图片放进 `ai_videos/{project}/characters/c{N}_*/` / `scenes/s{N}_*/` / `episodes/ep{NN}/prompts/shot{NN}/` 文件夹（per mozun_chongsheng follow-up 014 的 folder-per-asset schema），但 ai_video_management webapp 左侧 nav 只显示 `.md` 文件，**完全不显示 `.mp4` / `.png` / `.webp` 等媒体文件**。需求：(A) 让 webapp 左侧 nav 显示所有 media 文件 (mp4 / mov / webm / png / jpg / jpeg / webp / gif / bmp / etc.); (B) 用户点击 media 文件 → 直接在右侧 Reader 显示图片或播放视频；(C) 通用契约：folder 内任何 media 文件都自动显示，user 不需要 manually wire 每种文件类型。

## 用户原话

> 我把生成好的video和picture放到目录底下，ai_video_management left nav并没有显示出来，帮我在ai_video_management里加上图片和视频浏览的功能，不论我将来往folder里放什么文件，都可以显示播放

## 当前实现 vs 期望

**当前**:
- `exposed_tree.py` 的 `ALLOWED_EXTENSIONS = {.md, .json, .yaml, .yml, .jsonl, .txt, .png, .jpg}` — 只 8 种扩展名 visible in tree。
- 视频 (.mp4/.mov/.webm) + 多种图片 (.jpeg/.webp/.gif/.bmp) NOT in allowed set → tree_walker 跳过它们 → 左侧 nav 不显示。
- `/api/file` 对 .png/.jpg 返回 base64 inline content (1MB 限制)。视频远超 1MB，无法走 /api/file。
- 没有 /api/media route — 不能 serve raw video bytes。

**期望**:
- 左侧 nav 显示文件夹内 **所有** media 文件 (image + video + 未来扩展类型)
- 点击 → 右侧 Reader 直接渲染图片 (`<img>`) 或播放视频 (`<video controls>`)
- 通用：扩展 media 类型时只需 update 单一允许列表

## 实施方案

### (A) Backend changes

#### A1. `projects/ai_video_management/backend/libs/exposed_tree.py`

新增 `MEDIA_EXTENSIONS` set（与 `ALLOWED_EXTENSIONS` 解耦）：

```python
MEDIA_EXTENSIONS: frozenset[str] = frozenset({
    ".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp",     # images
    ".mp4", ".mov", ".webm", ".mkv", ".avi", ".m4v",      # videos
})
```

`ALLOWED_EXTENSIONS` 保持不变 (用于 `/api/file` GET / PUT — text + small images via base64)。

新增 `TREE_VISIBLE_EXTENSIONS = ALLOWED_EXTENSIONS | MEDIA_EXTENSIONS` 用于 tree walker。

#### A2. `projects/ai_video_management/backend/libs/tree_walker.py`

- `_is_allowed_leaf(p)` 改用 `TREE_VISIBLE_EXTENSIONS` (包含 media)。
- `_leaf_for(f)` 扩展 type tagging:
  - `.png/.jpg/.jpeg/.webp/.gif/.bmp` → `type: "image"`
  - `.mp4/.mov/.webm/.mkv/.avi/.m4v` → `type: "video"` (NEW)
  - 其他 ALLOWED → `type: "file"`

#### A3. `projects/ai_video_management/backend/libs/api.py`

新增 `/api/media` endpoint（与 `/api/file` 解耦；不走 base64，不走 MAX_FILE_BYTES）：

```python
@app.get("/api/media")
def get_media(path: str = Query(...)) -> Response:
    resolved = resolver.resolve(path)
    if resolved is None or not resolved.is_file():
        return JSONResponse(status_code=404, content={"detail": {"kind": "not_found"}})
    ext = Path(path).suffix.lower()
    if ext not in MEDIA_EXTENSIONS:
        return JSONResponse(status_code=400, content={"detail": {"kind": "extension_not_allowed"}})
    mime_map = {
        ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".webp": "image/webp", ".gif": "image/gif", ".bmp": "image/bmp",
        ".mp4": "video/mp4", ".mov": "video/quicktime", ".webm": "video/webm",
        ".mkv": "video/x-matroska", ".avi": "video/x-msvideo", ".m4v": "video/mp4",
    }
    return FileResponse(str(resolved), media_type=mime_map.get(ext, "application/octet-stream"))
```

注意：FileResponse 由 FastAPI 处理 streaming + range requests (HTTP 206)，浏览器视频播放需要 range support。

### (B) Frontend changes

#### B1. `projects/ai_video_management/frontend/src/types.ts`

`TreeNodeType` 加 `"video"`：

```ts
export type TreeNodeType = "section" | "directory" | "file" | "image" | "video";
```

#### B2. `projects/ai_video_management/frontend/src/api.ts`

加 `mediaUrl()` helper：

```ts
export function mediaUrl(path: string, mtime?: number): string {
  const cb = mtime !== undefined ? `&mtime=${encodeURIComponent(String(mtime))}` : "";
  return `/api/media?path=${encodeURIComponent(path)}${cb}`;
}
```

#### B3. `projects/ai_video_management/frontend/src/components/Reader.tsx`

- 当 path 扩展名是 video（.mp4/.mov/.webm/.mkv/.avi/.m4v）→ 渲染 `<video controls src={mediaUrl(path)} />`。
- 当 path 扩展名是 image（已支持 .png/.jpg via /api/file base64；扩展 .jpeg/.webp/.gif/.bmp via /api/media）→ 渲染 `<img src={mediaUrl(path)} />`。
- 现有 `isImage` check 扩展为 `isMediaImage` 包含所有 image extensions；新加 `isMediaVideo` check.
- 当 user 当前查看 .md 文件时，scan `knownPaths` 找同 folder 内 sibling media files → 在 markdown 渲染下方渲染 SiblingMedia gallery（image + video grid）。

#### B4. `projects/ai_video_management/frontend/src/components/SiblingMedia.tsx` (NEW)

```tsx
interface SiblingMediaProps {
  currentPath: string;
  knownPaths: string[];
}

export function SiblingMedia({ currentPath, knownPaths }: SiblingMediaProps): JSX.Element | null {
  const siblings = useMemo(() => findSiblingMedia(currentPath, knownPaths), [currentPath, knownPaths]);
  if (siblings.length === 0) return null;
  return (
    <div className="sibling-media-grid">
      <h3>📁 同 folder media</h3>
      {siblings.map(p => {
        const ext = p.slice(p.lastIndexOf(".")).toLowerCase();
        const isVideo = [".mp4", ".mov", ".webm", ".mkv", ".avi", ".m4v"].includes(ext);
        const url = mediaUrl(p);
        const filename = p.split("/").pop() ?? p;
        return (
          <figure key={p} className="sibling-media-item">
            {isVideo ? <video controls src={url} /> : <img src={url} alt={filename} />}
            <figcaption>{filename}</figcaption>
          </figure>
        );
      })}
    </div>
  );
}

function findSiblingMedia(path: string, all: string[]): string[] {
  const lastSlash = path.lastIndexOf("/");
  if (lastSlash < 0) return [];
  const parent = path.slice(0, lastSlash + 1);
  const mediaExt = /\.(mp4|mov|webm|mkv|avi|m4v|png|jpg|jpeg|webp|gif|bmp)$/i;
  return all
    .filter(p => p !== path && p.startsWith(parent) && !p.slice(parent.length).includes("/") && mediaExt.test(p))
    .sort();
}
```

#### B5. `projects/ai_video_management/frontend/src/components/Sidebar.tsx`

Sidebar 已 render TreeNode based on `node.type`. 加 "video" 图标 (e.g., 🎬) 让用户区分 media files。

#### B6. `projects/ai_video_management/frontend/src/styles.css`

```css
.media-view { padding: 16px; text-align: center; }
.media-view img, .media-view video { max-width: 100%; max-height: 80vh; border-radius: 6px; }

.sibling-media-grid { margin-top: 24px; padding-top: 16px; border-top: 1px solid var(--border); }
.sibling-media-grid h3 { font-size: 14px; color: var(--text-muted); margin: 0 0 12px 0; font-weight: 600; }
.sibling-media-grid .sibling-media-item { display: inline-block; margin: 0 12px 12px 0; vertical-align: top; max-width: 320px; }
.sibling-media-grid .sibling-media-item img,
.sibling-media-grid .sibling-media-item video { width: 100%; max-height: 240px; object-fit: contain; border-radius: 4px; background: var(--bg-toolbar); }
.sibling-media-grid .sibling-media-item figcaption { font-size: 11px; color: var(--text-muted); margin-top: 4px; word-break: break-all; }
```

### (C) Test coverage (Out of scope for this follow-up — TBD)

Existing tests in `backend/tests/` cover ALLOWED_EXTENSIONS + sandbox security. After this follow-up, add:
- `test_api_media_route.py`: GET /api/media returns 200 for valid media path within sandbox; 400 for non-media ext; 404 for outside-sandbox path.
- `test_tree_walker_includes_media.py`: tree includes .mp4 / .webm files, tagged as "video"; .webp / .gif as "image".

These can land in independent surgical follow-up; webapp functionality works end-to-end without them.

## 期望行为

1. 用户把 `c1_沧冥/turntable.mp4` 放进 folder → 刷新 webapp → 左侧 nav 内 `c1_沧冥/` folder 下显示 `c1_沧冥.md` + `turntable.mp4` 两个 children.
2. 用户 click `turntable.mp4` → 右侧 Reader 内嵌播放该视频（HTML5 `<video controls>`）。
3. 用户 click `c1_沧冥.md` → 渲染 markdown content + 下方自动 grid display 同 folder 的所有 media files（含播放控件）。
4. 任何未来添加的 media 类型只需 add 到 `MEDIA_EXTENSIONS` 一处即可（前后端单源 truth）。

## Out of scope

- 不修改 mozun_chongsheng (or any specific ai_video project) content.
- 不实现 backend tests (deferred to independent surgical follow-up).
- 不修改 spec_driven webapp.
- 不实现 audio file support (.mp3 / .wav etc.) — 当前需求只关注 image + video; audio 可在 next follow-up 加。
- 不实现 thumbnail generation for videos (浏览器原生 video preview 已足够 for v1).
- 不实现 download button (用户右键 → 另存为 已能下载)。

## Security considerations

- `/api/media` 复用现有 `safe_resolve` sandbox - 路径必在 ai_videos/ 或 research/ 之内。
- `MEDIA_EXTENSIONS` 严格 allowlist (无 .exe / .bat / 等可执行扩展)。
- FastAPI FileResponse 自动设 correct Content-Type + Content-Length，没有 directory traversal 风险（safe_resolve 已防）。
- MAX_FILE_BYTES 不 apply to /api/media (videos can be 100MB+) — 但路径仍在 sandbox 内，无法上传任意文件 (无 PUT /api/media endpoint，只 GET)。
