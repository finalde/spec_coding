export type NodeType = "section" | "type" | "project" | "stage" | "file";

export interface TreeNode {
  name: string;
  path: string;
  type: NodeType;
  children: TreeNode[];
}

export interface FileResult {
  path: string;
  content: string;
  mtime: string;
  bytes: number;
  data_encoding?: "base64";
}

export interface WriteResult {
  path: string;
  bytes: number;
  mtime: string;
}

export interface Module {
  id: string;
  label: string;
  relative_path: string;
  description: string;
}

export interface Stage {
  id: string;
  label: string;
  folder: string;
  invocation: string;
  modules: Module[];
}

export interface RegenResult {
  prompt: string;
  warning: string | null;
  selected_stages_count: number;
  follow_ups_count: number;
  autonomous: boolean;
  bytes: number;
}

export type BrokenLinkCause =
  | "file not found"
  | "outside exposed tree"
  | "case mismatch"
  | "anchor not in document";
