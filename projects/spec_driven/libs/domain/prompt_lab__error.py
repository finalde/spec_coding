from __future__ import annotations


class PromptLabPathRejected(Exception):
    pass


class PromptLabFileExists(Exception):
    pass


class PromptLabFileNotFound(Exception):
    pass


class PromptLabAlreadyRunning(Exception):
    pass


class PromptLabExecUnavailable(Exception):
    pass
