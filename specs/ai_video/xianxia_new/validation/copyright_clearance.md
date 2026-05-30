---
worker_id: level-specialist-05-copyright_clearance
stage: 5
role: level-specialist
level: copyright_clearance
status: complete
blockers: []
confidence: high
---

# Validation level — copyright_clearance

## 1. Scope and role of this level

**This level (`copyright_clearance`)** owns:

- **Auto-grep gate** against two BLACKLIST tables (14-baseline distinctive entities + sibling project `mozun_chongsheng` canonical entities).
- **Cross-project** byte-level collision check (no entity from `my_novel/feng_shou_lu/` outputs may literally appear in `ai_videos/mozun_chongsheng/` and vice-versa).
- **Etymology preservation** check on character bibles' `词源` line (FR-5.2 traceability).
- **Sign-off ritual** that timestamps the gate-pass and gets stamped into the canonical `my_novel/feng_shou_lu/copyright_clearance.md` (FR-12).

**Out of scope here (lives at `character_visual_consistency`)**:

- Byte-identical lock-down of the 10-field 锁定描述符 between character bibles and shot prompts (intra-project; NFR-2).
- Seedream立绘 vs shot prompt 面部 differentiator drift checks.

The two levels are complementary: `copyright_clearance` ensures **what is named** is original and non-colliding; `character_visual_consistency` ensures **what is named is rendered consistently** across the project's own files.

## 2. Validators V-CR-1 through V-CR-7

### V-CR-1 — Canonical `copyright_clearance.md` exists and has all four mandatory sections

