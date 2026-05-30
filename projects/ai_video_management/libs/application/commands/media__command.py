"""Media-aggregate commands: archive / unarchive / delete / hard_delete / rename.

Single MediaCommand class with five methods. The delete operation has a
cross-aggregate refuse-if-actor-assigned check (follow-up 043), so the
class takes a CastingRepository in addition to MediaArchiver + MediaRenamer.
"""
from __future__ import annotations

from libs.application.dtos.media__dto import (
    MediaHardDeleteCdto,
    MediaMoveCdto,
    RenameMediaResultCdto,
)
from libs.application.mappers.media__mapper import MediaMapper
from libs.domain.errors.actor__error import (
    ActorAlreadyAssignedError,
    InvalidActorIdError,
)
from libs.domain.errors.media__error import (
    AlreadyArchivedError,
    NotUnderDeletedError,
)
from libs.domain.repositories.casting__repository import CastingRepository
from libs.domain.value_objects.drama__valueobject import DramaPath
from libs.domain.value_objects.media__valueobject import (
    ArchiveState,
    MediaPath,
    classify_state,
)
from libs.infrastructure.writers.media__writer import MediaArchiver, MediaRenamer


class MediaCommand:
    def __init__(
        self,
        archiver: MediaArchiver,
        renamer: MediaRenamer,
        casting: CastingRepository,
    ) -> None:
        self._archiver = archiver
        self._renamer = renamer
        self._casting = casting

    def archive(self, rel_path: str) -> MediaMoveCdto:
        media = MediaPath(rel=rel_path)
        if classify_state(media) is ArchiveState.ARCHIVED:
            raise AlreadyArchivedError("file is already inside an archive/ folder")
        self._refuse_if_actor_assigned(media)
        return MediaMapper.move_to_cdto(self._archiver.archive(rel_path))

    def unarchive(self, rel_path: str) -> MediaMoveCdto:
        MediaPath(rel=rel_path)
        return MediaMapper.move_to_cdto(self._archiver.unarchive(rel_path))

    def delete(self, rel_path: str) -> MediaMoveCdto:
        """Soft-delete (move to ai_videos/_deleted/{path}). Refuses when
        the target is under _actors/ and that actor still has assignments
        (cross-aggregate rule, follow-up 043)."""
        media = MediaPath(rel=rel_path)
        self._refuse_if_actor_assigned(media)
        return MediaMapper.move_to_cdto(self._archiver.delete(rel_path))

    def hard_delete(self, rel_path: str) -> MediaHardDeleteCdto:
        media = MediaPath(rel=rel_path)
        if not media.is_under_deleted:
            raise NotUnderDeletedError("hard_delete only operates inside ai_videos/_deleted/")
        deleted_rel = self._archiver.hard_delete(rel_path)
        return MediaHardDeleteCdto(deleted_rel=deleted_rel)

    def rename(self, rel_drama_path: str) -> RenameMediaResultCdto:
        """Drama-scoped batch rename of image/video files to match their
        parent folder name."""
        DramaPath(rel=rel_drama_path)
        return MediaMapper.rename_to_cdto(
            self._renamer.rename_drama(
                rel_drama_path, excluded_folder_names=frozenset({"frames"})
            )
        )

    def _refuse_if_actor_assigned(self, media: MediaPath) -> None:
        actor_id = media.actor_id_if_under_actors
        if actor_id is None:
            return
        try:
            assignments = self._casting.find_assignments_for_actor(actor_id)
        except (InvalidActorIdError, OSError):
            return
        if assignments:
            raise ActorAlreadyAssignedError(actor_id=actor_id, assignments=assignments)
