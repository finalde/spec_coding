export class TypedLocalStorage<T> {
  private readonly key: string;
  private readonly fallback: T;
  private readonly serialize: (value: T) => string;
  private readonly deserialize: (raw: string) => T;

  constructor(
    key: string,
    fallback: T,
    serialize: (value: T) => string = JSON.stringify,
    deserialize: (raw: string) => T = JSON.parse,
  ) {
    this.key = key;
    this.fallback = fallback;
    this.serialize = serialize;
    this.deserialize = deserialize;
  }

  read(): T {
    if (typeof window === "undefined" || !window.localStorage) return this.fallback;
    try {
      const raw = window.localStorage.getItem(this.key);
      if (raw === null) return this.fallback;
      return this.deserialize(raw);
    } catch {
      return this.fallback;
    }
  }

  write(value: T): void {
    if (typeof window === "undefined" || !window.localStorage) return;
    try {
      window.localStorage.setItem(this.key, this.serialize(value));
    } catch {
      // ignored — storage may be full or disabled
    }
  }

  storageKey(): string {
    return this.key;
  }
}
