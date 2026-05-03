# Follow-up draft 006 — 2026-05-03

Summary: Two coupled changes. (a) Apply **Option A** for the `localhost:5173 → 8765` Build-prompt 403: make the Vite dev-server proxy rewrite the `Origin` header to match the backend's bound origin, so the strict-Origin gate in `api_security.py` stays uniform across `make run-prod` (single process, same-origin) and `make run-frontend` (cross-port via Vite proxy). The backend gate is unchanged. (b) Capture the **class of failure** that allowed this bug to ship past validation as **institutional memory** in the shared `.claude/agent_refs/validation/` refs, so any future development task with multi-mode runtime / reverse-proxy / Origin-style middleware is forced to test the dev-flow shape and forced to question every "v1 out of scope" carve-out at stage 5. The user-stated priority is (b); (a) is the proximate fix.

## (a) The proximate bug fix — Vite proxy rewrites Origin

### Root cause

Browser at `http://localhost:5173/` sends `Origin: http://localhost:5173` on the proxied `POST /api/regen-prompt`. Vite's default proxy preserves that Origin while rewriting Host (when `changeOrigin: true`) — but the backend sees `Origin: http://localhost:5173` and the allow-list is `{http://127.0.0.1:8765, http://localhost:8765}` (loopback aliases at the bound port, per follow-up 004). Mismatch → 403. The same flow under `make run-prod` (browser at `localhost:8765`, fetch is same-origin) sends `Origin: http://localhost:8765` and matches the allow-list → 200. The bug is dev-mode-only.

### Fix

`projects/spec_driven/frontend/vite.config.ts` proxy block: extend each `/api`, `/file`, `/project` entry from a bare target string to an object with `target`, `changeOrigin: true`, AND a `configure(proxy) => proxy.on('proxyReq', proxyReq => proxyReq.setHeader('origin', 'http://127.0.0.1:8765'))` hook. Both `Host` and `Origin` are now rewritten to the bound origin before the request hits the backend, so the backend gate sees the same shape it sees under `make run-prod`. No backend change.

### Why not Option B (backend admits 5173)

Widening `BoundOrigin.origin_allow_list()` to include `:5173` would:
- Couple the production gate to a dev-time port choice.
- Trust ANY local service that happens to bind 5173 (e.g., another dev tool the user runs in a separate terminal).
- Hide a real cross-origin shape from the production-strict gate, which would mask future dev-vs-prod drift.

Option A keeps the strict gate intact and pushes the rewrite into the dev tool that owns the proxy boundary. Standard Vite + strict-backend pattern.

### Why this couldn't have been a stale-bundle / cache problem

`api_security.py` is a backend-only module; rebuilding the frontend bundle has no effect on it. The unit test `test_post_regen_prompt_with_localhost_origin_succeeds` exercises the post-fix code in pytest, so the fix is genuinely on disk and in any restarted backend. The only path that still 403s is the cross-port proxy path — which is exactly the case the follow-up-004 spec carved out.

## (b) The validation-gap class — institutional memory updates

This bug shipped past validation because of three structural gaps in the validation strategy. Each maps to a durable lesson that should not depend on this one bug being remembered.

### Gap 1 — Spec carved out the dev-flow case as "v1 out of scope"

Follow-up 004's prose: *"when the user runs `make run-frontend` and accesses Vite at `http://127.0.0.1:5173/`, the resulting cross-port `Origin` is intentional cross-origin and stays a 403; that case is out of scope for v1."* The validation gate followed the spec literally — AC-11 and SYS-16 assert what the spec said should pass (single-port loopback) and don't assert what was carved out. The runtime gate cannot fail an assertion the spec never made.

The deeper problem: `make run-frontend` is in the spec's own developer workflow (FR-39 lists it). A "v1 out of scope" decision on a feature in the documented dev workflow is a contract-vs-user-feature gap. Stage 5 strategy should have caught this — *"if FR-39 advertises `make run-frontend` as a supported dev target, then the FR-9 carve-out makes a documented workflow 403 every mutation, and that's a UX bug not an out-of-scope decision."* That pushback didn't happen because no principle in `agent_refs/validation/general.md` told stage 5 to scan for spec carve-outs that conflict with documented workflows.

### Gap 2 — The Playwright e2e suite is hard-wired to one runtime mode

`projects/spec_driven/frontend/playwright.config.ts:15-21` boots `python ../backend/main.py` directly (single-process at 8765) and pins `baseURL: "http://127.0.0.1:8765"`. There is no second project / webServer entry that boots `make run-frontend` (Vite at 5173 + backend at 8765) and drives the SPA at the dev-server URL. Every Build-prompt e2e scenario (SYS-9 etc.) runs against the mode where Origin already matches the bound port — i.e., the mode that was already working. The mode the user actually exercises is structurally outside the gate.

`agent_refs/validation/development.md` move #1 ("End-to-end browser dogfood is mandatory, not optional") is true but underspecified — it doesn't say "for every runtime mode the spec advertises." A development project with N runtime modes needs N e2e profiles, not 1.

### Gap 3 — Unit tests mirrored the spec's narrow contract, not the proxied-request shape

`test_post_regen_prompt_with_localhost_origin_succeeds` sends `Origin: http://localhost:8765` + `Host: localhost:8765` — both at the bound port. The realistic developer-flow shape (`Origin: http://localhost:5173` + `Host: 127.0.0.1:8765`) is not tested. Even after Option A's fix, the post-rewrite shape that the backend actually sees IS the same as the existing test (both ports are 8765 after rewrite), but the *missing* test class is "what shape does the backend see in dev mode, and does it pass?" — which would have forced the test author to think about the proxy at all and notice that without the proxy rewrite, the test would NOT have matched reality.

