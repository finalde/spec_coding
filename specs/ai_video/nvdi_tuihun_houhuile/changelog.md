## Follow-up 001 — 2026-05-24

Source: user_input/follow_ups/001-20260524-actor-photo-directive-and-prompts-to-shots-rename.md
Summary: Add 演员参考照片解读契约 (actor photo = face/build anchor only, 装扮 strictly per prompt) as new common-level rule 12.5-A + apply to c1/c3/c4 turntable prompts. Patch raw_prompt.md to reflect user's `prompts/` → `shots/` rename in both ai_videos READMEs.

Auto-updated:
- `.claude/agent_refs/project/ai_video.md` — new sub-rule `#### 12.5-A 演员参考照片解读契约` inserted before rule 12.6. Establishes byte-identical contract paragraph that must appear in every character turntable prompt's `主体:` 行下方.
- `ai_videos/nvdi_tuihun_houhuile/characters/c1_陈凡/c1_陈凡.md` — turntable prompt `主体:` 行下追加契约段 + 装扮锚 line (黑发束白玉冠 / 玉白世家锦袍 / 装废态病弱妆 vs 演员日常素颜).
- `ai_videos/nvdi_tuihun_houhuile/characters/c3_陈国公/c3_陈国公.md` — turntable prompt 契约段 + 装扮锚 (紫金冠 / 长须银白及胸 强制加须 / 一品国公朝服).
- `ai_videos/nvdi_tuihun_houhuile/characters/c4_太监/c4_太监.md` — turntable prompt 契约段 + 装扮锚 (玄色冠 / 强制无须无胡 / 内监紫袍).
- `specs/ai_video/nvdi_tuihun_houhuile/user_input/raw_prompt.md` — layout diagram `prompts/` → `shots/` to match user's README edit; folder-per-asset path corrected to `shots/shotNN/shotNN.md` per rule 12.9.

No conflicts found in: world.md, style_guide.md, arc_outline.md, scenes/s1_陈国公府正厅 (scene reference 不涉及演员照片解读 per 12.5-A 应用范围 ❌ 部分), episodes/ep01/script.md + shotlist.md (无演员照片 / 文件夹路径直接引用).

Deferred:
- c2_女帝 — placeholder bible, no turntable prompt yet; will inherit 12.5-A 契约 when ep02+ 实出场时填档.
- ~~`prompts/` → `shots/` 是否提升为 canonical rule — 留待下个 follow-up~~ **Corrected in follow-up 002**: canonical rule already says `shots/` (migrated by xianxia_new/011 earlier than follow-up 001's grep). 无 drift, 无需 promote.

---

## Follow-up 002 — 2026-05-24

Source: user_input/follow_ups/002-20260524-shotlist-lock-decisions-and-shot14-cliff.md
Summary: User authorized parent-direct best-judgment on shotlist 待确认 items. Locked 6 decisions, generated shot14 cliff, corrected follow-up 001's wrong `prompts/` → `shots/` divergence claim.

Auto-updated:
- `ai_videos/nvdi_tuihun_houhuile/episodes/ep01/shotlist.md` — header re-locked from 13→14 shots / 68→70s total; "待 user 确认" section replaced with "已锁定决定" 6-row table; shot14 row demoted from "cliff 候选" to "cliff" with reveal motif 光位渐变 detail; renderorder note updated.
- `ai_videos/nvdi_tuihun_houhuile/episodes/ep01/shots/shot14/shot14.md` — created. 8s 特写锁机位 + 反向锐光 (顶左 30° → 0° 正面冷光 4200K), 3-5s 桃花眼瞳孔渐变 暗琥珀→冷金, V.O. "戏 ... 该开场了" ep02 入口锚。负向严防 reveal 锐光骤现 / 装废+reveal 同时出现 / 唇角勾起过大。
- `specs/ai_video/nvdi_tuihun_houhuile/user_input/raw_prompt.md` — `shots/` 注释 corrected: 从 "project-scoped naming divergence" → "canonical per xianxia_new/011" (follow-up 001 的判断有误, 实际无 drift).

No conflicts found in: shot01-13 prompts (无需 patch — 决定已 byte-aligned 进各 shot prompt 的 reaction shot 锁机位 / shot02 侧背仰角 / shot01 实拍诏书 等 detail).

Final ep01 状态: 14 shots locked, 70s total, 渲染 ready. 操作人下步: 渲染 3 角色 turntable + s1 scene walk-through, 按 shotlist 顺序拍 shot01-14, 后期剪映拼接出 ep01_final.mp4.

---

## Follow-up 003 — 2026-05-30 02:22:17

Source: user_input/follow_ups/003-20260530-shot02-face-eunuch-respectful-receive-edict.md
Summary: shot02 改为父子统一面朝太监恭敬接旨 (reverse POV, 父子正面入画), 太监不入画 (仍 OS)。取代 follow-up 002 锁定决定 (e) 的"侧背"构图。

Auto-updated:
- `ai_videos/nvdi_tuihun_houhuile/episodes/ep01/shots/shot02/shot02.md` — 全文 patch: 标题改"父子面朝接旨全景 (reverse POV)"; Summary / Characters / reference 備注 / 起始帧 / 结束帧 / 视频 prompt 的 镜头 + 动作 + 光线 全部由"侧背 (从太监身后 30°)"改为"reverse POV 父子正面面朝太监恭敬接旨, 双手前举 + 垂首, 太监不入画"; 负向加"不要 父子侧背入画 / 不要 太监入画"。小说原文段 陈凡 posture 由"不弓背不叩首慵懒"改为"垂首敛眉恭谨接旨 + 眸底藏锋"(与装废伪装自洽)。
- `ai_videos/nvdi_tuihun_houhuile/episodes/ep01/shotlist.md` — shot02 行景别由"全景 锁机位 (背向 / 侧背)"改为"reverse POV, 父子正面, 太监不入画"; 已锁定决定 (e) 标记被 follow-up 003 取代 (侧背 → reverse POV 正面)。

No conflicts found in: script.md (无 shot02 posture / 机位描述), dialogue.md (仅台词), c1_陈凡 bible (装废仍为总体 canon — 本 shot 公开恭谨属伪装表层, 不改 bible), shot01 + shot03-14 (shot01 太监正面朝镜头 / shot02 reverse POV 朝父子 构成 shot/reverse-shot 对偶, 几何自洽)。
