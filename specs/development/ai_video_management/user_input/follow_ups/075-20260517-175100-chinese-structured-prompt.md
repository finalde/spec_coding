# Follow-up draft 075 — 2026-05-17

Switch every actor-generation prompt sent to Kling from English variance-composed strings to **structured Chinese**, in the format the user specified:

```
角色描述：东亚 女性，30 岁左右
眼睛：大眼睛, 双眼皮, 桃花眼, 含情脉脉
鼻子：高挺鼻梁, 直挺有型, 中等大小
嘴巴：樱桃小嘴, 薄唇, 唇形精致
眉毛：柳叶眉, 细长上挑, 妩媚动人
轮廓：瓜子脸, 下巴尖锐, 妩媚精致
皮肤：白皙肤色, 细腻光滑, 自然光泽
体型：纤瘦苗条, 腰肢纤细, 仙女线条
综合描述：一位妖媚妩媚的女配, 风情万种, 美艳动人, 致命诱惑
服装：中国古装, 仙侠武侠风
摄影：佳能 EOS R5 85mm f/1.4 人像镜头, 真实皮肤微纹理
要求：人像写真, 自然光, 真实质感, 8K 高清, 抓拍随意感, 真实毛孔, 自然不对称
避免：塑料感皮肤, 蜡像感, 卡通比例, 过度磨皮, 对称完美脸, AI 生成同质化脸, 影楼美化, 千篇一律的网红脸
```

Kling 是快手（Kuaishou）训练的中文模型，对中文原生 prompt 支持优于英文。Follow-up 072 之前的 `(中文)` 失败问题是 **English 主体内 parens-CJK 切换**触发的 tokenizer 边界问题，**纯中文** prompt 没有这个问题。

## Required moves

### 1. New file: `libs/infrastructure/writers/actor__chinese_prompt.py` (per SRP)

One file, one concern — the Chinese prompt builder. Contains:

- **7 Chinese variance pools** (≥ 20 entries each, covering 大小 / 形状 / 颜色 / 神态 dimensions per pool):
  - `_EYES_ZH` (22): 大/小/圆/细长 + 单/双眼皮 + 桃花/丹凤/鹿/狐/卧蚕/凤/杏 + 含情/锐利/温婉/凌厉/忧郁/明亮/凌厉
  - `_NOSE_ZH` (22): 高挺/驼峰/蒜头/挺直/小巧/挺拔/鹰钩/塌/宽鼻翼/窄/精雕/K-beauty 标准 + 大小 + 形状
  - `_LIPS_ZH` (22): 樱桃小嘴/薄/厚/丰满嘟嘴/咬唇/温和/嘟嘟/性感丰唇/古典樱唇 + 唇形 + 厚度
  - `_BROW_ZH` (22): 剑/柳叶/远山/卧蚕/细弯/浓/淡/上挑/平直/弯月/古典蛾眉/羽毛 + 粗细 + 弧度
  - `_CONTOUR_ZH` (22): 方/V字/鹅蛋/圆/瓜子/国字/心形/长/短/婴儿肥/骨感/刀削 + 颧骨高低 + 脸型
  - `_SKIN_ZH` (22): 颜色 (白皙/小麦/古铜/瓷白/蜜糖/象牙/焦糖/深棕/乌黑/橄榄/麦色/古典藕色) + 质地 (玻璃/水光/哑光/婴儿肌/雀斑/沧桑)
  - `_BODY_ZH` (22): **新增体型池** — 高矮 (高挑修长/中等/娇小玲珑/高大魁梧) + 胖瘦 (纤瘦/丰满/骨感/健硕/匀称/曲线/圆润福态/瘦削)
  - `_PHOTOGRAPHY_ZH` (10): 中文相机 cue (佳能 EOS R5 / 索尼 A7 IV / 富士 X-T5 / 哈苏中画幅 / 柯达 Portra 400 / 徕卡 M11 / iPhone 15 Pro …)

- **Archetype-keyed Chinese synthesis** (`_SYNTHESIS_BY_ARCHETYPE`): 10 entries mapping each of the existing archetype slugs (`leading_hero` / `femme_fatale` / etc.) to a one-line 综合描述 (e.g. `"一位妖媚妩媚的女配, 风情万种, 美艳动人, 致命诱惑"`).

- **Body-type bias map** (`_BODY_BIAS_BY_ARCHETYPE`): 10 entries narrowing 体型 to fit the archetype while leaving 8+ candidate indices per slot. `leading_hero` → 高挑/魁梧/健硕/欧巴/瘦削挺拔/高瘦冷峻; `femme_fatale` → 高挑/纤瘦/丰满/曲线/娇媚/高瘦冷峻; `ingenue_kind` → 娇小/纤瘦/娇媚柔弱/匀称; etc. The 25% wild-card fallthrough from follow-up 074 is preserved.

- **Builder functions**:
  - `build_face_prompt(attrs_dict, seed, archetype) -> str` — emits the 13-line structured Chinese face prompt above
  - `build_body_prompt(attrs_dict, seed, archetype) -> str` — same structure, body-shot specifics (姿态 / 灰色 T 恤 + 黑色运动短裤 industry-standard wardrobe / 9:16 full-figure framing) preserved from follow-up 052; `_BODY_BIAS_BY_ARCHETYPE` shapes the 体型 line

