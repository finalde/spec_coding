export class SlugRegistry {
  private readonly seen = new Map<string, number>();

  generate(text: string): string {
    const base = SlugRegistry.baseSlug(text);
    const root = base === "" ? "section" : base;
    const count = this.seen.get(root) ?? 0;
    this.seen.set(root, count + 1);
    return count === 0 ? root : `${root}-${count}`;
  }

  static baseSlug(text: string): string {
    let s = text.toLowerCase();
    s = s.replace(/[^\x00-\x7f]/g, "");
    s = s.replace(/[^a-z0-9\s-]/g, "");
    s = s.replace(/\s+/g, "-");
    s = s.replace(/-+/g, "-");
    s = s.replace(/^-+|-+$/g, "");
    return s;
  }
}
