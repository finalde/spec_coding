const KEY = "spec_driven.sidebar.v1";

export interface SidebarState {
  expanded: Record<string, boolean>;
  lastSelectedPath: string | null;
}

const DEFAULT_STATE: SidebarState = {
  expanded: {},
  lastSelectedPath: null,
};

export function loadSidebarState(): SidebarState {
  try {
    const raw = window.localStorage.getItem(KEY);
    if (raw === null) {
      return { expanded: {}, lastSelectedPath: null };
    }
    const parsed = JSON.parse(raw) as unknown;
    if (
      parsed === null ||
      typeof parsed !== "object" ||
      Array.isArray(parsed)
    ) {
      return { expanded: {}, lastSelectedPath: null };
    }
    const obj = parsed as Record<string, unknown>;
    const expandedRaw = obj.expanded;
    const lastRaw = obj.lastSelectedPath;
    const expanded: Record<string, boolean> = {};
    if (expandedRaw && typeof expandedRaw === "object" && !Array.isArray(expandedRaw)) {
      for (const [k, v] of Object.entries(expandedRaw as Record<string, unknown>)) {
        if (typeof v === "boolean") {
          expanded[k] = v;
        }
      }
    }
    const lastSelectedPath =
      typeof lastRaw === "string" ? lastRaw : null;
    return { expanded, lastSelectedPath };
  } catch {
    return { expanded: {}, lastSelectedPath: null };
  }
}

export function saveSidebarState(state: SidebarState): void {
  try {
    window.localStorage.setItem(KEY, JSON.stringify(state));
  } catch {
    // localStorage unavailable; intentional no-op
  }
}

export const _DEFAULT_SIDEBAR_STATE: SidebarState = DEFAULT_STATE;
