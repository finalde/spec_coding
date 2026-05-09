import { defineConfig, devices } from "@playwright/test";

/** Two Playwright projects: one per advertised runtime mode.
 * - prod-mode: single-process FastAPI serving SPA + API on 8766
 * - dev-mode:  Vite dev-server on 5174 proxying /api to backend on 8766
 *
 * The dev-mode baseURL deliberately points at the Vite port so the proxy `configure`
 * hook is part of the test surface (catches Origin-rewrite regressions).
 */
export default defineConfig({
  testDir: ".",
  timeout: 30_000,
  retries: 0,
  use: {
    headless: true,
  },
  projects: [
    {
      name: "prod-mode",
      use: { ...devices["Desktop Chrome"], baseURL: "http://127.0.0.1:8766" },
    },
    {
      name: "dev-mode",
      use: { ...devices["Desktop Chrome"], baseURL: "http://127.0.0.1:5174" },
    },
  ],
});
