export interface TreeNode {
  kind: "file" | "folder" | "missing-folder";
  name: string;
  path: string;
  children?: TreeNode[];
  present?: boolean;
}

export interface TreeResponse {
  settings: {
    claude_md: TreeNode[];
    agents: TreeNode[];
    skills: TreeNode[];
  };
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
