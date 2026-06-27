"""中文 actor prompt builder for Kling.

Per follow-up 075: 用户要求 actor generation 的 prompt 全部用中文，按固定结构
输出 — 眼睛：{大小}, {形状}, {...} / 鼻子：... / 嘴巴：... /
轮廓：... / 皮肤：{颜色}, {质地}, ... / 体型：{高矮}, {胖瘦}, ... / 综合描述：
{archetype 风韵} / 摄影：{...}。

Kling 由快手 (Kuaishou) 制造，对中文 prompt 支持优于英文。Follow-up 072 之前
的失败仅因 ` (中文)` 混在英文 prompt 里破坏 tokenizer；纯中文 prompt 没有
parens-语言切换问题。

Per SRP (follow-up 068): 此文件只做一件事 — 生成中文 prompt。Pool tuples
和 builder 函数都在这里；不混任何 writer/reader/exception 关注点。
"""
from __future__ import annotations

import random


# ============================================================================
# 五官 + 皮肤 + 体型 池 — 每池 ≥ 20 条覆盖大小/形状/颜色多维度
# ============================================================================


_EYES_ZH: tuple[str, ...] = (
    "大眼睛, 双眼皮, 桃花眼, 含情脉脉",
    "细长眼, 单眼皮, 丹凤眼, 神情锐利",
    "圆眼, 双眼皮, 鹿眼, 童真清澈",
    "中等大小, 内双, 杏眼, 温婉柔和",
    "小眼睛, 单眼皮, 狐眼, 妩媚妖艳",
    "大眼睛, 双眼皮, 圆眼, 明亮有神",
    "细眯眼, 卧蚕饱满, 笑眼弯弯, 邻家亲切",
    "深邃眼眸, 双眼皮, 凤眼, 凌厉冷峻",
    "灵动大眼, 双眼皮, 桃花眼, 风情万种",
    "沉静眼神, 卧蚕明显, 杏眼, 温润如玉",
    "凌厉眼神, 单眼皮, 凤眼, 杀气凛然",
    "水汪汪大眼, 双眼皮, 圆眼, 楚楚动人",
    "忧郁眼神, 双眼皮, 泪眼, 惹人怜爱",
    "明眸善睐, 双眼皮, 桃花眼, 含羞带怯",
    "锐利鹰眼, 单眼皮, 细长眼, 王者霸气",
    "清澈眼神, 双眼皮, 大眼, 纯真无邪",
    "妩媚眼波, 桃花眼, 上挑眼角, 风韵犹存",
    "古典凤眼, 单眼皮, 眉目如画, 端庄秀美",
    "婴儿肥眼袋, 卧蚕明显, 笑容可掬, 童颜",
    "猫眼上挑, 双眼皮, 灵动调皮, 俏皮可人",
    "端庄秀眼, 双眼皮, 杏眼, 温柔贤淑",
    "睥睨众生, 凤眼上挑, 冷艳孤高, 不可一世",
)


_NOSE_ZH: tuple[str, ...] = (
    "高挺鼻梁, 直挺有型, 中等大小",
    "驼峰鼻, 鼻梁有弧度, 立体感强",
    "蒜头鼻, 鼻头圆润, 鼻翼宽阔",
    "小巧鼻型, 精致玲珑, 鼻头微翘",
    "挺直鼻梁, 山根高耸, 鼻翼适中",
    "小巧翘鼻, 微微上翘, 俏皮可爱",
    "中等鼻型, 端正大方, 鼻头圆润",
    "高鼻梁, 鼻尖微钩, 立体精致",
    "塌鼻梁, 鼻翼略宽, 亲切可亲",
    "鹰钩鼻, 鼻梁微突, 锐利威严",
    "挺拔鼻梁, 鼻头精致, 古典美感",
    "圆润鼻头, 鼻梁中等, 温和儒雅",
    "窄鼻梁, 高挺笔直, 模特鼻",
    "宽鼻翼, 鼻梁低矮, 朴实憨厚",
    "细长鼻型, 鼻尖微翘, 灵动可人",
    "丰隆鼻, 鼻梁饱满, 福气满满",
    "精雕鼻型, 比例完美, 立体分明",
    "娇小翘鼻, 短俏可爱, 童颜",
    "威严鹰勾, 鼻梁高耸, 王者气场",
    "古典直鼻, 端庄秀美, 江南风韵",
    "韩式标准鼻, 直挺立体, K-beauty",
    "中正鼻型, 不偏不倚, 端正大气",
)


_LIPS_ZH: tuple[str, ...] = (
    "樱桃小嘴, 薄唇, 唇形精致",
    "丰满嘟嘴, 厚唇, 性感诱人",
    "宽阔嘴型, 中等厚度, 大笑灿烂",
    "薄唇紧抿, 唇线分明, 高冷气质",
    "中等嘴型, 上薄下厚, 温柔贤淑",
    "娇小红唇, 唇珠明显, 古典美人",
    "厚唇丰润, 唇色玫瑰, 妩媚妖艳",
    "上翘嘴角, 笑容甜美, 阳光开朗",
    "嘟嘟嘴, 唇形可爱, 萌系少女",
    "咬唇微笑, 唇珠清晰, 楚楚动人",
    "温和微笑, 唇色淡雅, 邻家女孩",
    "厚唇半启, 露齿微笑, 热情奔放",
    "性感丰唇, 上下均匀, 国际超模",
    "古典樱唇, 小巧饱满, 江南闺秀",
    "棱角分明, 唇线清晰, 男性化",
    "娇憨小嘴, 嘟嘟可爱, 童颜萌妹",
    "妩媚红唇, 性感丰满, 致命诱惑",
    "清秀薄唇, 端庄秀美, 大家闺秀",
    "调皮翘嘴, 上扬嘴角, 灵动俏皮",
    "端正大方, 中等厚度, 端庄稳重",
    "嘴角微翘, 似笑非笑, 神秘莫测",
    "厚薄适中, 唇色健康, 自然清新",
)


