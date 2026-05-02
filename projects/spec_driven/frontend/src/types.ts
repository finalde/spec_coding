export type NodeKind = "file" | "folder" | "missing-folder";

export interface TreeNode {
  name: string;
  kind: NodeKind;
  path: string;
  present: boolean;
  children?: TreeNode[];
}

export interface SettingsSection {
  claude_md: TreeNode[];
  agents: TreeNode[];
  skills: TreeNode[];
}

export interface TreeResponse {
  settings: SettingsSection;
  projects: TreeNode[];
}

export interface FileResponse {
  path: string;
  extension: string;
  bytes: number;
  text: string;
}

export interface FileError {
  error: string;
  kind?: string;
}
