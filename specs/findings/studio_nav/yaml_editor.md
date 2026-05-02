# Research — yaml_editor — studio_nav

**Sources:**

| # | Source | URL |
|---|---|---|
| 1 | @monaco-editor/react (npm) | https://www.npmjs.com/package/@monaco-editor/react |
| 2 | suren-atoyan/monaco-react (GitHub) | https://github.com/suren-atoyan/monaco-react |
| 3 | vite-plugin-monaco-editor | https://www.npmjs.com/package/vite-plugin-monaco-editor |
| 4 | Vite #1791 — importing monaco-editor | https://github.com/vitejs/vite/discussions/1791 |
| 5 | remcohaszing/monaco-yaml (GitHub + README) | https://github.com/remcohaszing/monaco-yaml |
| 6 | monaco-yaml docs site | https://monaco-yaml.js.org/ |
| 7 | YAML+JSONSchema Monaco demo | https://yaml-monaco-jsonschema.vercel.app/ |
| 8 | @codemirror/lang-yaml | https://github.com/codemirror/lang-yaml |
| 9 | @codemirror/lint | https://www.npmjs.com/package/@codemirror/lint |
| 10 | uiwjs/react-codemirror | https://github.com/uiwjs/react-codemirror |
| 11 | discuss.codemirror — YAML lint | https://discuss.codemirror.net/t/yaml-linter-for-uiw-react-codemirror-or-codemirror-v6/4976 |
| 12 | Sourcegraph — Monaco→CodeMirror migration | https://sourcegraph.com/blog/migrating-monaco-codemirror |
| 13 | Replit — Betting on CodeMirror | https://blog.replit.com/codemirror |
| 14 | Monaco vs CodeMirror comparison | https://agenthicks.com/research/codemirror-vs-monaco-editor-comparison |
| 15 | @focus-reactive/react-yaml | https://www.npmjs.com/package/@focus-reactive/react-yaml |
| 16 | fraserxu/react-yaml-editor | https://github.com/fraserxu/react-yaml-editor |

**Key findings (≤500 tokens):**

- **`@monaco-editor/react`** (suren-atoyan, the de facto React wrapper) handles worker loading automatically out-of-the-box — no MonacoEnvironment plumbing needed for plain Monaco. The pain only starts when you add a language plugin like `monaco-yaml`, which ships its own dedicated worker that the wrapper does not know about. So for a YAML‑only editor, you must wire one extra worker.
- **`monaco-yaml` (v5.4.1, Feb 2026)** is the only mature, maintained YAML language service for Monaco. It gives JSON-Schema–based validation (red squiggles), hover docs, completion, and Prettier formatting. It is the Right Tool for our `plan.yaml`, since the schema is stable and documented in `agent_team__execution_plan_compiler.md`.
- **Known Vite gotcha for monaco-yaml:** loading `monaco-yaml/yaml.worker` directly via `new Worker(new URL(...))` breaks under Vite. The README's documented workaround is a one-line wrapper file (`yaml.worker.js` → `import 'monaco-yaml/yaml.worker.js'`) imported with `?worker`. This is the 2025/2026-current best practice and is the same pattern GitLab landed in MR !152660. Avoid `vite-plugin-monaco-editor` for this task — it duplicates what the wrapper already does and historically conflicts with monaco-yaml's worker.
- **Bundle size:** Monaco core ≈ 2–5 MB gzipped depending on language packs. For a single-route, single-file editor that's substantial but acceptable when the chunk is **lazy-loaded** (`React.lazy` on `ExecutionPlanModule`). Replit and Sourcegraph migrated away mainly because they ship Monaco on every page; that's not us.
- **CodeMirror 6 + `@codemirror/lang-yaml`** is dramatically lighter (~150–300 KB gzipped with extensions) but has **no built‑in JSON-Schema validation for YAML**. You'd have to hand-roll a linter via `@codemirror/lint` + `js-yaml` + `ajv`. That's real engineering work for a feature monaco-yaml gives us for free.
- **`@focus-reactive/react-yaml`** is built on CodeMirror 6 and gives you a controlled YAML field with syntax highlighting, but it does **not** do JSON-Schema validation either. `fraserxu/react-yaml-editor` is unmaintained (last publish 6 years ago) — disqualified.
- Monaco-yaml schema validation requires only: a stable `uri` per schema (use `http://example.com/plan-schema.json` — the README warns that with Vite the URI is also used as the schema name, and a real fetchable URL would trigger network IO), `fileMatch: ['**/plan.yaml']`, and an inline `schema` object. We can ship the JSON Schema as a TS object alongside the editor — no remote fetch.

## Detailed notes

### @monaco-editor/react (suren-atoyan/monaco-react)

- npm: `@monaco-editor/react` — React wrapper around `monaco-editor`. ~2 M+ weekly downloads, current and maintained.
- Auto-loads the editor + base workers from CDN by default; for self-hosted/offline you call `loader.config({ paths: { vs: '/monaco/vs' } })` or `loader.config({ monaco })` after importing your own `monaco-editor` instance.
- For Vite + a language plugin (monaco-yaml), the standard recipe is **import the local `monaco-editor` package, set `MonacoEnvironment` before the first `<Editor />` mounts, then call `loader.config({ monaco })`** so the wrapper uses our locally bundled instance — this is the only way to ensure `monaco-yaml` and the wrapper share one Monaco instance (otherwise schemas are wired into a different copy and silently no-op).

