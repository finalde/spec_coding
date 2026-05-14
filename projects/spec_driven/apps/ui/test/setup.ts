import "@testing-library/jest-dom/vitest";
import { afterEach, beforeEach } from "vitest";
import { cleanup } from "@testing-library/react";

afterEach(() => {
  cleanup();
});

beforeEach(() => {
  if (typeof window !== "undefined" && window.localStorage) {
    if (typeof window.localStorage.clear === "function") {
      window.localStorage.clear();
    } else {
      // Fallback for environments where clear is missing (Node 25 web-storage)
      try {
        for (let i = window.localStorage.length - 1; i >= 0; i -= 1) {
          const key = window.localStorage.key(i);
          if (key) window.localStorage.removeItem(key);
        }
      } catch {
        // ignored
      }
    }
  }
});

if (typeof window !== "undefined" && !("matchMedia" in window)) {
  Object.defineProperty(window, "matchMedia", {
    writable: true,
    value: (query: string) => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: () => {},
      removeListener: () => {},
      addEventListener: () => {},
      removeEventListener: () => {},
      dispatchEvent: () => false,
    }),
  });
}
