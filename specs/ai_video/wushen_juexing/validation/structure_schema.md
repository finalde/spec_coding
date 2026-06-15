---
worker_id: level-specialist-03-structure-schema
stage: 5
role: level-specialist
level: structure_schema
status: complete
blockers: []
confidence: high
---

# Validation level — STRUCTURE & PROMPT-SCHEMA compliance (wushen_juexing)

Stage-5 strategy. Defines greppable, stage-6-checkable rules for layout, shot-file schema,
duration math, aspect ratio, zero-hex, and content-language compliance. Target tree root:
`ai_videos/wushen_juexing/` (sub_type=**novel**). **follow-up 022: per-episode checks now apply to
both `episodes/ep01/` AND `episodes/ep02/`** (EP1 = 15 镜/90s; EP2 = EP1 溢出段 7 镜/46s「溢出段·待补」，
S-DUR 豁免). Re-run every S-LAYOUT-3 / S-SHOT-* / S-DUR-* check per episode folder.

## CRITICAL precedence note (read before running any check)

`agent_refs/validation/ai_video.md` **move #4** ("Dual-prompt presence + seam-frame still-image
prompts") still names the **OLD separate-files schema**: `shotNN_kling.md` / `shotNN_seedance.md`
/ `shotNN_lastframe_seedream.md` / `shot01_startframe_seedream.md`, plus the seam-frame
still-image pipeline. **That schema is ABOLISHED.**

`agent_refs/project/ai_video.md` **rule 5 v3** + **rule 11** supersede it:
- Rule 11 (seam-frame pipeline) = **ARCHIVED / not load-bearing**; stage-6 validators no longer
  grep for seam-frame blocks.
- Rule 5 v3 = **one self-contained `episodes/epNN/shots/shotNN.md` per shot**, containing
  **THREE `text` code blocks** (`## 起始帧` / `## 结束帧` / `## 视频 prompt`) plus a top prose
  section + Shot context.

Per **CLAUDE.md precedence** (`project ref > stage ref`; per-project spec > both), all checks below
validate against the **CURRENT project schema**: single `shotNN.md` with 3 code blocks.
**Do NOT require** the abolished `shotNN_kling.md` / `shotNN_seedance.md` / `*_lastframe_seedream.md`
/ `shot01_startframe_seedream.md` files. **A shot folder containing those separate files is itself a
schema violation** (S-SCHEMA-OLDFILES below). This note resolves the move #4 vs rule 5-v3 conflict
in favor of rule 5 v3.

Spec source-of-truth for this level: `final_specs/spec.md` FR-1, FR-4, FR-6, FR-9, FR-10, FR-11,
FR-12, NFR-1, NFR-2, NFR-4, NFR-6 + acceptance summary.

---

## Severity legend

