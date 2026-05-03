import { useEffect, useState } from "react";
import { readLocal, writeLocal } from "./localStorage";

export const AUTONOMOUS_KEY = "spec_driven.autonomous_mode.v1";

type Listener = (value: boolean) => void;
const listeners = new Set<Listener>();

function readMode(): boolean {
  const v = readLocal(AUTONOMOUS_KEY);
  return v === "true";
}

function writeMode(v: boolean): void {
  writeLocal(AUTONOMOUS_KEY, v ? "true" : "false");
  for (const l of listeners) l(v);
}

export function useAutonomousMode(): [boolean, (v: boolean) => void] {
  const [mode, setModeState] = useState<boolean>(readMode);

  useEffect(() => {
    const onStorage = (e: StorageEvent) => {
      if (e.key === AUTONOMOUS_KEY) {
        setModeState(e.newValue === "true");
      }
    };
    const onLocal: Listener = (v) => setModeState(v);
    window.addEventListener("storage", onStorage);
    listeners.add(onLocal);
    return () => {
      window.removeEventListener("storage", onStorage);
      listeners.delete(onLocal);
    };
  }, []);

  const setMode = (v: boolean) => {
    writeMode(v);
    setModeState(v);
  };

  return [mode, setMode];
}
