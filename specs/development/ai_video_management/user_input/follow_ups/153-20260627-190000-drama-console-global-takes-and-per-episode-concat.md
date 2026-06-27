# Follow-up draft 153 — 2026-06-27
Drama production console (main page): add a global 全局定版 button + a per-episode 拼接成片 button list.

---
target_stage: 6
target_artifacts:
  - apps/ui/src/components/DramaDashboard.tsx
  - apps/api/routes/drama__route.py
severity: medium
---

On the drama main page (`DramaDashboard`, the 🎬 剧集制作台 console):

1. **全局定版 button** — a drama-wide counterpart to the per-episode 定版
   (`select-episode-takes`). Walks every `episodes/ep{NN}/` of the drama and, for
   each shot, locks its newest `renders/` take to a stable `shot{NN}.mp4`
   (`renders/` left untouched). Does NOT concat. A single episode with no
   shots / no render is reported, not fatal.

2. **Per-episode 拼接成片 button** — the main page lists every episode (with
   定版 progress + whether a master already exists); each row has a one-click
   button that concats that episode's locked takes into `ep{NN}.mp4` (reuses the
   existing `/api/concat-episode`, defaults lang=original / no rife / auto plan).
   Disabled until the episode has at least one 定版-locked shot.

New backend endpoints: `POST /api/select-drama-takes`, `POST /api/list-drama-episodes`.
