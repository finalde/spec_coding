export type TreeNodeType = "section" | "directory" | "file";

export interface TreeNode {
  type: TreeNodeType;
  name: string;
  path: string;
  children?: TreeNode[];
}

export interface FileResult {
  path: string;
  content: string;
  mtime: string;
  bytes: number;
}

export interface WriteResult {
  bytes: number;
  mtime: string;
}

export interface StaleWriteDetail {
  kind: "stale_write";
  current_mtime: string;
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

export interface StageModule {
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
  modules: StageModule[];
}

export interface RegenWarning {
  kind: string;
  bytes: number;
  soft_limit: number;
}

export interface RegenResult {
  prompt: string;
  warning: RegenWarning | null;
  selected_stages_count: number;
  follow_ups_count: number;
  autonomous: boolean;
  bytes: number;
}

export interface PromoteRequest {
  project_type: string;
  project_name: string;
  stage_folder: "interview" | "findings" | "final_specs" | "validation";
  source_file: string;
  item_id: string;
  item_text: string;
}

export interface UnpromoteRequest {
  project_type: string;
  project_name: string;
  stage_folder: "interview" | "findings" | "final_specs" | "validation";
  item_id: string;
}

export interface PromoteResult {
  status: string;
  item_id: string;
}

export interface RegenRequest {
  project_type: string;
  project_name: string;
  stages: string[];
  modules: Record<string, string[]>;
  autonomous: boolean;
}