### monaco-yaml

- v5.4.1 (Feb 2026). Ships YAML 1.1/1.2, schema validation, formatting, hover, completion. Has `configureMonacoYaml(monaco, { enableSchemaRequest, schemas: [...] })`.
- Vite worker recipe (verbatim from README, validated by GitLab MR !152660):

  ```ts
  // yaml.worker.ts
  import 'monaco-yaml/yaml.worker.js'
  ```

  ```ts
  // monacoEnv.ts — load before any <Editor/> mounts
  import * as monaco from 'monaco-editor'
  import EditorWorker from 'monaco-editor/esm/vs/editor/editor.worker?worker'
  import YamlWorker from './yaml.worker?worker'
  import { configureMonacoYaml } from 'monaco-yaml'
  import { loader } from '@monaco-editor/react'

  self.MonacoEnvironment = {
    getWorker(_, label) {
      if (label === 'yaml') return new YamlWorker()
      return new EditorWorker()
    },
  }
  loader.config({ monaco })

  configureMonacoYaml(monaco, {
    enableSchemaRequest: false,
    schemas: [
      {
        uri: 'http://spec-coding/plan-schema.json',
        fileMatch: ['**/plan.yaml'],
        schema: planSchema, // local TS-imported JSON Schema
      },
    ],
  })
  ```

- Watch-out: the README explicitly warns "monaco-yaml is using a different instance of monaco-editor than your project" — fix by deduping (`npm ls monaco-editor` should show one copy; add `resolutions` / `overrides` if not).

### CodeMirror 6 + @codemirror/lang-yaml

- Tiny core (~124 KB gzipped baseline; ~150–300 KB with our extension set).
- `@codemirror/lang-yaml` gives parsing + highlighting only. **No diagnostics**.
- For schema validation we'd need: `js-yaml` to parse → `ajv` against our schema → translate ajv errors to `Diagnostic[]` for `@codemirror/lint`'s `linter()`. Mapping ajv `instancePath` back to source positions is the painful part — there's no canonical helper.
- `@uiw/react-codemirror` is the standard React wrapper; mature.
- Sourcegraph and Replit migrated **from** Monaco **to** CodeMirror, but their motivation was multi-page bundle weight, not single-route. Our case is the opposite end of that tradeoff.

### react-yaml (specialized)

- `@focus-reactive/react-yaml`: maintained (~26 K weekly downloads), CodeMirror-based, YAML highlight + value/text dual mode, theming. **No JSON-Schema validation.** Useful only as a sugar layer if we picked CodeMirror.
- `react-yaml-editor` (fraserxu): last publish 6 years ago, v0.1.1. **Disqualified.**

## Recommendation

- **Pick:** `@monaco-editor/react` + `monaco-yaml`.
- **Vite worker setup:** create a one-line wrapper `src/editor/yaml.worker.ts` containing `import 'monaco-yaml/yaml.worker.js'`; in a module imported once at app boot (e.g. `src/editor/monacoEnv.ts`), set `self.MonacoEnvironment.getWorker` to return `new YamlWorker()` for label `'yaml'` and `new EditorWorker()` (from `monaco-editor/esm/vs/editor/editor.worker?worker`) otherwise, then call `loader.config({ monaco })` so the React wrapper shares the same Monaco instance that `configureMonacoYaml(monaco, …)` configures.
- **Schema validation in v1?** **Yes.** The whole reason we picked Monaco over the lighter CodeMirror stack is that monaco-yaml gives us schema validation for free. Ship a local JSON Schema for `plan.yaml` (derived from `agent_team__execution_plan_compiler.md` § Output) as a TS module, `enableSchemaRequest: false`, and use a synthetic URI like `http://spec-coding/plan-schema.json`. Even a permissive schema (require `metadata`, `globals`, `work_units`, with `work_units[].id` matching `^WU-\d{3}$`) catches the common hand-edit mistakes.
- **Bundle-size note:** Monaco core ~2–3 MB gzipped, +~150 KB for monaco-yaml. We'll lazy-load `ExecutionPlanModule` via `React.lazy` so the rest of the studio shell stays cheap; the YAML chunk only loads when the user opens the Plan tab. Acceptable for a single-user local studio.

## Gaps

- Did not verify exact gzipped chunk size for our specific Monaco subset (core + JSON + YAML + a single theme); confirm via `vite build --report` after wiring.
- `monaco-yaml` formatting uses Prettier under the hood — confirm it ships the YAML parser bundle (we don't want a surprise Prettier core load).
- Did not test whether `@monaco-editor/react`'s default CDN-loader path conflicts with our locally bundled `monaco-editor` if `loader.config({ monaco })` is called late (after first render). Best practice is to call it at module scope before any `<Editor />` mounts; verify in implementation.
- No measurement of monaco-yaml memory footprint with large `plan.yaml` files (>1 MB). Our plans are tiny so unlikely to matter, but unverified.
