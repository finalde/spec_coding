"""Named domain errors for the Voice aggregate. Application layer catches
these and maps to transport-layer error shapes; infrastructure raises them
directly per follow-up 114. Generic exceptions (ValueError, OSError) are NOT
used for domain violations — every invariant breach is a named class."""
from __future__ import annotations


class VoiceDomainError(Exception):
    """Base for all Voice-aggregate domain errors."""


class InvalidVoiceAttributeError(VoiceDomainError):
    """An attribute (archetype / gender / age_impression / pace / pitch_register /
    emotion_default / tone / signature_inflection / notes / count / seeds) is
    out of schema."""


class InvalidVoiceIdError(VoiceDomainError):
    """voice_id does not match the voice_NNNN shape."""


class VoiceNotFoundError(VoiceDomainError):
    """No voice folder under _voices/ for the given id."""


class VoiceAlreadyAssignedError(VoiceDomainError):
    """The voice is currently bound to at least one character role — cannot delete."""

    def __init__(self, voice_id: str, assignments: list[dict[str, object]]) -> None:
        super().__init__(f"voice {voice_id} has {len(assignments)} assignment(s)")
        self.voice_id: str = voice_id
        self.assignments: list[dict[str, object]] = assignments


class VoiceAlreadyDeletedError(VoiceDomainError):
    """The voice folder is already under _deleted/."""


class VoiceDeleteTargetExistsError(VoiceDomainError):
    """The target path under _deleted/_voices/ already exists."""


class VoiceDeleteFailedError(VoiceDomainError):
    """OS-level failure during the rename / mkdir step of delete_voice."""


class VoiceGenerationDirMissingError(VoiceDomainError):
    """The _voices directory cannot be created (filesystem error)."""


class VoiceAudioUploadFailedError(VoiceDomainError):
    """OS-level failure writing the user-supplied audio sample."""


class VoiceAudioExtensionNotAllowedError(VoiceDomainError):
    """The uploaded audio file extension is not in {.mp3, .wav, .m4a}."""


class VoiceAudioTooLargeError(VoiceDomainError):
    """The uploaded audio file exceeds the 10 MiB cap."""


class VoiceMp4MissingError(VoiceDomainError):
    """No `*.mp4` file present in the voice folder to extract audio from."""


class VoiceFfmpegMissingError(VoiceDomainError):
    """`imageio_ffmpeg.get_ffmpeg_exe()` could not locate an ffmpeg binary."""


class VoiceAudioExtractFailedError(VoiceDomainError):
    """ffmpeg subprocess failed while extracting an mp3 from a source mp4."""
