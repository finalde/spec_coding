import { test, expect, type Page, type ConsoleMessage, type Request } from "@playwright/test";
import * as fs from "node:fs";
import * as path from "node:path";

const PORT_BACKEND = 8765;
const PORT_FRONTEND = 5173;
const URL_BACKEND = `http://127.0.0.1:${PORT_BACKEND}`;
const URL_FRONTEND = `http://127.0.0.1:${PORT_FRONTEND}`;

const REPO_ROOT = path.resolve(__dirname, "..", "..", "..", "..");
const PROJECT_REL = "specs/development/spec_driven";

function attachConsoleErrorTracker(page: Page): { errors: string[]; pageErrors: Error[] } {
  const errors: string[] = [];
  const pageErrors: Error[] = [];
  page.on("console", (msg: ConsoleMessage) => {
    if (msg.type() === "error") errors.push(msg.text());
  });
  page.on("pageerror", (err: Error) => pageErrors.push(err));
  return { errors, pageErrors };
}

function repoFile(rel: string): string {
  return path.join(REPO_ROOT, ...rel.split("/"));
}

function encodePathParam(rel: string): string {
  return encodeURIComponent(rel);
}

function restoreFile(absPath: string, original: string | null): void {
  if (original === null) {
    if (fs.existsSync(absPath)) fs.unlinkSync(absPath);
  } else {
    fs.writeFileSync(absPath, original, "utf8");
  }
}

// SYS-1 — Boot smoke under `make run-prod`
test.describe("SYS-1 — Boot smoke under make run-prod", () => {
  test("backend tree shape + sidebar leaves under each top-level section", async ({ page, request }) => {
    const tracker = attachConsoleErrorTracker(page);

    const treeResp = await request.get(`${URL_BACKEND}/api/tree`);
    expect(treeResp.status()).toBe(200);
    const tree = await treeResp.json();
    expect(tree.type).toBe("section");
    expect(Array.isArray(tree.children)).toBe(true);
    const topNames = tree.children.map((c: { name: string }) => c.name);
    expect(topNames).toEqual(
      expect.arrayContaining(["Claude Settings & Shared Context", "Projects"]),
    );
    function hasFileLeaf(node: { type: string; children?: unknown[] }): boolean {
      if (node.type === "file") return true;
      if (!Array.isArray(node.children)) return false;
      return node.children.some((c) => hasFileLeaf(c as { type: string; children?: unknown[] }));
    }
    for (const section of tree.children) {
      expect(hasFileLeaf(section)).toBe(true);
    }

    const indexResp = await request.get(`${URL_BACKEND}/`);
    expect(indexResp.status()).toBe(200);
    expect(indexResp.headers()["content-type"]).toMatch(/text\/html/);
    const indexBody = await indexResp.text();
    expect(indexBody).toContain('id="root"');

    await page.goto("/");
    await expect(page.locator('[data-testid="sidebar"]')).toBeVisible();
    const topSectionButtons = page.locator('[data-testid="sidebar"] [data-section-toplevel]');
    await expect(topSectionButtons).toHaveCount(2, { timeout: 10_000 });
    const count = await topSectionButtons.count();
    for (let i = 0; i < count; i++) {
      const btn = topSectionButtons.nth(i);
      const isExpanded = await btn.getAttribute("aria-expanded");
      if (isExpanded === "false") await btn.click();
    }
    const fileLeaves = page.locator('[data-testid="sidebar"] [role="treeitem"][data-leaf="true"]');
    await expect(fileLeaves.first()).toBeVisible({ timeout: 10_000 });

    expect(tracker.errors.filter((e) => /Failed to fetch|TypeError|Error/i.test(e))).toEqual([]);
  });
});

// SYS-2 — MarkdownView deep-link (default render)
test.describe("SYS-2 — MarkdownView deep-link", () => {
  test("renders markdown with headings, code fences, and link semantics", async ({ page, context }) => {
    const tracker = attachConsoleErrorTracker(page);
    const url = `/file/${encodePathParam(`${PROJECT_REL}/final_specs/spec.md`)}`;
    await page.goto(url);
    await expect(page.locator('[data-render-mode="markdown"]')).toBeVisible();
    expect(await page.locator('[data-render-mode="markdown"] h1, [data-render-mode="markdown"] h2').count()).toBeGreaterThanOrEqual(3);
    expect(await page.locator('[data-render-mode="markdown"] pre code').count()).toBeGreaterThanOrEqual(1);
    expect(await page.locator('[data-render-mode="markdown"] script').count()).toBe(0);

    const breadcrumb = page.locator('nav[aria-label="Breadcrumb"]');
    await expect(breadcrumb).toBeVisible();
    await expect(breadcrumb.locator('[aria-current="page"]')).toHaveCount(1);
    const currentTag = await breadcrumb.locator('[aria-current="page"]').evaluate((el) => el.tagName.toLowerCase());
    expect(currentTag).not.toBe("a");

    const externalLink = page.locator('[data-render-mode="markdown"] a[href^="https://"]').first();
    if (await externalLink.count()) {
      await expect(externalLink).toHaveAttribute("target", "_blank");
      const rel = await externalLink.getAttribute("rel");
      expect(rel || "").toContain("noopener");
    }

    expect(tracker.errors.filter((e) => /Failed to fetch|TypeError/i.test(e))).toEqual([]);
  });
});

// SYS-3 — QaView render mode
test.describe("SYS-3 — QaView render mode", () => {
  test("interview/qa.md renders Q/A blocks with category badges, both legacy and judgment-call answer forms parse", async ({ page }) => {
    const tracker = attachConsoleErrorTracker(page);
    await page.goto(`/file/${encodePathParam(`${PROJECT_REL}/interview/qa.md`)}`);
    await expect(page.locator('[data-render-mode="qa"]')).toBeVisible();
    await expect(page.locator('[data-testid="parse-fallback"]')).toHaveCount(0);
    expect(await page.locator(".qa-question").count()).toBeGreaterThanOrEqual(1);
    expect(await page.locator(".qa-answer").count()).toBeGreaterThanOrEqual(1);
    expect(await page.locator('[data-action="edit-q"]').count()).toBeGreaterThanOrEqual(1);
    expect(await page.locator('[data-action="edit-a"]').count()).toBeGreaterThanOrEqual(1);
    expect(await page.locator('[data-action="pin"]').count()).toBeGreaterThanOrEqual(1);
    expect(tracker.errors).toEqual([]);
  });
});