_CONTOUR_ZH: tuple[str, ...] = (
    "方下颌, 棱角分明, 颧骨适中",
    "V字脸, 下巴尖, 瓜子脸",
    "鹅蛋脸, 五官端正, 经典美人脸",
    "圆脸, 苹果肌饱满, 童颜可爱",
    "瓜子脸, 下巴尖锐, 妩媚精致",
    "国字脸, 方正大气, 男性硬朗",
    "心形脸, 下颌纤细, 上额饱满",
    "长脸型, 五官立体, 高级感",
    "短下巴, 圆润可爱, 婴儿脸",
    "突出下巴, 棱角硬朗, 阳刚之气",
    "高颧骨, 立体感强, 模特脸",
    "低颧骨, 平和柔和, 温柔气质",
    "宽颧骨, 性感诱惑, 国际超模",
    "窄脸, 精致玲珑, 古典美人",
    "对称脸型, 完美比例, 经典美感",
    "不对称特色, 个性鲜明, 独特韵味",
    "婴儿肥, 苹果肌饱满, 萌系少女",
    "骨感脸型, 颧骨突出, 时尚硬朗",
    "圆润脸庞, 颊肉饱满, 富态福气",
    "刀削脸, 棱角分明, 江湖侠客",
    "韩式小脸, V字精致, 上镜",
    "古典圆脸, 福气满满, 大家闺秀",
)


_SKIN_ZH: tuple[str, ...] = (
    "白皙肤色, 细腻光滑, 自然光泽",
    "小麦色, 健康活力, 阳光气息",
    "古铜色, 性感野性, 健美有型",
    "瓷白透亮, 玻璃感肌肤, 韩式护肤",
    "蜜糖色, 温暖通透, 自然光感",
    "象牙白, 冷调高级感, 贵族气质",
    "焦糖色, 深邃迷人, 异域风情",
    "深棕色, 巧克力质感, 性感浑厚",
    "乌黑健康, 黝黑发亮, 阳光男孩",
    "白里透红, 健康气色, 自然红润",
    "奶白细腻, 婴儿肌肤, 嫩滑无瑕",
    "橄榄色, 地中海风情, 异域美人",
    "麦色健康, 中性肤色, 大众友好",
    "褐色暖调, 自然质朴, 邻家亲切",
    "古典藕色, 江南水乡, 温润如玉",
    "哑光磨砂, 滋润保湿, 高级哑光感",
    "水光肌, 莹润剔透, 韩式光感",
    "自然毛孔, 真实细节, 写实质感",
    "雀斑点点, 自然俏皮, 法式可爱",
    "沧桑皱纹, 岁月痕迹, 故事感",
    "婴儿肌, 嫩滑无瑕, 童颜光感",
    "健康麦色, 户外晒痕, 阳光味",
)


_BODY_ZH: tuple[str, ...] = (
    "高挑修长, 模特身材, 腿长腰细",
    "中等身高, 比例匀称, 健康标准",
    "娇小玲珑, 萌妹身材, 小巧可爱",
    "高大魁梧, 健壮型男, 肌肉发达",
    "纤瘦苗条, 腰肢纤细, 仙女线条",
    "丰满圆润, 性感曲线, 沙漏身材",
    "骨感清瘦, 苗条细长, 衣架子",
    "健硕肌肉, 腹肌分明, 健身房型",
    "匀称丰腴, 不胖不瘦, 健康标准",
    "魁梧壮硕, 肩宽腰窄, 强壮有力",
    "娇小可爱, 婴儿肥, 萌系少女",
    "颀长清瘦, 长腿欧巴, 偶像身材",
    "曲线玲珑, 凹凸有致, 妙曼身姿",
    "圆润福态, 富态丰盈, 富贵气场",
    "标准身材, 健康匀称, 大众友好",
    "长腿细腰, 模特身材, 时尚气场",
    "健康丰满, 阳光开朗, 邻家形态",
    "瘦削挺拔, 骨节分明, 文艺范",
    "运动型身材, 肌肉线条, 健美阳光",
    "娇媚柔弱, 弱不禁风, 古典美人",
    "高瘦冷峻, 衣架子, 时尚酷感",
    "标准身材, 健康匀称, 中等胖瘦",
)


# ============================================================================
# Archetype → 综合描述 + 形体倾向
# ============================================================================


_SYNTHESIS_BY_ARCHETYPE: dict[str, str] = {
    "leading_hero":    "一位气场冷峻的男主, 英俊挺拔, 不怒自威, 王者风范",
    "leading_warm":    "一位温润如玉的男主, 翩翩公子, 温柔儒雅, 谦谦君子",
    "ingenue_kind":    "一位清纯善良的女主, 温婉可人, 眉目含情, 邻家女孩",
    "ingenue_lively":  "一位娇俏灵动的女主, 活泼可爱, 灵气逼人, 少女感十足",
    "femme_fatale":    "一位妖媚妩媚的女配, 风情万种, 美艳动人, 致命诱惑",
    "villain_cold":    "一位阴鸷冷峻的反派男配, 阴险狡诈, 城府极深, 杀气凛然",
    "sage_elder":      "一位德高望重的长辈宗师, 鹤发童颜, 慈眉善目, 气度非凡",
    "martial_drifter": "一位江湖侠客, 行走江湖, 风餐露宿, 一身侠气",
    "everyman":        "一位市井百姓, 朴实无华, 邻家亲切, 烟火气十足",
    "youth_fresh":     "一位清俊少年, 朝气蓬勃, 青春活力, 阳光开朗",
}


# Body-type bias per archetype — narrows 形体 to fit the archetype while still
# leaving room for diversity (each archetype gets 8+ candidate indices).
_BODY_BIAS_BY_ARCHETYPE: dict[str, tuple[int, ...]] = {
    "leading_hero":    (0, 3, 7, 9, 11, 15, 18, 20),   # 高挑/魁梧/健硕/欧巴/瘦削挺拔/高瘦冷峻
    "leading_warm":    (0, 1, 4, 11, 14, 15, 17),       # 高挑修长/中等匀称/纤瘦/欧巴/文艺
    "ingenue_kind":    (1, 2, 4, 10, 16, 19, 21),       # 娇小/纤瘦/娇媚柔弱/匀称
    "ingenue_lively":  (1, 2, 10, 14, 16),               # 中等/娇小/婴儿肥/邻家
    "femme_fatale":    (0, 4, 5, 12, 15, 19, 20),       # 高挑/纤瘦/丰满/曲线/娇媚/高瘦冷峻
    "villain_cold":    (0, 3, 7, 9, 17, 20),             # 高挑/魁梧/健硕/瘦削/冷峻
    "sage_elder":      (1, 8, 13, 14),                    # 匀称丰腴/福态/中等
    "martial_drifter": (0, 3, 7, 9, 17),                  # 高挑/魁梧/健硕
    "everyman":        (1, 8, 14, 16, 21),                # 中等/匀称/邻家
    "youth_fresh":     (0, 1, 4, 11, 14, 17),             # 高挑/中等/纤瘦/欧巴
}


