"""NovelSpec value object + CANONICAL_NOVELS manifest.

Per follow-up 107: each novel can have multiple sources, tried in order.
`NovelSource(host, source_id)` carries one (host, identifier) pair.
`NovelSpec.sources` is a tuple of sources; the downloader picks the first
reachable one at index time. Compat properties `source_host` / `source_id`
return the first source for callers that still use the single-source API.
"""
from __future__ import annotations

from dataclasses import dataclass

from libs.domain.errors.novel__error import NovelNotFoundError


@dataclass(frozen=True)
class NovelSource:
    host: str
    source_id: str

    def __post_init__(self) -> None:
        if not self.host:
            raise ValueError("host is required")
        if not self.source_id:
            raise ValueError("source_id is required")


@dataclass(frozen=True)
class NovelSpec:
    slug: str
    title_zh: str
    author: str
    category: str
    category_zh: str
    sources: tuple[NovelSource, ...]

    def __post_init__(self) -> None:
        if not self.slug or not self.slug.replace("_", "").isalnum():
            raise ValueError(f"invalid slug: {self.slug!r}")
        if not self.title_zh:
            raise ValueError("title_zh is required")
        if not self.category or not self.category.isalpha():
            raise ValueError(f"invalid category slug: {self.category!r}")
        if not self.category_zh:
            raise ValueError("category_zh is required")
        if not self.sources:
            raise ValueError(f"{self.slug}: at least one source required")

    @property
    def source_host(self) -> str:
        """Compat — returns the first source's host."""
        return self.sources[0].host

    @property
    def source_id(self) -> str:
        """Compat — returns the first source's source_id."""
        return self.sources[0].source_id


def _sudugu(source_id: str) -> NovelSource:
    return NovelSource("sudugu.org", source_id)


def _ttkan(source_slug: str) -> NovelSource:
    # cn. subdomain serves Simplified Chinese; www. served Traditional (follow-up 109).
    return NovelSource("cn.ttkan.co", source_slug)