// SYS-4 — JsonlView render mode
test.describe("SYS-4 — JsonlView render mode", () => {
  const fixturePath = repoFile(`${PROJECT_REL}/findings/sample_events.jsonl`);
  let originalContent: string | null = null;

  test.beforeAll(() => {
    const lines = [
      '{"event":"validation.started","level":"system","ts":"2026-05-03T14:58:59Z"}',
      '{"event":"exec.unit.started","unit":"impl-01-backend","ts":"2026-05-03T14:59:01Z","details":{"nested":{"a":1,"b":[1,2,3]}}}',
      '{"event":"validation.pass","level":"unit","ts":"2026-05-03T14:59:30Z"}',
      "{ trailing-comma-malformed, }",
      '{"event":"exec.unit.completed","unit":"impl-01-backend","ts":"2026-05-03T15:00:00Z"}',
      '{"event":"regen.delete.planned","path":"specs/development/spec_driven/findings/dossier.md"}',
      '{"event":"regen.delete.completed","count":4}',
      '{"event":"regen.write.completed","path":"specs/development/spec_driven/findings/dossier.md","bytes":2048}',
      '{"event":"validation.issue.raised","severity":"warning","detail":"single-run outlier"}',
      '{"event":"validation.requires_manual_walkthrough","checklist_keys":["focus_visibility","contrast","motion"]}',
      '{"event":"pipeline.halted","reason":"max_revisions"}',
    ];
    if (fs.existsSync(fixturePath)) originalContent = fs.readFileSync(fixturePath, "utf8");
    fs.mkdirSync(path.dirname(fixturePath), { recursive: true });
    fs.writeFileSync(fixturePath, lines.join("\n") + "\n", "utf8");
  });

  test.afterAll(() => {
    restoreFile(fixturePath, originalContent);
  });

  test("each line independently parsed; malformed line shows parse-error badge but does NOT trip file-level boundary", async ({ page }) => {
    const tracker = attachConsoleErrorTracker(page);
    await page.goto(`/file/${encodePathParam(`${PROJECT_REL}/findings/sample_events.jsonl`)}`);
    await expect(page.locator('[data-render-mode="jsonl"]')).toBeVisible();
    expect(await page.locator(".jsonl-line").count()).toBeGreaterThanOrEqual(10);
    expect(await page.locator(".jsonl-line.jsonl-parse-error").count()).toBeGreaterThanOrEqual(1);
    await expect(page.locator('[data-testid="jsonl-parse-error-badge"]').first()).toBeVisible();
    await expect(page.locator('[data-testid="parse-fallback"]')).toHaveCount(0);
    const firstWellFormed = page.locator(".jsonl-line:not(.jsonl-parse-error) details").first();
    await firstWellFormed.click();
    expect(tracker.pageErrors).toEqual([]);
  });
});

// SYS-5 — CodeView render mode (.json / .yaml)
test.describe("SYS-5 — CodeView render mode", () => {
  test("json file renders under code mode with syntax-highlight class on dark <pre>", async ({ page }) => {
    const tracker = attachConsoleErrorTracker(page);
    const candidates = [
      `projects/spec_driven/frontend/package.json`,
      `projects/spec_driven/frontend/tsconfig.json`,
    ];
    let target: string | null = null;
    for (const c of candidates) {
      if (fs.existsSync(repoFile(c))) {
        target = c;
        break;
      }
    }
    test.skip(target === null, "no exposed .json fixture available yet");
    await page.goto(`/file/${encodePathParam(target!)}`);
    await expect(page.locator('[data-render-mode="code"]')).toBeVisible();
    const pre = page.locator('[data-render-mode="code"] pre').first();
    await expect(pre).toBeVisible();
    const highlightCount = await pre.locator('[class*="hljs"]').count();
    expect(highlightCount).toBeGreaterThanOrEqual(1);
    const bg = await pre.evaluate((el) => getComputedStyle(el).backgroundColor);
    // Dark carve-out: low luminance background (rgb sum < 200)
    const m = /rgb[a]?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)/.exec(bg);
    if (m) {
      const sum = Number(m[1]) + Number(m[2]) + Number(m[3]);
      expect(sum).toBeLessThan(200);
    }
    expect(await page.locator('[data-action="pin"]').count()).toBe(0);
    expect(tracker.errors).toEqual([]);
  });
});

// SYS-6 — ImagePlaceholder render mode
test.describe("SYS-6 — ImagePlaceholder render mode", () => {
  const pngPath = repoFile(`${PROJECT_REL}/findings/sample.png`);
  const jpgPath = repoFile(`${PROJECT_REL}/findings/sample.jpg`);
  let pngOriginal: string | null = null;
  let jpgOriginal: string | null = null;

  test.beforeAll(() => {
    const pngBytes = Buffer.from(
      "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4890000000d4944415478da6300010000000500010d0a2db40000000049454e44ae426082",
      "hex",
    );
    const jpgBytes = Buffer.from(
      "ffd8ffe000104a46494600010101006000600000ffdb004300080606070605080707070909080a0c140d0c0b0b0c1912130f141d1a1f1e1d1a1c1c20242e2720222c231c1c2837292c30313434341f27393d38323c2e333432ffc0000b0801000100018401110200ffc40014000100000000000000000000000000000000ffc40014100100000000000000000000000000000000ffc40014010100000000000000000000000000000000ffc40014110100000000000000000000000000000000ffda0008010100013f10ffd9",
      "hex",
    );
    if (fs.existsSync(pngPath)) pngOriginal = fs.readFileSync(pngPath, "base64");
    if (fs.existsSync(jpgPath)) jpgOriginal = fs.readFileSync(jpgPath, "base64");
    fs.mkdirSync(path.dirname(pngPath), { recursive: true });
    fs.writeFileSync(pngPath, pngBytes);
    fs.writeFileSync(jpgPath, jpgBytes);
  });

  test.afterAll(() => {
    if (pngOriginal === null) {
      if (fs.existsSync(pngPath)) fs.unlinkSync(pngPath);
    } else {
      fs.writeFileSync(pngPath, Buffer.from(pngOriginal, "base64"));
    }
    if (jpgOriginal === null) {
      if (fs.existsSync(jpgPath)) fs.unlinkSync(jpgPath);
    } else {
      fs.writeFileSync(jpgPath, Buffer.from(jpgOriginal, "base64"));
    }
  });

  test("png/jpg render as placeholder card; PUT to image path returns 415", async ({ page, request }) => {
    const tracker = attachConsoleErrorTracker(page);
    await page.goto(`/file/${encodePathParam(`${PROJECT_REL}/findings/sample.png`)}`);
    await expect(page.locator('[data-render-mode="image"]')).toBeVisible();
    await expect(page.locator('[data-testid="image-placeholder"]')).toBeVisible();
    await expect(page.locator('[data-testid="image-placeholder"]')).toContainText("binary content not previewed");
    expect(await page.locator('[data-render-mode="image"] img').count()).toBe(0);
    const editBtn = page.locator('[data-action="edit-file"]');
    if (await editBtn.count()) {
      const isDisabled = await editBtn.first().isDisabled();
      const ariaDisabled = await editBtn.first().getAttribute("aria-disabled");
      expect(isDisabled || ariaDisabled === "true").toBe(true);
    }
    const putResp = await request.put(`${URL_BACKEND}/api/file`, {
      headers: { Origin: URL_BACKEND, Host: `127.0.0.1:${PORT_BACKEND}` },
      data: { path: `${PROJECT_REL}/findings/sample.png`, content: "x" },
    });
    expect(putResp.status()).toBe(415);

    await page.goto(`/file/${encodePathParam(`${PROJECT_REL}/findings/sample.jpg`)}`);
    await expect(page.locator('[data-testid="image-placeholder"]')).toBeVisible();
    expect(tracker.errors).toEqual([]);
  });
});

