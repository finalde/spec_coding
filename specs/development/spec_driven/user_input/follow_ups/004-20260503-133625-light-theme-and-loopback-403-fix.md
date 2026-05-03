# Follow-up draft 004 — 2026-05-03

Summary: (a) Apply the new repo-wide **light-theme rule** (added to `CLAUDE.md` under "Project rules") to the spec_driven webapp by removing every `@media (prefers-color-scheme: dark)` override on app chrome and switching `:root { color-scheme }` from `light dark` to `light`. The rule itself is cross-project and lives in `CLAUDE.md`, NOT in this project's spec — this follow-up is the spec_driven *application* of the rule. (b) Fix the `403 forbidden` the user hits when clicking "Build prompt" while the SPA is opened at `http://localhost:8765/` instead of `http://127.0.0.1:8765/` — the Origin/Host middleware's strict string compare treats `localhost` as a foreign origin even though both literals resolve to the same loopback socket.

## (a) Light-theme — repo-wide rule, applied here

### Where the rule lives

The cross-project preference ("webapps default to a light theme; no `prefers-color-scheme: dark` overrides on app chrome") is documented in `CLAUDE.md` under `## Project rules (under projects/)`. It is NOT a spec_driven-specific decision and MUST NOT be re-derived from this follow-up by future regenerations of `spec_driven`'s spec — the source of truth is `CLAUDE.md`.

### What this follow-up changes in spec_driven

- `projects/spec_driven/frontend/src/styles.css`:
  - `:root { color-scheme: light dark; }` → `:root { color-scheme: light; }`.
  - Deleted every `@media (prefers-color-scheme: dark) { ... }` block targeting `body`, `aside.sidebar`, `.toolbar`, `.markdown-view`, `.qa-view`, `.regen-panel`, and `button`.
  - Kept the dark `<pre>` code-block colors inside `.regen-prompt-block` (`#0d1117` / `#c9d1d9` / `#161b22`) and the dark `.markdown-view pre` / `.code-view pre` palette — those are intentional per NFR-16 / A11Y-11 (validated for WCAG AA contrast). The CLAUDE.md rule explicitly carves these out.
- No spec FR/NFR is added — theme is now a CLAUDE.md-level rule, and the spec already describes the visual hierarchy in functional terms.

## (b) Origin/Host middleware: accept loopback equivalents

### Bug

`projects/spec_driven/backend/libs/api_security.py` compares request `Origin` and `Host` headers byte-for-byte against the bound `http://127.0.0.1:8765` / `127.0.0.1:8765`. The browser sends whatever the user typed in the address bar, so opening the SPA at `http://localhost:8765/` and clicking "Build prompt" produces `Origin: http://localhost:8765` → middleware returns `403 forbidden`. (Independent: when the user runs `make run-frontend` and accesses Vite at `http://127.0.0.1:5173/`, the resulting cross-port `Origin: http://127.0.0.1:5173` is *intentional* cross-origin and stays a 403; that case is out of scope for v1.)

### Why validation didn't catch it

`backend/tests/unit/test_api.py` covers four cases for the guarded mutation routes:

1. no `Origin` header → 403 (`test_put_without_origin_returns_403`).
2. `Origin: http://evil.example.com` → 403 (`test_put_with_foreign_origin_returns_403`).
3. `Host: evil.com` → 403 (`test_put_with_bad_host_returns_403`).
4. `Origin: http://127.0.0.1:8765` + `Host: 127.0.0.1:8765` → 200 (`test_put_with_legitimate_origin_succeeds`).

`validation/acceptance_criteria.md` AC-11, `validation/bdd_scenarios.md` "Cross-origin save attempt", and `validation/system_tests.md` SYS-16 all assert the same shape: hostile-domain → 403 and exact-127.0.0.1 → 200. None exercise `Origin: http://localhost:PORT` / `Host: localhost:PORT`. The realistic developer-flow case ("I typed `localhost` in the address bar") was simply absent from the gate — the spec prose treated `localhost` and `127.0.0.1` as interchangeable (NFR-3, NFR-7) but never tested that interchangeability against the middleware's literal string compare. That's a coverage gap, not a logic flaw in any individual test.

### Fix

- Extend `BoundOrigin` with two methods producing **allow-lists** instead of a single string: `origin_allow_list()` and `host_allow_list()`. When the bound host is a loopback literal (`127.0.0.1` or `localhost`), both literals are admitted at the bound port; otherwise the allow-list collapses to the single bound value. IPv6 (`::1`) is intentionally NOT added in v1 — uvicorn binds IPv4-only and IPv6 traffic does not reach it.
- `OriginHostMiddleware` precomputes the two allow-sets in `__init__` and replaces the equality check with `in` membership.
- 403 branches stay byte-identical for foreign / missing values, preserving CSRF defense.

### Spec / validation updates

- `final_specs/spec.md` FR-9: explicitly admit the loopback equivalence for `localhost` ↔ `127.0.0.1` at the bound port.
- `validation/acceptance_criteria.md` AC-11: extend with two new "Then" branches asserting `Origin: http://localhost:8765` + `Host: localhost:8765` → **200** and that any other host literal still → 403.
- `backend/tests/unit/test_api.py`: add `test_put_with_localhost_origin_succeeds` and `test_post_regen_prompt_with_localhost_origin_succeeds`.

## Out of scope (this follow-up)

- A user-toggleable theme picker in spec_driven. v1 stays light-only per the new CLAUDE.md rule.
- Cross-port dev-mode CORS between Vite (5173) and FastAPI (8765). v2 concern.
- IPv6 loopback (`[::1]`). uvicorn is bound IPv4-only.
