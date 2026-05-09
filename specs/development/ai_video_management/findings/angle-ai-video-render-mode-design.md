# Findings — angle: ai-video-render-mode-design

Researcher: 02
Run: ai_video_management-20260505-002710
Goal: Lock concrete React component design patterns for the 3 new view modes (ShotPairView, ShotlistTableView, ImageRefView) — split-pane layouts, table libraries (or hand-rolled), image preview UX, CJK markdown rendering — so stage 4 names specific patterns and stage 6 doesn't research at implementation time.

## 1. What this angle covers

Six load-bearing UI decisions that the spec must lock before stage 6 starts coding:

1. **Split-pane layout** for the two two-pane views (ShotPairView, ImageRefView) — pick a library or commit to hand-rolled CSS.
2. **ShotlistTableView**: render `shotlist.md`'s GFM table so the `镜次` cell becomes a clickable affordance that opens the matching ShotPairView.
3. **ImageRefView**: how the companion `main_seedream.png` is fetched and rendered through the EXPOSED_TREE sandbox + extension allowlist.
4. **"锁定块" pill** detection on the locked-descriptor block that appears byte-identically inside every shot prompt.
5. **CJK rendering** in markdown views — `lang` attribute, `word-break` defaults, font stack interaction.
6. **Copy-to-clipboard** affordance per pane with accessible "已复制" feedback.

This angle deliberately stops at component-pattern level. Backend security (Origin gate, sandbox, traversal hardening) is angle 01's territory; this angle assumes those exist and consumes the file-read endpoint as-is.

## 2. Pattern recommendations

### 2.1 Split-pane layout — `react-resizable-panels` (single library, both views)

**Recommendation:** Adopt `react-resizable-panels` v4 for both `ShotPairView` and `ImageRefView`. Do NOT hand-roll.