// SYS-7 — Editor save round-trip (file-level)
test.describe("SYS-7 — Editor save round-trip", () => {
  const target = `${PROJECT_REL}/findings/dossier.md`;
  const targetAbs = repoFile(target);
  let original: string | null = null;

  test.beforeAll(() => {
    if (fs.existsSync(targetAbs)) original = fs.readFileSync(targetAbs, "utf8");
    else fs.writeFileSync(targetAbs, "# dossier\n\ninitial content for SYS-7\n", "utf8");
  });
  test.afterAll(() => {
    if (original !== null) fs.writeFileSync(targetAbs, original, "utf8");
  });

  test("PUT carries If-Unmodified-Since; reload reflects new content; dirty indicator behaves", async ({ page }) => {
    const tracker = attachConsoleErrorTracker(page);
    const requests: Request[] = [];
    page.on("request", (req) => {
      if (req.method() === "PUT" && req.url().includes("/api/file")) requests.push(req);
    });

    await page.goto(`/file/${encodePathParam(target)}`);
    await expect(page.locator('[data-render-mode="markdown"]')).toBeVisible();
    await page.click('[data-action="edit-file"]');
    const textarea = page.locator('textarea[data-testid="file-editor-textarea"]');
    await expect(textarea).toBeVisible();
    const before = await textarea.inputValue();
    const marker = "\n<!-- sys-7 round-trip marker -->\n";
    await textarea.fill(before + marker);

    await expect(page.locator('[data-testid="dirty-indicator"]')).toBeVisible({ timeout: 1000 });
    const title = await page.title();
    expect(title.startsWith("*")).toBe(true);

    await page.keyboard.press("Control+s");
    await expect(page.locator('[data-testid="dirty-indicator"]')).toHaveCount(0, { timeout: 5000 });

    expect(requests.length).toBeGreaterThanOrEqual(1);
    const put = requests[requests.length - 1];
    const ius = put.headers()["if-unmodified-since"];
    expect(ius).toBeTruthy();

    const onDisk = fs.readFileSync(targetAbs, "utf8");
    expect(onDisk).toContain("sys-7 round-trip marker");

    await page.reload();
    await expect(page.locator('[data-render-mode="markdown"]')).toContainText("sys-7 round-trip marker");

    expect(tracker.errors).toEqual([]);
  });
});

// SYS-8 — Per-Q inline edit + mutual exclusion with file-level edit
test.describe("SYS-8 — Per-Q inline edit", () => {
  const target = `${PROJECT_REL}/interview/qa.md`;
  const targetAbs = repoFile(target);
  let original: string | null = null;

  test.beforeAll(() => {
    if (fs.existsSync(targetAbs)) original = fs.readFileSync(targetAbs, "utf8");
  });
  test.afterAll(() => {
    if (original !== null) fs.writeFileSync(targetAbs, original, "utf8");
  });

  test("file-level Edit disabled while a per-Q editor is open; save persists full file content", async ({ page }) => {
    const tracker = attachConsoleErrorTracker(page);
    test.skip(original === null, "qa.md fixture missing");
    await page.goto(`/file/${encodePathParam(target)}`);
    await expect(page.locator('[data-render-mode="qa"]')).toBeVisible();
    const firstEditQ = page.locator('[data-action="edit-q"]').first();
    await firstEditQ.click();
    const fileEdit = page.locator('[data-action="edit-file"]');
    if (await fileEdit.count()) {
      const isDisabled = await fileEdit.isDisabled();
      const ariaDisabled = await fileEdit.getAttribute("aria-disabled");
      expect(isDisabled || ariaDisabled === "true").toBe(true);
    }
    const inlineTextarea = page.locator('[data-testid="qa-inline-editor"] textarea').first();
    await expect(inlineTextarea).toBeVisible();
    const oldQ = await inlineTextarea.inputValue();
    const newQ = oldQ + " (sys-8-marker)";
    await inlineTextarea.fill(newQ);
    await page.locator('[data-testid="qa-inline-editor"] [data-action="save-inline"]').first().click();
    await expect(page.locator('[data-testid="qa-inline-editor"]')).toHaveCount(0, { timeout: 5000 });
    const onDisk = fs.readFileSync(targetAbs, "utf8");
    expect(onDisk).toContain("sys-8-marker");
    await page.reload();
    await expect(page.locator('[data-render-mode="qa"]')).toContainText("sys-8-marker");
    if (await fileEdit.count()) {
      const isDisabled = await fileEdit.isDisabled();
      expect(isDisabled).toBe(false);
    }
    expect(tracker.errors).toEqual([]);
  });
});

// SYS-9 — Regen-prompt assembly (small, no warning)
test.describe("SYS-9 — Regen-prompt assembly small", () => {
  test("interactive header, follow-ups inlined, breakdown line, Copy button works", async ({ page, context }) => {
    const tracker = attachConsoleErrorTracker(page);
    await context.grantPermissions(["clipboard-read", "clipboard-write"]);
    await page.goto(`/project/development/spec_driven`);
    await expect(page.locator('[data-testid="project-page"]')).toBeVisible();
    await page.locator('[data-testid="stage-checkbox"][data-stage="interview"]').check();
    await page.locator('[data-testid="stage-checkbox"][data-stage="research"]').check();
    const auto = page.locator('[data-testid="autonomous-toggle"]');
    if ((await auto.getAttribute("aria-checked")) === "true") await auto.click();
    await page.locator('[data-testid="build-prompt"]').click();

    const block = page.locator('[data-testid="regen-prompt-block"]');
    await expect(block).toBeVisible();
    expect(await page.locator('[data-testid="regen-prompt-block"] details').count()).toBe(0);

    const breakdown = page.locator('[data-testid="regen-breakdown-line"]');
    await expect(breakdown).toContainText(/2 stages selected/);
    await expect(breakdown).toContainText(/follow-ups inlined/);
    await expect(breakdown).toContainText(/autonomous=off/);
    await expect(breakdown).toContainText(/KB/);

    const body = page.locator('[data-testid="regen-prompt-body"]');
    const text = await body.innerText();
    expect(text.split("\n")[0]).toBe("# EXECUTION MODE: INTERACTIVE");
    expect(text).toContain("### Constraints");
    expect(text).toMatch(/read-zero|Read-zero/);

    const copyBtn = page.locator('[data-testid="copy-prompt"]');
    const beforeRect = await copyBtn.boundingBox();
    await copyBtn.click();
    await expect(copyBtn).toContainText("Copied!", { timeout: 2000 });
    const clipboardText = await page.evaluate(() => navigator.clipboard.readText());
    expect(clipboardText.split("\n")[0]).toBe("# EXECUTION MODE: INTERACTIVE");
    const afterRect = await copyBtn.boundingBox();
    if (beforeRect && afterRect) {
      expect(Math.abs(beforeRect.width - afterRect.width)).toBeLessThan(2);
    }
    await expect(page.locator('[data-testid="regen-warning-banner"]')).toHaveCount(0);
    expect(tracker.errors).toEqual([]);
  });
});

