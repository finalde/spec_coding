"""Character-video aggregate commands: truncate per-character mp4 + concat
per-shot character reel."""
from __future__ import annotations

from libs.application.dtos.character_video__dto import (
    ConcatShotCharactersResultCdto,
    TruncateCharacterVideoResultCdto,
)
from libs.application.mappers.character_video__mapper import CharacterVideoMapper
from libs.domain.errors.character_video__error import (
    CharacterVideoNotFoundError,
    ConcatFailedError,
    FfmpegMissingForCharacterVideoError,
    InvalidCharacterVideoPathError,
    InvalidShotMdPathError,
    NoCharacterTableError,
    NotCharacterVideoError,
    NotShotMdError,
    ShotMdNotFoundError,
    TruncateFailedError,
)
from libs.infrastructure.writers.character_video__writer import (
    CharacterVideoTruncator,
    ConcatFailed,
    FfmpegMissing,
    InvalidPath,
    NoCharacterTable,
    NotCharacterVideo,
    NotFound,
    NotShotMd,
    ShotConcatBuilder,
    TruncateFailed,
)


class CharacterVideoCommand:
    def __init__(
        self,
        truncator: CharacterVideoTruncator,
        builder: ShotConcatBuilder,
    ) -> None:
        self._truncator = truncator
        self._builder = builder

    def truncate(self, rel_path: str) -> TruncateCharacterVideoResultCdto:
        try:
            result = self._truncator.truncate(rel_path)
        except InvalidPath as exc:
            raise InvalidCharacterVideoPathError(str(exc)) from exc
        except NotCharacterVideo as exc:
            raise NotCharacterVideoError(str(exc)) from exc
        except NotFound as exc:
            raise CharacterVideoNotFoundError(str(exc)) from exc
        except FfmpegMissing as exc:
            raise FfmpegMissingForCharacterVideoError(str(exc)) from exc
        except TruncateFailed as exc:
            raise TruncateFailedError(str(exc)) from exc
        return CharacterVideoMapper.truncate_to_cdto(result)

    def concat_shot(self, rel_path: str) -> ConcatShotCharactersResultCdto:
        try:
            result = self._builder.build(rel_path)
        except InvalidPath as exc:
            raise InvalidShotMdPathError(str(exc)) from exc
        except NotShotMd as exc:
            raise NotShotMdError(str(exc)) from exc
        except NotFound as exc:
            raise ShotMdNotFoundError(str(exc)) from exc
        except NoCharacterTable as exc:
            raise NoCharacterTableError(str(exc)) from exc
        except FfmpegMissing as exc:
            raise FfmpegMissingForCharacterVideoError(str(exc)) from exc
        except ConcatFailed as exc:
            raise ConcatFailedError(str(exc)) from exc
        return CharacterVideoMapper.concat_to_cdto(result)