_BIAS_WILD_PROB: float = 0.25
"""Per follow-up 074 carried into 075: 25% 概率 ignore body bias 走 uniform —
within-archetype 形体 variety 保持。Follow-up 077 把同 wild-prob 复用到
look bias（眼睛 / 鼻子 / 嘴巴 / 轮廓） — 用户接受"细节自由发挥"，
6 个 feature 全命中 bias 的概率 = 0.75^6 ≈ 18%，绝大多数 actor 至少有
1-2 个 wild-card feature，但整体气质仍由 bias 主导。"""


# ============================================================================
# Look → 五官 / 轮廓 / 体型 bias + overlay  (follow-up 077)
# ============================================================================
#
# Per follow-up 077: 用户报 look=sinister 时 10 个 preview prompt 跟所选
# look 不太相关。根因是 075 后 face/body builder 仅 body 一行按 archetype
# bias，其余 五官 全部 uniform 随机抽 — 即使 archetype 命中 villain_cold，
# 综合描述一行也压不住 7 行 uniform 随机的 face descriptor。
#
# 5 个 character-archetype look 各自有 6 个 pool 的 bias index 子集；非这
# 5 个 look 时 bias dict 为空 — `_pick_biased` 退化为 uniform，与 pre-077
# byte-identical。

_LOOK_FEATURE_BIAS_ZH: dict[str, dict[str, tuple[int, ...]]] = {
    "sinister": {
        "eyes":    (1, 4, 7, 10, 14, 21),
        "nose":    (0, 1, 7, 9, 18),
        "lips":    (3, 14, 20),
        "contour": (5, 7, 9, 10, 15, 17, 19),
        "body":    (0, 3, 7, 9, 17, 20),
    },
    "seductive": {
        "eyes":    (0, 4, 8, 13, 16, 19),
        "nose":    (10, 12, 14, 16, 20),
        "lips":    (1, 5, 6, 9, 11, 12, 16),
        "contour": (1, 4, 6, 10, 12, 13, 17, 20),
        "body":    (0, 4, 5, 12, 15, 19, 20),
    },
    "righteous": {
        "eyes":    (5, 9, 14, 17, 20),
        "nose":    (0, 4, 6, 10, 11, 19, 21),
        "lips":    (2, 4, 14, 17, 19),
        "contour": (0, 2, 5, 9, 14),
        "body":    (0, 1, 3, 7, 9, 15, 18),
    },
    "cunning": {
        "eyes":    (1, 4, 19, 21),
        "nose":    (1, 7, 9, 16),
        "lips":    (3, 20),
        "contour": (4, 7, 10, 13, 15, 17),
        "body":    (0, 11, 14, 15, 17, 20),
    },
    "innocent": {
        "eyes":    (0, 2, 3, 5, 6, 11, 12, 13, 15, 18, 19, 20),
        "nose":    (2, 3, 5, 6, 8, 11, 13, 14, 15, 17),
        "lips":    (0, 5, 7, 8, 10, 13, 15, 18, 21),
        "contour": (1, 3, 8, 11, 16, 18, 21),
        "body":    (1, 2, 4, 10, 14, 16, 19, 21),
    },
}


_LOOK_OVERLAY_ZH: dict[str, str] = {
    "righteous": "正气凛然, 浩然正气, 不怒自威, 一身正派之气",
    "sinister":  "阴邪冷峻, 似笑非笑, 隐含杀机, 城府难测, 阴险毒辣之气",
    "seductive": "妩媚妖艳, 风情万种, 眼波流转, 含情脉脉, 致命诱惑之气",
    "cunning":   "狡诈精明, 算计深沉, 嘴角邪魅, 眼神精明, 城府深算之气",
    "innocent":  "天真烂漫, 纯真无邪, 清澈如水, 不谙世事, 邻家亲切之气",
}


# ============================================================================
# Helpers
# ============================================================================


def _pick(rng: random.Random, pool: tuple[str, ...]) -> str:
    return rng.choice(pool)


def _is_character_look(look: str) -> bool:
    """True for the 5 character-archetype looks that carry a curated feature
    bias (`_LOOK_FEATURE_BIAS_ZH`): righteous / sinister / seductive / cunning /
    innocent. For these, unselected features are pinned to the archetype subset
    — NO wild-card escape to contradictory descriptors (e.g. `look=sinister`
    must never draw `圆眼, 童真清澈`). The 8 physical-appearance looks carry no
    bias and keep the prior uniform-with-archetype-body behaviour byte-identical.
    """
    return look in _LOOK_FEATURE_BIAS_ZH


def _pick_biased(
    rng: random.Random,
    pool: tuple[str, ...],
    bias_indices: tuple[int, ...] | None,
    wild_prob: float = _BIAS_WILD_PROB,
) -> str:
    if bias_indices and rng.random() >= wild_prob:
        candidates = [pool[i] for i in bias_indices if 0 <= i < len(pool)]
        if candidates:
            return rng.choice(candidates)
    return rng.choice(pool)


# Per follow-up 095: strip pool entries whose descriptor carries a marker that
# unambiguously implies the opposite gender. The original 22-entry pools mix
# neutral and gendered descriptors uniformly; without filtering, a male batch
# pulls a feminine descriptor in ~30-45% of slots per pool, and 7 such pulls
# cumulate to >95% chance of at least one cross-gender leak — enough to push
# Kling toward female rendering even when 性别：男性 is in the prompt header.
_FEMALE_ONLY_MARKERS: tuple[str, ...] = (
    "少女", "女孩", "美人", "闺秀", "佳人", "妩媚", "妖艳", "妖媚",
    "娇憨", "楚楚动人", "致命诱惑", "贤淑", "仕女", "邻家姐姐",
    "萌妹", "娇媚柔弱", "弱不禁风", "婴儿肥",
)

_MALE_ONLY_MARKERS: tuple[str, ...] = (
    "男性化", "男性硬朗", "邻家男孩", "阳光男孩", "健壮型男",
    "长腿欧巴", "偶像身材", "腹肌分明", "魁梧", "强壮有力",
)