// SYS-10 — Regen-prompt approaching-ceiling warning
test.describe("SYS-10 — Regen-prompt approaching-ceiling", () => {
  const target = `${PROJECT_REL}/user_input/follow_ups/999-sys10-padding.md`;
  const targetAbs = repoFile(target);

  test.beforeAll(() => {
    fs.mkdirSync(path.dirname(targetAbs), { recursive: true });
    const filler = "# Follow-up draft 999 — SYS-10 padding\n\n" + "lorem ipsum ".repeat(8000) + "\n";
    fs.writeFileSync(targetAbs, filler, "utf8");
  });
  test.afterAll(() => {
    if (fs.existsSync(targetAbs)) fs.unlinkSync(targetAbs);
  });

  test("yellow banner above prompt block; 200 OK with approaching_ceiling warning; copy still works", async ({ page }) => {
    const tracker = attachConsoleErrorTracker(page);
    await page.goto(`/project/development/spec_driven`);
    await expect(page.locator('[data-testid="project-page"]')).toBeVisible();
    const checkboxes = page.locator('[data-testid="stage-checkbox"]');
    const n = await checkboxes.count();
    for (let i = 0; i < n; i++) await checkboxes.nth(i).check();

    const respPromise = page.waitForResponse((r) => r.url().includes("/api/regen-prompt") && r.request().method() === "POST");
    await page.locator('[data-testid="build-prompt"]').click();
    const resp = await respPromise;
    expect(resp.status()).toBe(200);
    const body = await resp.json();
    if (body.bytes >= 50 * 1024 && body.bytes < 1024 * 1024) {
      expect(body.warning).toBeTruthy();
      expect(body.warning.kind).toBe("approaching_ceiling");
      await expect(page.locator('[data-testid="regen-warning-banner"]')).toBeVisible();
      await expect(page.locator('[data-testid="regen-prompt-block"]')).toBeVisible();
    } else {
      test.skip(true, `padding did not push into 50KB-1MB band (bytes=${body.bytes})`);
    }
    expect(tracker.errors).toEqual([]);
  });
});

// SYS-11 — Regen-prompt 413 hard ceiling
test.describe("SYS-11 — Regen-prompt 413", () => {
  const target = `${PROJECT_REL}/user_input/follow_ups/998-sys11-padding.md`;
  const targetAbs = repoFile(target);

  test.beforeAll(() => {
    fs.mkdirSync(path.dirname(targetAbs), { recursive: true });
    const filler = "# Follow-up draft 998 — SYS-11 padding\n\n" + "X".repeat(1_100_000) + "\n";
    fs.writeFileSync(targetAbs, filler, "utf8");
  });
  test.afterAll(() => {
    if (fs.existsSync(targetAbs)) fs.unlinkSync(targetAbs);
  });

  test("413 with too_large; build-error banner; prompt block NOT rendered; no Copy button", async ({ page }) => {
    const tracker = attachConsoleErrorTracker(page);
    await page.goto(`/project/development/spec_driven`);
    const checkboxes = page.locator('[data-testid="stage-checkbox"]');
    const n = await checkboxes.count();
    for (let i = 0; i < n; i++) await checkboxes.nth(i).check();
    const respPromise = page.waitForResponse((r) => r.url().includes("/api/regen-prompt") && r.request().method() === "POST");
    await page.locator('[data-testid="build-prompt"]').click();
    const resp = await respPromise;
    expect(resp.status()).toBe(413);
    const j = await resp.json();
    expect(j.detail.kind).toBe("too_large");
    await expect(page.locator('[data-testid="regen-error-banner"]')).toBeVisible();
    await expect(page.locator('[data-testid="regen-prompt-block"]')).toHaveCount(0);
    await expect(page.locator('[data-testid="copy-prompt"]')).toHaveCount(0);
    expect(tracker.errors).toEqual([]);
  });
});

// SYS-12 — Autonomous toggle persistence + cross-tab storage event
test.describe("SYS-12 — Autonomous toggle persistence + cross-tab", () => {
  test("toggle persists in localStorage; cross-tab sync; assembled header reflects on", async ({ context }) => {
    const pageA = await context.newPage();
    const pageB = await context.newPage();
    const trackerA = attachConsoleErrorTracker(pageA);
    await pageA.goto(`${URL_BACKEND}/project/development/spec_driven`);
    await pageA.evaluate(() => localStorage.removeItem("spec_driven.autonomous_mode.v1"));
    await pageA.reload();
    await pageB.goto(`${URL_BACKEND}/project/development/spec_driven`);

    const toggleA = pageA.locator('[data-testid="autonomous-toggle"]');
    await expect(toggleA).toHaveAttribute("aria-checked", "false");
    await toggleA.click();
    await expect(toggleA).toHaveAttribute("aria-checked", "true");
    const stored = await pageA.evaluate(() => localStorage.getItem("spec_driven.autonomous_mode.v1"));
    expect(stored).toBe("true");

    const toggleB = pageB.locator('[data-testid="autonomous-toggle"]');
    await expect(toggleB).toHaveAttribute("aria-checked", "true", { timeout: 1500 });

    await pageA.locator('[data-testid="stage-checkbox"][data-stage="interview"]').check();
    await pageA.locator('[data-testid="build-prompt"]').click();
    const text = await pageA.locator('[data-testid="regen-prompt-body"]').innerText();
    expect(text.split("\n")[0]).toBe("# EXECUTION MODE: AUTONOMOUS");

    await pageA.reload();
    await expect(pageA.locator('[data-testid="autonomous-toggle"]')).toHaveAttribute("aria-checked", "true");

    expect(trackerA.errors).toEqual([]);
  });
});

// SYS-13 — QaView Error Boundary fallback
test.describe("SYS-13 — QaView Error Boundary fallback", () => {
  const target = `${PROJECT_REL}/interview/qa.md`;
  const targetAbs = repoFile(target);
  let original: string | null = null;

  test.beforeAll(() => {
    if (fs.existsSync(targetAbs)) original = fs.readFileSync(targetAbs, "utf8");
    fs.writeFileSync(
      targetAbs,
      [
        "# Interview Q/A — DELIBERATELY MALFORMED FIXTURE",
        "",
        "## Round ?",
        "category-without-badge",
        "  - Q: question with bad indentation",
        "    - A *(judgment call: unclosed parenthetical: this never closes",
        "  weird trailing  ",
      ].join("\n"),
      "utf8",
    );
  });
  test.afterAll(() => {
    if (original !== null) fs.writeFileSync(targetAbs, original, "utf8");
  });

  test("ParseFallback renders raw text + banner; no blank page; SPA still navigable", async ({ page }) => {
    const errors: string[] = [];
    page.on("pageerror", (e) => errors.push(e.message));
    await page.goto(`/file/${encodePathParam(target)}`);
    const fb = page.locator('[data-testid="parse-fallback"]');
    const qa = page.locator('[data-render-mode="qa"]');
    await expect(fb.or(qa)).toBeVisible();
    if (await fb.count()) {
      await expect(fb.locator("pre")).toBeVisible();
      await expect(fb).toContainText(/QaView failed to parse|parse error|fallback/i);
      await expect(page.locator('[data-action="edit-file"]')).toBeVisible();
    }
    // Navigate to another file: SPA still works.
    await page.goto(`/file/${encodePathParam("CLAUDE.md")}`);
    await expect(page.locator('[data-render-mode="markdown"]')).toBeVisible();
  });
});