`blocker` halts the work unit (per `validation/ai_video.md` severity table); `warning` is logged and
the work unit may still close with ≤2 warnings (per move #9 closing contract).

All greps are run from repo root. `\b` / `-E` are ripgrep/POSIX-ERE. Paths use forward slashes.

---

## Rule group A — Layout (rule 2 novel)

### S-LAYOUT-1 — Project-root skeleton present (blocker)
`ai_videos/wushen_juexing/` MUST contain, non-empty: `README.md`, `world.md`, `style_guide.md`,
`arc_outline.md`, `copyright_clearance.md`, and a `characters/` dir + an `episodes/ep01/` dir.
(FR-1, FR-2, FR-3, FR-6, FR-12; rule 2 v3 production-side layout.)

Check:
```bash
for f in README.md world.md style_guide.md arc_outline.md copyright_clearance.md; do
  test -s "ai_videos/wushen_juexing/$f" || echo "MISSING/EMPTY: $f"
done
test -d ai_videos/wushen_juexing/characters || echo "MISSING dir: characters/"
test -d ai_videos/wushen_juexing/episodes/ep01 || echo "MISSING dir: episodes/ep01/"
```
Any line of output = blocker.

### S-LAYOUT-2 — Character bibles: folder-per-char, byte-identical Chinese name, N not zero-padded (blocker)
Exactly the 4 spec characters, each as `characters/cN_中文名/cN_中文名.md` where the folder name and
file stem are **byte-identical** and `N` is `1..4` **not zero-padded** (rule 2 + rule 12.9).
Expected: `c1_裴知秋`, `c2_裴昭`, `c3_裴霆`, `c4_凌虚子`.

Check:
```bash
# every char dir must hold a same-named .md
for d in ai_videos/wushen_juexing/characters/*/; do
  base=$(basename "$d"); test -s "$d/$base.md" || echo "BAD char file: $d (expected $base.md)";
done
# folder names must be cN_ with N in 1..4, not c0N_
ls ai_videos/wushen_juexing/characters | grep -nE '^c0[0-9]_' && echo "ZERO-PADDED N (forbidden)"
```
Missing/mismatched same-named file, zero-padded `c0N_`, or count ≠ 4 = blocker.

### S-LAYOUT-3 — EP1 episode files present (blocker)
`episodes/ep01/` MUST contain non-empty `script.md`, `dialogue.md`, `shotlist.md`, `publish.md`, and a
`shots/` dir (FR-7..FR-11; rule 2 novel).

Check:
```bash
for f in script.md dialogue.md shotlist.md publish.md; do
  test -s "ai_videos/wushen_juexing/episodes/ep01/$f" || echo "MISSING/EMPTY ep01: $f"
done
test -d ai_videos/wushen_juexing/episodes/ep01/shots || echo "MISSING dir: ep01/shots/"
```
Any output = blocker.

### S-LAYOUT-4 — folder-per-shot `shots/shotNN/shotNN.md` (blocker · follow-up 021)
**⚠ Corrected follow-up 021 (2026-06-14): the prompt source is NOT a flat `shotNN.md`.** Per
`agent_refs/project/ai_video.md` rule #12.9 + validation move #10, every shot is a same-named folder
`episodes/ep01/shots/shotNN/` (zero-padded NN) containing `shotNN.md` (+ optional `subtitles.md` +
`renders/` media). A flat `shots/shotNN.md` directly under `shots/` is non-conformant — it breaks the
webapp display / render-import (`renders/`) / 台词 burn-in contracts and is inconsistent with the other
dramas (`nvdi_tuihun_houhuile`). The earlier "flat is the prompt source" wording was the drift this
follow-up fixes.

Check:
```bash
# 1. no flat shot md directly under shots/ (must be empty):
find ai_videos/wushen_juexing/episodes/ep01/shots -maxdepth 1 -name 'shot*.md'
# 2. each shotNN/ folder has a byte-identical-named shotNN.md inside (= shot count):
find ai_videos/wushen_juexing/episodes/ep01/shots -regextype posix-extended \
  -regex '.*/shot[0-9]{2}/shot[0-9]{2}\.md' | wc -l
```
Any flat `shots/shotNN.md`, or a `shotNN/` folder whose inner md name ≠ folder name = blocker.

### S-SCHEMA-OLDFILES — abolished separate prompt files forbidden (blocker)
The seam-frame / dual-file schema is abolished. Any file matching the old names = blocker.

Check:
```bash
ls ai_videos/wushen_juexing/episodes/ep01/shots/ \
  | grep -nE '_(kling|seedance|lastframe_seedream)\.md$|^shot01_startframe_seedream\.md$' \
  && echo "ABOLISHED separate prompt file present (rule 5 v3 / rule 11)"
```
Any hit = blocker.

### S-SCENE-TEMPLATE — 每个场景档用同一 canonical 模板（blocker · follow-up 024）
Every `scenes/s{N}_{名}/s{N}_{名}.md` MUST follow the v3 canonical template (per `agent_refs/project/ai_video.md`
rule 12.3 v3, reference实体 `s1_裴王府正厅`): the sections `## 锁定描述符` + `## 关键变化态` + `## 出现镜头`
+ `# 步骤一 · 背景图 seed prompt` + `# 步骤二 · 场景 walk-through video prompt` + `# 背景图系统 index`,
AND folder-per-plate (`scenes/s{N}_…/{plate}/{plate}.md`, folder name = inner md name). No scene may ship
with only 步骤一 (the drift this rule fixes: s2–s5 originally lacked 步骤二 + index).

Check (per scene dir):
```bash
for d in ai_videos/wushen_juexing/scenes/s*/; do b=$(basename "$d"); S="$d$b.md"
  for h in '^## 锁定描述符' '^## 关键变化态' '^## 出现镜头' '^# 步骤一' '^# 步骤二' '^# 背景图系统 index'; do
    grep -qE "$h" "$S" || echo "$S: 缺节 $h (S-SCENE-TEMPLATE)"
  done
  for p in "$d"*/; do pb=$(basename "$p"); [ -d "$p" ] && [ "$pb" != "frames" ] && { test -f "$p$pb.md" || echo "$p: plate 文件夹名≠内层 md 名"; }; done
done
```
Any missing section, or plate folder whose inner md ≠ folder name = blocker.

---

## Rule group B — Zero hex (rule 1b / NFR-2)

### S-HEX — zero hexadecimal color codes anywhere under the project (blocker)
No 6-hex-digit color code may appear in any output file, backticked or not (rule 1b). Color is natural
Chinese only. (Color **temperatures** like `5500K` and ratio `9:16` are NOT hex — the pattern below
does not match them.)

Check (MUST be 0 matches):
```bash
grep -rnE '#[0-9a-fA-F]{6}' ai_videos/wushen_juexing/ ; echo "exit:$?"
```
Any match = blocker. Acceptance criterion in spec: "grep `#[0-9a-fA-F]{6}` 命中 = 0".
(Also reject residual hex-bound field labels per rule 1b: `瞳色（hex）`, `主色（hex）`,
`配色 hex`, `色调对齐主/辅/点缀 hex` — grep `hex` over the tree; any field label naming hex = blocker.)
```bash
grep -rnE '（hex）|配色 hex|色调对齐.*hex' ai_videos/wushen_juexing/ && echo "hex-bound field label (rule 1b)"
```

---

## Rule group C — Shot file schema (rule 5 v3 + 2026-05-27/30/31 amendments)

Run per `shotNN.md`. Let `S` = the shot file.

### S-SHOT-PROSE — top prose section present, outside fences, with bolded character names (blocker)
Each `shotNN.md` opens (before the `# ep01 / shotNN` H1, separated by `---`) with a 200–400 字 Chinese
prose section headed `## 小说原文` (this drama is script-first / novel-less per FR-10, so heading is
`## 小说原文`, not `## Chapter excerpt`). On-stage character names appear in markdown **bold**
(rule 5 v3 + follow-up nvdi 005). Prose lives OUTSIDE all `text` fences.

Check:
```bash
grep -nE '^## 小说原文' "$S" || echo "MISSING ## 小说原文 prose section"
grep -nE '\*\*[^*]+\*\*' "$S" | head -1 || echo "WARN: no bolded 出场角色名 in prose"
```
Missing prose heading = blocker; missing any bold = warning (cross-check against Shot context
`Characters:` for completeness in the consistency level).

### S-SHOT-CONTEXT — Shot context block present (blocker)
A `## Shot context` section carrying Summary / Characters / Scene / Duration / Reference.

Check:
```bash
grep -nE '^## Shot context' "$S" || echo "MISSING ## Shot context"
```
Missing = blocker.

### S-SHOT-3BLOCKS — exactly the three code blocks present (blocker)
`shotNN.md` MUST carry, in source order, the three headings + a fenced `text` block under each
(rule 5 v3 / 2026-05-27 three-block amendment):
1. `## 起始帧` (t=0 静帧)
2. `## 结束帧` (末帧静态落点)
3. `## 视频 prompt`

Check:
```bash
grep -nE '^## 起始帧'      "$S" || echo "MISSING ## 起始帧"
grep -nE '^## 结束帧'      "$S" || echo "MISSING ## 结束帧"
grep -nE '^## 视频 prompt' "$S" || echo "MISSING ## 视频 prompt"
# fence count: 3 opening ```text expected
grep -cE '^```text' "$S"   # must be == 3
```
Missing any heading, or `text` fence count ≠ 3 = blocker.

### S-SHOT-TAG — compact Chinese tag as first line of every fenced block (blocker)
The first line **inside** each `text` block is the compact Chinese tag (rule 2026-05-30), distinct per
block type for EP1 (集=01):
- 视频 block first line = `01集NN镜视`
- 起始帧 block first line = `01集NN镜始`
- 结束帧 block first line = `01集NN镜末`
where `NN` = the shot's zero-padded number (NOT necessarily the file's — match the file).

Check (per shot, derive NN from filename):
```bash
NN=$(basename "$S" .md | grep -oE '[0-9]{2}')
grep -nE "^01集${NN}镜视" "$S" || echo "MISSING/WRONG 视频 tag 01集${NN}镜视"
grep -nE "^01集${NN}镜始" "$S" || echo "MISSING/WRONG 起始帧 tag 01集${NN}镜始"
grep -nE "^01集${NN}镜末" "$S" || echo "MISSING/WRONG 结束帧 tag 01集${NN}镜末"
```
Any missing/wrong tag = blocker (Kling 9-char filename-truncation routing depends on it).

### S-SHOT-VIDEOFIELDS — required video fields present, basic-skeleton OK (blocker on absence)
The `## 视频 prompt` body MUST carry these field labels (order fixed; basic-skeleton allowed per
2026-05-31 — field-in-place with concise content, NOT field-removed):
`人物` / `场景` / `镜头` / `动作` / (`台词 / 字幕`) / (`光线 / 色调`) / `色调` may be folded into
`光线 / 色调` / `节奏` / `渲染样式` / `比例` / `时长`.

