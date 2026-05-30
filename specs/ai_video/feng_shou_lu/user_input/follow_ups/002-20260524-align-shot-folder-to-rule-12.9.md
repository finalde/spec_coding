---
target_stage: 6
target_artifacts:
  - ai_videos/feng_shou_lu/episodes/ep01/shots/
  - ai_videos/feng_shou_lu/README.md
severity: medium
---

# Follow-up draft 002 — 2026-05-24

Migrate `ai_videos/feng_shou_lu/episodes/ep01/shots/` from flat `shot{NN}.md` files to the rule 12.9 per-shot folder pattern `shot{NN}/shot{NN}.md`. Same rationale that drove follow-up 001 (characters + scenes folder migration to rule 12.8 v2): align to the canonical webapp pattern (proven in mozun_chongsheng), give each shot a folder to hold its rendered Kling/Seedance mp4 + 缩略图 + 等 media (gitignored per NFR-18), and remove a structural inconsistency where characters + scenes already use per-asset folders but shots don't.

Abstracted intent (rule 12.9 codifies this — this follow-up just executes it for the project):

1. **Future ai_video projects MUST follow rule 12.9 shot-folder pattern.** `episodes/ep{NN}/shots/shot{NN}/shot{NN}.md` — folder + filename byte-identical, no zero-padding policy change (shot{NN} retains 2-digit zero-pad per existing convention since shot count typically ≤ 99 per episode).
2. **Existing flat-shot projects need migration.** feng_shou_lu's ep01 has 7 flat shot files; converting them to per-shot folders is mechanical (mkdir + mv + path patches).

Scope of this follow-up:

- (a) Convert 7 shot files: `shots/shot{NN}.md` → `shots/shot{NN}/shot{NN}.md` (mkdir + mv preserve content byte-identical).
- (b) Patch README.md path references — `episodes/ep01/shots/shot{NN}.md` lines update to `episodes/ep01/shots/shot{NN}/shot{NN}.md`.
- (c) No content change inside shot .md files (YAML envelope / Chapter excerpt / Shot context / 视频 prompt sections all preserved).
- (d) `.gitignore` (per rule 12.9 NFR-18) media patterns already cover `ai_videos/**/*.mp4` etc. — no separate per-shot folder addition needed.

Not in scope:

- Backfill raw_prompt.md / interview / findings / final_specs / validation (same posture as follow-up 001: feng_shou_lu was authored outside the spec-driven workflow).
- Migration of nvdi_tuihun_houhuile or any other project — only feng_shou_lu's ep01 shots are touched.
- Re-renumbering shots (shot01 → c1 style). Shots retain 2-digit zero-pad (shot01/shot02/.../shot07).
