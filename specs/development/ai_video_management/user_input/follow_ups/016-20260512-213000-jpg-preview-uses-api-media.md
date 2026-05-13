# Follow-up draft 016 — 2026-05-12

修 follow-up 014 / 015 之后用户报告的另一个 UX bug：点击 `ai_videos/_actors/actor_NNNN/actor_NNNN.jpg` 文件，Reader 不显示图片预览，而是一大段 base64 字符串。

## 用户原话

> when I select a jpg under actors, it is now display or preview properly on the UI

## 根因

**两件事的交叉**：

1. `backend/libs/file_reader.py:72-74` 对图片扩展名（`.png`/`.jpg`）走 base64 encode 路径返回 JSON：
   ```python
   if ext in _IMAGE_EXTENSIONS:
       content = base64.b64encode(raw).decode("ascii")
       encoding = "base64"
   ```
   所以 `GET /api/file?path=*.jpg` 的响应是 `{path, content: "<base64>", encoding: "base64", ...}`，不是图片字节。

2. `frontend/src/components/Reader.tsx:43` 的 dispatch 把 `.jpg`/`.png` **显式排除**在 media-only 之外：
   ```tsx
   const isMediaOnly = isMediaVideo || (isMediaImage && ext !== ".png" && ext !== ".jpg");
   ```
   理由（推测）：follow-up 005 加 `/api/media` 时，意图保留 `.png`/`.jpg` 走老的 `/api/file` 路径（FR-61 写 `<img src="/api/file?path=...">`），但 `/api/file` 返回的是 JSON 不是图片字节 —— 那个 `<img>` src 永远 broken。其他扩展（`.webp`/`.gif`/`.bmp`/视频）走 `/api/media` 路径直接渲染 raw bytes，正常。

3. 渲染分支：
   ```tsx
   isVideo ? <video ...> :
   isMediaImage && ext !== ".png" && ext !== ".jpg" ? <img src={mediaUrl(path)} ...> :
   isCasting ? ... :
   isImageRef ? <ImageRefView/> :  // 但 isImageRef 要求 isMarkdown，对 .jpg 永 false
   ...
   isMarkdown ? <Renderer/> :     // .jpg 不是 markdown
   isTxt ? <pre>... :              // 不是 .txt
   <pre className="text-view">{file.content}</pre>   // ← 兜底渲染 base64 文本
   ```
   `.jpg`/`.png` 全部 fall through 到最末尾的 `<pre>{file.content}</pre>` —— 渲染 base64 字符串。

follow-up 014 引入 actor pool（`ai_videos/_actors/*/*.jpg`）后，用户首次大规模点 `.jpg` 文件 → 触发这个潜在了 5+ follow-up 的 bug。

## 修复

**改 Reader 的 dispatch，让 `.png`/`.jpg` 也走 `/api/media`**，与其他 image / video 扩展一致；同时改 ImageRefView 的 `<img src>` 用 `mediaUrl()` 取代 `imageUrl()`（同根因 —— 但当前仓库无 `_seedream.png` 资产被加载过，所以这个分支的 broken 之前没暴露）：

1. `Reader.tsx:43` `isMediaOnly = isMediaVideo || isMediaImage`（去掉 `.png`/`.jpg` 排除），所有图片扩展统一不走 `/api/file` fetch。
2. `Reader.tsx` 渲染分支：把 `isMediaImage && ext !== ".png" && ext !== ".jpg"` 简化为 `isMediaImage`，并把 `.png`/`.jpg` 也通过 `<img src={mediaUrl(path)}>` 渲染。
3. `ImageRefView.tsx:55, 86-87` 把 `imageUrl()` 改 `mediaUrl()`。mtime 仍由 `companionImage.mtime` 提供（mediaUrl 第二参可选）。
4. `imageUrl` helper 保留 在 `api.ts`（公共 API，可能有外部调用方；本 follow-up 不删除）—— 仅业务代码改路由。

`/api/media` 端点的 sandbox 限制（`exposed.is_inside` + `resolver.resolve`）与 `/api/file` 等价（见 `api.py:178`），所以这个改动不弱化安全。

## 不在本 follow-up 范围

- 不删 `imageUrl` helper（保留兼容；可后续 follow-up 清理）
- 不动 `/api/file` 对 `.png`/`.jpg` 的 base64 行为（其他调用方 e.g. 测试 / 直接 download 可能仍依赖；本 follow-up 只改前端 render 路由）
- 不动 FR-61（spec 文字写 `/api/file`，与实际现状不符 —— 是 specs 的历史陈述，不阻碍 fix）
- 不写 backend pytest / e2e（与 005-015 一致推迟）
