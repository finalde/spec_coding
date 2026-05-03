// e2e — Playwright system-test scenarios.
//
// Maps to SYS-1..SYS-27 in specs/development/spec_driven/validation/system_tests.md.
// `make run-prod` is started by playwright.config.ts via the webServer fixture.
//
// Console-error tracking is per-test: each scenario asserts consoleErrors is empty
// (modulo the explicit allow-list for SYS-23 where a 500 is intentionally injected).

import { expect, test, type Page } from "@playwright/test";

function trackConsoleErrors(page: Page, allowed: RegExp[] = []): string[] {
  const errs: string[] = [];
  page.on("console", (msg) => {
    if (msg.type() !== "error") return;
    const t = msg.text();
    if (allowed.some((re) => re.test(t))) return;
    errs.push(t);
  });
  return errs;
}

test.describe("SYS-1 boot smoke", () => {
  test("GET /api/tree returns 200 with both top-level sections; SPA loads at /", async ({ page, request }) => {
    const tree = await request.get("/api/tree");
    expect(tree.status()).toBe(200);
    const body = await tree.json();
    expect(body.children).toBeTruthy();
    const names = body.children.map((c: any) => c.name);
    expect(names).toContain("Claude Settings & Shared Context");
    expect(names).toContain("Projects");

    const errs = trackConsoleErrors(page);
    await page.goto("/");
    await page.waitForSelector('[data-testid="sidebar"]');
    expect(errs).toEqual([]);
  });
});

test.describe("SYS-2 markdown render", () => {
  test("deep-link to spec.md mounts MarkdownView", async ({ page }) => {
    const errs = trackConsoleErrors(page);
    await page.goto("/file/specs/development/spec_driven/final_specs/spec.md");
    await page.waitForSelector('[data-testid="markdown-view"]', { timeout: 10_000 });
    await expect(page.locator('[data-testid="qa-view"]')).toHaveCount(0);
    await expect(page.locator("main h1").first()).toContainText("Specification");
    expect(errs).toEqual([]);
  });
});

test.describe("SYS-3 QaView render", () => {
  test("deep-link to qa.md mounts QaView with Q/A blocks", async ({ page }) => {
    const errs = trackConsoleErrors(page);
    await page.goto("/file/specs/development/spec_driven/interview/qa.md");
    await page.waitForSelector('[data-testid="qa-view"]', { timeout: 10_000 });
    await expect(page.locator('[data-testid="qa-q-block"]').first()).toBeVisible();
    await expect(page.locator('[data-testid="qa-a-block"]').first()).toBeVisible();
    expect(errs).toEqual([]);
  });
});

