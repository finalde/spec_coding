from __future__ import annotations

from pathlib import Path
from typing import Any

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, FastAPI, Header, Query
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from apps.api.container import Container
from libs.application.add_promotion__command import AddPromotionCommand
from libs.application.build_regen_prompt__query import BuildRegenPromptQuery
from libs.application.create_prompt_lab_file__command import CreatePromptLabFileCommand
from libs.application.delete_project__command import DeleteProjectCommand
from libs.application.delete_prompt_lab_file__command import DeletePromptLabFileCommand
from libs.application.get_stages__query import GetStagesQuery
from libs.application.get_tree__query import GetTreeQuery
from libs.application.list_prompt_lab__query import ListPromptLabQuery
from libs.application.prompt_lab__cdto import (
    CreatePromptLabFileCdto,
    DeletePromptLabFileCdto,
)
from libs.application.promotion__cdto import AddPromotionCdto, RemovePromotionCdto
from libs.application.read_file__query import ReadFileQuery
from libs.application.remove_promotion__command import RemovePromotionCommand
from libs.application.write_file__cdto import WriteFileCdto
from libs.application.write_file__command import WriteFileCommand
from libs.domain.project__error import (
    InvalidProjectName,
    ProjectNotFound,
    SelfDeleteRefused,
    UnsupportedTaskType,
)
from libs.domain.prompt_lab__error import (
    PromptLabAlreadyRunning,
    PromptLabExecUnavailable,
    PromptLabFileExists,
    PromptLabFileNotFound,
    PromptLabPathRejected,
)
from libs.domain.promotion__error import PromotionPathRejected, StageFolderRejected
from libs.domain.regen_prompt__error import PromptTooLarge
from libs.infrastructure.prompt_lab__executor import PromptLabExecutor
from libs.infrastructure.prompt_lab__writer import PromptLabFileTooLarge
from libs.infrastructure.file__reader import (
    FileReader,
    FileTooLarge as ReadFileTooLarge,
    OutsideSandbox as ReadOutsideSandbox,
    UnsupportedExtension as ReadUnsupportedExtension,
)
from libs.infrastructure.file__writer import (
    FileTooLarge as WriteFileTooLarge,
    InvalidBodyEncoding,
    OutsideSandbox as WriteOutsideSandbox,
    StaleWrite,
    UnsupportedExtension as WriteUnsupportedExtension,
)
from libs.infrastructure.origin_host__middleware import OriginHostMiddleware


class FilePutBody(BaseModel):
    path: str
    content: str


class PromotePostBody(BaseModel):
    project_type: str
    project_name: str
    stage_folder: str
    source_file: str
    item_id: str
    item_text: str


class PromoteDeleteBody(BaseModel):
    project_type: str
    project_name: str
    stage_folder: str
    item_id: str


class RegenPromptBody(BaseModel):
    project_type: str
    project_name: str
    stages: list[str] = Field(default_factory=list)
    modules: dict[str, list[str]] = Field(default_factory=dict)
    autonomous: bool = False


class ProjectDeleteBody(BaseModel):
    project_type: str
    project_name: str


class PromptLabCreateBody(BaseModel):
    category: str
    filename: str
    content: str


class PromptLabDeleteBody(BaseModel):
    path: str


class PromptLabExecuteBody(BaseModel):
    path: str


router = APIRouter()


@router.get("/api/tree")
@inject
def get_tree(
    query: GetTreeQuery = Depends(Provide[Container.get_tree_query]),
) -> dict[str, Any]:
    return query.execute().to_payload()


@router.get("/api/stages")
@inject
def get_stages(
    project_type: str | None = Query(default=None),
    project_name: str | None = Query(default=None),
    query: GetStagesQuery = Depends(Provide[Container.get_stages_query]),
) -> dict[str, Any]:
    return query.execute().to_payload()


@router.get("/api/file")
@inject
def get_file(
    path: str = Query(...),
    query: ReadFileQuery = Depends(Provide[Container.read_file_query]),
) -> Response:
    try:
        qdto = query.execute(path)
    except ReadUnsupportedExtension:
        return JSONResponse(
            status_code=415,
            content={"detail": {"kind": "extension_not_allowed"}},
            headers={"X-Content-Type-Options": "nosniff"},
        )
    except ReadFileTooLarge:
        return JSONResponse(
            status_code=413,
            content={"detail": {"kind": "too_large"}},
            headers={"X-Content-Type-Options": "nosniff"},
        )
    except ReadOutsideSandbox:
        return JSONResponse(
            status_code=404,
            content={"detail": {"kind": "not_found"}},
            headers={"X-Content-Type-Options": "nosniff"},
        )
    headers = FileReader.security_headers(Path(qdto.path).name)
    return JSONResponse(status_code=200, content=qdto.to_payload(), headers=headers)