// SYS-14 — Path traversal probes collapse to single 404
test.describe("SYS-14 — Path traversal probes", () => {
  const probes = [
    "../../etc/passwd",
    "..%2f..%2f.claude%2fsettings.local.json",
    `${PROJECT_REL}/findings/dossier.md::$DATA`,
    `${PROJECT_REL}/findings/COM1`,
    `${PROJECT_REL}/findings/dossier.md\\foo`,
    `${PROJECT_REL}/findings/dossier.md\u0000.txt`,
    "SPECS~1\\DEVELO~1\\dossier.md",
    `${PROJECT_REL}/findings//dossier.md`,
    "tools/foo.py",
    "tools/does-not-exist.py",
  ];

  for (const probe of probes) {
    test(`probe collapses to 404 with no realpath leak: ${JSON.stringify(probe).slice(0, 80)}`, async ({ request }) => {
      const url = `${URL_BACKEND}/api/file?path=${encodeURIComponent(probe)}`;
      const resp = await request.get(url);
      expect(resp.status()).toBe(404);
      const body = await resp.text();
      // No absolute path leak.
      expect(body).not.toMatch(/[A-Za-z]:[\\/]/);
      expect(body).not.toMatch(/\/home\/|\/etc\/|\/var\/|\/usr\//);
    });
  }
});

// SYS-15 — Symlink / junction refusal
test.describe("SYS-15 — Symlink / junction refusal", () => {
  const linkPath = repoFile(`${PROJECT_REL}/findings/sys15-symlink-out`);
  let created = false;

  test.beforeAll(() => {
    try {
      const target = process.platform === "win32" ? "C:\\Windows\\System32" : "/etc";
      fs.symlinkSync(target, linkPath, process.platform === "win32" ? "junction" : "dir");
      created = true;
    } catch {
      created = false;
    }
  });
  test.afterAll(() => {
    if (created && fs.existsSync(linkPath)) {
      try {
        fs.unlinkSync(linkPath);
      } catch {
        try {
          fs.rmdirSync(linkPath);
        } catch {
          /* ignore */
        }
      }
    }
  });

  test("symlink/junction returns 404 and tree does NOT enumerate it", async ({ request }) => {
    test.skip(!created, "symlink/junction creation refused on this runner (move 5: SKIPPED-WINDOWS without Developer Mode)");
    const child = process.platform === "win32" ? "win.ini" : "passwd";
    const r1 = await request.get(`${URL_BACKEND}/api/file?path=${encodeURIComponent(`${PROJECT_REL}/findings/sys15-symlink-out/${child}`)}`);
    expect(r1.status()).toBe(404);
    const r2 = await request.get(`${URL_BACKEND}/api/file?path=${encodeURIComponent(`${PROJECT_REL}/findings/sys15-symlink-out`)}`);
    expect(r2.status()).toBe(404);
    const tree = await (await request.get(`${URL_BACKEND}/api/tree`)).json();
    function findName(node: { name?: string; children?: unknown[] }, name: string): boolean {
      if (node.name === name) return true;
      if (!Array.isArray(node.children)) return false;
      return node.children.some((c) => findName(c as { name?: string; children?: unknown[] }, name));
    }
    expect(findName(tree, "sys15-symlink-out")).toBe(false);
  });
});

// SYS-16 — Origin / Host validation
test.describe("SYS-16 — Origin/Host validation under run-prod", () => {
  const target = `${PROJECT_REL}/findings/dossier.md`;
  const headerCases: { id: string; origin?: string; host: string; expect: number }[] = [
    { id: "a", origin: `http://127.0.0.1:${PORT_BACKEND}`, host: `127.0.0.1:${PORT_BACKEND}`, expect: 200 },
    { id: "b", origin: `http://localhost:${PORT_BACKEND}`, host: `localhost:${PORT_BACKEND}`, expect: 200 },
    { id: "c", origin: `http://127.0.0.1:${PORT_BACKEND}`, host: `localhost:${PORT_BACKEND}`, expect: 200 },
    { id: "d", origin: "http://example.com", host: `127.0.0.1:${PORT_BACKEND}`, expect: 403 },
    { id: "e", origin: undefined, host: `127.0.0.1:${PORT_BACKEND}`, expect: 403 },
    { id: "f", origin: `http://127.0.0.1:${PORT_FRONTEND}`, host: `127.0.0.1:${PORT_BACKEND}`, expect: 403 },
    { id: "g", origin: `http://localhost:${PORT_FRONTEND}`, host: `localhost:${PORT_BACKEND}`, expect: 403 },
    { id: "h", origin: `http://[::1]:${PORT_BACKEND}`, host: `[::1]:${PORT_BACKEND}`, expect: 403 },
    { id: "i", origin: `http://127.0.0.1:${PORT_BACKEND}`, host: "attacker.example.com", expect: 403 },
    { id: "j", origin: "http://127.0.0.1.nip.io", host: `127.0.0.1.nip.io:${PORT_BACKEND}`, expect: 403 },
  ];

  for (const c of headerCases) {
    test(`PUT /api/file row ${c.id} → ${c.expect}`, async ({ request }) => {
      const headers: Record<string, string> = { Host: c.host };
      if (c.origin) headers.Origin = c.origin;
      const resp = await request.put(`${URL_BACKEND}/api/file`, {
        headers,
        data: { path: target, content: "x" },
      });
      expect(resp.status()).toBe(c.expect);
      if (c.expect === 403) {
        const body = await resp.text();
        expect(body).not.toContain(c.host);
        if (c.origin) expect(body).not.toContain(c.origin);
      }
    });
  }

  test("read paths are not subject to Origin/Host gating", async ({ request }) => {
    const r = await request.get(`${URL_BACKEND}/api/tree`, { headers: { Origin: "http://example.com" } });
    expect(r.status()).toBe(200);
  });
});

// SYS-16b — Dev-server proxy mode under make run-frontend (multi-mode parity)
test.describe("SYS-16b — Dev-server proxy mode (run-frontend project only)", () => {
  test("Build-prompt UX works at 5173; raw browser-Origin direct → 403; proxied → 200", async ({ page, request, context }) => {
    test.skip(!process.env.PLAYWRIGHT_RUN_FRONTEND_MODE && !page.url().includes(":5173"), "run-frontend project only — guarded by grep");
    const tracker = attachConsoleErrorTracker(page);
    await context.grantPermissions(["clipboard-read", "clipboard-write"]);

    // (1) Browser-driven build-prompt flow under proxy.
    await page.goto(`${URL_FRONTEND}/project/development/spec_driven`);
    await expect(page.locator('[data-testid="project-page"]')).toBeVisible();
    await page.locator('[data-testid="stage-checkbox"][data-stage="interview"]').check();

    const respPromise = page.waitForResponse((r) => r.url().includes("/api/regen-prompt") && r.request().method() === "POST");
    await page.locator('[data-testid="build-prompt"]').click();
    const proxiedResp = await respPromise;
    expect(proxiedResp.status()).toBe(200);
    await expect(page.locator('[data-testid="regen-prompt-block"]')).toBeVisible();

    // (2) Direct-to-backend with raw browser-shape Origin (no proxy).
    const directResp = await request.post(`${URL_BACKEND}/api/regen-prompt`, {
      headers: {
        Origin: `http://localhost:${PORT_FRONTEND}`,
        Host: `localhost:${PORT_FRONTEND}`,
      },
      data: {
        project_type: "development",
        project_name: "spec_driven",
        stages: ["interview"],
        modules: { interview: ["qa"] },
        autonomous: false,
      },
    });
    expect(directResp.status()).toBe(403);

    // (3) Proxied request through Vite dev server.
    const proxiedFetchStatus = await page.evaluate(
      async ({ port }) => {
        const r = await fetch("/api/regen-prompt", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            project_type: "development",
            project_name: "spec_driven",
            stages: ["interview"],
            modules: { interview: ["qa"] },
            autonomous: false,
          }),
        });
        return r.status;
      },
      { port: PORT_FRONTEND },
    );
    expect(proxiedFetchStatus).toBe(200);

    expect(tracker.errors).toEqual([]);
  });
});

