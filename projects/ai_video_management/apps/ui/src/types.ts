export type TreeNodeType = "section" | "directory" | "file" | "image" | "video" | "audio" | "actor";

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
  /** Only populated on `type === "actor"` leaves: relative path of the first face image inside the collapsed actor folder. */
  face_path?: string | null;
  /** Chinese (or otherwise human-friendly) label rendered in place of `name` when present. Used by `novels/{category}/{slug}/` to show 仙侠 / 凡人修仙传 instead of the pinyin slug. */
  display_name?: string;
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
