"""Named domain errors for the Bgm aggregate. Application layer catches
these and maps to transport-layer error shapes; infrastructure raises them
directly (mirrors actor / voice follow-up 114). Generic exceptions
(ValueError, OSError) are NOT used for domain violations — every invariant
breach is a named class."""
from __future__ import annotations


class BgmDomainError(Exception):
    """Base for all Bgm-aggregate domain errors."""


class InvalidBgmAttributeError(BgmDomainError):
    """An attribute (category / mood / bpm / duration / loopable / intensity /
    instruments / notes / count / seeds) is out of schema."""


class InvalidBgmIdError(BgmDomainError):
    """bgm_id does not match the bgm_NNNN shape."""


class BgmNotFoundError(BgmDomainError):
    """No bgm folder under _bgm/{category}/ for the given id."""


class BgmAlreadyAssignedError(BgmDomainError):
    """The track is referenced by at least one drama's bgm.md — cannot delete."""

    def __init__(self, bgm_id: str, assignments: list[dict[str, object]]) -> None:
        super().__init__(f"bgm {bgm_id} has {len(assignments)} reference(s)")
        self.bgm_id: str = bgm_id
        self.assignments: list[dict[str, object]] = assignments


class BgmDeleteTargetExistsError(BgmDomainError):
    """The target path under _deleted/_bgm/ already exists."""


class BgmDeleteFailedError(BgmDomainError):
    """OS-level failure during the rename / mkdir step of delete_bgm."""


class BgmGenerationDirMissingError(BgmDomainError):
    """The _bgm directory cannot be created (filesystem error)."""


class BgmReferenceScanFailedError(BgmDomainError):
    """OS-level failure while scanning bgm.md files for track references."""


class StableAudioMissingError(BgmDomainError):
    """The Stable Audio generation tool (tools/stableaudio_gen.py) or its
    Python interpreter / torch dependency could not be located."""


class StableAudioFailedError(BgmDomainError):
    """The Stable Audio generation subprocess ran but failed to produce an mp3."""


class BgmSidecarUnreadableError(BgmDomainError):
    """The track's `.md` sidecar is missing or its 生成 prompt block cannot be
    parsed — local audio generation needs the prompt / seed / duration it
    carries."""