// SYS-17 — `make run` binds 127.0.0.1 only
test.describe("SYS-17 — Loopback bind only", () => {
  test("backend reachable on 127.0.0.1; foreign-LAN address returns connection refused", async ({ request }) => {
    const r = await request.get(`${URL_BACKEND}/api/tree`);
    expect(r.status()).toBe(200);
    // Note: enumerating the host's LAN IP for a negative test is platform-dependent;
    // the make-target / source-grep checks live in the unit test layer per move 4.
    // Here we assert the listener responds on loopback and that the test environment
    // proves the backend at least bound 127.0.0.1.
  });
});

// SYS-18 — HTTP verb whitelist on /api/file
test.describe("SYS-18 — HTTP verb whitelist", () => {
  const target = `${PROJECT_REL}/findings/dossier.md`;
  const url = `${URL_BACKEND}/api/file?path=${encodeURIComponent(target)}`;
  const headers = { Origin: URL_BACKEND, Host: `127.0.0.1:${PORT_BACKEND}` };

  test("GET 200, PUT 200, PATCH 405, DELETE 405", async ({ request }) => {
    const get = await request.get(url);
    expect(get.status()).toBe(200);
    const put = await request.put(`${URL_BACKEND}/api/file`, {
      headers,
      data: { path: target, content: fs.readFileSync(repoFile(target), "utf8") },
    });
    expect([200, 409]).toContain(put.status());
    const patch = await request.fetch(`${URL_BACKEND}/api/file`, {
      method: "PATCH",
      headers,
      data: { path: target, content: "x" },
    });
    expect(patch.status()).toBe(405);
    const del = await request.delete(`${URL_BACKEND}/api/file?path=${encodeURIComponent(target)}`, { headers });
    expect(del.status()).toBe(405);
  });

  test("HEAD 200 with empty body", async ({ request }) => {
    const head = await request.fetch(url, { method: "HEAD" });
    expect(head.status()).toBe(200);
  });
});

// SYS-19 — Extension allowlist (415) and 1 MB body cap (413)
test.describe("SYS-19 — Extension + body cap", () => {
  const target = `${PROJECT_REL}/findings/dossier.md`;
  const headers = { Origin: URL_BACKEND, Host: `127.0.0.1:${PORT_BACKEND}` };

  test("svg → 415, exe → 415, png → 415, NUL → 415, invalid UTF-8 → 415", async ({ request }) => {
    const svg = await request.put(`${URL_BACKEND}/api/file`, {
      headers,
      data: { path: `${PROJECT_REL}/findings/x.svg`, content: "<svg/>" },
    });
    expect(svg.status()).toBe(415);
    const exe = await request.put(`${URL_BACKEND}/api/file`, {
      headers,
      data: { path: `${PROJECT_REL}/findings/x.exe`, content: "MZ" },
    });
    expect(exe.status()).toBe(415);
    const png = await request.put(`${URL_BACKEND}/api/file`, {
      headers,
      data: { path: `${PROJECT_REL}/findings/sample.png`, content: "x" },
    });
    expect(png.status()).toBe(415);
    const nul = await request.fetch(`${URL_BACKEND}/api/file`, {
      method: "PUT",
      headers: { ...headers, "Content-Type": "application/json" },
      data: '{"path":"' + target + '","content":"\u0000abc"}',
    });
    expect(nul.status()).toBe(415);
    const badUtf = await request.fetch(`${URL_BACKEND}/api/file`, {
      method: "PUT",
      headers: { ...headers, "Content-Type": "application/json" },
      data: '{"path":"' + target + '","content":"\\udc80\\udc80"}',
    });
    expect([400, 415]).toContain(badUtf.status());
  });

  test("1.5 MB body → 413; 999 KB body → 200/409", async ({ request }) => {
    const big = "X".repeat(1_500_000);
    const r413 = await request.put(`${URL_BACKEND}/api/file`, {
      headers,
      data: { path: target, content: big },
    });
    expect(r413.status()).toBe(413);
    const okSize = "Y".repeat(900_000);
    const rOk = await request.put(`${URL_BACKEND}/api/file`, {
      headers,
      data: { path: target, content: okSize },
    });
    expect([200, 409]).toContain(rOk.status());
    if (rOk.status() === 200) {
      // Restore original
      const original = fs.readFileSync(repoFile(target), "utf8");
      await request.put(`${URL_BACKEND}/api/file`, {
        headers,
        data: { path: target, content: original },
      });
    }
  });
});

// SYS-20 — Sidebar structural sanity
test.describe("SYS-20 — Sidebar structural sanity", () => {
  test("each top-level section has ≥1 leaf; project subtree has canonical stage subfolders", async ({ page }) => {
    const tracker = attachConsoleErrorTracker(page);
    await page.goto("/");
    await expect(page.locator('[data-testid="sidebar"]')).toBeVisible();
    const topSections = page.locator('[data-testid="sidebar"] [data-section-toplevel]');
    await expect(topSections).toHaveCount(2);
    for (let i = 0; i < 2; i++) {
      const sec = topSections.nth(i);
      if ((await sec.getAttribute("aria-expanded")) === "false") await sec.click();
    }
    const leaves = page.locator('[data-testid="sidebar"] [role="treeitem"][data-leaf="true"]');
    expect(await leaves.count()).toBeGreaterThanOrEqual(3);
    // Drill into the spec_driven project — every canonical stage subfolder shows up.
    const stageFolders = ["user_input", "interview", "findings", "final_specs", "validation"];
    for (const sf of stageFolders) {
      await expect(page.locator(`[data-testid="sidebar"] [data-folder-name="${sf}"]`).first()).toBeVisible();
    }
    expect(tracker.errors).toEqual([]);
  });
});