Minimum required (a missing label = blocker): `人物:`, `场景:`, `镜头:`, `动作:`, `台词` or `字幕`,
`光线` (i.e. `光线 / 色调:`), `节奏:`, `渲染样式:`, `比例:`, `时长:`.

Check (scoped to the 视频 fence — practical grep over whole file is acceptable since these labels only
occur in the 视频 block):
```bash
for lbl in '人物:' '场景:' '镜头:' '动作:' '光线' '节奏:' '渲染样式:' '比例:' '时长:'; do
  grep -qE "$lbl" "$S" || echo "$S: MISSING video field $lbl"
done
grep -qE '台词|字幕' "$S" || echo "$S: MISSING 台词 / 字幕 field"
```
Missing any = blocker. **Per 2026-05-31**: do NOT raise warning/blocker merely because a descriptive
dimension (`镜头` motion detail, multi-beat `动作`, `光线/色调` layering, `节奏`, `渲染样式` keyword
set) is a one-line stub. **Substantive-at-generation** fields (`场景` / `镜头` 一行 / `动作` ≥1 拍
`0–{时长}s …` / `台词 / 字幕` 三选一+台词原文 / `比例` / `时长`) MUST be non-empty — empty value on
any of these = blocker.

### S-SHOT-SCENE-REF — `参考:` 行必含场景条目（blocker · follow-up 023）
Every shot's `参考:` line MUST list a scene reference (a `bg…` plate token for plated scenes, or a
`s{N}_…_bg` token for single-angle / 回忆 / 室外 scenes) in addition to its characters — per
`agent_refs/project/ai_video.md` 参考行格式 + follow-up 023. No shot may omit the scene (the 回忆 /
末镜 shots that listed only characters were the drift this rule fixes; each now resolves to a
`scenes/s{N}_…/` asset).

