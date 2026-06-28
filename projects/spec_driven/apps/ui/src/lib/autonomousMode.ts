import { useCallback, useEffect, useState } from "react";

export const AUTONOMOUS_MODE_STORAGE_KEY = "spec_driven.autonomous_mode.v1";

function readStored(): boolean {
  if (typeof window === "undefined" || !window.localStorage) return false;
  try {
    const raw = window.localStorage.getItem(AUTONOMOUS_MODE_STORAGE_KEY);
    if (raw === "true") return true;
    return false;
  } catch (err) {
    if (typeof console !== "undefined") console.warn(err);
    return false;
  }
}

function writeStored(value: boolean): void {
  if (typeof window === "undefined" || !window.localStorage) return;
  try {
    window.localStorage.setItem(AUTONOMOUS_MODE_STORAGE_KEY, value ? "true" : "false");
  } catch (err) {
    if (typeof console !== "undefined") console.warn(err);
  }
}

export function useAutonomousMode(): [boolean, (value: boolean) => void] {
  const [value, setValue] = useState<boolean>(() => readStored());

  useEffect(() => {
    if (typeof window === "undefined") return;
    const handler = (event: StorageEvent): void => {
      if (event.key !== AUTONOMOUS_MODE_STORAGE_KEY) return;
      if (event.newValue === null) setValue(false);
      else setValue(event.newValue === "true");
    };
    window.addEventListener("storage", handler);
    return () => {
      window.removeEventListener("storage", handler);
    };
  }, []);

  const update = useCallback((next: boolean) => {
    writeStored(next);
    setValue(next);
  }, []);

  return [value, update];
}
