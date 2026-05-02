from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class RootFolder(str, Enum):
    PROJECTS = "projects"
    AI_VIDEOS = "ai_videos"


class Phase(str, Enum):
    INTERVIEW = "interview"
    SPEC = "spec"
    RESEARCH = "research"
    ADJUSTMENTS = "adjustments"
    PLAN = "plan"
    EXECUTE = "execute"
    FINAL_VALIDATE = "final_validate"
    DONE = "done"


class TaskStatus(str, Enum):
    CREATED = "created"
    INTERVIEWING = "interviewing"
    SPECIFYING = "specifying"
    RESEARCHING = "researching"
    ADJUSTING = "adjusting"
    PLANNING = "planning"
    EXECUTING = "executing"
    VALIDATING = "validating"
    PASSED = "passed"
    HALTED = "halted"
    FAILED = "failed"


ArtifactKind = Literal[
    "qa",
    "spec",
    "adjustments",
    "dossier",
    "plan",
    "findings_report",
    "initial_prompt",
]


EditableArtifactKind = Literal[
    "qa",
    "spec",
    "plan",
    "initial_prompt",
]


class TaskSummary(BaseModel):
    id: str
    name: str
    root_folder: RootFolder
    current_phase: Phase
    status: TaskStatus
    created_at: str
    updated_at: str


class Task(TaskSummary):
    initial_prompt: str
    artifacts: dict[str, bool] = Field(default_factory=dict)
    last_run_ids: dict[str, str] = Field(default_factory=dict)


class CreateTask(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    root_folder: RootFolder
    initial_prompt: str = Field(min_length=1)

    @field_validator("name")
    @classmethod
    def slug_safe(cls, v: str) -> str:
        if not all(c.isalnum() or c in "_-" for c in v):
            raise ValueError("name must contain only [a-zA-Z0-9_-]")
        return v


class InterviewAnswer(BaseModel):
    question_id: str
    selected: list[str] = Field(default_factory=list)
    notes: str | None = None


class InterviewAnswers(BaseModel):
    round: int = Field(ge=1)
    answers: list[InterviewAnswer]


class Adjustments(BaseModel):
    notes: str


class Artifact(BaseModel):
    kind: ArtifactKind
    path: str
    exists: bool
    content: str | None = None
    mime: str = "text/markdown"
    sha256: str | None = None


class RunHandle(BaseModel):
    run_id: str
    task_id: str
    phase: Phase


class Event(BaseModel):
    seq: int
    ts: str
    run_id: str
    task_id: str
    source: str
    type: str
    payload: dict[str, Any] = Field(default_factory=dict)


# ── Editable input + artifact models ───────────────────────────────────────


InputSourceKind = Literal["claude_md", "skill_md", "phase_manager_md", "initial_prompt"]


class InputSource(BaseModel):
    kind: InputSourceKind
    path: str
    content: str
    editable: bool
    sha256: str
    requires_confirm: bool


class InputBundle(BaseModel):
    task_id: str
    sources: list[InputSource]


class ArtifactEditBody(BaseModel):
    content: str
    if_match: str | None = None


class RepoEditBody(BaseModel):
    content: str
    confirm: bool = False
    if_match: str | None = None


class ArtifactSaveResult(BaseModel):
    path: str
    sha256: str
    bytes_written: int
    backed_up: bool
    stale_etag: bool = False


# ── Interview Q&A typed model ──────────────────────────────────────────────


class InterviewOption(BaseModel):
    key: str
    text: str
    picked: bool = False
    freeform_value: str | None = None


class InterviewQuestion(BaseModel):
    qid: str
    perspective: str
    text: str
    kind: str = "single"
    options: list[InterviewOption] = Field(default_factory=list)
    notes: str | None = None


class InterviewRound(BaseModel):
    number: int = Field(ge=1)
    questions: list[InterviewQuestion] = Field(default_factory=list)


class InterviewQA(BaseModel):
    task_id: str
    initial_prompt_ref: str = "initial_prompt.md"
    rounds: list[InterviewRound] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)
    sha256: str | None = None
