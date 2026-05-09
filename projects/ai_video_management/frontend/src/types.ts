export type TreeNodeType = "section" | "directory" | "file" | "image";

export interface ProjectMeta {
  sub_type: "novel" | "short" | null;
  shot_count: number | null;
  episode_count: number | null;
}

export interface TreeNode {
  type: TreeNodeType;
  name: string;
  path: string;
  children?: TreeNode[];
  /** Only populated on `ai_videos/{name}/` directory nodes. */
  project_meta?: ProjectMeta | null;
}

export interface FileResult {
  path: string;
  content: string;
  encoding: string;
  bytes: number;
  mtime: number;
  mtime_http: string;
}

export interface WriteResult {
  path: string;
  bytes: number;
  mtime: number;
  mtime_http: string;
}

export interface ApiErrorDetail {
  kind: string;
  [key: string]: unknown;
}

export class ApiError extends Error {
  readonly status: number;
  readonly detail: ApiErrorDetail | null;

  constructor(status: number, message: string, detail: ApiErrorDetail | null) {
    super(message);
    this.status = status;
    this.detail = detail;
  }
}