Check (per shot):
```bash
grep -m1 '^参考:' "$S" | grep -qE 'bg[0-9_]|s[0-9]_|_bg' || echo "$S: 参考 行缺场景条目 (S-SHOT-SCENE-REF)"
```
Any shot whose `参考:` has no scene token = blocker. Also: every scene token referenced MUST have a
matching `scenes/s{N}_{名}/s{N}_{名}.md` asset (dangling scene ref = blocker).

### S-SHOT-CLOSEUP-BLUR — 近景/特写镜 `镜头:` 标背景虚化（warning · follow-up 023）
When a shot's `镜头:` 景别 is 特写 / 大特写 / 中近景 (人物近景), the `镜头:` line SHOULD carry an explicit
background-blur note (`背景浅景深虚化柔焦、主体清晰` or equivalent) per follow-up 023. 中景 / 全景
environment-establishing shots are exempt (background must stay legible).

Check (per shot):
```bash
cam=$(grep -m1 '^镜头:' "$S")
echo "$cam" | grep -qE '特写|近景' && { echo "$cam" | grep -q '背景浅景深虚化\|背景虚化' || echo "$S: 近景/特写镜未标背景虚化 (S-SHOT-CLOSEUP-BLUR)"; }
```
Close-up shot missing the blur note = warning.

