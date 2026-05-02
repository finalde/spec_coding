const STORAGE_KEY = "spec_driven.sidebar.v1";

export interface SidebarState {
  expanded: Record<string, boolean>;
  lastSelectedPath: string | null;
}

const DEFAULT_STATE: SidebarState = { expanded: {}, lastSelectedPath: null };

export function loadSidebarState(): SidebarState {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return { ...DEFAULT_STATE };
    const parsed = JSON.parse(raw) as Partial<SidebarState>;
    return {
      expanded: parsed.expanded && typeof parsed.expanded === "object" ? parsed.expanded : {},
      lastSelectedPath:
        typeof parsed.lastSelectedPath === "string" ? parsed.lastSelectedPath : null,
    };
  } catch {
    return { ...DEFAULT_STATE };
  }
}

export function saveSidebarState(state: SidebarState): void {
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  } catch {
    // ignore quota / privacy errors
  }
}
