import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { renderHook, act } from "@testing-library/react";
import {
  useAutonomousMode,
  AUTONOMOUS_MODE_STORAGE_KEY,
} from "../src/lib/autonomousMode";

const STORAGE_KEY = "spec_driven.autonomous_mode.v1";

describe("autonomousMode — storage key constant (Group 12.12)", () => {
  it("is exactly 'spec_driven.autonomous_mode.v1'", () => {
    expect(AUTONOMOUS_MODE_STORAGE_KEY).toBe(STORAGE_KEY);
  });
});

describe("autonomousMode — default off (Group 12.1)", () => {
  it("hook initial value is false when localStorage has no value", () => {
    const { result } = renderHook(() => useAutonomousMode());
    expect(result.current[0]).toBe(false);
  });
});

describe("autonomousMode — persistence (Groups 12.2, 12.3)", () => {
  it("toggling true persists to localStorage", () => {
    const { result } = renderHook(() => useAutonomousMode());
    act(() => {
      result.current[1](true);
    });
    expect(window.localStorage.getItem(STORAGE_KEY)).toBe("true");
    expect(result.current[0]).toBe(true);
  });

  it("reads pre-existing localStorage value on mount", () => {
    window.localStorage.setItem(STORAGE_KEY, "true");
    const { result } = renderHook(() => useAutonomousMode());
    expect(result.current[0]).toBe(true);
  });

  it("toggling back to false either persists 'false' or removes the key", () => {
    const { result } = renderHook(() => useAutonomousMode());
    act(() => {
      result.current[1](true);
    });
    act(() => {
      result.current[1](false);
    });
    const stored = window.localStorage.getItem(STORAGE_KEY);
    expect(stored === null || stored === "false").toBe(true);
    expect(result.current[0]).toBe(false);
  });
});

describe("autonomousMode — corrupt-value tolerance (Group 12.4)", () => {
  it("falls back to false when stored value is junk", () => {
    window.localStorage.setItem(STORAGE_KEY, "banana");
    const { result } = renderHook(() => useAutonomousMode());
    expect(result.current[0]).toBe(false);
  });

  it("does not throw when stored value is malformed JSON-ish", () => {
    window.localStorage.setItem(STORAGE_KEY, "{");
    expect(() => renderHook(() => useAutonomousMode())).not.toThrow();
  });
});

describe("autonomousMode — cross-tab storage event (Groups 12.5..12.7, AC-23)", () => {
  it("synthetic storage event for the autonomous key updates the hook value", () => {
    const { result } = renderHook(() => useAutonomousMode());
    expect(result.current[0]).toBe(false);

    act(() => {
      window.dispatchEvent(
        new StorageEvent("storage", {
          key: STORAGE_KEY,
          newValue: "true",
          oldValue: "false",
          storageArea: window.localStorage,
        }),
      );
    });
    expect(result.current[0]).toBe(true);
  });

  it("ignores storage events for other keys", () => {
    const { result } = renderHook(() => useAutonomousMode());
    act(() => {
      window.dispatchEvent(
        new StorageEvent("storage", {
          key: "unrelated.key",
          newValue: "true",
          oldValue: null,
          storageArea: window.localStorage,
        }),
      );
    });
    expect(result.current[0]).toBe(false);
  });

  it("storage event with newValue=null resets hook to default false", () => {
    window.localStorage.setItem(STORAGE_KEY, "true");
    const { result } = renderHook(() => useAutonomousMode());
    expect(result.current[0]).toBe(true);

    act(() => {
      window.dispatchEvent(
        new StorageEvent("storage", {
          key: STORAGE_KEY,
          newValue: null,
          oldValue: "true",
          storageArea: window.localStorage,
        }),
      );
    });
    expect(result.current[0]).toBe(false);
  });
});

describe("autonomousMode — unsubscribe and best-effort persistence (Groups 12.8, 12.10, 12.11)", () => {
  it("removes its storage listener on unmount", () => {
    const removeSpy = vi.spyOn(window, "removeEventListener");
    const { unmount } = renderHook(() => useAutonomousMode());
    unmount();
    const callsForStorage = removeSpy.mock.calls.filter((c) => c[0] === "storage");
    expect(callsForStorage.length).toBeGreaterThan(0);
    removeSpy.mockRestore();
  });

  it("swallows QuotaExceededError on setItem and still updates in-memory value", () => {
    const original = Storage.prototype.setItem;
    const stub = vi.fn(() => {
      const err = new Error("QuotaExceeded");
      err.name = "QuotaExceededError";
      throw err;
    });
    Storage.prototype.setItem = stub as unknown as typeof Storage.prototype.setItem;

    const consoleWarn = vi.spyOn(console, "warn").mockImplementation(() => {});

    let didThrow = false;
    const { result } = renderHook(() => useAutonomousMode());
    try {
      act(() => {
        result.current[1](true);
      });
    } catch {
      didThrow = true;
    }
    expect(didThrow).toBe(false);
    expect(result.current[0]).toBe(true);

    Storage.prototype.setItem = original;
    consoleWarn.mockRestore();
  });
});

describe("autonomousMode — no server-side persistence (Group 12.9)", () => {
  it("toggling does NOT trigger any fetch", () => {
    const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response("{}", { status: 200 }),
    );
    const { result } = renderHook(() => useAutonomousMode());
    act(() => {
      result.current[1](true);
    });
    act(() => {
      result.current[1](false);
    });
    expect(fetchSpy).not.toHaveBeenCalled();
    fetchSpy.mockRestore();
  });
});

describe("autonomousMode — localStorage unavailable (Group 12.11)", () => {
  let origGetItem: typeof Storage.prototype.getItem;
  let origSetItem: typeof Storage.prototype.setItem;

  beforeEach(() => {
    origGetItem = Storage.prototype.getItem;
    origSetItem = Storage.prototype.setItem;
  });

  afterEach(() => {
    Storage.prototype.getItem = origGetItem;
    Storage.prototype.setItem = origSetItem;
  });

  it("hook works even when localStorage access throws on read", () => {
    Storage.prototype.getItem = vi.fn(() => {
      throw new Error("denied");
    }) as unknown as typeof Storage.prototype.getItem;
    const consoleWarn = vi.spyOn(console, "warn").mockImplementation(() => {});
    let result: ReturnType<typeof renderHook<unknown, unknown>> | null = null;
    expect(() => {
      result = renderHook(() => useAutonomousMode()) as unknown as typeof result;
    }).not.toThrow();
    expect(result).not.toBeNull();
    consoleWarn.mockRestore();
  });
});
