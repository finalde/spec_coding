import { test, expect } from "@playwright/test";

/**
 * Dogfood golden-path e2e.
 *
 * Exists because frontend↔backend contract drift on the tree shape (run
 * spec_driven-20260502-clean: backend used `projects`/`stages`, frontend
 * walked `children`) shipped past green unit tests. A real browser pass is
 * the cheapest way to catch that class of bug.
 *
 * Pre-req: `make run-prod` is up on http://127.0.0.1:8765 with the
 * spec_driven project's full pipeline output on disk.
 */

test.describe("spec_driven dogfood", () => {
  test("landing page redirects to spec.md and renders the rendered file H1", async ({ page }) => {
    await page.goto("/");
    await expect(page).toHaveURL(/\/file\/specs\/development\/spec_driven\/final_specs\/spec\.md/);

    // The sidebar's title is also an H1; pick the H1 inside the reader pane
    // specifically. The reader is a <main> landmark.
    const readerHeading = page.locator("main").getByRole("heading", { level: 1 }).first();
    await expect(readerHeading).toContainText(/Spec.*spec_driven/i);
  });

  test("Projects > development > spec_driven > [5 stages] all render in the tree", async ({
    page,
  }) => {
    await page.goto("/");
    await page.waitForSelector('[role="tree"]');

    // The five stage folder rows must all be present as treeitems at level 4.
    const stages = ["user_input", "interview", "findings", "final_specs", "validation"];
    for (const stage of stages) {
      const row = page.getByRole("treeitem", { name: new RegExp(`^${stage}`) });
      await expect(row, `stage row '${stage}' must be present`).toBeVisible();
    }
  });

  test("clicking dossier.md via sidebar navigates the reader pane", async ({ page }) => {
    await page.goto("/");
    await page.waitForSelector('[role="tree"]');

    // findings is collapsed by default — click to expand.
    const findings = page.getByRole("treeitem", { name: /^findings/ });
    await findings.click();

    // After expand, the dossier.md leaf is a treeitem at level 5 (not an
    // anchor) — the Sidebar's leaves use onClick + push-history, not <a>.
    const dossierLeaf = page.getByRole("treeitem", { name: "dossier.md" });
    await expect(dossierLeaf).toBeVisible();
    await dossierLeaf.click();

    await expect(page).toHaveURL(/\/file\/specs\/development\/spec_driven\/findings\/dossier\.md/);
    const readerHeading = page.locator("main").getByRole("heading", { level: 1 }).first();
    await expect(readerHeading).toContainText(/Findings dossier/i);
  });

  test("Settings section shows agent_refs subgroup with both validation playbooks", async ({
    page,
  }) => {
    await page.goto("/");

    // The Settings section is always expanded; the agent_refs subgroup
    // appears as a fourth subgroup beneath CLAUDE.md / Agents / Skills.
    const refsHeader = page.getByRole("heading", { level: 3, name: "Agent refs" });
    await expect(refsHeader).toBeVisible();

    // Both validation_manager files are clickable as direct sidebar leaves.
    const dev = page.locator(
      'a[href="/file/.claude/agent_refs/agent_team__validation_manager/development.md"]',
    );
    const general = page.locator(
      'a[href="/file/.claude/agent_refs/agent_team__validation_manager/general.md"]',
    );
    await expect(dev).toBeVisible();
    await expect(general).toBeVisible();
  });

  test("agent_refs file opens in the reader and shows its H1", async ({ page }) => {
    await page.goto("/");
    const dev = page.locator(
      'a[href="/file/.claude/agent_refs/agent_team__validation_manager/development.md"]',
    );
    await dev.click();

    await expect(page).toHaveURL(
      /\/file\/\.claude\/agent_refs\/agent_team__validation_manager\/development\.md/,
    );
    const readerHeading = page.locator("main").getByRole("heading", { level: 1 }).first();
    await expect(readerHeading).toContainText(/Validation playbook/i);
  });

  test("opening qa.md renders the structured Q/A view (or markdown fallback) without blank page", async ({
    page,
  }) => {
    // Regression guard: deep-linking to qa.md previously produced a blank
    // page because (a) the answer regex didn't match the autonomous-mode
    // form `- A *(judgment call ...)*:` and (b) the QaViewSafe try/catch
    // didn't actually catch parse errors thrown during React rendering.
    const consoleErrors: string[] = [];
    page.on("pageerror", (err) => consoleErrors.push(String(err)));
    page.on("console", (msg) => {
      if (msg.type() === "error") consoleErrors.push(msg.text());
    });

    await page.goto("/file/specs/development/spec_driven/interview/qa.md");
    // Reader pane must contain SOMETHING — either the structured Q/A view
    // (`.qa-view`) or the markdown fallback (a heading from qa.md).
    const main = page.locator("main");
    await expect(main).toBeVisible();
    const qaView = main.locator(".qa-view");
    const fallbackHeading = main.getByRole("heading", { name: /Interview/i }).first();
    // Whichever path renders, the reader must show real content, not be empty.
    const eitherVisible = await Promise.race([
      qaView.waitFor({ state: "visible", timeout: 5000 }).then(() => "qaView"),
      fallbackHeading
        .waitFor({ state: "visible", timeout: 5000 })
        .then(() => "markdown"),
    ]).catch(() => null);
    expect(
      eitherVisible,
      "qa.md must render either the structured Q/A view or the markdown fallback — never a blank page",
    ).not.toBeNull();

    // No uncaught render errors during the load.
    expect(consoleErrors).toEqual([]);
  });

  test("pin a Q/A on qa.md and see it appear on the promoted.md page", async ({
    page,
    request,
  }) => {
    // Clean state: remove any pre-existing promoted.md so this test is hermetic.
    // We do this by deleting any pre-existing pins via the API.
    const stagePath = "specs/development/spec_driven/interview";
    const existing = await request.get(
      `/api/promotions?stage_path=${encodeURIComponent(stagePath)}`,
    );
    if (existing.ok()) {
      const body = (await existing.json()) as {
        pins: Array<{ pin_id: string }>;
      };
      for (const p of body.pins) {
        await request.delete("/api/promote", {
          data: { stage_path: stagePath, pin_id: p.pin_id },
        });
      }
    }

    // Open qa.md and pin the FIRST Q/A pair.
    await page.goto("/file/specs/development/spec_driven/interview/qa.md");
    const qaView = page.locator(".qa-view");
    await expect(qaView).toBeVisible();
    const firstPinToggle = page.locator(".pin-toggle").first();
    await expect(firstPinToggle).toBeVisible();
    // Click the toggle and wait for the on-state to take effect (the button
    // gains aria-pressed="true").
    await firstPinToggle.click();
    await expect(firstPinToggle).toHaveAttribute("aria-pressed", "true", {
      timeout: 5000,
    });

    // Navigate to the promoted.md page and confirm the pin appears.
    await page.goto("/file/specs/development/spec_driven/interview/promoted.md");
    const promotedView = page.locator(".promoted-view");
    await expect(promotedView).toBeVisible();
    const pinCard = page.locator(".promoted-pin-card").first();
    await expect(pinCard).toBeVisible();
    await expect(pinCard.locator(".promoted-pin-id")).toContainText(/^pin-\d+/);

    // Unpin from the promoted page and confirm it disappears.
    await pinCard.locator(".promoted-pin-unpin").click();
    await expect(page.locator(".promoted-pin-card")).toHaveCount(0, {
      timeout: 5000,
    });

    // Cleanup: ensure no stray pins linger for the next test run.
    const after = await request.get(
      `/api/promotions?stage_path=${encodeURIComponent(stagePath)}`,
    );
    expect(after.ok()).toBe(true);
  });

  test("Sidebar walks the live /api/tree shape without errors", async ({ page }) => {
    // Smoke test that catches the children/projects/stages contract drift class.
    // If the backend regresses to emitting non-children descent fields, the tree
    // would render as empty under Projects and this test fails.
    const consoleErrors: string[] = [];
    page.on("pageerror", (err) => consoleErrors.push(String(err)));
    page.on("console", (msg) => {
      if (msg.type() === "error") consoleErrors.push(msg.text());
    });

    await page.goto("/");
    await page.waitForSelector('[role="tree"]');

    // Projects section MUST contain at least one project row at level 3.
    const projectRow = page.getByRole("treeitem", { name: /^spec_driven/ });
    await expect(projectRow).toBeVisible();

    // No console errors during initial render.
    expect(consoleErrors).toEqual([]);
  });
});
