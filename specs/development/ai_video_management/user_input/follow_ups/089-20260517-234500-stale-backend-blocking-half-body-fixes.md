# Follow-up draft 089 — 2026-05-17

Half-body still happens because the running backend is stale: 085 + 087 fixes are on disk but the uvicorn process loaded the old module before those edits and still serves it from memory. Restart the backend before drawing any further conclusions about Kling.

## Evidence

- `projects/ai_video_management/libs/infrastructure/writers/actor__writer.py` on disk has the post-085 constants: `IMAGE_WIDTH=720, IMAGE_HEIGHT=1280, IMAGE_WIDTH_BODY=720, IMAGE_HEIGHT_BODY=1280` and an aspect-preserving `_resize_jpeg` (longest edge → target_px).
- `projects/ai_video_management/libs/infrastructure/writers/actor__chinese_prompt.py` on disk has the post-087 structure:
  - Negatives live in the dedicated `_NEGATIVE_PROMPT_ZH` (sent via Kling's `negative_prompt` API field), not stuffed inside the positive prompt.
  - The first line of every prompt is the single positive composition tag `_POSITIVE_COMPOSITION_TAG = "镜头：full body shot · head to toe · 9:16 vertical · long shot · 全身照"`.
  - The descriptor row says `正面全身模特造型照 / fashion comp card full-body shot` (085's 定妆照 → 模特造型照 swap).
  - `_PHOTOGRAPHY_ZH` is the 24-50mm + 「全身」 pool (no 85mm/105mm portrait lenses, no Portra 400, no SX-70).
- Yet `ai_videos/_actors/actor_0141/actor_0141.md` (created today at 22:12) shows the OLD prompt format:
  - First line `镜头【强制 MANDATORY · 全身从头到脚】：full-body wide shot · long shot · 9:16 竖屏 · 头顶到脚趾完整入画 · MUST show entire body from top of head to toes · 严禁 portrait / half-body / close-up / head-shoulder crop ...` — does not exist in current source (grep across `projects/ai_video_management/libs/` returns 0 matches).
  - Photography line: `佳能 EOS R5 85mm f/1.4 人像镜头, 真实皮肤微纹理` — `85mm f/1.4 人像镜头` does not exist in current `_PHOTOGRAPHY_ZH`.
  - 「定妆照」appears in the prompt — does not exist in current builder.
  - 「严禁 portrait / half-body」 baked into the positive prompt body — does not exist in current builder (moved to `_NEGATIVE_PROMPT_ZH` per 087).
- The sidecar is written at generation time and reflects the exact prompt string sent to Kling, so this proves the request actually shipped from old in-memory code.

## Why the disk → memory gap

Python `import` caches modules. Once `libs.infrastructure.writers.actor__chinese_prompt` and `libs.infrastructure.writers.actor__writer` are imported into the FastAPI worker, subsequent edits to those `.py` files don't take effect until the process restarts or the module is force-reloaded. Uvicorn `--reload` is dev-only; if the backend is being run with the production-style command (no `--reload`), in-place edits never propagate.

The previous half-body follow-ups (080 → 081 → 082 → 083 → 085 → 087) each ran the same `Edit` operation against the source files, and the user kept testing without restart. Every "still half-body" report from after 085 is therefore not evidence that 085's structural fixes are insufficient — it's evidence that the fixes were never loaded.

## Action

1. Restart the backend so the new modules load. From `projects/ai_video_management/`:
   ```powershell
   # whatever launcher you use — kill the existing uvicorn / docker container,
   # restart it. If using `uv run uvicorn apps.api.asgi:app --reload`, the
   # --reload flag would have caught the edits, so its absence is the bug.
   ```
   If the launch command is committed somewhere, prefer adding `--reload` for dev — that way future prompt-pool edits propagate without manual restart. (Production should NOT use `--reload`; if this backend is intended for prod, the operational discipline is "restart after prompt edits" instead.)
2. Generate ONE test actor (any settings) after the restart.
3. Open the resulting `actor_NNNN.md` sidecar. The first line of the prompt MUST be exactly:
   ```
   镜头：full body shot · head to toe · 9:16 vertical · long shot · 全身照
   ```
   If yes → fixes are live, inspect the actual JPGs to judge whether Kling complied with full-body framing.
   If no → still stale; double-check the launch command and process tree.
4. If the prompt is the new format AND the JPG is still chest-up / waist-up: at that point the structural fixes are insufficient and the next escalation is the Kling image model itself (`KLING_DEFAULT_MODEL = "kling-v1"` is the oldest text-to-image gen — newer Kling models have stronger framing adherence). Do NOT preemptively switch the model — that's a separate follow-up that should be cut only after a clean restart still shows half-body output.

## Convention for future Kling prompt edits

After any edit to `actor__chinese_prompt.py` or the prompt-assembling parts of `actor__writer.py`, the next generation's sidecar md is the source of truth for what actually shipped. If the sidecar text does not contain the new strings, the backend did not pick up the edit — restart before drawing conclusions about Kling.

## Touch list

- `specs/development/ai_video_management/changelog.md` — append 089 entry.
