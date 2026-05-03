import { describe, it, expect } from "vitest";
import { readFileSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { parseQa, QaParseError } from "../src/lib/qaParser";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const fixture = (slug: string): string =>
  readFileSync(resolve(__dirname, "fixtures", "qa", `${slug}.md`), "utf-8");

const realQaPath = resolve(
  __dirname,
  "..",
  "..",
  "..",
  "..",
  "specs",
  "development",
  "spec_driven",
  "interview",
  "qa.md",
);

describe("qaParser — interactive form (Group 9.1)", () => {
  it("parses a simple Round/Category/Q-A in the interactive form", () => {
    const text = fixture("interactive");
    const result = parseQa(text);
    expect(result.rounds.length).toBeGreaterThanOrEqual(1);
    const round1 = result.rounds[0];
    expect(round1.index).toBe(1);
    const cat = round1.categories.find((c) => c.name === "functional-scope");
    expect(cat).toBeDefined();
    expect(cat!.pairs.length).toBeGreaterThanOrEqual(2);
    expect(cat!.pairs[0].q).toMatch(/projects.*appear/i);
    expect(cat!.pairs[0].a).toMatch(/all discovered/i);
    expect(cat!.pairs[0].judgmentCall).toBeFalsy();
  });

  it("preserves multiple categories within a single round (Group 9.4)", () => {
    const text = fixture("interactive");
    const result = parseQa(text);
    const cats = result.rounds[0].categories.map((c) => c.name);
    expect(cats).toContain("functional-scope");
    expect(cats).toContain("ux-interaction");
  });

  it("preserves multiple rounds in source order (Group 9.4)", () => {
    const text = fixture("interactive");
    const result = parseQa(text);
    expect(result.rounds.map((r) => r.index)).toEqual([1, 2]);
  });
});

describe("qaParser — autonomous form (Group 9.2, move 10)", () => {
  it("extracts judgmentCall annotation out of `- A *(judgment call — chose X because Y)*:`", () => {
    const text = fixture("autonomous");
    const result = parseQa(text);
    const cat = result.rounds[0].categories.find(
      (c) => c.name === "ux-interaction",
    );
    expect(cat).toBeDefined();
    const pair = cat!.pairs.find((p) => /Autonomous-mode/i.test(p.q));
    expect(pair).toBeDefined();
    expect(pair!.judgmentCall).toBeTruthy();
    expect(pair!.judgmentCall).toMatch(/localStorage/i);
    // The parenthetical MUST NOT bleed into the answer text.
    expect(pair!.a).not.toMatch(/judgment call/i);
    expect(pair!.a).toMatch(/spec_driven\.autonomous_mode\.v1/);
  });

  it("treats the autonomous-form annotation as optional metadata, not part of the answer (Group 9.2)", () => {
    const text = fixture("autonomous");
    const result = parseQa(text);
    const allPairs = result.rounds.flatMap((r) =>
      r.categories.flatMap((c) => c.pairs),
    );
    expect(allPairs.length).toBeGreaterThanOrEqual(4);
    for (const p of allPairs) {
      expect(p.a).not.toMatch(/^\s*\*\(judgment call/);
    }
  });

  it("supports both em-dash and hyphen separators in the annotation", () => {
    const withEmDash = `## Round 1\n### Category: foo\n**Q:** A?\n- A *(judgment call — chose X because Y)*: text.\n`;
    const withHyphen = `## Round 1\n### Category: foo\n**Q:** A?\n- A *(judgment call - chose X because Y)*: text.\n`;
    const a = parseQa(withEmDash);
    const b = parseQa(withHyphen);
    expect(a.rounds[0].categories[0].pairs[0].judgmentCall).toMatch(/X/);
    expect(b.rounds[0].categories[0].pairs[0].judgmentCall).toMatch(/X/);
  });
});

describe("qaParser — real on-disk artifact (Group 9.3, move 10)", () => {
  it("parses the actual interview/qa.md from this run without throwing", () => {
    const text = readFileSync(realQaPath, "utf-8");
    const result = parseQa(text);
    expect(result.rounds.length).toBeGreaterThanOrEqual(1);
    const allPairs = result.rounds.flatMap((r) =>
      r.categories.flatMap((c) => c.pairs),
    );
    expect(allPairs.length).toBeGreaterThan(5);
  });

  it("captures judgmentCall on every A that has the autonomous annotation", () => {
    const text = readFileSync(realQaPath, "utf-8");
    const result = parseQa(text);
    const annotated = result.rounds
      .flatMap((r) => r.categories.flatMap((c) => c.pairs))
      .filter((p) => /\*\(judgment call/i.test(p.rawAnswerLine ?? ""));
    expect(annotated.length).toBeGreaterThan(0);
    for (const p of annotated) {
      expect(p.judgmentCall).toBeTruthy();
      expect(p.judgmentCall!.length).toBeGreaterThan(0);
    }
  });
});

describe("qaParser — error handling (Group 9.6)", () => {
  it("throws QaParseError on malformed input (no round headers, no Q/A)", () => {
    const malformed = "## Not a Round\nrandom prose without Q or A markers\n";
    expect(() => parseQa(malformed)).toThrow(QaParseError);
  });

  it("returns empty rounds for an empty file", () => {
    const result = parseQa("");
    expect(result.rounds).toEqual([]);
  });

  it("returns empty rounds for a whitespace-only file", () => {
    const result = parseQa("   \n   \n\n");
    expect(result.rounds).toEqual([]);
  });
});

describe("qaParser — render-time discriminants (Groups 9.7, 9.8)", () => {
  it("each pair has a stable itemId derivable from round/category/index", () => {
    const text = fixture("interactive");
    const a = parseQa(text);
    const b = parseQa(text);
    const aIds = a.rounds.flatMap((r) =>
      r.categories.flatMap((c) => c.pairs.map((p) => p.itemId)),
    );
    const bIds = b.rounds.flatMap((r) =>
      r.categories.flatMap((c) => c.pairs.map((p) => p.itemId)),
    );
    expect(aIds.length).toBeGreaterThan(0);
    expect(aIds).toEqual(bIds);
    expect(new Set(aIds).size).toBe(aIds.length);
  });

  it("category nodes carry kind 'category' (Group 9.7)", () => {
    const text = fixture("interactive");
    const result = parseQa(text);
    const cat = result.rounds[0].categories[0];
    expect(cat.kind).toBe("category");
  });

  it("Q and A nodes carry kind discriminants (Group 9.7)", () => {
    const text = fixture("interactive");
    const result = parseQa(text);
    const pair = result.rounds[0].categories[0].pairs[0];
    expect(pair.kind).toBe("qa");
  });
});

describe("qaParser — does not silently swallow unrecognized lines (Group 9.9)", () => {
  it("surfaces stray lines under an unrecognized array OR throws", () => {
    const stray = `## Round 1\n### Category: foo\n**Q:** ok?\n- A: yes.\nNote: this is a stray line.\n`;
    let result: ReturnType<typeof parseQa> | null = null;
    let err: unknown = null;
    try {
      result = parseQa(stray);
    } catch (e) {
      err = e;
    }
    if (err) {
      expect(err).toBeInstanceOf(QaParseError);
    } else {
      expect(result).not.toBeNull();
      // If no throw, parser must surface the stray line — never silently drop.
      expect(result!.unrecognized?.length ?? 0).toBeGreaterThan(0);
    }
  });
});
