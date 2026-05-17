# Follow-up draft 062 — 2026-05-17

Summary: 修 "点击确认发送后 UI 没反应" 的 bug。`PromptPreviewModal` 在用户点 ✓ 确认发送之后**没被关闭** — `onConfirmGenerate` 启动 9-worker pool 但从不调 `setPreview(null)`。预览模态仍叠在生成器模态之上，遮住底下的 `ProgressPanel` → 用户看不到 done/failed/inFlight 进度，错以为 "什么都没发生"。实际后台正在跑生成（HTTP 已发出，actor 文件夹已建立）。修法：`onConfirmGenerate` 首行（busy guard 之后）立刻 `setPreview(null)`，关闭预览模态让 ProgressPanel 浮上来。

## 用户原话

> after I click 确认发送，on the ui, nothing happens, is the right behaviour to just close that modal or what?

回答用户的问题：**是的**，正确行为应该是点 ✓ 确认发送后立即关闭 `PromptPreviewModal`，回到生成器模态展示实时进度。现行代码漏了关闭这一步，所以 UI "什么都没发生"（实际生成进行中，被预览模态盖住了）。

## 根因

`apps/ui/src/components/ActorPoolGenerator.tsx` `onConfirmGenerate`:

```typescript
const onConfirmGenerate = useCallback(async () => {
  if (!preview || busy) return;
  setBusy(true);
  setToast(null);
  ...
  setProgress({ done: 0, failed: 0, total, inFlight: 0, phase: "idle", ... });
  ...
  // 9-worker pool 启动 — 后台跑
}, [...]);
```

整段没 `setPreview(null)`。`PromptPreviewModal` 是条件渲染 `{preview ? <PromptPreviewModal /> : null}`，preview 不被清就一直显示，遮住下面的 generator modal 体内的 `ProgressPanel`（仅当 `progress` truthy 时渲染）。

## 决策

| 项 | 决策 | 理由 |
|---|---|---|
| 修法 | `onConfirmGenerate` 在 `setBusy(true)` 之前 / 之后立即调 `setPreview(null)` | 一行修复，让预览模态关闭，ProgressPanel 浮上来 |
| 关闭时机 | 启动 worker pool **之前**（先关 preview，再 start）| 用户立即看到 ProgressPanel；如果 worker 启动失败也至少看见 toast |
| Cancel 行为不变 | 是 — "取消" 按钮（PromptPreviewModal 内部）走 `onCancel = cancelPreview`，仅 `setPreview(null)`，不启动生成 | 不破 follow-up 032 的 preview-then-confirm 契约 |
| Generator modal × 按钮 | 不动 — 既有 `onCloseRequest` busy state 下为 cancel-in-flight；正常 close 时关 generator modal | follow-up 058 行为保留 |
| 同时关 generator modal？ | **否** | 用户需要看进度；自动关 generator modal 会丢失 ProgressPanel + toast。生成完成后用户自己点 × |
| 自动关 generator modal on success | **否**（v1）| 进度 + toast 是 useful 信息；用户点 × 显式关闭。未来可加 "auto-close on success" 选项，本 follow-up 不做 |

## 功能要求

### Frontend only

`apps/ui/src/components/ActorPoolGenerator.tsx`:

```typescript
const onConfirmGenerate = useCallback(async () => {
  if (!preview || busy) return;
  setPreview(null);  // <-- 新增：关闭预览模态让 ProgressPanel 可见
  setBusy(true);
  setToast(null);
  ...
}, [...]);
```

### 不动

- `PromptPreviewModal` 组件不动 — 它本身就是被外层 `preview` state 控制 mount/unmount 的，无需内部改造。
- 后端 / endpoint / DTO 全部不变。
- `cancelPreview` 不动 — 取消路径已正确。
- ProgressPanel 不动 — 已支持实时 `done/failed/inFlight` 更新。

### User input + audit

- `revised_prompt.md` header bump for 062。
- `changelog.md` append 062 entry。

## 安全 / 边界

- **`preview` 在 closure 内仍可用**：`useCallback` 捕获的是 setState 触发前的 preview 引用；setPreview(null) 触发 re-render 但当前执行中的 `onConfirmGenerate` async function 内 `preview.prompts.map` 等仍正常工作（closure capture）。
- **Re-clicking 确认发送**：第一次 click → `setPreview(null)` + `setBusy(true)`；之后 PromptPreviewModal 卸载；不会有第二次 click，因为按钮已被卸载。
- **Generation 完成后**：toast 显示在 generator modal 内；用户点 × 关闭。
- **Cancel 中途**：用户点 generator modal 内的 "停止" 按钮 → `cancelledRef.current = true` → worker 不再 claim 新 slot → done/failed 最终 count 更新 → toast 显示 "已中断 — 已生成 X / 失败 Y / 跳过 Z"。Preview 模态早已关闭，不影响。

## 不在本 follow-up 范围

- 不引入 "auto-close generator modal on success" 选项。
- 不动 generator modal × 关闭路径（follow-up 058 保留）。
- 不动 cancel 路径。
- 不重写 ProgressPanel。
- 不加 progress bar animation / sound notification。