def _filter_pool_by_gender(
    pool: tuple[str, ...],
    bias_indices: tuple[int, ...] | None,
    gender_slug: str,
) -> tuple[tuple[str, ...], tuple[int, ...] | None]:
    """Return `(filtered_pool, translated_bias_indices)`. Strip entries whose
    descriptor contains a cross-gender marker; translate `bias_indices` to
    point into the filtered pool (dropping entries that were stripped). If
    every biased entry is stripped, the translated bias is None — caller
    falls through to uniform pick.
    """
    forbidden = _FEMALE_ONLY_MARKERS if gender_slug == "male" else _MALE_ONLY_MARKERS
    new_pool: list[str] = []
    old_to_new: dict[int, int] = {}
    for old_i, descriptor in enumerate(pool):
        if any(m in descriptor for m in forbidden):
            continue
        old_to_new[old_i] = len(new_pool)
        new_pool.append(descriptor)
    if bias_indices is None:
        return tuple(new_pool), None
    translated = tuple(old_to_new[i] for i in bias_indices if i in old_to_new)
    return tuple(new_pool), (translated if translated else None)


def _synthesis_for(archetype: str | None) -> str:
    if archetype and archetype in _SYNTHESIS_BY_ARCHETYPE:
        return _SYNTHESIS_BY_ARCHETYPE[archetype]
    return "一位演员, 真实自然, 富有个性"


def _batch_sample_pool(
    batch_rng: random.Random,
    pool_len: int,
    bias_indices: tuple[int, ...] | None,
    count: int,
    wild_prob: float = _BIAS_WILD_PROB,
    strict: bool = False,
) -> list[int]:
    """Per follow-up 082: deterministic batch-coordinated sampler that returns
    `count` POOL INDICES with no within-batch repeats unless the pool is
    genuinely exhausted (count > pool_len).

    `strict=True` (character-archetype look): never leave the curated bias
    subset — no wild-card slots and no fall-through to the full pool. Picks stay
    unique while the subset lasts, then repeat WITHIN the subset (archetype
    coherence outranks no-repeat). This is what stops a `look=sinister` batch
    from leaking `圆眼, 童真清澈` once the small subset is exhausted.

    Algorithm: bias-preferred + exhaust-then-fall-through + 074 wild-card
    retained at the batch level (~`wild_prob` of slots free-roam the full
    pool for within-archetype variance). Deterministic in
    `(batch_rng state, pool_len, bias_indices, count)` so every parallel
    `count=1` call seeded with the same `batch_seed` recomputes the same
    list and picks its own `slot_index`.
    """
    bias_pool = [i for i in (bias_indices or ()) if 0 <= i < pool_len]
    if strict and bias_pool:
        batch_rng.shuffle(bias_pool)
        picks = list(bias_pool[:count])
        while len(picks) < count:
            picks.append(batch_rng.choice(bias_pool))
        batch_rng.shuffle(picks)
        return picks[:count]
    wild_count = sum(1 for _ in range(count) if batch_rng.random() < wild_prob)
    bias_count = count - wild_count
    batch_rng.shuffle(bias_pool)
    full_pool = list(range(pool_len))
    batch_rng.shuffle(full_pool)
    biased_taken = bias_pool[:bias_count]
    used: set[int] = set(biased_taken)
    fallthrough_needed = bias_count - len(biased_taken)
    fallthrough_pool = [i for i in full_pool if i not in used]
    fallthrough_taken = fallthrough_pool[:fallthrough_needed]
    used.update(fallthrough_taken)
    wild_pool = [i for i in full_pool if i not in used]
    wild_taken = wild_pool[:wild_count]
    used.update(wild_taken)
    picks = biased_taken + fallthrough_taken + wild_taken
    batch_rng.shuffle(picks)
    while len(picks) < count:
        picks.append(batch_rng.choice(range(pool_len)))
    return picks[:count]


def _resolve_batch_picks(
    batch_seed: int,
    batch_size: int,
    slot_index: int,
    look: str,
    archetype: str | None,
    gender_slug: str,
) -> dict[str, str]:
    """Per follow-up 082: return this slot's pre-resolved descriptors for the
    7 face/body pools, coordinated across the batch via `batch_seed`.

    Same `(batch_seed, batch_size)` across all N parallel `count=1` calls
    produces the same per-pool index list — each call independently picks
    `slot_index`'s position. Look bias (077) routes per pool; body falls
    through to archetype bias when look bias absent. Per follow-up 095, each
    pool is gender-filtered via `_filter_pool_by_gender` before sampling so
    a male batch never pulls feminine descriptors (and vice versa).
    """
    if slot_index < 0 or slot_index >= batch_size:
        raise ValueError(
            f"slot_index={slot_index} must be in [0, {batch_size})"
        )
    batch_rng = random.Random(batch_seed)
    look_bias = _LOOK_FEATURE_BIAS_ZH.get(look, {})
    body_bias = look_bias.get("body") or _BODY_BIAS_BY_ARCHETYPE.get(archetype or "")
    # Character-archetype looks pin every biased feature to its curated subset
    # (no contradictory wild-cards / fall-through). The 8 physical looks have no
    # look bias → strict has no effect (body keeps its archetype-bias + wild).
    strict = _is_character_look(look)
    plan: list[tuple[str, tuple[str, ...], tuple[int, ...] | None, bool]] = [
        ("eyes",    _EYES_ZH,    look_bias.get("eyes"),    strict),
        ("nose",    _NOSE_ZH,    look_bias.get("nose"),    strict),
        ("lips",    _LIPS_ZH,    look_bias.get("lips"),    strict),
        ("contour", _CONTOUR_ZH, look_bias.get("contour"), strict),
        ("skin",    _SKIN_ZH,    None,                     False),  # skin stays unbiased (074)
        ("body",    _BODY_ZH,    body_bias,                strict),
    ]
    picks: dict[str, str] = {}
    for key, pool, bias, pool_strict in plan:
        filtered_pool, filtered_bias = _filter_pool_by_gender(pool, bias, gender_slug)
        indices = _batch_sample_pool(
            batch_rng, len(filtered_pool), filtered_bias, batch_size, strict=pool_strict
        )
        picks[key] = filtered_pool[indices[slot_index]]
    return picks


# ============================================================================
# Prompt builders
# ============================================================================


_AGE_ZH: dict[str, str] = {
    "18-25": "22 岁左右",
    "26-35": "30 岁左右",
    "36-50": "42 岁左右",
    "51-65": "58 岁左右",
    "65+":   "70 岁左右",
}

_ETHNICITY_ZH: dict[str, str] = {
    "asian":          "亚洲",
    "east-asian":     "东亚",
    "south-asian":    "南亚",
    "caucasian":      "白人",
    "african":        "非洲",
    "latino":         "拉丁裔",
    "middle-eastern": "中东",
    "mixed":          "混血",
}