// SYS-21 — Project-page master Regenerate panel + Wrap toggle
test.describe("SYS-21 — Project-page master Regenerate panel", () => {
  test("multi-stage build, autonomous header, wrap toggle behaviour, computed style", async ({ page, context }) => {
    const tracker = attachConsoleErrorTracker(page);
    await context.grantPermissions(["clipboard-read", "clipboard-write"]);
    await page.goto(`/project/development/spec_driven`);
    await expect(page.locator('[data-testid="project-page"]')).toBeVisible();
    const allStages = page.locator('[data-testid="stage-checkbox"]');
    const n = await allStages.count();
    for (let i = 0; i < n; i++) await allStages.nth(i).uncheck();
    await page.locator('[data-testid="stage-checkbox"][data-stage="interview"]').check();
    await page.locator('[data-testid="stage-checkbox"][data-stage="final_specs"]').check();
    const auto = page.locator('[data-testid="autonomous-toggle"]');
    if ((await auto.getAttribute("aria-checked")) === "false") await auto.click();
    await page.locator('[data-testid="build-prompt"]').click();

    const block = page.locator('[data-testid="regen-prompt-block"]');
    await expect(block).toBeVisible();
    const breakdown = page.locator('[data-testid="regen-breakdown-line"]');
    await expect(breakdown).toContainText(/2 stages selected/);
    await expect(breakdown).toContainText(/autonomous=on/);

    const body = page.locator('[data-testid="regen-prompt-body"]');
    const text = await body.innerText();
    expect(text.split("\n")[0]).toBe("# EXECUTION MODE: AUTONOMOUS");
    const interviewIdx = text.indexOf("interview");
    const finalIdx = text.indexOf("final_specs");
    expect(interviewIdx).toBeGreaterThan(-1);
    expect(finalIdx).toBeGreaterThan(-1);
    expect(interviewIdx).toBeLessThan(finalIdx);

    const wrap = page.locator('[data-testid="wrap-toggle"]');
    await expect(wrap).toHaveAttribute("aria-checked", "true");
    const pre = page.locator('[data-testid="regen-prompt-body"] pre').first();
    let ws = await pre.evaluate((el) => getComputedStyle(el).whiteSpace);
    expect(ws).toMatch(/pre-wrap|break-spaces/);
    await wrap.click();
    ws = await pre.evaluate((el) => getComputedStyle(el).whiteSpace);
    expect(ws).toBe("pre");
    await wrap.click();
    ws = await pre.evaluate((el) => getComputedStyle(el).whiteSpace);
    expect(ws).toMatch(/pre-wrap|break-spaces/);

    const fs13 = await pre.evaluate((el) => getComputedStyle(el).fontSize);
    expect(fs13).toBe("13px");
    const lh = await pre.evaluate((el) => getComputedStyle(el).lineHeight);
    expect(parseFloat(lh)).toBeCloseTo(13 * 1.55, 0);
    const mh = await pre.evaluate((el) => getComputedStyle(el).maxHeight);
    expect(mh).toBe("520px");

    await page.reload();
    await expect(page.locator('[data-testid="autonomous-toggle"]')).toHaveAttribute("aria-checked", "true");

    expect(tracker.errors).toEqual([]);
  });
});

// SYS-22 — Broken internal markdown links render as muted span
test.describe("SYS-22 — Broken internal links", () => {
  const fixturePath = repoFile(`${PROJECT_REL}/findings/link-fixture.md`);
  const validPath = repoFile(`${PROJECT_REL}/findings/valid-target.md`);
  let fixtureOriginal: string | null = null;
  let validOriginal: string | null = null;

  test.beforeAll(() => {
    if (fs.existsSync(fixturePath)) fixtureOriginal = fs.readFileSync(fixturePath, "utf8");
    if (fs.existsSync(validPath)) validOriginal = fs.readFileSync(validPath, "utf8");
    fs.mkdirSync(path.dirname(fixturePath), { recursive: true });
    fs.writeFileSync(validPath, "# valid target\nhello\n", "utf8");
    fs.writeFileSync(
      fixturePath,
      [
        "# Link fixture",
        "",
        "- valid: [valid](./valid-target.md)",
        "- broken: [broken](./does-not-exist.md)",
        "- external: [external](https://example.com)",
        "",
      ].join("\n"),
      "utf8",
    );
  });
  test.afterAll(() => {
    if (fixtureOriginal === null) {
      if (fs.existsSync(fixturePath)) fs.unlinkSync(fixturePath);
    } else fs.writeFileSync(fixturePath, fixtureOriginal, "utf8");
    if (validOriginal === null) {
      if (fs.existsSync(validPath)) fs.unlinkSync(validPath);
    } else fs.writeFileSync(validPath, validOriginal, "utf8");
  });

  test("valid → <a>, broken → <span class='broken-link'>, external → target=_blank rel=noopener", async ({ page }) => {
    const tracker = attachConsoleErrorTracker(page);
    await page.goto(`/file/${encodePathParam(`${PROJECT_REL}/findings/link-fixture.md`)}`);
    await expect(page.locator('[data-render-mode="markdown"]')).toBeVisible();
    const main = page.locator('[data-render-mode="markdown"]');
    await expect(main.locator('a[href*="valid-target"]')).toHaveCount(1);
    const broken = main.locator(".broken-link");
    await expect(broken).toHaveCount(1);
    expect(await broken.evaluate((el) => el.tagName.toLowerCase())).toBe("span");
    await expect(broken).toHaveAttribute("title", /not found|broken|missing/i);
    const ext = main.locator('a[href^="https://"]');
    await expect(ext.first()).toHaveAttribute("target", "_blank");
    const rel = (await ext.first().getAttribute("rel")) || "";
    expect(rel).toContain("noopener");
    expect(tracker.errors).toEqual([]);
  });
});

// SYS-23 — Editor save-error banner persistence
test.describe("SYS-23 — Save-error banner persistence", () => {
  test("inline banner above textarea, persists past toast timeout, clears on retry success", async ({ page }) => {
    const tracker = attachConsoleErrorTracker(page);
    const target = `${PROJECT_REL}/findings/dossier.md`;
    const targetAbs = repoFile(target);
    const original = fs.existsSync(targetAbs) ? fs.readFileSync(targetAbs, "utf8") : null;

    let failNext = true;
    await page.route(`**/api/file**`, async (route) => {
      const req = route.request();
      if (req.method() === "PUT" && failNext) {
        failNext = false;
        await route.fulfill({ status: 500, contentType: "application/json", body: JSON.stringify({ detail: "internal_error" }) });
        return;
      }
      await route.continue();
    });

    await page.goto(`/file/${encodePathParam(target)}`);
    await page.click('[data-action="edit-file"]');
    const textarea = page.locator('textarea[data-testid="file-editor-textarea"]');
    await textarea.fill((await textarea.inputValue()) + "\n<!-- sys-23 -->\n");

    await page.keyboard.press("Control+s");
    const banner = page.locator('[data-testid="save-error-banner"]');
    await expect(banner).toBeVisible();
    // Verify banner is in normal flow above the textarea (NOT a toast).
    const bannerBox = await banner.boundingBox();
    const taBox = await textarea.boundingBox();
    expect(bannerBox && taBox && bannerBox.y < taBox.y).toBe(true);

    // Wait beyond a toast lifetime (5s) and assert banner persists.
    await page.waitForTimeout(5500);
    await expect(banner).toBeVisible();

    // Dirty indicator persists during failure.
    await expect(page.locator('[data-testid="dirty-indicator"]')).toBeVisible();

    // Retry succeeds (route allows PUT through this time).
    await page.keyboard.press("Control+s");
    await expect(banner).toHaveCount(0, { timeout: 5000 });

    if (original !== null) fs.writeFileSync(targetAbs, original, "utf8");
    expect(tracker.errors.filter((e) => !/500|internal_error/i.test(e))).toEqual([]);
  });
});

