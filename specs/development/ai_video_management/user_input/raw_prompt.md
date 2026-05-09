# Raw prompt — ai_video_management

**Captured:** 2026-05-05
**task_id:** ai_video_management-20260505-002710
**task_type:** development
**task_name:** ai_video_management

## User's words

> now lets build a new webapp with a backend and front end, call it ai_video_management, basically, it is similar to spec_driven project, but this one is used to visualized and manage the artifacts of ai_videos instead of specs

## Context the user implicitly invokes

- Existing parallel webapp: `projects/spec_driven/` — interactive viewer/editor SPA for `specs/{task_type}/{task_name}/` artifacts. FastAPI backend on `127.0.0.1:8765`, React + Vite frontend.
- The new webapp targets `ai_videos/{task_name}/` artifacts instead — but otherwise wants the same overall shape (sidebar viewer, edit-in-place, regen prompts, pinning, security model, light theme).
- The user just shipped `ai_videos/wukong_juexing/` (a YouTube-Shorts cinematic Sun Wukong project) end-to-end via the agent_team pipeline. That run produced 17 deliverables under `ai_videos/wukong_juexing/` (character bible + Seedream立绘 prompt + style_guide + script + shotlist + 10 dual prompts + publish + README) plus the spec-pipeline artifacts under `specs/ai_video/wukong_juexing/`. The new webapp should make that directory tree navigable, editable, and regen-promptable — same as `spec_driven` does for `specs/`.

## What's open (deferred to interview)

- Visual / view modes specific to ai_video: shot-storyboard view (5 shots in row with thumbnails + durations + hex chips)? side-by-side Kling vs Seedance per shot? image preview for `ref_images/`?
- Render / preview integration: just text-prompt management, or also embed Kling/Seedance/Seedream API calls so the user can render in-browser? (Likely out of v1 scope — user can iterate.)
- Pinning surface for ai_video: same `<stage>/promoted.md` pattern as `spec_driven`, or different granularity (per-shot pins)?
- Regen-prompt scopes: should the webapp surface `scope=episode N` (novels) and `scope=project` (shorts) as a UI toggle, since `agent_refs/project/ai_video.md` rule 10 calls them out?
- Cross-publish surfaces: does the ai_video sub-type (`short` vs `novel`) drive different navigation modes?
- Tooling parity: same FastAPI + React + Vite + Vitest + Playwright + pytest stack as `spec_driven`?
