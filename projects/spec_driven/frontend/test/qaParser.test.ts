import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { ParseError, parseQa } from "../src/lib/qaParser";

const FIXTURE_DIR = join(__dirname, "fixtures", "qa");

function load(name: string): string {
  return readFileSync(join(FIXTURE_DIR, name), "utf-8");
}

describe("qaParser", () => {
  it("[regression-2026-05-02-clean] parses interactive form", () => {
    const doc = parseQa(load("interactive.md"));
    expect(doc.rounds).toHaveLength(1);
    expect(doc.rounds[0].number).toBe(1);
    expect(doc.rounds[0].categories).toHaveLength(2);
    const fnPairs = doc.rounds[0].categories[0].pairs;
    expect(fnPairs).toHaveLength(1);
    expect(fnPairs[0].q).toContain("Section 2");
    expect(fnPairs[0].a).toContain("All discovered");
    expect(fnPairs[0].judgmentCall).toBeNull();
  });

  it("[regression-2026-05-02-clean] parses autonomous form (judgment-call)", () => {
    const doc = parseQa(load("autonomous.md"));
    expect(doc.rounds).toHaveLength(1);
    const fnPairs = doc.rounds[0].categories[0].pairs;
    expect(fnPairs).toHaveLength(1);
    expect(fnPairs[0].a).toBe("All discovered.");
    expect(fnPairs[0].judgmentCall).toContain("All discovered");
    expect(fnPairs[0].judgmentCall).toContain("spec_driven is the first");
  });

  it("[regression-2026-05-02-clean] every fixture in fixtures/qa parses", () => {
    for (const name of ["interactive.md", "autonomous.md"]) {
      const doc = parseQa(load(name));
      expect(doc.rounds.length).toBeGreaterThan(0);
    }
  });

  it("throws ParseError on malformed input (no Round headings)", () => {
    expect(() => parseQa("### floating-category\n\n- Q: a\n- A: b")).toThrow(ParseError);
  });

  it("throws ParseError on Q without A", () => {
    expect(() => parseQa("## Round 1\n\n### cat\n\n- Q: orphan question")).toThrow(ParseError);
  });

  it("returns empty rounds on whitespace-only source", () => {
    expect(parseQa("   \n\n  ").rounds).toEqual([]);
  });
});
