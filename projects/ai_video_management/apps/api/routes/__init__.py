"""Routes package — per-aggregate route files combined into one APIRouter.

Per follow-up 062: the single 850-line `routes.py` was split into
`{aggregate}__route.py` files, one per aggregate. This `__init__.py`
exposes a combined `router` that `apps/api/app_factory.py` mounts on
the FastAPI app via `app.include_router(router)`. Each per-aggregate
file defines its own `APIRouter()`.
"""
from __future__ import annotations

from fastapi import APIRouter

from apps.api.routes.actor__route import router as _actor_router
from apps.api.routes.bgm__route import router as _bgm_router
from apps.api.routes.casting__route import router as _casting_router
from apps.api.routes.character_video__route import router as _character_video_router
from apps.api.routes.downloads__route import router as _downloads_router
from apps.api.routes.episode__route import router as _episode_router
from apps.api.routes.episode_bgm__route import router as _episode_bgm_router
from apps.api.routes.file__route import router as _file_router
from apps.api.routes.frame__route import router as _frame_router
from apps.api.routes.intro_card__route import router as _intro_card_router
from apps.api.routes.scene_plate__route import router as _scene_plate_router
from apps.api.routes.media__route import router as _media_router
from apps.api.routes.novel__route import router as _novel_router
from apps.api.routes.perf_check__route import router as _perf_check_router
from apps.api.routes.perf_score__route import router as _perf_score_router
from apps.api.routes.performance__route import router as _performance_router
from apps.api.routes.prompt__route import router as _prompt_router
from apps.api.routes.shot_regen__route import router as _shot_regen_router
from apps.api.routes.subtitle__route import router as _subtitle_router
from apps.api.routes.tree__route import router as _tree_router
from apps.api.routes.voice__route import router as _voice_router

router = APIRouter()
router.include_router(_tree_router)
router.include_router(_file_router)
router.include_router(_media_router)
router.include_router(_frame_router)
router.include_router(_scene_plate_router)
router.include_router(_downloads_router)
router.include_router(_actor_router)
router.include_router(_bgm_router)
router.include_router(_casting_router)
router.include_router(_character_video_router)
router.include_router(_episode_router)
router.include_router(_episode_bgm_router)
router.include_router(_novel_router)
router.include_router(_voice_router)
router.include_router(_prompt_router)
router.include_router(_perf_score_router)
router.include_router(_perf_check_router)
router.include_router(_performance_router)
router.include_router(_shot_regen_router)
router.include_router(_subtitle_router)
router.include_router(_intro_card_router)