This is `agent_refs/validation/general.md` Principle 1 ("Validate the contract, not the implementation") extended: when a request crosses a reverse proxy or a same-process router that mutates headers, the unit test must simulate the *post-mutation* shape. Mock the proxy if you must; don't mock it away.

### Lessons to add to `agent_refs/validation/`

1. **`general.md` — new Principle 7: "Question every spec-level 'out of scope for v1' carve-out at stage 5."** A carve-out is the spec author's decision to NOT test a behavior. Stage-5 strategy MUST surface every such carve-out back to the user as: *"this is outside the validation gate; confirm that's intended."* When a carve-out conflicts with another part of the spec (FR-39 lists `make run-frontend`; FR-9 carves out the dev-flow at 5173), that's a contract drift, not an acceptable scoping decision — flag it as a `blocker` for stage 5 sign-off.

2. **`development.md` — new Required move 11: "Multi-mode runtime feature parity."** When the spec defines more than one runtime mode (production single-process, dev-server proxy, …) the e2e suite MUST exercise the same user-facing feature in EVERY advertised mode. Mode count = e2e profile count. A feature that "works in mode A but 403s in mode B" where both modes are documented in the spec is a `blocker`, not a carve-out. Concrete requirement: `playwright.config.ts` (or equivalent) ships one `webServer` / project entry per runtime mode the spec lists in its dev-workflow / Makefile-targets section.

3. **`development.md` — new Required move 12: "Cross-origin / cross-port middleware tests must include the proxied-request shape."** When the backend has `Origin`/`Host`/CSRF middleware AND the dev workflow has any reverse-proxy / dev-server proxy, the unit-test set MUST include at least one case that simulates the proxied request shape (Origin = browser-origin, Host = target-origin, both pre-proxy-rewrite) AND at least one case that simulates the post-proxy-rewrite shape. Without the pre-proxy case, the test set diverges from the dev-flow reality. Without the post-proxy case, you can't tell if the proxy rewrite is wired up.

4. **`development.md` — new severity-table rows.** Multi-mode feature parity gap (mode advertised in spec, not exercised in e2e) → `blocker`. Origin/Host middleware with no proxied-shape unit test when a reverse proxy exists → `blocker`. Spec carve-out conflicting with another spec section → `critical` (caught at stage 5; halts strategy sign-off).

## Surface changes

- `projects/spec_driven/frontend/vite.config.ts` — proxy entries upgraded to objects with `changeOrigin: true` + `configure` hook rewriting `Origin` to `http://127.0.0.1:8765`.
- `.claude/agent_refs/validation/general.md` — Principle 7 added (out-of-scope carve-out scanning).
- `.claude/agent_refs/validation/development.md` — Moves 11 and 12 added; severity table extended with three new rows; cite this follow-up 006 of run `spec_driven` as the lesson source.
- `specs/development/spec_driven/final_specs/spec.md` — FR-9 amended with one sentence: in the `make run-frontend` dev mode, the Vite proxy MUST rewrite `Origin` to the bound origin so the backend gate sees the same shape it sees in `make run-prod`. The spec's "out of scope" disclaimer for the cross-port case from follow-up 004 is removed (the case is now in scope and tested).
- `specs/development/spec_driven/validation/acceptance_criteria.md` — AC-11 extended with one new "When/Then" branch asserting the dev-server-proxy flow returns 200 (under `make run-frontend`, the browser-Origin is `http://localhost:5173` but the backend sees the rewritten shape and admits it).
- `specs/development/spec_driven/validation/system_tests.md` — SYS-16 extended OR a new SYS scenario added that boots `make run-frontend` (Vite at 5173 + backend at 8765) and drives Build-prompt against the dev-server, asserting 200. The actual second Playwright profile wiring is acknowledged as a follow-on implementation task; the SYS-test is the contract.
- `specs/development/spec_driven/validation/strategy.md` — one paragraph added under the existing Origin-validation strategy bullet noting the multi-mode-e2e requirement that follow-up 006 introduces (cross-references the new `agent_refs/validation/development.md` move 11).
- `specs/development/spec_driven/user_input/revised_prompt.md` — Last-regenerated line bumped; "Cross-cutting constraints" bullet about the loopback alias updated to reflect that the dev-server case is now in scope (no carve-out remaining).
- `specs/development/spec_driven/changelog.md` — follow-up 006 entry appended.

## Out of scope (this follow-up)

- Wiring up the actual second Playwright `webServer` / project entry for `make run-frontend`. This is real implementation work (boot two processes, manage port collision, set baseURL = 5173 for the project, share fixtures) that warrants its own pass. The SYS-test text and the agent_refs lesson are added so that *next time* a development task ships and stage 5 runs, the missing profile becomes a `blocker` finding. For spec_driven specifically, the missing profile is a known follow-on; the institutional-memory addition prevents the same gap from recurring on future projects.
- Touching `CLAUDE.md`. The validation lessons live in `agent_refs/validation/`, not in `CLAUDE.md` (per follow-up 005's separation: workflow contracts in `CLAUDE.md`; accumulated institutional memory in `agent_refs/`).
- Re-running stage 5 strategy in full. The agent_refs additions and surgical AC / SYS / strategy patches are the correct surgical-update path per `## Follow-up prompt handling` in `CLAUDE.md`. Full stage-5 regen is user-triggered.
- Migrating other spec carve-outs (e.g., IPv6 `::1`, multi-user auth) into-scope. They remain genuinely out of scope; the new Principle 7 only requires they be re-confirmed with the user at stage 5, not automatically expanded.
