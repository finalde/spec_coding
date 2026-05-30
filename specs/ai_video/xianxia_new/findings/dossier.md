# Findings dossier — xianxia_new (working slug)

Run: `xianxia_new-20260524-101931`
**task_type:** ai_video · **sub_type:** novel · **genre:** xianxia (locked)
**Synthesized:** 2026-05-24
**Synthesis confidence:** high (3 angles complete, 1 partial — `baseline_extraction` saw 11 of 14 baselines; conclusions hold because the corpus-generic threshold ≥3 books is well-satisfied by the readable subset)

## Angles researched

1. **baseline_extraction** — what reusable structural elements are common across the 14 baseline xianxia novels, and which named entities must be renamed/reworked.
2. **trend_research** — what's working / failing in 2025–2026 xianxia 短剧 + 网文 + Douyin / 红果 / 小红书 discourse, with citations.
3. **visual_style** — concrete style-guide draft: cinematography vocabulary, lighting palette (named + hex), motion vocabulary, sect/魔门 visual distinctions, transformation visual signature for parasitic level-ups.
4. **character_anonymization** — anonymization rules + final candidate naming table for protagonist / betrayers / sects / 功法 / 神器 / locations, with WebSearch collision verification per name.

## Cross-cutting insights

### CCI-1 — `wode_moni_changsheng_lu` is both the strongest triangulation target AND the highest collision risk
*(baseline_extraction + character_anonymization)*
Of all 14 baselines, only `wode_moni_changsheng_lu` (我的模拟长生路) carries a *true* "重生 + revenge + system" protagonist. Every other baseline is穿越 (transplanted-modern-soul), not 重生. This makes wode_moni the **inspiration of choice for narrative cadence** (rebirth panic → calibration → revenge sequencing) AND the **#1 forbidden-zone** for字面 carryover. Concretely: `太师寿宴` / `流星仙人斗法` / `仙凡瘴` / `锚定 N 年` / `天玄镜` / `万仙盟` / `玄京` / `琅琊王` / `温县` / `江淮府` / `李凡` are ALL forbidden. The differentiator must live on the **cost axis**:李凡的 simulator is cost-free reruns; our parasitic system charges 寿命/记忆 per level-up. This is non-negotiable for stage-5 copyright clearance.

### CCI-2 — The "parasitic / loss-system" concept has near-zero competitive precedent in 2025–2026
*(trend_research + character_anonymization)*
trend_research's Q5 open question came up empty: no head 网文/短剧 in 2025–2026 has shipped a "system that costs you something per level-up" with the lifespan/memory mechanic we locked in qa.md Q12. The closest is《风华鉴》("每次重生都在燃烧男主的生命") but that's reincarnation-cost, not system-cost. **This is the project's load-bearing differentiator** — and it pairs perfectly with character_anonymization's name design (《残忆经》 = memory-erase; 焚寿罗盘 = 24-tick lifespan dial; 《偿岁真言》 = rival functor that turns the system into a stealable artifact). Our naming and mechanic are mutually reinforcing — every artifact name is also a hint at the system's nature, which the parent character_anonymization angle already wired into the 5-stage reveal cadence (ep01 / ep08 / ep17 / ep28 / ep49).

