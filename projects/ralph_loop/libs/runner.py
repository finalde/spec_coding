import subprocess
from dataclasses import dataclass


@dataclass(frozen=True)
class RunResult:
    stdout: str
    stderr: str
    returncode: int


class ClaudeRunner:
    def __init__(self, stream: bool = False) -> None:
        self._stream: bool = stream

    def run(self, prompt: str) -> RunResult:
        cmd: list[str] = ["claude", "--continue", "-p"]
        if not self._stream:
            proc = subprocess.run(cmd, input=prompt, capture_output=True, text=True, check=False)
            return RunResult(proc.stdout, proc.stderr, proc.returncode)

        proc = subprocess.Popen(
            cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        assert proc.stdin and proc.stdout and proc.stderr
        proc.stdin.write(prompt)
        proc.stdin.close()

        chunks: list[str] = []
        for line in proc.stdout:
            print(line, end="", flush=True)
            chunks.append(line)

        stderr: str = proc.stderr.read()
        proc.wait()
        return RunResult("".join(chunks), stderr, proc.returncode)