_GENDER_ZH: dict[str, str] = {"male": "男性", "female": "女性"}


# Per follow-up 087: _NEGATIVES_ZH is gone. Every negative token now lives
# in `_NEGATIVE_PROMPT_ZH` below and is sent via Kling's dedicated
# `negative_prompt` API field — not stuffed inside the positive prompt
# (which is a diffusion-model anti-pattern: negative tokens in positive
# prompt inject the concept they try to forbid into the model's attention).


_NEGATIVE_PROMPT_ZH: str = (
    # composition negatives (the main half-body fix)
    "portrait, half body, headshot, close-up, head and shoulders, "
    "head-shoulder crop, upper body only, chest up, waist up, "
    "cropped feet, cropped legs, cropped hands, cropped head, "
    "head too large, body too small, "
    # frontal-face lock — face must point straight at camera so facial detail
    # is captured (user req); ban every away-facing head pose.
    "侧脸, 侧面, 半侧脸, 3/4 侧脸, 转头, 扭头, 回头, 低头, 仰头, 脸朝向一侧, "
    "面部转开, 背对镜头, 后脑勺, 不看镜头, 目光偏离镜头, profile view, side face, "
    # photorealism / anti-AI-face (was in old _NEGATIVES_ZH leading list)
    "塑料感皮肤, 蜡像感, 卡通比例, 过度磨皮, 对称完美脸, "
    "AI 生成同质化脸, 影楼美化, 千篇一律的网红脸, "
    # explicit anti-anime / anti-illustration (paired with the positive
    # 风格 realism cue — belt-and-suspenders against Kling drifting toward
    # stylised aesthetics)
    "动漫, 动漫风格, anime, anime style, cartoon, cartoon style, "
    "插画风格, illustration, 二次元, 三维动画, 3D render, "
    # wardrobe-fallback bans (was in old _NEGATIVES_ZH 080 addition)
    "宽松衣物, T 恤, 长裤, 长裙, 大衣, 厚外套, 多层服装, "
    # glamour drift (was in old _NEGATIVES_ZH 080 addition)
    "故意性感姿势, 媚态, 内衣广告, glamour pose, "
    # hairstyle lock — enforce the uniform 寸头 buzz cut (user req 2026-06-14);
    # ban every long / styled / face-obscuring hair variant the positive
    # 发型 line is trying to suppress.
    "长发, 披肩发, 中长发, 刘海, 盘发, 编发, 丸子头, 马尾, 卷发, 头发遮挡面部, 头发遮挡额头, "
    # no scars / disfiguring marks (user req 2026-06-14) — keep faces clean for
    # fair comparison.
    "伤疤, 疤痕, 刀疤, 烧伤痕迹, 纹身, "
    # generic image quality fallbacks
    "blurry, low quality, deformed, extra limbs, wrong proportions"
)


def build_negatives() -> str:
    """Returns the negative-prompt string sent to Kling's `negative_prompt`
    API field. Per follow-up 087 — separate inversion pass keeps these tokens
    out of the positive prompt's attention. Same negatives apply to both
    face + body shots (composition + photorealism + wardrobe-fallback bans
    don't differ between the two shots).
    """
    return _NEGATIVE_PROMPT_ZH


# Per follow-up 100: the closing requirement block (`_CASTING_REQUIREMENTS_ZH`)
# and the positive composition tag (`_POSITIVE_COMPOSITION_TAG`) were the third
# and fourth "全身" repetitions inside the same prompt; combined with the
# header line + the _PHOTOGRAPHY_ZH entries' "全身" word, Kling saw the cue
# four times. Removed — the framing now lives only in the header line at the
# top of each build function. The 9:16 cue is also gone (user sets aspect
# ratio at the Kling-app level, not the prompt level).


def _qi_zhi_for(look: str, archetype: str | None) -> str:
    """气质 = look overlay (richer character flavor) when the look slug carries
    one (`_LOOK_OVERLAY_ZH`); otherwise falls back to the archetype synthesis
    so character-archetype-flavored looks like `righteous` still imprint."""
    if look and look in _LOOK_OVERLAY_ZH:
        return _LOOK_OVERLAY_ZH[look]
    return _synthesis_for(archetype)


# Per follow-up 100: optional "feature-locked" inputs. When set to a concrete
# Chinese string (e.g. "大眼") in attrs, the prompt line shows that exact
# value instead of a pool sample. RANDOM / empty / missing → pool sample.
_RANDOM_TOKENS: frozenset[str] = frozenset({"", "__random__", "random", "随机"})


def _is_random(value: str | None) -> bool:
    return value is None or value in _RANDOM_TOKENS


_HEADER_FACE: str = "全身定妆照（试镜照）, 正脸正面平视镜头（绝不侧脸、不转头、不低头、不仰头，面部完整正对镜头便于捕捉五官细节）, 头顶到脚趾完整入画"
_HEADER_BODY: str = "全身定妆照（试镜照, 形体对焦）, 正脸正面平视镜头（绝不侧脸、不转头、不低头，面部完整正对镜头便于捕捉五官细节）, 双腿略分开半肩宽, 头顶到脚趾完整入画"

# Realism cue — pushes Kling toward live-action photography and away from
# anime / illustrated / "AI face" aesthetics. Sits on its own line so the cue
# carries weight equal to the other structured aspects.
_STYLE_REALISM_ZH: str = "风格：真实人像摄影, 写实风格, 真人模样"

# Wardrobe cue — gender-specific so a male actor never renders in a feminine
# 吊带背心 (spaghetti-strap camisole). Both variants are tight try-out wear that
# reveals body contour (leg shape, 腰臀比, 肩宽); only the top differs by gender —
# male = 无袖运动背心 (athletic tank), female = 吊带背心. Kling keys clothing off
# the explicit garment noun, so the old single neutral line leaked the camisole
# onto men. The same wardrobe line is appended once per prompt by the line
# builders, which pass the actor's gender slug.
_WARDROBE_MALE_ZH: str = (
    "统一白色紧身试镜服（纯白色无袖紧身运动背心【男款圆领运动背心、绝非女式吊带背心】 + 纯白色紧身运动短裤）, "
    "充分展示身材轮廓, "
    "能清晰看出腿型（直腿 / 弯腿 / O型腿 / X型腿）, "
    "大腿内外侧线条, 胸肌与肩背轮廓, 腰臀比例, 肩宽"
)
_WARDROBE_FEMALE_ZH: str = (
    "统一白色紧身试镜服（纯白色紧身吊带背心 + 纯白色紧身短裤）, "
    "充分展示身材轮廓, "
    "能清晰看出腿型（直腿 / 弯腿 / O型腿 / X型腿）, "
    "大腿内外侧线条, 胸型大小, 腰臀比例, 肩宽"
)


