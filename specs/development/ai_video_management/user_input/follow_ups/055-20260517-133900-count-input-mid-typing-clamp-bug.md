# Follow-up draft 055 — 2026-05-17

Summary: 修 `ActorPoolGenerator` 数量 input 在中途输入时被自动 clamp 到 50 的 bug。当前 `onChange` 通过 `Math.min(MAX_BATCH_COUNT=50, Number(value))` 在每次 keystroke 都 clamp，导致用户在显示 "5" 的 input 里光标放在末尾输入 "1" → 中间值 "51" 被 React 立即 clamp 为 "50"，再输入 "0" 变 "500" → 又 clamp 为 50。用户看到的就是 "想输入 10 但永远停在 50"，且 input 视觉上短暂闪烁（"51" → "50" 的快速 snap = "fade away" 描述）。修法：input 用独立 string state 控制（`countText`），允许任意中间值；派生 numeric `count` 在使用时 clamp；input `onBlur` 时把 string state 重置回 canonical clamped 字符串。

## 用户原话

> some bug on the UI, try to enter a number in the box, the UI box just fade away, and even after I type 10, the number still stay as 50

## 根因

`apps/ui/src/components/ActorPoolGenerator.tsx`:
```tsx
<input
  type="number"
  value={count}
  onChange={(e) => setCount(Math.max(1, Math.min(MAX_BATCH_COUNT, Number(e.target.value) || 1)))}
/>
```

`MAX_BATCH_COUNT = 50`。Controlled `<input value={count}>` 每次 keystroke：
1. Browser appends digit to current displayed value (e.g. "5" + "1" = "51")
2. onChange fires with value "51"
3. `Number("51") || 1 = 51`
4. `Math.min(50, 51) = 50`, `Math.max(1, 50) = 50`
5. `setCount(50)` → React re-renders with `value={50}` → input snaps to "50"
6. 用户继续输 "0" → "500" → clamp 回 50 → input snap

中途值永远到不了 user 想要的数字（除非用户先全选清空再输入；但 browser default 行为是 cursor 不 select-all on focus）。

## 决策

| 项 | 决策 | 理由 |
|---|---|---|
| 修法 | input 用独立 `countText: string` 状态；派生 `count: number` 用 `useMemo` clamp at use-time | 经典 controlled-input + late-validation pattern；user 中途输入自由，只在 blur 或 submit 时落到 canonical |
| Blur 行为 | onBlur 把 `countText` 重置为 `String(count)`（canonical clamped 字符串） | 失焦后 input 显示合法 stamp 值；保留 visual 反馈 |
| Initial state | `countText = "5"`（与原 `count=5` 默认一致） | 无 UX 变化 |
| 何处用 numeric `count` | `onPreview` / `onConfirmGenerate` / `onDiverseGenerate` / progress 显示等所有现有点；用 `useMemo` 派生即可全自动 | 0 调用方改动 |
| `<input>` 的 `min` / `max` 属性 | 保留 `min={1}` `max={MAX_BATCH_COUNT}` | HTML5 visual hint（上下箭头）；不再用于 onChange clamp 但浏览器仍提供约束 UX |
| Edge case: 用户输入空 / 非数字 | derived `count` fallback 到 1 | 与原行为一致 |
| Edge case: 用户输入小数 / 负数 | `Math.trunc` + `Math.max(1, ...)` | 强制正整数 |
| 测试 | 手动 — 进 ActorPoolGenerator，光标停在末尾输 "1" "0" 应得到 10；input 不闪烁 | 单一 UI fix，无 backend 改动 |

## 功能要求

### Frontend only

**`apps/ui/src/components/ActorPoolGenerator.tsx`**：

1. 替换 `const [count, setCount] = useState<number>(5)` 为 `const [countText, setCountText] = useState<string>("5")`。
2. 加 `const count = useMemo<number>(() => { ... }, [countText])` — 解析 + clamp 派生。
3. Input 改为：
   ```tsx
   <input
     type="number"
     min={1}
     max={MAX_BATCH_COUNT}
     value={countText}
     onChange={(e) => setCountText(e.target.value)}
     onBlur={() => setCountText(String(count))}
     disabled={busy || previewBusy}
   />
   ```
4. 删除现有 onChange 内的 clamp 逻辑（被 derived count 取代）。
5. 其余 call sites（`onPreview` / `onConfirmGenerate` / `onDiverseGenerate` / footer 按钮 label）不动 — 仍用 `count`，因为它现在是 useMemo derived。

### 不动

- 后端 / endpoint / DTO / Container / mapper / 域层全部不变。
- 其它 frontend 组件不变。
- spec.md / acceptance_criteria.md 不动（无 FR 行为变化，仅 UI bugfix）。

### User input + audit

- `revised_prompt.md` header bump for 054。
- `changelog.md` append follow-up 054 entry。

## 安全 / 边界

- 纯前端 UI fix；零 backend / endpoint / shape 变化。
- Derived `count` 总在 `[1, MAX_BATCH_COUNT]` 范围；非数字 / 空 / 负数 fallback 到 1；submit 时永远是合法值。
- `useMemo` 依赖只有 countText；不引入新 re-render 触发器。
- `onBlur` 把 input value 重置为 canonical 后，下次 focus 时若 user select-all 输入，行为正常；不 select-all 直接 append，最终 blur 时也会归位（不会有 stuck-at-50）。
- HTML5 `<input type="number" max=50>` 浏览器箭头点击仍会 cap 在 50 — 与 derived count clamp 一致，无矛盾。

## 不在本 follow-up 范围

- 不引入 select-all-on-focus（可作为 v2 UX polish；目前 fix 已足够让 user 顺利输入）。
- 不动其它 number input（如 ActorView form 内的字段 / SiblingMedia bulk-select）— 它们要么不存在同 bug，要么不在用户上下文中。
- 不增 / 减 `MAX_BATCH_COUNT`。
- 不写 frontend Vitest（统一推迟）。
