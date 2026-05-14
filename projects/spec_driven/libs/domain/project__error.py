from __future__ import annotations


class ProjectError(Exception):
    pass


class UnsupportedTaskType(ProjectError):
    def __init__(self, task_type: str) -> None:
        super().__init__(f"unsupported task_type for delete: {task_type}")
        self.task_type: str = task_type


class InvalidProjectName(ProjectError):
    pass


class ProjectNotFound(ProjectError):
    pass


class SelfDeleteRefused(ProjectError):
    def __init__(self) -> None:
        super().__init__(
            "refusing UI-driven self-delete of development/spec_driven (the running webapp)"
        )
