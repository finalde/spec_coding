---
target_stage: 6
target_artifacts:
  - ai_videos/feng_shou_lu/characters/
  - ai_videos/feng_shou_lu/scenes/
  - .claude/agent_refs/project/ai_video.md
severity: high
---

# Follow-up draft 001 — 2026-05-24

Migrate feng_shou_lu's `characters/` and `scenes/` folder structure from the deprecated rule 12.5 v5 hybrid pattern (`c{NN}_{pinyin}/{中文名}.md` + flat `scenes/s{N}_{name}.md`) to the canonical rule 12.8 v2 + 12.9 pattern (`c{N}_{中文名}/c{N}_{中文名}.md` + `scenes/s{N}_{name}/s{N}_{name}.md`). Reason: ai_video_management import / casting / shot-concat features expect the 12.8 v2 shape (proven working in `mozun_chongsheng`); v5 hybrid was authored against a stale layout diagram (line 40 of `agent_refs/project/ai_video.md`) and against an unfounded fear that the webapp regex `^c\d+(_.*)?$` rejected Chinese folder segments.

Abstracted intent (this becomes the rule, not just a one-off fix):

1. **Future ai_video projects MUST follow rule 12.8 v2.** Both folder and filename use `c{N}_{中文名}` / `s{N}_{shortname}`, byte-identical, no zero-padding, Chinese permitted in both segments.
2. **Existing v5-hybrid projects need migration**, not preservation. The v5 hybrid is now marked SUPERSEDED in `agent_refs/project/ai_video.md`.
3. **Project README's `角色清单` table's "folder" column** must show the actual folder slug — when the folder is renamed, the table must be patched.

Scope of this follow-up:

- (a) Update `agent_refs/project/ai_video.md` line 40 layout diagram + add SUPERSEDED notice on rule 12.5 v5 "文件位置约定" subsection + cross-link the supersedes from rule 12.8 v2's originated-from note.
- (b) Rename 11 character folders + inner .md files: `c01_pei_zhi_qiu/裴知秋.md` → `c1_裴知秋/c1_裴知秋.md`, etc. Preserve assigned N (drop zero-pad only; do not renumber per rule 12.8 "once assigned, never renumber").
- (c) Convert `scenes/s1_无寿崖.md` + `scenes/s2_落雁渊.md` from flat .md to `s{N}_name/s{N}_name.md` folder shape.
- (d) Patch path references across README.md, copyright_clearance.md, arc_outline.md, world.md, shot01.md, both scene files, all 11 character bibles. YAML envelope `worker_id` / `work_unit_id` left intact (worker provenance metadata, not paths).

Not in scope:

- No backfill of `raw_prompt.md` / `interview/qa.md` / `findings/` / `final_specs/spec.md` / `validation/`. feng_shou_lu was authored outside the spec-driven workflow; we are only persisting the follow-up + changelog so the citation in `ai_video.md` resolves and future migrations have a reference.
