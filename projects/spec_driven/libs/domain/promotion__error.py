from __future__ import annotations


class PromotionError(Exception):
    pass


class StageFolderRejected(PromotionError):
    pass


class PromotionPathRejected(PromotionError):
    pass
