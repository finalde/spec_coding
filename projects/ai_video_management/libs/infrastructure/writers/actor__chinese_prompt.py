"""中文 actor prompt builder for Kling.

Per follow-up 075: 用户要求 actor generation 的 prompt 全部用中文，按固定结构
输出 — 眼睛：{大小}, {形状}, {...} / 鼻子：... / 嘴巴：... / 眉毛：... /
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


_BROW_ZH: tuple[str, ...] = (
    "剑眉, 浓密粗黑, 英气逼人",
    "柳叶眉, 细长上挑, 妩媚动人",
    "远山眉, 淡雅清远, 温柔如水",
    "卧蚕眉, 粗黑挺直, 男性硬朗",
    "细弯眉, 精致秀气, 古典美人",
    "浓眉, 粗犷豪放, 个性张扬",
    "淡眉清眉, 自然柔和, 清秀脱俗",
    "上挑眉, 眉角飞扬, 凌厉冷艳",
    "平直眉, 韩式眉, 温柔大气",
    "弯月眉, 弧度精致, 笑容温婉",
    "剑眉星目, 英姿飒爽, 文武双全",
    "修长眉峰, 微微挑起, 灵动俏皮",
    "粗眉直线, 现代时尚, 中性飒爽",
    "细眉精致, 化妆精修, 韩范十足",
    "羽毛眉, 自然向上, 时尚潮流",
    "古典蛾眉, 细长妩媚, 风情万种",
    "浓眉硬朗, 不羁锐利, 江湖侠气",
    "低垂眉头, 略带忧郁, 文艺气息",
    "高挑眉峰, 锐利上扬, 王者风范",
    "亲和淡眉, 温柔下垂, 萌系可爱",
    "挑眉冷峻, 凌厉如刀, 杀手气场",
    "温柔细眉, 弯弯如月, 邻家姐姐",
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


_PHOTOGRAPHY_ZH: tuple[str, ...] = (
    "佳能 EOS R5 85mm f/1.4 人像镜头, 真实皮肤微纹理",
    "索尼 A7 IV 50mm 自然色彩, 抓拍构图",
    "富士 X-T5 经典反转片, 自然胶片颗粒感",
    "哈苏中画幅人像, 油画般层次, 真实毛孔",
    "柯达 Portra 400 胶片, 温暖肤色, 轻微光晕",
    "Cinestill 800T 电影胶片, 高光晕染, 写实电影感",
    "徕卡 M11 旁轴抓拍, 自然环境光, 真实质感",
    "iPhone 15 Pro 街拍, 略微失焦, 真实生活感",
    "尼康 Z9 105mm f/1.4, 超自然渲染, 不平滑皮肤",
    "宝丽来 SX-70 拍立得, 化学色偏, 真诚记录",
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
within-archetype 形体 variety 保持。"""


# ============================================================================
# Helpers
# ============================================================================


def _pick(rng: random.Random, pool: tuple[str, ...]) -> str:
    return rng.choice(pool)


def _pick_biased(
    rng: random.Random,
    pool: tuple[str, ...],
    bias_indices: tuple[int, ...] | None,
) -> str:
    if bias_indices and rng.random() >= _BIAS_WILD_PROB:
        candidates = [pool[i] for i in bias_indices if 0 <= i < len(pool)]
        if candidates:
            return rng.choice(candidates)
    return rng.choice(pool)


def _synthesis_for(archetype: str | None) -> str:
    if archetype and archetype in _SYNTHESIS_BY_ARCHETYPE:
        return _SYNTHESIS_BY_ARCHETYPE[archetype]
    return "一位演员, 真实自然, 富有个性"


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

_STYLE_ZH: dict[str, str] = {
    "modern-casual":         "现代休闲装, 都市背景",
    "period-ancient-china":  "中国古装, 仙侠武侠风",
    "period-western":        "维多利亚时代古装",
    "business":              "正装西装, 商务场景",
    "streetwear":            "街头潮流, 都市街拍",
    "sci-fi":                "未来科幻装, 中性背景",
    "fantasy":               "高奇幻服装, 中性背景",
}


_NEGATIVES_ZH: str = (
    "避免：塑料感皮肤, 蜡像感, 卡通比例, 过度磨皮, "
    "对称完美脸, AI 生成同质化脸, 影楼美化, 千篇一律的网红脸"
)


