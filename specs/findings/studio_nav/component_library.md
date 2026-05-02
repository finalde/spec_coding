# Research — component_library — studio_nav

**Sources:**
| # | Title | URL | Type | Quality (1–5) | Recency |
|---|-------|-----|------|----------------|---------|
| 1 | Mantine v8 — official site | https://v8.mantine.dev/ | docs | 5 | 2026-04 |
| 2 | Mantine CodeHighlight (`@mantine/code-highlight`) | https://mantine.dev/x/code-highlight/ | docs | 5 | 2026 |
| 3 | Mantine Notifications system | https://mantine.dev/x/notifications/ | docs | 5 | 2026 |
| 4 | Mantine AppShell | https://mantine.dev/core/app-shell/ | docs | 5 | 2026 |
| 5 | Mantine v8.0.0 changelog | https://mantine.dev/changelog/8-0-0/ | docs | 4 | 2025 |
| 6 | Mantine vs Chakra UI vs MUI: 2026 comparison | https://adminlte.io/blog/mantine-vs-chakra-ui-vs-mui/ | blog | 3 | 2026 |
| 7 | Best React Component Libraries 2026 (Untitled UI) | https://www.untitledui.com/blog/react-component-libraries | blog | 3 | 2026 |
| 8 | shadcn/ui Vite installation guide | https://ui.shadcn.com/docs/installation/vite | docs | 5 | 2026 |
| 9 | How to Build a Modern Admin Dashboard with shadcn/ui in 2026 | https://dev.to/ausrobdev/how-to-build-a-modern-admin-dashboard-with-shadcnui-in-2026-3477 | blog | 3 | 2026 |
| 10 | React Admin Dashboard — Best Templates & Frameworks (Refine) | https://refine.dev/blog/react-admin-dashboard/ | blog | 3 | 2026 |

**Key findings (≤500 tokens):**
- **Mantine v8** ships **120+ components and ~70 hooks** with **native CSS Modules** (no runtime CSS-in-JS since the v7 rewrite); 28k+ GitHub stars and ~2.2M monthly downloads. Provides every primitive `studio_nav` needs *out of the box, in one package*: `AppShell` (header / navbar / aside / footer with `position: fixed`), `Tabs`, `NavLink`, `Card`, `Modal` + `modals` manager, `Notifications` (toast), `TypographyStylesProvider` for markdown, `@mantine/code-highlight` (Shiki/HLJS adapters with `CodeHighlightTabs`). Theming is token-based with built-in dark mode.
- **Ant Design v5** is the largest enterprise React kit (~92k stars), purpose-built for data-heavy admin dashboards; v5's design-token system makes brand recoloring straightforward and tree-shaking is improved. Bundle is heavy but acceptable for an internal tool loaded once. Strong on tables/forms; weaker for a "beautified question card" feel — its visual language is dense corporate, not breezy.
- **shadcn/ui** is **not a dependency** — you `npx shadcn add <component>` and the source is *copied into your repo* (Radix primitives + Tailwind classes you own). Best Tailwind fit, smallest runtime, but you assemble the AppShell from `Sidebar` + `SidebarProvider` blocks, wire `sonner` for toasts (legacy `Toast` deprecated), and integrate Monaco yourself. Tailwind v4 / React 19 is the new default but the docs explicitly say Tailwind v3 + React 18 projects stay on v3 — compatible with the existing stack.
- **4th candidate considered: Chakra UI v3 / Park UI / MUI Joy** — Chakra v3 has a new Panda CSS engine (60+ components, accessibility-first) but fewer admin-shell primitives than Mantine; not a clear win over the top three. No 4th finalist warranted.
- For a **single-user local admin tool** with markdown viewer, YAML editor (Monaco), tabs, toasts, modals, and a polished question-card layout, **Mantine v8 wins on "everything in one box"**. shadcn gives the cleanest Tailwind continuity but every feature (sidebar, toasts, Monaco) is wired by hand. Ant Design wins on data-grid depth that this task does not need.
- **Bundle posture for an internal tool** — all three are acceptable; bundle is not a deciding factor since the app loads once locally on `127.0.0.1`.
- **TypeScript first-class** — all three. Mantine and Ant Design ship types in the package; shadcn copies typed `.tsx` source into `src/components/ui/`.

## Detailed notes

### Source 1 — Mantine v8 official site
- URL: https://v8.mantine.dev/
- Insights: 120+ components, 70 hooks, native CSS (no runtime CSS-in-JS), built-in dark theme, `@mantine/form` is 6.3kb gz, 28k+ GitHub stars, 2.2M monthly downloads. Extension packages: notifications, modals, spotlight (command palette), code-highlight, rich-text, carousel, dates.

### Source 2 — Mantine CodeHighlight
- URL: https://mantine.dev/x/code-highlight/
- Insights: `@mantine/code-highlight` no longer depends on `highlight.js` directly — adapter API supports **Shiki** (TypeScript-grade highlighting) or `highlight.js`. `CodeHighlightTabs` component organizes multiple code blocks; `getFileIcon` prop assigns icons by filename. Good fit for the YAML viewer; for full editing the spec calls for Monaco, which is a separate `@monaco-editor/react` install regardless of library choice.

### Source 3 — Mantine Notifications
- URL: https://mantine.dev/x/notifications/
- Insights: Drop-in toast system via `<Notifications />` + `notifications.show({...})`. Matches the spec's "notification toasts" requirement with zero extra glue.

