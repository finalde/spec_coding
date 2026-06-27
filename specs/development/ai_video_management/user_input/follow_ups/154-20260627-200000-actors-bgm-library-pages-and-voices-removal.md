# Follow-up draft 154 — 2026-06-27
Turn `_actors` / `_bgm` into named library main pages (演员库 / 背景音乐库) with their toolbar + grid consolidated onto the page; delete the `_voices` library.

---
target_stage: 6
target_artifacts:
  - apps/ui/src/components/Sidebar.tsx
  - apps/ui/src/components/ActorGrid.tsx
  - apps/ui/src/components/BgmGrid.tsx
  - libs/infrastructure/readers/tree__reader.py
severity: medium
---

1. **演员库**: the left-nav `_actors/` folder shows the Chinese label **演员库**.
   Clicking the node opens its own main page (`/actors`) on the right — like a
   drama node. The left-nav action buttons (生成演员 / 导入演员 / 网格) move ONTO
   that page; since the page already IS the grid, the standalone 网格 button is
   dropped (consolidated).

2. **背景音乐库**: same treatment for `_bgm/` → label **背景音乐库**, main page
   `/bgm`, toolbar (生成 BGM / 导入下载音乐) moved onto the page.

3. **Delete `_voices`**: remove the `ai_videos/_voices/` folder and all its
   contents, plus its left-nav surface (buttons, `/voices` grid route,
   VoicePoolGenerator). Backend `/api/voices/*` endpoints are left defined but
   unreachable from the nav.
