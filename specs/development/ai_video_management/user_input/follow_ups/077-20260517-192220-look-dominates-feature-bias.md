# Follow-up draft 077 — 2026-05-17

User reports that 角色生成预览的 10 个 prompt 跟所选 look 不太相关 — they picked **阴邪** (the 075 user message wrote "淫邪" — same intent, the dropdown slug is `sinister` / 中文标签 阴邪) and the 10 preview prompts all felt generic. User accepts variance in 眼睛大小 / 鼻子形状 / 等细节 ("自由发挥") but the **整体气质** must match the picked look.

## 用户原话

> 在角色生成是，预览显示的prompt跟我所要的有比较大的出入，我在选项中已经选择了要淫邪的，但是预览里的10个prompt都跟淫邪不太相关，你可以在眼睛大小，鼻子形状等等细节自由发挥，但整体需要按我的要求来

## 根因

`libs/infrastructure/writers/actor__chinese_prompt.py` (post-075) 把 face/body prompt 拆成 8 行结构化中文。每行如 `眼睛：{descriptor}` 从 22-条池 **uniform random** 抽。Bias 仅作用于 `体型` 一行（per `_BODY_BIAS_BY_ARCHETYPE`），其它 5 个 五官/skin 池没有 bias。

当用户选 `look=sinister`：
1. `_classify_actor_attrs(attrs)` 走 `_ARCHETYPES` 严格 tuple 匹配，需要 `gender + age_range + look + style` **全部命中** 才返回非-`everyman` slug。当 age/style 是 🎲 随机 时，命中 `villain_cold` 的概率约 4/15 × 4/7 ≈ **15%**；其余 85% 落到 `everyman` 兜底。
2. 即使命中 `villain_cold`，输出 prompt 里**只有 `综合描述` 一行** 反映 archetype（"一位阴鸷冷峻的反派男配..."）。剩下 7 行（眼睛 / 鼻子 / 嘴巴 / 眉毛 / 轮廓 / 皮肤 / 摄影）全部 uniform random。
3. 池里**确实有** 阴邪向 descriptors（`凌厉眼神, 单眼皮, 凤眼, 杀气凛然` / `挑眉冷峻, 凌厉如刀, 杀手气场` / `薄唇紧抿, 唇线分明, 高冷气质` 等），但 uniform 抽到的概率太低 — 10 个 prompt 跑下来大多是 `大眼睛 + 桃花眼 + 樱桃小嘴 + 弯月眉` 之类与 sinister 无关的组合。

整体效果：用户感觉所选 look 完全没体现。

## 修复

### 1. 新 `_LOOK_FEATURE_BIAS_ZH` map — 五官 + 轮廓 + 体型 全部按 look bias

5 个 character-archetype look (`righteous` / `sinister` / `seductive` / `cunning` / `innocent`) 各自有一份 bias 子集。Index 是 075 池子内的位置（眼睛 0..21，鼻子 0..21，嘴巴 0..21，眉毛 0..21，轮廓 0..21，体型 0..21）。Bias 子集挑选标准：descriptor 文字里含 look 主题的关键词或近义词（如 sinister → 凌厉 / 杀气 / 冷峻 / 阴险 / 锐利）。

