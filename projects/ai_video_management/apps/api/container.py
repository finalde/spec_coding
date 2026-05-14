from __future__ import annotations

from pathlib import Path

from dependency_injector import containers, providers

from libs.common.exposed_tree import ExposedTree
from libs.common.safe_resolve import SafeResolver
from libs.infrastructure.actor_pool__writer import ActorPool
from libs.infrastructure.casting__writer import Casting
from libs.infrastructure.downloads__importer import DownloadsImporter
from libs.infrastructure.file__reader import FileReader
from libs.infrastructure.file__writer import FileWriter
from libs.infrastructure.frame__extractor import FrameExtractor
from libs.infrastructure.media__archiver import MediaArchiver
from libs.infrastructure.media__renamer import MediaRenamer
from libs.infrastructure.origin_host__middleware import BoundOrigin
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
        media_renamer=media_renamer,
    )
    actor_pool: providers.Singleton[ActorPool] = providers.Singleton(
        ActorPool, exposed=exposed_tree, resolver=safe_resolver
    )
    casting: providers.Singleton[Casting] = providers.Singleton(
        Casting,
        exposed=exposed_tree,
        resolver=safe_resolver,
        media_renamer=media_renamer,
        actor_pool=actor_pool,
    )
