# Follow-up draft 058 — 2026-05-17

Summary: 把 "🎭 生成演员人脸" 模态锁死为**仅顶角 × 按钮才能关闭**。当前 `.modal-backdrop` `onClick={onCloseRequest}` 让点击空白处关闭模态，footer 的 "关闭" 按钮也是一条关闭路径——这两条都是 follow-up 057 防御 layer 之外的合法用户交互，但用户希望进一步收紧：**所有"意外关闭"路径全部移除**，只有顶角 × 是合法 close affordance。"停止" 按钮（busy state 期间）保留为 cancel-in-flight 动作，不是 close。

## 用户原话

> please make 生成演员人脸 model only close by explictly click the x button, no other way to close it on front end

## 决策

| 项 | 决策 | 理由 |
|---|---|---|
| Backdrop 关闭 | **移除** — `.modal-backdrop` 的 `onClick={onCloseRequest}` 改为 noop（直接删除 onClick） | 用户原话 "no other way to close it on front end"；click-outside 是最常见 "意外关闭" 路径 |
| Footer "关闭" 按钮 | **移除** | 文字按钮也算 "another way"；用户要 single-affordance |
| × 顶角按钮 | **保留** — 既有 `onClick={onCloseRequest}` 路径不变 | 唯一合法 close affordance；保持 busy-state cancel-only 行为 |
| 停止按钮 (busy state) | **保留** | 不是 close — 是 cancel-in-flight；按下后 modal 仍开，只是 `cancelledRef.current = true` 停掉 in-flight worker |
| Esc 键 | 现在就不绑定 — 检查后无需新增防御 | 该 modal 不是 native `<dialog>`，浏览器不会自动响应 Esc；现有 keydown listener 只对 Ctrl+Shift+E 响应（sidebar tree focus），与本 modal 无关 |
| Backdrop visual 不变 | 是 — backdrop 仍渲染为半透明遮罩，仅失去 click 关闭功能 | 视觉上还是 modal；只是 click-outside dead |
| Stop-propagation 调整 | `.modal-panel` 的 `e.stopPropagation()` 可以保留但不再必要（无 backdrop close handler 接收冒泡）| 保留作 defensive — 与 follow-up 057 的 input-level guards 一致 |
| `onCloseRequest` 函数 | 保留 — × 按钮仍调用它（busy → cancel；not busy → onClose） | 唯一 caller 后仍是 × |
| `onClose` prop | 不动 — 仍由 Sidebar 传入 setGeneratorOpen(false) | 内部 onClose 调用次数减少（footer 按钮删除后），但 prop 保持 |
| 其它 modal (如 PromptPreviewModal / 未来 modals) | **不动** | 用户明确指 "生成演员人脸 model"；其它 modal 保持现行 click-outside-close 行为 |

## 功能要求

### Frontend only

`apps/ui/src/components/ActorPoolGenerator.tsx`:

1. `.modal-backdrop` 的 `onClick={onCloseRequest}` **删除**（变成无 onClick 的纯遮罩 div）。
2. `.modal-panel` 的 `e.stopPropagation()` **保留**（与 follow-up 057 input guard 风格一致；纯防御）。
3. Footer 内 `{busy ? "停止" : "关闭"}` 三元分支：busy 分支保留，not-busy 分支的 `<button>关闭</button>` **整段删除** — not-busy state 下 footer 仅剩主按钮（"预览 prompt" / "生成 N 个多样化 actor"）。
4. `onCloseRequest` 函数本身不动（× 按钮仍调用）。
5. `onClose` callback prop 不动。

### 不动

- 后端 / endpoint / DTO / Container / 域层 / repository / 域错误全部不变。
- 其它 frontend 组件不变（PromptPreviewModal / DeletedView / Editor 等其它 modal 不收紧）。
- spec.md / acceptance_criteria.md 不动（无 FR 行为变化 — 仅 close-affordance 收紧，模态的功能契约不变）。

### User input + audit

- `revised_prompt.md` header bump for 058。
- `changelog.md` append 058 entry。

## 安全 / 边界

- **Modal 关闭路径单点化** — 整个 generator modal 的 close action 仅经 × 按钮 → `onCloseRequest`；busy 时变 cancel，not-busy 时调 `onClose()`。便于未来加 confirmation prompt（"真的要放弃 N 个 actor 的生成？"）只需 patch 一处。
- **× 按钮始终 enabled**（仅 aria-label 在 busy 时切换为 "中断后关闭"）— 用户始终能逃出模态；不构成无逃逸 trap。
- **Backdrop 仍渲染** — 视觉上保持 modal 语义（背景遮罩 + 居中面板）；只是失去 click-to-dismiss 功能。
- **键盘逃出**：Tab 仍能在 modal 内循环 focus（无 focus-trap 库引入；现有行为不变）；Esc 不绑定 → 不关闭 → 与 footer "关闭" 移除一致。
- **A11y 影响**：用户必须用鼠标 / 触摸点 × 或键盘 tab 到 × 后 Enter。`type="button"` × 仍是 native button，screen-reader 可达。
- **未来如需 confirm-on-close**：只需在 `onCloseRequest` 内加 `if (!confirm("...")) return;` —— 单点 patch。

## 不在本 follow-up 范围

- 不引入 focus-trap 库
- 不收紧 PromptPreviewModal 或其它 modal
- 不加 confirm-on-close prompt
- 不动 stage 6 generation worker pool / cancel 语义
- 不写 pytest / vitest