Pure deterministic — same `(seed, archetype)` reproduces the same draw, so the face + body images for one actor share the same identity-anchor (五官 + 体型 + 综合描述).

### 2. `actor__writer.py`: delegate `_build_face_prompt` + `_build_body_prompt` to the Chinese builder

Both static methods on `ActorPool` now have signatures `(attrs: ActorAttrs, seed: int, archetype: str | None)` and delegate via `from libs.infrastructure.writers.actor__chinese_prompt import build_face_prompt / build_body_prompt`. The English `Variance` machinery (`_VARIANCE_*` pools + `_variance_for` + `_ARCHETYPE_FEATURE_BIAS` + `_pick_biased` + `_LOOK_ENRICHED`) is now dead code as far as wire-prompt content goes. Kept in source (not removed) for legacy reference and minimal-blast-radius this turn.

### 3. Call-site updates (4 places)

`preview_prompts` / `preview_diverse_prompts` / `generate_batch` / `generate_diverse_batch` each lose the `variance = _variance_for(...)` line and pass `seed + archetype` directly to the two builders:

```python
# was:
variance = _variance_for(seed, attrs.gender, archetype=archetype)
face_prompt = self._build_face_prompt(attrs, variance)
body_prompt = self._build_body_prompt(attrs, variance)
# is:
face_prompt = self._build_face_prompt(attrs, seed, archetype)
body_prompt = self._build_body_prompt(attrs, seed, archetype)
```

For diverse-mode sites the archetype source is `spec.slug`; for standard-mode sites it's the `archetype` kwarg threaded from the command. Both unchanged in behavior — the change is just *what* the prompt content looks like, not *which* archetype it gets.

### 4. `_CJK_PARENS_RE` strip kept but no longer load-bearing

The strip from follow-up 072 still runs in `_variance_for` for the English path, but the English `Variance.features_text` is no longer fed to Kling (the Chinese builder produces the wire content directly). The strip is now a harmless legacy guard against the old English pool entries' `(中文)` annotations.

## Smoke proof

```
==== femme_fatale face prompt (seed=42) ====
角色描述：东亚 女性，30 岁左右
眼睛：端庄秀眼, 双眼皮, 杏眼, 温柔贤淑
鼻子：小巧鼻型, 精致玲珑, 鼻头微翘
嘴巴：樱桃小嘴, 薄唇, 唇形精致
眉毛：平直眉, 韩式眉, 温柔大气
轮廓：长脸型, 五官立体, 高级感
皮肤：深棕色, 巧克力质感, 性感浑厚
体型：高大魁梧, 健壮型男, 肌肉发达
综合描述：一位妖媚妩媚的女配, 风情万种, 美艳动人, 致命诱惑
服装：中国古装, 仙侠武侠风
摄影：尼康 Z9 105mm f/1.4, 超自然渲染, 不平滑皮肤
要求：人像写真, 自然光, 真实质感, 8K 高清, 抓拍随意感, 真实毛孔, 自然不对称
避免：塑料感皮肤, 蜡像感, 卡通比例, 过度磨皮, 对称完美脸, AI 生成同质化脸, 影楼美化, 千篇一律的网红脸
```

`ActorPool._build_face_prompt` + `ActorPool._build_body_prompt` smoke-tested to delegate correctly. Pytest baseline preserved (18 pass / 5 pre-existing wukong fixture failures). `import apps.api.main` + `import apps.api.asgi` boot clean.

## Out of scope

- **Removing the dead English variance machinery**. Substantial cleanup, would shrink `actor__writer.py` from ~2300 lines toward ~600 lines. Deferred — this turn focused on wire-format change.
- **Per-五官 archetype bias** (e.g., `femme_fatale` should prefer 桃花眼 / 红唇 / 高颧骨 specifically). The Chinese pools currently uniform-random 5 of the 7 sections; only 体型 has archetype bias. The 综合描述 carries the archetype direction so Kling should still produce on-archetype images; tightening the per-五官 bias is a future follow-up if `femme_fatale` outputs aren't consistently 妖艳-coded enough.
- **Frontend prompt-preview UI updates** — the preview pane will now show structured Chinese instead of comma-separated English, which is the user-visible improvement.
- HTTP routes + JSON shapes — byte-identical.

## Acceptance trigger

- `from libs.infrastructure.writers.actor__chinese_prompt import build_face_prompt` works.
- `ActorPool._build_face_prompt(attrs, seed, archetype)` returns a string containing 眼睛：/ 鼻子：/ 嘴巴：/ 眉毛：/ 轮廓：/ 皮肤：/ 体型：/ 综合描述：/ 服装：/ 摄影：/ 避免：.
- Re-running "generate 6 actors" through the UI completes without Kling per-slot 500 errors (the user verifies in the UI; if Kling still rejects, fall-back is to swap the prompt back to English in a future fix).
- Pytest baseline preserved.