### CCI-3 — AI-short-drama visual strengths align with our parasitic-cost beats; weaknesses align with what we already wanted to drop
*(trend_research + visual_style)*
trend_research found the audience explicitly tired of "御剑骑共享单车 / 群战法宝乱舞" and AI can't render those reliably anyway. Conversely, AI is *strong* at transformation / 渡劫 / 灵气漩涡 / 心法觉醒 / 月夜独行 / 山门洞府 — exactly the beats our parasitic-cost design needs (5s "寄生升级 motif" with red-字 寿命计数器 + 三拍 顿挫). **The visual budget bottleneck becomes a feature, not a bug.** visual_style's "12-state lighting dictionary" (mozun baseline's 10 states + new `寄生 aura` and `寿命流失` states) is the operational expression of this.

### CCI-4 — Naming convergence around "水墨 + 寿尽" semantic cluster is internally consistent and externally differentiated
*(character_anonymization + visual_style)*
character_anonymization landed on a naming family sharing the glyph cluster 砚 / 漪 / 川 / 烟 / 秋 / 忆 / 寿 (intentional water-ink + lifespan motif). visual_style independently picked a灰青 + 月白 + 寄生紫 palette for the protagonist's two-state visual signature. **The naming and the palette point at the same aesthetic** — water/ink/秋叶 motifs → grey-blue/灰青 chromatic family → the protagonist's clothing/etymology/setting reinforce each other. AND this palette is intentionally orthogonal to the sibling mozun_chongsheng project's 黑/金/紫霄/朱砂 cluster, so the two projects' Seedream ref-images won't cross-contaminate.

### CCI-5 — Paid-conversion node placement, cliffhanger catalog, and the 5-stage reveal cadence are all temporally aligned at the same 5 episodes
*(trend_research + character_anonymization)*
trend_research's paid-conversion theory says ep10 / ep30 / ep50 / ep60 are the load-bearing payment nodes (70% / 25% / 5% / season-end). character_anonymization's reveal cadence independently lands these revelations at ep08 / ep17 / ep28 / ep49 / ep60 — within ±2 episodes of the paid nodes for nodes 1/3/4 and exactly at node 5. **Stage 4 should lock the reveals AT the paid nodes** (ep10 = "归砚镜 first awakened + first 寿命 cost crash"; ep30 = "《偿岁真言》 vs《残忆经》 mirror revealed"; ep50 = "protagonist IS the system's origin"; ep60 = "parasitic 代价 真正兑现"). This makes every paywall a revelation; every revelation a paywall. Clean.

### CCI-6 — The "11 of 14 baselines" gap doesn't undermine corpus-generic conclusions but DOES leave the rename blacklist slightly under-spec'd
*(baseline_extraction)*
3 of 14 baseline folders (`cong_jianshu_xiuxing`, `gou_zai_xiuxianjie`, `zhutian_daozu`) are empty on disk and produced no readable content. The "generic ≥ 3 sources" rule for safe reuse is satisfied many times over by the 11 readable books, so corpus-generic conclusions (8-stage ladder, trifecta格局, recurring locations) are robust. The RISK: the rename blacklist for distinctive entities may grow when the 3 empty books are downloaded. Recommendation: fire a补抓 follow-up under `specs/development/ai_video_management/user_input/follow_ups/` to re-run the downloader BEFORE stage 5's copyright_clearance validator runs (stage 4 can proceed without). User to confirm at stage 4 review whether to block stage 5 on this.

### CCI-7 — Some trend-research sources were unreachable; cite-second-source recommended
*(trend_research)*
≥ 7 high-value sources (paper.cn / 36kr / huxiu / boyamedia, several zhuanlan.zhihu.com links) returned 403 Forbidden or timeout under WebFetch. Trend conclusions used WebSearch titles + summaries + cross-source corroboration as a workaround, with `confidence: medium` self-reported. **Stage 5 should treat any specific numeric claim sourced exclusively from these blocked domains as "needs human verification"** before letting it influence acceptance criteria.

---

## Per-angle highlights

### baseline_extraction
- **Safe to reuse verbatim:** 8-stage ladder (练气-筑基-金丹-元婴-化神-炼虚-合体-大乘) — ≥9 of 11 readable baselines align literally; 三方格局 (正/散/魔) — ≥5 baselines have all three; door-pattern "外门 / 内门 / 嫡传" — ≥4 baselines.
- **Recurring scenes safe to lock down for stage 4 (≥3 baseline appearance each):** 山门石阶 / 修炼洞府 / 丹房 / 灵田竹林 / 密林月夜 / 演武场 / 山顶悬崖 / 坊市 / 宗门议事大殿 / 阵法密室. Drop entirely: 海岛渔村, 末世废墟血雨 (single-baseline + AI gen instability).
- **Naming-fingerprint blacklist for stage 3/4:** surnames 陆 / 方 / 李 / 韩 / 张 / 墨 / 楚 / 许; sect prefixes 七 / 通 / 问 / 碧 / 丹 / 万仙 / 玄.

### trend_research
- **MUST-avoid saturated tropes (5):** 工业糖精白月光恋爱线 · 师父工具人 + 单线智商反派 · 圣母「我重生了但我要原谅」 · 「100集违法乱纪最后强行自首」式 ex-machina 救赎收尾 · 御剑骑共享单车 / 群战法宝乱舞视觉密度.
- **Verbatim-borrowable hook template:** 死亡开局 (前 3秒：渡劫雷劫劈下 / 灭门火光 / 被剑刺穿) → 重生 + 系统觉醒 + 代价已计算 (ep01 倒数 15秒).
- **Cliffhanger 8-class catalog** for 60-ep rotation: 好奇 / 借势 / 痛点 / 极限 / 恐吓 / 反差 / 利益输送 / 同理心.
- **Paid-conversion node theory** (70% / 25% / 5% rule): ep10 / ep30 / ep50 / ep60.
- **Confidence:** medium (cross-source corroboration; several high-value sources blocked per CCI-7).

### visual_style
- **Adopt verbatim from mozun_chongsheng baseline:** 亚洲俊男靓女审美 11-item negative list + 演员锚点表 + follow-up 012 photorealism (24+ 正向 / 14 负向) + Seedream 四段式 + 9:16 竖屏铁律 + 字幕规范 + 转场词典 8 类 + 景别词典 13 类.
- **Project-unique additions:** 双形态契约 (state A 重生弱体 vs state B 寄生觉醒) · 5s 寄生升级 motif 三拍 · 12-state lighting (mozun's 10 + `寄生 aura` `#4a1a5a` + `寿命流失` red `#a82c2c`) · 6-faction palette · 寿命计数器过 transition · 12 project-specific negatives.
- **Production risk:** Seedream may struggle with 寄生紫 `#4a1a5a` in low-saturation 9:16 (purple tends to read black). Mitigation: stage-4 validates both states from the same Seedream prompt; fallback hex `#5a2a6a` (+10% L+S); stage-5 validator checks "两 state 同人识别" (Δ ≤ 15% face-differentiator hex shift between states).

### character_anonymization
- **Naming cluster (water-ink + lifespan):** glyphs 砚 / 漪 / 川 / 烟 / 秋 / 忆 / 寿. Surname pool: 裴 / 闻 / 容 / 卫 / 应 / 戚 / 池 / 阮 / 言. Sect stems: 赤霞 / 九寰 / 澹台 / 流烛 / 忘川.
- **Web-checked, zero-collision final names** (verified against 2025–2026 head xianxia 网文 + 短剧):
  - 主角: **裴知秋** (前世 **裴长砚**, ep17 reveal)
  - 师父: **闻砚清** (前世师父, dead in ep01 倒叙)
  - 主女主: **容漪** (散修盟; ep28 reveal that she's a 忘川教-planted memory backup)
  - 5+1 反派 (cross-faction): **卫长烛** 正派赤霞门 / **应砚之** 朝堂 / **戚归砚** 散修盟暗投魔门 / **池洇** 散修盟杀手 / **阮惘** 忘川教三长老 / **言息** 忘川教教主 (final boss)
  - 5 件 signature 神器/功法: **《残忆经》** (主角功法 — 修一章失一段记忆) / **焚寿罗盘** (24-tick lifespan dial = system 物化) / **《偿岁真言》** (魔门 mirror functor; ep20 revealed as the SOURCE of《残忆经》) / **归砚镜** (师父遗物 → reveal-engine across ep08/28/49) / **长烟幡** (散修长老遗物 → 主女主转交主角 ep35)
  - 3 派组织: **赤霞门** (剑宗) / **九寰阁** (藏书+阵法) / **澹台宗** (御剑冷静派) / 散修 **流烛盟** / 魔门 **忘川教**
  - 3 锚点地名: **澹江洲** (转生地) / **落雁渊** (ep01 系统觉醒处) / **栖梧崖** (旧名 "无寿崖", 前世坐化处)
  - 灵兽: **乌泽** (主角灵兽 — 水鸟, 能以己寿换主角寿)
- **Near-collisions caught and replaced:** `沈烬` → blocked (collides with 影子爱人 短剧 / 长生烬 晋江 / 烬灭之力 QQ); entire `烬` semantic family black-listed. `青冥剑宗` → blocked (collides with 炼气练了三千年 Tencent/Bilibili manga); replaced by `赤霞门`.

---

## Recommendations for the spec (stage 4 inheritance)

### R-1 — Title and slug (open question — surface in stage 4 review gate)
Working slug `xianxia_new` should be replaced. Candidates derived from the naming cluster:
- 《焚寿录》 (féng shòu lù) — slug `feng_shou_lu` — directly names the focal artifact + suffix "录" (chronicle) matches the "memoir/erasure" motif.
- 《残忆长砚》 (cán yì cháng yàn) — slug `can_yi_chang_yan` — combines the functional system (memory-loss) with the former-life name.
- 《知秋不返》 (zhī qiū bú fǎn) — slug `zhi_qiu_bu_fan` — protagonist-name forward, "autumn knows but cannot return" double-entendre for the lifespan motif.

Stage 4 picks one; folder rename `mv specs/ai_video/xianxia_new/ specs/ai_video/{final_slug}/` happens at stage 4 approval gate, plus `my_novel/{final_slug}/` and `ai_videos/{final_slug}/` creation.

### R-2 — Stage 4 inherits the character bible verbatim
character_anonymization's `§3 Implications` (3.1–3.6) is the seed for `my_novel/{slug}/characters/`. Stage 4 produces one file per named character following `agent_refs/project/ai_video.md` rule 12.1 (10-field locked descriptor + 一句话锁定 line) — names + etymologies come from the angle file unchanged; face/服装/气质 fields are filled in stage 4 from the visual_style angle's 6-faction palette + 双形态契约 framework.

### R-3 — Stage 4 inherits the style_guide verbatim
visual_style's `§3` (camera language / lighting state / palette per setting / 双形态 / 寄生升级 motif / negative-prompt / aspect ratio / subtitle) is the seed for `my_novel/{slug}/style_guide.md` (and the parallel `ai_videos/{slug}/style_guide.md`). Stage 4 lifts with minimal edits — primarily replacing the working `xianxia_new` slug with the final pick from R-1.

### R-4 — Episode 1 design (concrete)
- **First 3 seconds:** 渡劫雷劫劈下 — 裴长砚（前世）于「无寿崖」(later renamed 栖梧崖) 渡劫，雷劫第三道劈下，背后剑光起。被剑刺穿瞬间镜头切。
- **Cold open 0:03–0:30:** 倒叙 quick-cut montage — 5 reasons-to-trust shots of the 5 betrayers (卫长烛递剑给他 / 应砚之联名上奏 / 戚归砚发誓共生 / 池洇受恩 / 阮惘救命 / 言息授业) — all reversed in the next 5 seconds as the 5 reasons-to-die (剑回到自己心口 / 上奏改成弹劾 / 共生誓变背刺 / 受恩反噬 / 救命变绞杀 / 授业藏祸).
- **0:30–1:30:** 主角苏醒于 7 岁练气体, 在 落雁渊 渊底; 焚寿罗盘 (24格) 从胸前浮起; 系统红字弹出「代价已计算 · 寿元 -1 / 修为 +1」.
- **Final 15 seconds (ep01 cliffhanger):** 主角自取新名「裴知秋」(水边题字); 远处出现「师父闻砚清」剪影 → 师父正常出现 / 倒叙中已死的师父在本世活着. Cut to black + 闪黑 transition + 「第二集 即将揭晓」字幕.

This satisfies CCI-3 (transformation/觉醒 visual beats) + R-2 reveal cadence + trend_research's "死亡开局 + 系统觉醒 + 代价已计算" hook template.

### R-5 — Recurring scenes to lock at stage 4 (≥6 of these 10)
Per baseline_extraction §2.6 — these are corpus-generic, prop-light, and AI-gen friendly. Recommend stage 4 declare at least: 山门石阶 / 修炼洞府 / 丹房 / 灵田竹林 / 密林月夜 / 演武场 / 山顶悬崖 / 阵法密室. Each gets a `scenes/{slug}.md` per ai_video.md rule 12.3 (since ≥2 shots reuse). Specific instantiated names per R-2/R-3 (赤霞门正殿, 九寰阁玉环, 澹台宗高台, 流烛盟杂修堂, 忘川教石塔群, 澹江洲苇草洲, 落雁渊白骨底, 栖梧崖白梧桐).

### R-6 — Reveal cadence locked to paid-conversion nodes
Per CCI-5:
- **ep08:** 归砚镜 first activation; first memory shard surfaces (the actual ep01 betrayal seen through unfiltered eyes — confirms it wasn't paranoia).
- **ep10 (paid node 1, 70% load):** Face-slap on 卫长烛 + first "不可承受" 寿命 cost (主角因升 1 阶失去关于「母亲长相」的记忆) + 神秘人 cliffhanger (闻砚清剪影实为分身 / 影子).
- **ep17:** Past-life name 裴长砚 revealed; 前世 vs 本世 timeline reconciled.
- **ep20:** 《偿岁真言》 vs 《残忆经》 mirror revealed (魔门功法 = 主角功法的源头).
- **ep28:** 容漪 = 忘川教-planted memory backup; 信任反转.
- **ep30 (paid node 2, 25%):** Parasitic system's origin partially revealed (主角前世 = 系统的设计者 — but for what purpose?).
- **ep35:** 长烟幡 transfer scene (容漪 → 裴知秋); 共苦盟约.
- **ep49:** 归砚镜 拼回 完整 memory; 主角发现自己设计 system 是为 trap 忘川教 — but the trap costs him everything.
- **ep50 (paid node 3, 5%):** 主角 = 系统 source revealed.
- **ep60 (season finale + season hook):** Parasitic cost actually paid (主角失去与 容漪 最后的共同记忆 → she becomes a stranger in front of him after defeating 言息) + season-2 hook (《偿岁真言》 traveling to a fragment of 容漪 — she carries pieces of the contract now).

### R-7 — Validation strategy hand-offs (stage 5 input)
- **Copyright clearance** validator: blacklist seed = baseline_extraction §2.5 (all distinctive entities) + the 5 mozun_chongsheng major characters (沧冥 / 苏璃月 / 柳红袖 / 苓夭夭 / 方鼎元 etc. by reference to that project's character files). Auto-grep all stage-6 outputs.
- **Genre fidelity:** xianxia checklist from baseline_extraction §2.1–§2.4 (8-stage ladder present; 三方 trifecta present; 修炼 → 突破 → cliffhanger cadence present at episode rhythm; ≥3 foreshadowed reveals visible by ep30).
- **Short-drama feasibility:** ≤5 named characters per ep / ≤6 prop per scene / every shot ≤15s / 9:16. Per-shot prompt body word-count ≤ 2000 (soft) / ≤ 2500 (hard) per ai_video.md rule 12.4 v4.
- **Hook/retention:** ep01 first-3-second hook present; every ep ends on one of the 8 cliffhanger classes; no two consecutive episodes use the same class. Paid-conversion nodes at ep10/30/50/60 carry the reveal cadence per R-6.
- **Internal consistency:** parasitic-cost ledger — every level-up burns exactly 1 tick on 焚寿罗盘; running total must be tracked across episodes in the character bible.

### R-8 — Trend-stance application (sanity check from trend_research §3.5)
All 8 qa.md locks are trend-supported or trend-neutral. **No qa.md decision needs to be reopened.** Differentiation work happens at:
- Parasitic system specific form (lifespan-vs-memory dual cost; configured in our design).
- Revenge target distribution across 3 factions (configured in R-2 character_anonymization).
- AI visual budget allocation to 强项 palette (configured in R-3/R-4).

---

## Open questions surviving research

1. **Title + slug pick** — from R-1's 3 candidates, stage 4 choose; surface to user at stage 4 review gate.
2. **3 empty baseline novel folders** (`cong_jianshu_xiuxing`, `gou_zai_xiuxianjie`, `zhutian_daozu`) — fire a补抓 follow-up to `specs/development/ai_video_management/` to re-run the downloader BEFORE stage 5 copyright_clearance, or accept the slightly under-spec'd blacklist. Recommendation: download补抓 (cheap, doesn't block stage 4).
3. **Cultivation system terminal stage naming** — 8-stage ladder either ends 合体 → 大乘 (fanren / character_anonymization implicit) or 合体 → 渡劫 (wode_moni / shei_rang). baseline_extraction punts to stage 4. Recommendation: use 大乘 to triangulate against wode_moni's 渡劫 (avoids cadence echo at season finale).
4. ~~**First 5-episode detail-batch — should it include the ep10 paid-node deep dive in batch 1?**~~ **Resolved by follow-up 001 (2026-05-24): detail batch = 1 (ep01 only)**. User shifted to fail-fast / iterate-per-episode. ep10 paid-node design stays at outline level in `arc_outline.md` until a subsequent run; ep01 shot prompts still plant the ep10-side seeds (e.g., 卫长烛's face is recognizable in the 0:03–0:30 montage so the ep10 face-slap callback is visually pre-funded). All R-2 / R-3 / R-4 above still apply — they describe ep01-relevant material in full.
5. **Mozun_chongsheng character-pool cross-pollination check** — visual_style mitigated by hex-divergent palette (灰青/月白/寄生紫 vs 黑/金/紫霄/朱砂); character_anonymization mitigated by sernname-disjoint pool (mozun 沧/方/苏/柳/苓 vs ours 裴/闻/容/卫/应/戚/池/阮/言). One concrete check stage 5 should run: every named entity in this dossier is grep-checked against `ai_videos/mozun_chongsheng/` outputs as well as `downloaded_novels/`.
6. **YouTube Shorts double-subtitle pass** — qa.md selected YouTube Shorts as one of 3 platforms. visual_style §3.7 mentions the post-v1 follow-up. Confirm: this stage's deliverables do NOT include English subtitles; that's a separate follow-up after stage 6 ships ep01 in Chinese only.
7. **Web-source unavailability** (CCI-7) — paper.cn / 36kr / huxiu cited several times in trend_research. Stage 5 validation should explicitly flag any quoted-number claim sourced exclusively from these blocked domains as "needs manual second-source verification".
8. **Episode count vs detail commitment trade-off** — qa.md locked 60 episodes with detail batch 5. If the user later wants fewer (say 30) to accelerate first-render, the over-arc was designed for 60 — would need re-pacing of the ep10/30/50/60 paid-node placement. Recommendation: lock 60 and stage 6 ship ep01–05 first; only revisit if production cost exceeds budget.

---

## Pre-reading consulted

Recorded in `.audit/adhoc_agents/2026-05-24/xianxia_new-20260524-101931/events.jsonl` as the stage 3 `stage.started` event with `pre_reading_consulted` array of `{path, sha256}` for:

- `.claude/skills/agent_team/playbooks/research.md`
- `.claude/agent_refs/research/general.md`
- `.claude/agent_refs/research/ai_video.md`
- `.claude/agent_refs/project/general.md`
- `.claude/agent_refs/project/ai_video.md`

## Worker spawn audit

- `researcher-01-baseline_extraction` (status: partial — 3 of 14 baselines empty; confidence: high on the 11-baseline subset)
- `researcher-02-trend_research` (status: complete; confidence: medium — CCI-7)
- `researcher-03-visual_style` (status: complete; confidence: high)
- `researcher-04-character_anonymization` (status: complete; confidence: high — every name web-checked)

Each worker's `prompt.md` + `output.md` lives at `.audit/adhoc_agents/2026-05-24/xianxia_new-20260524-101931/spawns/{worker_id}/`.
