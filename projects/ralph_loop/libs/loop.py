import logging
import re

from .runner import ClaudeRunner, RunResult
from .state import Prompt

log: logging.Logger = logging.getLogger(__name__)

DEFAULT_MAX_ITERATIONS: int = 10
_PROMISE_RE: re.Pattern[str] = re.compile(r"<promise>(.+?)</promise>", re.DOTALL)


class RalphLoop:
    def __init__(self, prompt: Prompt, max_iterations: int = DEFAULT_MAX_ITERATIONS) -> None:
        self._prompt: Prompt = prompt
        self._max_iterations: int = max_iterations
        self._runner: ClaudeRunner = ClaudeRunner()

    @staticmethod
    def detect_promise(text: str) -> str | None:
        m: re.Match[str] | None = _PROMISE_RE.search(text)
        return m.group(1).strip() if m else None

    def run(self) -> int:
        log.info("Starting — prompt=%r, max_iterations=%d", self._prompt.path, self._max_iterations)
        for i in range(1, self._max_iterations + 1):
            log.info("Iteration %d/%d ...", i, self._max_iterations)
            result: RunResult = self._runner.run(self._prompt.text)
            if result.returncode != 0:
                log.warning("claude exited %d", result.returncode)
            promise: str | None = self.detect_promise(result.stdout + result.stderr)
            if promise:
                log.info("Promise detected: %r — done in %d iteration(s).", promise, i)
                return 0
            preview: str = result.stdout[:200].replace("\n", " ").strip()
            log.debug("preview: %r", preview)
        log.error("Max iterations (%d) reached without a promise.", self._max_iterations)
        return 1