**Severity:** blocker if file missing or any of the 4 main sections (BLACKLIST · mozun cross-grep · PROPOSED naming · DELTA report) is missing. SIGN-OFF section may be empty pre-run (this validator's job is to write it).

**Executable check (parent runs):**

```bash
# 1. file existence
test -f my_novel/feng_shou_lu/copyright_clearance.md || fail "FR-12 file missing"

# 2. four section headers present (heading-level agnostic; case-sensitive Chinese match)
grep -F "BLACKLIST" my_novel/feng_shou_lu/copyright_clearance.md   || fail "missing BLACKLIST section"
grep -F "mozun"     my_novel/feng_shou_lu/copyright_clearance.md   || fail "missing mozun_chongsheng cross-grep section"
grep -F "PROPOSED"  my_novel/feng_shou_lu/copyright_clearance.md   || fail "missing PROPOSED naming section"
grep -F "DELTA"     my_novel/feng_shou_lu/copyright_clearance.md   || fail "missing DELTA report section"
```

**Audit event templates:**

```json
{"event":"validation.started","level":"copyright_clearance","check":"V-CR-1","ts":"<ISO8601>","file":"my_novel/feng_shou_lu/copyright_clearance.md"}
{"event":"validation.pass","level":"copyright_clearance","check":"V-CR-1","ts":"<ISO8601>"}
{"event":"validation.issue.raised","level":"copyright_clearance","check":"V-CR-1","severity":"blocker","reason":"<one of: file_missing | section_missing:BLACKLIST | section_missing:mozun_cross_grep | section_missing:PROPOSED | section_missing:DELTA>","ts":"<ISO8601>"}
```

### V-CR-2 — Auto-grep gate against both BLACKLIST tables

**Severity:** blocker on any literal hit.

**Executable check:** parent builds the union BLACKLIST = (§3 seed table below) ∪ (§4 mozun seed table below; supplemented by recursive grep at stage-6 runtime per Implementation notes). Then runs a literal-match (no regex) UTF-8 case-sensitive Han search across:

- All `*.md` files under `my_novel/feng_shou_lu/`.
- All `*.md` files under `ai_videos/feng_shou_lu/`.

Whitelist exemptions (files where blacklist terms are *expected* to appear by design — these terms inside these files do NOT raise issues):

1. `my_novel/feng_shou_lu/copyright_clearance.md` (the BLACKLIST table itself).
2. The DELTA report subsection within `copyright_clearance.md` (it quotes "we replaced X with Y" — X may be a blacklist term).

**Pseudocode (see §5 Grep implementation for the full Bash):**

```python
BLACKLIST = parse_table_rows(copyright_clearance.md, sections=[1, 2])
EXEMPT_FILES = ["my_novel/feng_shou_lu/copyright_clearance.md"]
TARGET_GLOBS = ["my_novel/feng_shou_lu/**/*.md", "ai_videos/feng_shou_lu/**/*.md"]

for term in BLACKLIST:
    for path in glob(TARGET_GLOBS):
        if path in EXEMPT_FILES:
            continue
        for lineno, line in enumerate(open(path, encoding="utf-8"), 1):
            if term in line:  # literal substring; no regex
                emit_blocker(path, lineno, term)
```

**Audit event template (one per hit):**

```json
{"event":"validation.issue.raised","level":"copyright_clearance","check":"V-CR-2","severity":"blocker","reason":"BLACKLIST_HIT","term":"<term>","file":"<rel_path>","line":<int>,"line_text":"<line content>","ts":"<ISO8601>"}
```

Zero-hit success:

```json
{"event":"validation.pass","level":"copyright_clearance","check":"V-CR-2","terms_checked":<int>,"files_scanned":<int>,"ts":"<ISO8601>"}
```

### V-CR-3 — Character anonymization etymology preservation

**Severity:**

- Missing `词源` line in any bible → **blocker** (FR-5.2 contract).
- Drift from `findings/angle-character_anonymization.md` §3 verbatim → **warning** (stage 4 may have intentionally refined; surface for user review).

**Executable check:**

```bash
# load reference etymology table (key = character name; value = etymology text)
ref_table=$(extract_etymology_table findings/angle-character_anonymization.md §3)

for bible in my_novel/feng_shou_lu/characters/*.md; do
    char_name=$(basename "$bible" .md)
    bible_etym=$(grep -F "词源" "$bible" | head -1)
    if [ -z "$bible_etym" ]; then
        emit_blocker "$bible" "MISSING_ETYMOLOGY"
        continue
    fi
    ref_etym="${ref_table[$char_name]}"
    if [ "$bible_etym" != "$ref_etym" ]; then
        emit_warning "$bible" "ETYMOLOGY_DRIFT" "expected=$ref_etym actual=$bible_etym"
    fi
done
```

Reference etymologies (from `findings/angle-character_anonymization.md` §3.1–3.2, byte-identical seed):

| Character | Reference 词源 (from angle file §3) |
|---|---|
| 裴知秋 | "一叶知秋"先知预言性 + "秋"字寿尽凋零母题；本世自取「知秋」是 ep01 落叶之夜系统觉醒后给自己的新名 |
| 裴长砚 | 主角前世名；与师父闻砚清共享"砚"字 — ep17 揭穿后 timeline 缝合关键符号 |
| 闻砚清 | "砚清"= 砚水清；师徒记忆传承的核心象征 |
| 容漪 | "漪"= 水纹涟漪；与系统"波纹消散"视觉母题暗扣；ep28 揭穿为 忘川教 安插的活体记忆库 |
| 卫长烛 | "长烛"= 长明烛（虚伪的"道义不灭"）|
| 应砚之 | "应砚"= 应被打碎的砚（背叛契约）|
| 戚归砚 | "归砚"= 弃笔归砚（弃道）|
| 池洇 | "洇"= 水墨晕染（被毁契约的渗透）|
| 阮惘 | "惘"= 怅然若失（被夺记忆者）|
| 言息 | "息"= 气息 / 寿数 / 利息（三重双关，与系统设计共名）|

**Audit events:**

```json
{"event":"validation.issue.raised","level":"copyright_clearance","check":"V-CR-3","severity":"blocker","reason":"MISSING_ETYMOLOGY","character":"<name>","file":"<path>","ts":"<ISO8601>"}
{"event":"validation.issue.raised","level":"copyright_clearance","check":"V-CR-3","severity":"warning","reason":"ETYMOLOGY_DRIFT","character":"<name>","expected":"<ref>","actual":"<bible>","ts":"<ISO8601>"}
```

### V-CR-4 — Cross-project mozun grep

**Severity:** blocker on any hit.

**Executable check:** for every named entity defined in `my_novel/feng_shou_lu/` (characters + scenes + sects + 神器 + 功法 + 地名), grep all `ai_videos/mozun_chongsheng/` outputs for the literal string. Build the "named entity" set from `characters/*.md` filenames + `scenes/*.md` filenames + `world.md` heading and table entries + `style_guide.md` palette-named entities.

```bash
# 1. extract our project's named entities
OUR_ENTITIES=$(
    ls my_novel/feng_shou_lu/characters/*.md | xargs -n1 basename | sed 's/\.md$//' ;
    ls my_novel/feng_shou_lu/scenes/*.md     | xargs -n1 basename | sed 's/\.md$//' | sed 's/^s[0-9]*_//' ;
    grep -oP "(赤霞门|九寰阁|澹台宗|流烛盟|忘川教|焚寿罗盘|残忆经|偿岁真言|归砚镜|长烟幡|澹江洲|落雁渊|栖梧崖|乌泽)" my_novel/feng_shou_lu/world.md | sort -u
)

# 2. literal-match grep against mozun project
for entity in $OUR_ENTITIES; do
    for path in ai_videos/mozun_chongsheng/**/*.md; do
        if grep -F "$entity" "$path" > /dev/null; then
            emit_blocker "$path" "$entity" "CROSS_PROJECT_COLLISION"
        fi
    done
done
```

**Audit event:**

```json
{"event":"validation.issue.raised","level":"copyright_clearance","check":"V-CR-4","severity":"blocker","reason":"CROSS_PROJECT_COLLISION","entity":"<name>","mozun_file":"<path>","ts":"<ISO8601>"}
```

### V-CR-5 — `wode_moni_changsheng_lu` fingerprint check (CCI-1 extra paranoia)

**Severity:**

- Literal hit on the 11 forbidden phrases → **blocker**.
- Semantic match on simulator金手指 mechanic (cost-free reruns / 锚定 N 年 / 无限重来) → **warning** for stage-5 manual review.

**Forbidden phrases (literal-grep seed, per dossier CCI-1):**

| # | Phrase | Why forbidden |
|---|---|---|
| 1 | 太师寿宴 | wode_moni ep01 hook scene |
| 2 | 流星仙人斗法 | wode_moni ep01 inciting incident |
| 3 | 仙凡瘴 | wode_moni signature setting term |
| 4 | 锚定 | wode_moni simulator核心动词 |
| 5 | 天玄镜 | wode_moni金手指 神器名 |
| 6 | 万仙盟 | wode_moni 正派联盟 |
| 7 | 玄京 | wode_moni 首都地名 |
| 8 | 琅琊王 | wode_moni 政体角色 |
| 9 | 温县 | wode_moni 主角故乡 |
| 10 | 江淮府 | wode_moni 主要 region |
| 11 | 李凡 | wode_moni 主角名 |

**Executable check:**

```bash
FORBIDDEN_WODE_MONI=("太师寿宴" "流星仙人斗法" "仙凡瘴" "锚定" "天玄镜" "万仙盟" "玄京" "琅琊王" "温县" "江淮府" "李凡")
for phrase in "${FORBIDDEN_WODE_MONI[@]}"; do
    grep -rnF --include='*.md' "$phrase" my_novel/feng_shou_lu/ ai_videos/feng_shou_lu/ 2>/dev/null \
        | grep -v "copyright_clearance.md" \
        | while read -r hit; do emit_blocker "$hit" "$phrase" "WODE_MONI_FINGERPRINT"; done
done

# semantic flag (warning — manual review)
SEMANTIC_SIMULATOR_HINTS=("无成本" "无限重来" "无代价重活" "无成本重来" "无成本重活" "无消耗重活" "cost-free")
for hint in "${SEMANTIC_SIMULATOR_HINTS[@]}"; do
    grep -rnF --include='script.md' "$hint" my_novel/feng_shou_lu/episodes/ \
        | while read -r hit; do emit_warning "$hit" "$hint" "WODE_MONI_SIMULATOR_SEMANTIC"; done
done
```

**Note on collision with our own design**: our project name 焚寿罗盘 is a *cost-bearing* dial — the opposite of wode_moni's cost-free 天玄镜. The semantic hint check above is specifically for accidental drift toward the "无成本" framing.

**Audit events:**

```json
{"event":"validation.issue.raised","level":"copyright_clearance","check":"V-CR-5","severity":"blocker","reason":"WODE_MONI_FINGERPRINT","phrase":"<phrase>","file":"<path>","line":<int>,"ts":"<ISO8601>"}
{"event":"validation.issue.raised","level":"copyright_clearance","check":"V-CR-5","severity":"warning","reason":"WODE_MONI_SIMULATOR_SEMANTIC","hint":"<hint>","file":"<path>","line":<int>,"ts":"<ISO8601>"}
```

### V-CR-6 — Final SIGN-OFF block

**Severity:** missing or malformed SIGN-OFF when all V-CR-1..5 pass = blocker (AC-5 unsatisfied).

**Action:** on full pass of V-CR-1..5, the validator MUST append a SIGN-OFF block to `my_novel/feng_shou_lu/copyright_clearance.md`:

```markdown
## SIGN-OFF

- **Timestamp (UTC):** <ISO8601>
- **Grep-pass status:** PASS (V-CR-1..5 all green)
- **BLACKLIST terms checked:** <int> from 14-baseline + <int> from mozun_chongsheng = <total>
- **Files scanned:** <int> under my_novel/feng_shou_lu/ + <int> under ai_videos/feng_shou_lu/
- **Zero-hit confirmation:** yes
- **Validator agent id:** level-specialist-05-copyright_clearance (task_id <task_id>)
- **Empty-baseline gap (CCI-6):** <one of: "RESOLVED — 3 baselines downloaded and merged" | "OPEN — BLACKLIST under-spec'd by 3 baselines (cong_jianshu_xiuxing, gou_zai_xiuxianjie, zhutian_daozu); flag for re-validation when downloaded">
```

**Audit event:**

```json
{"event":"validation.pass","level":"copyright_clearance","check":"V-CR-6","sign_off_appended_to":"my_novel/feng_shou_lu/copyright_clearance.md","ts":"<ISO8601>"}
```

### V-CR-7 — Empty-folder补抓 status note (CCI-6)

**Severity:**

- Empty folders still empty at stage-6 runtime AND SIGN-OFF lacks the "OPEN" gap note → **blocker** (silent under-spec'd validation).
- Empty folders downloaded since stage-3, BLACKLIST NOT extended with their distinctive entities → **blocker** (we'd be running validation against a stale BLACKLIST).
- Empty folders downloaded AND BLACKLIST extended properly → **pass**.

**Executable check:**

```bash
# 1. detect download state
EMPTY_FOLDERS=("cong_jianshu_xiuxing" "gou_zai_xiuxianjie" "zhutian_daozu")
for folder in "${EMPTY_FOLDERS[@]}"; do
    if [ -n "$(ls -A downloaded_novels/xianxia/$folder/chapters/ 2>/dev/null)" ]; then
        DOWNLOADED+=("$folder")
    fi
done

# 2. branch
if [ "${#DOWNLOADED[@]}" -gt 0 ]; then
    # mini baseline_extraction pass required
    for folder in "${DOWNLOADED[@]}"; do
        new_entities=$(run_mini_baseline_extraction "downloaded_novels/xianxia/$folder/")
        appended_to_blacklist=$(check_appended "my_novel/feng_shou_lu/copyright_clearance.md" "$folder" "$new_entities")
        if [ "$appended_to_blacklist" != "yes" ]; then
            emit_blocker "BLACKLIST_NOT_EXTENDED" "$folder"
        fi
    done
else
    # still empty — sign-off must declare the gap
    if ! grep -q "OPEN — BLACKLIST under-spec'd by 3 baselines" my_novel/feng_shou_lu/copyright_clearance.md; then
        emit_blocker "SIGN_OFF_MISSING_GAP_NOTE"
    fi
fi
```

**`run_mini_baseline_extraction` contract:** re-read first 5 + ch50 + last chapter of the newly-populated folder, extract distinctive命名实体 (characters, sects, locations, 神器, 功法) using the same heuristics as `findings/angle-baseline_extraction.md` §2.5 — append as new rows under the BLACKLIST table with `source = <folder>, ch = <n>` provenance.

**Audit events:**

```json
{"event":"validation.issue.raised","level":"copyright_clearance","check":"V-CR-7","severity":"blocker","reason":"BLACKLIST_NOT_EXTENDED","folder":"<folder>","new_entities":["<term1>","..."],"ts":"<ISO8601>"}
{"event":"validation.issue.raised","level":"copyright_clearance","check":"V-CR-7","severity":"blocker","reason":"SIGN_OFF_MISSING_GAP_NOTE","ts":"<ISO8601>"}
{"event":"validation.pass","level":"copyright_clearance","check":"V-CR-7","empty_folders_downloaded":<bool>,"blacklist_extended":<bool>,"ts":"<ISO8601>"}
```

## 3. The seed BLACKLIST (14-baseline distinctive entities — verbatim from `findings/angle-baseline_extraction.md` §2.5)

> Canonical seed. Stage 6's `copyright_clearance.md` BLACKLIST section MUST be this table, byte-identical.

| 类别 | 具名实体 | 源基线 + 章节 | 类型化后是否可保留？ |
|---|---|---|---|
| 神器 / 金手指 | 天玄镜 | wode_moni_changsheng_lu, ch50 | 概念（商店类系统镜）→ ok，名字必须换 |
| 神器 / 金手指 | 道碑（识海内古碑） | zhen_wen_changsheng, ch01–02 | 概念（识海器灵）→ ok 但需重新设计样态 |
| 神器 / 金手指 | 鉴子（圆形发光物 / 器灵） | xuanjian_xianzu, ch01 | 概念太独特，建议整体规避 |
| 神器 / 金手指 | 紫水晶（神灵尸身吸取） | guangyin_zhiwai, ch02–03 | 类型可（治疗型宝物），具名禁用 |
| 神器 / 金手指 | 珠子（两界穿梭） | gou_zai_liangjie_xiuxian, ch01–02 | 双界穿梭机制本身在 gou_zai_yaowu 也出现，但 gou_zai_liangjie 的"珠子"具名禁用 |
| 神器 / 金手指 | 玄天胎息丹（丹王炼） | jie_jian, ch48 | 类型可（突破丹），具名禁用 |
| 宗门 | 七玄门（七绝堂、百锻堂） | fanren_xiuxian_zhuan, ch02–05 | 模式可（"X 玄门 / X 绝堂"），具名禁用 |
| 宗门 | 通仙门（嫡传/内门/外门 + 猎妖堂） | zhen_wen_changsheng, ch01–03 | 模式可，具名禁用 |
| 宗门 | 问道宗、悬空庙、丹霞帮 | shei_rang_ta_xiuxian_de + shan_he_ji | 同上 |
| 宗门 | 碧海门、玉芽丹（突破丹） | gou_zai_liangjie + xuanjian_xianzu | 具名禁用 |
| 宗门 | 万仙盟 | wode_moni_changsheng_lu, ch100 | 具名禁用 |
| 功法 | 太阴吐纳练气诀 / 月华纪要秘旨 | xuanjian_xianzu, ch01 | 具名禁用 |
| 功法 | 月阙剑弧、玄水剑诀 | xuanjian_xianzu, ch99 | 具名禁用 |
| 功法 | 炼剑诀 | jie_jian, ch48 | 具名禁用（虽朴素，仍禁） |
| 阵法 | 铁甲阵（六道阵纹） | zhen_wen_changsheng, ch100 | 类型可（防御阵），具名禁用 |
| 阵法 | 五行阵法基础阵纹 | zhen_wen_changsheng, ch01 | "五行" 是通用概念，可保留 |
| 妖物 | 石龙子（不入阶妖虫） | gou_zai_yaowu_luanshi, ch01 | 具名禁用 |
| 妖物 | 吴柞虫（吐丝织灵布） | xuanjian_xianzu, ch99 | 具名禁用 |
| 妖物 | 缠香丝（毒物） | fanren_xiuxian_zhuan, ch50 | 具名禁用 |
| 地名 | 玄京、温县、江淮府、琅琊王府、嘉元城、岚州、青牛镇、彩霞山、落日峰、仙霞山 | wode_moni + fanren | 具名禁用 |
| 地名 | 通仙城、墨山、大黎山、眉尺河、黎泾村 | zhen_wen + xuanjian | 具名禁用 |
| 地名 | 青竹山坊市、南荒修仙界、越国 | gou_zai_yaowu | 具名禁用 |
| 地名 | 碧玉岛、巴郡、三水坳、天府城、大凉世界、黑石城 | gou_zai_liangjie | 具名禁用 |
| 地名 | 镜州、镜州城、夏州、京师 | fanren + shan_he_ji | 具名禁用 |
| 地名 | 嵩阳高中（仙道高中） | meiqian_xiu_shenme_xian | 具名禁用 |
| 地名 | 玄黄界 / 东洲（游戏世界） | jie_jian | 具名禁用 |
| 人物 | 韩立、墨大夫、舞岩、岳堂主、王护法、张铁、张均（fanren）；李凡、宣景帝、琅琊王、孙二狗（wode_moni）；墨画、白子胜、白子曦、安少爷、严教习、俞长老、墨山（zhen_wen）；方夕、方青、阿福、查老汉、珠儿（gou_zai 双本）；陆行舟、盛元瑶、柳擎苍、柳烟儿、白驰、霍家（shan_he_ji）；陆阳、孟景舟、戴不凡、云芝（shei_rang）；楚槐序、韩霜降（jie_jian）；张羽、王海（meiqian）；陆江仙 / 李项平 / 李木田 / 李通崖 / 李玄宣 / 田芸（xuanjian）；许青（guangyin） | 各对应基线 | 全部具名禁用 — 主角名、姓氏组合都要避开 |

**Stage 6 grep-flatten rule:** the parent expands all the comma- / "/"-separated entity lists above into individual atomic terms before grepping. The compound entries above (e.g., "玄京、温县、江淮府、…") are not greppable as one literal — they must be tokenized first. Stage-6 implementer: split on Chinese comma (`、`), Western comma (`,`), Chinese semicolon (`；`), slash (`/`), and parenthetical glosses, then trim whitespace. The expected expansion of this seed table yields **≈ 95 atomic terms** (see §5 Implementation pseudocode for the tokenizer).

**Supplementary literal-only seed (from `angle-character_anonymization.md` §2.1 — auxiliary corpus widening):**

In addition to the §2.5 distinctive entities above, the `character_anonymization` angle's §2.1 BLACKLIST adds the following named entities scraped from chapters 1-3 of each baseline + `_meta.json` chapter titles. These augment §2.5 with longer-corpus coverage. Stage 6 MUST add these atomic terms to the BLACKLIST as well:

| 类别 | 具名实体 |
|---|---|
| 主角兄长 (fanren) | 韩铸 |
| 宗门 (fanren) | 清虚门 / 掩月宗 / 天星宗 / 鬼灵门 |
| 魔门 (fanren) | 黑煞教 |
| 阁殿 (fanren) | 星尘阁 / 登仙阁 / 岳麓殿 |
| 地名 (fanren) | 百莽山 |
| 同辈反派 (gou_zai_liangjie) | 麻老三 |
| 设定 (gou_zai_liangjie) | 值岁 / 亢金 |
| 地名 (gou_zai_liangjie) | 古蜀 |
| 家族 (gou_zai_liangjie) | 罗家 / 方家 |
| 邻居 (gou_zai_yaowu) | 老麦头 |
| 家族 (gou_zai_yaowu) | 司徒家 |
| 功法 (gou_zai_yaowu) | 长春诀 |
| 灵植 (gou_zai_yaowu) | 翠玉碧竹 / 碧玉竹米 |
| 场所 (gou_zai_yaowu) | 醉仙楼 |
| 地名 (guangyin) | 南凰洲 / 望古 |
| 设定 (guangyin) | 异质 / 异化点 / 末土 |
| 功法 (jie_jian) | 万剑归宗 / 剑宗 / 剑尊 |
| 学校 (meiqian) | 嵩阳高中 / 东阳初级中学 / 魔教 |
| 功法 (meiqian) | 元阴链气之术 |
| 女官 (shan_he_ji) | 盛元瑶 |
| 反派 (shan_he_ji) | 元慕鱼 |
| 家族 (shan_he_ji) | 霍家 / 裴府 |
| 宗门 (shan_he_ji) | 天行剑宗 / 姹女合欢宗 / 冰狱宗 / 罗生门 |
| 地区 (shan_he_ji) | 夏州 / 大干国 |
| 帮派 (shan_he_ji) | 丹霞帮 / 丹霞山 |
| 司 (shan_he_ji) | 镇魔司 / 丹药司 |
| 仇敌 (wode_moni) | 道玄子 / 寇洪 |
| 政体 (wode_moni) | 大玄国 / 太师府 |
| 宗门 (wode_moni) | 紫霄宗 / 朝元宗 / 御兽宗 / 偷天换日宗 / 药王宗 |
| 阁 (wode_moni) | 传法阁 / 万藏阁 / 三茳阁 |
| 设定 (wode_moni) | 仙凡瘴 |
| 功法 (xuanjian) | 太阴吐纳练气诀 / 月华纪要秘旨 |
| 宗门 (xuanjian) | 仙宗 / 青迟魔门 / 五行宗 / 乾道宗 / 太虚门 / 苍云宗 / 小灵隐宗 / 藏阵阁 |
| 家府 (xuanjian) | 紫府 / 水府 / 芮家峰 |
| 同辈对照 (zhen_wen) | 安少爷 |
| 大族 (zhen_wen) | 钱家 / 洛府 |

**Note on "裴" surname collision risk:** the `shan_he_ji` BLACKLIST includes "裴府" as a family/region term. Our protagonist is **裴知秋** — surname collision but full-name distinct. Stage-6 grep tokenizer MUST atomize on full-tokens only ("裴府" → grep "裴府" as a single literal, NOT a "裴" wildcard). Our 裴知秋 / 裴长砚 should not trigger this row. This is an acknowledged collision-risk-margin item flagged here for the SIGN-OFF section to call out explicitly.

## 4. The mozun seed BLACKLIST (sample-extracted from `ai_videos/mozun_chongsheng/characters/` + `world.md`)

> Sample read of the sibling project. Stage 6 EXTENDS this seed at runtime by recursive grep across all `ai_videos/mozun_chongsheng/**/*.md` to capture entities introduced in `episodes/`, `scenes/`, and `arc_outline.md` files not sampled here.

### 4.1 Characters (10 named — from `characters/c*/` folders)

| 编号 | 名 | 角色 |
|---|---|---|
| c1 | 沧冥 | 男主前世魔尊 |
| c2 | 叶无尘 | 男主转生形态 |
| c3 | 苏璃月 | 主女主（紫霄宫圣女）|
| c4 | 柳红袖 | 副女主 1（红袖招老板娘）|
| c5 | 苓夭夭 | 副女主 2（药王谷女医师）|
| c6 | 白月清 | 紫霄宫宗主（反派 1）|
| c7 | 赵焚天 | 玄炎宗宗主（反派 2）|
| c8 | 方鼎元 | 太清门宗主（反派 3）|
| c9 | 韩夺心 | 万剑宗宗主（反派 4）|
| c10 | 司空玄 | 影神殿宗主（反派 5）|

### 4.2 Sects / Factions (from `world.md` § 五大宗派 + § 三界对峙)

- **正派盟**: 中州五道盟 · 紫霄宫 · 玄炎宗 · 太清门 · 万剑宗 · 影神殿
- **魔界**: 沧冥魔域 · 九幽之地

### 4.3 Locations (from `world.md` § 关键地点 + `scenes/`)

- 沧冥魔域 / 九幽之地 / 乞丐城 / 红袖招酒楼 / 紫霄宫 / 玄炎宗（铸器堂 + 血池） / 药王谷 / 太清门金殿 / 万剑宗悬剑殿 / 影神殿密室 / 中州论道大会场 / 碧落殿 / 中州
- Scene tokens (from `scenes/`): 长阶顶 / 大殿内 / 铸器堂 / 金殿密室 / 破庙 / 雪山 / 山道平台 / 云海 / 识海

### 4.4 Artifacts / Cultivation system (from `world.md` § 关键道具 + § 男主魔功)

- **魔功 (9 阶)**: 黑息引 · 九幽指 · 九幽噬魂掌 · 魔气化龙 · 血色雷 · 魔影分身 · 虚空蚀心 · 血雨九重劫 · 星辰魔阵·沧冥归位
- **丹药体系 (具名禁用 4)**: 聚气丹 / 化神丹 / 大乘丹 / 渡劫保命丹 — note: "金丹" 是境界通用术语，不在 BLACKLIST 范围内
- **境界 10 阶系统**: 练气-筑基-金丹-元婴-化神-合体-大乘-渡劫-真仙-圣人 — 通用术语不入 BLACKLIST，但 "圣人 / 沧冥归位" 复合名禁用

### 4.5 Mechanics (semantic, not grep-able — manual review)

- 男主独占金手指 = **系统** + 三轨混合（任务 / 双修 / 丹药）
- 双修破境机制（红绳缠手 / 莲花共开 / 灵泉双沐 visual tokens）

### 4.6 Recursive-grep supplement (stage 6 runtime)

Stage 6 MUST also recursively grep `ai_videos/mozun_chongsheng/{episodes/,scenes/,arc_outline.md,casting.md}` for any named-entity tokens not in §4.1–§4.4 above (e.g., minor characters mentioned in episode scripts, scene-specific prop names). Heuristic for extraction: any Chinese 2–4 字 token preceded by a 角色/场景/道具 header in those files. Add all extracted tokens to the BLACKLIST grep set.

**Net mozun seed (§4.1 + §4.2 + §4.3 + §4.4 atomic terms only):** ≈ 50 atomic terms before recursive supplement.

## 5. Grep implementation pseudocode (stage 6 reference)

```bash
#!/usr/bin/env bash
set -euo pipefail

CC_FILE="my_novel/feng_shou_lu/copyright_clearance.md"
PROJECT_GLOB=("my_novel/feng_shou_lu" "ai_videos/feng_shou_lu")
MOZUN_GLOB="ai_videos/mozun_chongsheng"
AUDIT_EVENTS=".audit/adhoc_agents/$(date +%F)/${TASK_ID}/events.jsonl"

emit() { echo "$1" >> "$AUDIT_EVENTS"; }

# --- V-CR-1: file + section existence ---
[ -f "$CC_FILE" ] || { emit '{"event":"validation.issue.raised","check":"V-CR-1","severity":"blocker","reason":"file_missing"}'; exit 1; }
for section in BLACKLIST mozun PROPOSED DELTA; do
    grep -qF "$section" "$CC_FILE" || \
        emit "{\"event\":\"validation.issue.raised\",\"check\":\"V-CR-1\",\"severity\":\"blocker\",\"reason\":\"section_missing:$section\"}"
done

# --- Tokenize the BLACKLIST table into atomic terms ---
# Heuristic: take column-2 cells of every | A | B | C | row in sections 1 and 2,
# then split each cell on these delimiters: 、 ， ； / 「」 （） and trim.
TERMS=$(awk -F'|' '/^\|/ && NR>2 { print $3 }' "$CC_FILE" \
    | tr '、，；/「」（）()' '\n' \
    | sed 's/^[[:space:]]*//; s/[[:space:]]*$//' \
    | grep -v '^$' \
    | grep -v '具名禁用\|类型化\|---' \
    | sort -u)

# --- V-CR-2: auto-grep gate ---
files_scanned=0; hits=0
while IFS= read -r path; do
    [ "$path" = "$CC_FILE" ] && continue   # whitelist exemption
    files_scanned=$((files_scanned + 1))
    while IFS= read -r term; do
        # literal-match, UTF-8, case-sensitive Han matters → use grep -F (no regex)
        if grep -nF -- "$term" "$path" > /tmp/hits 2>/dev/null; then
            while IFS=: read -r lineno line_text; do
                hits=$((hits + 1))
                emit "{\"event\":\"validation.issue.raised\",\"check\":\"V-CR-2\",\"severity\":\"blocker\",\"reason\":\"BLACKLIST_HIT\",\"term\":\"$term\",\"file\":\"$path\",\"line\":$lineno}"
            done < /tmp/hits
        fi
    done <<< "$TERMS"
done < <(find "${PROJECT_GLOB[@]}" -name '*.md' 2>/dev/null)
[ "$hits" -eq 0 ] && emit "{\"event\":\"validation.pass\",\"check\":\"V-CR-2\",\"terms_checked\":$(echo "$TERMS" | wc -l),\"files_scanned\":$files_scanned}"

# --- V-CR-3: etymology preservation (loop over character bibles) ---
# Implemented inline per §2 V-CR-3 spec; uses an awk-extracted reference etymology dict.

# --- V-CR-4: cross-project mozun grep ---
# Our project's named entities → extract from filenames + world.md table rows + scenes/ filenames
OUR_NAMED=$(
    ls my_novel/feng_shou_lu/characters/*.md 2>/dev/null | xargs -n1 basename | sed 's/\.md$//';
    ls my_novel/feng_shou_lu/scenes/*.md 2>/dev/null     | xargs -n1 basename | sed 's/\.md$//; s/^s[0-9]*_//';
    grep -hoE '(赤霞门|九寰阁|澹台宗|流烛盟|忘川教|焚寿罗盘|残忆经|偿岁真言|归砚镜|长烟幡|澹江洲|落雁渊|栖梧崖|乌泽)' \
        my_novel/feng_shou_lu/world.md 2>/dev/null
) | sort -u

while IFS= read -r entity; do
    grep -rnF --include='*.md' -- "$entity" "$MOZUN_GLOB" 2>/dev/null \
        | while IFS=: read -r mozun_file lineno _; do
            emit "{\"event\":\"validation.issue.raised\",\"check\":\"V-CR-4\",\"severity\":\"blocker\",\"reason\":\"CROSS_PROJECT_COLLISION\",\"entity\":\"$entity\",\"mozun_file\":\"$mozun_file\",\"line\":$lineno}"
        done
done <<< "$OUR_NAMED"

# --- V-CR-5: wode_moni fingerprint ---
WODE_MONI_PHRASES=("太师寿宴" "流星仙人斗法" "仙凡瘴" "锚定" "天玄镜" "万仙盟" "玄京" "琅琊王" "温县" "江淮府" "李凡")
for phrase in "${WODE_MONI_PHRASES[@]}"; do
    grep -rnF --include='*.md' -- "$phrase" "${PROJECT_GLOB[@]}" 2>/dev/null \
        | grep -v "$CC_FILE" \
        | while IFS=: read -r path lineno _; do
            emit "{\"event\":\"validation.issue.raised\",\"check\":\"V-CR-5\",\"severity\":\"blocker\",\"reason\":\"WODE_MONI_FINGERPRINT\",\"phrase\":\"$phrase\",\"file\":\"$path\",\"line\":$lineno}"
        done
done

# semantic simulator hint (warning only)
SEMANTIC_HINTS=("无成本" "无限重来" "无代价重活" "无成本重来" "无消耗重活")
for hint in "${SEMANTIC_HINTS[@]}"; do
    grep -rnF --include='script.md' -- "$hint" my_novel/feng_shou_lu/episodes/ 2>/dev/null \
        | while IFS=: read -r path lineno _; do
            emit "{\"event\":\"validation.issue.raised\",\"check\":\"V-CR-5\",\"severity\":\"warning\",\"reason\":\"WODE_MONI_SIMULATOR_SEMANTIC\",\"hint\":\"$hint\",\"file\":\"$path\",\"line\":$lineno}"
        done
done

# --- V-CR-6: SIGN-OFF append (only on full pass of V-CR-1..5) ---
if [ "$hits" -eq 0 ] && [ "$(check_other_levels_pass)" = "yes" ]; then
    {
      echo ""
      echo "## SIGN-OFF"
      echo ""
      echo "- **Timestamp (UTC):** $(date -u +%FT%TZ)"
      echo "- **Grep-pass status:** PASS (V-CR-1..5 all green)"
      echo "- **BLACKLIST terms checked:** $(echo "$TERMS" | wc -l) atomic terms"
      echo "- **Files scanned:** $files_scanned"
      echo "- **Zero-hit confirmation:** yes"
      echo "- **Validator agent id:** level-specialist-05-copyright_clearance (task_id ${TASK_ID})"
      echo "- **Empty-baseline gap (CCI-6):** ${CCI6_STATUS}"
    } >> "$CC_FILE"
    emit "{\"event\":\"validation.pass\",\"check\":\"V-CR-6\",\"sign_off_appended_to\":\"$CC_FILE\"}"
fi

# --- V-CR-7: empty-folder check ---
EMPTY=("cong_jianshu_xiuxing" "gou_zai_xiuxianjie" "zhutian_daozu")
for folder in "${EMPTY[@]}"; do
    if [ -d "downloaded_novels/xianxia/$folder/chapters" ] && \
       [ -n "$(ls -A "downloaded_novels/xianxia/$folder/chapters" 2>/dev/null)" ]; then
        # downloaded since stage 3 — must verify BLACKLIST was extended
        if ! grep -qF "source = $folder" "$CC_FILE"; then
            emit "{\"event\":\"validation.issue.raised\",\"check\":\"V-CR-7\",\"severity\":\"blocker\",\"reason\":\"BLACKLIST_NOT_EXTENDED\",\"folder\":\"$folder\"}"
        fi
    else
        # still empty — sign-off must declare gap
        if ! grep -qF "OPEN — BLACKLIST under-spec'd by 3 baselines" "$CC_FILE"; then
            emit "{\"event\":\"validation.issue.raised\",\"check\":\"V-CR-7\",\"severity\":\"blocker\",\"reason\":\"SIGN_OFF_MISSING_GAP_NOTE\"}"
        fi
    fi
done
```

## 6. Summary counts (for SIGN-OFF preview)

- **§3 (14-baseline) atomic terms after tokenization:** ≈ **95** unique terms.
- **§4 (mozun_chongsheng) atomic terms from sample reads (§4.1–4.4):** ≈ **50** unique terms; supplemented by stage-6 recursive grep.
- **§ V-CR-5 wode_moni forbidden phrases:** **11** literal phrases (subset of §3 with extra paranoia per CCI-1).
- **Highest-risk accidental-use term (rank 1):** `万仙盟` — it appears in BOTH §3 (wode_moni baseline) AND is a structurally tempting name for our 正派 sect alliance (we landed on `中州五道盟` for mozun but our own project's normalized "X 盟" instinct for the 散修 organization risks accidentally generating `万仙盟`-shaped names like "万x盟"). Stage-6 author must consciously avoid the 万-prefix-盟 pattern.
- **Highest-risk accidental-use term (rank 2):** `沈烬` (from `angle-character_anonymization.md` §2.3 web-collision); not in §3 grep but tracked in CCI-2 as the most-likely accidental-rename-candidate if any author edits push toward "烬" semantic family. Add to BLACKLIST under a §3 "web-collision" sub-table at stage 6.

## 7. Stage-6 recommendation on V-CR-7 / CCI-6

**Recommendation (this validator's stance):** stage 6 SHOULD proceed without blocking on the empty-folder补抓 for the ep01 MVP run. Rationale:

1. The "generic ≥ 3 sources" baseline-extraction reuse threshold is satisfied many times over by the 11 readable baselines; the 8-stage ladder + 三方格局 conclusions are robust.
2. The risk surface from the 3 empty folders is **only** the rename BLACKLIST under-spec — not the structural conclusions.
3. The user-shifted MVP scope (per follow-up 001) is iterative; ep02+ runs naturally re-open stage 5, which will catch any name conflict the补抓 surfaces.
4. **Hard requirement:** the SIGN-OFF block MUST carry the explicit "OPEN — BLACKLIST under-spec'd by 3 baselines (cong_jianshu_xiuxing, gou_zai_xiuxianjie, zhutian_daozu); flag for re-validation when downloaded" gap-note (V-CR-7 enforces this).

If, however, the user wants belt-and-braces, the cheap path is firing a补抓 follow-up to `specs/development/ai_video_management/` BEFORE stage 6 starts. That doesn't change V-CR-7's logic — it just shifts the SIGN-OFF gap-note to the "RESOLVED" branch.
