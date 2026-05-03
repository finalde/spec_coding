import { describe, expect, it } from "vitest";
import { resolveLink } from "../src/lib/linkResolver";

const cur = "specs/development/spec_driven/final_specs/spec.md";

describe("resolveLink", () => {
  it("rewrites a relative link to /file/<resolved>", () => {
    expect(resolveLink(cur, "../interview/qa.md")).toEqual({
      kind: "internal",
      href: "/file/specs/development/spec_driven/interview/qa.md",
    });
  });

  it("opens absolute http(s) externally", () => {
    expect(resolveLink(cur, "https://owasp.org")).toEqual({
      kind: "external",
      href: "https://owasp.org",
    });
  });

  it("anchor-only stays as anchor", () => {
    expect(resolveLink(cur, "#section-1")).toEqual({ kind: "anchor", href: "#section-1" });
  });

  it("rejects javascript: as broken", () => {
    expect(resolveLink(cur, "javascript:alert(1)").kind).toBe("broken");
  });

  it("rejects deeply traversing paths as broken", () => {
    expect(resolveLink(cur, "../../../../../etc/passwd").kind).toBe("broken");
  });
});
