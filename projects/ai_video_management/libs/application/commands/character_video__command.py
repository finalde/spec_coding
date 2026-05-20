"""Character-video aggregate commands: truncate per-character mp4 + concat
per-shot character reel."""
from __future__ import annotations

from libs.application.dtos.character_video__dto import (
    ConcatShotCharactersResultCdto,
    ExtractCharacterViewsResultCdto,
    TruncateCharacterVideoResultCdto,
)
from libs.application.mappers.character_video__mapper import CharacterVideoMapper
from libs.domain.errors.character_video__error import (
    AudioExtractFailedError,
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
    ViewExtractFailedError,
)
from libs.infrastructure.writers.character_video__writer import (
    AudioExtractFailed,
    CharacterVideoTruncator,
    CharacterViewExtractor,
    ConcatFailed,
    FfmpegMissing,
    InvalidPath,
    NoCharacterTable,
    NotCharacterVideo,
    NotFound,
    NotShotMd,
    ShotConcatBuilder,
    TruncateFailed,
    ViewExtractFailed,
)


class CharacterVideoCommand:
    def __init__(
        self,
        truncator: CharacterVideoTruncator,
        builder: ShotConcatBuilder,
        extractor: CharacterViewExtractor,
    ) -> None:
        self._truncator = truncator
        self._builder = builder
        self._extractor = extractor

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

    def extract_views(self, rel_path: str) -> ExtractCharacterViewsResultCdto:
        try:
            result = self._extractor.extract(rel_path)
        except InvalidPath as exc:
            raise InvalidCharacterVideoPathError(str(exc)) from exc
        except NotCharacterVideo as exc:
            raise NotCharacterVideoError(str(exc)) from exc
        except NotFound as exc:
            raise CharacterVideoNotFoundError(str(exc)) from exc
        except FfmpegMissing as exc:
            raise FfmpegMissingForCharacterVideoError(str(exc)) from exc
        except AudioExtractFailed as exc:
            raise AudioExtractFailedError(str(exc)) from exc
        except ViewExtractFailed as exc:
            raise ViewExtractFailedError(str(exc)) from exc
        return CharacterVideoMapper.views_to_cdto(result)
