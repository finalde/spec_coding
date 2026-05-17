"""DI wiring for the ai_video_management API.

Per follow-ups 051 + 060 + 061: route handlers receive aggregate-level
application Query / Command instances (one Factory per aggregate). Each
aggregate class exposes one method per operation. 12 Factories cover all
19 endpoints. The infrastructure Readers / Writers / Clients are
Singleton providers feeding into those Factories. The route layer does
NOT import infrastructure classes — see apps/api/routes/.

Per follow-up 062: routes split into apps/api/routes/{aggregate}__route.py.
`wiring_config` uses `packages=` so every per-aggregate route module's
@inject decorators bind automatically.
"""
from __future__ import annotations

from pathlib import Path

from dependency_injector import containers, providers

from libs.application.commands.actor__command import ActorCommand
from libs.application.commands.casting__command import CastingCommand
from libs.application.commands.character_video__command import CharacterVideoCommand
from libs.application.commands.downloads__command import DownloadsCommand
from libs.application.commands.file__command import FileCommand
from libs.application.commands.frame__command import FrameCommand
from libs.application.commands.media__command import MediaCommand
from libs.application.queries.actor__query import ActorQuery
from libs.application.queries.casting__query import CastingQuery
from libs.application.queries.file__query import FileQuery
from libs.application.queries.media__query import MediaQuery
from libs.application.queries.tree__query import TreeQuery
from libs.common.exposed_tree import ExposedTree
from libs.common.origin import BoundOrigin
from libs.common.safe_resolve import SafeResolver
from libs.infrastructure.readers.file__reader import FileReader
from libs.infrastructure.readers.tree__reader import TreeReader
from libs.infrastructure.writers.actor__writer import ActorPool
from libs.infrastructure.writers.casting__writer import Casting
from libs.infrastructure.writers.character_video__writer import (
    CharacterVideoTruncator,
    ShotConcatBuilder,
)
from libs.infrastructure.writers.downloads__writer import DownloadsImporter
from libs.infrastructure.writers.file__writer import FileWriter
from libs.infrastructure.writers.frame__writer import FrameExtractor
from libs.infrastructure.writers.media__writer import MediaArchiver, MediaRenamer


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=["apps.api.routes"])

    repo_root_path: providers.Dependency[Path] = providers.Dependency()
    bound_origin: providers.Dependency[BoundOrigin] = providers.Dependency()

    # --- Infrastructure singletons -----------------------------------------
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
    media_renamer: providers.Singleton[MediaRenamer] = providers.Singleton(
        MediaRenamer, exposed=exposed_tree, resolver=safe_resolver
    )
    media_archiver: providers.Singleton[MediaArchiver] = providers.Singleton(
        MediaArchiver, exposed=exposed_tree, resolver=safe_resolver
    )
    frame_extractor: providers.Singleton[FrameExtractor] = providers.Singleton(
        FrameExtractor, exposed=exposed_tree, resolver=safe_resolver
    )
    downloads_importer: providers.Singleton[DownloadsImporter] = providers.Singleton(
        DownloadsImporter,
        exposed=exposed_tree,
        resolver=safe_resolver,
        renamer=media_renamer,
    )
    actor_pool: providers.Singleton[ActorPool] = providers.Singleton(
        ActorPool, exposed=exposed_tree, resolver=safe_resolver
    )
    casting: providers.Singleton[Casting] = providers.Singleton(
        Casting,
        exposed=exposed_tree,
        resolver=safe_resolver,
        renamer=media_renamer,
        actor_pool=actor_pool,
    )
    character_video_truncator: providers.Singleton[CharacterVideoTruncator] = providers.Singleton(
        CharacterVideoTruncator, exposed=exposed_tree, resolver=safe_resolver
    )
    shot_concat_builder: providers.Singleton[ShotConcatBuilder] = providers.Singleton(
        ShotConcatBuilder, exposed=exposed_tree, resolver=safe_resolver
    )

    # --- Application-layer factories: one per aggregate Q/C -----------------
    actor_command: providers.Factory[ActorCommand] = providers.Factory(
        ActorCommand, pool=actor_pool, casting=casting
    )
    casting_command: providers.Factory[CastingCommand] = providers.Factory(
        CastingCommand, casting=casting
    )
    media_command: providers.Factory[MediaCommand] = providers.Factory(
        MediaCommand, archiver=media_archiver, renamer=media_renamer, casting=casting
    )
    file_command: providers.Factory[FileCommand] = providers.Factory(
        FileCommand, writer=file_writer
    )
    frame_command: providers.Factory[FrameCommand] = providers.Factory(
        FrameCommand, extractor=frame_extractor
    )
    downloads_command: providers.Factory[DownloadsCommand] = providers.Factory(
        DownloadsCommand, importer=downloads_importer
    )
    character_video_command: providers.Factory[CharacterVideoCommand] = providers.Factory(
        CharacterVideoCommand,
        truncator=character_video_truncator,
        builder=shot_concat_builder,
    )

    actor_query: providers.Factory[ActorQuery] = providers.Factory(
        ActorQuery, pool=actor_pool, casting=casting
    )
    casting_query: providers.Factory[CastingQuery] = providers.Factory(
        CastingQuery, casting=casting
    )
    media_query: providers.Factory[MediaQuery] = providers.Factory(
        MediaQuery, exposed=exposed_tree, resolver=safe_resolver
    )
    file_query: providers.Factory[FileQuery] = providers.Factory(
        FileQuery, reader=file_reader
    )
    tree_query: providers.Factory[TreeQuery] = providers.Factory(
        TreeQuery, reader=tree_reader
    )