def build_face_prompt(attrs: dict[str, str], seed: int, archetype: str | None) -> str:
    """构造结构化中文 face-shot prompt.

    Pure deterministic — same `(seed, archetype)` reproduces the same draw.
    Structure:
        角色描述：{ethnicity} {gender}，{age}
        眼睛：{...}
        鼻子：{...}
        嘴巴：{...}
        眉毛：{...}
        轮廓：{...}
        皮肤：{...}
        体型：{...}
        综合描述：{archetype 风韵}
        服装：{style 风格}
        摄影：{photography 风格}
        要求：人像写真, 自然光, 真实质感, 8K 高清
        {negatives}
    """
    rng = random.Random(seed)
    ethn = _ETHNICITY_ZH.get(attrs["ethnicity"], attrs["ethnicity"])
    gender = _GENDER_ZH.get(attrs["gender"], attrs["gender"])
    age = _AGE_ZH.get(attrs["age_range"], attrs["age_range"])
    style = _STYLE_ZH.get(attrs["style"], attrs["style"])
    body_bias = _BODY_BIAS_BY_ARCHETYPE.get(archetype or "")
    lines = [
        f"角色描述：{ethn} {gender}，{age}",
        f"眼睛：{_pick(rng, _EYES_ZH)}",
        f"鼻子：{_pick(rng, _NOSE_ZH)}",
        f"嘴巴：{_pick(rng, _LIPS_ZH)}",
        f"眉毛：{_pick(rng, _BROW_ZH)}",
        f"轮廓：{_pick(rng, _CONTOUR_ZH)}",
        f"皮肤：{_pick(rng, _SKIN_ZH)}",
        f"体型：{_pick_biased(rng, _BODY_ZH, body_bias)}",
        f"综合描述：{_synthesis_for(archetype)}",
        f"服装：{style}",
        f"摄影：{_pick(rng, _PHOTOGRAPHY_ZH)}",
        "要求：人像写真, 自然光, 真实质感, 8K 高清, 抓拍随意感, 真实毛孔, 自然不对称",
        _NEGATIVES_ZH,
    ]
    return "\n".join(lines)


def build_body_prompt(attrs: dict[str, str], seed: int, archetype: str | None) -> str:
    """构造结构化中文 body-shot prompt.

    Per follow-up 052: body wardrobe LOCKED to casting-standard 灰色修身 T 恤 +
    黑色运动短裤，不受 attrs.style 影响（行业 comp-card 惯例 — 形体判断不被
    戏服干扰）。Same `(seed, archetype)` → 与 face 共享身份锚 (相同的五官 +
    体型抽样)。
    """
    rng = random.Random(seed)
    ethn = _ETHNICITY_ZH.get(attrs["ethnicity"], attrs["ethnicity"])
    gender = _GENDER_ZH.get(attrs["gender"], attrs["gender"])
    age = _AGE_ZH.get(attrs["age_range"], attrs["age_range"])
    body_bias = _BODY_BIAS_BY_ARCHETYPE.get(archetype or "")
    lines = [
        f"全身定妆照：{ethn} {gender}，{age}",
        f"眼睛：{_pick(rng, _EYES_ZH)}",
        f"鼻子：{_pick(rng, _NOSE_ZH)}",
        f"嘴巴：{_pick(rng, _LIPS_ZH)}",
        f"眉毛：{_pick(rng, _BROW_ZH)}",
        f"轮廓：{_pick(rng, _CONTOUR_ZH)}",
        f"皮肤：{_pick(rng, _SKIN_ZH)}",
        f"体型：{_pick_biased(rng, _BODY_ZH, body_bias)}",
        f"综合描述：{_synthesis_for(archetype)}",
        "姿态：自然站立, 双臂自然下垂, 正面面向镜头, 重心均匀",
        "服装：灰色修身 T 恤, 黑色运动短裤, 朴素运动鞋（业内 comp-card 标准）",
        "画面：从头到脚全身可见, 中性纯色背景",
        f"摄影：{_pick(rng, _PHOTOGRAPHY_ZH)}",
        "要求：定妆照, 自然光, 真实质感, 8K 高清, 不带戏服干扰形体判断",
        _NEGATIVES_ZH,
    ]
    return "\n".join(lines)
