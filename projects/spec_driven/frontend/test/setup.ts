import "@testing-library/jest-dom/vitest";

// Some jsdom configurations leave localStorage on an opaque origin (DOMException
// SecurityError). Provide a working in-memory localStorage shim so component
// tests can persist values without depending on jsdom's URL config.
if (typeof window !== "undefined") {
  let needsShim = false;
  try {
    // Calling getItem before reads tells us whether the storage is opaque.
    window.localStorage.getItem("__probe__");
  } catch {
    needsShim = true;
  }
  if (needsShim || typeof window.localStorage?.setItem !== "function") {
    const store = new Map<string, string>();
    Object.defineProperty(window, "localStorage", {
      configurable: true,
      value: {
        getItem: (k: string) => (store.has(k) ? store.get(k)! : null),
        setItem: (k: string, v: string) => {
          store.set(k, String(v));
        },
        removeItem: (k: string) => {
          store.delete(k);
        },
        clear: () => store.clear(),
        key: (i: number) => Array.from(store.keys())[i] ?? null,
        get length() {
          return store.size;
        },
      },
    });
  }
}
