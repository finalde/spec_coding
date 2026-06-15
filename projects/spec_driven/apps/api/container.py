from __future__ import annotations

from pathlib import Path

from dependency_injector import containers, providers

from libs.application.add_promotion__command import AddPromotionCommand
from libs.application.build_regen_prompt__query import BuildRegenPromptQuery
from libs.application.delete_project__command import DeleteProjectCommand
from libs.application.get_stages__query import GetStagesQuery
from libs.application.create_prompt_lab_file__command import CreatePromptLabFileCommand
from libs.application.delete_prompt_lab_file__command import DeletePromptLabFileCommand
from libs.application.get_tree__query import GetTreeQuery
from libs.application.list_prompt_lab__query import ListPromptLabQuery
from libs.application.read_file__query import ReadFileQuery
from libs.application.remove_promotion__command import RemovePromotionCommand
from libs.application.write_file__command import WriteFileCommand
from libs.common.exposed_tree import ExposedTree
from libs.common.repo_root import RepoRoot
from libs.common.safe_resolve import SafeResolver
from libs.infrastructure.audit__writer import AuditWriter
from libs.infrastructure.file__reader import FileReader
from libs.infrastructure.file__writer import FileWriter
from libs.infrastructure.origin_host__middleware import BoundOrigin
from libs.infrastructure.project_directory__writer import ProjectDirectoryWriter
from libs.infrastructure.prompt_lab__executor import PromptLabExecutor
from libs.infrastructure.prompt_lab__reader import PromptLabReader
from libs.infrastructure.prompt_lab__writer import PromptLabWriter
from libs.infrastructure.promotion__writer import PromotionWriter
from libs.infrastructure.tree__reader import TreeReader


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=["apps.api.routes"])

    repo_root_path: providers.Dependency[Path] = providers.Dependency()
    bound_origin: providers.Dependency[BoundOrigin] = providers.Dependency()

    exposed_tree: providers.Singleton[ExposedTree] = providers.Singleton(
        ExposedTree, repo_root=repo_root_path
    )
    safe_resolver: providers.Singleton[SafeResolver] = providers.Singleton(
        SafeResolver, root=repo_root_path
    )

    file_reader: providers.Singleton[FileReader] = providers.Singleton(
        FileReader, exposed=exposed_tree, resolver=safe_resolver
    )
    file_writer: providers.Singleton[FileWriter] = providers.Singleton(
        FileWriter, exposed=exposed_tree, resolver=safe_resolver
    )
    tree_reader: providers.Singleton[TreeReader] = providers.Singleton(
        TreeReader, exposed=exposed_tree
    )
    promotion_writer: providers.Singleton[PromotionWriter] = providers.Singleton(
        PromotionWriter, exposed=exposed_tree, resolver=safe_resolver
    )
    prompt_lab_reader: providers.Singleton[PromptLabReader] = providers.Singleton(
        PromptLabReader, exposed=exposed_tree
    )
    prompt_lab_writer: providers.Singleton[PromptLabWriter] = providers.Singleton(
        PromptLabWriter, exposed=exposed_tree, resolver=safe_resolver
    )
    prompt_lab_executor: providers.Singleton[PromptLabExecutor] = providers.Singleton(
        PromptLabExecutor, exposed=exposed_tree, resolver=safe_resolver
    )
    project_directory_writer: providers.Singleton[ProjectDirectoryWriter] = providers.Singleton(
        ProjectDirectoryWriter, repo_root=repo_root_path
    )
    audit_writer: providers.Singleton[AuditWriter] = providers.Singleton(
        AuditWriter, repo_root=repo_root_path
    )

    read_file_query: providers.Factory[ReadFileQuery] = providers.Factory(
        ReadFileQuery, reader=file_reader
    )
    write_file_command: providers.Factory[WriteFileCommand] = providers.Factory(
        WriteFileCommand, writer=file_writer
    )
    get_tree_query: providers.Factory[GetTreeQuery] = providers.Factory(
        GetTreeQuery, reader=tree_reader
    )
    get_stages_query: providers.Factory[GetStagesQuery] = providers.Factory(GetStagesQuery)
    add_promotion_command: providers.Factory[AddPromotionCommand] = providers.Factory(
        AddPromotionCommand, writer=promotion_writer
    )
    remove_promotion_command: providers.Factory[RemovePromotionCommand] = providers.Factory(
        RemovePromotionCommand, writer=promotion_writer
    )
    build_regen_prompt_query: providers.Factory[BuildRegenPromptQuery] = providers.Factory(
        BuildRegenPromptQuery, exposed=exposed_tree, resolver=safe_resolver
    )
    delete_project_command: providers.Factory[DeleteProjectCommand] = providers.Factory(
        DeleteProjectCommand, writer=project_directory_writer, audit=audit_writer
    )
    list_prompt_lab_query: providers.Factory[ListPromptLabQuery] = providers.Factory(
        ListPromptLabQuery, reader=prompt_lab_reader
    )
    create_prompt_lab_file_command: providers.Factory[CreatePromptLabFileCommand] = providers.Factory(
        CreatePromptLabFileCommand, writer=prompt_lab_writer
    )
    delete_prompt_lab_file_command: providers.Factory[DeletePromptLabFileCommand] = providers.Factory(
        DeletePromptLabFileCommand, writer=prompt_lab_writer
    )
