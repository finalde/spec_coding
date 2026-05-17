# Follow-up draft 057 — 2026-05-17

Summary: Follow-up 055 fixed the mid-typing clamp flicker on `ActorPoolGenerator` count input, but the user reports a second symptom — "when I try to enter the amount, the UI window just get closed" — modal dismisses entirely on input interaction. The remaining failure modes are native-`<input type="number">` quirks (spinner-arrow click bubbling, validation-tooltip blur, IME compose-cancel) that can leak past the modal-panel's `e.stopPropagation()` on certain browsers. Fix: switch the input from `type="number"` to `type="text" inputMode="numeric"`, strip non-digits at onChange, and add explicit `stopPropagation` on `onClick` / `onMouseDown` / `onKeyDown` to bulletproof against any bubble. Also `preventDefault` Enter so accidental form-submit semantics never escape the input.

## 用户原话

> the bug still exist, when I try to enter the amount, the UI window just get closed

## 决策

| 项 | 决策 | 理由 |
|---|---|---|
| Input type | `text` + `inputMode="numeric"` + `pattern="[0-9]*"` | 消除原生 number input 的 spinner / validation-tooltip / wheel-scroll 副作用；mobile 仍弹数字键盘 |
| `onChange` 过滤 | 用 regex `replace(/[^0-9]/g, "")` strip 非数字 | 保留 055 的 string-state 自由输入，但只接收纯数字 char |
| `onBlur` snap | 保留 — `setCountText(String(count))` | 失焦归位到合法 clamped 字符串 |
| `onKeyDown` | `e.stopPropagation()` + `if e.key === "Enter" e.preventDefault()` | 杀死任何 Enter-自动-submit / 任何 keydown 冒泡到 modal-backdrop |
| `onClick` + `onMouseDown` | `e.stopPropagation()` | 防御性 — 即便 modal-panel 已 stopPropagation，input 自身再 stop 一次确保 spinner / validation-tooltip 等浏览器内部分发不会泄漏 |
| `min` / `max` HTML5 属性 | 删除（text input 不再需要） | clamp 全由 useMemo 派生层处理 |
| Vite HMR / 缓存提醒 | 用户应硬刷新（Ctrl+Shift+R）以确保新代码生效 | 055 修复后用户立即报"still exists"，可能 HMR 没拾到改动 |
| 不动 055 的 `countText` / `count` derive 逻辑 | 是 | 055 的 state 分离 + useMemo clamp 仍是正确底座；本 follow-up 只加防御层 |
| 不动其它 input | 是 | 仅 count input 报错；其它 select / textarea 暂未观察到问题 |

## 功能要求

### Frontend only

`apps/ui/src/components/ActorPoolGenerator.tsx`:

替换 count input 元素：
```tsx
<input
  type="text"
  inputMode="numeric"
  pattern="[0-9]*"
  value={countText}
  onChange={(e) => setCountText(e.target.value.replace(/[^0-9]/g, ""))}
  onBlur={() => setCountText(String(count))}
  onKeyDown={(e) => {
    e.stopPropagation();
    if (e.key === "Enter") e.preventDefault();
  }}
  onClick={(e) => e.stopPropagation()}
  onMouseDown={(e) => e.stopPropagation()}
  disabled={busy || previewBusy}
/>
```

不动其它内容（055 的 state 分离 + useMemo derive 保留）。

### 不动

- 后端 / endpoint / DTO / Container / 域层全部不变
- 其它 frontend 组件不变
- spec / acceptance criteria 不动

## 安全 / 边界

- `inputMode="numeric"` 让 mobile 弹数字键盘（替代 type="number" 的同行为）。
- `pattern="[0-9]*"` 是 HTML5 visual hint；不强制（也不该强制 — string-state 允许 transient）。
- `replace(/[^0-9]/g, "")` 在每次 keystroke 过滤；用户 paste 含非数字内容时只保留数字。
- `e.stopPropagation()` 在 React 合成事件层阻止冒泡 — 与 modal-panel 已有 stopPropagation 互不冲突 / 互补。
- `preventDefault` Enter — 防止 form-submit 默认行为（本组件无 form，但浏览器有些版本仍可能触发副作用）。
- 不影响 derived `count` 逻辑：useMemo 仍 clamp 到 [1, MAX_BATCH_COUNT]。

## 不在本 follow-up 范围

- 不重写整个模态为 `<dialog>` element / 引入 focus-trap 库
- 不写 vitest（统一推迟）
- 不动 spec 或 acceptance — 是 v1 UI defensive patch，无 FR 行为变化
- 不调整 MAX_BATCH_COUNT
