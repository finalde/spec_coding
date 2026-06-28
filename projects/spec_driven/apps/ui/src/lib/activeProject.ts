import { TypedLocalStorage } from "../localStorage";

export interface ActiveProject {
  type: string;
  name: string;
}

const STORAGE_KEY = "spec_driven.active_project.v1";

const store = new TypedLocalStorage<string | null>(
  STORAGE_KEY,
  null,
  (v) => (v === null ? "" : v),
  (raw) => (raw === "" ? null : raw),
);

export function parseActiveProject(raw: string | null): ActiveProject | null {
  if (!raw) return null;
  const slash = raw.indexOf("/");
  if (slash <= 0 || slash === raw.length - 1) return null;
  const type = raw.slice(0, slash);
  const name = raw.slice(slash + 1);
  if (!type || !name || name.includes("/")) return null;
  return { type, name };
}

export function readActiveProject(): ActiveProject | null {
  return parseActiveProject(store.read());
}

export function writeActiveProject(project: ActiveProject | null): void {
  store.write(project === null ? null : `${project.type}/${project.name}`);
}

export function activeProjectStorageKey(): string {
  return STORAGE_KEY;
}
