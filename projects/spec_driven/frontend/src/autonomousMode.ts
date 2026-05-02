const KEY = "spec_driven.autonomous_mode.v1";

export function loadAutonomous(): boolean {
  try {
    return window.localStorage.getItem(KEY) === "true";
  } catch {
    return false;
  }
}

export function saveAutonomous(value: boolean): void {
  try {
    window.localStorage.setItem(KEY, value ? "true" : "false");
    window.dispatchEvent(new CustomEvent(EVENT_NAME, { detail: { value } }));
  } catch {
    // localStorage unavailable; silently ignore
  }
}

const EVENT_NAME = "spec_driven:autonomous-mode-changed";

export function subscribeAutonomous(handler: (value: boolean) => void): () => void {
  const listener = (e: Event): void => {
    const detail = (e as CustomEvent<{ value: boolean }>).detail;
    if (detail) handler(detail.value);
  };
  window.addEventListener(EVENT_NAME, listener);
  return () => window.removeEventListener(EVENT_NAME, listener);
}