def _wardrobe_for(gender_slug: str) -> str:
    """Gender-appropriate try-out wardrobe (male never in 吊带背心)."""
    return _WARDROBE_MALE_ZH if gender_slug == "male" else _WARDROBE_FEMALE_ZH

# Hairstyle cue — uniform buzz cut for EVERY actor regardless of gender (user
# req 2026-06-14). Hair is the single biggest confound when comparing faces in
# a casting pool: long / styled hair reframes the face shape and hides the
# hairline + ears. Forcing 寸头 on both men and women makes the comparison
# purely about the face. Reinforced by the long-hair / bangs bans in
# `_NEGATIVE_PROMPT_ZH`.
_HAIRSTYLE_BUZZCUT_ZH: str = (
    "发型：寸头（均匀贴头皮的极短板寸超短发）, 男女一律相同发型, "
    "完整露出额头、发际线、耳朵与整张脸轮廓, 头发不遮挡面部, 便于公平比对五官"
)


def _structured_lines(
    rng: random.Random,
    attrs: dict[str, str],
    archetype: str | None,
) -> list[str]:
    """The shared body of every prompt, in the order the user spec'd:
    {header line + dropdown selections}
    风格 (写实, 真人) / 眼睛 / 鼻子 / 嘴巴 / 脸型 / 体型 / 皮肤 / 气质 / 服装
    Each aspect appears exactly once; "全身" appears only via the caller's
    header line (face vs body variant). 风格 sits right after the ethnicity/
    gender descriptor to anchor the photorealism cue early; 服装 closes the
    prompt with body-visibility outcome cues (leg shape, 胸型大小, 腰臀比).
    """
    ethn = _ETHNICITY_ZH.get(attrs["ethnicity"], attrs["ethnicity"])
    gender_slug = attrs["gender"]
    gender = _GENDER_ZH.get(gender_slug, gender_slug)
    age = _AGE_ZH.get(attrs["age_range"], attrs["age_range"])
    look = attrs.get("look", "")
    look_bias = _LOOK_FEATURE_BIAS_ZH.get(look, {})
    body_bias = look_bias.get("body") or _BODY_BIAS_BY_ARCHETYPE.get(archetype or "")
    eyes_pool, eyes_bias = _filter_pool_by_gender(_EYES_ZH, look_bias.get("eyes"), gender_slug)
    nose_pool, nose_bias = _filter_pool_by_gender(_NOSE_ZH, look_bias.get("nose"), gender_slug)
    lips_pool, lips_bias = _filter_pool_by_gender(_LIPS_ZH, look_bias.get("lips"), gender_slug)
    contour_pool, contour_bias = _filter_pool_by_gender(_CONTOUR_ZH, look_bias.get("contour"), gender_slug)
    skin_pool, _ = _filter_pool_by_gender(_SKIN_ZH, None, gender_slug)
    body_pool, body_bias_f = _filter_pool_by_gender(_BODY_ZH, body_bias, gender_slug)
    eyes_locked = attrs.get("eyes", "")
    nose_locked = attrs.get("nose", "")
    lips_locked = attrs.get("lips", "")
    face_locked = attrs.get("face", "")
    skin_locked = attrs.get("skin", "")
    body_locked = attrs.get("body", "")
    qi_zhi_locked = attrs.get("qi_zhi", "")
    # Character-archetype looks pin features to the curated subset (wild_prob=0);
    # physical looks keep the 25% wild-card. Body uses the same wild_prob so a
    # character look can't wander, while an archetype-only body keeps its variety.
    wp = 0.0 if _is_character_look(look) else _BIAS_WILD_PROB
    eyes_value = eyes_locked if not _is_random(eyes_locked) else _pick_biased(rng, eyes_pool, eyes_bias, wp)
    nose_value = nose_locked if not _is_random(nose_locked) else _pick_biased(rng, nose_pool, nose_bias, wp)
    lips_value = lips_locked if not _is_random(lips_locked) else _pick_biased(rng, lips_pool, lips_bias, wp)
    face_value = face_locked if not _is_random(face_locked) else _pick_biased(rng, contour_pool, contour_bias, wp)
    skin_value = skin_locked if not _is_random(skin_locked) else _pick(rng, skin_pool)
    body_value = body_locked if not _is_random(body_locked) else _pick_biased(rng, body_pool, body_bias_f, wp)
    qi_zhi_value = qi_zhi_locked if not _is_random(qi_zhi_locked) else _qi_zhi_for(look, archetype)
    # `look` is intentionally NOT included here — its richer Chinese overlay
    # surfaces once via the 气质 line below (per user's "each aspect mentioned
    # once" rule).
    desc_parts = [f"{ethn} {gender}", age]
    return [
        "，".join(desc_parts),
        _STYLE_REALISM_ZH,
        f"眼睛：{eyes_value}",
        f"鼻子：{nose_value}",
        f"嘴巴：{lips_value}",
        f"脸型：{face_value}",
        _HAIRSTYLE_BUZZCUT_ZH,
        f"体型：{body_value}",
        f"皮肤：{skin_value}",
        f"气质：{qi_zhi_value}",
        _wardrobe_for(gender_slug),
    ]


def build_face_prompt(attrs: dict[str, str], seed: int, archetype: str | None) -> str:
    """构造结构化中文 试镜装定妆照 prompt — face emphasis 变体（follow-up 100）.

    Per follow-up 100: collapsed to a single 全身 cue in the header, dropped
    9:16 / 画面 / _CASTING_REQUIREMENTS_ZH / 轮廓 / 综合描述 lines per user
    spec ("only mention each aspect once"). 服装 is universal 试镜装.

    Pure deterministic — same `(seed, archetype, attrs)` reproduces the same
    draw. eyes/skin/body in attrs may carry a user-locked Chinese string;
    otherwise pool sampling fires deterministically off `seed`.
    """
    rng = random.Random(seed)
    body_lines = _structured_lines(rng, attrs, archetype)
    return "\n".join([f"{_HEADER_FACE}，{body_lines[0]}", *body_lines[1:]])