@router.put("/api/file")
@inject
def put_file(
    body: FilePutBody,
    if_unmodified_since: str | None = Header(default=None, alias="If-Unmodified-Since"),
    command: WriteFileCommand = Depends(Provide[Container.write_file_command]),
) -> Response:
    try:
        cdto = command.execute(
            WriteFileCdto(
                path=body.path,
                content=body.content,
                if_unmodified_since=if_unmodified_since,
            )
        )
    except WriteUnsupportedExtension:
        return JSONResponse(status_code=415, content={"detail": {"kind": "extension_not_allowed"}})
    except WriteFileTooLarge:
        return JSONResponse(status_code=413, content={"detail": {"kind": "too_large"}})
    except InvalidBodyEncoding:
        return JSONResponse(status_code=415, content={"detail": {"kind": "invalid_body_encoding"}})
    except StaleWrite as sw:
        return JSONResponse(
            status_code=409,
            content={"detail": {"kind": "stale_write", "current_mtime": sw.current_mtime}},
        )
    except WriteOutsideSandbox:
        return JSONResponse(status_code=404, content={"detail": {"kind": "not_found"}})
    return JSONResponse(status_code=200, content=cdto.to_payload())


@router.api_route("/api/file", methods=["PATCH", "DELETE"])
def file_method_not_allowed() -> Response:
    return JSONResponse(
        status_code=405,
        content={"detail": {"kind": "method_not_allowed"}},
        headers={"Allow": "GET, PUT"},
    )


@router.post("/api/regen-prompt")
@inject
def post_regen_prompt(
    body: RegenPromptBody,
    query: BuildRegenPromptQuery = Depends(Provide[Container.build_regen_prompt_query]),
) -> Response:
    try:
        qdto = query.execute(
            project_type=body.project_type,
            project_name=body.project_name,
            stages=body.stages,
            modules=body.modules,
            autonomous=body.autonomous,
        )
    except PromptTooLarge:
        return JSONResponse(status_code=413, content={"detail": {"kind": "too_large"}})
    return JSONResponse(status_code=200, content=qdto.to_payload())


@router.post("/api/promote")
@inject
def post_promote(
    body: PromotePostBody,
    command: AddPromotionCommand = Depends(Provide[Container.add_promotion_command]),
) -> Response:
    try:
        cdto = command.execute(
            AddPromotionCdto(
                project_type=body.project_type,
                project_name=body.project_name,
                stage_folder=body.stage_folder,
                source_file=body.source_file,
                item_id=body.item_id,
                item_text=body.item_text,
            )
        )
    except StageFolderRejected:
        return JSONResponse(status_code=400, content={"detail": {"kind": "stage_folder_rejected"}})
    except PromotionPathRejected:
        return JSONResponse(status_code=404, content={"detail": {"kind": "not_found"}})
    return JSONResponse(status_code=200, content=cdto.to_payload())


@router.delete("/api/promote")
@inject
def delete_promote(
    body: PromoteDeleteBody,
    command: RemovePromotionCommand = Depends(Provide[Container.remove_promotion_command]),
) -> Response:
    try:
        cdto = command.execute(
            RemovePromotionCdto(
                project_type=body.project_type,
                project_name=body.project_name,
                stage_folder=body.stage_folder,
                item_id=body.item_id,
            )
        )
    except StageFolderRejected:
        return JSONResponse(status_code=400, content={"detail": {"kind": "stage_folder_rejected"}})
    except PromotionPathRejected:
        return JSONResponse(status_code=404, content={"detail": {"kind": "not_found"}})
    return JSONResponse(status_code=200, content=cdto.to_payload())


@router.delete("/api/project")
@inject
def delete_project(
    body: ProjectDeleteBody,
    command: DeleteProjectCommand = Depends(Provide[Container.delete_project_command]),
) -> Response:
    try:
        cdto = command.execute(body.project_type, body.project_name)
    except UnsupportedTaskType:
        return JSONResponse(
            status_code=400,
            content={"detail": {"kind": "unsupported_task_type", "task_type": body.project_type}},
        )
    except InvalidProjectName:
        return JSONResponse(status_code=400, content={"detail": {"kind": "invalid_project_name"}})
    except SelfDeleteRefused:
        return JSONResponse(status_code=400, content={"detail": {"kind": "self_delete_refused"}})
    except ProjectNotFound:
        return JSONResponse(status_code=404, content={"detail": {"kind": "not_found"}})
    return JSONResponse(status_code=200, content=cdto.to_payload())


