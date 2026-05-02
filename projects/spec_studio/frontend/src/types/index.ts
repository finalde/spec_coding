export type RootFolder = "projects" | "ai_videos";

export type Phase =
  | "interview"
  | "spec"
  | "research"
  | "adjustments"
  | "plan"
  | "execute"
  | "final_validate"
  | "done";

export type TaskStatus =
  | "created"
  | "interviewing"
  | "specifying"
  | "researching"
  | "adjusting"
  | "planning"
  | "executing"
  | "validating"
  | "passed"
  | "halted"
  | "failed";

export type ArtifactKind =
  | "qa"
  | "spec"
  | "adjustments"
  | "dossier"
  | "plan"
  | "findings_report"
  | "initial_prompt";

export type EditableArtifactKind = "qa" | "spec" | "plan" | "initial_prompt";

export type InputSourceKind =
  | "claude_md"
  | "skill_md"
  | "phase_manager_md"
  | "initial_prompt";

export type ModuleKey =
  | "input"
  | "interview"
  | "specs"
  | "findings"
  | "plan";

export interface TaskSummary {
  id: string;
  name: string;
  root_folder: RootFolder;
  current_phase: Phase;
  status: TaskStatus;
  created_at: string;
  updated_at: string;
}

export interface Task extends TaskSummary {
  initial_prompt: string;
  artifacts: Record<string, boolean>;
  last_run_ids: Record<string, string>;
}

export interface CreateTaskInput {
  name: string;
  root_folder: RootFolder;
  initial_prompt: string;
}

export interface InterviewAnswer {
  question_id: string;
  selected: string[];
  notes?: string | null;
}

export interface InterviewAnswers {
  round: number;
  answers: InterviewAnswer[];
}

export interface Adjustments {
  notes: string;
}

export interface Artifact {
  kind: ArtifactKind;
  path: string;
  exists: boolean;
  content: string | null;
  mime: string;
  sha256?: string | null;
}

export interface RunHandle {
  run_id: string;
  task_id: string;
  phase: Phase;
}

export interface StreamEvent {
  seq: number;
  ts: string;
  run_id: string;
  task_id: string;
  source: string;
  type: string;
  payload: Record<string, unknown>;
}

export interface InputSource {
  kind: InputSourceKind;
  path: string;
  content: string;
  editable: boolean;
  sha256: string;
  requires_confirm: boolean;
}

export interface InputBundle {
  task_id: string;
  sources: InputSource[];
}

export interface ArtifactSaveResult {
  path: string;
  sha256: string;
  bytes_written: number;
  backed_up: boolean;
  stale_etag: boolean;
}

export interface InterviewOption {
  key: string;
  text: string;
  picked: boolean;
  freeform_value?: string | null;
}

export interface InterviewQuestion {
  qid: string;
  perspective: string;
  text: string;
  kind: string;
  options: InterviewOption[];
  notes?: string | null;
}

export interface InterviewRound {
  number: number;
  questions: InterviewQuestion[];
}

export interface InterviewQA {
  task_id: string;
  initial_prompt_ref: string;
  rounds: InterviewRound[];
  open_questions: string[];
  sha256?: string | null;
}