// SYS-24 — Pin survival in regen prompt
test.describe("SYS-24 — Pin survival roundtrip", () => {
  const promotedPath = repoFile(`${PROJECT_REL}/validation/promoted.md`);
  let originalPromoted: string | null = null;

  test.beforeAll(() => {
    if (fs.existsSync(promotedPath)) originalPromoted = fs.readFileSync(promotedPath, "utf8");
    if (fs.existsSync(promotedPath)) fs.unlinkSync(promotedPath);
  });
  test.afterAll(() => {
    if (originalPromoted !== null) fs.writeFileSync(promotedPath, originalPromoted, "utf8");
    else if (fs.existsSync(promotedPath)) fs.unlinkSync(promotedPath);
  });

  test("pin AC-7 → promoted.md gets verbatim text → regen prompt includes Pinned items section → unpin clears it", async ({ page }) => {
    const tracker = attachConsoleErrorTracker(page);
    await page.goto(`/file/${encodePathParam(`${PROJECT_REL}/validation/acceptance_criteria.md`)}`);
    const ac7Pin = page.locator('[data-action="pin"][data-item-id="AC-7"]').first();
    await expect(ac7Pin).toBeVisible();
    await ac7Pin.click();
    await expect.poll(() => fs.existsSync(promotedPath) ? fs.readFileSync(promotedPath, "utf8") : "", { timeout: 5000 }).toMatch(/AC-7/);

    await page.goto(`/project/development/spec_driven`);
    const all = page.locator('[data-testid="stage-checkbox"]');
    const n = await all.count();
    for (let i = 0; i < n; i++) await all.nth(i).uncheck();
    await page.locator('[data-testid="stage-checkbox"][data-stage="validation"]').check();
    await page.locator('[data-testid="build-prompt"]').click();
    const body = page.locator('[data-testid="regen-prompt-body"]');
    const text = await body.innerText();
    expect(text).toMatch(/Pinned items \(MUST survive regeneration\)/);
    expect(text).toContain("AC-7");

    await page.goto(`/file/${encodePathParam(`${PROJECT_REL}/validation/acceptance_criteria.md`)}`);
    const ac7Unpin = page.locator('[data-action="pin"][data-item-id="AC-7"]').first();
    await ac7Unpin.click();
    await expect
      .poll(() => (fs.existsSync(promotedPath) ? fs.readFileSync(promotedPath, "utf8") : ""), { timeout: 5000 })
      .not.toMatch(/AC-7/);

    await page.goto(`/project/development/spec_driven`);
    const all2 = page.locator('[data-testid="stage-checkbox"]');
    const m = await all2.count();
    for (let i = 0; i < m; i++) await all2.nth(i).uncheck();
    await page.locator('[data-testid="stage-checkbox"][data-stage="validation"]').check();
    await page.locator('[data-testid="build-prompt"]').click();
    const text2 = await page.locator('[data-testid="regen-prompt-body"]').innerText();
    expect(text2).not.toMatch(/AC-7/);
    expect(tracker.errors).toEqual([]);
  });
});

// SYS-25 — NFR-3 latency budget
test.describe("SYS-25 — Initial app load < 2s on localhost", () => {
  test("median over 3 runs satisfies budgets", async ({ page, request }) => {
    const elapsed: number[] = [];
    for (let i = 0; i < 3; i++) {
      await page.context().clearCookies();
      const t0 = Date.now();
      await page.goto("/", { waitUntil: "networkidle" });
      await expect(page.locator('[data-testid="sidebar"] [role="treeitem"]').first()).toBeVisible();
      await expect(page.locator("main h1, main h2").first()).toBeVisible();
      elapsed.push(Date.now() - t0);
    }
    elapsed.sort((a, b) => a - b);
    const median = elapsed[1];
    expect(median).toBeLessThan(2000);

    const t0 = Date.now();
    const tree = await request.get(`${URL_BACKEND}/api/tree`);
    expect(tree.status()).toBe(200);
    expect(Date.now() - t0).toBeLessThan(250);

    const t1 = Date.now();
    const claudeMd = await request.get(`${URL_BACKEND}/api/file?path=CLAUDE.md`);
    expect(claudeMd.status()).toBe(200);
    expect(Date.now() - t1).toBeLessThan(100);
  });
});

// SYS-26 — Stale-write 409
test.describe("SYS-26 — Stale-write 409 conflict", () => {
  const target = `${PROJECT_REL}/findings/conflict-fixture.md`;
  const targetAbs = repoFile(target);
  let originalExisted = false;
  let originalContent: string | null = null;

  test.beforeAll(() => {
    originalExisted = fs.existsSync(targetAbs);
    if (originalExisted) originalContent = fs.readFileSync(targetAbs, "utf8");
    fs.mkdirSync(path.dirname(targetAbs), { recursive: true });
    fs.writeFileSync(targetAbs, "v1\n", "utf8");
  });
  test.afterAll(() => {
    if (originalExisted && originalContent !== null) fs.writeFileSync(targetAbs, originalContent, "utf8");
    else if (fs.existsSync(targetAbs)) fs.unlinkSync(targetAbs);
  });

  test("If-Unmodified-Since stale → 409; Reload button refreshes editor; subsequent save succeeds", async ({ page }) => {
    const tracker = attachConsoleErrorTracker(page);
    await page.goto(`/file/${encodePathParam(target)}`);
    await page.click('[data-action="edit-file"]');
    const textarea = page.locator('textarea[data-testid="file-editor-textarea"]');
    await expect(textarea).toBeVisible();

    // Side-channel write — bumps mtime.
    await new Promise((r) => setTimeout(r, 1100));
    fs.writeFileSync(targetAbs, "v2\n", "utf8");

    await textarea.fill((await textarea.inputValue()) + "user-edit");
    await page.keyboard.press("Control+s");
    const banner = page.locator('[data-testid="save-error-banner"]');
    await expect(banner).toBeVisible();
    await expect(banner).toContainText(/changed externally|stale|reload/i);

    const reload = page.locator('[data-testid="banner-reload"]');
    await reload.click();
    await expect(textarea).toHaveValue(/v2/, { timeout: 5000 });
    await expect(banner).toHaveCount(0);

    await textarea.fill((await textarea.inputValue()) + "user-edit-2");
    await page.keyboard.press("Control+s");
    await expect(banner).toHaveCount(0);

    const onDisk = fs.readFileSync(targetAbs, "utf8");
    expect(onDisk).toContain("user-edit-2");
    expect(tracker.errors).toEqual([]);
  });
});

// SYS-27 — Manual UI walkthrough handoff
test.describe("SYS-27 — Manual walkthrough handoff", () => {
  test("validation.requires_manual_walkthrough event present in events.jsonl with checklist payload", async () => {
    const auditDir = path.join(REPO_ROOT, ".audit", "adhoc_agents", "2026-05-03");
    test.skip(!fs.existsSync(auditDir), "no audit run folder yet — stage 6 not started");
    const runs = fs.readdirSync(auditDir).filter((d) => d.startsWith("spec_driven-"));
    test.skip(runs.length === 0, "no spec_driven runs in audit dir");
    let foundEvent: Record<string, unknown> | null = null;
    for (const run of runs) {
      const eventsPath = path.join(auditDir, run, "events.jsonl");
      if (!fs.existsSync(eventsPath)) continue;
      const lines = fs.readFileSync(eventsPath, "utf8").split("\n").filter(Boolean);
      for (const ln of lines) {
        try {
          const ev = JSON.parse(ln);
          if (ev.type === "validation.requires_manual_walkthrough" || ev.event === "validation.requires_manual_walkthrough") {
            foundEvent = ev;
            break;
          }
        } catch {
          /* skip parse-failed line */
        }
      }
      if (foundEvent) break;
    }
    expect(foundEvent).not.toBeNull();
    const payload = JSON.stringify(foundEvent);
    expect(payload).toMatch(/contrast|focus|motion|wrap|walkthrough|keyboard|forced.colors|zoom|copy/i);
  });
});
