import subprocess
from dataclasses import dataclass


@dataclass(frozen=True)
class RunResult:
    stdout: str
    stderr: str
    returncode: int


class ClaudeRunner:
    def run(self, prompt: str) -> RunResult:
        proc = subprocess.run(
            ["claude", "--continue", "-p"],
            input=prompt,
            capture_output=True,
            text=True,
            check=False,
        )
        return RunResult(proc.stdout, proc.stderr, proc.returncode)