### S-SHOT-MULTIBEAT — multi-beat 动作 sum = 时长 (conditional warning)
The multi-beat `动作:` timed beats must sum to `时长`. **Applies only when `动作` is already expanded
to ≥2 beats** (2026-05-31: a single `0–{时长}s …` skeleton beat is legal and exempt).

Check: if `动作` contains ≥2 `N–Ms` ranges, the last range's upper bound MUST equal `时长` seconds.
Mismatch = warning (story/duration level owns the hard duration math; this level flags the skeleton
inconsistency only).

### S-SHOT-FORBIDDEN — abolished fields inside any code block (blocker)
Reject if any of these appear **inside a shot code block** (the regen would have stripped them; their
presence means a stale/old-schema shot):
- `负向:` (abolished 2026-05-25)
- `场景视角锚:` (abolished 2026-05-27)
- a body-level `角色:` line — i.e. `角色:` as a field row inside the fence (abolished 2026-05-27).
  NOTE: `人物:` is the CURRENT first-class field (2026-05-30) and is **allowed**; only the old
  `角色:` label is forbidden. The reference-handle header `<char>请参考:` is also allowed.
- a repeated free-text shot-title line of the form `ep01 / shotNN ·` **inside** a code block
  (abolished 2026-05-31). The file-level `# ep01 / shotNN · …` H1 (with `# ` prefix, OUTSIDE fences)
  is retained — do not flag it.

Check:
```bash
grep -nE '^负向:'        "$S" && echo "$S: FORBIDDEN 负向"
grep -nE '^场景视角锚:'  "$S" && echo "$S: FORBIDDEN 场景视角锚"
grep -nE '^角色:'        "$S" && echo "$S: FORBIDDEN body 角色: (use 人物:)"
grep -nE '^ep01 / shot[0-9]{2} ·' "$S" && echo "$S: FORBIDDEN repeated in-block shot title"
```
Any hit = blocker. (The last grep keys on a line that does NOT start with `# `, so it won't match the
legit H1; verify the hit is inside a fence before flagging.)

### S-SHOT-OS-LIPSYNC — off-screen / OS / V.O. 台词 carries speaker label + 在画人物口型 (warning)
Per 2026-05-30: any `台词` line spoken off-screen (画外音 / OS / V.O. / 内心独白) MUST carry an
explicit `【画外音 / OS · 说话人=<角色>(不在画面内)】` label AND a `· 在画人物口型:` sub-bullet
stating on-screen characters 全程闭口. SHOULD-level → `warning` (move #9 / 2026-05-30 says
validators SHOULD flag).

Check (heuristic):
```bash
grep -nE 'OS|画外|V\.O\.|内心独白' "$S" | grep -E '台词' \
  && { grep -qE '在画人物口型|无嘴动|全程闭口' "$S" || echo "$S: OS 台词 missing 在画人物口型 directive"; }
```
OS/画外/V.O. 台词 present but no 口型 directive = warning.

---

## Rule group D — Duration (rule 6 / move #2 / NFR-4)

