# Follow-up draft 063 — 2026-05-17

Summary: `ActorPoolGenerator` 下拉菜单 option 文字汉化。当前 `<option>` 使用 `ATTR_OPTIONS` 的 raw 英文/slug（"asian", "male", "handsome", "modern-casual", "normal"），用户希望看到中文标签。`<option value>` 仍传 slug（与后端 closed-enum schema 兼容），仅显示文本汉化。

## 用户原话

> the drop down menu under 生成演员人脸 should be all chinese

## 决策

| 项 | 决策 | 理由 |
|---|---|---|
| 实现 | 在 `apps/ui/src/api.ts` 加 `ATTR_LABELS_ZH` map（per-field slug→Chinese label）| 单点 export；与 ATTR_OPTIONS 平行；ActorGrid filter 也可复用 |
| `<option value>` | 保留 slug | 后端 closed-enum schema 不变 |
| 翻译表 | ethnicity / gender / age_range / look / style / resolution 全部 | 与现有 dropdown 一一对应 |
| 范围 | 仅 `ActorPoolGenerator`（用户原话） | ActorGrid filter 下次可用同 map 翻译，但本 follow-up 不扩 |
| 后端 | 不动 | 仅前端显示 |

## 功能要求

`apps/ui/src/api.ts`:
- 新 export `ATTR_LABELS_ZH: { [K in keyof typeof ATTR_OPTIONS]: Record<string, string> }`，6 个字段全填中文。

`apps/ui/src/components/ActorPoolGenerator.tsx`:
- import 加 `ATTR_LABELS_ZH`。
- 6 个 `<option>` 块的文本从 `{o}` 改为 `{ATTR_LABELS_ZH[field][o]}`。

无后端 / spec / 测试改动。

## 翻译表

| 字段 | slug → 中文 |
|---|---|
| ethnicity | asian→亚洲 / east-asian→东亚 / south-asian→南亚 / caucasian→白人 / african→非洲裔 / latino→拉丁裔 / middle-eastern→中东 / mixed→混血 |
| gender | male→男 / female→女 |
| age_range | 18-25→18-25 岁 / 26-35→26-35 岁 / 36-50→36-50 岁 / 51-65→51-65 岁 / 65+→65 岁以上 |
| look | handsome→俊朗 / beautiful→美丽 / cute→可爱 / mature→成熟 / rugged→粗犷 / soft→温柔 / aristocratic→贵族气质 / fierce→凌厉 |
| style | modern-casual→现代休闲 / period-ancient-china→古装仙侠 / period-western→西方古装 / business→商务 / streetwear→街头潮流 / sci-fi→科幻 / fantasy→奇幻 |
| resolution | normal→普通 (~1024px Kling 原始) / 2k→2K (2048px) / 4k→4K (4096px) |
