---
name: common__project-builder
description: Scaffold a new project in this monorepo following repo conventions. Use this whenever the user wants to add a new tool or project under `projects/` or `tools/`, initialize a new codebase component here, or asks for a standard project skeleton with README and requirements wiring.
---

# Common Project Builder

Scaffold new projects so they match this repository's monorepo conventions.

## Workflow

### 1. Gather the basics

Confirm:

- target path
- short purpose
- main class or module name
- known dependencies

### 2. Scaffold

Create the standard project layout:

- `main.py`
- `requirements.txt`
- `README.md`
- `libs/`

### 3. Keep the entry point thin

`main.py` should only do argument parsing and one call into `libs/`.

### 4. Document immediately

Update the README in the same pass so future sessions know:

- what the project does
- how to run it
- where the main logic lives

### 5. Register dependencies

Add the project-local requirements file to the root `requirements.txt`.