### S-DUR-EACH — every shot 时长 ≤ 15s (blocker)
Each `shotNN.md` 视频 block declares `时长:` ≤ 15 (seconds), present and parseable (move #2).

Check:
```bash
for S in ai_videos/wushen_juexing/episodes/ep01/shots/shot[0-9][0-9].md; do
  v=$(grep -oE '时长[:：]\s*[0-9]+' "$S" | grep -oE '[0-9]+' | head -1)
  [ -z "$v" ] && echo "$S: MISSING 时长" && continue
  [ "$v" -gt 15 ] && echo "$S: 时长 ${v}s > 15s"
done
```
Missing `时长` or `时长` > 15 = blocker.

### S-DUR-COUNT — shot count ∈ [14,18] (blocker, 溢出段集豁免)
每集 14–18 shots (FR-9 / NFR-4 / follow-up 022 ~90s). 溢出段集（如 EP2 当前 46s）暂可 <14、标注「溢出段·待补」豁免。

Check:
```bash
n=$(ls ai_videos/wushen_juexing/episodes/ep01/shots/ | grep -cE '^shot[0-9]{2}\.md$')
echo "shot count = $n"   # must be 28..32
```
`n < 28` or `n > 32` = blocker.

### S-DUR-TOTAL — shotlist.md `时长合计` line present and ∈ [85,100] (blocker, 溢出段集豁免)
`episodes/ep01/shotlist.md` MUST carry an explicit `时长合计` line whose value (seconds) ∈ [85,100]
(rule 6 per-episode total; spec acceptance). This line is the binding sum proof.

Check:
```bash
grep -nE '时长合计' ai_videos/wushen_juexing/episodes/ep01/shotlist.md \
  || echo "MISSING 时长合计 line"
total=$(grep -oE '时长合计[^0-9]*[0-9]+' ai_videos/wushen_juexing/episodes/ep01/shotlist.md \
        | grep -oE '[0-9]+' | head -1)
echo "时长合计 = ${total}s"   # must be 180..195
```
Missing line, or value `< 180` / `> 195` = blocker. (Independently, the sum of per-shot `时长` SHOULD
equal `时长合计`; cross-check is a warning here — the story/duration level owns the exact reconcile.)

---

## Rule group E — Aspect ratio (rule 7 / move #5 / NFR-6)

### S-RATIO — [已废止 follow-up 010] prompt 不写比例
follow-up 010 / spec NFR-6（divergence）：**所有 prompt 不写 `比例`**，用户在平台自行 set 画幅。
本规则废止——**不再校验 `比例` 字段**；反之，prompt 代码块内**出现** `比例: 9:16` 行视为应清理（warning）。

Check（反向，确保已清理）：
```bash
grep -rn '^比例: 9:16$' ai_videos/wushen_juexing/episodes/ep01/shots/ && echo "应删除 比例 行 (follow-up 010)" || echo "OK: 无比例行"
```

---

## Rule group F — Language compliance (move #1 / NFR-1)

### S-LANG — content ≥95% Chinese (blocker)
Every `*.md` under `ai_videos/wushen_juexing/`, after stripping ` ```…``` ` code fences, YAML
frontmatter, and raw URLs, MUST be ≥95% Chinese-block characters (Han + fullwidth punctuation).
Allowed and NOT counted against the threshold: English/pinyin proper nouns inside Chinese sentences
(`Kling`, `Seedance`, `Seedream`, `9:16`, field-label tokens, character pinyin if any), markdown
syntax. (move #1.)

Check (heuristic ratio over prose lines, excluding fences/frontmatter):
```bash
# per file: count Han chars vs ASCII-letter runs in the non-fence body
python tools/check_zh_ratio.py ai_videos/wushen_juexing  # if helper exists; else manual sample
```
A file whose stripped prose is < 95% Chinese = blocker. Note: shot **code blocks** are field-labeled
prompts (`镜头:` etc.) with Chinese values — labels like `比例`/`时长` are Chinese; the
fence-stripping rule means the in-fence content is exempt from the ratio, but the prose sections
(`## 小说原文`, Shot context narrative, README/world/style/arc/copyright bodies) carry the burden.

---

## Run order & synthesis

1. A (layout) first — if S-LAYOUT-1/2/3 blocker, the rest can't run; halt this level with the layout
   blocker.
2. B (hex) — single grep over the whole tree.
3. C/D/E per shot file (loop `shot[0-9][0-9].md`).
4. F (language) over all `*.md`.

Emit one `validation.issue.raised` per failing (rule, file) with `level: structure_schema`, the
severity above, and the concrete grep that found it. Close the level when **0 blockers** remain
(warnings ≤2 acceptable per move #9 closing contract; structure warnings here are
S-SHOT-PROSE-bold, S-SHOT-MULTIBEAT, S-SHOT-OS-LIPSYNC, and the 时长合计-vs-sum reconcile).

## Stage-6 applicability note
This level is **strategy only** at stage 5 — the `ai_videos/wushen_juexing/` tree does not yet exist
(stage 6 unrun). All greps above are the executable contract the stage-6 validator runs against each
`shotNN.md` as it is written and at the EP1 closing pass.
