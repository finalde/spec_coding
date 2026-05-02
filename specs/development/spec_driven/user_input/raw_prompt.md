# Raw prompt — spec_driven

Captured: 2026-05-02
Task type: development
Task name: spec_driven

---

> Build a spec-driven solution. We need an `agent_team` Claude agent team to help with spec-driven work.

> **High-level rules.** All spec-driven documents must be saved in a root-level folder called `specs`. Under `specs`, the layout is `specs/{task_type}/{task_name}/...`. `task_type` is an enum — could be `development`, `ai_video`, or other types. `task_name` is the project name for a development project.

> **First project: `spec_driven`.** It's a solution to facilitate the spec-driven workflow we're trying to create here.

> **High-level workflow.**
> 1. The user enters an initial prompt about the task; Claude revises it. Both raw and revised prompts go in a `user_input/` folder under `specs/development/spec_driven/`.
> 2. Next stage: interview questions and answers — saved in an `interview/` folder.
> 3. Use revised user input + interview Q&A to do research, save results in a `findings/` folder.
> 4. Use all the above to generate the spec, in a `final_specs/` subfolder.
> 5. Generate a validation strategy based on the final spec, save in a `validation/` folder.
> 6. Use specs to execute the plan and use validation artifacts to validate execution along the way in a streaming fashion — real-time, iterative feedback until execution is complete and there are no validation errors.

> **The `spec_driven` project provides readonly capability for:**
> 1. Claude settings, CLAUDE.md, shared context for all spec_driven projects.
> 2. A project-level view: left nav with two big sections — "Claude Settings & Shared Context" and "Projects" — under which `Projects/development/spec_driven/` shows the subfolders (user_input, interview, findings, final_specs, validation).

---

## Clarifications captured during intake

**Viewer stack:** FastAPI backend + React frontend. Single project with `backend/` and `frontend/` subfolders inside `projects/spec_driven/`.

**Viewer scope:** strictly readonly — view files in left nav, no write actions, no run controls. Just a markdown/file viewer.

**Agent team decomposition (3 manager roles only — let Claude do the rest directly):**
- `agent_team__interview_manager` — does NOT ask questions itself. Understands the use case, identifies probe categories, dynamically builds an interviewer team where each individual interviewer is good at asking questions in a certain category, and coordinates the team to ask multi-choice questions across all categories until the team agrees the use case is crystal clear and explicit.
- `agent_team__research_manager` — does NOT do research itself. Figures out which areas to research, always focused on business and use cases, dynamically builds a research team with multiple researchers, and coordinates them to do the best research and save results in a findings file.
- `agent_team__validation_manager` — builds a validation team. Validates the job from multiple levels: high-level acceptance criteria, BDD (behavior-driven design), unit tests / system tests at lower code level, etc. The team should have an opinion on the best strategy to validate the result generated from specs and ensure all issues are captured and fixed during the process.

**No specific agents for:**
- The prompt-revision step (Claude does it directly).
- The spec-compilation step (Claude takes revised input + interview + findings and generates the spec directly).
- The execution step (Claude uses spec + validation strategy to generate the actual project, validating along the way until done).

**Q&A UX:** the interview team should ask the user using a single-choice / multi-choice format, like Claude Code's planning mode (i.e., via the `AskUserQuestion` tool).
