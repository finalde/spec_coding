## Follow-up 001 — 2026-05-24

Source: user_input/follow_ups/001-20260524-align-folder-structure-to-rule-12.8-v2.md
Summary: Migrate feng_shou_lu's `characters/` + `scenes/` folder shape from rule 12.5 v5 hybrid to rule 12.8 v2 + 12.9 canonical pattern; mark v5 hybrid SUPERSEDED in `agent_refs/project/ai_video.md`.

Auto-updated:
- `.claude/agent_refs/project/ai_video.md` — line 40 layout diagram now shows `c{N}_{中文名}/c{N}_{中文名}.md` + `s{N}_{中文名}/s{N}_{中文名}.md`; rule 12.5 v5 "文件位置约定" subsection prefixed with SUPERSEDED notice; rule 12.8 v2's originated-from note cites this supersedes.
- `ai_videos/feng_shou_lu/characters/c01_pei_zhi_qiu/` … `c11_yan_xi/` — renamed to `c1_裴知秋/` … `c11_言息/`; inner `{中文名}.md` renamed to `c{N}_{中文名}.md`.
- `ai_videos/feng_shou_lu/scenes/s1_无寿崖.md` → `scenes/s1_无寿崖/s1_无寿崖.md` (flat .md → folder).
- `ai_videos/feng_shou_lu/scenes/s2_落雁渊.md` → `scenes/s2_落雁渊/s2_落雁渊.md`.
- `ai_videos/feng_shou_lu/README.md` — 渲染产物布局 diagram + 角色清单 table folder column updated to new slugs; legacy `c{NN}_{pinyin}` placeholder removed.
- `ai_videos/feng_shou_lu/copyright_clearance.md` — 7 path citations (`characters/{中文名}.md`, `scenes/s2_落雁渊.md`) rewritten to 12.8 v2.
- `ai_videos/feng_shou_lu/arc_outline.md` — 2 path citations rewritten.
- `ai_videos/feng_shou_lu/world.md` — 1 path citation rewritten.
- `ai_videos/feng_shou_lu/episodes/ep01/prompts/shot01.md` — Reference uploads checklist character + scene path rewritten.
- `ai_videos/feng_shou_lu/characters/c1_裴知秋/c1_裴知秋.md` (and c2..c11) — `参考: characters/{name}.md` self-reference + cross-character refs rewritten.
- `ai_videos/feng_shou_lu/scenes/s1_无寿崖/s1_无寿崖.md` + `s2_落雁渊/s2_落雁渊.md` — `参考: scenes/s{N}_*.md` + sibling `.mp4` references rewritten.

No conflicts found in: episodes/ep01/script.md, episodes/ep01/shotlist.md, episodes/ep01/publish.md, style_guide.md, episodes/ep01/prompts/shot02-07.md (no path-shape references; references go through scene/character short-slugs which are unchanged).

YAML envelope `worker_id` / `work_unit_id` fields preserved (worker provenance, not paths — rewriting would falsify the audit trail).
## Follow-up 002 — 2026-05-24
Source: user_input/follow_ups/002-20260524-align-shot-folder-to-rule-12.9.md
Summary: Migrate ep01 shots from flat `shots/shot{NN}.md` to rule 12.9 per-shot folder pattern `shots/shot{NN}/shot{NN}.md`. Aligns to canonical webapp pattern + provides per-shot folder for rendered Kling/Seedance mp4 + 缩略图 + 等 media (gitignored).

Auto-updated:
- ai_videos/feng_shou_lu/episodes/ep01/shots/shot{01..07}.md → ai_videos/feng_shou_lu/episodes/ep01/shots/shot{NN}/shot{NN}.md (7 files, mkdir + mv preserve content byte-identical).
- ai_videos/feng_shou_lu/README.md — path references patched (`shots/shotNN.md` → `shots/shotNN/shotNN.md`).

No conflicts found in: shot content (YAML envelope + Chapter excerpt + Shot context + 视频 prompt all preserved); cross-shot references (none — shots reference characters + scenes by folder path which are already 12.8 v2 / 12.9 compliant).
