# Follow-up draft 090 — 2026-05-18 — **SUPERSEDED by follow-up 091 before implementation**

**Status: spec-only, never shipped.** Within minutes of this spec being written, the user reported Kling's content validator rejecting uploaded character videos with: *"the current video contains cuts or transitions, and no clear, complete character is detected, please upload a single shot clear character video"*. The 7s casting reel designed below (with 360° fast orbit in 0-2s + camera-direction reversals + push-in/pull-out resets in the tail) violates Kling's single-shot constraint just like v5/v6 did. The 0-2s fast 360° also blurs the character so Kling can't detect a clear subject.

Superseded by follow-up 091 (v8 — static-camera 7s). Kept on file for audit trail; do NOT patch character files from this spec.

---

Step character reference turntable down from 15s (v6) to **7s** (v7). 0-2s self-sufficient contract (一/二 + 正面定场 + 360° 回正, byte-identical across characters) **stays** — `_CONCAT_SEGMENT_S = 2.0` shot-char concat + `✂ 截到 2s` button unchanged. 2-7s collapses the v6 casting reel down to its essential beats: 3 camera moves + 自报姓名 + 2 character-specific signature lines (slot #5 doubles as catch close + 标志特征点 final lock).

## Why

User: "lets change the charactor video prompt from 15s to 7s now".

15s gave room for 6 camera moves + 4 dialogue slots + silent expression range — generous but heavy to render and likely past actual user need for a casting reference. 7s keeps the most signal-dense beats and drops the parts that were "nice to have":

- **Kept (high-signal)**: 0-2s lock (truncate-compat) / 推近 (face read) / 反向 90° (silhouette variation) / 拉近 medium close-up (props + final lock) / 自报姓名 / 2 signature lines.
- **Dropped from v6**: 拉远 3/4 全身侧像 (5-8s, redundant with 0-2s 360° silhouette) / 横向 pan 360° silent expression range (8-11s, can't do justice in compressed budget) / 标志台词 #3 (11-13s) / standalone catch-phrase close row (13-15s — slot #5 now doubles as catch).

Net: 7-segment v6 → **5-segment v7**. 8-row dialogue table → **6-row**. Same locked 0-2s prefix.

## Spec — rule #12.5 v6 → v7

### Locked 0-2s prefix (UNCHANGED from v5/v6)

```
0-1s: 正面**全身远景**起手, {角色姿态 + 眼神跟镜 + 自然呼吸}; 说"一"。
1-2s: 镜头**快速 360° 顺时针环绕一圈**（侧面 90° → 正背 180° → 另一侧 270° → 回正 360°）; 说"二"。**必须在 2.0s 前完成发声 + 回正到正面**。
```

### New 2-7s casting tail (per-character variable)

```
2-3s: 镜头**推**至**面部中近景特写**（眉眼 + 服装领口 + 标志特征点 row #11）; 说"三, 我是 {角色姓名}"。
3-5s: 面部定格 0.5s + **反向慢速 90° 环绕**（正面 → 左侧 45° → 左侧 90°）; 角色说出**标志台词 #1**（character bible 中第 1 句, 演员标准声线 baseline）。
5-7s: 镜头回正 + **拉近至胸像 medium close-up**（含双手手势 + 标志道具 if any, 标志特征点 row #11 占满下半画面）; 角色说出**标志台词 #2**（catch + 情绪 peak + final lock); 定格 0.3s 结束。
```

### 6-row dialogue table (was 8-row in v6)

| # | 台词 | 用途 | 时段 | 情绪基调 |
|---|---|---|---|---|
| 1 | 一 | 起声 / 声线 timbre 锚点 | 0-1s | 平稳 / 中音 (byte-identical 跨角色) |
| 2 | 二 | 中段 / 节奏校准 (**2s 前结束**) | 1-2s | 平稳 / 中音 (byte-identical 跨角色) |
| 3 | 三, 我是 {角色名} | 落声 + 自我识别 | 2-3s | 平稳 / 中音 |
| 4 | {标志台词 #1} | 标准声线 baseline | 3-5s | character-specific (per bible 配音参考) |
| 5 | {标志台词 #2} | 情绪 peak + catch + final lock | 5-7s | character-specific |
| — | (no silent row) | — | — | — |

Slot 5 collapses v6's separate "情绪 peak" (slot 7) + "catch close" (slot 8) into one beat — the second signature line carries both purposes since 5-7s is the final 2 seconds.

### 时长

- v7 = **7s** (was 15s v6 / 4s v5 / 2.9s v4 / 12s pre-v4).
- Comfortably within Seedance / Sora / Veo / Runway / Kling reference upload ceilings.
- Cheaper to render than 15s; faster iteration loop for the user.

### Negatives (adjustments from v6)

- Replace `不要 超过 15s（reference 上传硬上限 v6）` → `不要 超过 7s（reference 上传硬上限 v7）`.
- Drop `不要 跳过任何 6 个 camera-move 段（结构性破坏 casting reel 完整性）` — v7 only has 3 camera moves in the tail, not 6.
- Keep all other v6 negatives: 一/二 must finish by 2s; 0-2s no extra dialogue (byte-identical truncate-compat); over-emote ban; standard camera-stability + lipsync-alignment bans.

### Locked-fields list (10+ character byte-identical)

Same carve-out logic as v6, with field values updated:

- `时长` = 7s (byte-identical)
- `台词 0-2s` = 一, 二 (byte-identical)
- `台词 2-7s` = per-character (from bible `## 标志台词或口头禅` — slots #1 and #2)
- All other locked fields (场景, 镜头 template, 光线 / 色调, 节奏, 渲染样式, 比例, video-specific negatives) byte-identical.

## Out of scope

- ai_video_management webapp code — **no code change**. 2s trim + concat path already does what v7 needs (slices 0-2s).
- `character_video__writer.py` — unchanged.
- Scene reference rule #12.10 v3 (15s walk-through) — orthogonal, unchanged.
- Shot prompts (rule #12.6) — only reference `{ref_cN_xxx}` placeholders, no embedded duration text.
- Existing rendered mp4s (currently a mix of 4s / 15s / older). User re-renders at their discretion.

## Touch list

- `.claude/agent_refs/project/ai_video.md` rule #12.5 v6 → v7 — bump duration 15s → 7s, swap 7-segment beats → 5-segment, swap 8-row table → 6-row, update negatives (drop the 6-camera-move ban, swap 15s → 7s ceiling), update locked-fields list, append footer attribution `rev — follow-up 090 …`.
- `specs/development/ai_video_management/user_input/revised_prompt.md` — header bump 090.
- `specs/development/ai_video_management/changelog.md` — append 090 entry.
- `specs/ai_video/mozun_chongsheng/user_input/follow_ups/023-{ts}-character-ref-7s-tighter-casting.md` — sibling follow-up.
- `specs/ai_video/mozun_chongsheng/user_input/revised_prompt.md` — header bump.
- `specs/ai_video/mozun_chongsheng/changelog.md` — entry.
- `ai_videos/mozun_chongsheng/characters/c{1..10}_*/c{N}_*.md` — patch via one-shot script: v6 7-segment dynamics → v7 5-segment; 8-row table → 6-row; 时长 15s → 7s; v7 negatives.