CANONICAL_NOVELS: tuple[NovelSpec, ...] = (
    # 仙侠 — original 10 from follow-up 101
    NovelSpec("fanren_xiuxian_zhuan", "凡人修仙传", "忘语", "xianxia", "仙侠",
              (_sudugu("128"), _ttkan("fanrenxiuxianchuan-wangyu"))),
    NovelSpec("guangyin_zhiwai", "光阴之外", "耳根", "xianxia", "仙侠",
              (_sudugu("1640"), _ttkan("guangyinzhiwai-ergen"))),
    NovelSpec("xuanjian_xianzu", "玄鉴仙族", "季越人", "xianxia", "仙侠",
              (_sudugu("53"),)),
    NovelSpec("meiqian_xiu_shenme_xian", "没钱修什么仙？", "熊狼狗", "xianxia", "仙侠",
              (_sudugu("52"),)),
    NovelSpec("jie_jian", "借剑", "幼儿园一把手", "xianxia", "仙侠",
              (_sudugu("55"),)),
    NovelSpec("gou_zai_liangjie_xiuxian", "苟在两界修仙", "文抄公", "xianxia", "仙侠",
              (_sudugu("3664"),)),
    NovelSpec("wode_moni_changsheng_lu", "我的模拟长生路", "愤怒的乌贼", "xianxia", "仙侠",
              (_sudugu("167"),)),
    NovelSpec("shei_rang_ta_xiuxian_de", "谁让他修仙的！", "最白的乌鸦", "xianxia", "仙侠",
              (_sudugu("207"),)),
    NovelSpec("shan_he_ji", "山河稷", "姬叉", "xianxia", "仙侠",
              (_sudugu("60"),)),
    NovelSpec("zhen_wen_changsheng", "阵问长生", "观虚", "xianxia", "仙侠",
              (_sudugu("115"),)),
    # 仙侠 — expanded in follow-up 103
    NovelSpec("gou_zai_yaowu_luanshi", "苟在妖武乱世修仙", "文抄公", "xianxia", "仙侠",
              (_sudugu("529"),)),
    NovelSpec("cong_jianshu_xiuxing", "从箭术开始修行", "豆浆油条热干面", "xianxia", "仙侠",
              (_sudugu("534"),)),
    NovelSpec("zhutian_daozu", "诸天道祖，从遮天开始", "山海一闲鱼", "xianxia", "仙侠",
              (_sudugu("2533"),)),
    NovelSpec("gou_zai_xiuxianjie", "苟在修仙界吞噬成圣", "喵郡王", "xianxia", "仙侠",
              (_sudugu("2036"),)),
    NovelSpec("changsheng_xiuxian_haomao", "长生修仙：从薅妖兽天赋开始", "廿三声", "xianxia", "仙侠",
              (_sudugu("2035"),)),
    NovelSpec("changsheng_zhuji_chenggong", "长生：筑基成功后，外挂才开启", "好的名字很难想", "xianxia", "仙侠",
              (_sudugu("1820"),)),
    NovelSpec("xiyou_baishi_taiyi", "西游：从拜师太乙救苦天尊开始", "清风映明月", "xianxia", "仙侠",
              (_sudugu("319"),)),
    NovelSpec("po_dao_xing", "泼刀行", "张老西", "xianxia", "仙侠",
              (_sudugu("205"),)),
    NovelSpec("xi_shen", "戏神！", "独孤欢", "xianxia", "仙侠",
              (_sudugu("1962"),)),
    NovelSpec("qinghu_jianxian", "青葫剑仙", "竹林剑隐", "xianxia", "仙侠",
              (_sudugu("1649"),)),
    NovelSpec("cong_songzi_liyu", "从送子鲤鱼到天庭仙官", "锦绣灰", "xianxia", "仙侠",
              (_sudugu("2528"),)),
    # 仙侠 — added in follow-up 110 (popular ongoing/complete picks from sudugu xianxia ranking)
    NovelSpec("jianlai", "剑来", "烽火戏诸侯", "xianxia", "仙侠",
              (_sudugu("287"),)),
    NovelSpec("xian_ni", "仙逆", "耳根", "xianxia", "仙侠",
              (_sudugu("410"),)),
    NovelSpec("dafeng_dagengren", "大奉打更人", "卖报小郎君", "xianxia", "仙侠",
              (_sudugu("405"),)),
    NovelSpec("chixin_xuntian", "赤心巡天", "情何以甚", "xianxia", "仙侠",
              (_sudugu("56"),)),
    NovelSpec("dadao_zhengfeng", "大道争锋", "误道者", "xianxia", "仙侠",
              (_sudugu("435"),)),
    # 玄幻
    NovelSpec("guimi_zhizhu", "诡秘之主", "爱潜水的乌贼", "xuanhuan", "玄幻",
              (_sudugu("13"),)),
    NovelSpec("wanmei_shijie", "完美世界", "辰东", "xuanhuan", "玄幻",
              (_sudugu("427"), _ttkan("wanmeishijie-chendong"))),
    NovelSpec("ze_tian_ji", "择天记", "猫腻", "xuanhuan", "玄幻",
              (_sudugu("2242"), _ttkan("zetianji-maoni"))),
    NovelSpec("puluo_zhizhu", "普罗之主", "沙拉古斯", "xuanhuan", "玄幻",
              (_sudugu("130"),)),
    NovelSpec("qing_shan", "青山", "会说话的肘子", "xuanhuan", "玄幻",
              (_sudugu("5"),)),
    # 都市
    NovelSpec("wo_bushi_xishen", "我不是戏神", "三九音域", "dushi", "都市",
              (_sudugu("617"),)),
    NovelSpec("shenkong_bian_an", "深空彼岸", "辰东", "dushi", "都市",
              (_sudugu("415"),)),
    NovelSpec("guomin_fayi", "国民法医", "志鸟村", "dushi", "都市",
              (_sudugu("89"),)),
    NovelSpec("laoshi_ren", "捞尸人", "纯洁滴小龙", "dushi", "都市",
              (_sudugu("51"),)),
    # 历史
    NovelSpec("zhuangyuan_lang", "状元郎", "三戒大师", "lishi", "历史",
              (_sudugu("87"),)),
    NovelSpec("jinmo_changjian", "晋末长剑", "孤独麦客", "lishi", "历史",
              (_sudugu("83"),)),
    NovelSpec("mingchao_baijiazi", "明朝败家子", "上山打老虎额", "lishi", "历史",
              (_sudugu("605"),)),
    # 科幻
    NovelSpec("tunshi_xingkong", "吞噬星空", "我吃西红柿", "kehuan", "科幻",
              (_sudugu("409"),)),
    NovelSpec("liming_zhijian", "黎明之剑", "远瞳", "kehuan", "科幻",
              (_sudugu("369"),)),
    NovelSpec("yidu_lvshe", "异度旅社", "远瞳", "kehuan", "科幻",
              (_sudugu("54"),)),
    NovelSpec("lingjing_xingzhe", "灵境行者", "卖报小郎君", "kehuan", "科幻",
              (_sudugu("408"), _ttkan("lingjingxingzhe-maibaoxiaolangjun"))),
    # 言情
    NovelSpec("wo_zai_jingsong_youxi", "我在惊悚游戏里封神", "壶鱼辣椒", "yanqing", "言情",
              (_sudugu("1753"),)),
    NovelSpec("denghua_xiao", "灯花笑", "千山茶客", "yanqing", "言情",
              (_sudugu("2389"),)),
)


def find_novel(slug: str) -> NovelSpec:
    for spec in CANONICAL_NOVELS:
        if spec.slug == slug:
            return spec
    raise NovelNotFoundError(f"unknown novel slug: {slug!r}")


def categories() -> list[tuple[str, str]]:
    """Return [(category_slug, category_zh), ...] in first-appearance order."""
    seen: dict[str, str] = {}
    for spec in CANONICAL_NOVELS:
        if spec.category not in seen:
            seen[spec.category] = spec.category_zh
    return list(seen.items())
