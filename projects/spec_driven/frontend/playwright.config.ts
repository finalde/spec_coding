import { defineConfig, devices } from "@playwright/test";

const REPO_ROOT = "../../..";
const BACKEND_CMD = `python ${REPO_ROOT}/projects/spec_driven/backend/main.py`;
const FRONTEND_CMD = "npm run dev";

const PORT_BACKEND = 8765;
const PORT_FRONTEND = 5173;

const URL_BACKEND = `http://127.0.0.1:${PORT_BACKEND}`;
const URL_FRONTEND = `http://127.0.0.1:${PORT_FRONTEND}`;

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  workers: 1,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  reporter: [["list"]],
  timeout: 60_000,
  expect: { timeout: 10_000 },

  use: {
    actionTimeout: 10_000,
    navigationTimeout: 15_000,
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
    video: "off",
    permissions: ["clipboard-read", "clipboard-write"],
  },

  webServer: [
    {
      command: BACKEND_CMD,
      url: `${URL_BACKEND}/api/tree`,
      reuseExistingServer: !process.env.CI,
      timeout: 30_000,
      stdout: "pipe",
      stderr: "pipe",
    },
    {
      command: FRONTEND_CMD,
      url: URL_FRONTEND,
      reuseExistingServer: !process.env.CI,
      timeout: 30_000,
      stdout: "pipe",
      stderr: "pipe",
    },
  ],

  projects: [
    {
      name: "run-prod",
      testMatch: /dogfood\.spec\.ts/,
      grepInvert: /SYS-16b/,
      use: {
        ...devices["Desktop Chrome"],
        baseURL: URL_BACKEND,
      },
    },
    {
      name: "run-frontend",
      testMatch: /dogfood\.spec\.ts/,
      grep: /SYS-16b/,
      use: {
        ...devices["Desktop Chrome"],
        baseURL: URL_FRONTEND,
      },
    },
  ],
});
