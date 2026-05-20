# Follow-up draft 084 — 2026-05-17

User 反馈："删除成功的提示在前端永远不消失，是个 bug"。

## 用户原话

> 删除成功的提示在前端永远不消失，是个bug

## 根因

`apps/ui/src/lib/announce.ts` 有一个**带 TTL 自动清除**的 shared `announceToast(message, ttlMs=4500)`（在 follow-up 060 引入），但**没有任何调用方 import 它**。4 个 component 各自复制了一个 **缺 TTL 清除** 的本地 `announceToast` / `announce`：

| 文件 | 本地 helper 位置 | 失效调用方 |
|---|---|---|
| `apps/ui/src/components/Reader.tsx:361-366` | `function announceToast(message: string)` 不 clear region | 7 处 (其中 line 134 `Deleted ${name}` 是删除提示) |
| `apps/ui/src/components/ActorGrid.tsx:406-411` | 同上 | 2 处 (line 147 批量删除成功) |
| `apps/ui/src/components/DeletedView.tsx:298-303` | 同上 | 1 处 (line 112 永久删除成功 `已永久删除 ${okCount}...`) |
| `apps/ui/src/components/SiblingMedia.tsx:66-74` | `function announce(message)` 同样不 clear | 8 处 archive/unarchive 提示 |

每个本地 helper 都只做了 `textContent = ""` + `setTimeout(... textContent = message, 30)`，**没有 `setTimeout(..., 4500)` 把 textContent 清空 + 移除 `.is-visible` class**。导致 region 一旦设置就永久驻留。

`lib/announce.ts` 的注释 (follow-up 060) 明确写过 "Auto-clears after a TTL — re-firing while still visible resets the clock" — utility 写对了, 但 caller migration 漏做。本 follow-up = 补做 060 的 caller migration。

## 改动范围

### 项目代码（本 follow-up 同 turn 落地）

1. `apps/ui/src/components/Reader.tsx`：
   - 顶部 import 加入 `import { announceToast } from "../lib/announce";`
   - 删除本地 helper (line 361-366)。
   - 7 处 call sites 不动 (函数签名一致)。

2. `apps/ui/src/components/ActorGrid.tsx`：
   - 顶部 import 加入 `import { announceToast } from "../lib/announce";`
   - 删除本地 helper (line 406-411)。
   - 2 处 call sites 不动。

3. `apps/ui/src/components/DeletedView.tsx`：
   - 顶部 import 加入 `import { announceToast } from "../lib/announce";`
   - 删除本地 helper (line 298-303)。
   - 1 处 call site 不动。

4. `apps/ui/src/components/SiblingMedia.tsx`：
   - 顶部 import 加入 `import { announceToast as announce } from "../lib/announce";` (aliased import 保留本地 8 处 `announce(...)` call sites 命名不动)。
   - 删除本地 helper (line 66-74)。

### Pipeline 状态

5. `specs/development/ai_video_management/user_input/revised_prompt.md` — `Last regenerated` 头 bump 到 084。
6. `specs/development/ai_video_management/changelog.md` — append 084 entry。

## 不在本 follow-up 范围

- `lib/announce.ts` 不动 — utility 已正确实现 (TTL 4500ms + clear region + remove `.is-visible` class)。
- `apps/api/` 后端不动 — 本 bug 纯前端 UX。
- `App.tsx` 里 mount 的 `#aria-live-toast` div 不动。
- CSS `.a11y-live-region` / `.is-visible` (styles.css:82-87) 不动。
- 其他 component 内 toast-like 提示 (如 inline error banner, modal) 不动 — 本 follow-up 只修 `aria-live-toast` region 永久驻留 bug。

## Acceptance trigger

- 4 文件 `Edit` 后, 仍只剩 1 个 `announceToast` definition (`lib/announce.ts:19`)。
- 仍只剩 1 个 `announce`-shape definition (`lib/announce.ts:19`, 在 SiblingMedia 通过 aliased import 暴露为 `announce`)。
- TypeScript `npm run typecheck` (or `tsc --noEmit`) 通过。
- `npm test` 通过 (existing test suite, 不要求新 test — follow-up 060 utility 已被覆盖, 这里仅是 import 拓宽)。
- 手测 (用户侧)：触发 删除 / 永久删除 / 批量删除 / archive / unarchive — 4.5 秒后 toast 自动消失 + DOM `#aria-live-toast` 失去 `.is-visible` class。

## 判断

- 选 import + delete-local-helper 而非 fix-each-local-helper：保留单一权威实现, 避免下次 TTL 调整时四处漂移。`lib/announce.ts` 的 follow-up 060 注释指明 utility 是为共享而生。
- SiblingMedia 用 aliased import (`as announce`) 而非 rename 8 处 call sites：最小 diff, 行为等价。
