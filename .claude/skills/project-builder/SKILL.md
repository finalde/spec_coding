---
name: project-builder
description: Scaffold a new project in this monorepo following all CLAUDE.md conventions — creates the folder structure, thin main.py entry point, libs/ module with typed class skeleton, README, and registers in root requirements.txt. Use this whenever the user wants to add a new project, create a tool, start something new in the repo, or says things like "let's build X", "add a new tool for Y", "scaffold a project called Z", "I want to create a new project here", or "initialize a new project". Trigger even if the user hasn't said the word "scaffold" — any intent to start a new codebase component in this monorepo belongs here.
---

# Project Builder

Scaffold a new project in this monorepo, following all conventions from CLAUDE.md.

## Step 0: Gather information

If the user provided a `spec.md` file, read it first — it likely contains the project name, purpose, and module structure. Use it to pre-fill answers and skip questions that are already answered.

Otherwise, ask these four questions together (they're quick, no need to split them up):

1. **Project path** — Should it live under `projects/` (general tools, experiments) or `tools/` (integrations, proxies, infrastructure)? What's the name? e.g. `projects/data_fetcher`
2. **Purpose** — What does this project do? (1-2 sentences, used verbatim in the README)
3. **Module name** — What should the main class inside `libs/` be called? e.g. `Fetcher`, `Analyzer`, `Processor`
4. **Dependencies** — Any known Python packages? (Fine to say none — easy to add later)

Confirm the project path before doing anything irreversible.

## Step 1: Run the scaffolder

```bash
make new-project PROJECT=<path>
```

This creates `<path>/`, a bare `<path>/main.py`, and `<path>/requirements.txt`. You'll overwrite `main.py` in Step 3.

## Step 2: Create libs/

Create `<path>/libs/__init__.py` — empty file, just marks it as a package.

Create `<path>/libs/<module_name>.py` with a typed skeleton class. The goal is to establish the interface contract — future readers (and Claude) should understand what the class does and how to call it without needing to read the README.

**This is scaffolding, not implementation.** Every method body must be `pass` — nothing else. No HTTP calls, no file I/O, no parsing logic, no validation, no print statements. The user will fill in the logic; your job is to define the shape so they have a solid starting point.

The skeleton should:
- Have a typed `__init__` with parameters that reflect how main.py will instantiate it
- Include 1-2 placeholder methods with correct type signatures and `pass` as the body — nothing more
- Use `str | None` union syntax, not `Optional[str]`
- Use `@dataclass(frozen=True)` only if it's purely a data container with no behavior

**Example** — a `log-analyzer` project with class `Analyzer`:
```python
class Analyzer:
    def __init__(self, log_path: str, verbose: bool = False) -> None:
        self.log_path = log_path
        self.verbose = verbose

    def parse(self) -> list[dict[str, str]]:
        pass

    def summarize(self) -> str:
        pass
```

Notice: no imports beyond what the type hints need, no logic inside any method, just `pass`. A skeleton with a real implementation inside it is not a skeleton — it's a complete module that bypassed the user's intent to write the code themselves.

If the user provided a detailed `spec.md`, use it to add more method signatures and docstrings that describe intent. Still `pass` bodies — spec.md informs the interface shape, not the implementation.

## Step 3: Write the thin entry point

Overwrite `<path>/main.py`. It should contain only: imports, argparse setup, and a single call into libs/. No business logic, no print statements, no data processing, no conditional branching based on results.

Line count naturally scales with argument count — 2 args gives ~15 lines, 5 args gives ~20 lines, both are fine. What matters is that the body is pure plumbing: wire args to class, call one method, done. If you find yourself writing anything after the single `runner.method()` call, that logic belongs in libs/ instead.

```python
import argparse

from libs.<module_name> import <ClassName>


def main() -> None:
    parser = argparse.ArgumentParser(description="<one-line description>")
    parser.add_argument("--input", required=True, help="<what this arg does>")
    args = parser.parse_args()

    runner = <ClassName>(args.input)
    runner.run()


if __name__ == "__main__":
    main()
```

Adjust arguments to match the class's `__init__` signature.

## Step 4: Write the README

Create `<path>/README.md`. A good README means someone can pick this up cold, understand what it does, and know where to start. Don't leave placeholder text.

```markdown
# <project name>

<one-line description from interview>

## Usage

\`\`\`bash
make run PROJECT=<path>
\`\`\`

Or directly:

\`\`\`bash
.venv/bin/python <path>/main.py --help
\`\`\`

## Project structure

\`\`\`
<path>/
├── main.py           # CLI entry point
├── requirements.txt  # project dependencies
└── libs/
    ├── __init__.py
    └── <module>.py   # <ClassName>: <one-line on what it does>
\`\`\`

## Development

Install dependencies:

\`\`\`bash
make sync-project PROJECT=<path>
\`\`\`
```

## Step 5: Register in root requirements.txt

Add this line to the root `requirements.txt`, grouped with the other `-r` includes:

```
-r <path>/requirements.txt
```

If the user mentioned specific dependencies, add them to `<path>/requirements.txt` now.

## Step 6: Confirm

List every file created with a one-line description:
- `<path>/main.py` — thin CLI entry point
- `<path>/requirements.txt` — project dependencies
- `<path>/libs/__init__.py` — package marker
- `<path>/libs/<module>.py` — skeleton class with typed interface
- `<path>/README.md` — project documentation
- root `requirements.txt` — updated to include this project

Then ask: "Anything you'd like to adjust — class name, method signatures, README content?"
