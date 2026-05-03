"""UserPromptSubmit hook — spec-driven follow-up triage reminder.

When the user's prompt references a spec-driven project (either by mentioning
the literal phrase "spec[-_ ]driven", or by naming a project folder X for
which specs/<type>/X/ exists in the repo), inject a system-reminder telling
Claude to run CLAUDE.md's "Follow-up prompt handling" triage BEFORE making
any code edits.

Stdin: the standard UserPromptSubmit JSON payload from Claude Code.
Stdout: when matched, a JSON object with `hookSpecificOutput.additionalContext`;
otherwise, nothing (silent no-op so non-spec-driven prompts are unaffected).
"""

from __future__ import annotations

import json
import os
import re
import sys


REMINDER_TEMPLATE: str = (
    "This prompt references a spec-driven project (matched: {matched}). "
    "Per CLAUDE.md -> 'Follow-up prompt handling', BEFORE editing any code: "
    "(1) triage which project is impacted (ask the user if ambiguous); "
    "(2) persist abstracted intent at "
    "specs/{{type}}/{{name}}/user_input/follow_ups/NNN-{{YYYYMMDD-HHmmss}}-{{slug}}.md; "
    "(3) regenerate specs/{{type}}/{{name}}/user_input/revised_prompt.md "
    "(= raw_prompt.md + every follow-up); "
    "(4) walk downstream artifacts (interview/qa.md, findings/, final_specs/spec.md, "
    "validation/*, generated outputs under projects/{{name}}/) and surgically patch "
    "any conflict or gap; "
    "(5) append a changelog.md entry. The code change AND the follow-up persistence "
    "MUST both happen in the same turn -- never edit code without doing the triage."
)


def find_repo_root(start: str) -> str | None:
    cur = os.path.abspath(start)
    while True:
        if os.path.isdir(os.path.join(cur, ".claude")) and os.path.isdir(
            os.path.join(cur, "specs")
        ):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            return None
        cur = parent


def list_project_names(specs_root: str) -> list[str]:
    out: list[str] = []
    try:
        type_dirs = os.listdir(specs_root)
    except OSError:
        return out
    for type_name in type_dirs:
        type_dir = os.path.join(specs_root, type_name)
        if not os.path.isdir(type_dir):
            continue
        try:
            proj_dirs = os.listdir(type_dir)
        except OSError:
            continue
        for proj_name in proj_dirs:
            if os.path.isdir(os.path.join(type_dir, proj_name)):
                out.append(proj_name)
    return out


def detect_match(prompt: str, project_names: list[str]) -> str | None:
    prompt_lc = prompt.lower()
    if re.search(r"spec[-_ ]driven", prompt_lc):
        return "the literal phrase 'spec-driven'"
    for name in project_names:
        pattern = (
            r"(?:^|[^a-z0-9_])" + re.escape(name.lower()) + r"(?:[^a-z0-9_]|$)"
        )
        if re.search(pattern, prompt_lc):
            return f"the project name '{name}'"
    return None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0
    if not isinstance(payload, dict):
        return 0

    prompt = payload.get("prompt") or ""
    if not isinstance(prompt, str) or not prompt.strip():
        return 0

    cwd = payload.get("cwd") or os.getcwd()
    repo_root = find_repo_root(cwd)
    project_names: list[str] = []
    if repo_root is not None:
        project_names = list_project_names(os.path.join(repo_root, "specs"))

    matched = detect_match(prompt, project_names)
    if matched is None:
        return 0

    output = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": REMINDER_TEMPLATE.format(matched=matched),
        }
    }
    sys.stdout.write(json.dumps(output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
