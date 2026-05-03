import { describe, it, expect } from "vitest";
import { resolveLink } from "../src/lib/linkResolver";

const knownPaths: ReadonlySet<string> = new Set([
  "specs/development/spec_driven/final_specs/spec.md",
  "specs/development/spec_driven/validation/strategy.md",
  "specs/development/spec_driven/validation/unit_tests.md",
  "specs/development/spec_driven/findings/dossier.md",
  "specs/development/spec_driven/findings/diagram.png",
  "specs/development/spec_driven/foo bar.md",
  "specs/development/spec_driven/sibling.md",
  "specs/development/different_project/spec.md",
]);

const isKnown = (p: string): boolean => knownPaths.has(p);

describe("linkResolver — relative resolution (Group 10.1)", () => {
  it("resolves '../validation/strategy.md' against the current file directory", () => {
    const result = resolveLink({
      currentFile: "specs/development/spec_driven/final_specs/spec.md",
      href: "../validation/strategy.md",
      isKnown,
    });
    expect(result.kind).toBe("internal");
    if (result.kind === "internal") {
      expect(result.path).toBe(
        "specs/development/spec_driven/validation/strategy.md",
      );
    }
  });

  it("resolves './sibling.md'", () => {
    const result = resolveLink({
      currentFile: "specs/development/spec_driven/final_specs/spec.md",
      href: "./sibling.md",
      isKnown: (p) => p === "specs/development/spec_driven/final_specs/sibling.md",
    });
    expect(result.kind).toBe("internal");
  });

  it("resolves bare paths without leading './'", () => {
    const result = resolveLink({
      currentFile: "specs/development/spec_driven/final_specs/spec.md",
      href: "sibling.md",
      isKnown: (p) => p === "specs/development/spec_driven/final_specs/sibling.md",
    });
    expect(result.kind).toBe("internal");
  });

  it("resolves '../../different_project/spec.md'", () => {
    const result = resolveLink({
      currentFile: "specs/development/spec_driven/final_specs/spec.md",
      href: "../../different_project/spec.md",
      isKnown,
    });
    expect(result.kind).toBe("internal");
    if (result.kind === "internal") {
      expect(result.path).toBe("specs/development/different_project/spec.md");
    }
  });
});

describe("linkResolver — external links (Group 10.2)", () => {
  it("returns external for https://", () => {
    const result = resolveLink({
      currentFile: "specs/development/spec_driven/final_specs/spec.md",
      href: "https://example.com/foo",
      isKnown,
    });
    expect(result.kind).toBe("external");
    if (result.kind === "external") {
      expect(result.href).toBe("https://example.com/foo");
    }
  });

  it("returns external for http://", () => {
    const result = resolveLink({
      currentFile: "specs/development/spec_driven/final_specs/spec.md",
      href: "http://example.com",
      isKnown,
    });
    expect(result.kind).toBe("external");
  });
});

describe("linkResolver — broken-link detection (Group 10.3, AC-27)", () => {
  it("returns broken kind (NOT external, NOT internal) for missing relative target", () => {
    const result = resolveLink({
      currentFile: "specs/development/spec_driven/final_specs/spec.md",
      href: "../validation/missing.md",
      isKnown,
    });
    expect(result.kind).toBe("broken");
  });

  it("broken-link result carries an explanatory title (Group 10.4)", () => {
    const result = resolveLink({
      currentFile: "specs/development/spec_driven/final_specs/spec.md",
      href: "../validation/nope.md",
      isKnown,
    });
    expect(result.kind).toBe("broken");
    if (result.kind === "broken") {
      expect(result.title).toBeTruthy();
      expect(result.title.length).toBeGreaterThan(0);
    }
  });

  it("path-resolves-outside-tree returns broken with an outside-tree title hint", () => {
    const result = resolveLink({
      currentFile: "specs/development/spec_driven/final_specs/spec.md",
      href: "../../../../etc/passwd",
      isKnown,
    });
    expect(result.kind).toBe("broken");
    if (result.kind === "broken") {
      expect(result.title.toLowerCase()).toMatch(/outside|exposed|tree/);
    }
  });
});

describe("linkResolver — anchor handling (Group 10.5)", () => {
  it("anchor-only link returns kind=anchor with the same-file path", () => {
    const result = resolveLink({
      currentFile: "specs/development/spec_driven/final_specs/spec.md",
      href: "#section-foo",
      isKnown,
    });
    expect(result.kind).toBe("anchor");
    if (result.kind === "anchor") {
      expect(result.hash).toBe("#section-foo");
    }
  });

  it("cross-file anchor resolves the file and passes the hash through", () => {
    const result = resolveLink({
      currentFile: "specs/development/spec_driven/final_specs/spec.md",
      href: "../validation/strategy.md#anchor",
      isKnown,
    });
    expect(result.kind).toBe("internal");
    if (result.kind === "internal") {
      expect(result.path).toBe(
        "specs/development/spec_driven/validation/strategy.md",
      );
      expect(result.hash).toBe("#anchor");
    }
  });
});

describe("linkResolver — encoding & normalization (Groups 10.6, 10.8)", () => {
  it("decodes percent-encoded paths once", () => {
    const result = resolveLink({
      currentFile: "specs/development/spec_driven/final_specs/spec.md",
      href: "../foo%20bar.md",
      isKnown: (p) => p === "specs/development/spec_driven/foo bar.md",
    });
    expect(result.kind).toBe("internal");
  });

  it("normalizes mixed/back-slashes in user-authored markdown content", () => {
    const result = resolveLink({
      currentFile: "specs/development/spec_driven/final_specs/spec.md",
      href: "..\\validation\\strategy.md",
      isKnown,
    });
    expect(result.kind).toBe("internal");
    if (result.kind === "internal") {
      expect(result.path).toBe(
        "specs/development/spec_driven/validation/strategy.md",
      );
    }
  });
});

describe("linkResolver — image routing & robustness (Groups 10.7, 10.9)", () => {
  it("image-extension link routes to internal kind so ImagePlaceholder can fetch", () => {
    const result = resolveLink({
      currentFile: "specs/development/spec_driven/final_specs/spec.md",
      href: "../findings/diagram.png",
      isKnown,
    });
    expect(result.kind).toBe("internal");
  });

  it("does not throw on pathological inputs — returns broken instead", () => {
    const longPath = "../" + "a/".repeat(2000) + "x.md";
    expect(() =>
      resolveLink({
        currentFile: "specs/development/spec_driven/final_specs/spec.md",
        href: longPath,
        isKnown,
      }),
    ).not.toThrow();
    const result = resolveLink({
      currentFile: "specs/development/spec_driven/final_specs/spec.md",
      href: longPath,
      isKnown,
    });
    expect(result.kind).toBe("broken");
  });

  it("does not throw on control characters", () => {
    expect(() =>
      resolveLink({
        currentFile: "specs/development/spec_driven/final_specs/spec.md",
        href: "../foo.md",
        isKnown,
      }),
    ).not.toThrow();
  });
});
