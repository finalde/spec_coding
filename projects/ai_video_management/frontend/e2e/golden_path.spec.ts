import { test, expect } from "@playwright/test";

/** Golden-path e2e — single-section AI Videos focus.
 * Each scenario opens a real triggering file and asserts the render-mode-specific selector.
 */

test.beforeEach(async ({ page }) => {
  page.on("pageerror", (err) => {
    throw new Error(`React reconciliation threw: ${err.message}`);
  });
  page.on("console", (msg) => {
    if (msg.type() === "error") throw new Error(`console.error: ${msg.text()}`);
  });
});

test("home page renders with single AI Videos sidebar section", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("navigation", { name: "File tree" })).toBeVisible();
  await expect(page.getByText("AI Videos")).toBeVisible();
});

test("ShotPairView renders Kling + Seedance side-by-side", async ({ page }) => {
  await page.goto("/file/" + encodeURIComponent("ai_videos/wukong_juexing/prompts/shot02_kling.md"));
  await expect(page.locator(".shot-pair-view")).toBeVisible();
  await expect(page.getByText("Kling (image-to-video)")).toBeVisible();
  await expect(page.getByText("Seedance (text-to-video)")).toBeVisible();
});

test("ShotlistTableView renders shot rows as clickable buttons", async ({ page }) => {
  await page.goto("/file/" + encodeURIComponent("ai_videos/wukong_juexing/shotlist.md"));
  await expect(page.locator(".shotlist-table-view")).toBeVisible();
  await expect(page.getByRole("button", { name: /shot01/ })).toBeVisible();
});

test("ImageRefView renders prompt + fallback when png missing", async ({ page }) => {
  await page.goto("/file/" + encodeURIComponent("ai_videos/wukong_juexing/characters/ref_images/main_seedream.md"));
  await expect(page.locator(".image-ref-view")).toBeVisible();
  await expect(page.getByText("Seedream prompt")).toBeVisible();
  const hasFallback = await page.getByText("尚未生成立绘").isVisible().catch(() => false);
  const hasImg = await page.locator(".image-ref-img").isVisible().catch(() => false);
  expect(hasFallback || hasImg).toBe(true);
});

test("MarkdownView renders main.md with locked-block pill", async ({ page }) => {
  await page.goto("/file/" + encodeURIComponent("ai_videos/wukong_juexing/characters/main.md"));
  await expect(page.locator(".markdown-view")).toBeVisible();
  await expect(page.locator(".locked-block")).toBeVisible();
});

test("Sub-type badge renders for wukong_juexing in sidebar", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator(".subtype-badge.subtype-short").first()).toBeVisible();
});

test("Origin/Host gate: PUT from foreign Origin returns 403", async ({ request }) => {
  const r = await request.put("/api/file", {
    headers: {
      Origin: "http://evil.example.com",
      "If-Unmodified-Since": new Date().toUTCString(),
    },
    data: { path: "ai_videos/wukong_juexing/README.md", content: "test" },
  });
  expect(r.status()).toBe(403);
});

test("Out-of-sandbox paths return 404", async ({ request }) => {
  // Anything not under ai_videos/ is invisible to the sandbox.
  const probes = ["node_modules/anything.md", "../escape.md", "random_top_level/file.md"];
  for (const probe of probes) {
    const r = await request.get(`/api/file?path=${encodeURIComponent(probe)}`);
    expect(r.status()).toBe(404);
  }
});
