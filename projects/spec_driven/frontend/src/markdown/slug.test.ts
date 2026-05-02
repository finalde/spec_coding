import { describe, expect, it } from "vitest";
import { SlugRegistry } from "./slug";

describe("SlugRegistry", () => {
  it("lowercases and hyphenates", () => {
    const r = new SlugRegistry();
    expect(r.generate("Hello World")).toBe("hello-world");
  });

  it("drops punctuation", () => {
    const r = new SlugRegistry();
    expect(r.generate("Hello, World!")).toBe("hello-world");
  });

  it("trims surrounding whitespace", () => {
    const r = new SlugRegistry();
    expect(r.generate("  Spaces  ")).toBe("spaces");
  });

  it("preserves existing hyphens", () => {
    const r = new SlugRegistry();
    expect(r.generate("Already-Hyphenated")).toBe("already-hyphenated");
  });

  it("appends collision suffixes", () => {
    const r = new SlugRegistry();
    expect(r.generate("Foo")).toBe("foo");
    expect(r.generate("Foo")).toBe("foo-1");
    expect(r.generate("Foo")).toBe("foo-2");
  });

  it("drops non-ASCII characters", () => {
    const r = new SlugRegistry();
    expect(r.generate("Café")).toBe("caf");
  });

  it("falls back to 'section' when slug is empty", () => {
    const r = new SlugRegistry();
    expect(r.generate("☃️")).toBe("section");
    expect(r.generate("！？")).toBe("section-1");
  });

  it("handles leading digits", () => {
    const r = new SlugRegistry();
    expect(r.generate("1. Intro")).toBe("1-intro");
  });
});
