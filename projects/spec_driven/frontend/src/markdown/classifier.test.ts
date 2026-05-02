import { describe, expect, it } from "vitest";
import { classifyLink } from "./classifier";

const exposedPaths = new Set([
  "specs/development/spec_driven/final_specs/spec.md",
  "specs/development/spec_driven/findings/dossier.md",
  "specs/development/spec_driven/findings/angle-prior-art-readonly-viewers.md",
  "CLAUDE.md",
]);

const ctx = {
  sourcePath: "specs/development/spec_driven/final_specs/spec.md",
  exposedPaths,
};

describe("classifyLink", () => {
  it("classifies https as external", () => {
    expect(classifyLink("https://example.com", ctx)).toEqual({
      kind: "external",
      href: "https://example.com",
    });
  });

  it("classifies mailto as external", () => {
    expect(classifyLink("mailto:x@y.com", ctx).kind).toBe("external");
  });

  it("classifies protocol-relative as external", () => {
    expect(classifyLink("//cdn.example.com/x", ctx).kind).toBe("external");
  });

  it("classifies hash as anchor", () => {
    expect(classifyLink("#goal", ctx)).toEqual({ kind: "anchor", fragment: "goal" });
  });

  it("classifies sibling existing file as internal", () => {
    expect(classifyLink("../findings/dossier.md", ctx)).toEqual({
      kind: "internal",
      targetPath: "specs/development/spec_driven/findings/dossier.md",
    });
  });

  it("classifies missing file as broken-missing", () => {
    expect(classifyLink("../findings/missing.md", ctx).kind).toBe("broken");
  });

  it("classifies escape-the-tree as broken", () => {
    const result = classifyLink("../../../../../etc/hosts", ctx);
    expect(result.kind).toBe("broken");
  });

  it("URL-decodes percent-encoded paths", () => {
    expect(classifyLink("..%2Ffindings%2Fdossier.md", ctx).kind).toBe("internal");
  });
});