test.describe("SYS-9 regen-prompt small (<50 KB)", () => {
  test("warning is null on a small interactive prompt", async ({ request }) => {
    const r = await request.post("/api/regen-prompt", {
      headers: { Origin: "http://127.0.0.1:8765" },
      data: {
        project_type: "development",
        project_name: "spec_driven",
        stages: ["interview"],
        modules: { interview: [] },
        autonomous: false,
      },
    });
    expect(r.status()).toBe(200);
    const body = await r.json();
    expect(body.bytes).toBeLessThan(50 * 1024);
    expect(body.warning).toBeNull();
    expect(body.prompt).toMatch(/^# EXECUTION MODE: INTERACTIVE/);
    expect(body.prompt).toContain("regeneration deletes prior outputs first; new generation reads only the inputs.");
  });
});

test.describe("SYS-14 traversal probes return single 404", () => {
  for (const probe of [
    "../etc/passwd",
    "specs/../../etc/passwd",
    "/etc/passwd",
    "specs/development/spec_driven/CON.md",
    "specs/development/spec_driven/final_specs/spec.md::$DATA",
  ]) {
    test(`probe: ${probe}`, async ({ request }) => {
      const r = await request.get(`/api/file?path=${encodeURIComponent(probe)}`);
      expect(r.status()).toBe(404);
    });
  }
});

test.describe("SYS-16 origin validation", () => {
  test("PUT from foreign origin returns 403", async ({ request }) => {
    const r = await request.put("/api/file", {
      headers: { Origin: "http://evil.example.com", Host: "127.0.0.1:8765" },
      data: { path: "specs/development/spec_driven/__scratch__/sys16.md", content: "x" },
    });
    expect(r.status()).toBe(403);
  });

  test("PUT with bad Host returns 403", async ({ request }) => {
    const r = await request.put("/api/file", {
      headers: { Origin: "http://127.0.0.1:8765", Host: "evil.com" },
      data: { path: "specs/development/spec_driven/__scratch__/sys16.md", content: "x" },
    });
    expect(r.status()).toBe(403);
  });
});

test.describe("SYS-18 verb whitelist", () => {
  test("PATCH /api/file returns 405", async ({ request }) => {
    const r = await request.fetch("/api/file", { method: "PATCH" });
    expect(r.status()).toBe(405);
  });

  test("DELETE /api/file returns 405", async ({ request }) => {
    const r = await request.fetch("/api/file?path=foo.md", { method: "DELETE" });
    expect(r.status()).toBe(405);
  });
});

test.describe("SYS-20 sidebar structural sanity", () => {
  test("≥1 leaf under each top-level section", async ({ page }) => {
    const errs = trackConsoleErrors(page);
    await page.goto("/");
    await page.waitForSelector('[data-testid="sidebar"]');
    await page.evaluate(() => {
      document.querySelectorAll('[data-testid="sidebar"] details').forEach((d) => {
        (d as HTMLDetailsElement).open = true;
      });
    });
    await expect(
      page.locator('[data-section="claude"] [data-testid="tree-leaf"]'),
    ).not.toHaveCount(0);
    await expect(
      page.locator('[data-section="projects"] [data-testid="tree-leaf"]'),
    ).not.toHaveCount(0);
    await expect(page.locator('[data-testid="project-link"]').first()).toBeVisible();
    expect(errs).toEqual([]);
  });
});

test.describe("SYS-22 broken-link rendering", () => {
  test.beforeAll(async ({ request }) => {
    await request.put("/api/file", {
      headers: { Origin: "http://127.0.0.1:8765" },
      data: {
        path: "specs/development/spec_driven/__scratch__/sys22.md",
        content:
          "This is [a broken link](does-not-exist.md) and this is [a real one](../final_specs/spec.md).",
      },
    });
  });

  test("relative link to a non-existent file renders as muted span (NOT anchor)", async ({ page }) => {
    await page.goto("/file/specs/development/spec_driven/__scratch__/sys22.md");
    await page.waitForSelector('[data-testid="markdown-view"]');
    const broken = page.locator('[data-testid="markdown-view"] .link-broken').first();
    await expect(broken).toBeVisible();
    expect(await broken.evaluate((e) => e.tagName)).toBe("SPAN");
    expect(await broken.getAttribute("aria-disabled")).toBe("true");
  });
});

test.describe("SYS-24 pin survives in regen prompt", () => {
  test("interview/promoted.md is inlined under Pinned items", async ({ request }) => {
    const r = await request.post("/api/regen-prompt", {
      headers: { Origin: "http://127.0.0.1:8765" },
      data: {
        project_type: "development",
        project_name: "spec_driven",
        stages: ["interview"],
        modules: {},
        autonomous: false,
      },
    });
    expect(r.status()).toBe(200);
    const body = await r.json();
    expect(body.prompt).toContain("### Pinned items (MUST survive regeneration)");
    expect(body.prompt).toContain("All discovered (Recommended)");
  });
});

test.describe("SYS-25 autonomous header + verbatim imperative", () => {
  test("autonomous=true emits AUTONOMOUS header and imperative verbatim", async ({ request }) => {
    const r = await request.post("/api/regen-prompt", {
      headers: { Origin: "http://127.0.0.1:8765" },
      data: {
        project_type: "development",
        project_name: "spec_driven",
        stages: ["interview"],
        modules: {},
        autonomous: true,
      },
    });
    const body = await r.json();
    expect(body.prompt.split("\n", 1)[0]).toBe("# EXECUTION MODE: AUTONOMOUS");
    expect(body.prompt).toContain(
      "Do not call AskUserQuestion. For anything unclear, use your best judgment, record the choice inline in the artifact, and keep going. Produce every requested artifact below in this single turn before stopping.",
    );
  });
});