**Rationale:**
- The library is the de-facto standard in the React ecosystem in 2026 — shadcn/ui ships its `Resizable` component as a thin wrapper over it ([shadcn/ui Resizable docs](https://ui.shadcn.com/docs/components/resizable)), and it is on v4.10.0 with active maintenance and ~1,956 dependent packages on npm ([npm package page](https://www.npmjs.com/package/react-resizable-panels)).
- It ships full **WAI-ARIA `role="separator"` + keyboard navigation** out of the box — a hand-rolled flexbox splitter would have to re-implement arrow-key resize, focus indicators, `aria-valuenow/min/max` semantics, and touch-target sizing ([bvaughn/react-resizable-panels README](https://github.com/bvaughn/react-resizable-panels)). The webapp's audience is a single user on desktop, but the accessibility primitives also drive the keyboard-only flow that lets us write deterministic Playwright tests.
- A "150 lines, no dependencies" hand-roll is technically feasible ([Theodo blog: Resizable Split Panels in React](https://blog.theodo.com/2020/11/react-resizeable-split-panels/)), but every implementation in the wild punts on persistence, double-binding, ResizeObserver edge cases on first paint, and percentage vs. pixel constraints. The library swallows those for a small bundle cost.
- Bundle cost is bounded — the library is lightweight enough that shadcn/ui adopts it without a code-splitting carve-out. We do not need a precise byte count to make this call; the alternative is hand-rolled code we'd have to test ourselves.

**Concrete usage:** wrap each view's two halves in `<PanelGroup direction="horizontal">` with `<Panel defaultSize={50}>` + `<PanelResizeHandle />` between them. Persist split position to `localStorage` under `ai_video_management.split_pos.v1` (per-view key) so the user's preferred ratio survives reload.

**Why not hand-roll:** the only cost saved is a single `npm install`. The cost incurred is reimplementing keyboard accessibility correctly. This is exactly the asymmetry the library exists to resolve.

### 2.2 ShotlistTableView — `react-markdown` + `remark-gfm` + `components.td` override + `useNavigate`

**Recommendation:** Render `shotlist.md` with the standard `react-markdown` + `remark-gfm` pipeline. Override the `td` (or `a`) component to detect rows whose first cell matches `/^\s*shot(\d{2})\s*$/` (with or without surrounding backticks) and replace the cell content with a `<button>` that calls `useNavigate()` to open `?file=ai_videos/{name}/prompts/shot{NN}_kling.md&view=shot-pair`.

**Rationale:**
- `react-markdown`'s `components` prop is the documented extension surface for swapping any HTML-tag-equivalent renderer ([react-markdown README](https://github.com/remarkjs/react-markdown)). With `remark-gfm`, the `td` slot is exposed precisely so callers can specialise table cells without forking the parser ([remark-gfm package page](https://github.com/remarkjs/remark-gfm)).
- Detecting the shot reference at the React layer (not at the AST layer) is dramatically simpler than writing a custom remark plugin: `td` receives `children` as React nodes; we string-coerce the first child, regex-match, and either return the original `<td>` or replace its content with a `<button onClick>`. No AST visitor, no plugin to test in isolation.
- For navigation, prefer `useNavigate()` from react-router over `<Link>` for two reasons: (a) the `<button>` semantics avoid invalid HTML inside `<td>` (a `<a>` inside a clickable `<tr>` is a real accessibility footgun — see [React School: React Table Navigate on Row Click](https://react.school/react-table-navigate-on-row-click/)), and (b) the action is "switch view mode + load partner file," not just a URL change, so we want a function we control ([React Router useNavigate docs](https://reactrouter.com/api/hooks/useNavigate)).
- Why not `<Link>` directly: react-markdown produces `<a>` elements for markdown links, and we'd have to build the URL inside the markdown source itself — coupling shot files to the webapp's URL scheme. Programmatic navigation keeps the `.md` file URL-agnostic.

**Why not a custom remark plugin:** plugins are the right answer when the markdown *grammar* needs extending. Here the grammar is unchanged — we're just specialising one specific cell's rendering. Component override is the smaller, more local hammer.

### 2.3 ImageRefView — direct `<img src="/api/file?path=...">` (no blob URL)

**Recommendation:** Render `main_seedream.png` with a plain `<img src="/api/file?path={encoded-relative-path}" alt="Seedream 立绘 reference" />`. No `fetch` + `URL.createObjectURL` indirection. Backend serves the binary with `Content-Type: image/png` via FastAPI `FileResponse` ([FastAPI: Serving Static Files](https://fastapitutorial.com/blog/static-files-fastapi/)).

**Rationale:**
- The `<img>` tag with a same-origin URL is the simplest correct path. Browsers send cookies / credentials automatically on same-origin GETs, the EXPOSED_TREE sandbox + extension allowlist (`.png` in v1, `.jpg` allowed) already gates the response on the backend, and the image route is the same `/api/file` endpoint already audited for path traversal — no new attack surface.
- Blob URL indirection is only worth its complexity when the request needs **custom auth headers** (Bearer tokens, X-Auth-* headers) that an `<img>` tag cannot inject ([AlphaHydrae: Display image protected by header-based auth](https://alphahydrae.com/2021/02/how-to-display-an-image-protected-by-header-based-authentication/)). Our backend's auth boundary is the Origin/Host gate + loopback-only binding — same-origin `<img>` requests pass that gate by construction.
- CSP implications: the app must declare `img-src 'self' data:` (or just `'self'`) to permit images from the same origin and reject everything else — the default `default-src` fallback would otherwise apply ([MDN: CSP img-src](https://content-security-policy.com/img-src/)). No `blob:` scheme needed in the policy because we don't use blob URLs.
- `rehype-sanitize`'s default schema allows `img` with same-origin / relative `src` URLs ([rehype-sanitize README](https://github.com/rehypejs/rehype-sanitize)); but the image is rendered by `ImageRefView` outside the markdown pipeline, not inside it, so sanitizer interaction is moot for this case.
- **SVG carve-out:** the extension allowlist already excludes `.svg` (revised hard constraint #4 — code-execution vector). ImageRefView's `<img>` MUST set `loading="lazy"` to avoid eager fetch when the user opens the file before scrolling to the right pane.

**Refresh semantics:** when the user replaces `main_seedream.png` on disk, a hard reload (or re-navigation to the file) re-issues the GET. Browser cache is bypassed because the file path is the only key — append `?mtime={mtime}` (read from the tree-walk metadata) to the `src` if cache-busting is needed; this couples to the same mtime the concurrency gate already exposes (revised hard constraint #6).

### 2.4 "锁定块" pill — pre-process markdown text with a regex (NOT a remark plugin)

**Recommendation:** Before passing the markdown source to `<ReactMarkdown>`, scan with a regex for the locked-descriptor sentinel (`/^【.+?·.+?·.+?锁定描述符.+?】/m` or simpler: a leading line matching `/^【.+?锁定描述符/`). Find the surrounding paragraph block (sentinel line + non-blank lines until next blank line OR end of `角色:` field), wrap it in an HTML span with a known class (`<span class="locked-block" data-pill="锁定块">…</span>`), then let `react-markdown` render. CSS positions the pill in the corner.

**Rationale:**
- The locked block is not a markdown construct — it's a project convention with a distinctive sentinel-bracket header (`【孙悟空 · 觉醒态 · 锁定描述符 v1】` is the canonical example, visible in `shot02_kling.md` and `main_seedream.md`). A `remark-directive`-style plugin ([remark-directive](https://github.com/remarkjs/remark-directive)) would be the "correct" approach if the syntax were `:::locked` fenced blocks, but our content is plain Chinese with bracket markers and we cannot edit the existing files to add directive syntax (byte-equality contract — FR-12/13 of wukong project).
- Pre-processing the markdown string with a single regex pass is O(n), runs once per file load, adds zero new dependencies, and is trivially testable as a pure string→string function.
- `rehype-sanitize`'s default schema allows `<span>` with `class` attribute, so the pill marker survives sanitization. If the schema is tightened to drop `data-*` attributes, fall back to a magic class name (`locked-block-pill-marker`) that CSS hooks on.
- The pill itself renders via `::after` content in CSS — no extra DOM, no React element to manage focus order on.

**Why not regex on the rendered DOM:** that'd run after every React reconciliation and require a `useEffect` + `MutationObserver` dance. Pre-processing the source string is one-pass at the boundary.

### 2.5 CJK rendering — `lang="zh-Hans"` on render container, browser-default wrap, system font stack

**Recommendation:** Wrap every markdown render output in a `<div lang="zh-Hans" class="md-cjk-content">` container. CSS:

```css
.md-cjk-content {
  font-family: -apple-system, BlinkMacSystemFont, "PingFang SC",
               "Microsoft YaHei", "Noto Sans CJK SC", sans-serif;
  word-break: normal;          /* matches qa.md Q3 answer A */
  overflow-wrap: anywhere;     /* defensive for very long URLs / hex dumps */
  line-height: 1.7;            /* CJK breathes more than Latin */
  text-rendering: optimizeLegibility;
}
```

**Rationale:**
- The `lang="zh-Hans"` attribute is **load-bearing** for Han Unification: without it, browsers may pick a Japanese or Korean glyph variant for the same Unicode codepoint ([font-converters.com: CJK Font Optimization Guide](https://font-converters.com/languages/cjk-font-optimization)). For our content (all Simplified Chinese), `zh-Hans` is the correct subtag — `zh-CN` is also accepted but `zh-Hans` more precisely identifies the script and is the W3C-preferred form.
- The system font stack avoids any `@font-face` / web-font load — eliminates FOUT / FOIT, eliminates the `font-display: swap` decision entirely, and keeps the bundle tiny. The macOS / Windows stacks each have a high-quality CJK face installed at OS level.
- `word-break: normal` is the qa.md-locked answer (Round 1, V1 view-mode scope Q3, option A). It matches the browser default and produces correct line breaks at CJK boundaries. `overflow-wrap: anywhere` is added as a defensive secondary so the rare extra-long token (e.g., a long English brand name embedded in Chinese prose, a hex color list, a pasted URL) doesn't overflow the pane.
- **Unicode normalization:** the only realistic pitfall is when content is authored in NFD (decomposed) and rendered in a font that lacks combining-mark glyph coverage. `react-markdown` doesn't normalize. Our source files are NFC (the default for Chinese on every modern editor) — we accept this as a known constraint and don't add a normalization step in v1.
- `text-rendering: optimizeLegibility` is safe for CJK at our scale (< 100KB markdown per render); it's the higher-quality kerning hint browsers fall back to. Avoid `optimizeSpeed` — visibly worse for CJK.

### 2.6 Copy-to-clipboard — `navigator.clipboard.writeText` + persistent `aria-live="polite"` region

**Recommendation:** Each pane (Kling pane, Seedance pane, Seedream-prompt pane) ships a `<button type="button" class="copy-btn">复制 Kling prompt</button>` (label varies). Click handler:

```ts
async function handleCopy(text: string, label: string) {
  await navigator.clipboard.writeText(text);
  setToastMsg(`已复制：${label}`);
}
```

The toast renders into a single app-wide live region:

```jsx
<div
  id="copy-toast-live-region"
  aria-live="polite"
  aria-atomic="true"
  className="visually-hidden-focusable"
>
  {toastMsg}
</div>
```

**Rationale:**
- A single, persistent live region mounted at app root is the documented React pattern that survives component re-mounts (toast text gets pushed in via state) — without it, screen readers may miss announcements when the live region itself is the thing being newly mounted ([dev.to: When Your Live Region Isn't Live](https://dev.to/dkoppenhagen/when-your-live-region-isnt-live-fixing-aria-live-in-angular-react-and-vue-1g0j)).
- `aria-live="polite"` (not `assertive`) is correct for a non-critical "copied" confirmation — it queues behind any in-flight announcement instead of interrupting ([React Aria Toast docs](https://react-aria.adobe.com/Toast/)).
- `navigator.clipboard.writeText` is available on all modern browsers in the localhost-loopback context (secure-context requirement is satisfied by `127.0.0.1`). No `document.execCommand('copy')` fallback needed.
- The visible toast can sit in the bottom-right corner with a 3-second auto-dismiss; the live region announcement is decoupled and fires the same instant. Visually-hidden styling on the live region (`clip: rect(0,0,0,0); position: absolute; height: 1px; width: 1px; overflow: hidden;`) keeps it screen-reader-only.

**What gets copied:** for ShotPairView, the entire file body (raw markdown) — this is what Kling/Seedance UIs accept as paste input. For ImageRefView, only the `## Prompt（中文）` section (per the README's usage step 2 in `main_seedream.md`); detect by extracting the section between the `## Prompt（中文）` heading and the next `##` heading.

## 3. Component structure sketches

### 3.1 TypeScript interfaces

```ts
// shared types
export interface FileMeta {
  readonly absPath: string;          // canonical, sandbox-resolved
  readonly relPath: string;          // for display + cross-links
  readonly mtimeMs: number;          // for cache-bust + concurrency gate
  readonly sizeBytes: number;
  readonly extension: string;        // ".md" | ".png" | ...
}

export interface FileBody {
  readonly meta: FileMeta;
  readonly text: string | null;      // null for binary
  readonly isBinary: boolean;
}

// view dispatch
export type ViewMode =
  | "markdown"
  | "shot-pair"
  | "shotlist-table"
  | "image-ref"
  | "qa"
  | "jsonl"
  | "code"
  | "image-placeholder";

export interface ViewProps {
  readonly file: FileBody;
  readonly projectName: string;      // e.g., "wukong_juexing"
}

// ShotPairView
export interface ShotPairViewProps extends ViewProps {
  readonly shotNumber: string;       // "02"
  readonly partnerKling: FileBody | null;
  readonly partnerSeedance: FileBody | null;
}

// ShotlistTableView
export interface ShotlistTableViewProps extends ViewProps {
  readonly onShotClick: (shotNumber: string) => void;
}

// ImageRefView
export interface ImageRefViewProps extends ViewProps {
  readonly companionImage: FileMeta | null;   // null => render fallback placeholder per qa.md Image preview Q2
}
```

### 3.2 ShotPairView — minimal JSX

```tsx
export function ShotPairView(props: ShotPairViewProps) {
  const { partnerKling, partnerSeedance, shotNumber } = props;
  const left = partnerKling;
  const right = partnerSeedance;

  return (
    <PanelGroup direction="horizontal" autoSaveId="shot-pair-split">
      <Panel defaultSize={50} minSize={20}>
        <ShotPane file={left} kind="kling" />
      </Panel>
      <PanelResizeHandle className="resize-handle" />
      <Panel defaultSize={50} minSize={20}>
        <ShotPane file={right} kind="seedance" />
      </Panel>
    </PanelGroup>
  );
}

function ShotPane({ file, kind }: { file: FileBody | null; kind: "kling" | "seedance" }) {
  if (!file) {
    return (
      <YellowBanner>
        缺少配对文件: {kind === "kling" ? "shotNN_kling.md" : "shotNN_seedance.md"}
      </YellowBanner>
    );
  }
  return (
    <div className="shot-pane">
      <PaneHeader title={file.meta.relPath}>
        <CopyButton text={file.text ?? ""} label={`${kind === "kling" ? "Kling" : "Seedance"} prompt`} />
      </PaneHeader>
      <MarkdownRenderer source={file.text ?? ""} />
    </div>
  );
}
```

### 3.3 ShotlistTableView — minimal JSX

```tsx
const SHOT_RE = /^\s*`?shot(\d{2})`?\s*$/;

export function ShotlistTableView({ file, onShotClick }: ShotlistTableViewProps) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      rehypePlugins={[rehypeSanitize]}
      components={{
        td(p) {
          const text = childrenToString(p.children);
          const m = text.match(SHOT_RE);
          if (m) {
            return (
              <td>
                <button
                  type="button"
                  className="shot-link"
                  onClick={() => onShotClick(m[1])}
                >
                  shot{m[1]}
                </button>
              </td>
            );
          }
          return <td {...p} />;
        },
      }}
    >
      {file.text ?? ""}
    </ReactMarkdown>
  );
}
```

### 3.4 ImageRefView — minimal JSX

```tsx
export function ImageRefView({ file, companionImage }: ImageRefViewProps) {
  return (
    <PanelGroup direction="horizontal" autoSaveId="image-ref-split">
      <Panel defaultSize={50} minSize={25}>
        <div className="image-ref-prompt-pane">
          <PaneHeader title={file.meta.relPath}>
            <CopyButton
              text={extractPromptSection(file.text ?? "")}
              label="Seedream prompt"
            />
          </PaneHeader>
          <MarkdownRenderer source={file.text ?? ""} />
        </div>
      </Panel>
      <PanelResizeHandle className="resize-handle" />
      <Panel defaultSize={50} minSize={25}>
        {companionImage ? (
          <img
            className="image-ref-preview"
            src={`/api/file?path=${encodeURIComponent(companionImage.relPath)}&mtime=${companionImage.mtimeMs}`}
            alt="Seedream 立绘 reference"
            loading="lazy"
          />
        ) : (
          <ImageRefMissingPlaceholder />
        )}
      </Panel>
    </PanelGroup>
  );
}
```

## 4. Implications for the spec — concrete FR seeds

Stage 4's spec should fold in (FR numbers illustrative — final numbering belongs to the spec author):

- **FR-views-v1** — Three new view-mode components ship in v1: `ShotPairView`, `ShotlistTableView`, `ImageRefView`. All other custom views (Storyboard, Render-API stub) deferred per qa.md.
- **FR-split-pane-lib** — Adopt `react-resizable-panels` v4 as the ONLY split-pane primitive. Both ShotPairView and ImageRefView use it. Persist split position per-view via `autoSaveId`.
- **FR-shotlist-link-mechanism** — `ShotlistTableView` overrides `react-markdown`'s `td` slot, regex-matches `^\s*\`?shot(\d{2})\`?\s*$` on the first cell text, and renders a `<button>` that calls a passed `onShotClick(shotNumber)` prop. The host component bridges to `useNavigate` to switch the active file to `prompts/shot{NN}_kling.md` with `view=shot-pair`.
- **FR-image-fetch-mode** — Companion `.png` rendered via plain `<img src="/api/file?path=...&mtime=...">` (NOT blob URL). `mtime` query param doubles as cache-buster. CSP header adds `img-src 'self'`; `blob:` not required.
- **FR-locked-block-pill** — Pre-render regex pass on markdown source wraps locked-descriptor blocks (sentinel: `^【.+?锁定描述符`) in `<span class="locked-block" data-pill="锁定块">`. CSS `::after` renders the corner pill. `rehype-sanitize` schema permits `class` and `data-pill` on `span`.
- **FR-cjk-rendering** — Every markdown render container declares `lang="zh-Hans"`. Font stack: `-apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", sans-serif`. `word-break: normal`, `overflow-wrap: anywhere`, `line-height: 1.7`. No bundled webfonts.
- **FR-copy-button** — Each pane (Kling, Seedance, Seedream prompt) ships a copy button using `navigator.clipboard.writeText`. Toast feedback writes into a single app-root `aria-live="polite" aria-atomic="true"` region. Visible toast 3s auto-dismiss; live-region announce instant.
- **FR-shot-pair-fallback** — Missing partner file: render a yellow banner with the expected partner path (qa.md Round 1 → Shot-pair detection rule Q2 → option A); other pane stays loaded.
- **FR-image-ref-fallback** — Missing companion `.png`: right pane shows the placeholder text from qa.md Round 1 → Image preview model Q2 → option A. No refresh button.
- **FR-image-readonly** — `.png` files NEVER writable via `PUT /api/file`. ImageRefView never renders an "edit" affordance for the image pane.

## 5. Open questions surfaced

1. **Shotlist click target precision:** the regex assumes the first cell of each shotlist row is the shot identifier (`shot01`, `shot02`, …). The actual `wukong_juexing/shotlist.md` matches this (cells are `` `shot01` `` ... `` `shot05` ``). If a future shotlist used a different layout (e.g., shot id in a different column, or a different naming convention), the table would render normally but no row would be clickable. Spec should either lock the layout convention in the AI-video output rules, or have ShotlistTableView fall back gracefully (already does — non-matching cells render as plain `<td>`).
2. **Shot-pair view URL state:** `useNavigate` lets us push state, but the spec must decide the URL scheme. Suggested: `?file={relPath}&view=shot-pair` so the view mode is part of the shareable URL state and a deep link survives reload. Alternative: derive view mode from file path (clicking any `prompts/shotNN_*.md` always opens ShotPairView). The latter is simpler but removes the user's ability to fall back to `MarkdownView` for a single shot file.
3. **Image refresh UX:** the recommendation is "user reloads or re-navigates." If the user wants a no-reload refresh after re-running Seedream externally, a tiny in-pane "刷新立绘" button bumping a local cache-bust counter would be a low-cost addition. Out of scope for v1 unless qa.md is revisited.
4. **Locked-block pill scope:** the regex looks for `【...锁定描述符...】` paragraph headers. If future ai_video projects use a different sentinel format (e.g., HTML-comment markers like `<!-- locked -->`), the recogniser needs updating. Spec should pin the sentinel format at the AI-video output rule layer, not at the webapp layer.
5. **`<img>` cache policy on backend:** FastAPI `FileResponse` defaults to no cache headers. If browser cache becomes an issue (image edited externally without `?mtime=` bust), backend should set `Cache-Control: no-cache, must-revalidate` for image responses — but the `?mtime=` query param already solves the practical case, so this is defense-in-depth only.
6. **`react-resizable-panels` SSR concern:** the library uses `useLayoutEffect`. In a pure SPA (Vite dev server + static build) there is no SSR, so the warning never fires. If the spec ever adds SSR (it shouldn't — it's a localhost SPA), this needs revisiting.

## Sources

- [bvaughn/react-resizable-panels (GitHub)](https://github.com/bvaughn/react-resizable-panels)
- [react-resizable-panels (npm)](https://www.npmjs.com/package/react-resizable-panels)
- [shadcn/ui Resizable docs](https://ui.shadcn.com/docs/components/resizable)
- [Theodo: Create resizeable split panels in React](https://blog.theodo.com/2020/11/react-resizeable-split-panels/)
- [remarkjs/react-markdown (GitHub)](https://github.com/remarkjs/react-markdown)
- [remarkjs/remark-gfm (GitHub)](https://github.com/remarkjs/remark-gfm)
- [rehypejs/rehype-sanitize (GitHub)](https://github.com/rehypejs/rehype-sanitize)
- [remarkjs/remark-directive (GitHub)](https://github.com/remarkjs/remark-directive)
- [React Router useNavigate hook](https://reactrouter.com/api/hooks/useNavigate)
- [React School: React Table Navigate on Row Click](https://react.school/react-table-navigate-on-row-click/)
- [AlphaHydrae: Display image protected by header-based authentication](https://alphahydrae.com/2021/02/how-to-display-an-image-protected-by-header-based-authentication/)
- [content-security-policy.com: img-src](https://content-security-policy.com/img-src/)
- [MDN: Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CSP)
- [FastAPI tutorial: serving static files](https://fastapitutorial.com/blog/static-files-fastapi/)
- [font-converters.com: CJK Font Optimization Guide 2026](https://font-converters.com/languages/cjk-font-optimization)
- [React Aria: Toast](https://react-aria.adobe.com/Toast/)
- [dev.to: When Your Live Region Isn't Live (React aria-live fixes)](https://dev.to/dkoppenhagen/when-your-live-region-isnt-live-fixing-aria-live-in-angular-react-and-vue-1g0j)
- [Mykola Aleksandrov: React.lazy + Vite manualChunks](http://www.mykolaaleksandrov.dev/posts/2025/10/react-lazy-suspense-vite-manualchunks/)
