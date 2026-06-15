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

/** Per follow-up 016: Prompt Lab overview + CRUD. */
export interface PromptLabLink {
  label: string;
  url: string;
}

export interface PromptLabEntry {
  path: string;
  name: string;
  title: string;
  meta: string;
  source: PromptLabLink | null;
  expected: PromptLabLink | null;
  prompt: string;
}

export interface PromptLabCategory {
  name: string;
  entries: PromptLabEntry[];
}

export interface PromptLabOverview {
  categories: PromptLabCategory[];
}

export interface PromptLabCreateRequest {
  category: string;
  filename: string;
  content: string;
}

export interface PromptLabFileResult {
  path: string;
  bytes: number;
  mtime: number;
  mtime_http: string;
}

export interface PromptLabDeleteResult {
  path: string;
  deleted: boolean;
}

export type PromptLabRunState =
  | "idle"
  | "running"
  | "succeeded"
  | "failed"
  | "stopped";

export interface PromptLabDecision {
  ts?: string;
  question?: string;
  decision?: string;
  why?: string;
}

export interface PromptLabRunFile {
  name: string;
  bytes: number;
}

export interface PromptLabRun {
  state: PromptLabRunState;
  run_id: string | null;
  started_at: string | null;
  ended_at: string | null;
  exit_code: number | null;
  output: string;
  decisions: PromptLabDecision[];
  files: PromptLabRunFile[];
}

export interface PromptLabExecuteResult {
  state: string;
  run_id: string;
  path: string;
}

/** Per follow-up 010: parent-level project delete. Widened to development by follow-up 011. */
export interface ProjectDeleteRequest {
  project_type: "ai_video" | "development";
  project_name: string;
}

export interface ProjectDeleteResult {
  project_type: string;
  project_name: string;
  deleted_paths: string[];
  not_found_paths: string[];
}
