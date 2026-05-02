const KEY = "spec_driven.autonomous_mode.v1";
const SAME_TAB_EVENT = "spec_driven_autonomous_mode_changed";

const sameTabBus = new EventTarget();

export function loadAutonomous(): boolean {
  try {
    const raw = window.localStorage.getItem(KEY);
    if (raw === null) {
      return false;
    }
    const parsed = JSON.parse(raw) as unknown;
    return parsed === true;
  } catch {
    return false;
  }
}

export function saveAutonomous(value: boolean): void {
  try {
    window.localStorage.setItem(KEY, JSON.stringify(value));
  } catch {
    // ignore quota/disabled storage
  }
  try {
    sameTabBus.dispatchEvent(
      new CustomEvent<boolean>(SAME_TAB_EVENT, { detail: value }),
    );
  } catch {
    // ignore
  }
}

export function subscribeAutonomous(cb: (v: boolean) => void): () => void {
  const onStorage = (e: StorageEvent): void => {
    if (e.key !== KEY) {
      return;
    }
    if (e.newValue === null) {
      cb(false);
      return;
    }
    try {
      const parsed = JSON.parse(e.newValue) as unknown;
      cb(parsed === true);
    } catch {
      cb(false);
    }
  };
  const onSameTab = (e: Event): void => {
    const ce = e as CustomEvent<boolean>;
    cb(ce.detail === true);
  };
  window.addEventListener("storage", onStorage);
  sameTabBus.addEventListener(SAME_TAB_EVENT, onSameTab);
  return () => {
    window.removeEventListener("storage", onStorage);
    sameTabBus.removeEventListener(SAME_TAB_EVENT, onSameTab);
  };
}