### Source 4 — Mantine AppShell
- URL: https://mantine.dev/core/app-shell/
- Insights: `AppShell` ships header / navbar / aside / footer slots, all `position: fixed` so they don't scroll with content. Direct match for the "two-pane: vertical module nav left, content pane right" requirement in `spec.md` Acceptance Criteria 2.

### Source 5 — Mantine v8.0.0 changelog
- URL: https://mantine.dev/changelog/8-0-0/
- Insights: v8 is the current major; CSS Modules architecture inherited from v7. Active maintenance into 2026.

### Source 6 — adminlte Mantine vs Chakra vs MUI comparison
- URL: https://adminlte.io/blog/mantine-vs-chakra-ui-vs-mui/
- Insights: "Mantine is the strongest all-around choice for new projects in 2026." Concrete numbers: Mantine 120+ components / 100+ hooks / CSS Modules; Chakra 60+ components / Panda CSS; MUI 70+ components / 6.7M weekly downloads / Emotion. (Article doesn't cover Ant Design or shadcn — confirmed via fetch.)

### Source 7 — Untitled UI 2026 library guide
- URL: https://www.untitledui.com/blog/react-component-libraries
- Insights: Ant Design ~92k stars, dominates enterprise / Asia, "purpose-built for data-heavy business applications." shadcn ecosystem is the fastest-growing in 2026, especially for premium admin templates. "Mantine is quietly winning the developer experience war."

### Source 8 — shadcn/ui Vite install
- URL: https://ui.shadcn.com/docs/installation/vite
- Insights: Install steps for existing Vite project — add `baseUrl` + `paths` to `tsconfig.json` and `tsconfig.app.json`, install `@types/node`, update `vite.config.ts` for `@` alias, then `npx shadcn init` and `npx shadcn add sidebar sonner dialog tabs card`. Existing **Tailwind v3 + React 18 apps stay on v3** when adding components — explicit compatibility note. `Toast` is deprecated in favor of `Sonner`.

### Source 9 — DEV "Modern Admin Dashboard with shadcn/ui in 2026"
- URL: https://dev.to/ausrobdev/how-to-build-a-modern-admin-dashboard-with-shadcnui-in-2026-3477
- Insights: Honest take — "shadcn/ui provides the component philosophy and accessibility foundation, but production dashboards require substantial additional architecture and pre-built patterns." Implication for `studio_nav`: with shadcn you would assemble AppShell + nav + tabs + toast yourself; not a pre-built `<AppShell>` like Mantine.

### Source 10 — Refine 2026 admin dashboard guide
- URL: https://refine.dev/blog/react-admin-dashboard/
- Insights: Mantine + Next/Vite is a popular admin-dashboard recipe for 2026; `mantine-analytics-dashboard` reference template uses Mantine 8 + React 18.

## Recommendation
- **Pick:** **Mantine v8**
- **Why:** Mantine v8 alone covers every component the spec lists — `AppShell` for the two-pane shell, `Tabs` + `NavLink` for module nav, `Modal` + `@mantine/modals` for the confirm-dialog gate on repo edits, `@mantine/notifications` for toasts, `TypographyStylesProvider` for markdown, and `@mantine/code-highlight` (Shiki) for read-only YAML; Monaco still slots in as a separate `@monaco-editor/react` for the editable plan view, same as it would for any library. The CSS-Modules architecture means **no runtime CSS-in-JS overhead**, theming is token-based, and it coexists with the existing Tailwind utilities (Mantine wins on its own scope; Tailwind keeps working for one-off layout). For a single-user local tool the bundle is irrelevant; ship velocity dominates, and Mantine is by far the lowest-glue option for the "beautified question card" + module-nav scope.
- **Migration cost from current Tailwind setup:** **Low–Medium.** Add `@mantine/core @mantine/hooks @mantine/notifications @mantine/modals @mantine/code-highlight @monaco-editor/react`, import the Mantine CSS in `main.tsx`, wrap `<App />` in `<MantineProvider>` + `<Notifications />` + `<ModalsProvider>`, and rewrite `TaskDetail.tsx` against `AppShell`. Tailwind stays in place for transitional bespoke styling; we are doing a full UI rewrite anyway (interview Q1 = "redo from scratch"), so the rewrite cost is already budgeted by the spec — the *library swap* itself is roughly one provider + one CSS import.

## Gaps
- No source quoted a hard initial-bundle KB number for Mantine v8 vs Ant Design v5 vs shadcn-blocks side-by-side; secondary sources only argue qualitatively that bundle is not a blocker for internal admin tools. Numeric bundle benchmarks were not located in the searches performed.
- The adminlte "Mantine vs Chakra vs MUI" article (Source 6) does not cover Ant Design or shadcn — comparison data for those came from Untitled UI (Source 7) and Refine (Source 10), both of which are blog-tier.
- I did not fetch the official Ant Design v5 docs or Ant Design Pro repo directly — the Ant Design data above is from secondary sources (Untitled UI, Refine, AdminLTE listings). Sufficient for a qualitative comparison; insufficient for primary-source quotes on AntD v5 token API.
- `@mantine/code-highlight` is a *viewer* (Shiki), not an editor. The spec's `ExecutionPlanModule` requires Monaco YAML *editing*, which sits outside any of the four libraries — `@monaco-editor/react` is recommended regardless of pick. This is mentioned in the recommendation but not from a single authoritative source.
