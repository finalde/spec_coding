# ralph_loop

**ralph_loop** is a tool that repeatedly sends the same prompt to a running Claude session
(`claude --continue`) until Claude's response contains a `<promise>` tag — or a maximum
number of attempts is reached.

Think of it as a retry loop with a clear "I'm done" signal. Claude keeps working on a task,
and when it is satisfied with the result, it signals completion by wrapping its conclusion
in a `<promise>` tag.

---

## Table of contents

1. [How it works](#how-it-works)
2. [Prerequisites](#prerequisites)
3. [Setup](#setup)
4. [Writing your prompt file](#writing-your-prompt-file)
5. [Running the loop](#running-the-loop)
6. [CLI reference](#cli-reference)
7. [Understanding the output](#understanding-the-output)
8. [Exit codes](#exit-codes)
9. [Troubleshooting](#troubleshooting)
10. [Project structure](#project-structure)
11. [Keeping this README up to date](#keeping-this-readme-up-to-date)

---

## How it works

```
┌─────────────────────────────────────────────────────────┐
│                      ralph_loop                         │
│                                                         │
│  Read PROMPT.md                                         │
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

**The `<promise>` tag** is the contract. When your prompt instructs Claude to wrap its
final answer in `<promise>done</promise>` (or any text inside the tags), ralph_loop
detects it and stops immediately. Without this tag, ralph_loop keeps retrying.

---

## Prerequisites

Before you start, make sure you have these installed:

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

Run all commands from the **repo root** (the `spec_coding/` folder), not from inside
`projects/ralph_loop/`.

**Step 1 — Create the virtual environment** (only needed once per machine):

```bash
make venv
```

This creates a `.venv/` folder and installs all dependencies.

**Step 2 — Verify the setup:**

```bash
.venv/bin/python projects/ralph_loop/main.py --help
```

You should see the help message. If you get an error, revisit step 1.

---

## Writing your prompt file

ralph_loop reads its instructions from a plain text file (default: `PROMPT.md` in whatever
directory you run it from).

**The golden rule:** your prompt must tell Claude to wrap its final answer in a
`<promise>` tag. Without this instruction, Claude will never emit the tag, and
ralph_loop will run until it hits the iteration limit.

### Minimal example

Create a file called `PROMPT.md` anywhere you like:

```markdown
Review the code in `main.py` and fix any bugs you find.

When you are fully satisfied that all bugs are fixed and the code is correct,
respond with:

<promise>all bugs fixed</promise>
```

The text inside `<promise>...</promise>` can be anything — ralph_loop just captures and
displays it. Use it to carry a meaningful status message.

### A more detailed example

```markdown
You are reviewing a Python script for correctness and style.

Tasks:
1. Read `app.py`
2. Fix any syntax errors
3. Ensure all functions have docstrings
4. Run the tests and confirm they pass

Only respond with the promise tag once ALL four tasks are complete:

<promise>review complete — tests passing</promise>

If you cannot complete a task, describe the problem instead of emitting the promise tag.
```

> **Tip:** The clearer your stopping condition, the more reliably Claude will know
> when to emit `<promise>`. Vague prompts lead to more iterations.

---

## Running the loop

All commands are run from the **repo root**.

### Using `make run` (recommended)

```bash
make run PROJECT=projects/ralph_loop
```

This uses the default prompt file (`PROMPT.md` in the current directory).

### Passing a custom prompt file

`make run` does not forward extra arguments. Use the Python interpreter directly:

```bash
.venv/bin/python projects/ralph_loop/main.py path/to/my_prompt.md
```

### Limiting the number of iterations

By default the loop runs up to **10 times**. To change this:

```bash
.venv/bin/python projects/ralph_loop/main.py PROMPT.md --max-iterations 5
```

Or with the short flag:

```bash
.venv/bin/python projects/ralph_loop/main.py PROMPT.md -n 5
```

### Enabling verbose (debug) output

Add `--verbose` or `-v` to see the first 200 characters of each Claude response:

```bash
.venv/bin/python projects/ralph_loop/main.py PROMPT.md --verbose
```

---

## CLI reference

```
usage: main.py [-h] [--max-iterations N] [--verbose] [prompt_file]

positional arguments:
  prompt_file            Path to the prompt file.
                         Default: PROMPT.md (in the current directory)

options:
  -h, --help             Show this help message and exit.

  --max-iterations N,    Maximum number of times to call Claude before giving up.
  -n N                   Default: 10

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

Here is what each message means:

| Log line | What it means |
|---|---|
| `INFO libs.loop: Starting — prompt='PROMPT.md', max_iterations=10` | The loop has started. Shows which file and limit are in use. |
| `INFO libs.loop: Iteration 1/10 ...` | About to call Claude for the Nth time. |
| `WARNING libs.loop: claude exited 1` | Claude returned a non-zero exit code. The loop continues anyway, but something may be wrong with the Claude CLI or your session. |
| `INFO libs.loop: Promise detected: 'all bugs fixed' — done in 3 iteration(s).` | Success. The text inside `<promise>` is shown. |
| `DEBUG libs.loop: preview: 'I have reviewed...'` | Only visible with `--verbose`. First 200 chars of Claude's response. |
| `ERROR libs.loop: Max iterations (10) reached without a promise.` | The loop gave up. Claude never emitted a `<promise>` tag. |
| `ERROR libs.loop: Prompt file not found: PROMPT.md` | The prompt file path does not exist. |
| `ERROR libs.loop: Prompt file is empty: PROMPT.md` | The prompt file exists but has no content. |

---

## Exit codes

| Code | Meaning |
|---|---|
| `0` | A `<promise>` tag was detected. Claude finished the task. |
| `1` | Something went wrong: missing/empty prompt file, or max iterations reached without a promise. |

You can use exit codes in shell scripts:

```bash
.venv/bin/python projects/ralph_loop/main.py my_prompt.md && echo "Done!" || echo "Failed."
```

---

## Troubleshooting

### "Prompt file not found"

```
ERROR libs.loop: Prompt file not found: PROMPT.md
```

ralph_loop looks for the file relative to the directory you run it from, not relative to
the project folder. If you run from the repo root, `PROMPT.md` must be in the repo root.

Fix: use an absolute path or a path relative to where you run the command.

```bash
.venv/bin/python projects/ralph_loop/main.py /absolute/path/to/PROMPT.md
```

---

### "claude exited 1" warning but the loop keeps going

```
WARNING libs.loop: claude exited 1
```

The Claude CLI returned an error. Common causes:

- No active Claude session (`claude --continue` needs a prior session). Fix: run `claude`
  once, send any message, then exit.
- The `claude` command is not on your `PATH`. Fix: check `which claude` or reinstall the
  Claude CLI.

The loop does not stop on this warning — it treats the (possibly empty) output as a normal
iteration. This means if Claude keeps failing, you will exhaust all iterations.

---

### Max iterations reached with no promise

```
ERROR libs.loop: Max iterations (10) reached without a promise.
```

Claude ran the full loop but never emitted `<promise>...</promise>`. Possible reasons:

1. **The prompt does not instruct Claude to emit the tag.** Fix: add an explicit instruction
   like `"When done, respond with: <promise>done</promise>"`.
2. **Claude decided it could not complete the task** and described the problem instead.
   Fix: run with `--verbose` to read Claude's responses and adjust your prompt.
3. **The iteration limit is too low** for the task. Fix: increase it with `--max-iterations`.

---

### "Virtualenv not found. Run: make venv"

You skipped the setup step. Run:

```bash
make venv
```

---

## Project structure

```
projects/ralph_loop/
├── README.md            ← you are here
├── requirements.txt     # dependencies (stdlib only — nothing to install)
├── main.py              # entry point: argument parsing + object construction only
└── libs/
    ├── __init__.py      # marks libs/ as a Python package
    ├── state.py         # Prompt class — validates and holds the prompt file's content
    ├── runner.py        # RunResult dataclass + ClaudeRunner class — subprocess wrapper
    └── loop.py          # RalphLoop class — orchestrates the iteration loop
```

**Class responsibilities:**

| Class | File | What it does |
|---|---|---|
| `Prompt` | `state.py` | Validates the prompt file on construction; exposes `.path` and `.text` |
| `RunResult` | `runner.py` | Immutable dataclass holding `stdout`, `stderr`, and `returncode` from one Claude call |
| `ClaudeRunner` | `runner.py` | Runs `claude --continue -p` as a subprocess; returns a `RunResult` |
| `RalphLoop` | `loop.py` | Composes a `Prompt` and `ClaudeRunner`; runs the iteration loop via `.run()` |

**Why this structure?** Each class owns exactly one concern. `main.py` only constructs
objects and wires them together — it contains no logic. All real behaviour lives in
`libs/` so it can be imported and tested independently, without going through the CLI.

---

## Keeping this README up to date

> **For contributors and maintainers:**
>
> This README is the primary documentation for junior users. Every time a feature is
> added or changed, update this file in the same commit. Specifically:
>
> - **New CLI flag** → add a row to the [CLI reference](#cli-reference) table and a
>   usage example in [Running the loop](#running-the-loop).
> - **New log message** → add a row to the table in
>   [Understanding the output](#understanding-the-output).
> - **New exit code** → add a row to [Exit codes](#exit-codes).
> - **New error condition** → add a section to [Troubleshooting](#troubleshooting).
> - **New module in `libs/`** → add a row to the table in
>   [Project structure](#project-structure).
>
> Do not leave documentation as a follow-up task — it is part of the feature.