```python
_LOOK_FEATURE_BIAS_ZH: dict[str, dict[str, tuple[int, ...]]] = {
    "sinister": {
        "eyes":    (1, 4, 7, 10, 14, 21),      # 丹凤/狐眼/凤眼凌厉/锐利鹰眼/睥睨众生
        "nose":    (0, 1, 7, 9, 18),           # 高挺/驼峰/鹰钩/威严鹰勾
        "lips":    (3, 14, 20),                # 薄唇紧抿/棱角/似笑非笑
        "brow":    (7, 18, 20),                # 上挑眉/高挑眉峰/挑眉冷峻
        "contour": (5, 7, 9, 10, 15, 17, 19),  # 国字/长脸/突出下巴/高颧骨/不对称/骨感/刀削
        "body":    (0, 3, 7, 9, 17, 20),       # 高挑/魁梧/健硕/瘦削挺拔/高瘦冷峻
    },
    "seductive": {
        "eyes":    (0, 4, 8, 13, 16, 19),      # 桃花含情/狐眼妩媚/灵动桃花/明眸/妩媚眼波/猫眼
        "nose":    (10, 12, 14, 16, 20),       # 挺拔古典/窄鼻模特/细长灵动/精雕/韩式
        "lips":    (1, 5, 6, 9, 11, 12, 16),   # 厚唇性感/古典美人/妩媚妖艳/咬唇/丰唇/超模/致命诱惑
        "brow":    (1, 7, 11, 13, 14, 15),     # 柳叶妩媚/上挑/修长俏皮/细眉韩范/羽毛/古典蛾眉
        "contour": (1, 4, 6, 10, 12, 13, 17, 20),  # V字/瓜子妩媚/心形/高颧骨/宽颧骨/窄脸古典/骨感/韩式小脸
        "body":    (0, 4, 5, 12, 15, 19, 20),  # 高挑/纤瘦/丰满/曲线/长腿细腰/娇媚柔弱
    },
    "righteous": {
        "eyes":    (5, 9, 14, 17, 20),         # 大眼明亮/沉静温润/锐利鹰眼王者/古典凤眼/端庄秀眼
        "nose":    (0, 4, 6, 10, 11, 19, 21),  # 高挺/挺直/中等端正/挺拔/圆润儒雅/古典直鼻/中正
        "lips":    (2, 4, 14, 17, 19),         # 宽阔大笑/温柔贤淑/棱角男性/清秀大家闺秀/端正稳重
        "brow":    (0, 3, 5, 8, 10, 12, 16, 18),  # 剑眉/卧蚕硬朗/浓眉/平直韩式/剑眉星目/粗眉中性/浓眉江湖/高挑王者
        "contour": (0, 2, 5, 9, 14),           # 方下颌/鹅蛋经典/国字/突出下巴阳刚/对称完美
        "body":    (0, 1, 3, 7, 9, 15, 18),    # 高挑/中等/魁梧/健硕/壮硕/标准/运动型
    },
    "cunning": {
        "eyes":    (1, 4, 19, 21),             # 丹凤锐利/狐眼/猫眼调皮/睥睨众生
        "nose":    (1, 7, 9, 16),              # 驼峰/鹰钩/鹰钩锐利/精雕
        "lips":    (3, 20),                    # 薄唇紧抿/似笑非笑
        "brow":    (7, 11, 20),                # 上挑凌厉/修长俏皮/挑眉杀手
        "contour": (4, 7, 10, 13, 15, 17),     # 瓜子妩媚/长脸/高颧骨/窄脸/不对称/骨感
        "body":    (0, 11, 14, 15, 17, 20),    # 高挑/欧巴/标准/长腿细腰/瘦削挺拔/高瘦冷峻
    },
    "innocent": {
        "eyes":    (0, 2, 3, 5, 6, 11, 12, 13, 15, 18, 19, 20),  # 桃花含情/鹿眼/杏眼温婉/大眼明亮/笑眼/水汪汪/泪眼/明眸/清澈/婴儿眼袋/猫眼/端庄秀
        "nose":    (2, 3, 5, 6, 8, 11, 13, 14, 15, 17),  # 蒜头/小巧/翘鼻/中等/塌鼻/圆润儒雅/宽鼻憨厚/细长/丰隆/娇小翘鼻
        "lips":    (0, 5, 7, 8, 10, 13, 15, 18, 21),     # 樱桃/古典美人/上翘甜美/嘟嘟萌系/温和邻家/古典樱唇/娇憨/调皮翘嘴/自然清新
        "brow":    (2, 4, 6, 9, 17, 19, 21),             # 远山温柔/细弯古典/淡眉清秀/弯月温婉/低垂忧郁/亲和萌系/温柔细眉
        "contour": (1, 3, 8, 11, 16, 18, 21),            # V字/圆脸童颜/短下巴婴儿/低颧骨/婴儿肥/圆润福气/古典圆脸
        "body":    (1, 2, 4, 10, 14, 16, 19, 21),        # 中等/娇小/纤瘦仙女/婴儿肥萌/标准/邻家/娇媚柔弱/标准
    },
}
```

8 个物理 look (`handsome` / `beautiful` / `cute` / `mature` / `rugged` / `soft` / `aristocratic` / `fierce`) 暂不加 bias — 这些已经覆盖在 archetype 表里，且用户没明说"画风跟它们也不对劲"。Out of scope for this follow-up.

### 2. 新 `_LOOK_OVERLAY_ZH` map — 在 `综合描述` 之后追加一行 `气质：xxx` 直接复述 look 主题

```python
_LOOK_OVERLAY_ZH: dict[str, str] = {
    "righteous": "正气凛然, 浩然正气, 不怒自威, 一身正派之气",
    "sinister":  "阴邪冷峻, 似笑非笑, 隐含杀机, 城府难测, 阴险毒辣之气",
    "seductive": "妩媚妖艳, 风情万种, 眼波流转, 含情脉脉, 致命诱惑之气",
    "cunning":   "狡诈精明, 算计深沉, 嘴角邪魅, 眼神精明, 城府深算之气",
    "innocent":  "天真烂漫, 纯真无邪, 清澈如水, 不谙世事, 邻家亲切之气",
}
```

只对这 5 个 look 触发（`.get(look)` returns None for the other 8 physical looks → 不追加 `气质` 行，prompt 形状向后兼容）。

### 3. `build_face_prompt` + `build_body_prompt` 切换到 `_pick_biased`

`attrs["look"]` 已经在 attrs dict 内 — 不需要改 signature。两 builder 内：

