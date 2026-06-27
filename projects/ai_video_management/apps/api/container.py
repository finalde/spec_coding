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
from libs.application.commands.bgm__command import BgmCommand
from libs.application.commands.casting__command import CastingCommand
from libs.application.commands.character_video__command import CharacterVideoCommand
from libs.application.queries.character__query import CharacterQuery
from libs.application.commands.downloads__command import DownloadsCommand
from libs.application.commands.episode__command import EpisodeCommand
from libs.application.commands.episode_bgm__command import EpisodeBgmCommand
from libs.application.commands.episode_takes__command import EpisodeTakesCommand
from libs.application.commands.drama_takes__command import DramaTakesCommand
from libs.application.queries.drama_episodes__query import DramaEpisodesQuery
from libs.application.commands.episode_subtitle__command import EpisodeSubtitleCommand
from libs.application.commands.file__command import FileCommand
from libs.application.commands.frame__command import FrameCommand
from libs.application.commands.scene_plate__command import ScenePlateCommand
from libs.application.commands.intro_card__command import IntroCardCommand
from libs.application.commands.media__command import MediaCommand
from libs.application.commands.novel__command import NovelCommand
from libs.application.commands.perf_score__command import PerfScoreCommand
from libs.application.commands.production__command import ProductionCommand
from libs.application.commands.subtitle__command import SubtitleCommand
from libs.application.commands.subtitle_batch__command import SubtitleBatchCommand
from libs.application.commands.voice__command import VoiceCommand
from libs.application.queries.actor__query import ActorQuery
from libs.application.queries.bgm__query import BgmQuery
from libs.application.queries.casting__query import CastingQuery
from libs.application.queries.episode__query import EpisodeQuery
from libs.application.queries.episode_bgm__query import EpisodeBgmQuery
from libs.application.queries.file__query import FileQuery
from libs.application.commands.shot_performance__command import ShotPerformanceCommand
from libs.application.queries.perf_check__query import PerfCheckPromptQuery
from libs.application.queries.performance_candidate__query import PerformanceCandidateQuery
from libs.application.queries.shot_regen__query import ShotRegenPromptQuery
from libs.application.queries.media__query import MediaQuery
from libs.application.queries.novel__query import NovelQuery
from libs.application.queries.prompt__query import PromptQuery
from libs.application.queries.tree__query import TreeQuery
from libs.application.queries.voice__query import VoiceQuery
from libs.common.exposed_tree import ExposedTree
from libs.common.origin import BoundOrigin
from libs.common.safe_resolve import SafeResolver
from libs.infrastructure.clients.anthropic__client import AnthropicClient
from libs.infrastructure.readers.bgm_reference__reader import BgmReferenceReader
from libs.infrastructure.readers.file__reader import FileReader
from libs.infrastructure.readers.perf_check__reader import PerfCheckPromptReader
from libs.infrastructure.readers.performance_library__reader import PerformanceLibraryReader
from libs.infrastructure.readers.shot_regen__reader import ShotRegenPromptReader
from libs.infrastructure.readers.character__reader import CharacterReader
from libs.infrastructure.readers.tree__reader import TreeReader
from libs.infrastructure.writers.actor__writer import ActorPool
from libs.infrastructure.writers.bgm__writer import BgmPool
from libs.infrastructure.writers.casting__writer import Casting
from libs.infrastructure.writers.character_video__writer import (
    CharacterVideoTruncator,
    CharacterViewExtractor,
    ShotConcatBuilder,
)
from libs.infrastructure.writers.downloads__writer import DownloadsImporter
from libs.infrastructure.writers.episode__writer import EpisodeConcatBuilder
from libs.infrastructure.writers.episode_bgm__writer import EpisodeBgmManager
from libs.infrastructure.writers.episode_takes__writer import EpisodeTakesSelector
from libs.infrastructure.writers.drama_takes__writer import DramaTakesSelector
from libs.infrastructure.readers.drama_episodes__reader import DramaEpisodesReader
from libs.infrastructure.writers.episode_subtitle__writer import EpisodeSubtitleBurner
from libs.infrastructure.writers.file__writer import FileWriter
from libs.infrastructure.writers.frame__writer import FrameExtractor
from libs.infrastructure.writers.scene_plate__writer import ScenePlateExtractor
from libs.infrastructure.writers.shot_performance__writer import ShotPerformanceWriter
from libs.infrastructure.writers.intro_card__writer import IntroCardBurner
from libs.infrastructure.writers.subtitle__writer import SubtitleBurner
from libs.infrastructure.writers.subtitle_batch__writer import SubtitleBatchBurner
from libs.infrastructure.writers.media__writer import MediaArchiver, MediaRenamer
from libs.infrastructure.writers.novel__writer import NovelDownloader
from libs.infrastructure.writers.perf_score__writer import PerfScorer
from libs.infrastructure.writers.production__writer import ProductionExporter
from libs.infrastructure.writers.voice__writer import VoicePool


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
    scene_plate_extractor: providers.Singleton[ScenePlateExtractor] = providers.Singleton(
        ScenePlateExtractor, exposed=exposed_tree, resolver=safe_resolver
    )
    subtitle_burner: providers.Singleton[SubtitleBurner] = providers.Singleton(
        SubtitleBurner, exposed=exposed_tree, resolver=safe_resolver
    )
    intro_card_burner: providers.Singleton[IntroCardBurner] = providers.Singleton(
        IntroCardBurner, exposed=exposed_tree, resolver=safe_resolver
    )
    subtitle_batch_burner: providers.Singleton[SubtitleBatchBurner] = providers.Singleton(
        SubtitleBatchBurner,
        exposed=exposed_tree,
        resolver=safe_resolver,
        burner=subtitle_burner,
    )
    perf_scorer: providers.Singleton[PerfScorer] = providers.Singleton(
        PerfScorer, exposed=exposed_tree, resolver=safe_resolver
    )
    production_exporter: providers.Singleton[ProductionExporter] = providers.Singleton(
        ProductionExporter, exposed=exposed_tree, resolver=safe_resolver
    )
    shot_regen_reader: providers.Singleton[ShotRegenPromptReader] = providers.Singleton(
        ShotRegenPromptReader, exposed=exposed_tree, resolver=safe_resolver
    )
    perf_check_reader: providers.Singleton[PerfCheckPromptReader] = providers.Singleton(
        PerfCheckPromptReader, exposed=exposed_tree, resolver=safe_resolver
    )
    performance_library_reader: providers.Singleton[PerformanceLibraryReader] = providers.Singleton(
        PerformanceLibraryReader, root=repo_root_path
    )
    shot_performance_writer: providers.Singleton[ShotPerformanceWriter] = providers.Singleton(
        ShotPerformanceWriter,
        exposed=exposed_tree,
        resolver=safe_resolver,
        library=performance_library_reader,
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
    voice_pool: providers.Singleton[VoicePool] = providers.Singleton(
        VoicePool, exposed=exposed_tree, resolver=safe_resolver
    )
    bgm_pool: providers.Singleton[BgmPool] = providers.Singleton(
        BgmPool, exposed=exposed_tree, resolver=safe_resolver
    )
    bgm_reference_reader: providers.Singleton[BgmReferenceReader] = providers.Singleton(
        BgmReferenceReader, exposed=exposed_tree, resolver=safe_resolver
    )
    casting: providers.Singleton[Casting] = providers.Singleton(
        Casting,
        exposed=exposed_tree,
        resolver=safe_resolver,
        renamer=media_renamer,
        actor_pool=actor_pool,
        voice_pool=voice_pool,
    )
    character_video_truncator: providers.Singleton[CharacterVideoTruncator] = providers.Singleton(
        CharacterVideoTruncator, exposed=exposed_tree, resolver=safe_resolver
    )
    shot_concat_builder: providers.Singleton[ShotConcatBuilder] = providers.Singleton(
        ShotConcatBuilder, exposed=exposed_tree, resolver=safe_resolver
    )
    character_view_extractor: providers.Singleton[CharacterViewExtractor] = providers.Singleton(
        CharacterViewExtractor, exposed=exposed_tree, resolver=safe_resolver
    )
    character_reader: providers.Singleton[CharacterReader] = providers.Singleton(
        CharacterReader, exposed=exposed_tree, resolver=safe_resolver
    )
    episode_concat_builder: providers.Singleton[EpisodeConcatBuilder] = providers.Singleton(
        EpisodeConcatBuilder, exposed=exposed_tree, resolver=safe_resolver
    )
    episode_takes_selector: providers.Singleton[EpisodeTakesSelector] = providers.Singleton(
        EpisodeTakesSelector, exposed=exposed_tree, resolver=safe_resolver
    )
    drama_takes_selector: providers.Singleton[DramaTakesSelector] = providers.Singleton(
        DramaTakesSelector,
        exposed=exposed_tree,
        resolver=safe_resolver,
        episode_selector=episode_takes_selector,
    )
    drama_episodes_reader: providers.Singleton[DramaEpisodesReader] = providers.Singleton(
        DramaEpisodesReader, exposed=exposed_tree, resolver=safe_resolver
    )
    episode_subtitle_burner: providers.Singleton[EpisodeSubtitleBurner] = providers.Singleton(
        EpisodeSubtitleBurner,
        exposed=exposed_tree,
        resolver=safe_resolver,
        burner=subtitle_burner,
    )
    episode_bgm_manager: providers.Singleton[EpisodeBgmManager] = providers.Singleton(
        EpisodeBgmManager,
        exposed=exposed_tree,
        resolver=safe_resolver,
        bgm_pool=bgm_pool,
    )
    downloaded_novels_root: providers.Singleton[Path] = providers.Singleton(
        lambda root: root / "downloaded_novels", repo_root_path
    )
    my_novel_root: providers.Singleton[Path] = providers.Singleton(
        lambda root: root / "my_novel", repo_root_path
    )
    novel_downloader: providers.Singleton[NovelDownloader] = providers.Singleton(
        NovelDownloader, novels_root=downloaded_novels_root
    )
    # follow-up 117: from_env() returns None when ANTHROPIC_API_KEY is unset,
    # so the container builds whether or not LLM suggestions are configured.
    anthropic_client: providers.Singleton[AnthropicClient | None] = providers.Singleton(
        AnthropicClient.from_env
    )

    # --- Application-layer factories: one per aggregate Q/C -----------------
    actor_command: providers.Factory[ActorCommand] = providers.Factory(
        ActorCommand, pool=actor_pool, casting=casting
    )
    casting_command: providers.Factory[CastingCommand] = providers.Factory(
        CastingCommand, casting=casting
    )
    bgm_command: providers.Factory[BgmCommand] = providers.Factory(
        BgmCommand, pool=bgm_pool, references=bgm_reference_reader
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
    scene_plate_command: providers.Factory[ScenePlateCommand] = providers.Factory(
        ScenePlateCommand, extractor=scene_plate_extractor
    )
    subtitle_command: providers.Factory[SubtitleCommand] = providers.Factory(
        SubtitleCommand, burner=subtitle_burner
    )
    intro_card_command: providers.Factory[IntroCardCommand] = providers.Factory(
        IntroCardCommand, burner=intro_card_burner
    )
    subtitle_batch_command: providers.Factory[SubtitleBatchCommand] = providers.Factory(
        SubtitleBatchCommand, batch_burner=subtitle_batch_burner
    )
    perf_score_command: providers.Factory[PerfScoreCommand] = providers.Factory(
        PerfScoreCommand, scorer=perf_scorer
    )
    production_command: providers.Factory[ProductionCommand] = providers.Factory(
        ProductionCommand, exporter=production_exporter
    )
    shot_regen_query: providers.Factory[ShotRegenPromptQuery] = providers.Factory(
        ShotRegenPromptQuery, reader=shot_regen_reader
    )
    perf_check_query: providers.Factory[PerfCheckPromptQuery] = providers.Factory(
        PerfCheckPromptQuery, reader=perf_check_reader
    )
    performance_candidate_query: providers.Factory[PerformanceCandidateQuery] = providers.Factory(
        PerformanceCandidateQuery,
        reader=performance_library_reader,
        resolver=safe_resolver,
    )
    shot_performance_command: providers.Factory[ShotPerformanceCommand] = providers.Factory(
        ShotPerformanceCommand, writer=shot_performance_writer
    )
    downloads_command: providers.Factory[DownloadsCommand] = providers.Factory(
        DownloadsCommand, importer=downloads_importer
    )
    character_video_command: providers.Factory[CharacterVideoCommand] = providers.Factory(
        CharacterVideoCommand,
        truncator=character_video_truncator,
        builder=shot_concat_builder,
        extractor=character_view_extractor,
    )
    character_query: providers.Factory[CharacterQuery] = providers.Factory(
        CharacterQuery, reader=character_reader
    )
    episode_command: providers.Factory[EpisodeCommand] = providers.Factory(
        EpisodeCommand, builder=episode_concat_builder
    )
    episode_takes_command: providers.Factory[EpisodeTakesCommand] = providers.Factory(
        EpisodeTakesCommand, selector=episode_takes_selector
    )
    drama_takes_command: providers.Factory[DramaTakesCommand] = providers.Factory(
        DramaTakesCommand, selector=drama_takes_selector
    )
    drama_episodes_query: providers.Factory[DramaEpisodesQuery] = providers.Factory(
        DramaEpisodesQuery, reader=drama_episodes_reader
    )
    episode_subtitle_command: providers.Factory[EpisodeSubtitleCommand] = providers.Factory(
        EpisodeSubtitleCommand, burner=episode_subtitle_burner
    )
    episode_query: providers.Factory[EpisodeQuery] = providers.Factory(
        EpisodeQuery, builder=episode_concat_builder
    )
    episode_bgm_command: providers.Factory[EpisodeBgmCommand] = providers.Factory(
        EpisodeBgmCommand, manager=episode_bgm_manager
    )
    episode_bgm_query: providers.Factory[EpisodeBgmQuery] = providers.Factory(
        EpisodeBgmQuery, manager=episode_bgm_manager
    )

    actor_query: providers.Factory[ActorQuery] = providers.Factory(
        ActorQuery, pool=actor_pool, casting=casting
    )
    bgm_query: providers.Factory[BgmQuery] = providers.Factory(
        BgmQuery, pool=bgm_pool, references=bgm_reference_reader
    )
    voice_command: providers.Factory[VoiceCommand] = providers.Factory(
        VoiceCommand, pool=voice_pool, casting=casting
    )
    voice_query: providers.Factory[VoiceQuery] = providers.Factory(
        VoiceQuery, pool=voice_pool, casting=casting
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
    novel_command: providers.Factory[NovelCommand] = providers.Factory(
        NovelCommand, downloader=novel_downloader
    )
    novel_query: providers.Factory[NovelQuery] = providers.Factory(
        NovelQuery, novels_root=downloaded_novels_root
    )
    prompt_query: providers.Factory[PromptQuery] = providers.Factory(
        PromptQuery, client=anthropic_client
    )