def build_body_prompt(attrs: dict[str, str], seed: int, archetype: str | None) -> str:
    """构造结构化中文 试镜装定妆照 prompt — body emphasis 变体（follow-up 100）.

    与 `build_face_prompt` 共享 `(seed, archetype, attrs)` 抽样以保证身份一致；
    唯一区别是 header 行 (`_HEADER_BODY` 加 "双腿略分开半肩宽 / 形体对焦")。
    """
    rng = random.Random(seed)
    body_lines = _structured_lines(rng, attrs, archetype)
    return "\n".join([f"{_HEADER_BODY}，{body_lines[0]}", *body_lines[1:]])


# ============================================================================
# Batch-coordinated builder variants (follow-up 082)
# ============================================================================
#
# These accept a pre-resolved `picks` dict (see `_resolve_batch_picks`) that
# fixes the 7 face/body pool descriptors so the caller can guarantee no
# within-batch repeats. Photo cue stays per-slot via the existing per-slot
# `seed` (so 10 actors don't all get the same camera/lens — that's batch
# variance noise we want, not pool variance noise we want to suppress).
#
# Pure deterministic in `(seed, archetype, picks)`. Backward-compat:
# `build_face_prompt` / `build_body_prompt` are unchanged and still drive
# legacy `count=1` paths + any caller that doesn't pass batch fields.


def _build_with_picks_lines(
    attrs: dict[str, str],
    seed: int,
    archetype: str | None,
    picks: dict[str, str],
) -> tuple[random.Random, list[str], str]:
    """Shared body lines for batch-coordinated face/body variants.

    Returns `(rng, body_lines, gender_zh)`. The 7 pool draws are sourced from
    `picks` (deterministic across the batch via `_resolve_batch_picks`);
    user-locked eyes/skin/body in `attrs` override the corresponding `picks`
    entry so the dropdown selection always wins. Only the camera cue stays
    per-slot via `rng` (kept that way intentionally — per-slot photo variance
    is what we want).
    """
    rng = random.Random(seed)
    ethn = _ETHNICITY_ZH.get(attrs["ethnicity"], attrs["ethnicity"])
    gender = _GENDER_ZH.get(attrs["gender"], attrs["gender"])
    age = _AGE_ZH.get(attrs["age_range"], attrs["age_range"])
    look = attrs.get("look", "")
    eyes_locked = attrs.get("eyes", "")
    nose_locked = attrs.get("nose", "")
    lips_locked = attrs.get("lips", "")
    face_locked = attrs.get("face", "")
    skin_locked = attrs.get("skin", "")
    body_locked = attrs.get("body", "")
    qi_zhi_locked = attrs.get("qi_zhi", "")
    eyes_value = eyes_locked if not _is_random(eyes_locked) else picks["eyes"]
    nose_value = nose_locked if not _is_random(nose_locked) else picks["nose"]
    lips_value = lips_locked if not _is_random(lips_locked) else picks["lips"]
    face_value = face_locked if not _is_random(face_locked) else picks["contour"]
    skin_value = skin_locked if not _is_random(skin_locked) else picks["skin"]
    body_value = body_locked if not _is_random(body_locked) else picks["body"]
    qi_zhi_value = qi_zhi_locked if not _is_random(qi_zhi_locked) else _qi_zhi_for(look, archetype)
    # `look` surfaces only via the 气质 line below (per user spec).
    desc_parts = [f"{ethn} {gender}", age]
    body_lines = [
        "，".join(desc_parts),
        _STYLE_REALISM_ZH,
        f"眼睛：{eyes_value}",
        f"鼻子：{nose_value}",
        f"嘴巴：{lips_value}",
        f"脸型：{face_value}",
        _HAIRSTYLE_BUZZCUT_ZH,
        f"体型：{body_value}",
        f"皮肤：{skin_value}",
        f"气质：{qi_zhi_value}",
        _wardrobe_for(attrs["gender"]),
    ]
    return rng, body_lines, gender


def build_face_prompt_with_picks(
    attrs: dict[str, str],
    seed: int,
    archetype: str | None,
    picks: dict[str, str],
) -> str:
    """Face-emphasis prompt with caller-supplied pool picks. See
    `_resolve_batch_picks`. Format mirrors `build_face_prompt` line-for-line
    so the preview pane + Kling input are byte-comparable.
    """
    _rng, body_lines, _gender = _build_with_picks_lines(attrs, seed, archetype, picks)
    return "\n".join([f"{_HEADER_FACE}，{body_lines[0]}", *body_lines[1:]])


def build_body_prompt_with_picks(
    attrs: dict[str, str],
    seed: int,
    archetype: str | None,
    picks: dict[str, str],
) -> str:
    """Body-emphasis prompt with caller-supplied pool picks. Mirrors
    `build_body_prompt`."""
    _rng, body_lines, _gender = _build_with_picks_lines(attrs, seed, archetype, picks)
    return "\n".join([f"{_HEADER_BODY}，{body_lines[0]}", *body_lines[1:]])


# ============================================================================
# Combined single prompt (face + body in one)  (user req 2026-06-14)
# ============================================================================
#
# 用户要求：每个 actor 只出 1 条 prompt，同图同时描述「面部 + 全身」；先按用户
# 所选 (下拉 / bias) 的五官体型，再在其上叠加「更丰富的面部纹理细节」，且每个
# actor 的这些细节要独特、随机（seed 决定，可复现）。
#
# 结构（在 `_structured_lines` 之上插入一行 `面部细节：…`）：
#   {合并 header（全身 + 面部清晰）}，{民族性别, 年龄}
#   风格 / 眼睛 / 鼻子 / 嘴巴 / 脸型 / 体型 / 皮肤 / 气质     ← 跟随用户所选
#   面部细节：{k 条 unique-random 纹理细节}                   ← 叠加的独特随机细节
#   {服装（展示全身形体轮廓）}

_HEADER_COMBINED: str = (
    "全身定妆照（试镜照）, 一张图同时呈现完整全身形体与清晰面部, "
    "正脸正面平视镜头（绝不侧脸、不转头、不低头、不仰头，面部完整正对镜头）, "
    "头顶到脚趾完整入画, 面部五官清晰可辨、面部细节高清"
)

