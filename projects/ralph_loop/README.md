# ralph_loop

**ralph_loop** repeatedly sends a structured spec to a running Claude session
(`claude --continue`) until Claude's response contains a `<promise>` tag — or a maximum
number of iterations is reached.

The spec (`SPEC.yaml`) is a YAML file that defines a goal, one or more tasks, and
**verifiable acceptance criteria** for each task. Every criterion declares exactly how
Claude Code will check it: by running a shell command (script check) or by interpreting
a natural-language instruction (natural check).

---

## Table of contents

1. [How it works](#how-it-works)
2. [Prerequisites](#prerequisites)
3. [Setup](#setup)
4. [Writing your SPEC.yaml](#writing-your-specyaml)
5. [Schema reference](#schema-reference)
6. [Check types](#check-types)
7. [Running the loop](#running-the-loop)
8. [CLI reference](#cli-reference)
9. [Understanding the output](#understanding-the-output)
10. [Exit codes](#exit-codes)
11. [Troubleshooting](#troubleshooting)
12. [Project structure](#project-structure)

---

## How it works

```
┌─────────────────────────────────────────────────────────┐
│                      ralph_loop                         │
│                                                         │
│  Parse SPEC.yaml → render structured prompt             │
│       │                                                 │
│       ▼                                                 │
│  Send prompt ──► claude --continue -p                   │
│       │                                                 │
│       ▼                                                 │
│  Did response contain <promise>...</promise>?           │
│       │                                                 │
│    Yes ──► Print promise text, exit 0 (success)         │
│    No  ──► Increment counter                            │
│              │                                          │
│           Counter < max? ──► Loop back                  │
│           Counter = max  ──► Exit 1 (failure)           │
└─────────────────────────────────────────────────────────┘
```

The prompt rendered from your spec instructs Claude to work through each task, verify
every acceptance criterion, and emit `<promise>all tasks complete</promise>` only when
all criteria have been confirmed.

---

## Prerequisites

| Requirement | Why | How to check |
|---|---|---|
| Python 3.10+ | Runs the tool | `python3 --version` |
| `uv` | Creates the virtual environment | `uv --version` |
| Claude CLI (`claude`) | Actually runs your prompts | `claude --version` |
| An active Claude session | `--continue` resumes an existing session | `claude` (start one) |

> **What is an "active Claude session"?**
> The `claude --continue` flag tells the Claude CLI to resume the most recent conversation
> rather than starting a fresh one. You need to have started at least one `claude` session
> in your terminal before using ralph_loop. If you haven't, run `claude` once, type
> anything, and exit.

---

## Setup

Run all commands from the **repo root** (`spec_coding/`), not from inside
`projects/ralph_loop/`.

**Step 1 — Create the virtual environment** (only needed once per machine):

```bash
make venv
```

**Step 2 — Install ralph_loop's dependencies** (adds `pyyaml`):

```bash
make sync-project PROJECT=projects/ralph_loop
```

**Step 3 — Verify the setup:**

```bash
.venv/bin/python projects/ralph_loop/main.py --help
```

---

## Writing your SPEC.yaml

Create a `SPEC.yaml` file (default location: the directory you run the tool from).

### Annotated example

```yaml
goal: "Add a /health endpoint to the Flask API"

context: |
  The API is a small Flask app in app.py. It currently has no health check.
  We need a simple GET /health that returns {"status": "ok"} with HTTP 200.

instructions:
  - "Follow the existing code style in app.py"
  - "Do not introduce new dependencies"

# Optional: override the default max_iterations (10) for this spec
max_iterations: 5

tasks:
  - id: add-endpoint                         # unique identifier (required)
    title: "Add GET /health endpoint"        # short label (required)
    description: |                           # what to implement (required)
      Add a route at GET /health to app.py that returns a JSON response
      with status 200 and body {"status": "ok"}.
    instructions:                            # task-specific hints (optional)
      - "Use Flask's jsonify() for the response"
    acceptance_criteria:                     # at least one required
      - criterion: "pytest passes with no failures"
        check:
          type: script
          run: "pytest tests/ -v"            # exit code 0 = pass

      - criterion: "GET /health returns HTTP 200 with correct body"
        check:
          type: natural
          description: >
            Start the Flask app in test mode and send GET /health.
            Confirm the response status is 200 and the body is {"status": "ok"}.

  - id: write-test
    title: "Write a test for GET /health"
    description: |
      Add a test in tests/test_app.py that calls GET /health and
      asserts the response status and body.
    acceptance_criteria:
      - criterion: "A test for /health exists and pytest exits 0"
        check:
          type: script
          run: "pytest tests/test_app.py -v -k health"
```

---

## Schema reference

```
Spec
├── goal            str      required — what the spec achieves overall
├── context         str      optional — background for Claude
├── instructions    list     optional — global hints applied to all tasks
├── max_iterations  int      optional — overrides the CLI default (10)
└── tasks           list     required, ≥1 entry
    └── Task
        ├── id                  str    required, unique across the spec
        ├── title               str    required
        ├── description         str    required
        ├── instructions        list   optional — task-specific hints
        └── acceptance_criteria list   required, ≥1 entry
            └── Criterion
                ├── criterion   str    required — what must be true
                └── check       obj    required — how Claude verifies it
                    ├── ScriptCheck  — type: script
                    │   └── run: str — shell command; passes when exit code 0
                    └── NaturalCheck — type: natural
                        └── description: str — Claude interprets this
```

**Validation rules enforced at parse time:**

- `goal` must be non-empty
- `tasks` must have ≥1 entry
- Every `Task.id` must be non-empty and unique across the spec
- Every task must have ≥1 `acceptance_criteria`
- Every criterion must have a `check` object
- `check.type` must be `"script"` or `"natural"`
- `ScriptCheck.run` must be non-empty
- `NaturalCheck.description` must be non-empty

Any violation causes an immediate exit with a clear error message before Claude is called.

---

## Check types

### Script check

```yaml
check:
  type: script
  run: "pytest tests/ -v"
```

Claude runs the shell command. Exit code 0 = criterion satisfied. Non-zero = criterion
failed and Claude must keep working.

Use script checks for anything objectively measurable: test suites, linters, file
existence checks, HTTP status codes via curl, etc.

### Natural language check

```yaml
check:
  type: natural
  description: >
    Start the Flask app in test mode and send GET /health.
    Confirm the response status is 200 and the body is {"status": "ok"}.
```

Claude interprets the description and performs the steps itself. Use natural checks for
things that require judgment or multi-step interaction that is awkward to encode as a
single shell command.

---

## Running the loop

All commands run from the **repo root**.

### Using `make run` (recommended, uses default `SPEC.yaml`):

```bash
make run PROJECT=projects/ralph_loop
```

### Passing a custom spec file:

```bash
.venv/bin/python projects/ralph_loop/main.py path/to/my_spec.yaml
```

### Limiting the number of iterations:

```bash
.venv/bin/python projects/ralph_loop/main.py SPEC.yaml --max-iterations 5
```

Or with the short flag:

```bash
.venv/bin/python projects/ralph_loop/main.py SPEC.yaml -n 5
```

The CLI flag takes priority over `max_iterations` in the spec file.

### Enabling verbose (debug) output:

```bash
.venv/bin/python projects/ralph_loop/main.py SPEC.yaml --verbose
```

---

## CLI reference

```
usage: main.py [-h] [--max-iterations N] [--verbose] [spec_file]

positional arguments:
  spec_file              Path to the SPEC.yaml file.
                         Default: SPEC.yaml (in the current directory)

options:
  -h, --help             Show this help message and exit.

  --max-iterations N,    Maximum number of times to call Claude before giving up.
  -n N                   Priority: CLI flag > spec max_iterations > default (10)

  --verbose, -v          Show DEBUG log output, including a 200-character
                         preview of each Claude response.
                         Without this flag only INFO and ERROR messages are shown.
```

---

## Understanding the output

ralph_loop uses Python's standard logging. Each line follows this format:

```
LEVEL libs.loop: message
```

| Log line | What it means |
|---|---|
| `INFO libs.loop: Starting — spec='SPEC.yaml', goal='...', max_iterations=10` | The loop has started. Shows spec file, goal, and iteration limit. |
| `INFO libs.loop: Iteration 1/10 ...` | About to call Claude for the Nth time. |
| `WARNING libs.loop: claude exited 1` | Claude returned a non-zero exit code. The loop continues but something may be wrong. |
| `INFO libs.loop: Promise detected: 'all tasks complete' — done in 3 iteration(s).` | Success. |
| `DEBUG libs.loop: preview: 'I have reviewed...'` | Only visible with `--verbose`. First 200 chars of Claude's response. |
| `ERROR libs.loop: Max iterations (10) reached without a promise.` | The loop gave up. Claude never emitted `<promise>`. |
| `ERROR main: Spec file not found: SPEC.yaml` | The spec file path does not exist. |
| `ERROR main: Spec must have a non-empty 'goal'` | Validation error — fix your SPEC.yaml. |

---

## Exit codes

| Code | Meaning |
|---|---|
| `0` | A `<promise>` tag was detected. All tasks complete. |
| `1` | Something went wrong: spec validation failed, file not found, or max iterations reached. |

---

## Troubleshooting

### "Spec file not found"

```
ERROR main: Spec file not found: SPEC.yaml
```

ralph_loop looks for the file relative to the directory you run it from. Use an absolute
path or a path relative to your working directory:

```bash
.venv/bin/python projects/ralph_loop/main.py /absolute/path/to/SPEC.yaml
```

---

### Spec validation errors

Examples:

```
ERROR main: Spec must have a non-empty 'goal'
ERROR main: Task 'my-task' has no acceptance_criteria — every task must have at least one verifiable criterion
ERROR main: Criterion 'tests pass' has no 'check' — all criteria must be verifiable
ERROR main: Unknown check type 'shell' for criterion 'tests pass'. Must be 'script' or 'natural'.
ERROR main: Duplicate task id: 'add-endpoint'
```

All validation errors are reported before Claude is called. Fix the SPEC.yaml and retry.

---

### "claude exited 1" warning but the loop keeps going

```
WARNING libs.loop: claude exited 1
```

The Claude CLI returned an error. Common causes:

- No active Claude session (`claude --continue` needs a prior session). Fix: run `claude`
  once, send any message, then exit.
- The `claude` command is not on your `PATH`. Fix: check `which claude` or reinstall.

The loop does not stop on this warning — it treats the output as a normal iteration.

---

### Max iterations reached with no promise

```
ERROR libs.loop: Max iterations (10) reached without a promise.
```

Possible reasons:

1. **Claude is not completing all criteria.** Run with `--verbose` to read the responses.
2. **The iteration limit is too low.** Increase with `--max-iterations` or add
   `max_iterations` to the spec.
3. **A script check keeps failing.** Ensure the command runs correctly in your environment.

---

### "Virtualenv not found. Run: make venv"

```bash
make venv
make sync-project PROJECT=projects/ralph_loop
```

---

## Project structure

```
projects/ralph_loop/
├── README.md            ← you are here
├── requirements.txt     # pyyaml
├── SPEC.yaml            # default/example spec
├── main.py              # entry point: argument parsing + object construction only
└── libs/
    ├── __init__.py      # marks libs/ as a Python package
    ├── spec.py          # Spec, Task, Criterion, ScriptCheck, NaturalCheck — schema + validation
    ├── runner.py        # RunResult dataclass + ClaudeRunner — subprocess wrapper
    └── loop.py          # RalphLoop — orchestrates the iteration loop
```

**Class responsibilities:**

| Class | File | What it does |
|---|---|---|
| `Spec` | `spec.py` | Parses and validates SPEC.yaml; renders a structured prompt via `.to_prompt()` |
| `Task` | `spec.py` | Holds task fields; validates id and acceptance_criteria at parse time |
| `Criterion` | `spec.py` | Holds a criterion string and its associated `Check` object |
| `ScriptCheck` | `spec.py` | Shell command to run; passes when exit code is 0 |
| `NaturalCheck` | `spec.py` | Natural-language description Claude interprets and executes |
| `RunResult` | `runner.py` | Immutable dataclass: `stdout`, `stderr`, `returncode` from one Claude call |
| `ClaudeRunner` | `runner.py` | Runs `claude --continue -p` as a subprocess; returns a `RunResult` |
| `RalphLoop` | `loop.py` | Composes a `Spec` and `ClaudeRunner`; runs the iteration loop via `.run()` |
