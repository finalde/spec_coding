from __future__ import annotations

from libs.application.delete_project__cdto import DeleteProjectCdto
from libs.infrastructure.audit__writer import AuditWriter
from libs.infrastructure.project_directory__writer import (
    ProjectDeleteDao,
    ProjectDirectoryWriter,
)


class DeleteProjectCommand:
    def __init__(self, writer: ProjectDirectoryWriter, audit: AuditWriter) -> None:
        self._writer = writer
        self._audit = audit

    def execute(self, project_type: str, project_name: str) -> DeleteProjectCdto:
        dao = self._writer.delete(project_type, project_name)
        try:
            self._audit.emit("project.deleted", dao.to_payload())
        except OSError:
            pass
        return _map_to_cdto(dao)


def _map_to_cdto(dao: ProjectDeleteDao) -> DeleteProjectCdto:
    return DeleteProjectCdto(
        project_type=dao.project_type,
        project_name=dao.project_name,
        deleted_paths=dao.deleted_paths,
        not_found_paths=dao.not_found_paths,
    )
