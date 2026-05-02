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
    skills: TreeNode[];
    playbooks?: TreeNode[];
    agent_refs?: TreeNode[];
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

export interface Pin {
  pin_id: string;
  location: string;
  body: string;
}

export interface PromotionsResponse {
  stage_path: string;
  pins: Pin[];
}