```python
look = attrs.get("look", "")
look_bias = _LOOK_FEATURE_BIAS_ZH.get(look, {})
body_bias = look_bias.get("body") or _BODY_BIAS_BY_ARCHETYPE.get(archetype or "")
overlay = _LOOK_OVERLAY_ZH.get(look)

lines = [
    f"正面全身定妆照（{头部/形体}对焦）：{ethn} {gender}，{age}",
    f"眼睛：{_pick_biased(rng, _EYES_ZH,    look_bias.get('eyes'))}",
    f"鼻子：{_pick_biased(rng, _NOSE_ZH,    look_bias.get('nose'))}",
    f"嘴巴：{_pick_biased(rng, _LIPS_ZH,    look_bias.get('lips'))}",
    f"眉毛：{_pick_biased(rng, _BROW_ZH,    look_bias.get('brow'))}",
    f"轮廓：{_pick_biased(rng, _CONTOUR_ZH, look_bias.get('contour'))}",
    f"皮肤：{_pick(rng, _SKIN_ZH)}",   # 保留 uniform — 075 + 074 都明说皮肤要跨-archetype 多样
    f"体型：{_pick_biased(rng, _BODY_ZH,    body_bias)}",
    f"综合描述：{_synthesis_for(archetype)}",
]
if overlay:
    lines.append(f"气质：{overlay}")
lines.extend([..., 姿态 / 服装 / 画面 / 摄影 / _CASTING_REQUIREMENTS_ZH / _NEGATIVES_ZH])
```

`_pick_biased` 已经有 `_BIAS_WILD_PROB = 0.25` 的 wild-card fallthrough — 即使 bias 有值，25% 概率仍从全池抽。**这正是用户要的"细节自由发挥"** — 6 个 五官-轮廓-体型 bias 全部命中的概率 = `0.75^6 ≈ 18%`，绝大多数 actor 至少有 1-2 个 wild-card feature 打破完全 same-look，但整体气质 + 综合描述 + 气质 overlay 三层叠加，保证用户看 10 个 prompt 都能感受到所选 look。

### 4. 不影响 8 个物理 look 的现有行为

`look_bias = {}` → 所有 `look_bias.get(...)` 返 `None` → `_pick_biased` 退化为 `_pick` (uniform) → 输出 byte-identical to pre-077。仅 `look ∈ {righteous, sinister, seductive, cunning, innocent}` 触发新行为。

## 不在本 follow-up 范围

- 不动 archetype tuple 匹配的 fall-through 逻辑 (075 已加 `_classify_actor_attrs` 兜底，这里靠 look bias 把缺位补齐 — 互补不冲突).
- 不收紧 `_classify_actor_attrs`（不强行把 look=sinister 都映射到 villain_cold，因为 fem-sinister 没有专门 archetype — 让 archetype 走老路径，look bias 兜底）。
- 不加 8 个物理 look 的 bias（用户没要求；现有覆盖通过 archetype 已经足够）。
- 不动 `_BODY_BIAS_BY_ARCHETYPE` — 当 look bias 提供 body 时优先；否则保留 archetype body bias。
- 不动 `_SKIN_ZH` bias — 075/074 明确皮肤跨-archetype 多样化是 feature，不是 bug。
- 不动 sidecar / `_build_sidecar` — `look` + `archetype` 字段都已经记录。
- 不动 HTTP routes + JSON shapes (byte-identical)。
- 不动 frontend（用户报的是 backend prompt 内容问题；UI 选项已就位 per 064）。

## Acceptance trigger

- `_LOOK_FEATURE_BIAS_ZH` 字典 keyed by 5 character-look slugs，每 slug 6 个 pool 都有非空 tuple。
- `_LOOK_OVERLAY_ZH` 字典 keyed by 同 5 slugs，每条 ≥ 10 个中文字。
- `build_face_prompt({look="sinister", ...}, seed, archetype)` 输出包含 `气质：阴邪...` 行；连续 30 个 seed 跑下来 ≥ 24/30 prompts 的眼睛/嘴巴/眉毛 descriptor 含 (凌厉 | 杀气 | 冷峻 | 阴险 | 锐利 | 似笑非笑 | 棱角 | 上挑 | 鹰 | 狐眼 | 凤眼 | 睥睨) 任一关键词。
- `build_face_prompt({look="handsome", ...}, seed, archetype)` 输出与 pre-077 byte-identical（uniform 行为不变）。
- Pytest baseline preserved (18 pass / 5 pre-existing wukong fixture failures).
- Discovery note (out of scope, not fixed): `actor__writer.py` + `actor__chinese_prompt.py` 都有 "Per follow-up 076" 引用但 follow-up 076 文件不存在。属于历史遗留 — 未来一次回填可写一个 076 entry 描述 075 之后 wardrobe + comp-card full-body framing + classify-actor-attrs fall-through 这三处实改动。本 follow-up 不回填。
