# Follow-up draft 067 — 2026-05-17

Summary: 修 follow-up 064 漏的第二份 `LOOK_OPTIONS`。064 把 5 个新 look 值（righteous / sinister / seductive / cunning / innocent）只加到 infrastructure 层 `actor__writer.py::LOOK_OPTIONS`，但 domain 层 `actor__valueobject.py::LOOK_OPTIONS` 仍是原 8 项；`ActorAttrs.validate()` 在 application command / query 里跑 → 用户选新 look 值 preview → `InvalidActorAttributeError("look=... not in schema")` → 路由层映射成 `400 invalid_attribute`。用户看到 "预览失败: 400 invalid_attribute"。一行扩 domain `LOOK_OPTIONS` 同步 5 新值即可。

## 用户原话

> when I try to generate actors, I got 预览失败: 400 invalid_attribute

## 根因

DDD 拆层后两份 closed-enum source-of-truth：
- `libs/domain/value_objects/actor__valueobject.py::LOOK_OPTIONS` (domain validate, 用 `ActorAttrs.validate()`)
- `libs/infrastructure/writers/actor__writer.py::LOOK_OPTIONS` (infra `_validate_attrs`)

Follow-up 064 only updated the infra copy; domain stayed at 8 entries. The application layer's `ActorQuery.preview_prompts` / `ActorCommand.generate` call `attrs.validate()` first (domain) — that's where the rejection happens.

## 决策

| 项 | 决策 | 理由 |
|---|---|---|
| Fix | 把 5 新 slug 加到 `libs/domain/value_objects/actor__valueobject.py::LOOK_OPTIONS` | One-line change；与 infra 对齐 |
| Inline 注释 | 加 "MUST stay in sync with infra LOOK_OPTIONS" 注释 | 防再漏；指向 infra path |
| 长期：单一 source of truth | **不在本 follow-up 范围** — 一份 enum 在 domain 是 DDD 应有；infra 应 `from libs.domain.value_objects... import LOOK_OPTIONS` 而不是自己定义。后续 cleanup | 当前 mismatch 已修，结构性 refactor 留独立 follow-up |
| 检查其它字段 | 跑了一遍 ETHNICITY / GENDER / AGE_RANGE / STYLE / RESOLUTION — 5 字段 064 未扩，domain + infra 都没改 → 仍 in sync | 无需动 |
| Validation | 跑 ActorAttrs.validate() against 5 new look values + 1 known-invalid value | 5 pass; invalid 仍 reject |

## 功能要求

`libs/domain/value_objects/actor__valueobject.py`:
- `LOOK_OPTIONS` frozenset 扩 5 个 slug: `righteous`, `sinister`, `seductive`, `cunning`, `innocent`。
- 加 inline 注释指明 "MUST stay in sync with `libs/infrastructure/writers/actor__writer.py::LOOK_OPTIONS`"。

无 frontend / API / spec FR 变化。

## 不在本 follow-up 范围

- 不重构 LOOK_OPTIONS 到单一 source of truth（domain 导出 → infra import）。这是 DDD enum-duplication 通用问题，需要扫所有 closed enums (ETHNICITY/GENDER/AGE_RANGE/STYLE/RESOLUTION 都有 domain+infra 两份)，留独立 follow-up。
- 不动 archetype 反查 / classify。
- 不写 pytest（添 enum 后 boot_smoke 已 catch；显式 vitest 推迟）。
