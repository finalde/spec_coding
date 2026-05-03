import { afterEach, describe, expect, it } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { AUTONOMOUS_KEY, useAutonomousMode } from "../src/autonomousMode";

afterEach(() => {
  window.localStorage.clear();
});

describe("useAutonomousMode", () => {
  it("default false when localStorage empty", () => {
    const { result } = renderHook(() => useAutonomousMode());
    expect(result.current[0]).toBe(false);
  });

  it("returns true when storage value is 'true'", () => {
    window.localStorage.setItem(AUTONOMOUS_KEY, "true");
    const { result } = renderHook(() => useAutonomousMode());
    expect(result.current[0]).toBe(true);
  });

  it("setMode persists to localStorage", () => {
    const { result } = renderHook(() => useAutonomousMode());
    act(() => result.current[1](true));
    expect(window.localStorage.getItem(AUTONOMOUS_KEY)).toBe("true");
    act(() => result.current[1](false));
    expect(window.localStorage.getItem(AUTONOMOUS_KEY)).toBe("false");
  });

  it("re-renders both consumers when one calls setMode (in-process subscription)", () => {
    const a = renderHook(() => useAutonomousMode());
    const b = renderHook(() => useAutonomousMode());
    act(() => a.result.current[1](true));
    expect(a.result.current[0]).toBe(true);
    expect(b.result.current[0]).toBe(true);
  });

  it("subscribes to storage events for cross-tab sync", () => {
    const { result } = renderHook(() => useAutonomousMode());
    expect(result.current[0]).toBe(false);
    act(() => {
      window.dispatchEvent(
        new StorageEvent("storage", { key: AUTONOMOUS_KEY, newValue: "true" }),
      );
    });
    expect(result.current[0]).toBe(true);
  });
});