# 面部纹理 / 细节池 — 写实级、性别中立（不含 _FEMALE_ONLY/_MALE_ONLY 标记，
# 男女皆可用）。每个 actor 随机抽 k 条（seed 决定）形成独一无二的脸。
_FACE_DETAIL_ZH: tuple[str, ...] = (
    "鼻翼两侧自然细密毛孔",
    "眼下卧蚕清晰、细微泪沟",
    "唇部纵向细纹、唇色自然过渡",
    "眉峰处几根未修饰的杂乱眉毛、真实感",
    "颧骨高光处淡淡皮脂油光",
    "下颌线边缘细小绒毛",
    "鼻尖细微毛孔与轻微高光",
    "眼角细纹随表情自然浮现",
    "左脸颊一颗浅淡小痣",
    "鼻梁侧淡淡几点雀斑",
    "睫毛根根分明、长短自然不齐",
    "虹膜纹理清晰、眼神湿润有高光",
    "皮肤表面真实细纹与微小瑕疵",
    "嘴角一侧浅浅梨涡",
    "额头淡淡抬头纹、自然不夸张",
    "耳廓轮廓清晰、耳垂厚实",
    "发际线边缘细碎绒毛、不完美的真实感",
    "面部左右轻微不对称、真实人脸感",
    "鼻头与脸颊交界处毛孔粗细不均",
    "下唇中央一道自然唇珠",
    "双眼皮褶皱深浅自然",
    "脸颊一抹自然的健康红晕",
    "鼻梁微微反光、皮肤真实通透感",
)

_FACE_DETAIL_COUNT: int = 5
"""每个 actor 叠加的随机面部细节条数。5 条足够拉开个体差异又不淹没所选特征。"""


# 角色原型 → 面部「神态」细节池（可观测的表情/神色细节，非情绪名词；与五官 bias
# 同向，进一步压实"选了阴邪就阴邪"）。仅 5 个 character-archetype look 有；其余
# look 走纯写实纹理池，与改动前 byte-identical。用户 req 2026-06-14：补充 prompt
# 细节时按角色原型添加。
_LOOK_FACE_DETAIL_ZH: dict[str, tuple[str, ...]] = {
    "sinister": (
        "眉宇间凝着一缕挥之不去的阴鸷",
        "嘴角噙着一抹似笑非笑的冷意",
        "眼神深处暗藏锋芒、深不见底",
        "颧骨投下冷硬的阴影",
        "眼尾微微下压、透出几分狠戾",
        "下颌线绷紧、隐隐透着压迫感",
    ),
    "seductive": (
        "眼尾上挑、眼波似能勾人",
        "唇角噙着若有若无的笑意",
        "眼神慵懒、含着三分春意",
        "下唇微抿、欲语还休",
        "目光流转间尽是风情",
        "下颌微收、眼神慵懒直视镜头、媚意自生",
    ),
    "righteous": (
        "目光坦荡清正、不闪不避",
        "眉宇间一身浩然正气",
        "下颌线刚毅、神色端方",
        "眼神明亮坚定、不怒自威",
        "唇线端正、神情磊落",
        "脊背挺直、气度凛然",
    ),
    "cunning": (
        "眼珠微转、似在暗自盘算",
        "嘴角挂着一抹狡黠的弧度",
        "眼神精明、藏着算计",
        "眉梢轻挑、心思难测",
        "似笑非笑间透出几分算计",
        "目光斜睨、不动声色",
    ),
    "innocent": (
        "眼神清澈见底、不谙世事",
        "嘴角天真无邪、漾着浅浅梨涡",
        "脸颊柔软、带着孩子气的圆润",
        "目光纯净、像未被世事沾染",
        "笑意干净、眉眼弯弯",
        "神情懵懂、惹人怜爱",
    ),
}

_LOOK_FACE_DETAIL_COUNT: int = 2
"""character-archetype look 时，面部细节里先放 N 条原型神态细节，其余补写实纹理。"""


def _sample_face_details(
    rng: random.Random, look: str = "", k: int = _FACE_DETAIL_COUNT
) -> list[str]:
    """Draw `k` distinct face details. For a character-archetype `look`, the
    first `_LOOK_FACE_DETAIL_COUNT` come from that archetype's 神态 pool (so the
    extra detail reinforces the 原型 instead of diluting it) and the rest from
    the realism-texture pool. Non-character looks → byte-identical to before
    (`k` from the texture pool). Deterministic in the rng state."""
    k = min(k, len(_FACE_DETAIL_ZH))
    look_pool = _LOOK_FACE_DETAIL_ZH.get(look)
    if not look_pool:
        return rng.sample(_FACE_DETAIL_ZH, k)
    n_look = min(_LOOK_FACE_DETAIL_COUNT, len(look_pool), k)
    flavored = rng.sample(list(look_pool), n_look)
    generic = rng.sample(_FACE_DETAIL_ZH, k - n_look)
    return flavored + generic


def _compose_combined(header: str, body_lines: list[str], detail_line: str) -> str:
    """Assemble: header+desc / selected feature lines / 面部细节 / 服装.
    `body_lines` = output of `_structured_lines` (desc, 风格, 眼…气, 服装);
    the 面部细节 line is inserted just before the closing 服装 line so the
    prompt reads 用户所选 → 叠加细节 → 全身服装."""
    head = body_lines[:-1]
    wardrobe = body_lines[-1]
    return "\n".join([f"{header}，{head[0]}", *head[1:], detail_line, wardrobe])


def build_combined_prompt(attrs: dict[str, str], seed: int, archetype: str | None) -> str:
    """单条「面部 + 全身」合并 prompt（用户 2026-06-14 需求）。

    先按用户所选 / archetype-bias 抽出五官体型（`_structured_lines`），再叠加
    `_FACE_DETAIL_COUNT` 条 unique-random 面部纹理细节。纯确定性 —
    `(seed, archetype, attrs)` 复现同一结果。"""
    rng = random.Random(seed)
    body_lines = _structured_lines(rng, attrs, archetype)
    detail_line = "面部细节：" + "，".join(_sample_face_details(rng, attrs.get("look", "")))
    return _compose_combined(_HEADER_COMBINED, body_lines, detail_line)


def build_combined_prompt_with_picks(
    attrs: dict[str, str],
    seed: int,
    archetype: str | None,
    picks: dict[str, str],
) -> str:
    """Batch-coordinated variant of `build_combined_prompt` — five structured
    pool draws come from `picks` (no within-batch repeats), the 面部细节 line
    is still per-actor unique-random off `seed`."""
    rng, body_lines, _gender = _build_with_picks_lines(attrs, seed, archetype, picks)
    detail_line = "面部细节：" + "，".join(_sample_face_details(rng, attrs.get("look", "")))
    return _compose_combined(_HEADER_COMBINED, body_lines, detail_line)