@router.get("/api/prompt-lab")
@inject
def get_prompt_lab(
    query: ListPromptLabQuery = Depends(Provide[Container.list_prompt_lab_query]),
) -> dict[str, Any]:
    return query.execute().to_payload()


@router.post("/api/prompt-lab/file")
@inject
def post_prompt_lab_file(
    body: PromptLabCreateBody,
    command: CreatePromptLabFileCommand = Depends(Provide[Container.create_prompt_lab_file_command]),
) -> Response:
    try:
        cdto = command.execute(
            CreatePromptLabFileCdto(
                category=body.category,
                filename=body.filename,
                content=body.content,
            )
        )
    except PromptLabFileExists:
        return JSONResponse(status_code=409, content={"detail": {"kind": "already_exists"}})
    except PromptLabFileTooLarge:
        return JSONResponse(status_code=413, content={"detail": {"kind": "too_large"}})
    except PromptLabPathRejected:
        return JSONResponse(status_code=400, content={"detail": {"kind": "path_rejected"}})
    return JSONResponse(status_code=200, content=cdto.to_payload())


@router.delete("/api/prompt-lab/file")
@inject
def delete_prompt_lab_file(
    body: PromptLabDeleteBody,
    command: DeletePromptLabFileCommand = Depends(Provide[Container.delete_prompt_lab_file_command]),
) -> Response:
    try:
        cdto = command.execute(DeletePromptLabFileCdto(path=body.path))
    except PromptLabFileNotFound:
        return JSONResponse(status_code=404, content={"detail": {"kind": "not_found"}})
    except PromptLabPathRejected:
        return JSONResponse(status_code=400, content={"detail": {"kind": "path_rejected"}})
    return JSONResponse(status_code=200, content=cdto.to_payload())


@router.post("/api/prompt-lab/execute")
@inject
def post_prompt_lab_execute(
    body: PromptLabExecuteBody,
    executor: PromptLabExecutor = Depends(Provide[Container.prompt_lab_executor]),
) -> Response:
    try:
        result = executor.execute(body.path)
    except PromptLabAlreadyRunning:
        return JSONResponse(status_code=409, content={"detail": {"kind": "already_running"}})
    except PromptLabExecUnavailable:
        return JSONResponse(status_code=503, content={"detail": {"kind": "exec_unavailable"}})
    except PromptLabFileNotFound:
        return JSONResponse(status_code=404, content={"detail": {"kind": "not_found"}})
    except PromptLabPathRejected:
        return JSONResponse(status_code=400, content={"detail": {"kind": "path_rejected"}})
    return JSONResponse(status_code=200, content=result)


@router.get("/api/prompt-lab/run")
@inject
def get_prompt_lab_run(
    path: str = Query(...),
    executor: PromptLabExecutor = Depends(Provide[Container.prompt_lab_executor]),
) -> Response:
    try:
        result = executor.status(path)
    except PromptLabFileNotFound:
        return JSONResponse(status_code=404, content={"detail": {"kind": "not_found"}})
    except PromptLabPathRejected:
        return JSONResponse(status_code=400, content={"detail": {"kind": "path_rejected"}})
    return JSONResponse(status_code=200, content=result)


@router.post("/api/prompt-lab/stop")
@inject
def post_prompt_lab_stop(
    body: PromptLabExecuteBody,
    executor: PromptLabExecutor = Depends(Provide[Container.prompt_lab_executor]),
) -> Response:
    try:
        result = executor.stop(body.path)
    except PromptLabFileNotFound:
        return JSONResponse(status_code=404, content={"detail": {"kind": "not_found"}})
    except PromptLabPathRejected:
        return JSONResponse(status_code=400, content={"detail": {"kind": "path_rejected"}})
    return JSONResponse(status_code=200, content=result)


def create_app(container: Container, serve_static: bool = True) -> FastAPI:
    app = FastAPI(title="spec_driven", openapi_url=None, docs_url=None, redoc_url=None)
    app.add_middleware(OriginHostMiddleware, bound=container.bound_origin())
    app.include_router(router)

    if serve_static:
        static_dir = Path(__file__).resolve().parent / "static"
        if static_dir.is_dir():
            app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")

    return app
